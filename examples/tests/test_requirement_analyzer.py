#!/usr/bin/env python3
"""
Test suite for Requirement Analyzer

Validates the requirement analysis system with test cases
"""

import json
import sys
from pathlib import Path
from requirement_analyzer import (
    RequirementFact, Conflict, Dependency, ConflictSeverity
)
from requirement_analyzer_demo import (
    analyze_new_header_files,
    analyze_malloc_requirement,
    analyze_non_docker_dev
)
from kraang import KraangStore


class TestResults:
    """Track test results"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []

    def add_pass(self, test_name: str):
        self.passed += 1
        self.tests.append((test_name, True, None))
        print(f"  ✓ {test_name}")

    def add_fail(self, test_name: str, reason: str):
        self.failed += 1
        self.tests.append((test_name, False, reason))
        print(f"  ✗ {test_name}: {reason}")

    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'='*80}")
        print(f"TEST SUMMARY")
        print(f"{'='*80}")
        print(f"Total: {total}, Passed: {self.passed}, Failed: {self.failed}")
        if self.failed == 0:
            print("✓ All tests passed!")
            return 0
        else:
            print(f"✗ {self.failed} tests failed")
            return 1


def test_scenario_1_new_headers(store: KraangStore, results: TestResults):
    """Test scenario 1: New header files"""
    print("\nTest Scenario 1: New Header Files")

    report = analyze_new_header_files(store)

    # Should have low feasibility
    if report.feasibility_score < 0.3:
        results.add_pass("Feasibility score is low (< 0.3)")
    else:
        results.add_fail("Feasibility score", f"Expected < 0.3, got {report.feasibility_score}")

    # Should have critical conflicts
    critical = [c for c in report.conflicts if c.severity == ConflictSeverity.CRITICAL]
    if len(critical) >= 1:
        results.add_pass("Has critical conflicts (>= 1)")
    else:
        results.add_fail("Critical conflicts", f"Expected >= 1, got {len(critical)}")

    # Should have fact_16 (no new headers)
    has_fact_16 = any(c.existing_fact.id == "fact_16" for c in report.conflicts)
    if has_fact_16:
        results.add_pass("Conflicts with fact_16 (no new headers)")
    else:
        results.add_fail("fact_16 conflict", "Should conflict with 'no new headers' constraint")

    # Should have recommendations
    if len(report.recommendations) > 0:
        results.add_pass("Has recommendations")
    else:
        results.add_fail("Recommendations", "Should have recommendations")

    # Should have impact areas
    if len(report.impact_areas) > 0:
        results.add_pass("Has impact areas")
    else:
        results.add_fail("Impact areas", "Should identify impact areas")


def test_scenario_2_malloc(store: KraangStore, results: TestResults):
    """Test scenario 2: malloc()"""
    print("\nTest Scenario 2: Allow malloc()")

    report = analyze_malloc_requirement(store)

    # Should have low feasibility
    if report.feasibility_score < 0.4:
        results.add_pass("Feasibility score is low (< 0.4)")
    else:
        results.add_fail("Feasibility score", f"Expected < 0.4, got {report.feasibility_score}")

    # Should have critical conflicts
    critical = [c for c in report.conflicts if c.severity == ConflictSeverity.CRITICAL]
    if len(critical) >= 1:
        results.add_pass("Has critical conflicts (>= 1)")
    else:
        results.add_fail("Critical conflicts", f"Expected >= 1, got {len(critical)}")

    # Should have fact_32 (no malloc)
    has_fact_32 = any(c.existing_fact.id == "fact_32" for c in report.conflicts)
    if has_fact_32:
        results.add_pass("Conflicts with fact_32 (no malloc)")
    else:
        results.add_fail("fact_32 conflict", "Should conflict with 'no malloc' constraint")

    # Should mention CREATE macro
    has_create_conflict = any(
        "CREATE" in c.existing_fact.statement
        for c in report.conflicts
    )
    if has_create_conflict:
        results.add_pass("Conflicts with CREATE macro requirement")
    else:
        results.add_fail("CREATE conflict", "Should conflict with CREATE macro")


def test_scenario_3_non_docker(store: KraangStore, results: TestResults):
    """Test scenario 3: Non-Docker development"""
    print("\nTest Scenario 3: Non-Docker Development")

    report = analyze_non_docker_dev(store)

    # Should have moderate feasibility
    if 0.4 <= report.feasibility_score <= 0.8:
        results.add_pass("Feasibility score is moderate (0.4-0.8)")
    else:
        results.add_fail("Feasibility score", f"Expected 0.4-0.8, got {report.feasibility_score}")

    # Should have fewer critical conflicts than scenarios 1 & 2
    critical = [c for c in report.conflicts if c.severity == ConflictSeverity.CRITICAL]
    if len(critical) == 0:
        results.add_pass("No critical conflicts (process policy)")
    else:
        results.add_fail("Critical conflicts", f"Expected 0, got {len(critical)}")

    # Should have dependencies (extends existing)
    if len(report.dependencies) > 0:
        results.add_pass("Has dependencies (extends Docker)")
    else:
        results.add_fail("Dependencies", "Should have dependency on Docker requirement")

    # Should have fact_2 (Docker required)
    has_fact_2 = any(
        c.existing_fact.id == "fact_2" or "Docker" in c.existing_fact.statement
        for c in report.conflicts
    )
    if has_fact_2:
        results.add_pass("Conflicts with Docker requirement")
    else:
        results.add_fail("Docker conflict", "Should conflict with Docker requirement")


def test_data_structures(results: TestResults):
    """Test data structure creation and serialization"""
    print("\nTest Data Structures")

    # Test RequirementFact
    req_fact = RequirementFact(
        statement="Test requirement",
        type="requirement",
        confidence=0.9
    )
    if req_fact.statement == "Test requirement":
        results.add_pass("RequirementFact creation")
    else:
        results.add_fail("RequirementFact", "Failed to create")

    # Test ConflictSeverity enum
    if ConflictSeverity.CRITICAL.value == "critical":
        results.add_pass("ConflictSeverity enum")
    else:
        results.add_fail("ConflictSeverity", "Enum values incorrect")


def test_feasibility_scoring(results: TestResults):
    """Test feasibility scoring logic"""
    print("\nTest Feasibility Scoring")

    # Scenario 1 should be lowest
    store = KraangStore()
    report1 = analyze_new_header_files(store)
    report2 = analyze_malloc_requirement(store)
    report3 = analyze_non_docker_dev(store)

    scores = [
        ("new_headers", report1.feasibility_score),
        ("malloc", report2.feasibility_score),
        ("non_docker", report3.feasibility_score)
    ]

    # Non-Docker should be highest
    if report3.feasibility_score > report1.feasibility_score:
        results.add_pass("Non-Docker has higher feasibility than new headers")
    else:
        results.add_fail("Feasibility ordering", "Non-Docker should be more feasible")

    if report3.feasibility_score > report2.feasibility_score:
        results.add_pass("Non-Docker has higher feasibility than malloc")
    else:
        results.add_fail("Feasibility ordering", "Non-Docker should be more feasible")

    # All scores should be 0-1
    all_valid = all(0.0 <= score <= 1.0 for _, score in scores)
    if all_valid:
        results.add_pass("All scores in valid range [0.0, 1.0]")
    else:
        results.add_fail("Score range", "Some scores out of valid range")


def test_report_structure(results: TestResults):
    """Test report structure completeness"""
    print("\nTest Report Structure")

    store = KraangStore()
    report = analyze_new_header_files(store)

    # Check all required fields exist
    required_fields = [
        'requirement',
        'extracted_facts',
        'conflicts',
        'dependencies',
        'impact_areas',
        'feasibility_score',
        'overall_assessment',
        'recommendations'
    ]

    report_dict = report.to_dict()

    for field in required_fields:
        if field in report_dict:
            results.add_pass(f"Report has '{field}' field")
        else:
            results.add_fail(f"Report field '{field}'", "Missing from report")


def test_json_serialization(results: TestResults):
    """Test JSON serialization of reports"""
    print("\nTest JSON Serialization")

    store = KraangStore()
    report = analyze_new_header_files(store)

    try:
        # Convert to dict
        report_dict = report.to_dict()
        results.add_pass("Report to_dict() conversion")

        # Serialize to JSON
        json_str = json.dumps(report_dict, indent=2)
        results.add_pass("JSON serialization")

        # Deserialize
        loaded = json.loads(json_str)
        results.add_pass("JSON deserialization")

        # Check key fields preserved
        if loaded['feasibility_score'] == report.feasibility_score:
            results.add_pass("Feasibility score preserved in JSON")
        else:
            results.add_fail("JSON preservation", "Feasibility score changed")

    except Exception as e:
        results.add_fail("JSON serialization", str(e))


def test_knowledge_base_access(results: TestResults):
    """Test access to knowledge base facts"""
    print("\nTest Knowledge Base Access")

    store = KraangStore()

    # Should have facts
    facts = store.get_facts()
    if len(facts) > 0:
        results.add_pass(f"Knowledge base has {len(facts)} facts")
    else:
        results.add_fail("Knowledge base", "No facts found")

    # Should have fact_16 (no new headers)
    fact_16 = store.get_fact("fact_16")
    if fact_16 and "header" in fact_16.statement.lower():
        results.add_pass("fact_16 (no new headers) found")
    else:
        results.add_fail("fact_16", "Not found or incorrect")

    # Should have fact_32 (no malloc)
    fact_32 = store.get_fact("fact_32")
    if fact_32 and "malloc" in fact_32.statement.lower():
        results.add_pass("fact_32 (no malloc) found")
    else:
        results.add_fail("fact_32", "Not found or incorrect")

    # Should have fact_2 (Docker required)
    fact_2 = store.get_fact("fact_2")
    if fact_2 and "Docker" in fact_2.statement:
        results.add_pass("fact_2 (Docker required) found")
    else:
        results.add_fail("fact_2", "Not found or incorrect")


def test_conflict_severity_levels(results: TestResults):
    """Test that different scenarios have appropriate severity levels"""
    print("\nTest Conflict Severity Levels")

    store = KraangStore()

    # Scenario 1: Should have CRITICAL
    report1 = analyze_new_header_files(store)
    critical1 = [c for c in report1.conflicts if c.severity == ConflictSeverity.CRITICAL]
    if len(critical1) > 0:
        results.add_pass("Scenario 1 has CRITICAL conflicts")
    else:
        results.add_fail("Scenario 1 severity", "Should have CRITICAL conflicts")

    # Scenario 2: Should have CRITICAL
    report2 = analyze_malloc_requirement(store)
    critical2 = [c for c in report2.conflicts if c.severity == ConflictSeverity.CRITICAL]
    if len(critical2) > 0:
        results.add_pass("Scenario 2 has CRITICAL conflicts")
    else:
        results.add_fail("Scenario 2 severity", "Should have CRITICAL conflicts")

    # Scenario 3: Should have HIGH (not CRITICAL)
    report3 = analyze_non_docker_dev(store)
    high3 = [c for c in report3.conflicts if c.severity == ConflictSeverity.HIGH]
    critical3 = [c for c in report3.conflicts if c.severity == ConflictSeverity.CRITICAL]
    if len(high3) > 0 and len(critical3) == 0:
        results.add_pass("Scenario 3 has HIGH (not CRITICAL) conflicts")
    else:
        results.add_fail("Scenario 3 severity", "Should have HIGH not CRITICAL")


def test_recommendations_quality(results: TestResults):
    """Test that recommendations are actionable"""
    print("\nTest Recommendations Quality")

    store = KraangStore()

    # Each scenario should have multiple recommendations
    scenarios = [
        ("New Headers", analyze_new_header_files(store)),
        ("malloc()", analyze_malloc_requirement(store)),
        ("Non-Docker", analyze_non_docker_dev(store))
    ]

    for name, report in scenarios:
        if len(report.recommendations) >= 3:
            results.add_pass(f"{name}: Has multiple recommendations (>= 3)")
        else:
            results.add_fail(f"{name} recommendations", "Should have >= 3 recommendations")

        # Should include alternatives or actions
        has_action_words = any(
            word in ' '.join(report.recommendations).lower()
            for word in ['alternative', 'instead', 'if', 'should', 'recommend']
        )
        if has_action_words:
            results.add_pass(f"{name}: Recommendations are actionable")
        else:
            results.add_fail(f"{name} recommendations", "Should be actionable")


def main():
    """Run all tests"""
    print("="*80)
    print("REQUIREMENT ANALYZER TEST SUITE")
    print("="*80)

    results = TestResults()
    store = KraangStore()

    # Run test suites
    test_data_structures(results)
    test_knowledge_base_access(results)
    test_scenario_1_new_headers(store, results)
    test_scenario_2_malloc(store, results)
    test_scenario_3_non_docker(store, results)
    test_feasibility_scoring(results)
    test_conflict_severity_levels(results)
    test_report_structure(results)
    test_json_serialization(results)
    test_recommendations_quality(results)

    # Print summary
    return results.summary()


if __name__ == "__main__":
    sys.exit(main())
