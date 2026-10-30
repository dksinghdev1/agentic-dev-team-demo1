"""Safe evaluator for the calculator's symbolic arithmetic grammar."""

import re
import sys
from decimal import Decimal, DecimalException, ROUND_HALF_UP, localcontext


_MAX_SOURCE_LENGTH = 1024
_MAGNITUDE_LIMIT = Decimal("1e100")
_ARITHMETIC_PRECISION = 4096
_PREFIX_RE = re.compile(r"^(?:evaluate|calculate)\s+", re.IGNORECASE)
_NUMBER_RE = re.compile(r"(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)")


class _Parser:
    """Iterative precedence parser and evaluator for tokenized expressions."""

    def __init__(self, tokens):
        self.tokens = tokens

    def parse(self):
        if not self.tokens:
            raise ValueError("expression is empty")
        values = []
        operators = []
        expect_operand = True
        previous_token = None

        for token in self.tokens:
            if _NUMBER_RE.fullmatch(token):
                if not expect_operand:
                    raise ValueError("unexpected number")
                value = Decimal(token)
                self._check_magnitude(value)
                values.append(value)
                expect_operand = False
            elif token == "(":
                if not expect_operand:
                    raise ValueError("unexpected opening parenthesis")
                operators.append(token)
                expect_operand = True
            elif token == ")":
                if expect_operand:
                    raise ValueError("expected an operand before closing parenthesis")
                while operators and operators[-1] != "(":
                    self._apply_operator(operators.pop(), values)
                if not operators:
                    raise ValueError("unmatched closing parenthesis")
                operators.pop()
                while operators and operators[-1] in ("u+", "u-"):
                    self._apply_operator(operators.pop(), values)
                expect_operand = False
            elif token == "%":
                if expect_operand or previous_token == "%":
                    raise ValueError("postfix percent requires a primary expression")
                value = values.pop() / Decimal(100)
                self._check_magnitude(value)
                values.append(value)
                expect_operand = False
            elif token in ("+", "-") and expect_operand:
                # Unary operators associate from right to left.
                operators.append("u" + token)
            elif token in ("+", "-", "*", "/"):
                if expect_operand:
                    raise ValueError("expected an operand")
                while (
                    operators
                    and operators[-1] != "("
                    and self._precedence(operators[-1]) >= self._precedence(token)
                ):
                    self._apply_operator(operators.pop(), values)
                operators.append(token)
                expect_operand = True
            else:
                raise ValueError("unexpected token")
            previous_token = token

        if expect_operand:
            raise ValueError("expression ends where an operand is required")
        while operators:
            operator = operators.pop()
            if operator == "(":
                raise ValueError("missing closing parenthesis")
            self._apply_operator(operator, values)
        if len(values) != 1:
            raise ValueError("malformed expression")
        return values[0]

    @staticmethod
    def _precedence(operator):
        if operator in ("u+", "u-"):
            return 3
        if operator in ("*", "/"):
            return 2
        return 1

    def _apply_operator(self, operator, values):
        if operator in ("u+", "u-"):
            if not values:
                raise ValueError("unary operator is missing an operand")
            value = values.pop()
            if operator == "u-":
                value = -value
            self._check_magnitude(value)
            values.append(value)
            return

        if len(values) < 2:
            raise ValueError("binary operator is missing an operand")
        right = values.pop()
        left = values.pop()
        if operator == "+":
            value = left + right
        elif operator == "-":
            value = left - right
        elif operator == "*":
            value = left * right
        else:
            if right.is_zero():
                raise ZeroDivisionError("division by zero")
            value = left / right
        self._check_magnitude(value)
        values.append(value)

    @staticmethod
    def _check_magnitude(value):
        if not value.is_finite() or abs(value) >= _MAGNITUDE_LIMIT:
            raise ValueError("numeric magnitude must be less than 10**100")


def _tokenize(expression):
    tokens = []
    position = 0
    while position < len(expression):
        if expression[position].isspace():
            position += 1
            continue

        number_match = _NUMBER_RE.match(expression, position)
        if number_match:
            tokens.append(number_match.group())
            position = number_match.end()
            continue

        character = expression[position]
        if character in "+-*/()%":
            tokens.append(character)
            position += 1
            continue

        raise ValueError("unsupported character or syntax")
    return tokens


