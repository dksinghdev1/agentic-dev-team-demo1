# Calculator

A small Python calculator that evaluates arithmetic expressions and a bounded
set of natural-language requests. Results can be shown as numbers, English
words, or both.

## Features

- Addition, subtraction, multiplication, and division with conventional
  precedence and parentheses.
- Decimal operands and postfix percentages, such as `10% * 120`.
- Bounded worded requests, including `23 plus 19`, `10% of 120`, and price
  increases such as the example below. It is not a general-purpose
  natural-language parser.
- Numeric, words, and combined output.
- An importable Python API and command-line interface.
- Strict expression parsing, input-size and magnitude bounds, and explicit
  errors for unsupported input and division by zero.

## Requirements

- Python 3.10 or later.
- For running tests, install the development dependency:

  ```bash
  python3 -m pip install -r requirements-dev.txt
  ```

## Command-line usage

Run one request as a quoted shell argument:

```bash
python3 -m calculator "Evaluate 3 * 10 / (2 + 3)"
# 6

python3 -m calculator "What is the new price of a book if its price has been increased by 10% and the original price is Rs 120/-?"
# Rs 132/-

python3 -m calculator "4 - 2 / 10"
# 3.8
```

Select an output format explicitly:

```bash
python3 -m calculator --output words "3.8"
# three point eight

python3 -m calculator --output both "6"
# 6 (six)
```

Without `--output`, a trailing `in words`, `as words`, or `both` selects that
format. Numeric output is the default.

## Python API

```python
from calculator import calculate, calculate_request, evaluate_expression

value = evaluate_expression("3 * 10 / (2 + 3)")  # Decimal("6")
price = calculate_request("10% of 120")          # Decimal("12")
display = calculate("4 - 2 / 10", output="words")
# "three point eight"
```

`evaluate_expression()` and `calculate_request()` return `decimal.Decimal`.
`calculate()` returns a formatted string and accepts `numeric`, `words`, or
`both` for its `output` argument.

## Tests

Run all tests with pytest:

```bash
python3 -m pytest -v
```

Run representative requests through the actual CLI:

```bash
./run_all_tests_cli.sh
```

## Project layout

- `.github/agents/` — Planner, Executor, and Reviewer custom-agent definitions.
- `calculator.py` — calculator parser, API, formatter, and CLI.
- `tests/` — pytest coverage for expression parsing, natural-language
  requests, the API/CLI, and end-to-end examples.
- `doc/` — goal, task tracking, and agent reports.
