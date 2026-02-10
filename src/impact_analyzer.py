#!/usr/bin/env python3
"""
Impact Analyzer - Shows consequences of resolving conflicts

Core purpose: When we find a conflict, show what changes if we pick one resolution vs another.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque


class ResolutionType(Enum):
    """Types of conflict resolutions"""
    CHANGE_A = "change_a"  # Change fact A to align with B
    CHANGE_B = "change_b"  # Change fact B to align with A
    CHANGE_BOTH = "change_both"  # Change both facts to a third option
    ADD_CONSTRAINT = "add_constraint"  # Add a new constraint that resolves the conflict
    ACCEPT_BOTH = "accept_both"  # Accept both as valid in different contexts


class ImpactLevel(Enum):
    """Impact severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Conflict:
    """A conflict between two facts"""
    fact_a_id: str
    fact_b_id: str
    conflict_type: str
    confidence: float
    reasoning: str


@dataclass
class Resolution:
    """A proposed resolution to a conflict"""
    resolution_type: ResolutionType
    description: str
    target_facts: List[str]  # Facts that would change
    new_constraint: Optional[str] = None  # For ADD_CONSTRAINT type

    def to_dict(self):
        d = asdict(self)
        d['resolution_type'] = self.resolution_type.value
        return d


@dataclass
class FileImpact:
    """Impact on a specific file"""
    file_path: str
    artifact_id: str
    affected_locations: List[str]
    estimated_loc_changed: int
    complexity: str  # "trivial", "simple", "moderate", "complex"
    risk_factors: List[str]

    def to_dict(self):
        return asdict(self)


@dataclass
class FactImpact:
    """Impact on a specific fact"""
    fact_id: str
    change_required: str  # Description of change needed
    dependent_facts: List[str]  # Facts that depend on this one
    dependent_count: int
    risk_level: ImpactLevel

    def to_dict(self):
        d = asdict(self)
        d['risk_level'] = self.risk_level.value
        return d


@dataclass
class ImpactAnalysis:
    """Complete impact analysis for a resolution"""
    conflict: Conflict
    resolution: Resolution
    affected_facts: List[FactImpact]
    affected_files: List[FileImpact]
    broken_constraints: List[str]  # Constraints that might break
    total_loc_estimate: int
    total_files_affected: int
    overall_risk: ImpactLevel
    effort_estimate: str  # "1 hour", "1 day", "1 week", etc.
    recommendation_score: float  # 0-10, higher is better

    def to_dict(self):
        d = {
            'conflict': asdict(self.conflict),
            'resolution': self.resolution.to_dict(),
            'affected_facts': [f.to_dict() for f in self.affected_facts],
            'affected_files': [f.to_dict() for f in self.affected_files],
            'broken_constraints': self.broken_constraints,
            'total_loc_estimate': self.total_loc_estimate,
            'total_files_affected': self.total_files_affected,
            'overall_risk': self.overall_risk.value,
            'effort_estimate': self.effort_estimate,
            'recommendation_score': self.recommendation_score
        }
        return d


