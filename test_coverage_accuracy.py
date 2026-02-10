#!/usr/bin/env python3
"""
Test coverage accuracy by validating metrics against actual data.
"""

import json
from pathlib import Path
from coverage import LocationParser, CoverageAnalyzer
from kraang import KraangStore

def test_location_parser():
    """Test that LocationParser correctly extracts line numbers"""
    parser = LocationParser()

    tests = [
        ("Lines 7-15, Section: IMPORTANT", {7, 8, 9, 10, 11, 12, 13, 14, 15}),
        ("Line 50", {50}),
        ("Lines 100-120", set(range(100, 121))),
        ("function do_command", set()),  # Should return empty
        ("Section: Architecture", set()),  # Should return empty
        ("Lines 19-21, Section: Codebase Overview", {19, 20, 21}),
    ]

    print("Testing LocationParser...")
    passed = 0
    failed = 0

    for location, expected in tests:
        result = parser.parse_location(location)
        if result == expected:
            print(f"  ✓ '{location}' -> {len(result)} lines")
            passed += 1
        else:
            print(f"  ✗ '{location}'")
            print(f"    Expected: {expected}")
            print(f"    Got: {result}")
            failed += 1

    print(f"\nLocationParser: {passed} passed, {failed} failed\n")
    return failed == 0

def test_coverage_metrics():
    """Test that coverage metrics match expectations"""
    store = KraangStore()
    analyzer = CoverageAnalyzer(store)

    print("Testing Coverage Metrics...")

    # Get artifacts
    artifacts = store.get_artifacts()
    print(f"  Found {len(artifacts)} artifacts")

    # Analyze coverage
    report = analyzer.analyze_all()

    print(f"  Total lines: {report.total_lines:,}")
    print(f"  Covered lines: {report.total_covered_lines:,}")
    print(f"  Overall coverage: {report.overall_percentage():.1f}%")
    print(f"  Total facts: {report.total_facts}")

    # Validate basic sanity checks
    checks = []

    # Check 1: Covered lines should be <= total lines
    if report.total_covered_lines <= report.total_lines:
        print(f"  ✓ Covered lines <= total lines")
        checks.append(True)
    else:
        print(f"  ✗ Covered lines ({report.total_covered_lines}) > total lines ({report.total_lines})")
        checks.append(False)

    # Check 2: Coverage should be between 0 and 100
    pct = report.overall_percentage()
    if 0 <= pct <= 100:
        print(f"  ✓ Coverage percentage in valid range: {pct:.1f}%")
        checks.append(True)
    else:
        print(f"  ✗ Coverage percentage out of range: {pct:.1f}%")
        checks.append(False)

    # Check 3: Each file coverage should be valid
    for fc in report.file_coverages:
        if len(fc.covered_lines) <= fc.total_lines:
            pass  # Valid
        else:
            print(f"  ✗ {fc.path}: covered ({len(fc.covered_lines)}) > total ({fc.total_lines})")
            checks.append(False)

    if all(checks):
        print(f"  ✓ All file coverages valid")

    print()
    return all(checks)

def test_specific_facts():
    """Test specific facts to verify line parsing"""
    store = KraangStore()
    parser = LocationParser()

    print("Testing Specific Facts...")

    facts = store.get_facts()[:5]  # Test first 5 facts

    for fact in facts:
        print(f"\n  {fact.id}: {fact.statement[:60]}...")
        for ref in fact.extracted_from:
            location = ref['location']
            lines = parser.parse_location(location)
            print(f"    Location: {location}")
            print(f"    Parsed to: {len(lines)} lines")
            if lines:
                print(f"    Line range: {min(lines)}-{max(lines)}")

    print()
    return True

def validate_heat_map_buckets():
    """Test that heat map buckets sum correctly"""
    store = KraangStore()
    analyzer = CoverageAnalyzer(store)

    print("Testing Heat Map Bucket Calculation...")

    artifact = store.get_artifact("artifact_1")
    if not artifact:
        print("  ✗ Could not find artifact_1")
        return False

    coverage = analyzer.analyze_artifact(artifact)

    # Generate heat map and validate
    bucket_size = 50
    num_buckets = (coverage.total_lines + bucket_size - 1) // bucket_size

    print(f"  Total lines: {coverage.total_lines}")
    print(f"  Bucket size: {bucket_size}")
    print(f"  Expected buckets: {num_buckets}")

    # Count lines covered per bucket
    bucket_coverage = [0] * num_buckets
    for line in coverage.covered_lines:
        bucket_idx = (line - 1) // bucket_size
        if 0 <= bucket_idx < num_buckets:
            bucket_coverage[bucket_idx] += 1

    total_bucketed = sum(bucket_coverage)

    if total_bucketed == len(coverage.covered_lines):
        print(f"  ✓ All {len(coverage.covered_lines)} covered lines accounted for in buckets")
        return True
    else:
        print(f"  ✗ Bucket mismatch: {total_bucketed} vs {len(coverage.covered_lines)}")
        return False

def main():
    print("=" * 70)
    print("COVERAGE ACCURACY VALIDATION")
    print("=" * 70)
    print()

    results = []

    results.append(("LocationParser", test_location_parser()))
    results.append(("Coverage Metrics", test_coverage_metrics()))
    results.append(("Specific Facts", test_specific_facts()))
    results.append(("Heat Map Buckets", validate_heat_map_buckets()))

    print("=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)

    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{name:30s} {status}")

    print()

    if all(r[1] for r in results):
        print("✓ All validation tests passed!")
        return 0
    else:
        print("✗ Some validation tests failed")
        return 1

if __name__ == "__main__":
    exit(main())
