"""Unit tests for each cleaning transform, using small hand-built fixtures."""

import pandas as pd
import pytest

from messydataeda.clean import (
    fill_missing_city,
    flag_invalid_quantity,
    flag_missing_discount,
    parse_order_date,
    remove_exact_duplicates,
    standardize_country,
    standardize_payment_method,
)


class TestParseOrderDate:
    def test_handles_all_five_known_formats(self) -> None:
        raw = pd.Series(["2025-05-29", "09-23-2025", "18/11/2024", "2025/07/27", "10 Apr 2026"])
        parsed = parse_order_date(raw)
        expected = pd.to_datetime(
            ["2025-05-29", "2025-09-23", "2024-11-18", "2025-07-27", "2026-04-10"]
        )
        assert list(parsed) == list(expected)

    def test_rejects_unknown_format(self) -> None:
        with pytest.raises(ValueError, match="matched no known format"):
            parse_order_date(pd.Series(["29-May-2025"]))


class TestStandardizePaymentMethod:
    def test_merges_casing_and_spacing_variants(self) -> None:
        raw = pd.Series(["paypal", "PayPal", "Pay Pal", "COD", "cash on delivery"])
        result = standardize_payment_method(raw)
        assert list(result) == [
            "PayPal",
            "PayPal",
            "PayPal",
            "Cash on Delivery",
            "Cash on Delivery",
        ]

    def test_rejects_unrecognized_value(self) -> None:
        with pytest.raises(ValueError, match="Unrecognized"):
            standardize_payment_method(pd.Series(["bitcoin"]))


class TestStandardizeCountry:
    def test_merges_abbreviations_and_casing(self) -> None:
        raw = pd.Series(["usa", "U.S.A", "United States", "uk", "U.K."])
        result = standardize_country(raw)
        assert list(result) == [
            "United States",
            "United States",
            "United States",
            "United Kingdom",
            "United Kingdom",
        ]

    def test_rejects_unrecognized_value(self) -> None:
        with pytest.raises(ValueError, match="Unrecognized"):
            standardize_country(pd.Series(["Narnia"]))


class TestFlagInvalidQuantity:
    def test_flags_zero_and_negative_only(self) -> None:
        result = flag_invalid_quantity(pd.Series([-1, 0, 1, 5]))
        assert list(result) == [True, True, False, False]


class TestRemoveExactDuplicates:
    def test_keeps_first_occurrence_only(self) -> None:
        df = pd.DataFrame({"a": [1, 1, 2], "b": ["x", "x", "y"]})
        result = remove_exact_duplicates(df)
        assert len(result) == 2
        assert result["a"].tolist() == [1, 2]

    def test_leaves_non_identical_rows_with_same_id_alone(self) -> None:
        df = pd.DataFrame({"id": [1, 1], "value": ["a", "b"]})
        result = remove_exact_duplicates(df)
        assert len(result) == 2


class TestFlagMissingDiscount:
    def test_flags_nan_but_not_explicit_zero(self) -> None:
        result = flag_missing_discount(pd.Series([0.0, None, 5.0, None]))
        assert list(result) == [False, True, False, True]


class TestFillMissingCity:
    def test_fills_unknown_and_flags_original_gaps(self) -> None:
        filled, flag = fill_missing_city(pd.Series(["London", None, "Cairo"]))
        assert list(filled) == ["London", "Unknown", "Cairo"]
        assert list(flag) == [False, True, False]
