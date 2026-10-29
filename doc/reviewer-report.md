# Reviewer Reports

Reviewer records each test-set and implementation review here, preserving earlier task entries when updating the document.

## Report template

### Task: `<task ID and title>`

#### Test-set review

- **Disposition:** Not reviewed
- **Evidence and requested changes:** None

#### Implementation review

- **Disposition:** Not reviewed
- **Findings:** None
- **Tests/checks:** Not run
- **Blockers or unverified areas:** None reported

### Task: CALC-1 — Safe symbolic arithmetic parsing and evaluation

#### Test-set review

- **Disposition:** CHANGES REQUIRED
- **Evidence:** Reviewed `tests/test_calculator.py` against the approved CALC-1 scope in `doc/calculator-goal.md` and `doc/planner-tasks.md`. The proposed set covers both required results (`6` and `3.8`), binary arithmetic and conventional precedence, parentheses, decimals, unary signs, postfix percent, both optional prefixes, malformed syntax, division by zero, rejection of Python names/calls/attributes/indexes, and inputs exceeding the proposed source and magnitude bounds. The test module itself was reviewed; no tests were run.
- **Required changes:**
  1. Add bound-edge coverage for the proposed maximum source length of 1024 characters (an accepted input at the limit, and rejection immediately above it). Current coverage rejects only a 1025-character input.
  2. Add magnitude cases that distinguish the literal, intermediate, and final-result constraints. The current oversized product has an over-limit intermediate and final result, so it does not establish that an over-limit intermediate is rejected when a later operation would bring the final result back below the limit. Add such a case (for example, a multiplication that reaches/exceeds `10**100` followed by division), and make the intended strict boundary (`< 10**100`) explicit with boundary acceptance/rejection cases.
- **Tests/checks:** Not run; this is a test-set review before implementation.
- **Implementation authorization:** Not authorized. The proposed set is not ready to gate implementation until the required cases are added and re-reviewed.

#### Test-set re-review

- **Disposition:** APPROVED
- **Evidence:** Re-reviewed the revised `tests/test_calculator.py` against the CALC-1 scope in `doc/calculator-goal.md` and `doc/planner-tasks.md`, and the two changes required in the prior review. It now accepts a valid 1024-character expression and rejects a valid 1025-character expression; accepts `10**99` and rejects `10**100` under the stated strict `< 10**100` magnitude bound; and rejects an over-limit multiplication intermediate even when subsequent division would produce `1`. The rest of the set covers the required examples, operators/precedence, decimals, parentheses, unary signs, postfix percent, optional prefixes, malformed and unsupported syntax, division by zero, and safe rejection of Python constructs.
- **Tests/checks:** Not run, as requested; this is a proposed test-set review, not implementation validation.
- **Implementation review:** Not performed. This approval is limited to the CALC-1 proposed test set.

#### Implementation review

- **Disposition:** CHANGES REQUIRED
- **Reviewed scope and evidence:** Independently reviewed `calculator.py` against the CALC-1 acceptance criteria in `doc/calculator-goal.md` and `doc/planner-tasks.md`, the approved CALC-1 test set and approval above, and the task status/validation recorded in `doc/executor-report.md`. The implementation uses a strict tokenizer and recursive-descent parser with Decimal arithmetic; no `eval` or `exec` is used. It checks the raw source length and strict magnitude bound and explicitly handles division by zero.
- **Finding (Medium) — Parser depth escapes the documented error contract:** `calculator.py:74-76` recursively parses parenthesized expressions, and `calculator.py:52-55` recursively parses unary signs, without a depth limit or `RecursionError` translation. Valid expressions that are within the 1024-character input limit can therefore raise an uncaught `RecursionError`; independently reproduced with 200 nested parentheses (401 characters) and 1000 unary minus signs (1001 characters). This makes bounded in-scope input fail with an unexpected implementation exception rather than evaluating or being rejected with the documented clear error. **Recommendation:** enforce an explicit nesting/unary-depth bound and raise `ValueError`, or use an iterative parser; add tests for both deep-parenthesis and deep-unary inputs.
- **Tests/checks:** `python3 -m unittest discover -s tests -v` — **PASSED**, 13 tests, exit code 0. Additional direct probes — **FAILED expected error contract** for deep but in-bound nesting and unary chains, both raising `RecursionError` (details above). Source inspection confirmed no `eval`/`exec` use. No CI/check-run status was available or verified; the executor report states no PR was created.
- **Blockers or unverified areas:** CALC-1 only was reviewed; CALC-2/3/4 were not assessed, per request. No PR or CI status was available. All approved tests pass, but the reproduced depth failure remains outstanding.

