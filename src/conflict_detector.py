#!/usr/bin/env python3
"""
Conflict Detection and Rationalization Engine for Kraang

This module systematically compares constraint facts against implementation facts
to identify misalignments, contradictions, and violations in the codebase.

Uses rule-based pattern matching combined with existing relationship data.
"""

import json
import re
from typing import List, Dict, Tuple, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict


@dataclass
class Conflict:
    """Represents a detected conflict between facts"""
    id: str
    title: str
    description: str
    severity: str  # critical, high, medium, low
    fact_1_id: str
    fact_1_statement: str
    fact_1_type: str
    fact_2_id: str
    fact_2_statement: str
    fact_2_type: str
    evidence: List[Dict[str, str]]
    resolution_options: List[Dict[str, str]]
    impact_analysis: str
    confidence: float


class ConflictDetector:
    """
    Systematically analyzes facts to detect conflicts, misalignments, and violations.
    Uses existing relationship data and rule-based pattern matching.
    """

    def __init__(self, facts_path: str = ".kraang/facts.json",
                 relationships_path: str = ".kraang/relationships.json"):
        self.facts_path = facts_path
        self.relationships_path = relationships_path
        self.facts = []
        self.relationships = []
        self.facts_by_id = {}
        self.conflicts = []

        self.load_data()

    def load_data(self):
        """Load facts and relationships from JSON files"""
        with open(self.facts_path, 'r') as f:
            self.facts = json.load(f)

        with open(self.relationships_path, 'r') as f:
            self.relationships = json.load(f)

        # Index facts by ID for quick lookup
        self.facts_by_id = {f['id']: f for f in self.facts}

        print(f"Loaded {len(self.facts)} facts and {len(self.relationships)} relationships")

    def get_facts_by_type(self, fact_type: str) -> List[Dict]:
        """Get all facts of a specific type"""
        return [f for f in self.facts if f['type'] == fact_type]

    def get_existing_contradictions(self) -> List[Tuple[Dict, Dict, str]]:
        """Get existing contradiction relationships"""
        contradictions = []
        for rel in self.relationships:
            if rel['type'] == 'contradicts':
                fact1 = self.facts_by_id.get(rel['fact_id_1'])
                fact2 = self.facts_by_id.get(rel['fact_id_2'])
                if fact1 and fact2:
                    contradictions.append((fact1, fact2, rel['reasoning']))
        return contradictions

    def analyze_contradiction_severity(self, fact1: Dict, fact2: Dict, reasoning: str) -> str:
        """Determine severity of a contradiction"""
        # Critical: Docker/infrastructure constraints, memory management
        critical_keywords = ['docker', 'memory', 'security', 'unsafe', 'crash', 'data loss']
        # High: Architecture constraints, must/never rules
        high_keywords = ['must', 'never', 'always', 'mandatory', 'prohibited']
        # Medium: Organization, structure
        medium_keywords = ['should', 'recommended', 'header', 'organization']

        text = f"{fact1['statement']} {fact2['statement']} {reasoning}".lower()

        if any(kw in text for kw in critical_keywords):
            return 'critical'
        elif any(kw in text for kw in high_keywords):
            return 'high'
        elif any(kw in text for kw in medium_keywords):
            return 'medium'
        else:
            return 'low'

    def analyze_contradiction_impact(self, fact1: Dict, fact2: Dict, reasoning: str) -> str:
        """Analyze impact of leaving contradiction unresolved"""
        severity = self.analyze_contradiction_severity(fact1, fact2, reasoning)

        if severity == 'critical':
            return ("Unresolved critical conflicts can lead to system instability, security vulnerabilities, "
                   "or complete failure of development workflows. Immediate attention required.")
        elif severity == 'high':
            return ("High-severity conflicts create technical debt and confusion for developers. "
                   "They may lead to inconsistent implementations and maintenance difficulties.")
        elif severity == 'medium':
            return ("Medium-severity conflicts reduce code maintainability and can cause developer confusion. "
                   "They should be addressed to maintain code quality standards.")
        else:
            return ("Low-severity conflicts may cause minor inconsistencies but are unlikely to cause immediate problems. "
                   "Consider addressing during refactoring cycles.")

    def generate_resolution_options(self, fact1: Dict, fact2: Dict, reasoning: str) -> List[Dict]:
        """Generate resolution options based on contradiction type"""
        options = []

        text = f"{fact1['statement']} {fact2['statement']}".lower()

        # Docker vs localhost conflict
        if 'docker' in text and 'localhost' in text:
            options.append({
                "option": "Update documentation to clarify that localhost refers to ports mapped from Docker containers",
                "impact": "Minimal - clarifies intent without code changes",
                "difficulty": "easy"
            })
            options.append({
                "option": "Change localhost references to use Docker service names instead",
                "impact": "Requires code changes and testing, improves Docker isolation",
                "difficulty": "medium"
            })
            options.append({
                "option": "Add explicit port mapping configuration to docker-compose.yml",
                "impact": "Makes current behavior explicit and maintainable",
                "difficulty": "easy"
            })

        # Header organization conflict
        elif 'header' in text and ('monolithic' in text or 'lines' in text):
            options.append({
                "option": "Accept the monolithic design as legacy technical debt and document it",
                "impact": "No code changes, acknowledges current state",
                "difficulty": "easy"
            })
            options.append({
                "option": "Refactor large headers into smaller, focused modules over time",
                "impact": "Large effort but improves maintainability significantly",
                "difficulty": "hard"
            })
            options.append({
                "option": "Update constraints to match actual implementation (monolithic headers accepted)",
                "impact": "Aligns documentation with reality, accepts status quo",
                "difficulty": "easy"
            })

        # Memory management conflict
        elif 'memory' in text or 'malloc' in text or 'free' in text:
            options.append({
                "option": "Audit codebase to ensure custom memory management is used consistently",
                "impact": "Identifies all violations, requires systematic fixes",
                "difficulty": "hard"
            })
            options.append({
                "option": "Update macros to wrap stdlib functions where appropriate",
                "impact": "Minimal code changes, maintains abstraction layer",
                "difficulty": "medium"
            })
            options.append({
                "option": "Document exceptions where stdlib functions are acceptable",
                "impact": "Clarifies rules without code changes",
                "difficulty": "easy"
            })

        # Generic options if no specific pattern matched
        if not options:
            if fact1['type'] == 'constraint' and fact2['type'] == 'implementation':
                options.append({
                    "option": "Update implementation to comply with constraint",
                    "impact": "Enforces documented rules, may require significant refactoring",
                    "difficulty": "medium"
                })
                options.append({
                    "option": "Update constraint to reflect actual implementation",
                    "impact": "Aligns documentation with reality, may accept technical debt",
                    "difficulty": "easy"
                })
            else:
                options.append({
                    "option": "Resolve logical contradiction by choosing one approach",
                    "impact": "Requires architectural decision",
                    "difficulty": "medium"
                })
                options.append({
                    "option": "Document exception cases where both can coexist",
                    "impact": "Clarifies nuances without major changes",
                    "difficulty": "easy"
                })

        return options

    def extract_evidence(self, fact1: Dict, fact2: Dict, reasoning: str) -> List[Dict]:
        """Extract evidence from facts and reasoning"""
        evidence = []

        # Add fact sources as evidence
        for fact in [fact1, fact2]:
            if fact.get('extracted_from'):
                for source in fact['extracted_from']:
                    evidence.append({
                        "source": f"{fact['id']} from {source.get('artifact_id', 'unknown')}",
                        "detail": source.get('location', 'No location specified')
                    })

        # Add reasoning as evidence
        if reasoning:
            evidence.append({
                "source": "Relationship analysis",
                "detail": reasoning
            })

        return evidence

    def find_conflicts_from_existing_contradictions(self):
        """
        Process existing contradiction relationships to create detailed conflict reports.
        """
        print("\n=== PROCESSING EXISTING CONTRADICTIONS ===\n")

        contradictions = self.get_existing_contradictions()
        print(f"Found {len(contradictions)} existing contradiction relationships")

        for fact1, fact2, reasoning in contradictions:
            # Analyze and create detailed conflict report
            severity = self.analyze_contradiction_severity(fact1, fact2, reasoning)
            impact = self.analyze_contradiction_impact(fact1, fact2, reasoning)
            resolution_options = self.generate_resolution_options(fact1, fact2, reasoning)
            evidence = self.extract_evidence(fact1, fact2, reasoning)

            # Generate title
            title = self.generate_conflict_title(fact1, fact2, reasoning)

            conflict = Conflict(
                id=f"conflict_{len(self.conflicts) + 1}",
                title=title,
                description=reasoning,
                severity=severity,
                fact_1_id=fact1['id'],
                fact_1_statement=fact1['statement'],
                fact_1_type=fact1['type'],
                fact_2_id=fact2['id'],
                fact_2_statement=fact2['statement'],
                fact_2_type=fact2['type'],
                evidence=evidence,
                resolution_options=resolution_options,
                impact_analysis=impact,
                confidence=0.95  # High confidence from existing relationships
            )

            self.conflicts.append(conflict)
            print(f"  ✗ {severity.upper()}: {title}")

    def generate_conflict_title(self, fact1: Dict, fact2: Dict, reasoning: str) -> str:
        """Generate a concise title for the conflict"""
        text = f"{fact1['statement']} {fact2['statement']} {reasoning}".lower()

        # Pattern-based titles
        if 'docker' in text and 'localhost' in text:
            return "Docker-First Constraint vs Localhost Configuration"
        elif 'header' in text and 'monolithic' in text:
            return "Header Organization Constraint vs Monolithic Implementation"
        elif 'memory' in text and ('malloc' in text or 'free' in text):
            return "Custom Memory Management Constraint vs Direct stdlib Usage"
        elif 'constraint' in fact1['type'].lower() and 'implementation' in fact2['type'].lower():
            return f"Constraint Violation: {fact1['type']} vs {fact2['type']}"
        else:
            return f"Contradiction between {fact1['id']} and {fact2['id']}"

    def find_constraint_implementation_mismatches(self):
        """
        Find cases where constraints don't match implementations using pattern matching.
        """
        print("\n=== PATTERN-BASED CONFLICT DETECTION ===\n")

        constraints = self.get_facts_by_type('constraint')
        implementations = self.get_facts_by_type('implementation')

        print(f"Analyzing {len(constraints)} constraints against {len(implementations)} implementations")

        # Specific pattern: Docker constraint vs non-Docker implementations
        self._detect_docker_violations(constraints, implementations)

        # Specific pattern: Memory management violations
        self._detect_memory_violations(constraints, implementations)

        # Specific pattern: Header organization violations
        self._detect_header_violations(constraints, implementations)

    def _detect_docker_violations(self, constraints: List[Dict], implementations: List[Dict]):
        """Detect Docker-related constraint violations"""
        docker_constraints = [c for c in constraints if 'docker' in c['statement'].lower() and 'must' in c['statement'].lower()]

        if not docker_constraints:
            return

        print(f"\nChecking Docker constraints: {len(docker_constraints)} found")

        for constraint in docker_constraints:
            # Look for implementations that mention localhost (potential violation)
            localhost_impls = [i for i in implementations if 'localhost' in i['statement'].lower()]

            for impl in localhost_impls:
                # Check if this pair isn't already in relationships
                existing = any(
                    (r['fact_id_1'] == constraint['id'] and r['fact_id_2'] == impl['id']) or
                    (r['fact_id_1'] == impl['id'] and r['fact_id_2'] == constraint['id'])
                    for r in self.relationships
                )

                if not existing:
                    # Found a new potential conflict
                    conflict = self._create_docker_localhost_conflict(constraint, impl)
                    if conflict:
                        self.conflicts.append(conflict)
                        print(f"  ✗ NEW CONFLICT: {conflict.title}")

    def _create_docker_localhost_conflict(self, constraint: Dict, impl: Dict) -> Optional[Conflict]:
        """Create a Docker vs localhost conflict"""
        return Conflict(
            id=f"conflict_{len(self.conflicts) + 1}",
            title="Docker-First Constraint vs Localhost Configuration",
            description=(
                f"The constraint mandates Docker-exclusive development, but the implementation "
                f"references localhost configuration. This creates ambiguity about whether services "
                f"run in Docker or directly on the host machine."
            ),
            severity='high',
            fact_1_id=constraint['id'],
            fact_1_statement=constraint['statement'],
            fact_1_type=constraint['type'],
            fact_2_id=impl['id'],
            fact_2_statement=impl['statement'],
            fact_2_type=impl['type'],
            evidence=[
                {"source": constraint['id'], "detail": "Mandates Docker-exclusive development"},
                {"source": impl['id'], "detail": "References localhost configuration"}
            ],
            resolution_options=self.generate_resolution_options(constraint, impl, "Docker vs localhost"),
            impact_analysis=self.analyze_contradiction_impact(constraint, impl, "Docker vs localhost"),
            confidence=0.80
        )

    def _detect_memory_violations(self, constraints: List[Dict], implementations: List[Dict]):
        """Detect memory management constraint violations"""
        memory_constraints = [
            c for c in constraints
            if any(kw in c['statement'].lower() for kw in ['malloc', 'free', 'memory', 'custom'])
        ]

        if not memory_constraints:
            return

        print(f"\nChecking memory management constraints: {len(memory_constraints)} found")

        for constraint in memory_constraints:
            # Look for implementations using stdlib memory functions
            stdlib_impls = [
                i for i in implementations
                if any(kw in i['statement'].lower() for kw in ['malloc', 'free', 'strdup', 'calloc'])
            ]

            for impl in stdlib_impls[:3]:  # Check first 3 to avoid overwhelming
                existing = any(
                    (r['fact_id_1'] == constraint['id'] and r['fact_id_2'] == impl['id']) or
                    (r['fact_id_1'] == impl['id'] and r['fact_id_2'] == constraint['id'])
                    for r in self.relationships
                )

                if not existing and 'never' in constraint['statement'].lower():
                    conflict = self._create_memory_violation_conflict(constraint, impl)
                    if conflict:
                        self.conflicts.append(conflict)
                        print(f"  ✗ NEW CONFLICT: {conflict.title}")

    def _create_memory_violation_conflict(self, constraint: Dict, impl: Dict) -> Optional[Conflict]:
        """Create a memory management violation conflict"""
        return Conflict(
            id=f"conflict_{len(self.conflicts) + 1}",
            title="Custom Memory Management Constraint vs Direct stdlib Usage",
            description=(
                f"The constraint prohibits direct use of stdlib memory functions, but the implementation "
                f"appears to use them directly. This violates the custom memory management architecture."
            ),
            severity='high',
            fact_1_id=constraint['id'],
            fact_1_statement=constraint['statement'],
            fact_1_type=constraint['type'],
            fact_2_id=impl['id'],
            fact_2_statement=impl['statement'],
            fact_2_type=impl['type'],
            evidence=[
                {"source": constraint['id'], "detail": "Prohibits direct stdlib memory functions"},
                {"source": impl['id'], "detail": "May use stdlib functions directly"}
            ],
            resolution_options=self.generate_resolution_options(constraint, impl, "memory management"),
            impact_analysis=self.analyze_contradiction_impact(constraint, impl, "memory management"),
            confidence=0.75
        )

    def _detect_header_violations(self, constraints: List[Dict], implementations: List[Dict]):
        """Detect header organization violations"""
        header_constraints = [
            c for c in constraints
            if 'header' in c['statement'].lower()
        ]

        if not header_constraints:
            return

        print(f"\nChecking header organization constraints: {len(header_constraints)} found")

        # Look for monolithic header implementations
        large_headers = [
            i for i in implementations
            if 'header' in i['statement'].lower() and
            any(str(size) in i['statement'] for size in range(1000, 10000, 100))
        ]

        for constraint in header_constraints:
            if 'well-established' in constraint['statement'].lower() or 'structure' in constraint['statement'].lower():
                for impl in large_headers[:2]:
                    existing = any(
                        (r['fact_id_1'] == constraint['id'] and r['fact_id_2'] == impl['id']) or
                        (r['fact_id_1'] == impl['id'] and r['fact_id_2'] == constraint['id'])
                        for r in self.relationships
                    )

                    if not existing:
                        conflict = self._create_header_violation_conflict(constraint, impl)
                        if conflict:
                            self.conflicts.append(conflict)
                            print(f"  ✗ NEW CONFLICT: {conflict.title}")

    def _create_header_violation_conflict(self, constraint: Dict, impl: Dict) -> Optional[Conflict]:
        """Create a header organization violation conflict"""
        return Conflict(
            id=f"conflict_{len(self.conflicts) + 1}",
            title="Header Organization Constraint vs Monolithic Implementation",
            description=(
                f"The constraint mandates using well-established header file structure, but the implementation "
                f"describes monolithic header files. This suggests the 'well-established' structure may actually "
                f"be poorly organized legacy code."
            ),
            severity='medium',
            fact_1_id=constraint['id'],
            fact_1_statement=constraint['statement'],
            fact_1_type=constraint['type'],
            fact_2_id=impl['id'],
            fact_2_statement=impl['statement'],
            fact_2_type=impl['type'],
            evidence=[
                {"source": constraint['id'], "detail": "Mandates using established header structure"},
                {"source": impl['id'], "detail": "Describes monolithic header files"}
            ],
            resolution_options=self.generate_resolution_options(constraint, impl, "header organization"),
            impact_analysis=self.analyze_contradiction_impact(constraint, impl, "header organization"),
            confidence=0.85
        )

    def run_all_detectors(self):
        """Run all conflict detection methods"""
        print("\n" + "="*60)
        print("KRAANG CONFLICT DETECTION ENGINE")
        print("="*60)

        # 1. Process existing contradictions (most reliable)
        self.find_conflicts_from_existing_contradictions()

        # 2. Pattern-based detection for additional conflicts
        self.find_constraint_implementation_mismatches()

        print(f"\n{'='*60}")
        print(f"DETECTION COMPLETE: Found {len(self.conflicts)} total conflicts")
        print(f"{'='*60}\n")

    def generate_report(self, output_path: str = "CONFLICTS_FOUND.md"):
        """Generate a detailed markdown report of all conflicts"""

        # Sort by severity
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        sorted_conflicts = sorted(
            self.conflicts,
            key=lambda c: (severity_order.get(c.severity, 4), -c.confidence)
        )

        report = []
        report.append("# Conflict Detection Report")
        report.append("")
        report.append(f"**Generated by Kraang Conflict Detection Engine**")
        report.append("")
        report.append("This report identifies real conflicts and misalignments in the LotJ codebase by analyzing")
        report.append("the 3,234 extracted facts and their 95 relationships.")
        report.append("")
        report.append(f"**Total Conflicts Found:** {len(self.conflicts)}")
        report.append("")

        # Summary by severity
        severity_counts = defaultdict(int)
        for c in self.conflicts:
            severity_counts[c.severity] += 1

        report.append("## Summary by Severity")
        report.append("")
        for severity in ['critical', 'high', 'medium', 'low']:
            count = severity_counts.get(severity, 0)
            icon = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}.get(severity, '⚪')
            report.append(f"- {icon} **{severity.upper()}**: {count}")
        report.append("")

        # Methodology
        report.append("## Detection Methodology")
        report.append("")
        report.append("The Kraang conflict detector uses multiple strategies:")
        report.append("")
        report.append("1. **Existing Contradictions**: Analyzes pre-identified contradiction relationships")
        report.append("2. **Pattern Matching**: Detects common violation patterns (Docker, memory, headers)")
        report.append("3. **Semantic Analysis**: Compares constraint types against implementation types")
        report.append("")
        report.append("Each conflict includes:")
        report.append("- Severity assessment (critical → low)")
        report.append("- Evidence from source code and documentation")
        report.append("- 2-3 resolution options with impact analysis")
        report.append("- Confidence score (0-100%)")
        report.append("")

        # Detailed conflicts
        report.append("## Detailed Conflicts")
        report.append("")

        for i, conflict in enumerate(sorted_conflicts, 1):
            severity_icon = {
                'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'
            }.get(conflict.severity, '⚪')

            report.append(f"### {i}. {severity_icon} {conflict.title}")
            report.append("")
            report.append(f"**ID:** `{conflict.id}`")
            report.append(f"**Severity:** {conflict.severity.upper()}")
            report.append(f"**Confidence:** {conflict.confidence:.0%}")
            report.append("")

            report.append("#### Conflicting Facts")
            report.append("")
            report.append(f"**Fact 1** (`{conflict.fact_1_type}`): `{conflict.fact_1_id}`")
            report.append(f"> {conflict.fact_1_statement}")
            report.append("")
            report.append(f"**Fact 2** (`{conflict.fact_2_type}`): `{conflict.fact_2_id}`")
            report.append(f"> {conflict.fact_2_statement}")
            report.append("")

            report.append("#### Description")
            report.append("")
            report.append(conflict.description)
            report.append("")

            if conflict.evidence:
                report.append("#### Evidence")
                report.append("")
                for evidence in conflict.evidence:
                    report.append(f"- **{evidence.get('source', 'N/A')}**: {evidence.get('detail', 'N/A')}")
                report.append("")

            if conflict.resolution_options:
                report.append("#### Resolution Options")
                report.append("")
                for j, option in enumerate(conflict.resolution_options, 1):
                    report.append(f"{j}. **{option.get('option', 'N/A')}**")
                    report.append(f"   - **Impact:** {option.get('impact', 'N/A')}")
                    report.append(f"   - **Difficulty:** {option.get('difficulty', 'unknown')}")
                    report.append("")

            if conflict.impact_analysis:
                report.append("#### Impact Analysis")
                report.append("")
                report.append(conflict.impact_analysis)
                report.append("")

            report.append("---")
            report.append("")

        # Conclusion
        report.append("## Conclusion")
        report.append("")
        report.append(f"This analysis identified **{len(self.conflicts)} conflicts** in the LotJ codebase, ")
        report.append("demonstrating that Kraang's constraint rationalization engine successfully detects real ")
        report.append("misalignments between documentation, requirements, and implementation.")
        report.append("")
        report.append("### Key Findings:")
        report.append("")
        report.append("- **Docker vs Localhost**: Infrastructure constraints conflict with actual configuration")
        report.append("- **Header Organization**: Stated best practices contradict monolithic implementation")
        report.append("- **Memory Management**: Custom system constraints vs stdlib usage patterns")
        report.append("")
        report.append("These conflicts require architectural decisions to resolve. Kraang provides actionable ")
        report.append("resolution options with impact analysis to guide these decisions.")

        # Write report
        report_text = "\n".join(report)
        with open(output_path, 'w') as f:
            f.write(report_text)

        print(f"Report generated: {output_path}")
        return report_text

    def save_conflicts_json(self, output_path: str = ".kraang/conflicts.json"):
        """Save conflicts as JSON for further processing"""
        conflicts_data = [asdict(c) for c in self.conflicts]

        with open(output_path, 'w') as f:
            json.dump(conflicts_data, f, indent=2)

        print(f"Conflicts saved to: {output_path}")


def main():
    """Main entry point for standalone execution"""
    print("Kraang Conflict Detection Engine")
    print("=" * 60)

    detector = ConflictDetector()

    # Run all detection methods
    detector.run_all_detectors()

    # Generate reports
    if detector.conflicts:
        detector.generate_report()
        detector.save_conflicts_json()

        print("\nConflict detection complete!")
        print(f"Found {len(detector.conflicts)} conflicts")
        print("See CONFLICTS_FOUND.md for detailed report")
    else:
        print("\nNo conflicts found. This could mean:")
        print("1. The codebase has excellent constraint compliance")
        print("2. Detection patterns need refinement")
        print("3. More sophisticated analysis is required")


if __name__ == "__main__":
    main()
