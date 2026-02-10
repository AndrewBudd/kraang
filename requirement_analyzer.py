#!/usr/bin/env python3
"""
Requirement Analyzer - Analyzes proposed NEW requirements against existing constraints

Analyzes proposed features/requirements by:
1. Extracting facts from the proposed requirement
2. Comparing against ALL existing facts in the knowledge base
3. Identifying conflicts, dependencies, and impacts
4. Generating a feasibility report with recommendations
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import anthropic
from kraang import KraangStore, Fact, Relationship, RelationType


class ConflictSeverity(Enum):
    CRITICAL = "critical"  # Direct contradiction, cannot proceed
    HIGH = "high"  # Major conflict, significant redesign needed
    MEDIUM = "medium"  # Moderate conflict, workarounds possible
    LOW = "low"  # Minor conflict, easy to resolve
    INFO = "info"  # Not a conflict, just related information


@dataclass
class RequirementFact:
    """A fact extracted from a proposed requirement"""
    statement: str
    type: str
    confidence: float


@dataclass
class Conflict:
    """A conflict between proposed requirement and existing constraint"""
    requirement_fact: RequirementFact
    existing_fact: Fact
    severity: ConflictSeverity
    reasoning: str
    confidence: float

    def to_dict(self):
        return {
            'requirement_fact': asdict(self.requirement_fact),
            'existing_fact': self.existing_fact.to_dict(),
            'severity': self.severity.value,
            'reasoning': self.reasoning,
            'confidence': self.confidence
        }


@dataclass
class Dependency:
    """A dependency on existing facts"""
    requirement_fact: RequirementFact
    existing_fact: Fact
    dependency_type: str  # requires, modifies, extends
    reasoning: str

    def to_dict(self):
        return {
            'requirement_fact': asdict(self.requirement_fact),
            'existing_fact': self.existing_fact.to_dict(),
            'dependency_type': self.dependency_type,
            'reasoning': self.reasoning
        }


@dataclass
class ImpactArea:
    """An area of code/documentation that would need changes"""
    artifact_id: str
    artifact_path: str
    location: str
    change_type: str  # modify, remove, add
    description: str

    def to_dict(self):
        return asdict(self)


@dataclass
class FeasibilityReport:
    """Complete analysis of a proposed requirement"""
    requirement: str
    extracted_facts: List[RequirementFact]
    conflicts: List[Conflict]
    dependencies: List[Dependency]
    impact_areas: List[ImpactArea]
    feasibility_score: float  # 0.0 to 1.0
    overall_assessment: str
    recommendations: List[str]

    def to_dict(self):
        return {
            'requirement': self.requirement,
            'extracted_facts': [asdict(f) for f in self.extracted_facts],
            'conflicts': [c.to_dict() for c in self.conflicts],
            'dependencies': [d.to_dict() for d in self.dependencies],
            'impact_areas': [ia.to_dict() for ia in self.impact_areas],
            'feasibility_score': self.feasibility_score,
            'overall_assessment': self.overall_assessment,
            'recommendations': self.recommendations
        }


class RequirementAnalyzer:
    """Analyzes proposed requirements against existing constraints"""

    def __init__(self, store: KraangStore = None, api_key: str = None):
        self.store = store or KraangStore()

        if api_key is None:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY environment variable not set")

        self.client = anthropic.Anthropic(api_key=api_key)

    def extract_requirement_facts(self, requirement: str) -> List[RequirementFact]:
        """Extract facts from a proposed requirement using LLM"""

        prompt = f"""You are analyzing a PROPOSED NEW requirement to extract its key facts and implications.

Proposed Requirement:
{requirement}

Please extract all significant facts, implications, and constraints from this proposed requirement.
Consider:
- What constraints does it introduce?
- What capabilities does it require?
- What existing systems might it affect?
- What technical changes would be needed?
- What resources would be needed?

For each fact, provide:
1. A clear, concise statement of the fact/constraint/implication
2. The type (requirement, implementation, design, constraint, capability)
3. Your confidence level (0.0 to 1.0)

Return your response as a JSON array of facts with this structure:
[
  {{
    "statement": "The fact or constraint",
    "type": "requirement|implementation|design|constraint|capability",
    "confidence": 0.9
  }},
  ...
]

