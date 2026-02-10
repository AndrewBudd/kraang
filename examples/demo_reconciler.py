#!/usr/bin/env python3
"""
Demonstration of Constraint Reconciler

This script demonstrates the constraint reconciliation process using real
LotJ examples, showing how the tool identifies conflicts, analyzes them,
and proposes actionable resolutions.
"""

from reconciler import ConstraintReconciler, ReconciliationStrategy
from kraang import KraangStore


def print_separator(char='=', length=80):
    print(char * length)


def print_section(title):
    print()
    print_separator()
    print(f"  {title}")
    print_separator()
    print()


def demo_conflict_analysis():
    """Demonstrate conflict analysis capabilities"""
    print_section("DEMONSTRATION: Constraint Reconciler")

    store = KraangStore()
    reconciler = ConstraintReconciler(store)

    print("Loading constraints from LotJ codebase...")
    conflicts = reconciler.find_all_conflicts()
    print(f"Found {len(conflicts)} conflicts to analyze")
    print()

    # Show conflict breakdown
    severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
    for conflict in conflicts:
        severity_counts[conflict.severity] += 1

    print("Severity Breakdown:")
    for severity in ['critical', 'high', 'medium', 'low']:
        count = severity_counts[severity]
        if count > 0:
            bar = '█' * count
            print(f"  {severity.upper():8s}: {bar} ({count})")
    print()

    return conflicts


def demo_reconciliation_strategies():
    """Demonstrate different reconciliation strategies"""
    print_section("RECONCILIATION STRATEGIES")

    strategies = [
        (ReconciliationStrategy.SOURCE_AUTHORITY_CODE,
         "Code is truth (documentation is wrong)",
         "When running code contradicts what documentation says",
         0.90),
        (ReconciliationStrategy.SOURCE_AUTHORITY_DOCS,
         "Docs are truth (code needs fixing)",
         "When requirements document what code should do",
         0.80),
        (ReconciliationStrategy.SPECIFICITY,
         "Specific rule beats general guideline",
         "More specific constraint takes precedence",
         0.85),
        (ReconciliationStrategy.SYNTHESIS,
         "Combine both into unified truth",
         "Both constraints are partially true",
         0.75),
        (ReconciliationStrategy.CONDITIONAL,
         "Both true in different contexts",
         "Context-dependent resolution",
         0.85),
        (ReconciliationStrategy.ESCALATE,
         "Needs human decision",
         "Too complex for automated resolution",
         0.50),
    ]

    print("Available Reconciliation Strategies:")
    print()
    for strategy, name, when, confidence in strategies:
        print(f"  Strategy: {strategy.value}")
        print(f"    Name: {name}")
        print(f"    When: {when}")
        print(f"    Confidence: {confidence:.2f}")
        print()


def demo_specific_conflict(conflict_id=None):
    """Demonstrate detailed analysis of specific conflict"""
    store = KraangStore()
    reconciler = ConstraintReconciler(store)

    if conflict_id is None:
        # Use the memory management conflict as default
        fact1_id = "fact_28"
        fact2_id = "fact_31"
    else:
        # Parse conflict_id (format: conflict_fact_X_fact_Y)
        parts = conflict_id.split('_')
        fact1_id = f"{parts[1]}_{parts[2]}"
        fact2_id = f"{parts[3]}_{parts[4]}"

    print_section(f"DETAILED ANALYSIS: {fact1_id} vs {fact2_id}")

    # Get facts
    fact1 = store.get_fact(fact1_id)
    fact2 = store.get_fact(fact2_id)

    if not fact1 or not fact2:
        print(f"Error: Facts not found ({fact1_id}, {fact2_id})")
        return

    print("BEFORE: Conflicting Facts")
    print_separator('-')
    print()

    print(f"Fact 1: {fact1.id}")
    print(f"  Type: {fact1.type}")
    print(f"  Statement: {fact1.statement}")
    if fact1.extracted_from:
        src = fact1.extracted_from[0]
        artifact = store.get_artifact(src.get('artifact_id', ''))
        if artifact:
            print(f"  Source: {artifact.path}")
            print(f"  Location: {src.get('location', 'unknown')}")
    print()

    print(f"Fact 2: {fact2.id}")
    print(f"  Type: {fact2.type}")
    print(f"  Statement: {fact2.statement}")
    if fact2.extracted_from:
        src = fact2.extracted_from[0]
        artifact = store.get_artifact(src.get('artifact_id', ''))
        if artifact:
            print(f"  Source: {artifact.path}")
            print(f"  Location: {src.get('location', 'unknown')}")
    print()

    # Analyze conflict
    relationships = store.get_relationships()
    rel = None
    for r in relationships:
        if (r.fact_id_1 == fact1_id and r.fact_id_2 == fact2_id) or \
           (r.fact_id_1 == fact2_id and r.fact_id_2 == fact1_id):
            rel = r
            break

    conflict = reconciler.analyze_conflict(fact1_id, fact2_id, rel)

    print("CONFLICT ANALYSIS")
    print_separator('-')
    print()
    print(f"  Type: {conflict.conflict_type}")
    print(f"  Severity: {conflict.severity.upper()}")
    print(f"  Confidence: {conflict.confidence:.2f}")
    print()
    print(f"  Description:")
    print(f"    {conflict.description}")
    print()

    # Generate reconciliation
    proposal = reconciler.propose_reconciliation(conflict)

    print("AFTER: Reconciled Version")
    print_separator('-')
    print()
    print(f"  Strategy: {proposal.strategy.value}")
    print(f"  Confidence: {proposal.confidence:.2f}")
    print()
    print(f"  Reconciled Statement:")
    for line in proposal.reconciled_statement.split('\n'):
        print(f"    {line}")
    print()
    print(f"  Rationale:")
    for line in proposal.reconciled_rationale.split('\n'):
        print(f"    {line}")
    print()

    # Show action items
    print("ACTION ITEMS")
    print_separator('-')
    print()

    if proposal.code_changes_needed:
        print("Code Changes Needed:")
        for change in proposal.code_changes_needed:
            print(f"  [ ] {change}")
        print()

    if proposal.doc_changes_needed:
        print("Documentation Changes Needed:")
        for change in proposal.doc_changes_needed:
            print(f"  [ ] {change}")
        print()

    if proposal.verification_steps:
        print("Verification Steps:")
        for i, step in enumerate(proposal.verification_steps, 1):
            print(f"  {i}. {step}")
        print()

    # Impact summary
    print("IMPACT SUMMARY")
    print_separator('-')
    print()
    if proposal.facts_to_update:
        print(f"  Facts to update: {len(proposal.facts_to_update)}")
        for fid in proposal.facts_to_update:
            print(f"    - {fid}")
    if proposal.facts_to_deprecate:
        print(f"  Facts to deprecate: {len(proposal.facts_to_deprecate)}")
        for fid in proposal.facts_to_deprecate:
            print(f"    - {fid}")
    if proposal.facts_to_create:
        print(f"  New facts to create: {len(proposal.facts_to_create)}")
    print()


