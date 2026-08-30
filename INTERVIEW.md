# Interview Prep — messy-data-eda

**Five questions, five answers.** An unanswered question means this project is not shipped.

If you can't answer one, you don't understand that part of your own project yet — go back and understand it. This file is the difference between a portfolio that survives a technical screen and one that collapses in it.

---

### Q1. Walk me through the architecture in 90 seconds.

_A:_ It's a script pipeline over a single CSV, no database or service — the right shape for a
one-off 12k-row dataset. `data/raw/*.csv` goes into `clean.py`, which runs five independent
transforms (date parsing, payment-method/country canonicalization, exact-dedup, and two
missing-value flags) and produces `data/processed/clean.csv` plus a `quality.py` report
comparing before and after. `eda.py` then answers specific business questions against the
clean data (revenue by category, the order-status funnel, ratings by category), `figures.py`
renders those as charts, and `cli.py` ties the whole thing together behind one command,
`uv run messy-data-eda`. Every step is a pure function over a DataFrame, so each one is
independently unit-tested without needing the real 12k-row file.

### Q2. Why did you choose to flag-and-keep invalid rows instead of dropping them?

_A:_ Because dropping is not free — a row with `Quantity = 0` still has a valid category,
payment method, and country that other analyses (like "which countries order most") would
lose for no reason. Before deciding, I checked whether the 192 invalid-quantity rows
clustered in Returned/Cancelled orders, which would have suggested they meant something (a
return credit, say). They didn't — they're proportionally spread across every `Order_Status`,
consistent with plain data-entry error. So the rule is: flag it (`Invalid_Quantity` column),
exclude it from the specific aggregates it would corrupt (quantity sums, revenue), and leave
everything else about that row intact. Same logic for missing `Discount_Percent` — it's not
imputed as 0 because 0.0 is already a common *explicit* value in the column (4,099 rows), so
imputing would erase a real distinction between "confirmed no discount" and "we don't know."

### Q3. What's the weakest part of this, and what would break first at scale?

_A:_ The date parser. `parse_order_date` loops row by row in Python, trying five regex
patterns against each value — fine at 12,180 rows, but it's the one part of the pipeline
that isn't vectorized, and it'd be the first thing to slow down noticeably past a few hundred
thousand rows. The fix is straightforward (classify rows into format-groups with one
vectorized `str.match` pass per pattern, then parse each group in a single `pd.to_datetime`
call instead of looping), I just didn't need it at this size and didn't want to add
complexity the dataset didn't call for.

### Q4. How do you know it works? What did you measure, and against what baseline?

_A:_ Every cleaning rule has a dedicated unit test against a small hand-built fixture (e.g.
`standardize_payment_method` merging `"paypal"`/`"PayPal"`/`"Pay Pal"` into one label), plus
one end-to-end test that runs a fixture carrying every documented issue at once through the
full pipeline and checks the exact expected output. 21 tests, 99% coverage. Beyond
correctness, I checked whether the cleaning actually *mattered*: grouping the raw
`Payment_Method` column naively, the top spelling is `"paypal"` (709 orders) — but after
standardizing casing, the true top method is Cash on Delivery (2,070 orders). That's the
baseline that matters here: not "does the code run," but "does skipping this step give you
the wrong business answer." It does.

### Q5. How did you handle the fact that two of your date formats look identical at a glance (`MM-DD-YYYY` vs `DD-MM-YYYY`, both just `##-##-####`)?

_A:_ I didn't assume — I checked. For the dash-separated group, I looked at whether the
first two-digit segment ever exceeded 12 anywhere in the file; it never did, while the
second segment did in ~60% of rows. That's only possible if the first segment is always the
month and the second is the day, i.e. the file consistently uses `MM-DD-YYYY` for that
group — not a per-row ambiguity, a per-group convention. Same check, mirrored, for the
slash-separated group (`DD/MM/YYYY`). If that check had come back mixed — some rows needing
`MM-DD` and others `DD-MM` within the *same* group — a fixed format string would have been
wrong for some rows no matter which I picked, and I'd have needed a different approach
entirely (probably flagging those as genuinely unparseable rather than guessing).

---

## 30-second pitch

A raw e-commerce export arrives with mixed date formats, 20 different spellings of 6 payment
methods, exact duplicate rows, and three different flavors of missing data — each with a
different honest cause. I profiled the file first to get real counts and real patterns behind
every issue, then wrote an evidence-based cleaning rule for each one instead of a blanket
"fill it in" pass — and proved the cleaning wasn't cosmetic: analyzing the raw payment-method
column naively gives you the *wrong* answer to "which payment method dominates," and only the
cleaned data gives you the right one.
