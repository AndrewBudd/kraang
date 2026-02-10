#!/usr/bin/env python3
"""
Example: Using Smart Pairing Algorithm as a Module

This demonstrates how to use the SmartPairingAlgorithm class
in your own scripts for relationship analysis.
"""

import json
from smart_pairing import SmartPairingAlgorithm


def main():
    print("Smart Pairing Algorithm - Example Usage")
    print("=" * 60)

    # Step 1: Load your facts
    print("\n1. Loading facts...")
    with open('.kraang/facts.json') as f:
        facts = json.load(f)
    print(f"   Loaded {len(facts)} facts")

    # Step 2: Initialize the algorithm
    print("\n2. Initializing algorithm...")
    algorithm = SmartPairingAlgorithm(facts)
    print(f"   Total possible pairs: {algorithm.total_possible_pairs:,}")

    # Step 3: Generate candidate pairs
    print("\n3. Generating candidate pairs...")
    pairs = algorithm.generate_pairs(
        budget=20,      # Get top 20 pairs
        threshold=15,   # Only pairs with score >= 15
        verbose=False   # Quiet mode
    )
    print(f"   Generated {len(pairs)} high-quality pairs")

    # Step 4: Get statistics
    print("\n4. Statistics:")
    stats = algorithm.get_statistics()
    print(f"   Total candidates: {stats['candidate_pairs']}")
    print(f"   Reduction: {(1-stats['reduction_ratio'])*100:.1f}%")
    print(f"   Score range: {stats['score_range']['min']} - {stats['score_range']['max']}")

    # Step 5: Examine top pairs
    print("\n5. Top 5 Pairs:")
    for i, pair in enumerate(pairs[:5], 1):
        # Get full details
        details = algorithm.get_pair_details(pair['fact1_id'], pair['fact2_id'])

        fact1 = details['fact1']
        fact2 = details['fact2']

        print(f"\n   Pair {i}: {pair['fact1_id']} ↔ {pair['fact2_id']}")
        print(f"   Score: {pair['score']}")
        print(f"   Reasons: {', '.join(pair['reasons'])}")
        print(f"   Type priority: {pair['type_priority']}")
        print(f"   Artifact priority: {pair['artifact_priority']}")
        print(f"   Domain similarity: {pair['domain_similarity']:.2f}")
        print(f"   Entity overlap: {pair['entity_overlap']:.2f}")
        print()
        print(f"   Fact 1 ({fact1['type']}): {fact1['statement'][:70]}...")
        print(f"   Fact 2 ({fact2['type']}): {fact2['statement'][:70]}...")

    # Step 6: Export results
    print("\n6. Exporting results...")
    output_file = '.kraang/example_pairs.json'
    with open(output_file, 'w') as f:
        json.dump(pairs, f, indent=2)
    print(f"   Saved {len(pairs)} pairs to {output_file}")

    # Step 7: Use cases
    print("\n7. Typical Use Cases:")
    print("   a) Quick exploration: budget=50, threshold=15")
    print("   b) Comprehensive: budget=500, threshold=10")
    print("   c) Deep dive: budget=1000, threshold=5")
    print("   d) Ultra-focused: budget=100, threshold=16")

    print("\n" + "=" * 60)
    print("Example complete!")


if __name__ == '__main__':
    main()
