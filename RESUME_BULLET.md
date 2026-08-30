# Resume Bullets — messy-data-eda

Form: **action → technical specifics → measured outcome.** Numbers or it doesn't go on the resume.

---

## Bullets

- Built an evidence-based data-cleaning pipeline (pandas) for a 12,180-row messy e-commerce
  export, resolving 5 distinct data-quality issues (mixed date formats, 20 payment-method
  spellings, exact duplicates, invalid quantities, three flavors of missing data) with a
  documented rule for each backed by measured patterns rather than blanket imputation.
- Proved the cleaning changed a real business conclusion: naive analysis of the raw
  `Payment_Method` column ranks `"paypal"` (709 orders) as the top method; after
  standardizing casing/format across 20 raw spellings, the true top method is Cash on
  Delivery (2,070 orders) — a materially different answer.
- Shipped with 21 unit + integration tests (99% coverage) covering every transform in
  isolation plus one end-to-end pipeline test against a fixture carrying all documented
  issues at once, and a fully reproducible CLI (`uv run messy-data-eda`) that regenerates
  every number and chart in the README from the committed raw data.

## Which roles this supports

- [ ] Data Scientist / ML
- [ ] AI Engineer (LLM/NLP/CV)
- [ ] Data Engineer
- [x] Data Analyst / Python Developer

## Keywords this project earns

pandas, matplotlib, seaborn, data cleaning, data quality, EDA, pytest, evidence-based
decision making, reproducible analysis

---

### Bad vs good

❌ "Built a machine learning model to predict customer churn using Python."
✅ "Built a churn classifier on 240k accounts (LightGBM, 1:40 class imbalance) with isotonic calibration and cost-sensitive thresholding, lifting precision@10% from 0.31 to 0.58 over the business's existing rules baseline."

The second one is answerable in an interview. The first invites the question you can't answer.
