#!/usr/bin/env python3
"""
Comprehensive Relationship Analysis for LotJ
Generates statistics and identifies critical findings
"""

import json
from collections import defaultdict, Counter
from typing import Dict, List, Set, Tuple

def load_json(path: str) -> any:
    """Load JSON from file."""
    with open(path) as f:
        return json.load(f)

def analyze_relationships(relationships: List[Dict], facts: List[Dict]) -> Dict:
    """Generate comprehensive relationship statistics."""

    # Create fact lookup
    facts_map = {f['id']: f for f in facts}

    # Basic counts
    total_relationships = len(relationships)

    # Relationship type distribution
    type_counts = Counter(r['type'] for r in relationships)

    # Confidence distribution
    confidence_bins = {
        '0.95-1.0': 0,
        '0.90-0.94': 0,
        '0.85-0.89': 0,
        '0.80-0.84': 0,
        'below 0.80': 0
    }

    for r in relationships:
        conf = r['confidence']
        if conf >= 0.95:
            confidence_bins['0.95-1.0'] += 1
        elif conf >= 0.90:
            confidence_bins['0.90-0.94'] += 1
        elif conf >= 0.85:
            confidence_bins['0.85-0.89'] += 1
        elif conf >= 0.80:
            confidence_bins['0.80-0.84'] += 1
        else:
            confidence_bins['below 0.80'] += 1

    # Find all facts involved in relationships
    facts_with_relationships = set()
    for r in relationships:
        facts_with_relationships.add(r['fact_id_1'])
        facts_with_relationships.add(r['fact_id_2'])

    # Calculate relationship density
    total_facts = len(facts)
    facts_with_rels = len(facts_with_relationships)
    orphaned_facts = total_facts - facts_with_rels

    # Relationship density = average relationships per fact
    fact_rel_count = defaultdict(int)
    for r in relationships:
        fact_rel_count[r['fact_id_1']] += 1
        fact_rel_count[r['fact_id_2']] += 1

    if facts_with_rels > 0:
        avg_relationships_per_fact = sum(fact_rel_count.values()) / facts_with_rels
    else:
        avg_relationships_per_fact = 0

    # Find most connected facts
    most_connected = sorted(fact_rel_count.items(), key=lambda x: x[1], reverse=True)[:10]

    # Find contradictions
    contradictions = [r for r in relationships if r['type'] == 'contradicts']

    # Analyze fact type combinations
    fact_type_pairs = defaultdict(int)
    for r in relationships:
        fact1 = facts_map.get(r['fact_id_1'])
        fact2 = facts_map.get(r['fact_id_2'])
        if fact1 and fact2:
            pair = tuple(sorted([fact1['type'], fact2['type']]))
            fact_type_pairs[pair] += 1

    # Constraint validation analysis
    constraint_facts = [f for f in facts if f['type'] == 'constraint']
    constraints_with_relationships = [
        f['id'] for f in constraint_facts if f['id'] in facts_with_relationships
    ]
    constraints_validated = len(constraints_with_relationships)
    constraints_orphaned = len(constraint_facts) - constraints_validated

    return {
        'total_relationships': total_relationships,
        'total_facts': total_facts,
        'facts_with_relationships': facts_with_rels,
        'orphaned_facts': orphaned_facts,
        'relationship_types': dict(type_counts),
        'confidence_distribution': confidence_bins,
        'avg_relationships_per_fact': avg_relationships_per_fact,
        'relationship_density': facts_with_rels / total_facts if total_facts > 0 else 0,
        'most_connected_facts': most_connected,
        'contradictions': contradictions,
        'fact_type_pairs': dict(fact_type_pairs),
        'constraint_validation': {
            'total_constraints': len(constraint_facts),
            'validated': constraints_validated,
            'orphaned': constraints_orphaned,
            'validation_rate': constraints_validated / len(constraint_facts) if constraint_facts else 0
        }
    }