#### Test-set re-review — deep in-bound expressions

- **Disposition:** APPROVED
- **Reviewed scope and evidence:** Reviewed only the revised deep-expression test in `tests/test_calculator.py`, against the CALC-1 assignment in `doc/calculator-goal.md` and `doc/planner-tasks.md`, the prior approved test set above, and the implementation finding above. The 200-level parenthesized expression is 401 characters, and the 1000-sign unary chain is 1001 characters; both are within the already-approved 1024-character inclusive source bound. They use only the CALC-1 grammar (parentheses, unary signs, and a decimal integer) and assert the expected exact `Decimal("1")` and `Decimal("3")` values. They directly cover the reproduced in-bound recursion failure and do not add natural-language, CLI, formatting, or other out-of-task behavior.
- **Tests/checks:** Not run, as requested; this was a test-only review.
- **Implementation review:** Not performed in this re-review. No implementation files were reviewed or edited.

#### Implementation re-review — deep-expression finding

- **Disposition:** APPROVED
- **Reviewed scope and evidence:** Independently re-reviewed only CALC-1 in `calculator.py` against the assignment, `doc/calculator-goal.md`, `doc/planner-tasks.md`, and the approved test set above. Confirmed the prior uncaught-recursion finding is resolved: `_Parser.parse()` now uses iterative value/operator stacks, and the approved 200-level parenthesis and 1000-sign regression inputs both evaluate within the 1024-character source limit. The tokenizer accepts only decimal literals, whitespace, the approved operators, parentheses, and `%`; the parser enforces operand placement, balanced parentheses, postfix-percent placement, conventional multiplication/division-before-addition/subtraction precedence, and left associativity for binary operators. Unary signs bind before binary operators and work with parenthesized expressions. Decimal arithmetic runs in a local precision-4096 context; source length is checked before stripping prefixes, and literals plus every unary, percent, and binary intermediate/result are checked against the strict `abs(value) < 10**100` bound. Division by zero raises `ZeroDivisionError`; malformed/unsupported syntax and bound violations raise `ValueError`. No `eval`/`exec` path is present. No actionable implementation findings were identified.
- **Tests/checks:** `python3 -m unittest discover -s tests -v` — **PASSED**, 14 tests, exit code 0. Focused probes — **PASSED** for required examples, precedence and associativity, unary/percent combinations, exact decimal addition, deep in-bound expressions, the strict magnitude boundary, malformed/Python-like syntax rejection, and explicit division-by-zero behavior. No CI or PR checks were available to verify.
- **Blockers or unverified areas:** None for the reviewed CALC-1 scope. CI/PR status was unavailable. CALC-2/3/4 were not reviewed, per request.

### Task: CALC-2 — Bounded natural-language arithmetic and percentage requests

#### Test-set review

- **Disposition:** APPROVED
- **Evidence:** Reviewed only `tests/test_natural_language.py` against the CALC-2 scope in `doc/calculator-goal.md`, `doc/planner-tasks.md`, and the task requirements supplied with this review. The proposed tests assert that the exact supplied book-price-increase sentence returns `Decimal("132")`; exercise `X% of Y`; cover digit operands for every approved phrase (`plus`, `minus`, `times`, `multiplied by`, and `divided by`); reject unsupported wording and number words; reject absent, extra, chained, or malformed operand/operator forms; and assert explicit `ZeroDivisionError` for division by zero. The test module explicitly limits the grammar to bounded forms and does not require operator precedence or general natural-language interpretation; the tests likewise do not impose precedence on chained requests.
- **Tests/checks:** Not run, as requested; this was a proposed test-set review only.
- **Implementation review:** Not performed. No implementation code was inspected or modified.