class ImpactAnalyzer:
    """
    Analyzes the impact of resolving conflicts.

    Core functionality:
    1. Takes a conflict between fact A and fact B
    2. Takes proposed resolutions
    3. Traces dependencies using relationship graph
    4. Shows ripple effects
    """

    def __init__(self, kraang_dir: str = ".kraang"):
        self.kraang_dir = Path(kraang_dir)
        self.facts: Dict[str, Dict] = {}
        self.relationships: List[Dict] = []
        self.artifacts: Dict[str, Dict] = {}
        self.dependency_graph: Dict[str, Set[str]] = defaultdict(set)
        self.reverse_dependency_graph: Dict[str, Set[str]] = defaultdict(set)

        self._load_data()
        self._build_dependency_graphs()

    def _load_data(self):
        """Load facts, relationships, and artifacts from Kraang store"""
        # Load facts
        facts_file = self.kraang_dir / "facts.json"
        if facts_file.exists():
            with open(facts_file) as f:
                facts_list = json.load(f)
                self.facts = {f['id']: f for f in facts_list}

        # Load relationships
        rels_file = self.kraang_dir / "relationships.json"
        if rels_file.exists():
            with open(rels_file) as f:
                self.relationships = json.load(f)

        # Load artifacts
        artifacts_file = self.kraang_dir / "artifacts.json"
        if artifacts_file.exists():
            with open(artifacts_file) as f:
                artifacts_list = json.load(f)
                self.artifacts = {a['id']: a for a in artifacts_list}

    def _build_dependency_graphs(self):
        """Build forward and reverse dependency graphs from relationships"""
        for rel in self.relationships:
            fact1 = rel['fact_id_1']
            fact2 = rel['fact_id_2']
            rel_type = rel['type']

            # Build directed graph based on relationship type
            if rel_type in ['supports', 'extends']:
                # fact2 depends on fact1
                self.dependency_graph[fact1].add(fact2)
                self.reverse_dependency_graph[fact2].add(fact1)
            elif rel_type == 'contradicts':
                # Bidirectional constraint
                self.dependency_graph[fact1].add(fact2)
                self.dependency_graph[fact2].add(fact1)
                self.reverse_dependency_graph[fact1].add(fact2)
                self.reverse_dependency_graph[fact2].add(fact1)

    def find_conflicts(self) -> List[Conflict]:
        """Find all conflicts in the relationship graph"""
        conflicts = []
        for rel in self.relationships:
            if rel['type'] == 'contradicts':
                conflict = Conflict(
                    fact_a_id=rel['fact_id_1'],
                    fact_b_id=rel['fact_id_2'],
                    conflict_type='contradiction',
                    confidence=rel['confidence'],
                    reasoning=rel['reasoning']
                )
                conflicts.append(conflict)
        return conflicts

    def get_dependent_facts(self, fact_id: str, max_depth: int = 10) -> Set[str]:
        """Get all facts that depend on this fact (BFS traversal)"""
        visited = set()
        queue = deque([(fact_id, 0)])

        while queue:
            current_fact, depth = queue.popleft()
            if current_fact in visited or depth > max_depth:
                continue

            visited.add(current_fact)

            # Add direct dependencies
            for dependent in self.dependency_graph.get(current_fact, set()):
                if dependent not in visited:
                    queue.append((dependent, depth + 1))

        visited.discard(fact_id)  # Remove the starting fact
        return visited

    def get_supporting_facts(self, fact_id: str, max_depth: int = 10) -> Set[str]:
        """Get all facts that support this fact (reverse BFS)"""
        visited = set()
        queue = deque([(fact_id, 0)])

        while queue:
            current_fact, depth = queue.popleft()
            if current_fact in visited or depth > max_depth:
                continue

            visited.add(current_fact)

            # Add facts this one depends on
            for supporter in self.reverse_dependency_graph.get(current_fact, set()):
                if supporter not in visited:
                    queue.append((supporter, depth + 1))

        visited.discard(fact_id)  # Remove the starting fact
        return visited

    def get_affected_files(self, fact_ids: List[str]) -> List[FileImpact]:
        """Get all files affected by changes to these facts"""
        file_impacts = {}

        for fact_id in fact_ids:
            if fact_id not in self.facts:
                continue

            fact = self.facts[fact_id]
            for ref in fact.get('extracted_from', []):
                artifact_id = ref.get('artifact_id')
                location = ref.get('location', 'unknown')

                if artifact_id not in self.artifacts:
                    continue

                artifact = self.artifacts[artifact_id]
                file_path = artifact.get('path', 'unknown')

                if file_path not in file_impacts:
                    file_impacts[file_path] = {
                        'file_path': file_path,
                        'artifact_id': artifact_id,
                        'affected_locations': [],
                        'fact_count': 0,
                        'artifact_type': artifact.get('type', 'unknown')
                    }

                file_impacts[file_path]['affected_locations'].append(location)
                file_impacts[file_path]['fact_count'] += 1

        # Convert to FileImpact objects with estimates
        impacts = []
        for file_path, data in file_impacts.items():
            complexity, loc_estimate = self._estimate_change_complexity(
                data['artifact_type'],
                data['fact_count'],
                len(data['affected_locations'])
            )

            risk_factors = self._assess_file_risk(file_path, data['artifact_type'])

            impact = FileImpact(
                file_path=file_path,
                artifact_id=data['artifact_id'],
                affected_locations=data['affected_locations'],
                estimated_loc_changed=loc_estimate,
                complexity=complexity,
                risk_factors=risk_factors
            )
            impacts.append(impact)

        return impacts

    def _estimate_change_complexity(self, artifact_type: str, fact_count: int,
                                    location_count: int) -> Tuple[str, int]:
        """Estimate complexity and LOC for changes"""
        # Base LOC estimate
        base_loc = {
            'code': 10,
            'doc': 5,
            'config': 3,
            'requirement': 2
        }.get(artifact_type, 5)

        loc_estimate = base_loc * fact_count

        # Complexity assessment
        if fact_count == 1 and location_count == 1:
            complexity = "trivial"
        elif fact_count <= 2 and location_count <= 3:
            complexity = "simple"
        elif fact_count <= 5 and location_count <= 10:
            complexity = "moderate"
        else:
            complexity = "complex"

        # Adjust LOC based on complexity
        complexity_multiplier = {
            "trivial": 1.0,
            "simple": 1.5,
            "moderate": 2.0,
            "complex": 3.0
        }
        loc_estimate = int(loc_estimate * complexity_multiplier[complexity])

        return complexity, loc_estimate

    def _assess_file_risk(self, file_path: str, artifact_type: str) -> List[str]:
        """Assess risk factors for modifying a file"""
        risks = []

        # Core infrastructure files
        if any(x in file_path.lower() for x in ['mud.h', 'types.h', 'functions.h', 'globals.h']):
            risks.append("Core header file - changes affect entire codebase")

        # C code vs docs
        if artifact_type == 'code':
            risks.append("Code changes require testing and compilation")
            if file_path.endswith('.c'):
                risks.append("C implementation - potential memory/pointer issues")

        # Config files
        if artifact_type == 'config':
            risks.append("Configuration change - may affect runtime behavior")

        # Large files
        if 'large' in file_path.lower() or any(x in file_path for x in ['5830', '2437']):
            risks.append("Large file - changes may be difficult to isolate")

        return risks if risks else ["Standard risk - normal development workflow"]

    def analyze_resolution(self, conflict: Conflict, resolution: Resolution) -> ImpactAnalysis:
        """Analyze the impact of a proposed resolution"""
        affected_fact_impacts = []
        all_affected_fact_ids = set(resolution.target_facts)

        # For each target fact, find dependencies
        for fact_id in resolution.target_facts:
            dependents = self.get_dependent_facts(fact_id)
            supporters = self.get_supporting_facts(fact_id)

            all_affected_fact_ids.update(dependents)

            # Determine change required based on resolution type
            change_desc = self._describe_change(resolution.resolution_type, fact_id, conflict)

            # Assess risk based on dependency count
            risk_level = self._assess_fact_risk(len(dependents), len(supporters))

            fact_impact = FactImpact(
                fact_id=fact_id,
                change_required=change_desc,
                dependent_facts=list(dependents),
                dependent_count=len(dependents),
                risk_level=risk_level
            )
            affected_fact_impacts.append(fact_impact)

        # Get affected files
        affected_files = self.get_affected_files(list(all_affected_fact_ids))

        # Find potentially broken constraints
        broken_constraints = self._find_broken_constraints(
            resolution.target_facts,
            all_affected_fact_ids
        )

        # Calculate totals
        total_loc = sum(f.estimated_loc_changed for f in affected_files)
        total_files = len(affected_files)

        # Determine overall risk
        overall_risk = self._calculate_overall_risk(
            affected_fact_impacts,
            affected_files,
            len(broken_constraints)
        )

        # Estimate effort
        effort = self._estimate_effort(total_loc, total_files, overall_risk)

        # Calculate recommendation score
        score = self._calculate_recommendation_score(
            resolution,
            overall_risk,
            total_files,
            len(broken_constraints),
            len(all_affected_fact_ids)
        )

        return ImpactAnalysis(
            conflict=conflict,
            resolution=resolution,
            affected_facts=affected_fact_impacts,
            affected_files=affected_files,
            broken_constraints=broken_constraints,
            total_loc_estimate=total_loc,
            total_files_affected=total_files,
            overall_risk=overall_risk,
            effort_estimate=effort,
            recommendation_score=score
        )

    def _describe_change(self, resolution_type: ResolutionType, fact_id: str,
                        conflict: Conflict) -> str:
        """Describe what change is needed for this fact"""
        descriptions = {
            ResolutionType.CHANGE_A: f"Modify to align with {conflict.fact_b_id}",
            ResolutionType.CHANGE_B: f"Modify to align with {conflict.fact_a_id}",
            ResolutionType.CHANGE_BOTH: "Modify to align with new unified constraint",
            ResolutionType.ADD_CONSTRAINT: "Add context to scope this constraint",
            ResolutionType.ACCEPT_BOTH: "Document as valid in specific context"
        }
        return descriptions.get(resolution_type, "Modify as needed")

    def _assess_fact_risk(self, dependent_count: int, supporter_count: int) -> ImpactLevel:
        """Assess risk level based on dependency counts"""
        # High risk if many dependents
        if dependent_count > 10:
            return ImpactLevel.CRITICAL
        elif dependent_count > 5:
            return ImpactLevel.HIGH
        elif dependent_count > 2:
            return ImpactLevel.MEDIUM
        else:
            return ImpactLevel.LOW

    def _find_broken_constraints(self, target_facts: List[str],
                                all_affected: Set[str]) -> List[str]:
        """Find constraints that might break due to the resolution"""
        broken = []

        for fact_id in all_affected:
            if fact_id not in self.facts:
                continue

            fact = self.facts[fact_id]
            if fact.get('type') == 'constraint' and fact_id not in target_facts:
                # This is a constraint that's affected but not directly targeted
                broken.append(fact_id)

        return broken

    def _calculate_overall_risk(self, fact_impacts: List[FactImpact],
                               file_impacts: List[FileImpact],
                               broken_count: int) -> ImpactLevel:
        """Calculate overall risk level"""
        # Check for critical fact risks
        if any(f.risk_level == ImpactLevel.CRITICAL for f in fact_impacts):
            return ImpactLevel.CRITICAL

        # Check for high complexity files
        if any(f.complexity == "complex" for f in file_impacts):
            return ImpactLevel.HIGH

        # Check for broken constraints
        if broken_count > 3:
            return ImpactLevel.HIGH
        elif broken_count > 1:
            return ImpactLevel.MEDIUM

        # Check for high risk facts
        if any(f.risk_level == ImpactLevel.HIGH for f in fact_impacts):
            return ImpactLevel.HIGH

        # Check number of affected files
        if len(file_impacts) > 10:
            return ImpactLevel.HIGH
        elif len(file_impacts) > 5:
            return ImpactLevel.MEDIUM

        # Default to medium if any moderate complexity
        if any(f.complexity in ["moderate", "complex"] for f in file_impacts):
            return ImpactLevel.MEDIUM

        return ImpactLevel.LOW

    def _estimate_effort(self, total_loc: int, total_files: int,
                        risk_level: ImpactLevel) -> str:
        """Estimate effort required"""
        # Base estimate on LOC
        if total_loc < 20:
            base = "1-2 hours"
        elif total_loc < 50:
            base = "half day"
        elif total_loc < 100:
            base = "1 day"
        elif total_loc < 300:
            base = "2-3 days"
        else:
            base = "1 week+"

        # Adjust for risk
        if risk_level in [ImpactLevel.CRITICAL, ImpactLevel.HIGH]:
            multiplier = " (plus extensive testing)"
        elif risk_level == ImpactLevel.MEDIUM:
            multiplier = " (plus testing)"
        else:
            multiplier = ""

        return base + multiplier

    def _calculate_recommendation_score(self, resolution: Resolution,
                                       risk_level: ImpactLevel,
                                       file_count: int,
                                       broken_count: int,
                                       affected_count: int) -> float:
        """Calculate recommendation score (0-10, higher is better)"""
        score = 10.0

        # Penalize by risk level
        risk_penalties = {
            ImpactLevel.LOW: 0,
            ImpactLevel.MEDIUM: 1.5,
            ImpactLevel.HIGH: 3.0,
            ImpactLevel.CRITICAL: 5.0
        }
        score -= risk_penalties[risk_level]

        # Penalize by number of affected files
        score -= min(file_count * 0.2, 3.0)

        # Penalize by broken constraints
        score -= min(broken_count * 0.5, 2.0)

        # Bonus for certain resolution types
        if resolution.resolution_type == ResolutionType.ADD_CONSTRAINT:
            score += 1.0  # Adding constraint is often cleanest
        elif resolution.resolution_type == ResolutionType.ACCEPT_BOTH:
            score += 0.5  # Accepting both is pragmatic

        # Ensure score is in valid range
        return max(0.0, min(10.0, score))

    def compare_resolutions(self, conflict: Conflict,
                          resolutions: List[Resolution]) -> Dict[str, Any]:
        """Compare multiple resolutions and recommend the best one"""
        analyses = []

        for resolution in resolutions:
            analysis = self.analyze_resolution(conflict, resolution)
            analyses.append(analysis)

        # Sort by recommendation score
        analyses.sort(key=lambda a: a.recommendation_score, reverse=True)

        return {
            'conflict': asdict(conflict),
            'analyses': [a.to_dict() for a in analyses],
            'recommended': analyses[0].to_dict() if analyses else None,
            'summary': self._generate_comparison_summary(analyses)
        }

    def _generate_comparison_summary(self, analyses: List[ImpactAnalysis]) -> str:
        """Generate a summary comparing the analyses"""
        if not analyses:
            return "No analyses available"

        best = analyses[0]

        summary = f"RECOMMENDED: {best.resolution.resolution_type.value}\n"
        summary += f"  Score: {best.recommendation_score:.1f}/10\n"
        summary += f"  Risk: {best.overall_risk.value}\n"
        summary += f"  Effort: {best.effort_estimate}\n"
        summary += f"  Files: {best.total_files_affected}\n"
        summary += f"  LOC: ~{best.total_loc_estimate}\n"

        if len(analyses) > 1:
            summary += f"\nAlternatives considered: {len(analyses) - 1}\n"
            for i, alt in enumerate(analyses[1:], 1):
                summary += f"  {i}. {alt.resolution.resolution_type.value} "
                summary += f"(score: {alt.recommendation_score:.1f}, "
                summary += f"risk: {alt.overall_risk.value})\n"

        return summary

    def generate_resolution_report(self, conflict: Conflict) -> Dict[str, Any]:
        """Generate a complete what-if analysis for all resolution options"""
        fact_a = self.facts.get(conflict.fact_a_id, {})
        fact_b = self.facts.get(conflict.fact_b_id, {})

        # Create standard resolution options
        resolutions = [
            Resolution(
                resolution_type=ResolutionType.CHANGE_A,
                description=f"Change '{fact_a.get('statement', 'fact A')[:50]}...' to align with fact B",
                target_facts=[conflict.fact_a_id]
            ),
            Resolution(
                resolution_type=ResolutionType.CHANGE_B,
                description=f"Change '{fact_b.get('statement', 'fact B')[:50]}...' to align with fact A",
                target_facts=[conflict.fact_b_id]
            ),
            Resolution(
                resolution_type=ResolutionType.CHANGE_BOTH,
                description="Refactor both facts to a new unified constraint",
                target_facts=[conflict.fact_a_id, conflict.fact_b_id]
            ),
            Resolution(
                resolution_type=ResolutionType.ADD_CONSTRAINT,
                description="Add a scoping constraint that allows both to be valid in different contexts",
                target_facts=[conflict.fact_a_id, conflict.fact_b_id],
                new_constraint="Context-dependent constraint to be defined"
            ),
            Resolution(
                resolution_type=ResolutionType.ACCEPT_BOTH,
                description="Document both as valid and explain the apparent contradiction",
                target_facts=[]
            )
        ]

        return self.compare_resolutions(conflict, resolutions)


