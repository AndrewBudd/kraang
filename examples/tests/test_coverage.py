#!/usr/bin/env python3
"""
Test script for coverage analyzer
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from coverage import (
    LocationParser, CoverageAnalyzer, FileCoverage,
    CoverageReport, CoverageLevel
)
from kraang import KraangStore, Artifact


def test_location_parser():
    """Test location parsing"""
    print("Testing LocationParser...")

    parser = LocationParser()

    # Test line range
    lines = parser.parse_location("Lines 100-120")
    assert lines == set(range(100, 121)), f"Expected 100-120, got {lines}"

    # Test with section
    lines = parser.parse_location("Lines 100-120, Section: Foo")
    assert lines == set(range(100, 121)), f"Expected 100-120, got {lines}"

    # Test single line
    lines = parser.parse_location("Line 50")
    assert lines == {50}, f"Expected {{50}}, got {lines}"

    # Test function reference (should return empty)
    lines = parser.parse_location("function do_command")
    assert lines == set(), f"Expected empty set, got {lines}"

    print("✓ LocationParser tests passed")


def test_file_coverage():
    """Test FileCoverage calculations"""
    print("Testing FileCoverage...")

    fc = FileCoverage(
        artifact_id="test_1",
        artifact_type="code",
        path="/test.c",
        total_lines=100,
        covered_lines={10, 11, 12, 20, 21},
        facts_by_line={
            10: ["fact_1"],
            11: ["fact_1"],
            12: ["fact_1"],
            20: ["fact_2", "fact_3"],
            21: ["fact_2"]
        },
        total_facts=3
    )

    # Test coverage percentage
    assert fc.coverage_percentage() == 5.0, "Expected 5% coverage"

    # Test density
    assert fc.density() == 1.2, f"Expected density 1.2, got {fc.density()}"

    # Test coverage level
    assert fc.coverage_level() == CoverageLevel.NONE, "Expected NONE level"

    # Test below target
    assert fc.is_below_target(10.0), "Should be below 10% target"
    assert not fc.is_below_target(4.0), "Should not be below 4% target"

    print("✓ FileCoverage tests passed")


def test_coverage_report():
    """Test CoverageReport calculations"""
    print("Testing CoverageReport...")

    fc1 = FileCoverage(
        artifact_id="test_1",
        artifact_type="code",
        path="/test.c",
        total_lines=100,
        covered_lines=set(range(1, 51)),  # 50 lines
        facts_by_line={},
        total_facts=10
    )

    fc2 = FileCoverage(
        artifact_id="test_2",
        artifact_type="doc",
        path="/test.md",
        total_lines=200,
        covered_lines=set(range(1, 101)),  # 100 lines
        facts_by_line={},
        total_facts=20
    )

    report = CoverageReport(
        file_coverages=[fc1, fc2],
        total_lines=300,
        total_covered_lines=150,
        total_facts=30
    )

    # Test overall percentage
    assert report.overall_percentage() == 50.0, "Expected 50% coverage"

    # Test by type
    code_files = report.by_type("code")
    assert len(code_files) == 1, "Expected 1 code file"
    assert code_files[0].artifact_id == "test_1"

    doc_files = report.by_type("doc")
    assert len(doc_files) == 1, "Expected 1 doc file"

    # Test uncovered files
    fc3 = FileCoverage(
        artifact_id="test_3",
        artifact_type="code",
        path="/test2.c",
        total_lines=100,
        covered_lines=set(),
        facts_by_line={},
        total_facts=0
    )
    report2 = CoverageReport(
        file_coverages=[fc1, fc2, fc3],
        total_lines=400,
        total_covered_lines=150,
        total_facts=30
    )
    uncovered = report2.uncovered_files()
    assert len(uncovered) == 1, "Expected 1 uncovered file"
    assert uncovered[0].artifact_id == "test_3"

    # Test low coverage files
    low = report2.low_coverage_files(threshold=40.0)
    assert len(low) == 0, f"Expected 0 low coverage files, got {len(low)}"

    print("✓ CoverageReport tests passed")


def test_with_real_data():
    """Test with actual LotJ data"""
    print("Testing with real data...")

    # Check if .kraang exists
    kraang_dir = Path(".kraang")
    if not kraang_dir.exists():
        print("⊘ Skipping real data test - .kraang directory not found")
        return

    store = KraangStore()
    analyzer = CoverageAnalyzer(store)

    # Test analyze_all
    report = analyzer.analyze_all()
    print(f"  Found {len(report.file_coverages)} artifacts")
    print(f"  Overall coverage: {report.overall_percentage():.1f}%")

    # Should have some coverage
    assert report.overall_percentage() > 0, "Expected some coverage"

    # Test individual artifact
    artifacts = store.get_artifacts()
    if artifacts:
        coverage = analyzer.analyze_artifact(artifacts[0])
        print(f"  Artifact {artifacts[0].id}: {coverage.coverage_percentage():.1f}% coverage")

        # Test heat map generation
        heatmap = analyzer.generate_heatmap(coverage)
        assert "Coverage Heat Map" in heatmap, "Expected heat map header"
        assert "Legend:" in heatmap, "Expected legend"

    print("✓ Real data tests passed")


def test_location_patterns():
    """Test various location string patterns"""
    print("Testing location patterns...")

    parser = LocationParser()

    test_cases = [
        ("Lines 100-120", set(range(100, 121))),
        ("Line 50", {50}),
        ("Lines 1-3", {1, 2, 3}),
        ("Lines 100-120, Section: Memory", set(range(100, 121))),
        ("Line 42, Section: Init", {42}),
        ("function do_command", set()),
        ("Section: Architecture", set()),
        ("Lines 5-5", {5}),  # Single line as range
    ]

    for location, expected in test_cases:
        result = parser.parse_location(location)
        assert result == expected, f"Failed for '{location}': expected {expected}, got {result}"

    print("✓ Location pattern tests passed")


def main():
    """Run all tests"""
    print("=" * 70)
    print("COVERAGE ANALYZER TEST SUITE")
    print("=" * 70)
    print()

    tests = [
        test_location_parser,
        test_file_coverage,
        test_coverage_report,
        test_location_patterns,
        test_with_real_data,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} error: {e}")
            failed += 1
        print()

    print("=" * 70)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 70)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
