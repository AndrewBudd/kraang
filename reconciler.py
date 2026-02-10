#!/usr/bin/env python3
"""
Constraint Reconciler - Helps reconcile and combine conflicting constraints into a coherent system.

Core Mission: When facts conflict, help merge them into a single truth.

This tool analyzes conflicting constraints, determines authority based on source type,
age, specificity, and context, then proposes reconciled versions with action items.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime

# Import Kraang components
try:
    from kraang import KraangStore, Fact, Relationship, RelationType, ArtifactReference
    KRAANG_AVAILABLE = True
except ImportError:
    KRAANG_AVAILABLE = False
    print("Warning: Kraang module not available, limited functionality")


class ReconciliationStrategy(Enum):
    """Strategy for reconciling conflicting facts"""
    SOURCE_AUTHORITY_CODE = "source_authority_code"  # Code is truth (docs wrong)
    SOURCE_AUTHORITY_DOCS = "source_authority_docs"  # Docs are truth (code wrong)
    TEMPORAL_NEWER = "temporal_newer"  # Newer fact supersedes older
    SPECIFICITY = "specificity"  # More specific fact wins, general becomes guideline
    SYNTHESIS = "synthesis"  # Combine both into unified constraint
    CONDITIONAL = "conditional"  # Both true in different contexts
    ELIMINATE_DUPLICATE = "eliminate_duplicate"  # Remove redundant fact
    ESCALATE = "escalate"  # Needs human decision


class SourceAuthority(Enum):
    """Authority level of different source types"""
    CODE_IMPLEMENTATION = 100  # Actual running code (highest authority)
    TESTS = 90  # Test code validates behavior
    API_DOCS = 80  # API documentation
    ARCHITECTURE_DOCS = 70  # Architecture and design docs
    DEVELOPER_GUIDE = 60  # Developer guidance
    COMMENTS = 50  # Code comments
    INFORMAL_DOCS = 40  # READMEs, guides
    UNKNOWN = 0  # Unknown source


@dataclass
class ConflictAnalysis:
    """Analysis of a conflict between two or more facts"""
    conflict_id: str
    facts: List[str]  # fact IDs involved
    conflict_type: str  # "direct_contradiction", "partial_overlap", "semantic_conflict"
    severity: str  # "critical", "high", "medium", "low"
    confidence: float
    description: str

    def to_dict(self):
        return asdict(self)


@dataclass
class ReconciliationProposal:
    """Proposed reconciliation of conflicting facts"""
    conflict_id: str
    strategy: ReconciliationStrategy
    confidence: float

    # Before state
    conflicting_facts: List[str]  # fact IDs
    conflict_description: str

    # After state
    reconciled_statement: str
    reconciled_type: str
    reconciled_rationale: str

    # Changes needed
    facts_to_update: List[str]  # fact IDs to modify
    facts_to_deprecate: List[str]  # fact IDs to mark as superseded
    facts_to_create: List[Dict]  # new facts to create

    # Action items
    code_changes_needed: List[str]
    doc_changes_needed: List[str]
    verification_steps: List[str]

    def to_dict(self):
        d = asdict(self)
        d['strategy'] = self.strategy.value
        return d


class ConstraintReconciler:
    """Main reconciliation engine"""

    def __init__(self, store: 'KraangStore' = None):
        self.store = store or KraangStore()

    def analyze_conflict(self, fact_id_1: str, fact_id_2: str,
                        relationship: Optional[Relationship] = None) -> ConflictAnalysis:
        """Analyze a conflict between two facts"""
        fact1 = self.store.get_fact(fact_id_1)
        fact2 = self.store.get_fact(fact_id_2)

        if not fact1 or not fact2:
            raise ValueError(f"Facts not found: {fact_id_1}, {fact_id_2}")

        # Determine conflict type
        conflict_type = self._determine_conflict_type(fact1, fact2, relationship)

        # Determine severity
        severity = self._determine_severity(fact1, fact2)

        # Generate description
        description = self._generate_conflict_description(fact1, fact2, relationship)

        conflict_id = f"conflict_{fact_id_1}_{fact_id_2}"

        return ConflictAnalysis(
            conflict_id=conflict_id,
            facts=[fact_id_1, fact_id_2],
            conflict_type=conflict_type,
            severity=severity,
            confidence=relationship.confidence if relationship else 0.8,
            description=description
        )

    def _determine_conflict_type(self, fact1: Fact, fact2: Fact,
                                 relationship: Optional[Relationship]) -> str:
        """Determine type of conflict"""
        # If we have relationship analysis, use it
        if relationship and relationship.type == RelationType.CONTRADICTS:
            # Check if they're direct opposites
            if self._is_direct_contradiction(fact1, fact2):
                return "direct_contradiction"
            elif self._has_semantic_conflict(fact1, fact2):
                return "semantic_conflict"
            else:
                return "partial_overlap"

        # Fallback: analyze statements
        s1, s2 = fact1.statement.lower(), fact2.statement.lower()

        # Look for negation words
        negations = ["never", "not", "don't", "do not", "must not", "cannot", "forbidden"]
        if any(neg in s1 for neg in negations) and any(neg in s2 for neg in negations):
            return "direct_contradiction"

        return "semantic_conflict"

    def _is_direct_contradiction(self, fact1: Fact, fact2: Fact) -> bool:
        """Check if facts directly contradict (e.g., 'must do X' vs 'must not do X')"""
        s1 = fact1.statement.lower()
        s2 = fact2.statement.lower()

        # Simple heuristic: look for opposing mandates
        positive_words = ["must", "should", "required", "mandatory"]
        negative_words = ["must not", "should not", "never", "forbidden", "prohibited"]

        has_positive = any(word in s1 for word in positive_words)
        has_negative = any(word in s2 for word in negative_words)

        return (has_positive and has_negative) or (has_negative and has_positive)

    def _has_semantic_conflict(self, fact1: Fact, fact2: Fact) -> bool:
        """Check if facts have semantic conflict (different approaches to same problem)"""
        # This is a simplification - in reality would use embeddings
        # For now, check if they mention similar concepts

        s1_words = set(fact1.statement.lower().split())
        s2_words = set(fact2.statement.lower().split())

        # If they share significant words, they might conflict semantically
        overlap = s1_words & s2_words
        return len(overlap) > 3

    def _determine_severity(self, fact1: Fact, fact2: Fact) -> str:
        """Determine severity of conflict"""
        # Critical: constraints that affect safety, security, or data integrity
        critical_keywords = ["security", "memory", "crash", "corruption", "data loss",
                           "unsafe", "vulnerability", "exploit"]

        # High: architectural decisions, APIs, interfaces
        high_keywords = ["api", "interface", "architecture", "structure", "must",
                        "required", "mandatory"]

        # Medium: implementation details, patterns
        medium_keywords = ["should", "recommended", "pattern", "convention"]

        combined_text = (fact1.statement + " " + fact2.statement).lower()

        if any(kw in combined_text for kw in critical_keywords):
            return "critical"
        elif any(kw in combined_text for kw in high_keywords):
            return "high"
        elif any(kw in combined_text for kw in medium_keywords):
            return "medium"
        else:
            return "low"

    def _generate_conflict_description(self, fact1: Fact, fact2: Fact,
                                      relationship: Optional[Relationship]) -> str:
        """Generate human-readable conflict description"""
        if relationship and relationship.reasoning:
            return relationship.reasoning

        return f"Fact {fact1.id} ({fact1.type}) conflicts with {fact2.id} ({fact2.type})"

    def _get_source_authority(self, fact: Fact) -> int:
        """Determine authority level based on source"""
        if not fact.extracted_from:
            return SourceAuthority.UNKNOWN.value

        # Get artifact info
        artifact_id = fact.extracted_from[0].get('artifact_id', '')
        artifact = self.store.get_artifact(artifact_id)

        if not artifact:
            return SourceAuthority.UNKNOWN.value

        # Determine authority based on artifact type and path
        path = artifact.path.lower()
        atype = artifact.type.lower()

        # Code files have highest authority
        if atype == "code":
            # Test files are authoritative for behavior
            if "test" in path or "_test" in path:
                return SourceAuthority.TESTS.value
            else:
                return SourceAuthority.CODE_IMPLEMENTATION.value

        # Documentation files vary
        if atype == "doc":
            if "api" in path or "reference" in path:
                return SourceAuthority.API_DOCS.value
            elif "architecture" in path or "design" in path:
                return SourceAuthority.ARCHITECTURE_DOCS.value
            elif "guide" in path or "manual" in path:
                return SourceAuthority.DEVELOPER_GUIDE.value
            elif "readme" in path:
                return SourceAuthority.INFORMAL_DOCS.value

        return SourceAuthority.UNKNOWN.value

    def _get_fact_specificity(self, fact: Fact) -> int:
        """Estimate specificity of a fact (higher = more specific)"""
        statement = fact.statement

        # Count specific markers
        specificity = 0

        # Numbers and quantities are specific
        import re
        numbers = re.findall(r'\d+', statement)
        specificity += len(numbers) * 10

        # Function/variable/type names are specific
        code_names = re.findall(r'[a-z_][a-z0-9_]*\(', statement, re.IGNORECASE)
        specificity += len(code_names) * 5

        # File paths are specific
        if '/' in statement or '\\' in statement:
            specificity += 20

        # Quoted strings are specific
        quotes = re.findall(r'"[^"]+"', statement)
        specificity += len(quotes) * 5

        # Longer statements tend to be more specific
        specificity += min(len(statement) // 20, 20)

        # General words reduce specificity
        general_words = ["should", "typically", "usually", "generally", "often", "may"]
        for word in general_words:
            if word in statement.lower():
                specificity -= 10

        return max(0, specificity)

    def propose_reconciliation(self, conflict: ConflictAnalysis) -> ReconciliationProposal:
        """Propose reconciliation strategy for a conflict"""

        if len(conflict.facts) != 2:
            raise ValueError("Currently only supports 2-way conflicts")

        fact1_id, fact2_id = conflict.facts
        fact1 = self.store.get_fact(fact1_id)
        fact2 = self.store.get_fact(fact2_id)

        # Get source authorities
        auth1 = self._get_source_authority(fact1)
        auth2 = self._get_source_authority(fact2)

        # Get specificities
        spec1 = self._get_fact_specificity(fact1)
        spec2 = self._get_fact_specificity(fact2)

        # Determine strategy
        strategy = self._select_strategy(
            fact1, fact2, auth1, auth2, spec1, spec2, conflict
        )

        # Generate reconciliation based on strategy
        return self._generate_reconciliation(
            strategy, fact1, fact2, auth1, auth2, spec1, spec2, conflict
        )

    def _select_strategy(self, fact1: Fact, fact2: Fact,
                        auth1: int, auth2: int,
                        spec1: int, spec2: int,
                        conflict: ConflictAnalysis) -> ReconciliationStrategy:
        """Select appropriate reconciliation strategy"""

        # If same type and very similar statements, might be duplicate
        if fact1.type == fact2.type and self._is_near_duplicate(fact1, fact2):
            return ReconciliationStrategy.ELIMINATE_DUPLICATE

        # If one is much more authoritative (20+ point difference)
        if auth1 - auth2 > 20:
            if auth1 >= SourceAuthority.CODE_IMPLEMENTATION.value:
                return ReconciliationStrategy.SOURCE_AUTHORITY_CODE
            else:
                return ReconciliationStrategy.SOURCE_AUTHORITY_DOCS
        elif auth2 - auth1 > 20:
            if auth2 >= SourceAuthority.CODE_IMPLEMENTATION.value:
                return ReconciliationStrategy.SOURCE_AUTHORITY_CODE
            else:
                return ReconciliationStrategy.SOURCE_AUTHORITY_DOCS

        # If specificity differs significantly (30+ points)
        if abs(spec1 - spec2) > 30:
            return ReconciliationStrategy.SPECIFICITY

        # If one is constraint and one is implementation, they might be contextual
        if (fact1.type == "constraint" and fact2.type == "implementation") or \
           (fact2.type == "constraint" and fact1.type == "implementation"):
            return ReconciliationStrategy.CONDITIONAL

        # If both are constraints or both are implementations, try synthesis
        if fact1.type == fact2.type:
            return ReconciliationStrategy.SYNTHESIS

        # Default: needs human decision
        return ReconciliationStrategy.ESCALATE

    def _is_near_duplicate(self, fact1: Fact, fact2: Fact) -> bool:
        """Check if facts are near duplicates"""
        s1 = set(fact1.statement.lower().split())
        s2 = set(fact2.statement.lower().split())

        # Jaccard similarity
        if len(s1) == 0 or len(s2) == 0:
            return False

        similarity = len(s1 & s2) / len(s1 | s2)
        return similarity > 0.7

    def _generate_reconciliation(self, strategy: ReconciliationStrategy,
                                fact1: Fact, fact2: Fact,
                                auth1: int, auth2: int,
                                spec1: int, spec2: int,
                                conflict: ConflictAnalysis) -> ReconciliationProposal:
        """Generate reconciliation proposal based on strategy"""

        if strategy == ReconciliationStrategy.SOURCE_AUTHORITY_CODE:
            return self._reconcile_by_code_authority(fact1, fact2, auth1, auth2, conflict)
        elif strategy == ReconciliationStrategy.SOURCE_AUTHORITY_DOCS:
            return self._reconcile_by_doc_authority(fact1, fact2, auth1, auth2, conflict)
        elif strategy == ReconciliationStrategy.SPECIFICITY:
            return self._reconcile_by_specificity(fact1, fact2, spec1, spec2, conflict)
        elif strategy == ReconciliationStrategy.SYNTHESIS:
            return self._reconcile_by_synthesis(fact1, fact2, conflict)
        elif strategy == ReconciliationStrategy.CONDITIONAL:
            return self._reconcile_conditionally(fact1, fact2, conflict)
        elif strategy == ReconciliationStrategy.ELIMINATE_DUPLICATE:
            return self._reconcile_duplicate(fact1, fact2, conflict)
        else:  # ESCALATE
            return self._escalate_to_human(fact1, fact2, conflict)

    def _reconcile_by_code_authority(self, fact1: Fact, fact2: Fact,
                                    auth1: int, auth2: int,
                                    conflict: ConflictAnalysis) -> ReconciliationProposal:
        """Reconcile by treating code as source of truth"""

        # Determine which fact is from code
        code_fact = fact1 if auth1 > auth2 else fact2
        doc_fact = fact2 if auth1 > auth2 else fact1

        return ReconciliationProposal(
            conflict_id=conflict.conflict_id,
            strategy=ReconciliationStrategy.SOURCE_AUTHORITY_CODE,
            confidence=0.9,
            conflicting_facts=[fact1.id, fact2.id],
            conflict_description=conflict.description,
            reconciled_statement=code_fact.statement,
            reconciled_type=code_fact.type,
            reconciled_rationale=(
                f"Code implementation ({code_fact.id}) takes precedence over "
                f"documentation ({doc_fact.id}). The code represents actual runtime "
                f"behavior and is the authoritative source of truth."
            ),
            facts_to_update=[doc_fact.id],
            facts_to_deprecate=[],
            facts_to_create=[{
                'statement': f"DEPRECATED: {doc_fact.statement}",
                'type': 'deprecated',
                'note': f'Superseded by code reality in {code_fact.id}'
            }],
            code_changes_needed=[],
            doc_changes_needed=[
                f"Update documentation to match actual implementation: {code_fact.statement}",
                f"Remove or correct statement: {doc_fact.statement}"
            ],
            verification_steps=[
                f"Verify code behavior matches: {code_fact.statement}",
                "Review documentation updates with team",
                "Test that examples in docs work with actual code"
            ]
        )

    def _reconcile_by_doc_authority(self, fact1: Fact, fact2: Fact,
                                   auth1: int, auth2: int,
                                   conflict: ConflictAnalysis) -> ReconciliationProposal:
        """Reconcile by treating docs as source of truth (code is wrong)"""

        doc_fact = fact1 if auth1 > auth2 else fact2
        code_fact = fact2 if auth1 > auth2 else fact1

        return ReconciliationProposal(
            conflict_id=conflict.conflict_id,
            strategy=ReconciliationStrategy.SOURCE_AUTHORITY_DOCS,
            confidence=0.8,
            conflicting_facts=[fact1.id, fact2.id],
            conflict_description=conflict.description,
            reconciled_statement=doc_fact.statement,
            reconciled_type=doc_fact.type,
            reconciled_rationale=(
                f"Documentation ({doc_fact.id}) represents intended behavior. "
                f"Code ({code_fact.id}) should be updated to match specification."
            ),
            facts_to_update=[code_fact.id],
            facts_to_deprecate=[],
            facts_to_create=[],
            code_changes_needed=[
                f"Update implementation to match specification: {doc_fact.statement}",
                f"Fix code that currently implements: {code_fact.statement}"
            ],
            doc_changes_needed=[],
            verification_steps=[
                f"Verify requirements in documentation are correct: {doc_fact.statement}",
                "Implement code changes to match requirements",
                "Add tests to verify new behavior",
                "Update any dependent code"
            ]
        )

    def _reconcile_by_specificity(self, fact1: Fact, fact2: Fact,
                                 spec1: int, spec2: int,
                                 conflict: ConflictAnalysis) -> ReconciliationProposal:
        """Reconcile by treating more specific fact as truth, general as guideline"""

        specific_fact = fact1 if spec1 > spec2 else fact2
        general_fact = fact2 if spec1 > spec2 else fact1

        return ReconciliationProposal(
            conflict_id=conflict.conflict_id,
            strategy=ReconciliationStrategy.SPECIFICITY,
            confidence=0.85,
            conflicting_facts=[fact1.id, fact2.id],
            conflict_description=conflict.description,
            reconciled_statement=(
                f"SPECIFIC CASE: {specific_fact.statement}\n"
                f"GENERAL GUIDELINE: {general_fact.statement}"
            ),
            reconciled_type="constraint",
            reconciled_rationale=(
                f"More specific fact ({specific_fact.id}) takes precedence in its context. "
                f"General fact ({general_fact.id}) becomes guideline for cases not "
                f"covered by specific rule."
            ),
            facts_to_update=[general_fact.id],
            facts_to_deprecate=[],
            facts_to_create=[{
                'statement': f"GUIDELINE (general case): {general_fact.statement}",
                'type': 'guideline',
                'note': f'Deferred to specific rule in {specific_fact.id} when applicable'
            }],
            code_changes_needed=[],
            doc_changes_needed=[
                f"Clarify that specific case takes precedence: {specific_fact.statement}",
                f"Mark general rule as guideline: {general_fact.statement}",
                "Add examples showing when each applies"
            ],
            verification_steps=[
                "Identify all contexts where specific rule applies",
                "Verify general rule applies to remaining cases",
                "Document exceptions and special cases"
            ]
        )

    def _reconcile_by_synthesis(self, fact1: Fact, fact2: Fact,
                               conflict: ConflictAnalysis) -> ReconciliationProposal:
        """Reconcile by synthesizing both facts into unified constraint"""

        return ReconciliationProposal(
            conflict_id=conflict.conflict_id,
            strategy=ReconciliationStrategy.SYNTHESIS,
            confidence=0.75,
            conflicting_facts=[fact1.id, fact2.id],
            conflict_description=conflict.description,
            reconciled_statement=(
                f"SYNTHESIZED: {fact1.statement} AND {fact2.statement} "
                f"both apply with appropriate context and priorities."
            ),
            reconciled_type="constraint",
            reconciled_rationale=(
                f"Both facts contain partial truth. Synthesized version combines "
                f"insights from {fact1.id} and {fact2.id} into coherent whole."
            ),
            facts_to_update=[fact1.id, fact2.id],
            facts_to_deprecate=[],
            facts_to_create=[{
                'statement': (
                    f"Combined constraint: {fact1.statement} | {fact2.statement}"
                ),
                'type': 'constraint',
                'note': f'Synthesized from {fact1.id} and {fact2.id}'
            }],
            code_changes_needed=[
                "Review if code implements both aspects correctly",
                "Add comments explaining the combined constraint"
            ],
            doc_changes_needed=[
                "Document how both constraints work together",
                "Provide examples showing synthesis in practice",
                "Clarify any priorities or ordering"
            ],
            verification_steps=[
                "Verify synthesized constraint makes logical sense",
                "Check for edge cases where constraints still conflict",
                "Test that implementation satisfies both requirements"
            ]
        )

    def _reconcile_conditionally(self, fact1: Fact, fact2: Fact,
                                conflict: ConflictAnalysis) -> ReconciliationProposal:
        """Reconcile by showing both are true in different contexts"""

        return ReconciliationProposal(
            conflict_id=conflict.conflict_id,
            strategy=ReconciliationStrategy.CONDITIONAL,
            confidence=0.85,
            conflicting_facts=[fact1.id, fact2.id],
            conflict_description=conflict.description,
            reconciled_statement=(
                f"CONTEXT A: {fact1.statement}\n"
                f"CONTEXT B: {fact2.statement}"
            ),
            reconciled_type="constraint",
            reconciled_rationale=(
                f"Both facts are true in different contexts. {fact1.id} applies in "
                f"one scenario while {fact2.id} applies in another. No actual conflict."
            ),
            facts_to_update=[fact1.id, fact2.id],
            facts_to_deprecate=[],
            facts_to_create=[{
                'statement': (
                    f"Context-dependent constraint: {fact1.statement} "
                    f"(Context A) vs {fact2.statement} (Context B)"
                ),
                'type': 'constraint',
                'note': f'Contextual resolution of {fact1.id} and {fact2.id}'
            }],
            code_changes_needed=[],
            doc_changes_needed=[
                "Clarify context where each fact applies",
                f"Document when to use: {fact1.statement}",
                f"Document when to use: {fact2.statement}",
                "Add decision tree or flowchart if helpful"
            ],
            verification_steps=[
                "Identify all contexts clearly",
                "Verify no overlap between contexts",
                "Ensure developers can determine which applies"
            ]
        )

    def _reconcile_duplicate(self, fact1: Fact, fact2: Fact,
                            conflict: ConflictAnalysis) -> ReconciliationProposal:
        """Reconcile by eliminating duplicate"""

        # Keep the one with higher confidence or first one
        keep_fact = fact1 if fact1.confidence >= fact2.confidence else fact2
        remove_fact = fact2 if fact1.confidence >= fact2.confidence else fact1

        return ReconciliationProposal(
            conflict_id=conflict.conflict_id,
            strategy=ReconciliationStrategy.ELIMINATE_DUPLICATE,
            confidence=0.95,
            conflicting_facts=[fact1.id, fact2.id],
            conflict_description=conflict.description,
            reconciled_statement=keep_fact.statement,
            reconciled_type=keep_fact.type,
            reconciled_rationale=(
                f"Facts are near-duplicates. Keeping {keep_fact.id} "
                f"and marking {remove_fact.id} as duplicate."
            ),
            facts_to_update=[],
            facts_to_deprecate=[remove_fact.id],
            facts_to_create=[],
            code_changes_needed=[],
            doc_changes_needed=[],
            verification_steps=[
                "Confirm facts are truly duplicates",
                "Merge any unique details from removed fact",
                f"Update references to point to {keep_fact.id}"
            ]
        )

    def _escalate_to_human(self, fact1: Fact, fact2: Fact,
                          conflict: ConflictAnalysis) -> ReconciliationProposal:
        """Escalate to human decision"""

        return ReconciliationProposal(
            conflict_id=conflict.conflict_id,
            strategy=ReconciliationStrategy.ESCALATE,
            confidence=0.5,
            conflicting_facts=[fact1.id, fact2.id],
            conflict_description=conflict.description,
            reconciled_statement="NEEDS HUMAN DECISION",
            reconciled_type="unresolved",
            reconciled_rationale=(
                f"Automated reconciliation cannot resolve this conflict with high "
                f"confidence. Requires human expertise to determine correct approach."
            ),
            facts_to_update=[],
            facts_to_deprecate=[],
            facts_to_create=[],
            code_changes_needed=["PENDING DECISION"],
            doc_changes_needed=["PENDING DECISION"],
            verification_steps=[
                "Schedule review meeting with domain experts",
                "Gather additional context about requirements",
                "Research historical decisions",
                "Make decision and document rationale",
                "Update facts accordingly"
            ]
        )

    def find_all_conflicts(self) -> List[ConflictAnalysis]:
        """Find all conflicts in the knowledge base"""
        relationships = self.store.get_relationships()
        contradictions = [r for r in relationships if r.type == RelationType.CONTRADICTS]

        conflicts = []
        for rel in contradictions:
            try:
                conflict = self.analyze_conflict(rel.fact_id_1, rel.fact_id_2, rel)
                conflicts.append(conflict)
            except Exception as e:
                print(f"Error analyzing conflict {rel.fact_id_1} <-> {rel.fact_id_2}: {e}")

        return conflicts

    def reconcile_all(self) -> List[ReconciliationProposal]:
        """Generate reconciliation proposals for all conflicts"""
        conflicts = self.find_all_conflicts()
        proposals = []

        for conflict in conflicts:
            try:
                proposal = self.propose_reconciliation(conflict)
                proposals.append(proposal)
            except Exception as e:
                print(f"Error generating proposal for {conflict.conflict_id}: {e}")

        return proposals

    def generate_report(self, proposals: List[ReconciliationProposal],
                       output_file: str = None) -> str:
        """Generate comprehensive reconciliation report"""

        report = []
        report.append("# Constraint Reconciliation Report")
        report.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Total Conflicts**: {len(proposals)}")
        report.append("")

        # Summary by strategy
        strategy_counts = {}
        for p in proposals:
            strategy_counts[p.strategy.value] = strategy_counts.get(p.strategy.value, 0) + 1

        report.append("## Summary by Strategy")
        report.append("")
        for strategy, count in sorted(strategy_counts.items(), key=lambda x: -x[1]):
            report.append(f"- **{strategy}**: {count}")
        report.append("")

        # Summary by severity
        report.append("## Conflicts by Severity")
        severity_groups = {'critical': [], 'high': [], 'medium': [], 'low': []}

        conflicts = self.find_all_conflicts()
        for conflict in conflicts:
            severity_groups[conflict.severity].append(conflict)

        for severity in ['critical', 'high', 'medium', 'low']:
            count = len(severity_groups[severity])
            if count > 0:
                report.append(f"- **{severity.upper()}**: {count}")
        report.append("")

        # Detailed proposals
        report.append("---")
        report.append("")
        report.append("## Detailed Reconciliation Proposals")
        report.append("")

        for i, proposal in enumerate(proposals, 1):
            report.append(f"### {i}. Conflict: {proposal.conflict_id}")
            report.append("")

            # Get fact details
            fact_ids = proposal.conflicting_facts
            facts = [self.store.get_fact(fid) for fid in fact_ids]

            report.append("#### Before (Conflicting Facts)")
            report.append("")
            for fact in facts:
                if fact:
                    report.append(f"**{fact.id}** ({fact.type}):")
                    report.append(f"> {fact.statement}")
                    report.append("")
                    if fact.extracted_from:
                        src = fact.extracted_from[0]
                        artifact = self.store.get_artifact(src.get('artifact_id', ''))
                        if artifact:
                            report.append(f"*Source*: {artifact.path} ({src.get('location', 'unknown')})")
                        report.append("")

            report.append(f"**Conflict Description**: {proposal.conflict_description}")
            report.append("")

            report.append("#### After (Reconciled)")
            report.append("")
            report.append(f"**Strategy**: {proposal.strategy.value}")
            report.append(f"**Confidence**: {proposal.confidence:.2f}")
            report.append("")
            report.append(f"**Reconciled Statement**:")
            report.append(f"> {proposal.reconciled_statement}")
            report.append("")
            report.append(f"**Rationale**: {proposal.reconciled_rationale}")
            report.append("")

            # Action items
            if proposal.code_changes_needed:
                report.append("#### Code Changes Needed")
                report.append("")
                for change in proposal.code_changes_needed:
                    report.append(f"- {change}")
                report.append("")

            if proposal.doc_changes_needed:
                report.append("#### Documentation Changes Needed")
                report.append("")
                for change in proposal.doc_changes_needed:
                    report.append(f"- {change}")
                report.append("")

            if proposal.verification_steps:
                report.append("#### Verification Steps")
                report.append("")
                for i, step in enumerate(proposal.verification_steps, 1):
                    report.append(f"{i}. {step}")
                report.append("")

            # What needs to change
            report.append("#### Impact")
            report.append("")
            if proposal.facts_to_update:
                report.append(f"- **Facts to update**: {', '.join(proposal.facts_to_update)}")
            if proposal.facts_to_deprecate:
                report.append(f"- **Facts to deprecate**: {', '.join(proposal.facts_to_deprecate)}")
            if proposal.facts_to_create:
                report.append(f"- **New facts to create**: {len(proposal.facts_to_create)}")
            report.append("")

            report.append("---")
            report.append("")

        # Action summary
        report.append("## Action Items Summary")
        report.append("")

        all_code_changes = []
        all_doc_changes = []

        for p in proposals:
            all_code_changes.extend(p.code_changes_needed)
            all_doc_changes.extend(p.doc_changes_needed)

        report.append(f"### Code Changes Required: {len(all_code_changes)}")
        report.append("")
        for change in all_code_changes:
            report.append(f"- {change}")
        report.append("")

        report.append(f"### Documentation Changes Required: {len(all_doc_changes)}")
        report.append("")
        for change in all_doc_changes:
            report.append(f"- {change}")
        report.append("")

        # Generate report text
        report_text = "\n".join(report)

        # Save if output file specified
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report_text)
            print(f"Report saved to {output_file}")

        return report_text


def main():
    """CLI for constraint reconciler"""
    if not KRAANG_AVAILABLE:
        print("Error: Kraang module not available")
        print("Make sure kraang.py is in the same directory")
        return 1

    if len(sys.argv) < 2:
        print("""Constraint Reconciler - Merge conflicting facts into coherent truth

