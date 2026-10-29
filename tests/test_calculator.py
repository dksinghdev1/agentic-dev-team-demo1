"""Proposed tests for the safe symbolic arithmetic core.

Proposed public API under test:
``calculator.evaluate_expression(expression: str) -> Decimal``. The function
accepts only the approved symbolic grammar and returns an exact
``decimal.Decimal``. It raises ``ValueError`` for malformed, unsupported, or
out-of-bounds expressions, and ``ZeroDivisionError`` for division by zero.

The proposed safety contract is a maximum raw source length of 1024
characters (inclusive) and an absolute literal/intermediate/result magnitude
strictly below 10**100. These concrete limits make the approved size and
magnitude-bound requirements verifiable; they can be adjusted by Reviewer
before implementation.
"""

import unittest
from decimal import Decimal

from calculator import evaluate_expression


class EvaluateExpressionTests(unittest.TestCase):
    def test_required_examples(self):
        self.assertEqual(evaluate_expression("3 * 10 / (2 + 3)"), Decimal("6"))
        self.assertEqual(evaluate_expression("4 - 2 / 10"), Decimal("3.8"))

    def test_binary_operators_and_conventional_precedence(self):
        cases = {
            "2 + 3": "5",
            "8 - 3": "5",
            "4 * 3": "12",
            "12 / 4": "3",
            "2 + 3 * 4": "14",
            "(2 + 3) * 4": "20",
            "20 / 5 * 2": "8",
        }
        for expression, expected in cases.items():
            with self.subTest(expression=expression):
                self.assertEqual(evaluate_expression(expression), Decimal(expected))

    def test_decimal_literals(self):
        self.assertEqual(evaluate_expression("1.25 + 2.5"), Decimal("3.75"))
        self.assertEqual(evaluate_expression("0.3 - 0.1"), Decimal("0.2"))

    def test_nested_parentheses(self):
        self.assertEqual(
            evaluate_expression("((2 + 3) * (4 - 1)) / 5"), Decimal("3")
        )

    def test_unary_signs(self):
        cases = {
            "-3": "-3",
            "+3": "3",
            "--3": "3",
            "-(2 + 3)": "-5",
            "2 * -3": "-6",
            "-2 * -3": "6",
        }
        for expression, expected in cases.items():
            with self.subTest(expression=expression):
                self.assertEqual(evaluate_expression(expression), Decimal(expected))

    def test_postfix_percent_is_a_fractional_literal(self):
        self.assertEqual(evaluate_expression("10%"), Decimal("0.1"))
        self.assertEqual(evaluate_expression("10% * 120"), Decimal("12"))
        self.assertEqual(evaluate_expression("2.5% * 200"), Decimal("5"))

    def test_optional_evaluate_and_calculate_prefixes(self):
        self.assertEqual(evaluate_expression("evaluate 3 * 10 / (2 + 3)"), Decimal("6"))
        self.assertEqual(evaluate_expression("calculate 4 - 2 / 10"), Decimal("3.8"))

    def test_rejects_malformed_or_out_of_grammar_syntax(self):
        expressions = (
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
        )
        for expression in expressions:
            with self.subTest(expression=expression):
                with self.assertRaises(ValueError):
                    evaluate_expression(expression)

    def test_division_by_zero_is_explicit(self):
        for expression in ("1 / 0", "1 / (2 - 2)"):
            with self.subTest(expression=expression):
                with self.assertRaises(ZeroDivisionError):
                    evaluate_expression(expression)

    def test_rejects_python_names_calls_attributes_and_indexes(self):
        expressions = (
            "x",
            "pi",
            "__import__('os')",
            "abs(1)",
            "x.y",
            "(1).real",
            "values[0]",
            "1[0]",
        )
        for expression in expressions:
            with self.subTest(expression=expression):
                with self.assertRaises(ValueError):
                    evaluate_expression(expression)

    def test_handles_deep_in_bounds_parentheses_and_unary_chains(self):
        nested_parentheses = "(" * 200 + "1" + ")" * 200
        self.assertEqual(evaluate_expression(nested_parentheses), Decimal("1"))

        unary_chain = "-" * 1000 + "3"
        self.assertEqual(evaluate_expression(unary_chain), Decimal("3"))

    def test_rejects_expressions_over_source_length_bound(self):
        # A valid expression at the inclusive boundary is accepted.
        at_limit = "1" + " " * 1021 + "+1"
        self.assertEqual(len(at_limit), 1024)
        self.assertEqual(evaluate_expression(at_limit), Decimal("2"))

        # 513 one-digit terms and 512 plus signs make a valid 1025-char input.
        expression = "1+" * 512 + "1"
        self.assertEqual(len(expression), 1025)
        with self.assertRaises(ValueError):
            evaluate_expression(expression)

    def test_rejects_literal_and_result_magnitude_over_bound(self):
        # Values below the strict bound are accepted; the bound itself is not.
        self.assertEqual(evaluate_expression("1" + "0" * 99), Decimal("1e99"))
        at_magnitude_bound = "1" + "0" * 100
        with self.assertRaises(ValueError):
            evaluate_expression(at_magnitude_bound)

        # This literal and final result exceed the proposed absolute bound.
        oversized_literal = "1" + "0" * 101
        oversized_result = "*".join(["10"] * 102)
        for expression in (oversized_literal, oversized_result):
            with self.subTest(expression=expression[:32]):
                with self.assertRaises(ValueError):
                    evaluate_expression(expression)

    def test_rejects_over_limit_intermediate_even_if_final_result_is_small(self):
        # The multiplication reaches 10**101 before division returns 1.
        over_limit_product = "*".join(["10"] * 101)
        expression = f"({over_limit_product}) / ({over_limit_product})"
        self.assertLessEqual(len(expression), 1024)
        with self.assertRaises(ValueError):
            evaluate_expression(expression)


if __name__ == "__main__":
    unittest.main()
