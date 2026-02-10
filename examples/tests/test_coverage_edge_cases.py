#!/usr/bin/env python3
"""
Test edge cases for coverage analysis system.
"""

from coverage import LocationParser, FileCoverage, CoverageLevel
from collections import defaultdict

def test_edge_case_locations():
    """Test edge cases in location parsing"""
    parser = LocationParser()

    tests = [
        # Edge case: Single line
        ("Line 1", {1}),

        # Edge case: Large range
        ("Lines 1-1000", set(range(1, 1001))),

        # Edge case: Mixed with text before
        ("In function foo() at Lines 50-60", {50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60}),

        # Edge case: Mixed with text after
        ("Lines 100-105 in main()", {100, 101, 102, 103, 104, 105}),

        # Edge case: Multiple line references (should get first)
        ("Lines 10-20 and Lines 30-40", {10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20}),

        # Edge case: Comma after range
        ("Lines 5-10, Section: Intro", {5, 6, 7, 8, 9, 10}),

        # Edge case: No line reference
        ("function main()", set()),

        # Edge case: Empty string
        ("", set()),

        # Edge case: Just numbers (no "Line" keyword)
        ("100-200", set()),

        # Edge case: Line at end of sentence
        ("See Line 42.", {42}),

        # Edge case: Line vs Lines
        ("Lines 50-50", {50}),  # Single line with range syntax
    ]

    print("Testing Edge Case Locations...")
    passed = 0
    failed = 0

    for location, expected in tests:
        result = parser.parse_location(location)
        if result == expected:
            print(f"  ✓ '{location[:50]}...' -> {len(result)} lines")
            passed += 1
        else:
            print(f"  ✗ '{location}'")
            print(f"    Expected: {len(expected)} lines")
            print(f"    Got: {len(result)} lines")
            print(f"    Diff: {result.symmetric_difference(expected)}")
            failed += 1

    print(f"\nEdge Cases: {passed} passed, {failed} failed\n")
    return failed == 0

def test_zero_coverage():
    """Test handling of files with zero coverage"""
    print("Testing Zero Coverage...")

    # Create a FileCoverage with no coverage
    fc = FileCoverage(
        artifact_id="test_1",
        artifact_type="code",
        path="/test/empty.c",
        total_lines=100,
        covered_lines=set(),
        facts_by_line={},
        total_facts=0
    )

    checks = []

    # Check percentage is 0
    pct = fc.coverage_percentage()
    if pct == 0.0:
        print(f"  ✓ Zero coverage percentage: {pct}%")
        checks.append(True)
    else:
        print(f"  ✗ Expected 0%, got {pct}%")
        checks.append(False)

    # Check density is 0
    density = fc.density()
    if density == 0.0:
        print(f"  ✓ Zero density: {density}")
        checks.append(True)
    else:
        print(f"  ✗ Expected 0.0 density, got {density}")
        checks.append(False)

    # Check coverage level
    level = fc.coverage_level()
    if level == CoverageLevel.NONE:
        print(f"  ✓ Coverage level: {level.value}")
        checks.append(True)
    else:
        print(f"  ✗ Expected NONE level, got {level.value}")
        checks.append(False)

    print()
    return all(checks)

def test_full_coverage():
    """Test handling of files with 100% coverage"""
    print("Testing Full Coverage...")

    # Create a FileCoverage with full coverage
    covered = set(range(1, 101))  # Lines 1-100
    facts_by_line = {i: [f"fact_{i}"] for i in covered}

    fc = FileCoverage(
        artifact_id="test_2",
        artifact_type="doc",
        path="/test/complete.md",
        total_lines=100,
        covered_lines=covered,
        facts_by_line=facts_by_line,
        total_facts=100
    )

    checks = []

    # Check percentage is 100
    pct = fc.coverage_percentage()
    if pct == 100.0:
        print(f"  ✓ Full coverage percentage: {pct}%")
        checks.append(True)
    else:
        print(f"  ✗ Expected 100%, got {pct}%")
        checks.append(False)

    # Check density is 1 (1 fact per line)
    density = fc.density()
    if density == 1.0:
        print(f"  ✓ Expected density: {density}")
        checks.append(True)
    else:
        print(f"  ✗ Expected 1.0 density, got {density}")
        checks.append(False)

    # Check coverage level
    level = fc.coverage_level()
    if level == CoverageLevel.EXCELLENT:
        print(f"  ✓ Coverage level: {level.value}")
        checks.append(True)
    else:
        print(f"  ✗ Expected EXCELLENT level, got {level.value}")
        checks.append(False)

    print()
    return all(checks)

