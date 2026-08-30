"""EDA functions that answer specific business questions on the cleaned data.

Each function returns a real pandas object (Series/DataFrame), not a chart --
`figures.py`-style plotting is kept separate so the numbers themselves are
directly testable.
"""

from __future__ import annotations

import pandas as pd


def revenue_by_category(clean: pd.DataFrame) -> pd.Series:
    """Gross revenue (Quantity * Unit_Price_USD) by category, excluding rows
    flagged Invalid_Quantity -- a negative/zero quantity produces nonsense
    revenue and would distort every category it touches."""
    valid = clean.loc[~clean["Invalid_Quantity"]]
    revenue = valid["Quantity"] * valid["Unit_Price_USD"]
    return revenue.groupby(valid["Product_Category"]).sum().sort_values(ascending=False)


def payment_method_breakdown(clean: pd.DataFrame) -> pd.Series:
    return clean["Payment_Method"].value_counts()


def naive_payment_method_breakdown(raw: pd.DataFrame) -> pd.Series:
    """The answer you'd get analyzing the raw column directly, casing and all
    -- used only to demonstrate how much cleaning changes the conclusion."""
    return raw["Payment_Method"].value_counts()


def country_breakdown(clean: pd.DataFrame) -> pd.Series:
    return clean["Country"].value_counts()


def order_status_funnel(clean: pd.DataFrame) -> pd.DataFrame:
    """Where orders end up: completed (Delivered), still moving through the
    pipeline (Pending/Shipped), or lost (Cancelled/Returned)."""
    counts = clean["Order_Status"].value_counts()
    total = len(clean)
    stage = {
        "Delivered": "Completed",
        "Pending": "In progress",
        "Shipped": "In progress",
        "Cancelled": "Lost",
        "Returned": "Lost",
    }
    df = counts.rename("Count").to_frame()
    df["Share"] = (df["Count"] / total).round(4)
    df["Stage"] = df.index.map(stage)
    return df.sort_values("Count", ascending=False)


def rating_by_category(clean: pd.DataFrame) -> pd.Series:
    """Mean Customer_Rating per category, computed only over rows that
    actually have a rating -- non-delivered/unrated rows are legitimately
    absent, not zero, so they must not enter the mean."""
    rated = clean.dropna(subset=["Customer_Rating"])
    return rated.groupby("Product_Category")["Customer_Rating"].mean().sort_values(ascending=False)


def cleaning_impact_on_payment_conclusion(
    raw: pd.DataFrame, clean: pd.DataFrame
) -> dict[str, object]:
    """Concrete evidence that cleaning changed a real conclusion, not just
    cosmetics: the naive top payment method (by raw spelling) differs from
    the true top method once casing/format variants are merged."""
    naive = naive_payment_method_breakdown(raw)
    true = payment_method_breakdown(clean)
    return {
        "naive_top_label": naive.idxmax(),
        "naive_top_count": int(naive.max()),
        "true_top_label": true.idxmax(),
        "true_top_count": int(true.max()),
        "conclusion_changed": naive.idxmax() != true.idxmax(),
    }
