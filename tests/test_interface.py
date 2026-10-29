"""Proposed tests for CALC-3's public formatting API and command-line interface.

Proposed public API:
``calculator.calculate(request: str, output: str = "numeric") -> str``.
It accepts the bounded symbolic and natural-language requests already covered
by the calculator tests and supports ``numeric``, ``words``, and ``both``
output modes. Numeric output is normalized; price-increase requests use
``Rs N/-`` currency notation, rounding fractional rupees to two places with
``ROUND_HALF_UP``. Words output renders finite decimal values in English
(``6`` as ``six`` and ``3.8`` as ``three point eight``), prefixes negative
values with ``negative``. For a currency request, words mode verbalizes its
numeric result; no currency-unit wording is asserted because the approved
scope does not prescribe one. Both mode is the numeric form followed by the
words in parentheses.

The CLI contract under test is ``calculator.main(argv=None) -> int``, with
``argv`` a list of argument strings and one request string after any options.
It writes a successful result plus a newline to stdout, returns zero on
success, and returns a nonzero status with a useful error on stderr for an
invalid request. ``--output`` selects an explicit mode. Without it, only a
trailing ``in words``, ``as words``, or ``both`` selects a non-numeric mode;
otherwise output defaults to numeric. No broader natural-language behavior
is implied by these interface tests.
"""

import contextlib
import io
import unittest

from calculator import calculate, main


class CalculateInterfaceTests(unittest.TestCase):
    def test_symbolic_and_natural_language_requests(self):
        self.assertEqual(calculate("Evaluate 3 * 10 / (2 + 3)"), "6")
        self.assertEqual(
            calculate(
                "What is the new price of a book if its price has been "
                "increased by 10% and the original price is Rs 120/-?"
            ),
            "Rs 132/-",
        )
        self.assertEqual(calculate("4 - 2 / 10"), "3.8")
        self.assertEqual(calculate("1.20 + 1.80"), "3")
        self.assertEqual(calculate("10% of 120"), "12")

    def test_numeric_words_and_both_output_modes(self):
        self.assertEqual(calculate("6"), "6")
        self.assertEqual(calculate("6", output="words"), "six")
        self.assertEqual(calculate("3.8", output="words"), "three point eight")
        self.assertEqual(calculate("6", output="both"), "6 (six)")
        self.assertEqual(
            calculate("3.8", output="both"), "3.8 (three point eight)"
        )

    def test_words_support_negative_values(self):
        self.assertEqual(calculate("-6", output="words"), "negative six")
        self.assertEqual(calculate("-3.8", output="words"), "negative three point eight")

    def test_words_preserve_zeroes_in_fractional_digits(self):
        self.assertEqual(calculate("3.08", output="words"), "three point zero eight")
        self.assertEqual(calculate("0.001", output="words"), "zero point zero zero one")

    def test_currency_formatting_omits_paise_for_whole_rupees(self):
        request = (
            "What is the new price of a book if its price has been increased "
            "by 10% and the original price is Rs 120/-?"
        )
        self.assertEqual(calculate(request), "Rs 132/-")

    def test_currency_fraction_rounding_uses_round_half_up_including_tie(self):
        # 0.05 increased by 10% is exactly 0.055: the paise tie rounds up.
        tie_request = (
            "What is the new price of a book if its price has been increased "
            "by 10% and the original price is Rs 0.05/-?"
        )
        self.assertEqual(calculate(tie_request), "Rs 0.06/-")
        fractional_request = (
            "What is the new price of a book if its price has been increased "
            "by 10% and the original price is Rs 120.01/-?"
        )
        self.assertEqual(calculate(fractional_request), "Rs 132.01/-")

    def test_currency_result_is_rendered_in_words_mode(self):
        request = (
            "What is the new price of a book if its price has been increased "
            "by 10% and the original price is Rs 120/-?"
        )
        self.assertEqual(calculate(request, output="words"), "one hundred thirty-two")

    def test_rejects_an_invalid_output_mode(self):
        with self.assertRaises(ValueError):
            calculate("6", output="roman")

    def test_words_magnitude_bound_is_strict(self):
        self.assertEqual(
            calculate("999999999999999", output="words"),
            "nine hundred ninety-nine trillion nine hundred ninety-nine billion "
            "nine hundred ninety-nine million nine hundred ninety-nine thousand "
            "nine hundred ninety-nine",
        )
        with self.assertRaises(ValueError):
            calculate("1000000000000000", output="words")

    def test_words_accept_up_to_64_fractional_digits_only(self):
        at_limit = "0." + "1" * 64
        self.assertEqual(
            calculate(at_limit, output="words"),
            "zero point " + " ".join(["one"] * 64),
        )
        over_limit = "0." + "1" * 65
        with self.assertRaises(ValueError):
            calculate(over_limit, output="words")


class CalculatorCliTests(unittest.TestCase):
    def invoke(self, argv):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            status = main(argv)
        return status, stdout.getvalue(), stderr.getvalue()

    def test_explicit_output_option_and_successful_stdout(self):
        status, stdout, stderr = self.invoke(["--output", "words", "6"])
        self.assertEqual(status, 0)
        self.assertEqual(stdout, "six\n")
        self.assertEqual(stderr, "")

    def test_explicit_output_option_selects_both(self):
        status, stdout, stderr = self.invoke(["--output", "both", "3.8"])
        self.assertEqual(status, 0)
        self.assertEqual(stdout, "3.8 (three point eight)\n")
        self.assertEqual(stderr, "")

    def test_suffix_inference_for_words_and_both(self):
        cases = (
            (["6 in words"], "six\n"),
            (["6 as words"], "six\n"),
            (["6 both"], "6 (six)\n"),
        )
        for argv, expected in cases:
            with self.subTest(argv=argv):
                status, stdout, stderr = self.invoke(argv)
                self.assertEqual(status, 0)
                self.assertEqual(stdout, expected)
                self.assertEqual(stderr, "")

    def test_cli_defaults_to_numeric_output(self):
        status, stdout, stderr = self.invoke(["3.8"])
        self.assertEqual(status, 0)
        self.assertEqual(stdout, "3.8\n")
        self.assertEqual(stderr, "")

    def test_cli_invalid_request_returns_error_status_and_stderr(self):
        status, stdout, stderr = self.invoke(["not a supported calculation"])
        self.assertNotEqual(status, 0)
        self.assertEqual(stdout, "")
        self.assertRegex(stderr.lower(), r"(invalid|unsupported|malformed)")


if __name__ == "__main__":
    unittest.main()