def evaluate_expression(expression: str) -> Decimal:
    """Evaluate one strict arithmetic expression and return a Decimal.

    Supported syntax consists of decimal literals, parentheses, unary signs,
    binary ``+ - * /``, and a single postfix ``%`` on a primary expression.
    ``evaluate`` and ``calculate`` may optionally prefix the expression.
    """
    if not isinstance(expression, str):
        raise ValueError("expression must be a string")
    if len(expression) > _MAX_SOURCE_LENGTH:
        raise ValueError("expression exceeds the 1024-character limit")

    source = expression.strip()
    prefix_match = _PREFIX_RE.match(source)
    if prefix_match:
        source = source[prefix_match.end():]

    tokens = _tokenize(source)
    try:
        # A fixed high precision keeps finite arithmetic exact for expressions
        # within the source bound and gives repeating divisions ample precision.
        with localcontext() as context:
            context.prec = _ARITHMETIC_PRECISION
            return _Parser(tokens).parse()
    except DecimalException as error:
        raise ValueError("decimal arithmetic is outside supported bounds") from error


_REQUEST_NUMBER_RE = r"[0-9]+(?:\.[0-9]+)?"
_BOOK_PRICE_INCREASE_REQUEST = re.compile(
    rf"^What is the new price of a book if its price has been increased by "
    rf"({_REQUEST_NUMBER_RE})% and the original price is Rs "
    rf"({_REQUEST_NUMBER_RE})/-\?$"
)
_PERCENT_OF_REQUEST_RE = re.compile(
    r"^([0-9]+)%\s+of\s+([0-9]+)$", re.IGNORECASE
)
_ARITHMETIC_REQUEST_RE = re.compile(
    r"^([0-9]+)\s+(plus|minus|times|multiplied\s+by|divided\s+by)\s+([0-9]+)$",
    re.IGNORECASE,
)


def calculate_request(request: str) -> Decimal:
    """Evaluate one approved bounded natural-language request.

    Supported requests are the exact supplied book-price-increase sentence
    with unsigned decimal-digit percentage and price operands, ``X% of Y``
    with unsigned integer digit operands, and one of
    ``X plus Y``, ``X minus Y``, ``X times Y``, ``X multiplied by Y``, or
    ``X divided by Y`` with unsigned integer digit operands. Operator requests
    ignore surrounding whitespace and allow case-insensitive operator names
    with whitespace between tokens. The raw request is limited to 1024
    characters. Unsupported or malformed requests raise ``ValueError``;
    division by zero propagates as ``ZeroDivisionError``.
    """
    if not isinstance(request, str):
        raise ValueError("request must be a string")

    if len(request) > _MAX_SOURCE_LENGTH:
        raise ValueError("request exceeds the 1024-character limit")

    match = _BOOK_PRICE_INCREASE_REQUEST.fullmatch(request)
    if match:
        percentage, original_price = match.groups()
        return evaluate_expression(f"{original_price} * (1 + {percentage}%)")

    source = request.strip()
    if source == "":
        raise ValueError("request is empty")

    match = _PERCENT_OF_REQUEST_RE.fullmatch(source)
    if match:
        left, right = match.groups()
        return evaluate_expression(f"{left}% * {right}")

    match = _ARITHMETIC_REQUEST_RE.fullmatch(source)
    if match:
        left, operator, right = match.groups()
        operator_mapping = {
            "plus": "+",
            "minus": "-",
            "times": "*",
            "multiplied by": "*",
            "divided by": "/",
        }
        normalized_operator = re.sub(r"\s+", " ", operator.lower())
        return evaluate_expression(
            f"{left} {operator_mapping[normalized_operator]} {right}"
        )

    raise ValueError("unsupported or malformed request")


_OUTPUT_MODES = frozenset(("numeric", "words", "both"))
_CURRENCY_QUANTUM = Decimal("0.01")


def _format_decimal(value: Decimal) -> str:
    """Render a finite Decimal in fixed-point notation without redundant zeroes."""
    if value.is_zero():
        return "0"
    rendered = format(value, "f")
    if "." in rendered:
        rendered = rendered.rstrip("0").rstrip(".")
    return rendered


def _under_thousand_words(number: int) -> str:
    ones = (
        "zero", "one", "two", "three", "four", "five", "six", "seven",
        "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen",
        "fifteen", "sixteen", "seventeen", "eighteen", "nineteen",
    )
    tens = (
        "", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy",
        "eighty", "ninety",
    )
    words = []
    hundreds, remainder = divmod(number, 100)
    if hundreds:
        words.extend((ones[hundreds], "hundred"))
    if remainder >= 20:
        ten, unit = divmod(remainder, 10)
        words.append(tens[ten] if unit == 0 else f"{tens[ten]}-{ones[unit]}")
    elif remainder:
        words.append(ones[remainder])
    return " ".join(words)