#### Implementation review — CALC-2

- **Disposition:** CHANGES REQUIRED
- **Reviewed scope and evidence:** Independently reviewed `calculate_request` in `calculator.py` against CALC-2 acceptance criteria in `doc/calculator-goal.md` and `doc/planner-tasks.md`, and the approved `tests/test_natural_language.py` set. The exact book-price sentence is recognized and delegates its expression to `evaluate_expression`; percentage-of and each approved operator phrase are full-matched with ASCII digit operands and mapped to symbolic arithmetic through `evaluate_expression`. Chained/unsupported forms fall through to `ValueError`; division by zero propagates from the evaluator as `ZeroDivisionError`. The evaluator retains its 1024-character expression bound, Decimal arithmetic, magnitude checks, strict parser, and no-eval behavior. One scope issue remains: `calculator.py:204` strips the original request before matching, so non-exact inputs with leading/trailing whitespace are accepted (directly verified for `" 10% of 120"`, `"10% of 120 "`, and a newline-wrapped form; each returned `12.0`). This conflicts with the assigned exact/bounded input contract.
- **Finding (Medium) — Non-exact requests are accepted:** `calculator.py:204` (`source = request.strip()`) silently normalizes the entire request before the full-match checks. Thus inputs beyond the exact supplied sentence and expressly specified forms are accepted. **Recommendation:** match the original request without trimming, and add tests asserting that leading/trailing spaces or newlines around a request raise `ValueError` (including the price sentence if it is required to be exact).
- **Tests/checks:** `python3 -m unittest -v tests/test_natural_language.py` — **PASSED**, 8 tests, exit code 0. Direct probe of outer whitespace — **FAILED acceptance boundary**: three padded requests were accepted. No CI/PR status was available or verified.
- **Blockers or unverified areas:** The approved test suite does not cover surrounding whitespace. No other actionable findings were identified in the reviewed CALC-2 behavior; fix and add the boundary tests before approval.


#### Implementation re-review — CALC-2 whitespace fix

- **Disposition:** APPROVED
- **Reviewed scope and evidence:** Independently re-reviewed `calculate_request` in `calculator.py` against the CALC-2 scope in `doc/calculator-goal.md` and `doc/planner-tasks.md`, and the approved `tests/test_natural_language.py` set. The earlier whitespace finding is resolved: the input is no longer stripped or normalized, and the anchored full-match patterns at `calculator.py:182-188` and their use at `207`, `210`, and `215` require exact spelling and canonical single ASCII spaces. The exact book-price sentence is recognized; `X% of Y` and only the five approved digit-operand operator phrases map to expressions passed to `evaluate_expression` (`208`, `213`, `225`). Unsupported, malformed, padded, newline/tab-separated, chained, or incomplete requests end in `ValueError` (`227`). Division-by-zero continues to propagate from the evaluator as `ZeroDivisionError`. The symbolic evaluator remains unchanged with its 1024-character source limit, magnitude checks, strict parser, Decimal context, and no dynamic evaluation path (`calculator.py:7-10`, `154-177`). No actionable findings remain.
- **Tests/checks:** `python3 -m unittest discover -s tests -v` — **PASSED**, 22 tests, exit code 0. Focused exact-match/safety probes — **PASSED**, including padded price sentence and percentage requests, tab/newline/double-space formatting, explicit division by zero, and requests exceeding evaluator bounds. `git diff --check` — **PASSED**. CI/PR checks — **not available / not verified**; no PR status was provided.
- **Blockers or unverified areas:** None for CALC-2. CI/PR status was unavailable. This approval is limited to the requested CALC-2 implementation review.

#### Test-set re-review — revised price, whitespace, and length cases

