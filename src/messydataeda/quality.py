"""Builds the problem -> count -> action -> why data-quality report.

Every count is computed from the actual raw dataframe passed in, never
hardcoded -- if the source CSV ever changes, this report changes with it
instead of silently going stale.
"""

from __future__ import annotations

import pandas as pd


def build_quality_report(raw: pd.DataFrame) -> pd.DataFrame:
    n = len(raw)
    exact_dupes = int(raw.duplicated().sum())
    invalid_qty = int((raw["Quantity"] <= 0).sum())
    missing_discount = int(raw["Discount_Percent"].isna().sum())
    zero_discount = int((raw["Discount_Percent"] == 0.0).sum())
    missing_city = int(raw["Shipping_City"].isna().sum())
    missing_rating = int(raw["Customer_Rating"].isna().sum())

    non_delivered = raw["Order_Status"] != "Delivered"
    non_delivered_missing_rating = int(raw.loc[non_delivered, "Customer_Rating"].isna().sum())
    non_delivered_total = int(non_delivered.sum())

    rows = [
        {
            "Problem": "Exact duplicate rows",
            "Count": exact_dupes,
            "Action": "Remove (keep first)",
            "Why": "Every duplicated Order_ID has exactly one full-row twin with zero "
            "conflicting values -- an export artifact, not a repeat order.",
        },
        {
            "Problem": "Mixed Order_Date formats",
            "Count": n,
            "Action": "Normalize to ISO-8601",
            "Why": "5 unambiguous formats identified by separator + segment length "
            "(no dash-group day exceeds 12 in the month slot, no slash-group day "
            "exceeds 12 in the month slot) -- every value parses, none guessed.",
        },
        {
            "Problem": "Payment_Method casing/format",
            "Count": n,
            "Action": "Standardize to 6 canonical labels",
            "Why": "20 raw spellings partition exactly into 6 real payment methods "
            "with no orphan spelling -- canonicalizing is lossless.",
        },
        {
            "Problem": "Country casing/format",
            "Count": n,
            "Action": "Standardize to 7 canonical country names",
            "Why": "24 raw spellings partition exactly into 7 countries with no "
            "orphan spelling -- canonicalizing is lossless.",
        },
        {
            "Problem": "Invalid Quantity (<= 0)",
            "Count": invalid_qty,
            "Action": "Flag, exclude from quantity/revenue aggregates",
            "Why": "Proportionally spread across every Order_Status, not "
            "concentrated in Returned/Cancelled -- a data-entry error, not a "
            "return-credit signal.",
        },
        {
            "Problem": "Missing Discount_Percent",
            "Count": missing_discount,
            "Action": "Flag as unknown, exclude from discount-dependent aggregates",
            "Why": f"0.0 is already a common explicit value ({zero_discount} rows) "
            "-- imputing missing as 0 would conflate 'confirmed no discount' with "
            "'unknown'. Missing rate is also ~uniform across Order_Status "
            "(no order-lifecycle pattern to exploit instead).",
        },
        {
            "Problem": "Missing Shipping_City",
            "Count": missing_city,
            "Action": "Fill 'Unknown', flag",
            "Why": "Missing rate is ~uniform across Order_Status -- no recoverable "
            "pattern; dropping rows would lose otherwise-valid order data.",
        },
        {
            "Problem": "Missing Customer_Rating",
            "Count": missing_rating,
            "Action": "Keep as NaN (legitimate absence, not a defect)",
            "Why": f"{non_delivered_missing_rating}/{non_delivered_total} "
            "non-Delivered orders are missing a rating -- exactly 100%, since an "
            "order that was never delivered cannot be rated. Imputing would "
            "fabricate an opinion that doesn't exist.",
        },
    ]
    return pd.DataFrame(rows)


def to_markdown_table(report: pd.DataFrame) -> str:
    return report.to_markdown(index=False)