def _integer_to_words(number: int) -> str:
    if number == 0:
        return "zero"

    chunks = []
    for scale, label in (
        (1_000_000_000_000, "trillion"),
        (1_000_000_000, "billion"),
        (1_000_000, "million"),
        (1_000, "thousand"),
        (1, ""),
    ):
        group, number = divmod(number, scale)
        if group:
            group_words = _under_thousand_words(group)
            chunks.append(group_words if not label else f"{group_words} {label}")
    return " ".join(chunks)


def _number_to_words(value: Decimal) -> str:
    """Convert a bounded finite decimal to English cardinal words."""
    if not value.is_finite() or abs(value) >= Decimal("1e15"):
        raise ValueError("words output requires an absolute value below 10**15")

    rendered = _format_decimal(value)
    negative = rendered.startswith("-")
    if negative:
        rendered = rendered[1:]
    integer_text, separator, fractional_text = rendered.partition(".")
    if len(fractional_text) > 64:
        raise ValueError("words output supports at most 64 fractional digits")

    words = _integer_to_words(int(integer_text))
    if separator:
        digit_words = (
            "zero", "one", "two", "three", "four", "five",
            "six", "seven", "eight", "nine",
        )
        words += " point " + " ".join(
            digit_words[int(digit)] for digit in fractional_text
        )
    if negative:
        words = "negative " + words
    return words


def _request_value(request: str) -> tuple[Decimal, bool]:
    """Route a request to the bounded phrase parser or symbolic evaluator."""
    if not isinstance(request, str):
        raise ValueError("request must be a string")
    currency_request = _BOOK_PRICE_INCREASE_REQUEST.fullmatch(request) is not None
    try:
        return calculate_request(request), currency_request
    except ValueError:
        # The natural-language parser is intentionally narrow. Any other input
        # is still given to the strict symbolic parser, never interpreted as code.
        return evaluate_expression(request), False


def _currency_result(value: Decimal) -> tuple[str, Decimal]:
    """Round a price to paise and return its display form and rounded value."""
    try:
        with localcontext() as context:
            context.prec = _ARITHMETIC_PRECISION
            rounded = value.quantize(_CURRENCY_QUANTUM, rounding=ROUND_HALF_UP)
    except DecimalException as error:
        raise ValueError("currency result is outside supported bounds") from error

    if rounded == rounded.to_integral_value():
        return f"Rs {rounded.to_integral_value():f}/-", rounded
    return f"Rs {rounded:.2f}/-", rounded


def calculate(request: str, output: str = "numeric") -> str:
    """Calculate an approved request and format it as numeric, words, or both."""
    if output not in _OUTPUT_MODES:
        raise ValueError("output must be 'numeric', 'words', or 'both'")

    value, is_currency = _request_value(request)
    if is_currency:
        numeric, words_value = _currency_result(value)
    else:
        numeric = _format_decimal(value)
        words_value = value

    if output == "numeric":
        return numeric

    words = _number_to_words(words_value)
    if output == "words":
        return words
    return f"{numeric} ({words})"


def _parse_cli_arguments(argv: list[str]) -> tuple[str, str | None]:
    """Parse the deliberately small CLI option set without swallowing requests."""
    explicit_output = None
    request_parts = []
    index = 0
    while index < len(argv):
        argument = argv[index]
        if argument == "--output":
            if explicit_output is not None:
                raise ValueError("--output may be specified only once")
            index += 1
            if index >= len(argv):
                raise ValueError("--output requires numeric, words, or both")
            explicit_output = argv[index]
        elif argument.startswith("--output="):
            if explicit_output is not None:
                raise ValueError("--output may be specified only once")
            explicit_output = argument.partition("=")[2]
        elif argument.startswith("--"):
            raise ValueError(f"unrecognized option: {argument}")
        else:
            request_parts.append(argument)
        index += 1

    if len(request_parts) != 1:
        raise ValueError("expected exactly one request argument string")
    return request_parts[0], explicit_output


_CLI_OUTPUT_SUFFIX_RE = re.compile(r"\s+(in words|as words|both)\s*$", re.IGNORECASE)


def main(argv=None) -> int:
    """Run the command-line interface, returning zero on success."""
    arguments = sys.argv[1:] if argv is None else list(argv)
    try:
        request, explicit_output = _parse_cli_arguments(arguments)
        output = explicit_output
        if output is None:
            suffix_match = _CLI_OUTPUT_SUFFIX_RE.search(request)
            if suffix_match:
                suffix = suffix_match.group(1).lower()
                output = "both" if suffix == "both" else "words"
                request = request[:suffix_match.start()].rstrip()
        if output is None:
            output = "numeric"
        result = calculate(request, output=output)
    except (ValueError, ZeroDivisionError) as error:
        print(f"Error: invalid request: {error}", file=sys.stderr)
        return 2

    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