Return ONLY the JSON array, no additional text."""

        message = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text

        # Extract JSON from response
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        try:
            facts_data = json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"Error parsing LLM response: {e}")
            print(f"Response: {response_text[:500]}")
            raise

        return [RequirementFact(**f) for f in facts_data]

    def analyze_conflict(
        self,
        req_fact: RequirementFact,
        existing_fact: Fact
    ) -> Optional[Conflict]:
        """Analyze if a requirement fact conflicts with an existing fact"""

        prompt = f"""Analyze if these two facts conflict with each other.

PROPOSED Requirement Fact:
"{req_fact.statement}"
(Type: {req_fact.type})

EXISTING System Fact:
"{existing_fact.statement}"
(Type: {existing_fact.type}, ID: {existing_fact.id})
Source: {existing_fact.extracted_from}

Determine:
1. Do they conflict? (yes/no)
2. If yes, how severe is the conflict?
   - CRITICAL: Direct contradiction, cannot proceed without removing constraint
   - HIGH: Major conflict, significant redesign needed
   - MEDIUM: Moderate conflict, workarounds possible
   - LOW: Minor conflict, easy to resolve
   - INFO: Not a conflict, but related/relevant information

3. Explain the relationship and why it's a conflict (or not)

Return a JSON object:
{{
  "is_conflict": true/false,
  "severity": "critical|high|medium|low|info",
  "reasoning": "Brief explanation",
  "confidence": 0.9
}}

Return ONLY the JSON object, no additional text."""

        message = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text

        # Extract JSON
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        try:
            result = json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"Error parsing conflict analysis: {e}")
            return None

        if not result.get('is_conflict', False):
            return None

        return Conflict(
            requirement_fact=req_fact,
            existing_fact=existing_fact,
            severity=ConflictSeverity(result['severity']),
            reasoning=result['reasoning'],
            confidence=result.get('confidence', 0.5)
        )

    def analyze_dependencies(
        self,
        req_fact: RequirementFact,
        existing_fact: Fact
    ) -> Optional[Dependency]:
        """Analyze if a requirement fact depends on an existing fact"""

        prompt = f"""Analyze if the proposed requirement depends on or relates to the existing fact.

PROPOSED Requirement Fact:
"{req_fact.statement}"

EXISTING System Fact:
"{existing_fact.statement}"
(ID: {existing_fact.id})

Determine:
1. Is there a dependency relationship? (yes/no)
2. If yes, what type?
   - REQUIRES: The requirement needs this existing fact to work
   - MODIFIES: The requirement would change this existing fact
   - EXTENDS: The requirement builds upon this existing fact
   - RELATED: Just related, no direct dependency

3. Explain the relationship

Return a JSON object:
{{
  "has_dependency": true/false,
  "dependency_type": "requires|modifies|extends|related",
  "reasoning": "Brief explanation"
}}

