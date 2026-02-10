#!/usr/bin/env python3
"""
Final Comprehensive Relationship Graph Report for LotJ
Generates complete analysis with statistics, findings, and recommendations
"""

import json
from collections import defaultdict, Counter
from typing import Dict, List, Set
from datetime import datetime

def load_json(path: str):
    """Load JSON from file."""
    with open(path) as f:
        return json.load(f)

def main():
    """Generate comprehensive final report."""

    print("=" * 80)
    print("LOTJ RELATIONSHIP GRAPH - FINAL COMPREHENSIVE REPORT")
    print("=" * 80)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    # Load all data
    facts = load_json('/home/budda/Code/kraang/.kraang/facts.json')
    relationships = load_json('/home/budda/Code/kraang/.kraang/relationships.json')
    candidate_pairs = load_json('/home/budda/Code/kraang/.kraang/candidate_pairs.json')

    facts_map = {f['id']: f for f in facts}

    # === SECTION 1: PROCESSING SUMMARY ===
    print("\n" + "=" * 80)
    print("1. PROCESSING SUMMARY")
    print("=" * 80)

    total_pairs_analyzed = len(candidate_pairs)
    relationships_found = len(relationships)
    progress_pct = relationships_found / total_pairs_analyzed * 100 if total_pairs_analyzed > 0 else 0

    print(f"  Candidate pairs analyzed: {total_pairs_analyzed:,}")
    print(f"  Relationships discovered: {relationships_found:,}")
    print(f"  Analysis completion:      {progress_pct:.1f}%")
    print(f"  Total facts in system:    {len(facts):,}")

    # === SECTION 2: RELATIONSHIP STATISTICS ===
    print("\n" + "=" * 80)
    print("2. RELATIONSHIP STATISTICS")
    print("=" * 80)

    # Type distribution
    type_counts = Counter(r['type'] for r in relationships)
    print("\n  2a. Relationship Types:")
    for rtype in ['supports', 'contradicts', 'extends']:
        count = type_counts.get(rtype, 0)
        pct = count / relationships_found * 100 if relationships_found > 0 else 0
        print(f"      {rtype.capitalize():12s}: {count:4d} ({pct:5.1f}%)")

    # Confidence distribution
    print("\n  2b. Confidence Distribution:")
    conf_bins = {
        '0.95-1.00': [r for r in relationships if r['confidence'] >= 0.95],
        '0.90-0.94': [r for r in relationships if 0.90 <= r['confidence'] < 0.95],
        '0.85-0.89': [r for r in relationships if 0.85 <= r['confidence'] < 0.90],
        '0.80-0.84': [r for r in relationships if 0.80 <= r['confidence'] < 0.85],
        '<0.80':     [r for r in relationships if r['confidence'] < 0.80],
    }

    for bin_name, bin_rels in conf_bins.items():
        count = len(bin_rels)
        pct = count / relationships_found * 100 if relationships_found > 0 else 0
        print(f"      {bin_name:10s}: {count:4d} ({pct:5.1f}%)")

    # === SECTION 3: RELATIONSHIP DENSITY ===
    print("\n" + "=" * 80)
    print("3. RELATIONSHIP DENSITY ANALYSIS")
    print("=" * 80)

    # Find facts involved in relationships
    facts_with_rels = set()
    fact_rel_counts = defaultdict(int)

    for r in relationships:
        facts_with_rels.add(r['fact_id_1'])
        facts_with_rels.add(r['fact_id_2'])
        fact_rel_counts[r['fact_id_1']] += 1
        fact_rel_counts[r['fact_id_2']] += 1

    connected_facts = len(facts_with_rels)
    orphaned_facts = len(facts) - connected_facts
    density = connected_facts / len(facts) * 100 if len(facts) > 0 else 0

    avg_rels_per_fact = sum(fact_rel_counts.values()) / connected_facts if connected_facts > 0 else 0

    print(f"  Total facts:               {len(facts):,}")
    print(f"  Facts with relationships:  {connected_facts:,}")
    print(f"  Orphaned facts:            {orphaned_facts:,}")
    print(f"  Relationship density:      {density:.1f}%")
    print(f"  Avg rels per connected fact: {avg_rels_per_fact:.2f}")

    # Density assessment
    print("\n  Assessment:")
    if density >= 70:
        print("    ✓ EXCELLENT: High relationship density (≥70%)")
    elif density >= 50:
        print("    ✓ GOOD: Moderate relationship density (50-70%)")
    elif density >= 30:
        print("    ⚠ FAIR: Low relationship density (30-50%)")
    else:
        print("    ✗ POOR: Very low relationship density (<30%)")

    # === SECTION 4: CONSTRAINT VALIDATION ===
    print("\n" + "=" * 80)
    print("4. CONSTRAINT VALIDATION SUMMARY")
    print("=" * 80)

    # Find all constraints
    constraint_facts = [f for f in facts if f['type'] == 'constraint']
    constraints_validated = [f for f in constraint_facts if f['id'] in facts_with_rels]
    constraints_orphaned = [f for f in constraint_facts if f['id'] not in facts_with_rels]

    val_rate = len(constraints_validated) / len(constraint_facts) * 100 if constraint_facts else 0

    print(f"  Total constraints:         {len(constraint_facts):,}")
    print(f"  Validated (with rels):     {len(constraints_validated):,}")
    print(f"  Orphaned (no rels):        {len(constraints_orphaned):,}")
    print(f"  Validation rate:           {val_rate:.1f}%")

    # Validation assessment
    print("\n  Assessment:")
    if val_rate >= 80:
        print("    ✓ EXCELLENT: Most constraints validated (≥80%)")
    elif val_rate >= 60:
        print("    ✓ GOOD: Majority validated (60-80%)")
    elif val_rate >= 40:
        print("    ⚠ FAIR: Some validated (40-60%)")
    else:
        print("    ✗ POOR: Low validation (<40%)")

    # Show sample orphaned constraints
    if constraints_orphaned:
        print("\n  Sample orphaned constraints (first 5):")
        for i, fact in enumerate(constraints_orphaned[:5], 1):
            print(f"    {i}. {fact['id']}: {fact['statement'][:70]}...")

    # === SECTION 5: CONTRADICTIONS ===
    print("\n" + "=" * 80)
    print("5. CONTRADICTIONS FOUND")
    print("=" * 80)

    contradictions = [r for r in relationships if r['type'] == 'contradicts']

    if not contradictions:
        print("  ✓ No contradictions detected between facts")
    else:
        print(f"  ⚠ Found {len(contradictions)} contradiction(s):\n")

        for i, contra in enumerate(contradictions, 1):
            fact1 = facts_map.get(contra['fact_id_1'])
            fact2 = facts_map.get(contra['fact_id_2'])

            print(f"  {i}. {contra['fact_id_1']} ↔ {contra['fact_id_2']}")
            print(f"     Confidence: {contra['confidence']:.2f}")

            if fact1:
                print(f"     Fact 1 ({fact1['type']}): {fact1['statement'][:65]}...")
            if fact2:
                print(f"     Fact 2 ({fact2['type']}): {fact2['statement'][:65]}...")

            reasoning = contra.get('reasoning', 'N/A')
            print(f"     Reasoning: {reasoning[:100]}...")
            print()

    # === SECTION 6: MOST CONNECTED FACTS ===
    print("\n" + "=" * 80)
    print("6. MOST CONNECTED FACTS (Top 15)")
    print("=" * 80)

    most_connected = sorted(fact_rel_counts.items(), key=lambda x: x[1], reverse=True)[:15]

    for i, (fact_id, rel_count) in enumerate(most_connected, 1):
        fact = facts_map.get(fact_id)
        if fact:
            print(f"  {i:2d}. {fact_id:12s} ({rel_count:2d} rels, {fact['type']:15s})")
            print(f"      {fact['statement'][:70]}...")

    # === SECTION 7: FACT TYPE COMBINATIONS ===
    print("\n" + "=" * 80)
    print("7. FACT TYPE PAIR ANALYSIS")
    print("=" * 80)

    fact_type_pairs = defaultdict(int)
    for r in relationships:
        fact1 = facts_map.get(r['fact_id_1'])
        fact2 = facts_map.get(r['fact_id_2'])
        if fact1 and fact2:
            pair = tuple(sorted([fact1['type'], fact2['type']]))
            fact_type_pairs[pair] += 1

    print("\n  Most common fact type combinations:")
    for (type1, type2), count in sorted(fact_type_pairs.items(), key=lambda x: x[1], reverse=True)[:10]:
        pct = count / relationships_found * 100 if relationships_found > 0 else 0
        print(f"    {type1:15s} ↔ {type2:15s}: {count:3d} ({pct:4.1f}%)")

    # === SECTION 8: KEY FINDINGS ===
    print("\n" + "=" * 80)
    print("8. KEY FINDINGS & CRITICAL ISSUES")
    print("=" * 80)

    findings = []

    # Check for doc vs code contradictions
    doc_code_contradictions = []
    for contra in contradictions:
        fact1 = facts_map.get(contra['fact_id_1'])
        fact2 = facts_map.get(contra['fact_id_2'])

        if fact1 and fact2:
            # Check if one is from docs and other from code
            artifacts1 = [e['artifact_id'] for e in fact1.get('extracted_from', [])]
            artifacts2 = [e['artifact_id'] for e in fact2.get('extracted_from', [])]

            has_doc1 = any('artifact_1' in a for a in artifacts1)
            has_doc2 = any('artifact_1' in a for a in artifacts2)
            has_code1 = any('artifact_' in a and a != 'artifact_1' for a in artifacts1)
            has_code2 = any('artifact_' in a and a != 'artifact_1' for a in artifacts2)

            if (has_doc1 and has_code2) or (has_code1 and has_doc2):
                doc_code_contradictions.append(contra)

    if doc_code_contradictions:
        findings.append(f"  ✗ CRITICAL: {len(doc_code_contradictions)} doc↔code contradiction(s) found")

    # Check for missing implementations
    impl_constraints = [
        f for f in constraint_facts
        if f['id'] in facts_with_rels
    ]

    # Look for constraints without implementation relationships
    constraints_without_impl = []
    for const_fact in impl_constraints:
        # Check if this constraint has any "supports" relationship to an implementation
        has_impl = False
        for r in relationships:
            if r['fact_id_1'] == const_fact['id'] or r['fact_id_2'] == const_fact['id']:
                other_id = r['fact_id_2'] if r['fact_id_1'] == const_fact['id'] else r['fact_id_1']
                other_fact = facts_map.get(other_id)
                if other_fact and other_fact['type'] == 'implementation' and r['type'] == 'supports':
                    has_impl = True
                    break

        if not has_impl:
            constraints_without_impl.append(const_fact)

    if len(constraints_without_impl) > 10:
        findings.append(f"  ⚠ WARNING: {len(constraints_without_impl)} constraints lack implementation links")

    # Check orphaned facts
    if orphaned_facts > len(facts) * 0.5:
        findings.append(f"  ⚠ WARNING: {orphaned_facts} orphaned facts (>{50}% of total)")

    # Positive findings
    if not contradictions:
        findings.append("  ✓ POSITIVE: No contradictions detected")

    supports_pct = type_counts.get('supports', 0) / relationships_found * 100 if relationships_found > 0 else 0
    if supports_pct >= 60:
        findings.append(f"  ✓ POSITIVE: High 'supports' ratio ({supports_pct:.0f}%)")

    if not findings:
        findings.append("  ℹ No critical issues identified")

    for finding in findings:
        print(finding)

    # === SECTION 9: RECOMMENDATIONS ===
    print("\n" + "=" * 80)
    print("9. RECOMMENDATIONS")
    print("=" * 80)

    recommendations = []

    if orphaned_facts > 100:
        recommendations.append("  • Review orphaned facts for potential relationships")

    if len(constraints_orphaned) > 20:
        recommendations.append("  • Investigate orphaned constraints for missing implementations")

    if contradictions:
        recommendations.append("  • Resolve all documented contradictions")

    if density < 50:
        recommendations.append("  • Consider additional relationship discovery passes")

    if val_rate < 60:
        recommendations.append("  • Improve constraint validation coverage")

    # Check if processing is incomplete
    if relationships_found < total_pairs_analyzed:
        remaining = total_pairs_analyzed - relationships_found
        recommendations.append(f"  • Complete processing of remaining {remaining:,} candidate pairs")

    if not recommendations:
        recommendations.append("  • Continue monitoring and maintaining relationship graph")
        recommendations.append("  • Periodically validate relationships as codebase evolves")

    for rec in recommendations:
        print(rec)

    # === FOOTER ===
    print("\n" + "=" * 80)
    print("END OF REPORT")
    print("=" * 80)

if __name__ == '__main__':
    main()
