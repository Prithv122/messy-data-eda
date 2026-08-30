"""End-to-end test: a small raw fixture carrying every documented issue at
least once, run through the full pipeline, checked against the exact
expected clean output."""

import pandas as pd

from messydataeda.clean import clean_pipeline

RAW_FIXTURE = pd.DataFrame(
    [
        # A1 appears twice, byte-for-byte identical -> exact duplicate.
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
        # Zero quantity + missing discount + missing city + missing rating (non-delivered).
        {
            "Order_ID": "A2",
            "Customer_ID": "C2",
            "Order_Date": "01-15-2025",
            "Product_Category": "Toys",
            "Product_Name": "Lego",
            "Quantity": 0,
            "Unit_Price_USD": 20.0,
            "Discount_Percent": None,
            "Payment_Method": "COD",
            "Shipping_City": None,
            "Country": "UK",
            "Order_Status": "Cancelled",
            "Customer_Rating": None,
        },
        # Negative quantity + explicit zero discount (must NOT be treated as missing).
        {
            "Order_ID": "A3",
            "Customer_ID": "C3",
            "Order_Date": "15/01/2025",
            "Product_Category": "Fashion",
            "Product_Name": "Shirt",
            "Quantity": -1,
            "Unit_Price_USD": 15.0,
            "Discount_Percent": 0.0,
            "Payment_Method": "Net Banking",
            "Shipping_City": "Berlin",
            "Country": "Germany",
            "Order_Status": "Returned",
            "Customer_Rating": None,
        },
        # Slash YYYY/MM/DD date format.
        {
            "Order_ID": "A4",
            "Customer_ID": "C4",
            "Order_Date": "2025/02/10",
            "Product_Category": "Beauty",
            "Product_Name": "Lotion",
            "Quantity": 3,
            "Unit_Price_USD": 8.0,
            "Discount_Percent": 10.0,
            "Payment_Method": "UPI",
            "Shipping_City": "Delhi",
            "Country": "India",
            "Order_Status": "Shipped",
            "Customer_Rating": None,
        },
        # "DD Mon YYYY" date format, delivered with a real rating.
        {
            "Order_ID": "A5",
            "Customer_ID": "C5",
            "Order_Date": "05 Mar 2025",
            "Product_Category": "Sports",
            "Product_Name": "Ball",
            "Quantity": 1,
            "Unit_Price_USD": 25.0,
            "Discount_Percent": 20.0,
            "Payment_Method": "credit card",
            "Shipping_City": "Sydney",
            "Country": "Australia",
            "Order_Status": "Delivered",
            "Customer_Rating": 5.0,
        },
    ]
)


def test_pipeline_end_to_end() -> None:
    clean = clean_pipeline(RAW_FIXTURE.copy())

    # Deduplication: 6 raw rows -> 5 unique orders.
    assert len(clean) == 5
    assert sorted(clean["Order_ID"]) == ["A1", "A2", "A3", "A4", "A5"]

    by_id = clean.set_index("Order_ID")

    # Dates normalized regardless of source format.
    assert by_id.loc["A1", "Order_Date"] == pd.Timestamp("2025-01-02")
    assert by_id.loc["A2", "Order_Date"] == pd.Timestamp("2025-01-15")
    assert by_id.loc["A3", "Order_Date"] == pd.Timestamp("2025-01-15")
    assert by_id.loc["A4", "Order_Date"] == pd.Timestamp("2025-02-10")
    assert by_id.loc["A5", "Order_Date"] == pd.Timestamp("2025-03-05")

    # Payment method and country casing standardized.
    assert by_id.loc["A1", "Payment_Method"] == "PayPal"
    assert by_id.loc["A2", "Payment_Method"] == "Cash on Delivery"
    assert by_id.loc["A5", "Payment_Method"] == "Credit Card"
    assert by_id.loc["A1", "Country"] == "United States"
    assert by_id.loc["A2", "Country"] == "United Kingdom"

    # Invalid quantity flagged, not removed.
    assert by_id.loc["A2", "Invalid_Quantity"]
    assert by_id.loc["A3", "Invalid_Quantity"]
    assert not by_id.loc["A1", "Invalid_Quantity"]

    # Missing discount flagged; explicit 0.0 is NOT flagged as missing.
    assert by_id.loc["A2", "Discount_Missing"]
    assert not by_id.loc["A3", "Discount_Missing"]

    # Missing city filled with "Unknown" and flagged.
    assert by_id.loc["A2", "Shipping_City"] == "Unknown"
    assert by_id.loc["A2", "City_Missing"]
    assert not by_id.loc["A1", "City_Missing"]

    # Rating left as real NaN for non-delivered orders, untouched for delivered ones.
    assert pd.isna(by_id.loc["A2", "Customer_Rating"])
    assert pd.isna(by_id.loc["A3", "Customer_Rating"])
    assert by_id.loc["A1", "Customer_Rating"] == 4.0
    assert by_id.loc["A5", "Customer_Rating"] == 5.0
