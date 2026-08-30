"""Cleaning transforms for the raw e-commerce export.

Every rule here is backed by a specific count from `scripts/profile_raw.py` /
`NOTES.md`, not a default "fix everything" pass. See DATA_DICTIONARY.md for the
full problem -> count -> action -> why table.
"""

from __future__ import annotations

import re

import pandas as pd

# Order_Date: five formats, unambiguous once separator + segment lengths are known
# (verified: no dash-group date has day > 12 in the first slot, no slash-group date
# has day > 12 in the second slot -- see NOTES.md for the profiling that proved this).
_DATE_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"^\d{4}-\d{2}-\d{2}$"), "%Y-%m-%d"),
    (re.compile(r"^\d{2}-\d{2}-\d{4}$"), "%m-%d-%Y"),
    (re.compile(r"^\d{2}/\d{2}/\d{4}$"), "%d/%m/%Y"),
    (re.compile(r"^\d{4}/\d{2}/\d{2}$"), "%Y/%m/%d"),
    (re.compile(r"^\d{2} [A-Za-z]{3} \d{4}$"), "%d %b %Y"),
]

# Keys are looked up after lowercasing AND stripping dots (see _canonicalize),
# so "U.P.I" -> "upi" before lookup -- dotted variants must not appear as keys.
PAYMENT_METHOD_MAP: dict[str, str] = {
    "paypal": "PayPal",
    "pay pal": "PayPal",
    "net banking": "Net Banking",
    "netbanking": "Net Banking",
    "upi": "UPI",
    "debit card": "Debit Card",
    "cod": "Cash on Delivery",
    "cash on delivery": "Cash on Delivery",
    "credit card": "Credit Card",
    "credit_card": "Credit Card",
}

COUNTRY_MAP: dict[str, str] = {
    "uae": "United Arab Emirates",
    "de": "Germany",
    "germany": "Germany",
    "australia": "Australia",
    "au": "Australia",
    "in": "India",
    "india": "India",
    "canada": "Canada",
    "ca": "Canada",
    "uk": "United Kingdom",
    "united kingdom": "United Kingdom",
    "usa": "United States",
    "united states": "United States",
    "us": "United States",
}


def parse_order_date(series: pd.Series) -> pd.Series:
    """Normalize mixed Order_Date formats to a single datetime64 column.

    Raises ValueError if any value doesn't match one of the five known
    formats -- a silent NaT here would hide a real data-quality regression.
    """
    result = pd.Series(pd.NaT, index=series.index, dtype="datetime64[ns]")
    unmatched: list[str] = []
    for raw in series.index:
        value = str(series[raw]).strip()
        for pattern, fmt in _DATE_PATTERNS:
            if pattern.match(value):
                result[raw] = pd.to_datetime(value, format=fmt)
                break
        else:
            unmatched.append(value)
    if unmatched:
        raise ValueError(
            f"{len(unmatched)} Order_Date values matched no known format: {unmatched[:5]}"
        )
    return result


def _canonicalize(series: pd.Series, mapping: dict[str, str]) -> pd.Series:
    normalized = series.str.strip().str.lower().str.replace(".", "", regex=False)
    mapped = normalized.map(mapping)
    unknown = mapped.isna() & series.notna()
    if unknown.any():
        bad = series[unknown].unique().tolist()
        raise ValueError(f"Unrecognized values with no canonical mapping: {bad}")
    return mapped


def standardize_payment_method(series: pd.Series) -> pd.Series:
    return _canonicalize(series, PAYMENT_METHOD_MAP)


def standardize_country(series: pd.Series) -> pd.Series:
    return _canonicalize(series, COUNTRY_MAP)


def flag_invalid_quantity(quantity: pd.Series) -> pd.Series:
    """Quantity <= 0 is a data-entry error, not a real order (see NOTES.md:
    invalid rows are proportionally spread across every Order_Status, not
    concentrated in Returned/Cancelled -- so it isn't a return-credit signal)."""
    return quantity <= 0


def remove_exact_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Drop full-row duplicates, keeping the first occurrence.

    Verified safe on this dataset: every duplicated Order_ID has exactly one
    full-row twin and zero conflicting values (checked in NOTES.md) -- these
    are export artifacts, not two different orders that happen to share an id.
    """
    return df.drop_duplicates(keep="first").reset_index(drop=True)


def flag_missing_discount(discount: pd.Series) -> pd.Series:
    """0.0 is already a common explicit value in this column (4,099 rows) --
    imputing missing as 0 would conflate "confirmed no discount" with
    "unknown", so missing is left as NaN and flagged instead."""
    return discount.isna()


def fill_missing_city(city: pd.Series) -> tuple[pd.Series, pd.Series]:
    """Missing rate is ~uniform across Order_Status (3.3%-4.8%), so there's no
    recoverable pattern to impute from. Filled with an explicit "Unknown"
    category rather than dropping otherwise-valid order rows."""
    flag = city.isna()
    filled = city.fillna("Unknown")
    return filled, flag


def clean_pipeline(raw: pd.DataFrame) -> pd.DataFrame:
    """Full cleaning pipeline. Order matters: dedupe before deriving flags,
    so flag counts reflect the deduplicated dataset the report is built on."""
    df = remove_exact_duplicates(raw)

    df["Order_Date"] = parse_order_date(df["Order_Date"])
    df["Payment_Method"] = standardize_payment_method(df["Payment_Method"])
    df["Country"] = standardize_country(df["Country"])

    df["Invalid_Quantity"] = flag_invalid_quantity(df["Quantity"])
    df["Discount_Missing"] = flag_missing_discount(df["Discount_Percent"])
    df["Shipping_City"], df["City_Missing"] = fill_missing_city(df["Shipping_City"])
    # Customer_Rating is intentionally left untouched: NaN means "not delivered
    # yet" or "delivered but not rated", both real states, not a defect.

    return df
