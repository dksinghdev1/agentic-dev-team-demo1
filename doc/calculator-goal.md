# Calculator Goal

## Objective

Implement a simple calculator that accepts requests expressed in words or mathematical symbols, computes results, and can present results in words or mathematical notation.

## Required operations

- Addition, subtraction, multiplication, and division.
- Percentage calculations, including percentage increases to a price.
- Parentheses and conventional arithmetic precedence for symbolic expressions.

## Example requests and expected results

| Request | Expected result |
|---|---|
| `Evaluate 3 * 10 / (2 + 3)` | `6` |
| `What is the new price of a book if its price has been increased by 10% and the original price is Rs 120/-?` | `Rs 132/-` |
| `4 - 2 / 10` | `3.8` |

When the user requests the result in words, provide a readable verbal rendering as well as respecting the requested format. For example, `6` may be rendered as “six,” and `3.8` as “three point eight.”

## Delivery expectations

- Follow the repository's existing conventions; use Python by default for new implementation when no project convention or task requirement specifies another language.
- Define and test behavior for the required examples and relevant edge cases.
- Keep implementation logic in source code and describe the approach in `doc/executor-report.md`.
- Planner records the full task breakdown and progress in `doc/planner-tasks.md`.
- Reviewer records test-set and implementation review results in `doc/reviewer-report.md`.
- Tests use pytest; install the development dependency with `python3 -m pip install -r requirements-dev.txt` and run the complete suite with `python3 -m pytest -v`.
- `./run_all_tests_cli.sh` runs representative requests through the actual CLI and reports each result.
- Do not report a task complete until the required reviews and test status are reported. Do not describe tests as passed unless they have completed successfully.

This file captures the high-level goal. The orchestrator supplies the exact task, acceptance criteria, constraints, and required tools/MCP context for each run.

## Approved initial implementation scope

- **Interface:** provide both an importable Python API and a command-line interface, using the Python standard library unless repository conventions require otherwise.
- **Symbolic expressions:** support decimal numeric literals, parentheses, unary `+`/`-`, binary `+`, `-`, `*`, `/`, and postfix `%` (a percentage literal, so `10%` is `0.1`) with conventional precedence. Accept optional `evaluate`/`calculate` prefixes. Parse with a strict grammar; never evaluate user input as Python code.
- **Natural-language calculations:** support the supplied price-increase wording and a bounded common `X% of Y` form. Support simple arithmetic expressed with digit operands and the words “plus”, “minus”, “times”/“multiplied by”, and “divided by”. Do not attempt open-ended natural-language interpretation; reject unsupported requests clearly.
- **Output modes:** the API accepts `numeric`, `words`, or `both`; default is `numeric`. The CLI uses numeric output unless the request explicitly asks for “in words” or “as words”; an explicit “both” request returns both forms.
- **Numbers and currency:** use decimal arithmetic. Avoid rounding intermediate results; render normalized numeric results without unnecessary trailing zeroes. Format currency in rupees, omitting paise for whole rupees and rounding fractional rupees to two decimal places using `ROUND_HALF_UP`. Convert finite decimal results to English words, using “point” followed by decimal digits; support absolute values below `10**15` and at most 64 fractional digits in words mode.
- **Output contract:** `calculator.calculate(request, output="numeric")` returns a string; `output` is one of `numeric`, `words`, or `both`. Numeric results use normalized decimal notation, while price-increase requests use `Rs N/-` notation. Words mode returns the verbal form only; both mode returns the numeric form followed by the words in parentheses. The CLI is `python -m calculator [--output numeric|words|both] REQUEST`; absent `--output`, a trailing “in words”/“as words” or “both” selects the corresponding mode, otherwise numeric is the default.
- **Errors and safety:** reject malformed, unsupported, or excessively long inputs with a clear error; handle division by zero explicitly; do not use `eval` or `exec`. Add reasonable expression-size and numeric-magnitude limits.

These are the initial release boundaries, not a claim of general natural-language understanding. Tests must cover all three supplied examples and the behaviors above.
