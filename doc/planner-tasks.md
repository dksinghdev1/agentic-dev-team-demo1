# Planner Task Breakdown

This file tracks the implementation plan for `doc/calculator-goal.md`.
CALC-3 is complete. CALC-4 is assigned to the Executor for its dedicated
integration-test phase; implementation is blocked until that test set is
approved by the Reviewer.
The task IDs below replace the initial coarse proposals; those proposals are
retained in the history section at the end of this file.

## Initial calculator implementation plan

### Approved initial scope

The orchestrator approved the initial interpretation recorded in
`doc/calculator-goal.md`: provide a Python API and CLI; use decimal arithmetic;
support the stated symbolic grammar (including unary signs and postfix `%`),
bounded natural-language arithmetic/percentage patterns, numeric/words/both
output modes, and clear safe input errors. The goal examples remain required.
This intentionally does not promise general natural-language understanding.

### Dependency order and task details

| ID | Task and scope | Dependencies | Acceptance criteria | Expected tests / validation | Assigned Executor | Status |
|---|---|---|---|---|---|---|
| CALC-0 | Resolve calculator behavior and integration decisions; record approved initial input/output scope. No implementation code. | None | Approved initial scope is recorded in `doc/calculator-goal.md`, including Python API plus CLI, grammar, bounded natural-language forms, output modes, numeric/currency formatting, and safety requirements. | Confirm decisions cover the identified ambiguities and preserve all required examples. | Orchestrator | Complete — initial scope approved |
| CALC-1 | Implement safe symbolic arithmetic parsing and evaluation for the approved expression grammar, including precedence, decimal literals, unary signs, and postfix `%`. | CALC-0 | `3 * 10 / (2 + 3)` evaluates to `6`; `4 - 2 / 10` evaluates to `3.8`; `10% * 120` evaluates to `12`; supported operators follow conventional precedence. Invalid or out-of-scope syntax is rejected safely, with no arbitrary code execution. | Before implementation, Executor supplies a test set and Reviewer approves it. Unit tests cover required examples, each operator, precedence, nested parentheses, unary signs, percentages, malformed input, division by zero, rejected names/calls/attributes/indexes, and configured size/magnitude bounds. Assert the approved decimal behavior. | Executor | Complete — 14 tests pass under Python 3; implementation review approved |
| CALC-2 | Implement bounded natural-language arithmetic and percentage request handling, including the required price increase and `X% of Y`. | CALC-0, CALC-1 | The supplied book-price request returns `Rs 132/-`; supported operator words and `X% of Y` calculate accurately; malformed or unsupported requests fail clearly. | Test exact examples, each supported operator phrase, percentage-of and increase cases, malformed/missing values, unsupported phrasing, and division by zero. Validate no broad natural-language guessing. | Executor | Complete — 25 tests pass; corrective independent implementation review approved |
| CALC-3 | Implement normalized numeric, rupee, and English words rendering plus the `calculate()` API and Python CLI. | CALC-0, CALC-1, CALC-2 | API and CLI return accurate results in numeric, words, and both modes; currency uses two decimals with ROUND_HALF_UP for fractional rupees; words mode supports absolute values below `10**15` and up to 64 fractional digits; numeric output is normalized. | Approved test set is `tests/test_interface.py`; do not alter it. After implementation, run the focused/full suite and report exact commands/results. Test required examples, all output modes, word conversion (including negative/fractional values and limits), rupee integer/fractional formatting and rounding ties, API mode validation, CLI inference/flags/errors, symbolic and bounded natural-language input. | Executor | Complete — all 39 tests pass; implementation re-review approved |
| CALC-4 | End-to-end acceptance validation/integration of the **existing** Python API and CLI. Keep changes strictly limited to integration/acceptance gaps needed for the defined scope; do not rewrite or refactor working calculator behavior unnecessarily. | CALC-1, CALC-2, CALC-3 | Validate the existing API and CLI end-to-end against all three original examples, numeric/words/both output modes, and safe rejection of unsupported input. Preserve the approved API/CLI behavior and avoid unnecessary rewrites. | First create a dedicated CALC-4 integration test set covering API and CLI paths, each of the three original examples, applicable output modes, and clear safe handling of unsupported input. Reviewer must approve this set before any CALC-4 implementation/code changes. After approval, make only necessary integration fixes, run the dedicated integration tests and full suite, and report exact commands/results. Then obtain independent implementation review against this scope and the approved tests; fix and re-review any findings. | Executor | Test set approved; tests not run; implementation not started |

### Workflow gates and current status

- Assignment strategy: sequential execution is selected because CALC-4 is
  dependent on the completed API/CLI and its integration test set must be
  approved before any implementation changes. CALC-0 through CALC-3 are
  complete. CALC-4 is assigned to the Executor for test-set preparation.
- Before any implementation, each Executor must prepare the task test set and
  obtain an explicit Reviewer approval. Changes-required means revise and
  re-review before implementation.
- After implementation, require independent Reviewer review against the
  original goal, approved decisions, and approved test set. Resolve findings
  through the Executor and request re-review.
- CALC-1 test-set review: **approved**, including the later re-review of two
  deep in-bound regression cases (see `doc/reviewer-report.md`). Implementation
  is present in `calculator.py`; all 14 approved tests passed under `python3`.
  The initial independent implementation review found an uncaught recursion
  failure; the parser was changed to an iterative implementation and
  independent implementation re-review was **approved with no actionable
  findings**. PRs: **none created**.
- CALC-0 through CALC-3 are complete. CALC-3's approved interface test set
  remains unchanged; all 39 tests pass, and independent implementation
  re-review is approved after fixing fractional-zero word rendering.
