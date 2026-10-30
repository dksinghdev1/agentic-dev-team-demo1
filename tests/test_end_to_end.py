"""End-to-end acceptance tests across the public API and Python CLI."""

import subprocess
import sys
from pathlib import Path

import pytest

from calculator import calculate


ROOT = Path(__file__).resolve().parents[1]
BOOK_PRICE_REQUEST = (
    "What is the new price of a book if its price has been increased by "
    "10% and the original price is Rs 120/-?"
)
SYMBOLIC_EXAMPLES = [
    ("Evaluate 3 * 10 / (2 + 3)", "6", "six", "6 (six)"),
    ("4 - 2 / 10", "3.8", "three point eight", "3.8 (three point eight)"),
]


def test_original_examples_return_required_api_results():
    assert calculate(SYMBOLIC_EXAMPLES[0][0]) == "6"
    assert calculate(BOOK_PRICE_REQUEST) == "Rs 132/-"
    assert calculate(SYMBOLIC_EXAMPLES[1][0]) == "3.8"


@pytest.mark.parametrize(("input_text", "_numeric", "words", "both"), SYMBOLIC_EXAMPLES)
def test_symbolic_examples_support_words_and_both(input_text, _numeric, words, both):
    assert calculate(input_text, output="words") == words
    assert calculate(input_text, output="both") == both


@pytest.mark.parametrize("input_text", ["what is the answer to everything", "1 + )"])
def test_unsupported_and_malformed_api_requests_raise_value_error(input_text):
    with pytest.raises(ValueError):
        calculate(input_text)


@pytest.mark.parametrize(
    ("input_text", "expected"),
    [
        (SYMBOLIC_EXAMPLES[0][0], "6\n"),
        (BOOK_PRICE_REQUEST, "Rs 132/-\n"),
        (SYMBOLIC_EXAMPLES[1][0], "3.8\n"),
    ],
)
def test_original_examples_return_required_cli_results(input_text, expected):
    result = subprocess.run(
        [sys.executable, "-m", "calculator", input_text],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert result.stdout == expected
    assert result.stderr == ""


@pytest.mark.parametrize(
    ("arguments", "expected"),
    [
        (["--output", "words", SYMBOLIC_EXAMPLES[0][0]], "six\n"),
        (["--output=both", SYMBOLIC_EXAMPLES[1][0]], "3.8 (three point eight)\n"),
        (["--output", "numeric", SYMBOLIC_EXAMPLES[1][0]], "3.8\n"),
        ([SYMBOLIC_EXAMPLES[0][0] + " in words"], "six\n"),
        ([SYMBOLIC_EXAMPLES[1][0] + " as words"], "three point eight\n"),
        ([SYMBOLIC_EXAMPLES[1][0] + " both"], "3.8 (three point eight)\n"),
    ],
)
def test_cli_output_option_and_suffix_inference(arguments, expected):
    result = subprocess.run(
        [sys.executable, "-m", "calculator", *arguments],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert result.stdout == expected
    assert result.stderr == ""


@pytest.mark.parametrize("input_text", ["what is the answer to everything", "1 + )"])
def test_unsupported_and_malformed_cli_requests_report_errors(input_text):
    result = subprocess.run(
        [sys.executable, "-m", "calculator", input_text],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert result.stdout == ""
    assert result.stderr.strip()
