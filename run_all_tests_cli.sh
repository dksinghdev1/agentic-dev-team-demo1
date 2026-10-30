#!/usr/bin/env bash
set -u

PYTHON_BIN="${PYTHON:-python3}"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
    printf 'ERROR: Python interpreter not found: %s\n' "$PYTHON_BIN" >&2
    exit 2
fi

passed=0
failed=0

run_case() {
    local name="$1"
    local request="$2"
    local expected_status="$3"
    local expected_output="${4:-}"
    local actual_output
    local actual_status

    if actual_output=$("$PYTHON_BIN" -m calculator "$request" 2>&1); then
        actual_status=0
    else
        actual_status=$?
    fi

    if [[ "$expected_status" == "success" ]]; then
        if [[ "$actual_status" -eq 0 && "$actual_output" == "$expected_output" ]]; then
            printf 'PASS: %s\n' "$name"
            ((passed += 1))
        else
            printf 'FAIL: %s\n  input: %s\n  expected exit: 0\n  actual exit: %s\n  expected output: %q\n  actual output:   %q\n' \
                "$name" "$request" "$actual_status" "$expected_output" "$actual_output"
            ((failed += 1))
        fi
    elif [[ "$actual_status" -ne 0 ]]; then
        printf 'PASS: %s (rejected as expected)\n' "$name"
        ((passed += 1))
    else
        printf 'FAIL: %s\n  input: %s\n  expected: nonzero exit\n  actual output: %q\n' \
            "$name" "$request" "$actual_output"
        ((failed += 1))
    fi
}

run_case "precedence and parentheses" \
    "Evaluate 3 * 10 / (2 + 3)" success "6"
run_case "division precedence" "4 - 2 / 10" success "3.8"
run_case "percentage price increase" \
    "What is the new price of a book if its price has been increased by 10% and the original price is Rs 120/-?" \
    success "Rs 132/-"
run_case "word output" "6 in words" success "six"
run_case "combined output" "3.8 both" success "3.8 (three point eight)"
run_case "percentage calculation" "10% of 120" success "12"
run_case "unsupported request" "please solve this somehow" failure
run_case "malformed expression" "1 + )" failure

printf '\nSummary: %d passed, %d failed\n' "$passed" "$failed"
if [[ "$failed" -ne 0 ]]; then
    exit 1
fi