Usage:
  python reconciler.py analyze              Analyze all conflicts
  python reconciler.py reconcile            Generate reconciliation proposals
  python reconciler.py report [output.md]   Generate full report
  python reconciler.py conflict <fact1> <fact2>  Analyze specific conflict

Examples:
  python reconciler.py analyze
  python reconciler.py reconcile
  python reconciler.py report RECONCILIATION_REPORT.md
  python reconciler.py conflict fact_16 fact_19
""")
        return 1

    command = sys.argv[1]
    store = KraangStore()
    reconciler = ConstraintReconciler(store)

    if command == "analyze":
        conflicts = reconciler.find_all_conflicts()
        print(f"Found {len(conflicts)} conflicts:")
        print()
        for conflict in conflicts:
            print(f"Conflict: {conflict.conflict_id}")
            print(f"  Type: {conflict.conflict_type}")
            print(f"  Severity: {conflict.severity}")
            print(f"  Facts: {', '.join(conflict.facts)}")
            print(f"  Description: {conflict.description[:100]}...")
            print()

    elif command == "reconcile":
        proposals = reconciler.reconcile_all()
        print(f"Generated {len(proposals)} reconciliation proposals:")
        print()
        for proposal in proposals:
            print(f"Conflict: {proposal.conflict_id}")
            print(f"  Strategy: {proposal.strategy.value}")
            print(f"  Confidence: {proposal.confidence:.2f}")
            print(f"  Reconciled: {proposal.reconciled_statement[:80]}...")
            print()

    elif command == "report":
        output_file = sys.argv[2] if len(sys.argv) > 2 else "RECONCILIATION_REPORT.md"
        proposals = reconciler.reconcile_all()
        report = reconciler.generate_report(proposals, output_file)
        print(f"Generated report with {len(proposals)} proposals")

    elif command == "conflict":
        if len(sys.argv) < 4:
            print("Usage: python reconciler.py conflict <fact1> <fact2>")
            return 1

        fact1_id = sys.argv[2]
        fact2_id = sys.argv[3]

        # Get relationship if exists
        relationships = store.get_relationships()
        rel = None
        for r in relationships:
            if (r.fact_id_1 == fact1_id and r.fact_id_2 == fact2_id) or \
               (r.fact_id_1 == fact2_id and r.fact_id_2 == fact1_id):
                rel = r
                break

        conflict = reconciler.analyze_conflict(fact1_id, fact2_id, rel)
        proposal = reconciler.propose_reconciliation(conflict)

        print(f"Conflict Analysis: {conflict.conflict_id}")
        print(f"  Type: {conflict.conflict_type}")
        print(f"  Severity: {conflict.severity}")
        print()
        print(f"Reconciliation Strategy: {proposal.strategy.value}")
        print(f"  Confidence: {proposal.confidence:.2f}")
        print()
        print(f"Reconciled Statement:")
        print(f"  {proposal.reconciled_statement}")
        print()
        print(f"Rationale:")
        print(f"  {proposal.reconciled_rationale}")
        print()

        if proposal.code_changes_needed:
            print("Code Changes:")
            for change in proposal.code_changes_needed:
                print(f"  - {change}")
            print()

        if proposal.doc_changes_needed:
            print("Doc Changes:")
            for change in proposal.doc_changes_needed:
                print(f"  - {change}")
            print()

    else:
        print(f"Unknown command: {command}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
