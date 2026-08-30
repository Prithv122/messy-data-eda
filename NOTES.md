# Build Notes — messy-data-eda

Working notes: what broke, what you tried, why you chose X over Y.
Not for recruiters — for you, six months from now, in an interview.

Keep it rough. Rough is the point.

---

## Log

### 2026-08-30 — dataset selection
Compared three Kaggle candidates before picking one:
- **UCI "Online Retail" / `carrie1/ecommerce-data`** — real transactions, but license listed
  as "Unknown" on Kaggle, and it's the single most reused e-commerce dataset on the platform
  (573 notebooks). Its real value is dated, per-customer invoices — better saved for D2
  cohort-funnel than spent on a pure cleaning case study.
- **`dirty_cafe_sales`** — re-uploaded by 3+ different Kaggle users, clearly the cliché
  "dirty data" tutorial dataset. Rejected for being too well-worn.
- **Chosen: `afaqkhan091/messy-e-commerce-sales-dataset-2026`** — synthetic (disclosed
  honestly in the README, not passed off as real), CC0, 12,180 rows × 13 cols, every
  data-quality issue enumerated by the dataset author up front (mixed date formats,
  inconsistent casing, missing values, ~180 exact dupes, invalid quantities) — right scope
  for a one-session Tier 1 case study, and obscure enough (139 downloads) not to read as a
  tutorial retread.

### 2026-08-30 — raw data committed, against the template default
The template `.gitignore` ignores `data/raw/` by default (right call for most projects — don't
bloat a repo with a full dataset). Overrode it here with one explicit exception for
`ecommerce_retail_transactions_raw.csv`: it's CC0, only 1.2 MB, and this project's entire
point is a real messy dataset — an interviewer cloning the repo should see the actual raw
export, not need a Kaggle account just to reproduce a cleaning case study.

### 2026-08-30 — profiled before deciding, not after
Before writing a single cleaning rule, ran a throwaway profiling script (`uv run python -c
"..."`, not committed) against the raw CSV to get exact counts for every documented issue.
This is what the evidence-based table in the README is built from — none of the "why" text
is guessed:
- **Duplicates**: confirmed all 180 duplicated `Order_ID`s have exactly one full-row twin
  and zero conflicting values (`12,180 - 180 = 12,000 = Order_ID.nunique()` exactly). Safe
  to drop with `keep="first"`, no fuzzy matching needed.
- **Order_Date**: classified every value by regex (separator + segment length) into 5
  groups. For the two ambiguous-looking groups (dash `##-##-####`, slash `##/##/####`),
  checked whether either day-segment ever exceeded 12 — it did, but only ever in one fixed
  slot per group (dash: never in the first slot, always possible in the second; slash: the
  reverse). That's the proof each format is applied consistently throughout the file, not
  row-by-row-ambiguous — a single dispatch table per format is safe.
- **Payment_Method / Country**: counted every raw spelling and grouped by hand into
  candidate canonical buckets, then verified the bucket totals summed to exactly `n` (no
  orphan spelling silently dropped or double-counted) before trusting the mapping.
- **Discount_Percent**: checked whether 0.0 already existed as an explicit value before
  considering "impute missing as 0" — it does (4,099 rows), which ruled that option out
  immediately. Also checked missing-rate by `Order_Status` (uniform, 5.1%-7.1%) to confirm
  there's no order-lifecycle pattern to impute from instead.
- **Shipping_City**: same by-status check, also uniform (3.3%-4.8%) — no pattern, so
  filled with `"Unknown"` rather than guessing.
- **Customer_Rating**: by-status breakdown showed **exactly** 100% missing for every
  non-Delivered status — not "mostly", not "correlated", literally every single row. That
  level of exactness is what justified treating it as a structural fact (can't rate an
  undelivered order) rather than a random gap to fill.
- **Invalid Quantity**: checked distribution by `Order_Status` — proportional to the
  overall status mix, no concentration in Returned/Cancelled. If it had concentrated there,
  a negative quantity might have meant "return credit" and deserved different handling.

### 2026-08-30 — real bug caught by the ambiguous-date check
First instinct for `Order_Date` was `pd.to_datetime(series, dayfirst=True)` and hope for the
best. Writing the profiling check above first (verifying which day-segment could exceed 12
in each format group) is what surfaced that the file uses **two different day/month orders**
for its two 2-digit-2-digit-4-digit groups — dash-separated dates are `MM-DD-YYYY`, slash-
separated dates are `DD/MM/YYYY`. A single `dayfirst` flag can't express that; the fix is
the regex-dispatch table in `clean.py` keyed on separator character, not just digit pattern.

### 2026-08-30 — "did cleaning change a conclusion" landed on the first real check
The one EDA question the reviewer flagged as most valuable — did cleaning change any actual
conclusion — didn't need to be manufactured. The very first thing checked (which payment
method has the most orders) already had a genuine answer: naively grouping the *raw* column,
`"paypal"` (lowercase, 709 orders) looks like the top spelling. After merging casing/format
variants, the true winner is **Cash on Delivery** (2,070 orders) — PayPal (merged) doesn't
even come second. Kept this as the headline "did cleaning matter" result rather than
searching for a more dramatic one, since it's the first thing an analyst would actually ask.

---

## Rejected approaches

| Approach | Why rejected |
|---|---|
| UCI Online Retail dataset | License "Unknown" on Kaggle; better reserved for D2's cohort/funnel analysis, which actually needs its dated per-customer invoice structure |
| `dirty_cafe_sales` | Re-uploaded by multiple Kaggle users — too commonly used to be distinctive |
| `pd.to_datetime(series, dayfirst=True)` for Order_Date | The file mixes `MM-DD-YYYY` (dash) and `DD/MM/YYYY` (slash) groups — a single `dayfirst` flag can't express two different conventions at once |
| Impute missing `Discount_Percent` as 0.0 | 0.0 is already a common explicit value (4,099 rows) — imputing would conflate "confirmed no discount" with "unknown" |
| Drop rows with invalid `Quantity` or missing `Shipping_City` | Both issues are proportionally spread across `Order_Status` with no recoverable pattern; dropping would discard otherwise-valid order data for no analytical benefit |

## Open questions

- [ ] None outstanding for the Tier 1 scope. A natural Tier 2 follow-up would be checking
      whether `Unit_Price_USD` is consistent per `Product_Name` (a per-product price that
      varies wildly across rows would be its own data-quality issue) — out of scope here
      since it wasn't in the dataset author's documented issue list and wasn't found during
      profiling.