- **Disposition:** CHANGES REQUIRED
- **Reviewed scope and evidence:** Reviewed only the revised `tests/test_natural_language.py` against the CALC-2 acceptance criteria and approved initial scope in `doc/calculator-goal.md` and `doc/planner-tasks.md`, including the original supplied book-price example. The additional price cases assert distinct percentage/price inputs and results (`25%` of `Rs 80/-` gives `100`; `12.5%` of `Rs 20.50/-` gives `23.0625`; `0%` leaves `Rs 120/-` unchanged), so they require the request values to determine the increase and exercise decimal operands/results. The operator test asserts case-insensitivity, multiple spaces, tabs between phrase tokens, and surrounding whitespace. However, the new length test supplies only 1025 spaces. That input is malformed/empty after whitespace handling and can be rejected for that reason regardless of any total-request-length limit; it does not demonstrate that an otherwise valid request exceeding the bound is rejected.
- **Required changes:** Replace or supplement the whitespace-only over-limit case with a valid recognized request padded so its raw total length exceeds the 1024-character bound, while preserving the contract that surrounding whitespace is ignored for requests within the bound. Prefer a paired boundary test: accept a valid request at exactly 1024 characters and reject the same valid request at 1025 characters. This will make the total-request bound independently verifiable rather than conflating it with malformed-input rejection.
- **Tests/checks:** Not run, as requested; this was a proposed test-set re-review only.
- **Implementation review:** Not performed. No implementation code was inspected or modified.

#### Test-set re-review — valid arithmetic length boundary

- **Disposition:** APPROVED
- **Reviewed scope and evidence:** Re-reviewed only the revised CALC-2 test set in `tests/test_natural_language.py`, focusing on the prior required change. The 1024-character case is a recognized `2 plus 3` request with only whitespace added between its two operands and operator phrase; it asserts the exact length and expects `Decimal("5")`. The 1025-character companion preserves the same valid request structure, asserts its exact length, and expects `ValueError`. Thus the test verifies the inclusive boundary and immediate over-limit rejection without relying on malformed syntax. The variable book-price cases assert different percentage and price values, including decimal percentage/price operands and exact decimal result (`23.0625`), as well as a zero-percent case. The operator coverage also checks case-insensitivity, multiple spaces, tabs between phrase tokens, and surrounding whitespace as specified by this test set.
- **Required changes:** None.
- **Tests/checks:** Not run, as requested; this was a test-set re-review only.
- **Implementation review:** Not performed. No implementation code was inspected or modified.

#### Implementation review — CALC-2 corrective work

- **Disposition:** APPROVED
- **Reviewed scope and evidence:** Independently reviewed the current `calculator.py` implementation against the CALC-2 task and the approved `tests/test_natural_language.py` set. `calculate_request` checks the raw request length against the inclusive 1024-character limit before stripping or matching. Its book-price pattern captures both requested operands, including decimal digits, and builds the calculation from those captures rather than fixed values. The `X% of Y` and arithmetic patterns use full matches; arithmetic operator matching is case-insensitive, accepts the tested surrounding whitespace after trimming, and permits multiple whitespace characters (including tabs) between tokens. The supported arithmetic phrases map only to `+`, `-`, `*`, and `/`; all calculations are delegated to `evaluate_expression`. Unsupported or malformed requests reach `ValueError`, and `ZeroDivisionError` from the evaluator is not swallowed. No broad NLP, synonyms, or number-word handling was added. No actionable implementation findings were identified.
- **Tests/checks:** `python3 -m unittest discover -s tests -v` — **PASSED**, 25 tests, exit code 0. No PR or CI status was available to verify.
- **Blockers or unverified areas:** None for the reviewed CALC-2 task. This review is limited to the requested `calculate_request` corrective work; no claim is made about unassigned CALC-3/CALC-4 scope or CI status.

#### Implementation re-review — CALC-2 narrow refinement (2026-10-29)