def print_report(stats: Dict, facts_map: Dict):
    """Print comprehensive analysis report."""

    print("=" * 80)
    print("LOTJ RELATIONSHIP GRAPH - COMPREHENSIVE ANALYSIS")
    print("=" * 80)

    print("\n" + "=" * 80)
    print("1. OVERALL STATISTICS")
    print("=" * 80)
    print(f"  Total Facts: {stats['total_facts']}")
    print(f"  Total Relationships: {stats['total_relationships']}")
    print(f"  Facts with Relationships: {stats['facts_with_relationships']}")
    print(f"  Orphaned Facts: {stats['orphaned_facts']}")
    print(f"  Relationship Density: {stats['relationship_density']:.2%}")
    print(f"    (% of facts with at least one relationship)")
    print(f"  Avg Relationships per Connected Fact: {stats['avg_relationships_per_fact']:.2f}")

    print("\n" + "=" * 80)
    print("2. RELATIONSHIP TYPE DISTRIBUTION")
    print("=" * 80)
    rel_types = stats['relationship_types']
    for rel_type, count in sorted(rel_types.items(), key=lambda x: x[1], reverse=True):
        pct = count / stats['total_relationships'] * 100 if stats['total_relationships'] > 0 else 0
        print(f"  {rel_type.capitalize():15s}: {count:4d} ({pct:5.1f}%)")

    print("\n" + "=" * 80)
    print("3. CONFIDENCE DISTRIBUTION")
    print("=" * 80)
    for bin_range, count in stats['confidence_distribution'].items():
        pct = count / stats['total_relationships'] * 100 if stats['total_relationships'] > 0 else 0
        print(f"  {bin_range:15s}: {count:4d} ({pct:5.1f}%)")

    print("\n" + "=" * 80)
    print("4. FACT TYPE PAIR ANALYSIS")
    print("=" * 80)
    print("  Most common fact type combinations:")
    fact_type_pairs = sorted(stats['fact_type_pairs'].items(), key=lambda x: x[1], reverse=True)
    for (type1, type2), count in fact_type_pairs[:10]:
        print(f"    {type1} ↔ {type2}: {count}")

    print("\n" + "=" * 80)
    print("5. CONSTRAINT VALIDATION SUMMARY")
    print("=" * 80)
    cv = stats['constraint_validation']
    print(f"  Total Constraints: {cv['total_constraints']}")
    print(f"  Validated (with relationships): {cv['validated']}")
    print(f"  Orphaned (no relationships): {cv['orphaned']}")
    print(f"  Validation Rate: {cv['validation_rate']:.1%}")

    if cv['orphaned'] > 0:
        print("\n  ⚠ Orphaned constraints may indicate:")
        print("    - Missing implementations")
        print("    - Documentation-only requirements")
        print("    - Opportunities for additional relationship discovery")

    print("\n" + "=" * 80)
    print("6. CONTRADICTIONS FOUND")
    print("=" * 80)
    contradictions = stats['contradictions']
    if len(contradictions) == 0:
        print("  ✓ No contradictions detected")
    else:
        print(f"  ⚠ Found {len(contradictions)} contradictions:")
        for i, contradiction in enumerate(contradictions[:10], 1):
            fact1_id = contradiction['fact_id_1']
            fact2_id = contradiction['fact_id_2']
            conf = contradiction['confidence']
            reasoning = contradiction.get('reasoning', 'N/A')

            print(f"\n  {i}. {fact1_id} ↔ {fact2_id} (confidence: {conf})")
            if fact1_id in facts_map and fact2_id in facts_map:
                fact1 = facts_map[fact1_id]
                fact2 = facts_map[fact2_id]
                print(f"     Fact 1 ({fact1['type']}): {fact1['statement'][:80]}...")
                print(f"     Fact 2 ({fact2['type']}): {fact2['statement'][:80]}...")
            print(f"     Reasoning: {reasoning[:150]}...")

        if len(contradictions) > 10:
            print(f"\n  ... and {len(contradictions) - 10} more contradictions")

    print("\n" + "=" * 80)
    print("7. MOST CONNECTED FACTS")
    print("=" * 80)
    print("  Top 10 facts by relationship count:")
    for i, (fact_id, rel_count) in enumerate(stats['most_connected_facts'][:10], 1):
        if fact_id in facts_map:
            fact = facts_map[fact_id]
            print(f"  {i:2d}. {fact_id:10s} ({rel_count} relationships, {fact['type']})")
            print(f"      {fact['statement'][:70]}...")

    print("\n" + "=" * 80)
    print("8. KEY FINDINGS & RECOMMENDATIONS")
    print("=" * 80)

    # Assess relationship density
    density = stats['relationship_density']
    if density >= 0.7:
        print("  ✓ EXCELLENT: High relationship density (>70% of facts connected)")
    elif density >= 0.5:
        print("  ✓ GOOD: Moderate relationship density (50-70% of facts connected)")
    elif density >= 0.3:
        print("  ⚠ FAIR: Low relationship density (30-50% of facts connected)")
    else:
        print("  ✗ POOR: Very low relationship density (<30% of facts connected)")

    # Assess constraint validation
    val_rate = cv['validation_rate']
    if val_rate >= 0.8:
        print("  ✓ EXCELLENT: Most constraints validated (>80%)")
    elif val_rate >= 0.6:
        print("  ✓ GOOD: Majority of constraints validated (60-80%)")
    elif val_rate >= 0.4:
        print("  ⚠ FAIR: Some constraints validated (40-60%)")
    else:
        print("  ✗ POOR: Low constraint validation (<40%)")

    # Contradiction assessment
    if len(contradictions) == 0:
        print("  ✓ EXCELLENT: No contradictions detected")
    elif len(contradictions) <= 5:
        print("  ✓ GOOD: Very few contradictions (1-5)")
    elif len(contradictions) <= 15:
        print("  ⚠ FAIR: Some contradictions detected (6-15)")
    else:
        print("  ✗ CONCERN: Many contradictions detected (>15)")

    # Recommendations
    print("\n  Recommendations:")
    if stats['orphaned_facts'] > 50:
        print("    • Investigate orphaned facts for missing relationships")
    if cv['orphaned'] > 10:
        print("    • Review orphaned constraints for implementation gaps")
    if len(contradictions) > 0:
        print("    • Resolve documented contradictions between facts")
    if density < 0.5:
        print("    • Consider additional relationship discovery passes")

    print("\n" + "=" * 80)

def main():
    """Main analysis function."""

    # Load data
    facts = load_json('/home/budda/Code/kraang/.kraang/facts.json')
    relationships = load_json('/home/budda/Code/kraang/.kraang/relationships.json')

    # Create facts map
    facts_map = {f['id']: f for f in facts}

    # Analyze
    stats = analyze_relationships(relationships, facts)

    # Print report
    print_report(stats, facts_map)

    # Save detailed stats
    with open('/home/budda/Code/kraang/.kraang/relationship_stats.json', 'w') as f:
        # Remove non-serializable items for JSON
        stats_copy = stats.copy()
        stats_copy['contradictions'] = [
            {
                'fact1': c['fact_id_1'],
                'fact2': c['fact_id_2'],
                'confidence': c['confidence']
            }
            for c in stats['contradictions']
        ]
        # Convert tuple keys to strings for fact_type_pairs
        stats_copy['fact_type_pairs'] = {
            f"{k[0]}↔{k[1]}": v for k, v in stats['fact_type_pairs'].items()
        }
        json.dump(stats_copy, f, indent=2)

    print(f"\nDetailed statistics saved to: /home/budda/Code/kraang/.kraang/relationship_stats.json")

if __name__ == '__main__':
    main()