def main():
    """Demo the impact analyzer"""
    import sys

    analyzer = ImpactAnalyzer()

    # Find conflicts
    conflicts = analyzer.find_conflicts()

    print("=" * 80)
    print("IMPACT ANALYZER - Conflict Resolution Analysis")
    print("=" * 80)
    print(f"\nFound {len(conflicts)} conflicts in the knowledge base\n")

    if not conflicts:
        print("No conflicts to analyze. The knowledge base is consistent!")
        return

    # Analyze first few conflicts
    max_conflicts = min(3, len(conflicts))

    for i, conflict in enumerate(conflicts[:max_conflicts], 1):
        print("=" * 80)
        print(f"CONFLICT #{i}")
        print("=" * 80)

        fact_a = analyzer.facts.get(conflict.fact_a_id, {})
        fact_b = analyzer.facts.get(conflict.fact_b_id, {})

        print(f"\nFact A ({conflict.fact_a_id}): {fact_a.get('statement', 'Unknown')[:100]}...")
        print(f"Fact B ({conflict.fact_b_id}): {fact_b.get('statement', 'Unknown')[:100]}...")
        print(f"\nReasoning: {conflict.reasoning[:200]}...")
        print(f"Confidence: {conflict.confidence}")

        # Generate resolution report
        print("\n" + "-" * 80)
        print("RESOLUTION ANALYSIS")
        print("-" * 80)

        report = analyzer.generate_resolution_report(conflict)
        print(report['summary'])

        # Save detailed report
        output_file = f"conflict_{i}_analysis.json"
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\nDetailed analysis saved to: {output_file}")
        print()

    print("=" * 80)
    print("Analysis complete!")
    print("=" * 80)


if __name__ == '__main__':
    main()