- **Disposition:** APPROVED
- **Reviewed scope and evidence:** Independently re-reviewed `calculator.py` and the existing approved `tests/test_natural_language.py` against the requested CALC-2 refinements. The book-price request is checked with a full match against its exact, case-sensitive sentence pattern before any whitespace stripping; its percentage and original-price decimal operands are captured and used to build the calculation expression. The raw request type and 1024-character limit are checked before matching or parsing. The recognized percentage-of and arithmetic forms remain bounded by full-match patterns and digit operands, and their operator wording accepts the configured case-insensitivity and whitespace tolerance; no general language parsing or chaining is introduced. Arithmetic is delegated to `evaluate_expression`, preserving its Decimal behavior and bounds. `ValueError` is used for unsupported/malformed requests and the evaluator's `ZeroDivisionError` propagates. The approved test file was not edited in this review.
- **Findings:** None. No actionable correctness or regression issue was identified for the requested scope.
- **Tests/checks:** `python3 -m unittest discover -s tests -v` — **PASSED**, 25 tests, exit code 0. Targeted probes confirmed case-insensitive and surrounding/multiple-whitespace operator handling, exact matching of the book-price sentence with decimal operands, and calculated decimal output. No PR or CI check status was available to verify.
- **Blockers or unverified areas:** None for the requested CALC-2 refinements. This review does not assess CALC-3/CALC-4 or external CI/PR status.

### Task: CALC-3 — Numeric, rupee, and English words rendering plus API and CLI

#### Test-set review

- **Disposition:** CHANGES REQUIRED
- **Reviewed scope and evidence:** Reviewed only `tests/test_interface.py` against the CALC-3 acceptance criteria in `doc/planner-tasks.md` and the approved behaviors in `doc/calculator-goal.md`. The tests cover the three required examples, API numeric/words/both modes, negative and fractional word rendering, the approved strict magnitude bound (`< 10**15`), the 64-fractional-digit limit, rupee formatting/rounding (including an exact half-paise tie), and CLI explicit modes, suffix inference, numeric default, and error status. The price-increase request strings, including decimal rupee operands at lines 67–75, use the bounded sentence form and decimal operands already covered by the approved CALC-2 natural-language scope. The magnitude boundary inputs at lines 93–99 match the approved strict bound. Tests were not run; implementation code was neither reviewed nor modified.
- **Findings / required changes:**
  1. **Unapproved currency wording contract — lines 78–85 (`test_currency_words_mode`).** The goal specifies numeric `Rs N/-` currency formatting and conversion of finite decimal results to English words, but does not approve adding a currency unit (“rupees”) to words-mode output. The exact `"one hundred thirty-two rupees"` expectation therefore adds an unapproved output contract. Remove/defer this assertion, or obtain approval and record the currency-words convention in the goal before testing it.
  2. **Fractional precision is not actually asserted — lines 101–106 (`test_words_accept_up_to_64_fractional_digits_only`).** The at-limit assertion checks only the `"zero point "` prefix, so it would pass if the converter dropped or truncated any or all of the 64 fractional digits. Assert the complete expected verbal rendering with all 64 digits in order; retain the 65-digit rejection.
  3. **“Useful error” is weakly verified — lines 148–152 (`test_cli_invalid_request_returns_error_status_and_stderr`).** A non-empty stderr assertion does not establish that the message is useful or identifies an invalid/unsupported request. Assert the documented error content/category (or another concrete, approved diagnostic contract) while retaining the nonzero status and empty stdout checks.
- **Non-blocking note:** Lines 58–64 duplicate the same whole-rupee request and expected result already asserted at lines 35–41. Consolidate the duplicate or give it a distinct purpose.
- **Tests/checks:** Not run, as explicitly requested; this is a pre-implementation test-set review. No implementation or CI checks were reviewed.
- **Implementation authorization:** Not authorized. CALC-3 implementation must remain unstarted until the required test-set corrections are reviewed and approved.

#### Test-set re-review — requested corrections

- **Disposition:** CHANGES REQUIRED
- **Reviewed scope and evidence:** Re-reviewed only the revised `tests/test_interface.py` against the CALC-3 task in `doc/planner-tasks.md` and the approved behaviors in `doc/calculator-goal.md`. The three prior requested corrections are present: the currency words-mode case expects only `"one hundred thirty-two"` and makes no currency-unit wording assertion; the 64-fractional-digit case compares the complete expected string containing all 64 spoken digits and retains rejection at 65 digits; and the CLI invalid-request case requires `invalid`, `unsupported`, or `malformed` wording while checking nonzero status and empty stdout. The set also covers the required examples, API output modes, word limits, rupee formatting and half-up tie rounding, CLI explicit modes/suffix inference/default, and invalid API output mode. Tests were not run and implementation code was not reviewed or modified.
- **Remaining finding / required change:**
  1. **Normalized numeric output is not distinguished by a test.** The goal explicitly requires numeric output without unnecessary trailing zeroes, but current numeric assertions (`"6"`, `"3.8"`, `"12"`, and rupee-formatted values) do not exercise a value whose input or arithmetic representation could retain redundant fractional zeroes. Add a concrete API assertion such as `calculate("1.20 + 1.80") == "3"` (or an equivalent case demonstrating removal of trailing zeroes) to verify normalization.
