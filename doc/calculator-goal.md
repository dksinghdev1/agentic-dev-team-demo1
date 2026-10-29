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
- Do not report a task complete until the required reviews and test status are reported. Do not describe tests as passed unless they have completed successfully.

This file captures the high-level goal. The orchestrator supplies the exact task, acceptance criteria, constraints, and required tools/MCP context for each run.
