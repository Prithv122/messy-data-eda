"""The quality report's counts must come from the actual data, not be
hardcoded -- these tests build a fixture with a known number of each issue
and check the report reflects exactly that number."""

import pandas as pd

from messydataeda.quality import build_quality_report

RAW_FIXTURE = pd.DataFrame(
    {
        "Order_ID": ["A1", "A1", "A2", "A3", "A4"],
        "Order_Date": ["2025-01-02"] * 5,
        "Product_Category": ["Books"] * 5,
        "Quantity": [2, 2, 0, -1, 3],
        "Unit_Price_USD": [10.0] * 5,
        "Discount_Percent": [5.0, 5.0, None, 0.0, 10.0],
        "Payment_Method": ["paypal"] * 5,
        "Shipping_City": ["London", "London", None, "Berlin", "Delhi"],
        "Country": ["usa"] * 5,
        "Order_Status": ["Delivered", "Delivered", "Cancelled", "Returned", "Shipped"],
        "Customer_Rating": [4.0, 4.0, None, None, None],
    }
)


def test_report_counts_match_fixture() -> None:
    report = build_quality_report(RAW_FIXTURE).set_index("Problem")

    assert report.loc["Exact duplicate rows", "Count"] == 1
    assert report.loc["Invalid Quantity (<= 0)", "Count"] == 2
    assert report.loc["Missing Discount_Percent", "Count"] == 1
    assert report.loc["Missing Shipping_City", "Count"] == 1
    assert report.loc["Missing Customer_Rating", "Count"] == 3


def test_report_has_all_required_columns() -> None:
    report = build_quality_report(RAW_FIXTURE)
    assert list(report.columns) == ["Problem", "Count", "Action", "Why"]
    assert report["Why"].str.len().gt(0).all()