- **Tests/checks:** Not run, as requested. This is a test-set review only; no implementation or CI checks were reviewed.
- **Implementation authorization:** Not authorized. CALC-3 implementation must remain unstarted pending approval of the revised test set.

#### Final test-set re-review — normalized numeric output

- **Disposition:** APPROVED
- **Reviewed scope and evidence:** Re-reviewed only the revised `tests/test_interface.py` against the original CALC-3 task in `doc/planner-tasks.md` and the approved behaviors in `doc/calculator-goal.md`. The previously requested normalization case is now present: `calculate("1.20 + 1.80")` must return `"3"`, directly verifying removal of unnecessary fractional zeroes. The test set also covers the three required examples; numeric, words, and both API output; negative/fractional words; strict word magnitude and 64-digit fractional limits; whole-rupee formatting and fractional currency rounding including a ROUND_HALF_UP tie; invalid API output mode; and CLI explicit output, suffix inference, numeric default, successful stdout/newline, and invalid-request stderr/status. Currency words mode asserts only the approved verbal numeric result and does not impose currency-unit wording. The complete expected verbal string is asserted at the 64-digit boundary.
- **Findings / required changes:** None. This approval is limited to the CALC-3 proposed test set.
- **Tests/checks:** Not run, as requested. No implementation or CI checks were reviewed.
- **Implementation status:** CALC-3 implementation has not started; this approval clears only the test-set gate.

#### Implementation review — CALC-3

- **Disposition:** CHANGES REQUIRED
- **Reviewed scope and evidence:** Independently reviewed `calculator.py` against the CALC-3 task, the approved contract in `doc/calculator-goal.md`, and the approved `tests/test_interface.py`. The public `calculate()` routes symbolic and bounded natural-language requests and supports the three specified output modes; numeric normalization, currency formatting with `ROUND_HALF_UP`, words magnitude/fraction limits, CLI mode selection and suffix inference, and error handling are implemented. The parser and formatting code use only the standard library and do not use `eval` or `exec`. The approved interface tests were not edited.
- **Finding (High) — Fractional zero digits are omitted in words output:** `calculator.py:319-321` passes each fractional digit to `_under_thousand_words()`, which returns an empty string for zero (`calculator.py:273-281`). Reproduced: `calculate("3.08", output="words")` returns `"three point  eight"` rather than `"three point zero eight"`. This loses both the spoken zero and its place in the fractional digits, violating the contract to verbalize fractional digits and causing wrong words output for numbers containing fractional zeroes. **Recommendation:** render each fractional digit explicitly, including `"zero"`, and add tests for internal and leading fractional zeroes (for example `3.08` and `0.001`).
- **Tests/checks:** `python3 -m unittest discover -s tests -v` — **PASSED**, 39 tests, exit code 0. Focused probe for fractional zero words — **FAILED expected behavior**, reproducing the defect above. Additional probes for negative words, decimal normalization, suffix-inferred `both`/`words`, and CLI division-by-zero error status/output behaved as expected. Source inspection found no `eval` or `exec`. No PR/CI status was available to verify.
- **Blockers or unverified areas:** The fractional-zero words defect is outstanding and blocks approval. No PR or external CI checks were available.

#### Implementation re-review — CALC-3 fractional-zero correction

