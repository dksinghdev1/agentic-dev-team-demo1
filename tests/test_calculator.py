"""Tests for the calculator's safe symbolic arithmetic core."""

from decimal import Decimal

import pytest

from calculator import evaluate_expression


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("3 * 10 / (2 + 3)", "6"),
        ("4 - 2 / 10", "3.8"),
        ("2 + 3", "5"),
        ("8 - 3", "5"),
        ("4 * 3", "12"),
        ("12 / 4", "3"),
        ("2 + 3 * 4", "14"),
        ("(2 + 3) * 4", "20"),
        ("20 / 5 * 2", "8"),
        ("1.25 + 2.5", "3.75"),
        ("0.3 - 0.1", "0.2"),
        ("((2 + 3) * (4 - 1)) / 5", "3"),
        ("-3", "-3"),
        ("+3", "3"),
        ("--3", "3"),
        ("-(2 + 3)", "-5"),
        ("2 * -3", "-6"),
        ("-2 * -3", "6"),
        ("10%", "0.1"),
        ("10% * 120", "12"),
        ("2.5% * 200", "5"),
        ("evaluate 3 * 10 / (2 + 3)", "6"),
        ("calculate 4 - 2 / 10", "3.8"),
        ("1" + " " * 1021 + "+1", "2"),
        ("1" + "0" * 99, "1e99"),
        ("(" * 200 + "1" + ")" * 200, "1"),
        ("-" * 1000 + "3", "3"),
    ],
)
def test_evaluates_supported_expression(expression, expected):
    assert evaluate_expression(expression) == Decimal(expected)


@pytest.mark.parametrize(
    "expression",
    [
        "",
        "   ",
        "1 +",
        "* 2",
        "1 2",
        "(1 + 2",
        "1 + 2)",
        "()",
        "1 ** 2",
        "1 // 2",
        "1 % 2",
        "10%%",
        "evaluate",
        "calculate",
        "eval 1 + 2",
        "x",
        "pi",
        "__import__('os')",
        "abs(1)",
        "x.y",
        "(1).real",
        "values[0]",
        "1[0]",
    ],
)
def test_rejects_malformed_or_unsupported_expression(expression):
    with pytest.raises(ValueError):
        evaluate_expression(expression)


@pytest.mark.parametrize("expression", ["1 / 0", "1 / (2 - 2)"])
def test_division_by_zero_is_explicit(expression):
    with pytest.raises(ZeroDivisionError):
        evaluate_expression(expression)


def test_rejects_expression_over_source_length_bound():
    expression = "1+" * 512 + "1"
    assert len(expression) == 1025
    with pytest.raises(ValueError):
        evaluate_expression(expression)


def test_rejects_literal_and_result_magnitude_over_bound():
    expressions = (
        "1" + "0" * 100,
        "1" + "0" * 101,
        "*".join(["10"] * 102),
    )
    for expression in expressions:
        with pytest.raises(ValueError):
            evaluate_expression(expression)


def test_rejects_over_limit_intermediate_even_if_final_result_is_small():
    over_limit_product = "*".join(["10"] * 101)
    expression = f"({over_limit_product}) / ({over_limit_product})"
    assert len(expression) <= 1024
    with pytest.raises(ValueError):
        evaluate_expression(expression)
