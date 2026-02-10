#!/bin/bash
# Integration test for coverage commands
# Tests all coverage commands with actual LotJ data

set -e  # Exit on any error

echo "========================================================================"
echo "COVERAGE INTEGRATION TEST"
echo "========================================================================"
echo ""

# Track test results
PASSED=0
FAILED=0

# Test function
test_command() {
    local name="$1"
    local cmd="$2"
    local expected_pattern="$3"

    echo "Testing: $name"
    echo "  Command: $cmd"

    output=$(eval "$cmd" 2>&1)

    if echo "$output" | grep -q "$expected_pattern"; then
        echo "  ✓ PASS"
        PASSED=$((PASSED + 1))
    else
        echo "  ✗ FAIL - Expected pattern not found: $expected_pattern"
        echo "  Output: ${output:0:200}..."
        FAILED=$((FAILED + 1))
    fi
    echo ""
}

# Test 1: Overall coverage command
test_command \
    "Overall Coverage" \
    "python3 kraang.py coverage" \
    "CODE COVERAGE ANALYSIS"

# Test 2: Overall coverage shows statistics
test_command \
    "Coverage Statistics" \
    "python3 kraang.py coverage" \
    "Total Artifacts:"

# Test 3: Overall coverage shows recommendations
test_command \
    "Coverage Recommendations" \
    "python3 kraang.py coverage" \
    "RECOMMENDATIONS"

# Test 4: Artifact detail command
test_command \
    "Artifact Detail" \
    "python3 kraang.py coverage artifact_1" \
    "COVERAGE DETAIL: artifact_1"

# Test 5: Artifact detail shows facts
test_command \
    "Artifact Facts" \
    "python3 kraang.py coverage artifact_1" \
    "EXTRACTED FACTS"

# Test 6: Heat map command
test_command \
    "Heat Map Generation" \
    "python3 kraang.py coverage artifact_1 --heatmap" \
    "Coverage Heat Map:"

# Test 7: Heat map shows legend
test_command \
    "Heat Map Legend" \
    "python3 kraang.py coverage artifact_1 --heatmap" \
    "Legend:"

# Test 8: Gaps analysis command
test_command \
    "Gaps Analysis" \
    "python3 kraang.py coverage --gaps" \
    "COVERAGE GAPS ANALYSIS"

# Test 9: List artifacts command (for reference)
test_command \
    "List Artifacts" \
    "python3 kraang.py list artifacts" \
    "artifact_1"

# Test 10: Help text includes coverage
test_command \
    "Help Text" \
    "python3 kraang.py --help 2>&1" \
    "coverage"

# Test 11: Invalid artifact ID handling
test_command \
    "Invalid Artifact" \
    "python3 kraang.py coverage artifact_999" \
    "Artifact not found"

# Test 12: Code file coverage
test_command \
    "Code File Coverage" \
    "python3 kraang.py coverage artifact_78" \
    "act_comm.c"

echo "========================================================================"
echo "TEST SUMMARY"
echo "========================================================================"
echo "Passed: $PASSED"
echo "Failed: $FAILED"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "✓ All integration tests passed!"
    exit 0
else
    echo "✗ Some integration tests failed"
    exit 1
fi
