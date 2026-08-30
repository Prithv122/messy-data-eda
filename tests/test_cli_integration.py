"""End-to-end integration test for the CLI orchestration: point `run()` at a
small fixture CSV and confirm it actually writes processed data, a quality
report, and every expected figure -- not just that the functions it calls
are individually correct."""

from pathlib import Path

import pandas as pd
import pytest

from messydataeda import cli

FIXTURE_ROWS = [
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
]


@pytest.fixture
def isolated_run(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    raw_dir = tmp_path / "data" / "raw"
    raw_dir.mkdir(parents=True)
    raw_path = raw_dir / "sample.csv"
    pd.DataFrame(FIXTURE_ROWS).to_csv(raw_path, index=False)

    monkeypatch.setattr(cli, "ROOT", tmp_path)
    monkeypatch.setattr(cli, "PROCESSED_PATH", tmp_path / "data" / "processed" / "clean.csv")
    monkeypatch.setattr(cli, "REPORTS_DIR", tmp_path / "reports")
    monkeypatch.setattr(cli, "FIGURES_DIR", tmp_path / "reports" / "figures")
    return raw_path


def test_run_writes_processed_data_report_and_figures(
    isolated_run: Path, capsys: pytest.CaptureFixture
) -> None:
    cli.run(raw_path=isolated_run)

    assert cli.PROCESSED_PATH.exists()
    processed = pd.read_csv(cli.PROCESSED_PATH)
    assert len(processed) == 2

    quality_report = cli.REPORTS_DIR / "quality_report.md"
    assert quality_report.exists()
    assert "Exact duplicate rows" in quality_report.read_text(encoding="utf-8")

    expected_figures = {
        "order_status_funnel.png",
        "revenue_by_category.png",
        "rating_by_category.png",
        "payment_method_before_after.png",
    }
    actual_figures = {p.name for p in cli.FIGURES_DIR.glob("*.png")}
    assert actual_figures == expected_figures

    out = capsys.readouterr().out
    assert "Did cleaning change a conclusion?" in out
