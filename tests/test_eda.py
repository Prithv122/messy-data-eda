"""EDA functions are tested on small fixtures so the aggregation logic is
verified independently of the real 12k-row dataset."""

import pandas as pd

from messydataeda import eda
from messydataeda.clean import clean_pipeline

RAW_FIXTURE = pd.DataFrame(
    [
        {
            "Order_ID": "A1",
            "Customer_ID": "C1",
            "Order_Date": "2025-01-02",
            "Product_Category": "Books",
            "Product_Name": "Novel",
            "Quantity": 2,
            "Unit_Price_USD": 10.0,
            "Discount_Percent": 5.0,
            "Payment_Method": "paypal",
            "Shipping_City": "London",
            "Country": "usa",
            "Order_Status": "Delivered",
            "Customer_Rating": 4.0,
        },
        {
            "Order_ID": "A2",
            "Customer_ID": "C2",
            "Order_Date": "2025-01-03",
            "Product_Category": "Books",
            "Product_Name": "Novel",
            "Quantity": -1,
            "Unit_Price_USD": 10.0,
            "Discount_Percent": 5.0,
            "Payment_Method": "PayPal",
            "Shipping_City": "London",
            "Country": "usa",
            "Order_Status": "Cancelled",
            "Customer_Rating": None,
        },
        {
            "Order_ID": "A3",
            "Customer_ID": "C3",
            "Order_Date": "2025-01-04",
            "Product_Category": "Toys",
            "Product_Name": "Lego",
            "Quantity": 3,
            "Unit_Price_USD": 20.0,
            "Discount_Percent": None,
            "Payment_Method": "COD",
            "Shipping_City": "Berlin",
            "Country": "Germany",
            "Order_Status": "Delivered",
            "Customer_Rating": 2.0,
        },
    ]
)


def test_revenue_by_category_excludes_invalid_quantity_rows() -> None:
    clean = clean_pipeline(RAW_FIXTURE.copy())
    revenue = eda.revenue_by_category(clean)
    # A2's revenue (Quantity=-1) must not count: Books revenue is A1 only (2 * 10.0 = 20.0).
    assert revenue["Books"] == 20.0
    assert revenue["Toys"] == 60.0


def test_rating_by_category_ignores_missing_ratings() -> None:
    clean = clean_pipeline(RAW_FIXTURE.copy())
    ratings = eda.rating_by_category(clean)
    # A2 has no rating and must not pull the Books mean toward it or NaN.
    assert ratings["Books"] == 4.0
    assert ratings["Toys"] == 2.0


def test_country_breakdown_counts_cleaned_countries() -> None:
    clean = clean_pipeline(RAW_FIXTURE.copy())
    countries = eda.country_breakdown(clean)
    assert countries["United States"] == 2  # A1 + A2 (A2's invalid qty is flagged, not dropped)
    assert countries["Germany"] == 1


def test_order_status_funnel_shares_sum_to_one() -> None:
    clean = clean_pipeline(RAW_FIXTURE.copy())
    funnel = eda.order_status_funnel(clean)
    assert abs(funnel["Share"].sum() - 1.0) < 1e-9


def _order(order_id: str, payment_method: str) -> dict:
    return {
        "Order_ID": order_id,
        "Customer_ID": order_id,
        "Order_Date": "2025-01-02",
        "Product_Category": "Books",
        "Product_Name": "Novel",
        "Quantity": 1,
        "Unit_Price_USD": 10.0,
        "Discount_Percent": 5.0,
        "Payment_Method": payment_method,
        "Shipping_City": "London",
        "Country": "usa",
        "Order_Status": "Delivered",
        "Customer_Rating": 4.0,
    }


def test_cleaning_impact_detects_a_changed_conclusion() -> None:
    # Raw spellings: "COD" x2 looks like the naive winner. But "paypal" and
    # "PayPal" are the same method split across two spellings (1 order each)
    # -- merged, PayPal totals 3 and actually beats COD's 2. The naive
    # top label must differ from the true top label.
    raw = pd.DataFrame(
        [
            _order("B1", "COD"),
            _order("B2", "COD"),
            _order("B3", "paypal"),
            _order("B4", "PayPal"),
            _order("B5", "PayPal"),
        ]
    )
    clean = clean_pipeline(raw.copy())
    impact = eda.cleaning_impact_on_payment_conclusion(raw, clean)
    assert impact["naive_top_label"] == "COD"
    assert impact["true_top_label"] == "PayPal"
    assert impact["true_top_count"] == 3
    assert impact["conclusion_changed"]
