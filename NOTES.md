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

### YYYY-MM-DD
- **Tried:**
- **Broke:**
- **Fixed by:**
- **Learned:**

---

## Rejected approaches

| Approach | Why rejected |
|---|---|
| UCI Online Retail dataset | License "Unknown" on Kaggle; better reserved for D2's cohort/funnel analysis, which actually needs its dated per-customer invoice structure |
| `dirty_cafe_sales` | Re-uploaded by multiple Kaggle users — too commonly used to be distinctive |

## Open questions

- [ ]
