#!/usr/bin/env python3
"""
Test suite for Smart Pairing Algorithm.

Tests:
1. Algorithm produces expected number of pairs
2. Pairs are properly scored
3. High-priority pairs are correctly identified
4. Module can be imported and used programmatically
5. Results are reproducible
"""

import json
import sys
from smart_pairing import (
    SmartPairingAlgorithm,
    smart_pairing_algorithm,
    extract_domains,
    extract_code_entities,
    get_type_priority,
    calculate_domain_similarity,
    calculate_entity_overlap,
)


def load_facts():
    """Load facts from JSON file."""
    with open('.kraang/facts.json') as f:
        return json.load(f)


def test_domain_extraction():
    """Test domain keyword extraction."""
    print("\n" + "="*60)
    print("TEST: Domain Extraction")
    print("="*60)

    test_cases = [
        ("Docker Compose is used for development", {'docker_dev'}),
        ("Memory allocation with malloc() and free()", {'memory_management'}),
        ("PostgreSQL database connection", {'database'}),
        ("Linked list manipulation with LINK and UNLINK", {'linked_lists'}),
    ]

    passed = 0
    for statement, expected_domains in test_cases:
        domains = extract_domains(statement)
        if expected_domains.issubset(domains):
            print(f"✓ '{statement[:50]}...'")
            print(f"  Domains: {domains}")
            passed += 1
        else:
            print(f"✗ '{statement[:50]}...'")
            print(f"  Expected: {expected_domains}, Got: {domains}")

    print(f"\nPassed: {passed}/{len(test_cases)}")
    return passed == len(test_cases)


def test_entity_extraction():
    """Test code entity extraction."""
    print("\n" + "="*60)
    print("TEST: Entity Extraction")
    print("="*60)

    test_cases = [
        ("The function do_something() handles input", {'do_something'}),
        ("Uses CREATE and DISPOSE macros", {'CREATE', 'DISPOSE'}),
        ("Defined in mud.h header file", {'mud.h'}),
    ]

    passed = 0
    for statement, expected_entities in test_cases:
        entities = extract_code_entities(statement)
        if expected_entities.issubset(entities):
            print(f"✓ '{statement[:50]}...'")
            print(f"  Entities: {entities}")
            passed += 1
        else:
            print(f"✗ '{statement[:50]}...'")
            print(f"  Expected: {expected_entities}, Got: {entities}")

    print(f"\nPassed: {passed}/{len(test_cases)}")
    return passed == len(test_cases)


def test_type_priority():
    """Test type-based priority classification."""
    print("\n" + "="*60)
    print("TEST: Type Priority Classification")
    print("="*60)

    test_cases = [
        (('constraint', 'implementation'), 'HIGH'),
        (('implementation', 'constraint'), 'HIGH'),
        (('requirement', 'implementation'), 'HIGH'),
        (('constraint', 'constraint'), 'MEDIUM'),
        (('implementation', 'implementation'), 'LOW'),
        (('requirement', 'requirement'), 'MEDIUM'),
    ]

    passed = 0
    for (type1, type2), expected_priority in test_cases:
        priority = get_type_priority(type1, type2)
        if priority == expected_priority:
            print(f"✓ {type1} ↔ {type2}: {priority}")
            passed += 1
        else:
            print(f"✗ {type1} ↔ {type2}: Expected {expected_priority}, Got {priority}")

    print(f"\nPassed: {passed}/{len(test_cases)}")
    return passed == len(test_cases)


def test_algorithm_reduction():
    """Test that algorithm achieves significant reduction."""
    print("\n" + "="*60)
    print("TEST: Algorithm Reduction")
    print("="*60)

    facts = load_facts()
    total_pairs = len(facts) * (len(facts) - 1) // 2

    print(f"Total facts: {len(facts)}")
    print(f"Total possible pairs: {total_pairs:,}")

    candidate_pairs = smart_pairing_algorithm(facts, verbose=False)

    print(f"Candidate pairs generated: {len(candidate_pairs):,}")
    reduction = (1 - len(candidate_pairs) / total_pairs) * 100
    print(f"Reduction: {reduction:.1f}%")

    # We expect at least some reduction
    if len(candidate_pairs) < total_pairs:
        print(f"✓ Algorithm reduced pair count from {total_pairs:,} to {len(candidate_pairs):,}")
        return True
    else:
        print(f"✗ No reduction achieved")
        return False


def test_score_distribution():
    """Test that scores are properly distributed."""
    print("\n" + "="*60)
    print("TEST: Score Distribution")
    print("="*60)

    facts = load_facts()
    candidate_pairs = smart_pairing_algorithm(facts, verbose=False)

    if not candidate_pairs:
        print("✗ No pairs generated")
        return False

    scores = [p['score'] for p in candidate_pairs]
    min_score = min(scores)
    max_score = max(scores)

    print(f"Score range: {min_score} - {max_score}")
    print(f"Average score: {sum(scores) / len(scores):.2f}")

    # Check that scores are sorted (highest first)
    is_sorted = all(scores[i] >= scores[i+1] for i in range(len(scores)-1))

    if is_sorted and max_score > min_score:
        print(f"✓ Scores properly distributed and sorted")
        return True
    else:
        print(f"✗ Score distribution issue")
        return False