def test_overlapping_facts():
    """Test handling of multiple facts referencing same lines"""
    print("Testing Overlapping Facts...")

    # Create coverage where multiple facts reference same lines
    covered = {10, 11, 12, 13, 14, 15}
    facts_by_line = {
        10: ["fact_1", "fact_2", "fact_3"],
        11: ["fact_1", "fact_2"],
        12: ["fact_1"],
        13: ["fact_1"],
        14: ["fact_1"],
        15: ["fact_1", "fact_4"],
    }

    fc = FileCoverage(
        artifact_id="test_3",
        artifact_type="code",
        path="/test/overlap.c",
        total_lines=100,
        covered_lines=covered,
        facts_by_line=facts_by_line,
        total_facts=4  # Total unique facts
    )

    checks = []

    # Check coverage percentage
    pct = fc.coverage_percentage()
    expected_pct = 6.0  # 6/100
    if pct == expected_pct:
        print(f"  ✓ Coverage percentage: {pct}%")
        checks.append(True)
    else:
        print(f"  ✗ Expected {expected_pct}%, got {pct}%")
        checks.append(False)

    # Check density (should be > 1 due to overlaps)
    density = fc.density()
    total_refs = sum(len(facts) for facts in facts_by_line.values())
    expected_density = total_refs / len(covered)  # 11 refs / 6 lines = ~1.83
    if abs(density - expected_density) < 0.01:
        print(f"  ✓ Density with overlaps: {density:.2f}")
        checks.append(True)
    else:
        print(f"  ✗ Expected {expected_density:.2f} density, got {density:.2f}")
        checks.append(False)

    print()
    return all(checks)

def test_coverage_levels():
    """Test coverage level categorization"""
    print("Testing Coverage Levels...")

    test_cases = [
        (0, CoverageLevel.NONE),
        (5, CoverageLevel.NONE),
        (10, CoverageLevel.LOW),
        (20, CoverageLevel.LOW),
        (30, CoverageLevel.MODERATE),
        (50, CoverageLevel.MODERATE),
        (60, CoverageLevel.GOOD),
        (75, CoverageLevel.GOOD),
        (80, CoverageLevel.EXCELLENT),
        (95, CoverageLevel.EXCELLENT),
        (100, CoverageLevel.EXCELLENT),
    ]

    passed = 0
    failed = 0

    for pct, expected_level in test_cases:
        # Create coverage with specific percentage
        total = 100
        covered = int(pct)

        fc = FileCoverage(
            artifact_id="test",
            artifact_type="code",
            path="/test/file.c",
            total_lines=total,
            covered_lines=set(range(1, covered + 1)),
            facts_by_line={i: ["fact_1"] for i in range(1, covered + 1)},
            total_facts=1
        )

        level = fc.coverage_level()
        if level == expected_level:
            passed += 1
        else:
            print(f"  ✗ {pct}%: Expected {expected_level.value}, got {level.value}")
            failed += 1

    if failed == 0:
        print(f"  ✓ All {passed} coverage level tests passed")

    print()
    return failed == 0

def main():
    print("=" * 70)
    print("COVERAGE EDGE CASES VALIDATION")
    print("=" * 70)
    print()

    results = []

    results.append(("Edge Case Locations", test_edge_case_locations()))
    results.append(("Zero Coverage", test_zero_coverage()))
    results.append(("Full Coverage", test_full_coverage()))
    results.append(("Overlapping Facts", test_overlapping_facts()))
    results.append(("Coverage Levels", test_coverage_levels()))

    print("=" * 70)
    print("EDGE CASE VALIDATION SUMMARY")
    print("=" * 70)

    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{name:30s} {status}")

    print()

    if all(r[1] for r in results):
        print("✓ All edge case tests passed!")
        return 0
    else:
        print("✗ Some edge case tests failed")
        return 1

if __name__ == "__main__":
    exit(main())
