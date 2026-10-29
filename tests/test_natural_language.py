"""Proposed tests for the bounded natural-language calculation API.

Proposed public contract:
``calculator.calculate_request(request: str) -> decimal.Decimal`` returns a
numeric Decimal for a single recognized request. Malformed or unsupported
requests raise ``ValueError``; division by zero raises ``ZeroDivisionError``.
This API does not format currency or interpret requests beyond the forms
listed below.

The exact recognized forms covered here are:

* The supplied sentence pattern:
  ``What is the new price of a book if its price has been increased by P%
  and the original price is Rs R/-?`` where P and R are unsigned decimal
  digit operands.
* ``X% of Y``, where X and Y are unsigned base-10 integer digit operands.
* ``X plus Y``, ``X minus Y``, ``X times Y``,
  ``X multiplied by Y``, and ``X divided by Y``, where X and Y are
  unsigned base-10 integer digit operands. Each arithmetic request contains
  exactly one operator phrase and exactly two operands; chaining and operator
  precedence are therefore not part of this natural-language grammar.

No general ``what is`` wrapper, number-word operands, synonyms, or broader
natural-language interpretation is implied. Operator forms are case
insensitive and allow ordinary whitespace between tokens; surrounding
whitespace is ignored.
"""

import unittest
from decimal import Decimal

from calculator import calculate_request


class CalculateRequestTests(unittest.TestCase):
    def test_exact_supplied_book_price_increase(self):
        request = (
            "What is the new price of a book if its price has been increased "
            "by 10% and the original price is Rs 120/-?"
        )
        self.assertEqual(calculate_request(request), Decimal("132"))

    def test_book_price_increase_uses_request_percentage_and_price(self):
        cases = {
            "What is the new price of a book if its price has been increased "
            "by 25% and the original price is Rs 80/-?": "100",
            "What is the new price of a book if its price has been increased "
            "by 12.5% and the original price is Rs 20.50/-?": "23.0625",
            "What is the new price of a book if its price has been increased "
            "by 0% and the original price is Rs 120/-?": "120",
        }
        for request, expected in cases.items():
            with self.subTest(request=request):
                self.assertEqual(calculate_request(request), Decimal(expected))

    def test_bounded_percentage_of_form(self):
        self.assertEqual(calculate_request("10% of 120"), Decimal("12"))

    def test_each_approved_arithmetic_operator_phrase(self):
        cases = {
            "23 plus 19": "42",
            "23 minus 19": "4",
            "6 times 7": "42",
            "6 multiplied by 7": "42",
            "84 divided by 7": "12",
        }
        for request, expected in cases.items():
            with self.subTest(request=request):
                self.assertEqual(calculate_request(request), Decimal(expected))

    def test_operator_phrases_are_case_insensitive_and_allow_whitespace(self):
        self.assertEqual(calculate_request(" 2   PLUS  3 "), Decimal("5"))
        self.assertEqual(calculate_request("6\tMULTIPLIED BY\t7"), Decimal("42"))

    def test_rejects_unsupported_phrasing_and_number_words(self):
        requests = (
            "Add 2 and 3",
            "What is 2 plus 3?",
            "twenty plus 3",
            "2 add 3",
            "10 percent of 120",
        )
        for request in requests:
            with self.subTest(request=request):
                with self.assertRaises(ValueError):
                    calculate_request(request)

    def test_rejects_absent_operands_and_incomplete_forms(self):
        requests = (
            "",
            "plus 3",
            "2 plus",
            "10% of",
            "of 120",
            "2 multiplied",
            "2 divided by",
        )
        for request in requests:
            with self.subTest(request=request):
                with self.assertRaises(ValueError):
                    calculate_request(request)

    def test_rejects_duplicate_or_chained_operands(self):
        requests = (
            "2 plus 3 plus 4",
            "2 plus 3 4",
            "10% of 120 of 2",
        )
        for request in requests:
            with self.subTest(request=request):
                with self.assertRaises(ValueError):
                    calculate_request(request)

    def test_rejects_malformed_operator_phrases(self):
        requests = (
            "2 plus plus 3",
            "2 multiplied 3",
            "2 divided 3",
            "2 times by 3",
        )
        for request in requests:
            with self.subTest(request=request):
                with self.assertRaises(ValueError):
                    calculate_request(request)

    def test_division_by_zero_is_explicit(self):
        with self.assertRaises(ZeroDivisionError):
            calculate_request("12 divided by 0")

    def test_natural_language_request_length_boundary(self):
        at_limit = "2" + " " * 509 + "plus" + " " * 509 + "3"
        self.assertEqual(len(at_limit), 1024)
        self.assertEqual(calculate_request(at_limit), Decimal("5"))

        over_limit = "2" + " " * 509 + "plus" + " " * 510 + "3"
        self.assertEqual(len(over_limit), 1025)
        with self.assertRaises(ValueError):
            calculate_request(over_limit)


if __name__ == "__main__":
    unittest.main()