def demo_full_reconciliation():
    """Demonstrate full reconciliation of all conflicts"""
    print_section("FULL RECONCILIATION REPORT")

    store = KraangStore()
    reconciler = ConstraintReconciler(store)

    print("Generating reconciliation proposals for all conflicts...")
    proposals = reconciler.reconcile_all()
    print(f"Generated {len(proposals)} proposals")
    print()

    # Strategy breakdown
    strategy_counts = {}
    for p in proposals:
        strategy_counts[p.strategy.value] = strategy_counts.get(p.strategy.value, 0) + 1

    print("Proposals by Strategy:")
    for strategy, count in sorted(strategy_counts.items(), key=lambda x: -x[1]):
        print(f"  {strategy:30s}: {count}")
    print()

    # Confidence breakdown
    high_conf = sum(1 for p in proposals if p.confidence >= 0.8)
    med_conf = sum(1 for p in proposals if 0.5 <= p.confidence < 0.8)
    low_conf = sum(1 for p in proposals if p.confidence < 0.5)

    print("Confidence Distribution:")
    print(f"  High (≥0.80): {high_conf}")
    print(f"  Medium (0.50-0.79): {med_conf}")
    print(f"  Low (<0.50): {low_conf}")
    print()

    # Action item summary
    total_code_changes = sum(len(p.code_changes_needed) for p in proposals)
    total_doc_changes = sum(len(p.doc_changes_needed) for p in proposals)
    total_verification = sum(len(p.verification_steps) for p in proposals)

    print("Total Action Items:")
    print(f"  Code changes: {total_code_changes}")
    print(f"  Documentation changes: {total_doc_changes}")
    print(f"  Verification steps: {total_verification}")
    print()


def main():
    """Run all demonstrations"""
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "analyze":
            demo_conflict_analysis()
        elif command == "strategies":
            demo_reconciliation_strategies()
        elif command == "detail":
            conflict_id = sys.argv[2] if len(sys.argv) > 2 else None
            demo_specific_conflict(conflict_id)
        elif command == "full":
            demo_full_reconciliation()
        else:
            print(f"Unknown command: {command}")
            print_usage()
    else:
        # Run full demo
        print("=" * 80)
        print(" " * 20 + "CONSTRAINT RECONCILER DEMONSTRATION")
        print("=" * 80)
        print()
        print("This demonstration shows how the Constraint Reconciler analyzes")
        print("conflicting facts and proposes actionable resolutions.")
        print()

        demo_conflict_analysis()
        input("\nPress Enter to continue...")

        demo_reconciliation_strategies()
        input("\nPress Enter to continue...")

        demo_specific_conflict()
        input("\nPress Enter to continue...")

        demo_full_reconciliation()

        print()
        print_separator()
        print("  DEMONSTRATION COMPLETE")
        print_separator()
        print()
        print("Next steps:")
        print("  1. Review the generated RECONCILIATION_EXAMPLES.md")
        print("  2. Run: python reconciler.py report RECONCILIATION_REPORT.md")
        print("  3. Implement the action items for each conflict")
        print("  4. Update facts in the knowledge base")
        print()


def print_usage():
    print("""
Constraint Reconciler Demonstration

Usage:
  python demo_reconciler.py [command]

Commands:
  analyze       Show conflict analysis
  strategies    Show available reconciliation strategies
  detail [id]   Show detailed analysis of specific conflict
  full          Show full reconciliation report
  (no command)  Run full interactive demonstration

Examples:
  python demo_reconciler.py
  python demo_reconciler.py analyze
  python demo_reconciler.py detail conflict_fact_28_fact_31
  python demo_reconciler.py full
""")


if __name__ == "__main__":
    main()