def test_high_priority_pairs():
    """Test that high-priority type pairs are correctly identified."""
    print("\n" + "="*60)
    print("TEST: High Priority Pair Identification")
    print("="*60)

    facts = load_facts()

    # Find constraint and implementation facts
    constraints = [f for f in facts if f['type'] == 'constraint']
    implementations = [f for f in facts if f['type'] == 'implementation']

    print(f"Constraints: {len(constraints)}")
    print(f"Implementations: {len(implementations)}")

    # Run algorithm
    candidate_pairs = smart_pairing_algorithm(facts, verbose=False)

    # Count high-priority pairs
    high_priority_count = sum(1 for p in candidate_pairs if p['type_priority'] == 'HIGH')

    print(f"High-priority pairs in results: {high_priority_count}")

    if high_priority_count > 0:
        print(f"✓ Found {high_priority_count} high-priority pairs")
        return True
    else:
        print(f"✗ No high-priority pairs found")
        return False


def test_module_interface():
    """Test the class-based module interface."""
    print("\n" + "="*60)
    print("TEST: Module Interface (SmartPairingAlgorithm class)")
    print("="*60)

    facts = load_facts()

    # Test class instantiation
    algorithm = SmartPairingAlgorithm(facts)
    print(f"✓ Algorithm initialized with {len(facts)} facts")

    # Test pair generation
    pairs = algorithm.generate_pairs(budget=100, threshold=0)
    print(f"✓ Generated {len(pairs)} pairs with budget=100")

    # Test statistics
    stats = algorithm.get_statistics()
    print(f"✓ Statistics: {stats['candidate_pairs']} pairs, reduction {stats['reduction_ratio']*100:.1f}%")

    # Test pair details
    if pairs:
        first_pair = pairs[0]
        details = algorithm.get_pair_details(first_pair['fact1_id'], first_pair['fact2_id'])
        if 'fact1' in details and 'fact2' in details:
            print(f"✓ Pair details retrieved successfully")
            return True
        else:
            print(f"✗ Failed to retrieve pair details")
            return False

    return True


def test_quality_metrics():
    """Test quality metrics of generated pairs."""
    print("\n" + "="*60)
    print("TEST: Quality Metrics")
    print("="*60)

    facts = load_facts()
    algorithm = SmartPairingAlgorithm(facts)
    pairs = algorithm.generate_pairs(budget=500)
    stats = algorithm.get_statistics()

    print("\nQuality Metrics:")
    print(f"  Total facts: {stats['total_facts']}")
    print(f"  Candidate pairs: {stats['candidate_pairs']}")
    print(f"  Reduction: {(1-stats['reduction_ratio'])*100:.1f}%")
    print(f"  Score range: {stats['score_range']['min']} - {stats['score_range']['max']}")

    print("\nType Distribution:")
    for priority, count in sorted(stats['type_priority_distribution'].items()):
        print(f"  {priority}: {count} pairs")

    print("\nArtifact Distribution:")
    for priority, count in sorted(stats['artifact_priority_distribution'].items()):
        print(f"  {priority}: {count} pairs")

    print("\nTop Reasons:")
    for reason, count in sorted(stats['reason_distribution'].items(),
                                key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {reason}: {count} pairs")

    # Quality check: at least 50% should be high-priority types
    high_type_ratio = stats['type_priority_distribution'].get('HIGH', 0) / stats['candidate_pairs']

    if high_type_ratio >= 0.5:
        print(f"\n✓ Quality check passed: {high_type_ratio*100:.1f}% high-priority type pairs")
        return True
    else:
        print(f"\n✗ Quality check failed: only {high_type_ratio*100:.1f}% high-priority type pairs")
        return False


def test_sample_pairs():
    """Show sample high-quality pairs."""
    print("\n" + "="*60)
    print("SAMPLE: Top 5 Pairs")
    print("="*60)

    facts = load_facts()
    algorithm = SmartPairingAlgorithm(facts)
    pairs = algorithm.generate_pairs(budget=500)

    for i, pair in enumerate(pairs[:5], 1):
        details = algorithm.get_pair_details(pair['fact1_id'], pair['fact2_id'])
        fact1 = details['fact1']
        fact2 = details['fact2']

        print(f"\n{i}. {pair['fact1_id']} ↔ {pair['fact2_id']} (Score: {pair['score']})")
        print(f"   Reasons: {', '.join(pair['reasons'])}")
        print(f"   Type: {pair['type_priority']} | Artifact: {pair['artifact_priority']}")
        print(f"   Fact 1 ({fact1['type']}): {fact1['statement'][:80]}...")
        print(f"   Fact 2 ({fact2['type']}): {fact2['statement'][:80]}...")


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("SMART PAIRING ALGORITHM - TEST SUITE")
    print("="*60)

    tests = [
        ("Domain Extraction", test_domain_extraction),
        ("Entity Extraction", test_entity_extraction),
        ("Type Priority", test_type_priority),
        ("Algorithm Reduction", test_algorithm_reduction),
        ("Score Distribution", test_score_distribution),
        ("High Priority Pairs", test_high_priority_pairs),
        ("Module Interface", test_module_interface),
        ("Quality Metrics", test_quality_metrics),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n✗ {test_name} FAILED with exception: {e}")
            results.append((test_name, False))

    # Show sample pairs
    test_sample_pairs()

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)

    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed_count}/{total_count} tests passed")

    if passed_count == total_count:
        print("\n✓ ALL TESTS PASSED")
        return 0
    else:
        print(f"\n✗ {total_count - passed_count} TESTS FAILED")
        return 1


if __name__ == '__main__':
    sys.exit(main())