- **Disposition:** APPROVED
- **Reviewed scope and evidence:** Independently re-reviewed the current `calculator.py` against the CALC-3 acceptance criteria in `doc/calculator-goal.md`, the CALC-3 task in `doc/planner-tasks.md`, and the approved `tests/test_interface.py`. The prior finding is resolved: `_number_to_words()` at `calculator.py:319-324` now maps each fractional character through an explicit digit-name tuple containing `"zero"`, preserving every zero and its position, including leading fractional zeroes. The API still returns a string for numeric/words/both modes; normalized numeric rendering, currency formatting with `ROUND_HALF_UP`, words bounds, and CLI explicit mode/suffix/default/error behavior are present and covered by the approved tests. I did not edit the implementation or approved tests.
- **Findings:** None. No remaining actionable correctness, regression, or contract issues were identified in the requested CALC-3 scope.
- **Tests/checks:** `python3 -m unittest discover -s tests -v` — **PASSED**, 39 tests, exit code 0. Focused assertions — **PASSED** for `3.08` → `"three point zero eight"`, `0.001` → `"zero point zero zero one"`, `120.4` → `"one hundred twenty point four"`, normalized numeric and both output, and negative fractional words. The approved interface tests cover the broader API/CLI contract, including all modes, currency rounding, word limits, CLI mode selection and errors.
- **Blockers or unverified areas:** No PR was found for this repository, so PR checks/CI status are unavailable and unverified. This does not block approval of the reviewed implementation; the local full suite and focused regression checks passed.

### Task: CALC-4 — End-to-end acceptance validation/integration

#### Test-set review

- **Disposition:** CHANGES REQUIRED
- **Reviewed scope and evidence:** Reviewed only `tests/test_end_to_end.py` against the CALC-4 test-set acceptance criteria in `doc/planner-tasks.md` and the approved contract in `doc/calculator-goal.md`. The proposed tests exercise the public `calculate()` API and invoke the actual `python -m calculator` CLI in subprocesses. They assert all three original numeric results through both paths; API `words`/`both` for both symbolic examples; CLI explicit `words` and `both` output; suffix-inferred `in words` and `both`; and API `ValueError` plus CLI nonzero status, empty stdout, and nonempty stderr for unsupported and malformed requests. This review did not run tests or inspect implementation behavior. Earlier CALC-1 through CALC-3 reports above are unchanged.
- **Required changes:**
  1. Add a subprocess CLI case for the approved `as words` suffix. The test set currently checks `in words` and `both`, but the approved CLI contract explicitly supports both `in words` and `as words`; end-to-end coverage should exercise both accepted words suffixes.
  2. Add an explicit `--output numeric` CLI case with an asserted numeric result. The current CLI examples exercise numeric only through the default path, while the approved CLI option explicitly accepts `numeric`, `words`, and `both`; the explicit option coverage currently checks only `words` and `both`.
- **Tests/checks:** Not run, as requested. This is a test-set review only; implementation and CI checks were not reviewed.
- **Implementation authorization:** Not authorized. CALC-4 implementation/code changes remain gated on approval of the revised test set.

#### Test-set re-review

- **Disposition:** APPROVED
- **Reviewed scope and evidence:** Re-reviewed only the revised `tests/test_end_to_end.py` against the CALC-4 task in `doc/planner-tasks.md`, the approved contract in `doc/calculator-goal.md`, and the two changes required above. The tests now explicitly invoke CLI `--output numeric` and assert `3.8`, and exercise suffix-inferred `as words` (in addition to `in words` and `both`). The set covers the public API and actual `python -m calculator` subprocess path; all three required numeric results (`6`, `Rs 132/-`, and `3.8`) are asserted through both paths; both symbolic examples are checked through the API in `words` and `both` modes; and CLI explicit mode options and suffix inference are exercised. Unsupported and malformed requests are each asserted to raise API `ValueError`; the corresponding CLI calls assert a nonzero exit status, empty stdout, and nonempty stderr. This remains a test-set-only review; implementation was not reviewed.
- **Findings / required changes:** None. Both items from the prior review are addressed.
- **Tests/checks:** Not run, as requested. No implementation or CI checks were run or reviewed.
- **Implementation authorization:** The CALC-4 proposed test set is approved; the test-set review gate for implementation is cleared. This does not constitute implementation approval.
