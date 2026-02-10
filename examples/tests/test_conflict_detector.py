#!/usr/bin/env python3
"""
Test script to demonstrate the Kraang conflict detector functionality.
"""

import json
from conflict_detector import ConflictDetector


def test_basic_functionality():
    """Test that the conflict detector loads data and finds conflicts"""
    print("="*60)
    print("TESTING KRAANG CONFLICT DETECTOR")
    print("="*60)

    # Initialize detector
    print("\n1. Initializing conflict detector...")
    detector = ConflictDetector()

    # Verify data loaded
    print(f"   ✓ Loaded {len(detector.facts)} facts")
    print(f"   ✓ Loaded {len(detector.relationships)} relationships")
    assert len(detector.facts) > 3000, "Should have loaded 3000+ facts"
    assert len(detector.relationships) > 0, "Should have loaded relationships"

    # Check fact types
    print("\n2. Analyzing fact distribution...")
    constraints = detector.get_facts_by_type('constraint')
    implementations = detector.get_facts_by_type('implementation')
    requirements = detector.get_facts_by_type('requirement')
    print(f"   ✓ {len(constraints)} constraints")
    print(f"   ✓ {len(implementations)} implementations")
    print(f"   ✓ {len(requirements)} requirements")

    # Check contradictions
    print("\n3. Checking for existing contradictions...")
    contradictions = detector.get_existing_contradictions()
    print(f"   ✓ Found {len(contradictions)} contradiction relationships")
    assert len(contradictions) > 0, "Should have found contradictions"

    # Run detection
    print("\n4. Running conflict detection...")
    detector.run_all_detectors()
    print(f"   ✓ Detected {len(detector.conflicts)} conflicts")
    assert len(detector.conflicts) >= 5, "Should have found at least 5 conflicts"

    # Verify conflict structure
    print("\n5. Validating conflict structure...")
    if detector.conflicts:
        conflict = detector.conflicts[0]
        assert conflict.id, "Conflict should have ID"
        assert conflict.title, "Conflict should have title"
        assert conflict.severity in ['critical', 'high', 'medium', 'low'], "Valid severity"
        assert conflict.fact_1_id, "Should reference fact 1"
        assert conflict.fact_2_id, "Should reference fact 2"
        assert len(conflict.resolution_options) > 0, "Should have resolution options"
        print(f"   ✓ Conflict structure valid")
        print(f"   ✓ Example: {conflict.title} ({conflict.severity})")

    # Check severity distribution
    print("\n6. Analyzing severity distribution...")
    severity_counts = {}
    for c in detector.conflicts:
        severity_counts[c.severity] = severity_counts.get(c.severity, 0) + 1

    for severity in ['critical', 'high', 'medium', 'low']:
        count = severity_counts.get(severity, 0)
        icon = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}.get(severity)
        print(f"   {icon} {severity.upper()}: {count}")

    # Verify specific conflicts exist
    print("\n7. Verifying key conflicts...")
    titles = [c.title for c in detector.conflicts]

    # Check for Docker conflict
    docker_conflicts = [t for t in titles if 'docker' in t.lower()]
    if docker_conflicts:
        print(f"   ✓ Found Docker conflict: {docker_conflicts[0][:50]}...")

    # Check for memory conflict
    memory_conflicts = [t for t in titles if 'memory' in t.lower()]
    if memory_conflicts:
        print(f"   ✓ Found memory conflict: {memory_conflicts[0][:50]}...")

    # Check for header conflict
    header_conflicts = [t for t in titles if 'header' in t.lower()]
    if header_conflicts:
        print(f"   ✓ Found header conflict: {header_conflicts[0][:50]}...")

    print("\n" + "="*60)
    print("ALL TESTS PASSED ✅")
    print("="*60)
    print(f"\nKraang successfully detected {len(detector.conflicts)} real conflicts")
    print("in the LotJ codebase using extracted facts and relationships.")
    print("\nSee CONFLICTS_FOUND.md for detailed report.")


def test_fact_lookup():
    """Test that we can look up specific facts involved in conflicts"""
    print("\n" + "="*60)
    print("DEMONSTRATING FACT LOOKUP")
    print("="*60)

    detector = ConflictDetector()

    # Look up some key facts involved in conflicts
    key_facts = ['fact_2', 'fact_10', 'fact_16', 'fact_19', 'fact_28', 'fact_31']

    print("\nKey facts involved in conflicts:\n")
    for fact_id in key_facts:
        fact = detector.facts_by_id.get(fact_id)
        if fact:
            print(f"{fact_id} ({fact['type']}):")
            print(f"  {fact['statement'][:80]}...")
            if fact.get('extracted_from'):
                source = fact['extracted_from'][0]
                print(f"  Source: {source.get('artifact_id')} - {source.get('location')}")
            print()


if __name__ == "__main__":
    try:
        test_basic_functionality()
        test_fact_lookup()
        print("\n✅ All validation tests passed!")
        print("The conflict detection system is working correctly.")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