Return ONLY the JSON object, no additional text."""

        message = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text

        # Extract JSON
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        try:
            result = json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"Error parsing dependency analysis: {e}")
            return None

        if not result.get('has_dependency', False):
            return None

        dep_type = result.get('dependency_type', 'related').lower()
        if dep_type not in ['requires', 'modifies', 'extends', 'related']:
            return None

        return Dependency(
            requirement_fact=req_fact,
            existing_fact=existing_fact,
            dependency_type=dep_type,
            reasoning=result['reasoning']
        )

    def identify_impact_areas(
        self,
        requirement: str,
        conflicts: List[Conflict],
        dependencies: List[Dependency]
    ) -> List[ImpactArea]:
        """Identify what artifacts would need to change"""

        impact_areas = []
        seen_artifacts = set()

        # From conflicts - things that need to change
        for conflict in conflicts:
            for ref in conflict.existing_fact.extracted_from:
                artifact_id = ref['artifact_id']
                if artifact_id in seen_artifacts:
                    continue
                seen_artifacts.add(artifact_id)

                artifact = self.store.get_artifact(artifact_id)
                if artifact:
                    change_type = "modify"
                    if conflict.severity == ConflictSeverity.CRITICAL:
                        change_type = "remove_or_modify"

                    impact_areas.append(ImpactArea(
                        artifact_id=artifact_id,
                        artifact_path=artifact.path,
                        location=ref['location'],
                        change_type=change_type,
                        description=f"Conflicts with: {conflict.existing_fact.statement[:100]}"
                    ))

        # From dependencies - things that might need updates
        for dep in dependencies:
            if dep.dependency_type in ['modifies', 'extends']:
                for ref in dep.existing_fact.extracted_from:
                    artifact_id = ref['artifact_id']
                    if artifact_id in seen_artifacts:
                        continue
                    seen_artifacts.add(artifact_id)

                    artifact = self.store.get_artifact(artifact_id)
                    if artifact:
                        impact_areas.append(ImpactArea(
                            artifact_id=artifact_id,
                            artifact_path=artifact.path,
                            location=ref['location'],
                            change_type="modify",
                            description=f"Depends on: {dep.existing_fact.statement[:100]}"
                        ))

        return impact_areas

    def calculate_feasibility_score(
        self,
        conflicts: List[Conflict],
        dependencies: List[Dependency],
        impact_areas: List[ImpactArea]
    ) -> float:
        """Calculate overall feasibility score (0.0 to 1.0)"""

        score = 1.0

        # Conflicts reduce feasibility
        for conflict in conflicts:
            if conflict.severity == ConflictSeverity.CRITICAL:
                score -= 0.3 * conflict.confidence
            elif conflict.severity == ConflictSeverity.HIGH:
                score -= 0.2 * conflict.confidence
            elif conflict.severity == ConflictSeverity.MEDIUM:
                score -= 0.1 * conflict.confidence
            elif conflict.severity == ConflictSeverity.LOW:
                score -= 0.05 * conflict.confidence

        # Many dependencies reduce feasibility
        if len(dependencies) > 10:
            score -= 0.1
        elif len(dependencies) > 20:
            score -= 0.2

        # Many impact areas reduce feasibility
        if len(impact_areas) > 5:
            score -= 0.05
        elif len(impact_areas) > 10:
            score -= 0.1

        return max(0.0, min(1.0, score))

    def generate_recommendations(
        self,
        requirement: str,
        conflicts: List[Conflict],
        dependencies: List[Dependency],
        feasibility_score: float
    ) -> List[str]:
        """Generate actionable recommendations"""

        recommendations = []

        # Critical conflicts
        critical_conflicts = [c for c in conflicts if c.severity == ConflictSeverity.CRITICAL]
        if critical_conflicts:
            recommendations.append(
                f"CRITICAL: Resolve {len(critical_conflicts)} critical conflicts before proceeding"
            )
            for c in critical_conflicts[:3]:  # Show top 3
                recommendations.append(
                    f"  - {c.reasoning}"
                )

        # High severity conflicts
        high_conflicts = [c for c in conflicts if c.severity == ConflictSeverity.HIGH]
        if high_conflicts:
            recommendations.append(
                f"Address {len(high_conflicts)} high-severity conflicts through redesign"
            )

        # Feasibility-based recommendations
        if feasibility_score < 0.3:
            recommendations.append(
                "Feasibility is very low. Consider alternative approaches or breaking into smaller increments."
            )
        elif feasibility_score < 0.6:
            recommendations.append(
                "Feasibility is moderate. Significant effort required to resolve conflicts."
            )
        else:
            recommendations.append(
                "Feasibility is good. Focus on resolving identified conflicts."
            )

        # Dependency recommendations
        modify_deps = [d for d in dependencies if d.dependency_type == 'modifies']
        if modify_deps:
            recommendations.append(
                f"Plan to modify {len(modify_deps)} existing components carefully"
            )

        return recommendations

    def analyze(
        self,
        requirement: str,
        max_conflicts_to_check: int = 100,
        max_dependencies_to_check: int = 50,
        verbose: bool = True
    ) -> FeasibilityReport:
        """
        Analyze a proposed requirement against all existing constraints

        Args:
            requirement: Natural language description of proposed feature
            max_conflicts_to_check: Maximum existing facts to check for conflicts
            max_dependencies_to_check: Maximum existing facts to check for dependencies
            verbose: Print progress information

        Returns:
            FeasibilityReport with complete analysis
        """

        if verbose:
            print(f"Analyzing requirement: {requirement[:100]}...")
            print()

        # Step 1: Extract facts from requirement
        if verbose:
            print("[1/5] Extracting facts from proposed requirement...")

        req_facts = self.extract_requirement_facts(requirement)

        if verbose:
            print(f"      Extracted {len(req_facts)} facts from requirement")
            for fact in req_facts:
                print(f"      - {fact.statement}")
            print()

        # Step 2: Load all existing facts
        if verbose:
            print("[2/5] Loading existing constraints from knowledge base...")

        all_facts = self.store.get_facts()

        if verbose:
            print(f"      Loaded {len(all_facts)} existing facts")
            print()

        # Step 3: Check for conflicts (limit to most relevant)
        if verbose:
            print(f"[3/5] Checking for conflicts (top {max_conflicts_to_check} facts)...")

        conflicts = []
        facts_to_check = all_facts[:max_conflicts_to_check]

        for i, req_fact in enumerate(req_facts):
            if verbose:
                print(f"      Checking requirement fact {i+1}/{len(req_facts)}: {req_fact.statement[:60]}...")

            for existing_fact in facts_to_check:
                conflict = self.analyze_conflict(req_fact, existing_fact)
                if conflict:
                    conflicts.append(conflict)
                    if verbose:
                        print(f"        CONFLICT ({conflict.severity.value}): {conflict.reasoning[:80]}")

        if verbose:
            print(f"      Found {len(conflicts)} conflicts")
            print()

        # Step 4: Check for dependencies
        if verbose:
            print(f"[4/5] Checking for dependencies (top {max_dependencies_to_check} facts)...")

        dependencies = []
        deps_to_check = all_facts[:max_dependencies_to_check]

        for i, req_fact in enumerate(req_facts):
            for existing_fact in deps_to_check:
                dep = self.analyze_dependencies(req_fact, existing_fact)
                if dep:
                    dependencies.append(dep)

        if verbose:
            print(f"      Found {len(dependencies)} dependencies")
            print()

        # Step 5: Identify impact areas
        if verbose:
            print("[5/5] Identifying impact areas...")

        impact_areas = self.identify_impact_areas(requirement, conflicts, dependencies)

        if verbose:
            print(f"      Identified {len(impact_areas)} impact areas")
            print()

        # Calculate feasibility
        feasibility_score = self.calculate_feasibility_score(
            conflicts, dependencies, impact_areas
        )

        # Generate assessment
        if feasibility_score >= 0.8:
            assessment = "HIGH - Requirement appears feasible with minor conflicts"
        elif feasibility_score >= 0.6:
            assessment = "MODERATE - Requirement is feasible but requires careful planning"
        elif feasibility_score >= 0.4:
            assessment = "LOW - Significant conflicts exist, major effort required"
        else:
            assessment = "VERY LOW - Critical conflicts make this very difficult"

        # Generate recommendations
        recommendations = self.generate_recommendations(
            requirement, conflicts, dependencies, feasibility_score
        )

        return FeasibilityReport(
            requirement=requirement,
            extracted_facts=req_facts,
            conflicts=conflicts,
            dependencies=dependencies,
            impact_areas=impact_areas,
            feasibility_score=feasibility_score,
            overall_assessment=assessment,
            recommendations=recommendations
        )


def print_report(report: FeasibilityReport):
    """Print a formatted feasibility report"""

    print("=" * 80)
    print("REQUIREMENT FEASIBILITY ANALYSIS")
    print("=" * 80)
    print()

    print("PROPOSED REQUIREMENT:")
    print(f"  {report.requirement}")
    print()

    print(f"FEASIBILITY SCORE: {report.feasibility_score:.2f} / 1.00")
    print(f"ASSESSMENT: {report.overall_assessment}")
    print()

    print("-" * 80)
    print("EXTRACTED FACTS FROM REQUIREMENT")
    print("-" * 80)
    print(f"Found {len(report.extracted_facts)} facts in proposed requirement:")
    print()
    for i, fact in enumerate(report.extracted_facts, 1):
        print(f"{i}. [{fact.type}] {fact.statement}")
        print(f"   Confidence: {fact.confidence:.2f}")
        print()

    print("-" * 80)
    print("CONFLICTS WITH EXISTING CONSTRAINTS")
    print("-" * 80)

    if not report.conflicts:
        print("No conflicts found.")
        print()
    else:
        print(f"Found {len(report.conflicts)} conflicts:")
        print()

        # Group by severity
        by_severity = {}
        for conflict in report.conflicts:
            sev = conflict.severity.value
            if sev not in by_severity:
                by_severity[sev] = []
            by_severity[sev].append(conflict)

        for severity in ['critical', 'high', 'medium', 'low', 'info']:
            if severity not in by_severity:
                continue

            conflicts = by_severity[severity]
            print(f"\n{severity.upper()} SEVERITY ({len(conflicts)} conflicts):")
            print()

            for conflict in conflicts:
                print(f"  Requirement: {conflict.requirement_fact.statement}")
                print(f"  Conflicts with [{conflict.existing_fact.id}]: {conflict.existing_fact.statement}")
                print(f"  Reasoning: {conflict.reasoning}")
                print(f"  Confidence: {conflict.confidence:.2f}")

                # Show source
                if conflict.existing_fact.extracted_from:
                    ref = conflict.existing_fact.extracted_from[0]
                    artifact = None
                    if 'artifact_id' in ref:
                        from kraang import KraangStore
                        store = KraangStore()
                        artifact = store.get_artifact(ref['artifact_id'])
                    if artifact:
                        print(f"  Source: {artifact.path} ({ref['location']})")
                print()

    print("-" * 80)
    print("DEPENDENCIES ON EXISTING FACTS")
    print("-" * 80)

    if not report.dependencies:
        print("No dependencies found.")
        print()
    else:
        print(f"Found {len(report.dependencies)} dependencies:")
        print()

        for dep in report.dependencies:
            print(f"  Requirement: {dep.requirement_fact.statement}")
            print(f"  {dep.dependency_type.upper()} [{dep.existing_fact.id}]: {dep.existing_fact.statement}")
            print(f"  Reasoning: {dep.reasoning}")
            print()

    print("-" * 80)
    print("IMPACT AREAS (Code/Docs Needing Changes)")
    print("-" * 80)

    if not report.impact_areas:
        print("No specific impact areas identified.")
        print()
    else:
        print(f"Would affect {len(report.impact_areas)} areas:")
        print()

        for area in report.impact_areas:
            print(f"  [{area.change_type.upper()}] {area.artifact_path}")
            print(f"    Location: {area.location}")
            print(f"    Reason: {area.description}")
            print()

    print("-" * 80)
    print("RECOMMENDATIONS")
    print("-" * 80)
    print()

    for i, rec in enumerate(report.recommendations, 1):
        if rec.startswith("  "):
            print(f"    {rec.strip()}")
        else:
            print(f"{i}. {rec}")

    print()
    print("=" * 80)


def main():
    """CLI for requirement analyzer"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Analyze proposed requirements against existing constraints"
    )
    parser.add_argument(
        'requirement',
        nargs='?',
        help='Proposed requirement (or use --file)'
    )
    parser.add_argument(
        '--file', '-f',
        help='Read requirement from file'
    )
    parser.add_argument(
        '--max-conflicts',
        type=int,
        default=100,
        help='Maximum facts to check for conflicts (default: 100)'
    )
    parser.add_argument(
        '--max-dependencies',
        type=int,
        default=50,
        help='Maximum facts to check for dependencies (default: 50)'
    )
    parser.add_argument(
        '--output', '-o',
        help='Save report to JSON file'
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress progress messages'
    )

    args = parser.parse_args()

    # Get requirement text
    if args.file:
        with open(args.file, 'r') as f:
            requirement = f.read().strip()
    elif args.requirement:
        requirement = args.requirement
    else:
        parser.print_help()
        sys.exit(1)

    # Run analysis
    analyzer = RequirementAnalyzer()
    report = analyzer.analyze(
        requirement,
        max_conflicts_to_check=args.max_conflicts,
        max_dependencies_to_check=args.max_dependencies,
        verbose=not args.quiet
    )

    # Print report
    print_report(report)

    # Save to file if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report.to_dict(), f, indent=2)
        print(f"\nReport saved to: {args.output}")


if __name__ == "__main__":
    main()