- CALC-4 is assigned to the Executor. The dedicated `tests/test_end_to_end.py`
  set is **approved** by Reviewer (see `doc/reviewer-report.md`). Tests have
  not been run, and CALC-4 implementation has not started. Approval clears
  the test-set gate; implementation and later independent review remain to be
  done. No PR was created for CALC-3.

## Task status log

| Date | Task | Status update |
|---|---|---|
| 2026-10-29 | CALC-0–CALC-4 | Initial concrete plan recorded; all tasks planned and pending assignment. CALC-1–CALC-4 are gated on decisions in CALC-0. No Executor or Reviewer assigned; tests not run; no PR. |
| 2026-10-29 | CALC-0 | Orchestrator approved Python API plus CLI and the bounded behavior documented in `doc/calculator-goal.md`; CALC-0 complete. |
| 2026-10-29 | CALC-1 | Assigned to Executor. Test-set creation/review requested. Implementation remains blocked pending Reviewer approval; tests not run. |
| 2026-10-29 | CALC-1 | Test-set approval confirmed in `doc/reviewer-report.md`; strict Decimal evaluator implemented in `calculator.py`. The initial independent review identified uncaught recursion for valid deep inputs. Added two in-bound regression tests (reviewer-approved), replaced recursive parsing with an iterative precedence parser, and reran `python3 -m unittest discover -s tests -v`: all 14 tests passed. Independent implementation re-review approved with no actionable findings. CALC-2–CALC-4 remain unstarted; no PR created. |
| 2026-10-29 | CALC-2 | Assigned to Executor. Test-set creation/review requested. Implementation remains blocked pending Reviewer approval; tests not run. |
| 2026-10-29 | CALC-2 | Added `tests/test_natural_language.py` specifying the proposed `calculate_request(request: str) -> Decimal` contract and bounded recognized forms. Reviewer approved the proposed test set (see `doc/reviewer-report.md`). The implementation was added in `calculator.py`, the whitespace-boundary bug was fixed, and the full suite ran: `python3 -m unittest discover -s tests -v` passed (22 tests). Independent implementation review was approved; no PR was created. |
| 2026-10-29 | CALC-2 corrective re-review | Corrected the price-increase parser to capture and use requested unsigned decimal percentage and price values; added the inclusive raw-request 1024-character check before parsing; made bounded operator forms case-insensitive and whitespace-tolerant without broadening phrase vocabulary. The approved tests were not changed. One intermediate full-suite run failed on uppercase operator lookup (`KeyError`); after normalization, `python3 -m unittest discover -s tests -v` passed (25 tests). Independent implementation review and refinement re-review are **APPROVED** with no findings. No PR/push/merge. |
| 2026-10-29 | CALC-3 | Orchestrator recorded exact output formatting, currency rounding, word-range, Python API, and CLI behavior in `doc/calculator-goal.md`. Assigned to Executor for test-set creation and Reviewer approval; implementation remains blocked pending approval. |
| 2026-10-29 | CALC-3 test set | Added `tests/test_interface.py` for the proposed `calculate(request: str, output: str = "numeric") -> str` API and `main(argv=None) -> int` CLI. Reviewer returned CHANGES REQUIRED twice; the test set was revised for currency-word scope, complete 64-digit rendering, CLI diagnostics, and numeric normalization, then approved (see `doc/reviewer-report.md`). Tests were not run as requested; implementation remains not started and was not authorized before approval. |
| 2026-10-29 | CALC-3 assignment | Assigned to Executor and moved to in progress. Reviewer approval of `tests/test_interface.py` authorizes implementation; implementation has not started. Approved tests must remain unchanged. CALC-4 stays pending until CALC-3 passes its implementation, test, and independent-review gates. |
| 2026-10-29 | CALC-3 implementation | Implemented `calculate()` numeric/words/both formatting and the CLI in `calculator.py`; the approved tests were not changed. `python3 -m unittest discover -s tests -v` passed all 39 tests. Independent implementation review initially required a fractional-zero rendering fix; re-review approved with no actionable findings. No PR/push/merge; CALC-4 remains pending assignment. |
| 2026-10-29 | CALC-3 completion / CALC-4 assignment | CALC-3 marked complete based on the 39 passing tests and approved independent implementation re-review in `doc/reviewer-report.md`. CALC-4 is assigned to Executor with strict end-to-end acceptance/integration scope for the existing API/CLI; first deliverable is a dedicated test set for Reviewer approval. No CALC-4 code changes are authorized until approval; tests are not run, implementation review and PR status are pending/no PR. |
| 2026-10-29 | CALC-4 test set | Added `tests/test_end_to_end.py` for end-to-end `calculate()` and `python -m calculator` paths through the three required examples, symbolic words/both output, explicit CLI options and suffix inference, and safe API/CLI error handling. Submitted for Reviewer approval; tests were not run and implementation has not started. |
| 2026-10-29 | CALC-4 test-set review | Initial review requested explicit `--output numeric` and `as words` suffix cases; both were added to `tests/test_end_to_end.py`. Reviewer re-review approved the revised test set (see `doc/reviewer-report.md`). Tests remain not run; implementation remains not started. |

## Preserved initial proposals

The original coarse proposals are retained here to preserve planning history:

| Original ID | Original proposal | Prior status |
|---|---|---|
| CALC-1 | Implement safe symbolic arithmetic evaluation. | Pending |
| CALC-2 | Implement percentage and price-increase calculations. | Pending |
| CALC-3 | Support word-based requests and words/symbol result formatting. | Pending |
| CALC-4 | Integrate behavior and validate end-to-end. | Pending |
