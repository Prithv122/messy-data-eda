"""Console entry point: run the cleaning pipeline end to end and print a
before -> after data-quality summary. Never dumps raw rows to stdout."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from messydataeda import eda, figures
from messydataeda.clean import clean_pipeline
from messydataeda.quality import build_quality_report, to_markdown_table

ROOT = Path(__file__).resolve().parents[2]
RAW_PATH = ROOT / "data" / "raw" / "ecommerce_retail_transactions_raw.csv"
PROCESSED_PATH = ROOT / "data" / "processed" / "clean.csv"
REPORTS_DIR = ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"


def run(raw_path: Path = RAW_PATH) -> None:
    raw = pd.read_csv(raw_path)
    print(f"Loaded {len(raw):,} raw rows from {raw_path.name}")

    report = build_quality_report(raw)
    print("\n=== Data quality report ===")
    print(report.to_string(index=False))

    clean = clean_pipeline(raw)
    print(f"\nCleaned dataset: {len(clean):,} rows (was {len(raw):,})")

    PROCESSED_PATH.parent.mkdir(parents=True, exist_ok=True)
    clean.to_csv(PROCESSED_PATH, index=False)
    print(f"Wrote cleaned data to {PROCESSED_PATH.relative_to(ROOT)}")

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / "quality_report.md").write_text(
        "# Data quality report\n\n" + to_markdown_table(report) + "\n", encoding="utf-8"
    )

    funnel = eda.order_status_funnel(clean)
    revenue = eda.revenue_by_category(clean)
    ratings = eda.rating_by_category(clean)
    impact = eda.cleaning_impact_on_payment_conclusion(raw, clean)

    print("\n=== Order status funnel ===")
    print(funnel.to_string())
    print("\n=== Revenue by category ===")
    print(revenue.to_string())
    print("\n=== Mean rating by category ===")
    print(ratings.to_string())
    print("\n=== Did cleaning change a conclusion? ===")
    print(
        f"Naive (raw spelling) top payment method: {impact['naive_top_label']} "
        f"({impact['naive_top_count']} orders)"
    )
    print(
        f"True (standardized) top payment method: {impact['true_top_label']} "
        f"({impact['true_top_count']} orders)"
    )
    print(f"Conclusion changed: {impact['conclusion_changed']}")

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    figures.save_order_status_funnel(funnel, FIGURES_DIR / "order_status_funnel.png")
    figures.save_revenue_by_category(revenue, FIGURES_DIR / "revenue_by_category.png")
    figures.save_rating_by_category(ratings, FIGURES_DIR / "rating_by_category.png")
    figures.save_payment_method_before_after(
        eda.naive_payment_method_breakdown(raw),
        eda.payment_method_breakdown(clean),
        FIGURES_DIR / "payment_method_before_after.png",
    )
    print(f"\nSaved 4 figures to {FIGURES_DIR.relative_to(ROOT)}")


def main() -> None:
    run()
