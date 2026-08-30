# messy-data-eda — D1

**Tier:** 1 · **Category:** Data Analyst / Python Developer — the actual daily job of an analyst · **Wave:** 2

Root rules in `../GUIDELINES.md` apply. This file is project-specific only — keep it under 40 lines.

## What this is

Messy real-world e-commerce sales data: cleaning pipeline, EDA, documented decisions and a
data dictionary.

## Stack

pandas, matplotlib/seaborn (or plotly), pytest, ruff, uv. No web framework, no DB — this is a
notebook/script-driven cleaning + EDA case study, not a service.

## Dataset

`data/raw/ecommerce_retail_transactions_raw.csv` — "Messy E-Commerce Sales Dataset 2026" by
AfaqKhan, Kaggle, CC0. Synthetic but explicitly disclosed as such (never claim it's real).
12,180 rows × 13 cols. Documented issues: mixed date formats, inconsistent casing
(payment method, country), missing discount/city/rating values, ~180 exact duplicate rows,
invalid (0/negative) quantities. Downloaded via `kaggle datasets download`, not committed
raw to git if large — check size against repo conventions before committing.

## Acceptance criteria

- [x] Cleaning pipeline (script or notebook) that resolves every documented data-quality issue,
      with each fix traceable to a decision in `NOTES.md`
- [x] Data dictionary (column name, type, meaning, cleaning applied) — `DATA_DICTIONARY.md`
- [x] EDA with real findings and charts, not just `.describe()`
- [x] Tests on the cleaning functions (not just a smoke test) — 21 tests, 99% coverage
- [ ] Ship gate passes (`/ship`)

## Project-specific notes

Dataset is synthetic — say so plainly in the README's data section, per root rule on
never overstating data provenance. No env vars needed unless a `KAGGLE_*` var is added for
a reproducible download script.
