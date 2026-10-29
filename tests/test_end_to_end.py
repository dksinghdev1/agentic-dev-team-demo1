"""CALC-4 integration test-set contract.

This proposed standard-library unittest set exercises the three original
calculator goal examples across the public ``calculate(request, output)``
API and the actual ``python -m calculator`` command-line entry point. The
required numeric results are ``6``, ``Rs 132/-``, and ``3.8``. The approved
``words`` and ``both`` modes are checked for the two symbolic examples;
explicit CLI ``--output`` selection and trailing ``in words``/``as words``/
``both`` inference are also checked.

The tests focus on wiring between expression or bounded natural-language
handling, public result formatting, and CLI dispatch rather than repeating
the broader parser, formatting, and mode unit cases in the existing test
modules. Unsupported and malformed requests must raise ``ValueError`` from
the API, while the CLI process must exit nonzero, leave stdout empty, and
write an error to stderr. This module specifies the proposed CALC-4
acceptance contract; it does not imply that these tests have been run.
"""

import subprocess
import sys
import unittest
from pathlib import Path

from calculator import calculate


_REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
_BOOK_PRICE_REQUEST = (
    "What is the new price of a book if its price has been increased by "
    "10% and the original price is Rs 120/-?"
)
_SYMBOLIC_EXAMPLES = (
    ("Evaluate 3 * 10 / (2 + 3)", "6", "six", "6 (six)"),
    ("4 - 2 / 10", "3.8", "three point eight", "3.8 (three point eight)"),
)


class EndToEndApiTests(unittest.TestCase):
    def test_original_examples_return_required_numeric_results(self):
        self.assertEqual(calculate(_SYMBOLIC_EXAMPLES[0][0]), "6")
        self.assertEqual(calculate(_BOOK_PRICE_REQUEST), "Rs 132/-")
        self.assertEqual(calculate(_SYMBOLIC_EXAMPLES[1][0]), "3.8")

    def test_symbolic_examples_support_words_and_both_output(self):
        for request, _numeric, words, both in _SYMBOLIC_EXAMPLES:
            with self.subTest(request=request, output="words"):
                self.assertEqual(calculate(request, output="words"), words)
            with self.subTest(request=request, output="both"):
                self.assertEqual(calculate(request, output="both"), both)

    def test_unsupported_and_malformed_requests_raise_value_error(self):
        for request in ("what is the answer to everything", "1 + )"):
            with self.subTest(request=request):
                with self.assertRaises(ValueError):
                    calculate(request)


class EndToEndCliTests(unittest.TestCase):
    def invoke_cli(self, *arguments):
        return subprocess.run(
            [sys.executable, "-m", "calculator", *arguments],
            cwd=_REPOSITORY_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_original_examples_return_required_numeric_results(self):
        cases = (
            (_SYMBOLIC_EXAMPLES[0][0], "6\n"),
            (_BOOK_PRICE_REQUEST, "Rs 132/-\n"),
            (_SYMBOLIC_EXAMPLES[1][0], "3.8\n"),
        )
        for request, expected in cases:
            with self.subTest(request=request):
                result = self.invoke_cli(request)
                self.assertEqual(result.returncode, 0)
                self.assertEqual(result.stdout, expected)
                self.assertEqual(result.stderr, "")

    def test_output_option_and_suffix_inference_on_symbolic_requests(self):
        cases = (
            (("--output", "words", _SYMBOLIC_EXAMPLES[0][0]), "six\n"),
            (("--output=both", _SYMBOLIC_EXAMPLES[1][0]), "3.8 (three point eight)\n"),
            (("--output", "numeric", _SYMBOLIC_EXAMPLES[1][0]), "3.8\n"),
            ((_SYMBOLIC_EXAMPLES[0][0] + " in words",), "six\n"),
            ((_SYMBOLIC_EXAMPLES[1][0] + " as words",), "three point eight\n"),
            ((_SYMBOLIC_EXAMPLES[1][0] + " both",), "3.8 (three point eight)\n"),
        )
        for arguments, expected in cases:
            with self.subTest(arguments=arguments):
                result = self.invoke_cli(*arguments)
                self.assertEqual(result.returncode, 0)
                self.assertEqual(result.stdout, expected)
                self.assertEqual(result.stderr, "")

    def test_unsupported_and_malformed_requests_report_cli_errors(self):
        for request in ("what is the answer to everything", "1 + )"):
            with self.subTest(request=request):
                result = self.invoke_cli(request)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, "")
                self.assertTrue(result.stderr.strip())


if __name__ == "__main__":
    unittest.main()
