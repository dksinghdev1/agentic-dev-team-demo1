"""Tests for the calculator's bounded natural-language calculation API."""

from decimal import Decimal

import pytest

from calculator import calculate_request


@pytest.mark.parametrize(
    ("input_text", "expected"),
    [
        (
            "What is the new price of a book if its price has been increased "
            "by 10% and the original price is Rs 120/-?",
            "132",
        ),
        (
            "What is the new price of a book if its price has been increased "
            "by 25% and the original price is Rs 80/-?",
            "100",
        ),
        (
            "What is the new price of a book if its price has been increased "
            "by 12.5% and the original price is Rs 20.50/-?",
            "23.0625",
        ),
        (
            "What is the new price of a book if its price has been increased "
            "by 0% and the original price is Rs 120/-?",
            "120",
        ),
        ("10% of 120", "12"),
        ("23 plus 19", "42"),
        ("23 minus 19", "4"),
        ("6 times 7", "42"),
        ("6 multiplied by 7", "42"),
        ("84 divided by 7", "12"),
        (" 2   PLUS  3 ", "5"),
        ("6\tMULTIPLIED BY\t7", "42"),
        ("2" + " " * 509 + "plus" + " " * 509 + "3", "5"),
    ],
)
def test_calculates_supported_requests(input_text, expected):
    assert calculate_request(input_text) == Decimal(expected)


@pytest.mark.parametrize(
    "input_text",
    [
        "Add 2 and 3",
        "What is 2 plus 3?",
        "twenty plus 3",
        "2 add 3",
        "10 percent of 120",
        "",
        "plus 3",
        "2 plus",
        "10% of",
        "of 120",
        "2 multiplied",
        "2 divided by",
        "2 plus 3 plus 4",
        "2 plus 3 4",
        "10% of 120 of 2",
        "2 plus plus 3",
        "2 multiplied 3",
        "2 divided 3",
        "2 times by 3",
        "2" + " " * 509 + "plus" + " " * 510 + "3",
    ],
)
def test_rejects_unsupported_or_malformed_requests(input_text):
    with pytest.raises(ValueError):
        calculate_request(input_text)


def test_division_by_zero_is_explicit():
    with pytest.raises(ZeroDivisionError):
        calculate_request("12 divided by 0")
