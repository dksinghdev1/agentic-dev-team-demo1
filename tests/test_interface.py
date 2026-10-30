"""Tests for public result formatting and the command-line interface."""

import subprocess
import sys
from pathlib import Path

import pytest

from calculator import calculate


ROOT = Path(__file__).resolve().parents[1]


def test_symbolic_and_natural_language_requests():
    assert calculate("Evaluate 3 * 10 / (2 + 3)") == "6"
    assert calculate(
        "What is the new price of a book if its price has been increased "
        "by 10% and the original price is Rs 120/-?"
    ) == "Rs 132/-"
    assert calculate("4 - 2 / 10") == "3.8"
    assert calculate("1.20 + 1.80") == "3"
    assert calculate("10% of 120") == "12"


@pytest.mark.parametrize(
    ("input_text", "output", "expected"),
    [
        ("6", "numeric", "6"),
        ("6", "words", "six"),
        ("3.8", "words", "three point eight"),
        ("6", "both", "6 (six)"),
        ("3.8", "both", "3.8 (three point eight)"),
        ("-6", "words", "negative six"),
        ("-3.8", "words", "negative three point eight"),
        ("3.08", "words", "three point zero eight"),
        ("0.001", "words", "zero point zero zero one"),
    ],
)
def test_formats_numeric_words_and_both_modes(input_text, output, expected):
    assert calculate(input_text, output=output) == expected


def test_currency_formatting_omits_paise_for_whole_rupees():
    request = (
        "What is the new price of a book if its price has been increased "
        "by 10% and the original price is Rs 120/-?"
    )
    assert calculate(request) == "Rs 132/-"
    assert calculate(request, output="words") == "one hundred thirty-two"


@pytest.mark.parametrize(
    ("input_text", "expected"),
    [
        (
            "What is the new price of a book if its price has been increased "
            "by 10% and the original price is Rs 0.05/-?",
            "Rs 0.06/-",
        ),
        (
            "What is the new price of a book if its price has been increased "
            "by 10% and the original price is Rs 120.01/-?",
            "Rs 132.01/-",
        ),
    ],
)
def test_currency_fraction_rounding_uses_round_half_up(input_text, expected):
    assert calculate(input_text) == expected


def test_rejects_an_invalid_output_mode():
    with pytest.raises(ValueError):
        calculate("6", output="roman")


def test_words_magnitude_bound_is_strict():
    assert calculate("999999999999999", output="words") == (
        "nine hundred ninety-nine trillion nine hundred ninety-nine billion "
        "nine hundred ninety-nine million nine hundred ninety-nine thousand "
        "nine hundred ninety-nine"
    )
    with pytest.raises(ValueError):
        calculate("1000000000000000", output="words")


def test_words_accept_up_to_64_fractional_digits_only():
    at_limit = "0." + "1" * 64
    assert calculate(at_limit, output="words") == (
        "zero point " + " ".join(["one"] * 64)
    )
    with pytest.raises(ValueError):
        calculate("0." + "1" * 65, output="words")


@pytest.mark.parametrize(
    ("arguments", "expected_output"),
    [
        (["--output", "words", "6"], "six\n"),
        (["--output", "both", "3.8"], "3.8 (three point eight)\n"),
        (["6 in words"], "six\n"),
        (["6 as words"], "six\n"),
        (["6 both"], "6 (six)\n"),
        (["3.8"], "3.8\n"),
    ],
)
def test_cli_success_modes(arguments, expected_output):
    result = subprocess.run(
        [sys.executable, "-m", "calculator", *arguments],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert result.stdout == expected_output
    assert result.stderr == ""


def test_cli_invalid_request_reports_error():
    result = subprocess.run(
        [sys.executable, "-m", "calculator", "not a supported calculation"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert result.stdout == ""
    assert any(word in result.stderr.lower() for word in ("invalid", "unsupported", "malformed"))
