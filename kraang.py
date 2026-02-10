#!/usr/bin/env python3
"""
Kraang - Constraint Rationalization Engine

Core thesis: "The core activity of building software is rationalizing conflicting constraints."
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import anthropic

# Import coverage analyzer if available
try:
    from coverage import CoverageAnalyzer
    COVERAGE_AVAILABLE = True
except ImportError:
    COVERAGE_AVAILABLE = False

# Import multi-pass extraction if available
try:
    from multi_pass_extraction import MultiPassExtractor
    MULTI_PASS_AVAILABLE = True
except ImportError:
    MULTI_PASS_AVAILABLE = False


class RelationType(Enum):
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    EXTENDS = "extends"
    UNKNOWN = "unknown"


@dataclass
class ArtifactReference:
    """Reference to a location in an artifact"""
    artifact_id: str
    location: str  # e.g., "lines 10-15", "function do_command", etc.

    def to_dict(self):
        return asdict(self)


@dataclass
class Artifact:
    """A source document (code, docs, requirements)"""
    id: str
    type: str  # code, doc, requirement, config
    path: str
    content: Optional[str] = None

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(data: Dict) -> 'Artifact':
        return Artifact(**data)


@dataclass
class Fact:
    """A constraint or fact extracted from artifacts"""
    id: str
    statement: str
    type: str  # requirement, implementation, design, constraint
    extracted_from: List[Dict]  # List of ArtifactReference dicts
    confidence: float = 1.0

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(data: Dict) -> 'Fact':
        return Fact(**data)


@dataclass
class Relationship:
    """Relationship between two facts"""
    fact_id_1: str
    fact_id_2: str
    type: RelationType
    confidence: float
    reasoning: str

    def to_dict(self):
        d = asdict(self)
        d['type'] = self.type.value
        return d

    @staticmethod
    def from_dict(data: Dict) -> 'Relationship':
        data['type'] = RelationType(data['type'])
        return Relationship(**data)


class KraangStore:
    """Manages persistent storage of Kraang data"""

    def __init__(self, base_dir: str = ".kraang"):
        self.base_dir = Path(base_dir)
        self.artifacts_file = self.base_dir / "artifacts.json"
        self.facts_file = self.base_dir / "facts.json"
        self.relationships_file = self.base_dir / "relationships.json"
        self.config_file = self.base_dir / "config.json"

    def init(self):
        """Initialize a new Kraang project"""
        self.base_dir.mkdir(exist_ok=True)

        if not self.artifacts_file.exists():
            self._save_json(self.artifacts_file, [])
        if not self.facts_file.exists():
            self._save_json(self.facts_file, [])
        if not self.relationships_file.exists():
            self._save_json(self.relationships_file, [])
        if not self.config_file.exists():
            self._save_json(self.config_file, {"next_id": 1})

    def _load_json(self, file_path: Path) -> Any:
        with open(file_path, 'r') as f:
            return json.load(f)

    def _save_json(self, file_path: Path, data: Any):
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)

    def get_next_id(self) -> str:
        """Get next available ID"""
        config = self._load_json(self.config_file)
        next_id = config["next_id"]
        config["next_id"] = next_id + 1
        self._save_json(self.config_file, config)
        return str(next_id)

    def add_artifact(self, artifact: Artifact):
        artifacts = self._load_json(self.artifacts_file)
        artifacts.append(artifact.to_dict())
        self._save_json(self.artifacts_file, artifacts)

    def get_artifacts(self) -> List[Artifact]:
        data = self._load_json(self.artifacts_file)
        return [Artifact.from_dict(a) for a in data]

    def get_artifact(self, artifact_id: str) -> Optional[Artifact]:
        artifacts = self.get_artifacts()
        for a in artifacts:
            if a.id == artifact_id:
                return a
        return None

    def add_fact(self, fact: Fact):
        facts = self._load_json(self.facts_file)
        facts.append(fact.to_dict())
        self._save_json(self.facts_file, facts)

    def get_facts(self) -> List[Fact]:
        data = self._load_json(self.facts_file)
        return [Fact.from_dict(f) for f in data]

    def get_fact(self, fact_id: str) -> Optional[Fact]:
        facts = self.get_facts()
        for f in facts:
            if f.id == fact_id:
                return f
        return None

    def add_relationship(self, relationship: Relationship):
        relationships = self._load_json(self.relationships_file)
        relationships.append(relationship.to_dict())
        self._save_json(self.relationships_file, relationships)

    def get_relationships(self) -> List[Relationship]:
        data = self._load_json(self.relationships_file)
        return [Relationship.from_dict(r) for r in data]

    def get_relationships_for_fact(self, fact_id: str) -> List[Relationship]:
        all_rels = self.get_relationships()
        return [r for r in all_rels if r.fact_id_1 == fact_id or r.fact_id_2 == fact_id]


class KraangExtractor:
    """LLM-powered fact extraction"""

    def __init__(self, store: KraangStore):
        self.store = store
        # Get API key from environment
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        self.client = anthropic.Anthropic(api_key=api_key)

    def extract_facts(self, artifact: Artifact) -> List[Fact]:
        """Extract facts from an artifact using Claude"""

        prompt = f"""You are analyzing a software artifact to extract facts and constraints.

Artifact Type: {artifact.type}
Path: {artifact.path}

Content:
{artifact.content}

Please extract all significant facts, constraints, requirements, and implementation details from this artifact.

For each fact, provide:
1. A clear, concise statement of the fact/constraint
2. The type (requirement, implementation, design, constraint)
3. The specific location in the artifact (line numbers, function name, section, etc.)
4. Your confidence level (0.0 to 1.0)

Focus on extractable, verifiable facts. Examples:
- "Memory allocation MUST use CREATE macro, not malloc" (constraint)
- "Docker-compose is required for local development" (requirement)
- "User authentication uses JWT tokens" (implementation)
- "The system processes user input via do_command function" (implementation)

Return your response as a JSON array of facts with this structure:
[
  {{
    "statement": "The fact or constraint",
    "type": "requirement|implementation|design|constraint",
    "location": "Specific location in artifact",
    "confidence": 0.9
  }},
  ...
]

Return ONLY the JSON array, no additional text."""

        message = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=8192,
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse response
        response_text = message.content[0].text

        # Extract JSON from response (handle potential markdown code blocks)
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        # Debug: save raw response
        debug_file = Path(".kraang/last_response.txt")
        with open(debug_file, 'w') as f:
            f.write(response_text)

        try:
            facts_data = json.loads(response_text)
        except json.JSONDecodeError as e:
            # Try to recover from truncated response
            print(f"⚠ JSON parsing failed, attempting to recover truncated response...")
            # Find the last complete JSON object
            lines = response_text.split('\n')
            # Walk backwards to find last complete object (ends with })
            for i in range(len(lines) - 1, -1, -1):
                if lines[i].strip().endswith('}') or lines[i].strip().endswith('},'):
                    # Try closing the array here
                    recovered = '\n'.join(lines[:i+1])
                    if recovered.strip().endswith(','):
                        recovered = recovered.rsplit(',', 1)[0]
                    recovered += '\n]'
                    try:
                        facts_data = json.loads(recovered)
                        print(f"✓ Recovered {len(facts_data)} facts from truncated response")
                        break
                    except:
                        continue
            else:
                print(f"✗ Could not recover from truncation")
                print(f"✗ Response saved to {debug_file}")
                raise e

        # Convert to Fact objects
        facts = []
        for fact_data in facts_data:
            fact_id = self.store.get_next_id()
            ref = ArtifactReference(
                artifact_id=artifact.id,
                location=fact_data["location"]
            )
            fact = Fact(
                id=f"fact_{fact_id}",
                statement=fact_data["statement"],
                type=fact_data["type"],
                extracted_from=[ref.to_dict()],
                confidence=fact_data.get("confidence", 1.0)
            )
            facts.append(fact)

        return facts

    def analyze_relationships(self, fact1: Fact, fact2: Fact) -> Optional[Relationship]:
        """Analyze relationship between two facts"""

        prompt = f"""Analyze the relationship between these two facts/constraints:

Fact 1: {fact1.statement}
(Type: {fact1.type}, from: {fact1.extracted_from})

Fact 2: {fact2.statement}
(Type: {fact2.type}, from: {fact2.extracted_from})

Determine if these facts:
- SUPPORT each other (reinforce, align with, complement)
- CONTRADICT each other (conflict, are incompatible)
- EXTEND each other (one builds on the other)
- Are UNRELATED

Return a JSON object with this structure:
{{
  "relationship": "supports|contradicts|extends|unrelated",
  "confidence": 0.9,
  "reasoning": "Brief explanation of the relationship"
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
            rel_data = json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"✗ JSON parsing failed in relationship analysis: {e}")
            print(f"Response: {response_text[:200]}")
            return None

        if rel_data["relationship"] == "unrelated":
            return None

        return Relationship(
            fact_id_1=fact1.id,
            fact_id_2=fact2.id,
            type=RelationType(rel_data["relationship"]),
            confidence=rel_data["confidence"],
            reasoning=rel_data["reasoning"]
        )


class KraangCLI:
    """Command-line interface for Kraang"""

    def __init__(self):
        self.store = KraangStore()

    def cmd_init(self):
        """Initialize a new Kraang project"""
        self.store.init()
        print("✓ Initialized Kraang project in .kraang/")

    def cmd_add(self, path: str, artifact_type: str = None):
        """Add an artifact to the project"""
        path_obj = Path(path)

        if not path_obj.exists():
            print(f"✗ Path not found: {path}")
            return

        # Auto-detect type if not specified
        if artifact_type is None:
            if path_obj.suffix in ['.c', '.h', '.py', '.js', '.lua']:
                artifact_type = "code"
            elif path_obj.suffix in ['.md', '.txt', '.rst']:
                artifact_type = "doc"
            else:
                artifact_type = "unknown"

        # Read content
        try:
            with open(path_obj, 'r') as f:
                content = f.read()
        except Exception as e:
            print(f"✗ Error reading file: {e}")
            return

        artifact_id = f"artifact_{self.store.get_next_id()}"
        artifact = Artifact(
            id=artifact_id,
            type=artifact_type,
            path=str(path_obj),
            content=content
        )

        self.store.add_artifact(artifact)
        print(f"✓ Added artifact: {artifact_id} ({artifact_type})")
        print(f"  Path: {path}")

    def cmd_extract(self, artifact_id: str):
        """Extract facts from an artifact"""
        artifact = self.store.get_artifact(artifact_id)
        if not artifact:
            print(f"✗ Artifact not found: {artifact_id}")
            return

        print(f"Extracting facts from {artifact.path}...")

        extractor = KraangExtractor(self.store)
        facts = extractor.extract_facts(artifact)

        print(f"✓ Extracted {len(facts)} facts:")
        for fact in facts:
            self.store.add_fact(fact)
            print(f"  {fact.id}: {fact.statement[:80]}...")

    def cmd_extract_multi(
        self,
        artifact_id: str,
        max_passes: int = 7,
        budget: int = None,
        enable_diminishing_returns: bool = True
    ):
        """Extract facts using multi-pass strategy"""
        if not MULTI_PASS_AVAILABLE:
            print("✗ Multi-pass extraction not available. Make sure multi_pass_extraction.py is in the same directory.")
            return

        artifact = self.store.get_artifact(artifact_id)
        if not artifact:
            print(f"✗ Artifact not found: {artifact_id}")
            return

        print(f"Multi-pass extraction from {artifact.path}...")
        print(f"  Max passes: {max_passes}")
        if budget:
            print(f"  Budget: {budget} API calls")
        print(f"  Diminishing returns detection: {'enabled' if enable_diminishing_returns else 'disabled'}")
        print()

        # Create multi-pass extractor
        extractor = MultiPassExtractor(
            max_passes=max_passes,
            enable_diminishing_returns=enable_diminishing_returns,
            budget_api_calls=budget
        )

        # Run extraction
        results = extractor.run_passes(
            artifact_type=artifact.type,
            artifact_path=artifact.path,
            artifact_content=artifact.content
        )

        # Save facts to store
        print(f"\nSaving {len(results['facts'])} facts to store...")
        for fact_data in results['facts']:
            fact_id = self.store.get_next_id()

            # Convert ExtractedFact to Kraang Fact format
            fact = Fact(
                id=f"fact_{fact_id}",
                statement=fact_data['statement'],
                type=fact_data['type'],
                extracted_from=[{
                    'artifact_id': artifact.id,
                    'location': fact_data['location']
                }],
                confidence=fact_data['confidence']
            )
            self.store.add_fact(fact)

        print(f"✓ Extracted {len(results['facts'])} facts")
        print(f"  Passes run: {results['passes_run']}")
        print(f"  API calls: {results['api_calls']}")
        print(f"  Tokens used: {results['tokens_used']:,}")

        # Show per-pass breakdown
        print(f"\nPer-pass breakdown:")
        for pass_result in results['pass_results']:
            pass_type = pass_result['pass_type']
            extracted = pass_result['facts_extracted']
            new = pass_result['new_unique_facts']
            dupes = pass_result['facts_deduplicated']
            print(f"  {pass_type:20s}: {extracted:3d} raw -> {new:3d} new ({dupes:3d} duplicates)")

    def cmd_relate(self, fact_id_1: str = None, fact_id_2: str = None):
        """Analyze relationships between facts"""
        facts = self.store.get_facts()

        if len(facts) < 2:
            print("✗ Need at least 2 facts to analyze relationships")
            return

        extractor = KraangExtractor(self.store)

        # If specific facts specified, analyze just those
        if fact_id_1 and fact_id_2:
            f1 = self.store.get_fact(fact_id_1)
            f2 = self.store.get_fact(fact_id_2)
            if not f1 or not f2:
                print("✗ One or both facts not found")
                return

            print(f"Analyzing relationship between {fact_id_1} and {fact_id_2}...")
            rel = extractor.analyze_relationships(f1, f2)
            if rel:
                self.store.add_relationship(rel)
                print(f"✓ {rel.type.value}: {rel.reasoning}")
            else:
                print("  No significant relationship found")
            return

        # Otherwise, analyze all pairs
        print(f"Analyzing relationships between {len(facts)} facts...")
        count = 0
        for i, f1 in enumerate(facts):
            for f2 in facts[i+1:]:
                rel = extractor.analyze_relationships(f1, f2)
                if rel:
                    self.store.add_relationship(rel)
                    print(f"  {f1.id} <-> {f2.id}: {rel.type.value}")
                    count += 1

        print(f"✓ Found {count} relationships")

    def cmd_conflicts(self):
        """Show all contradicting facts"""
        relationships = self.store.get_relationships()
        contradictions = [r for r in relationships if r.type == RelationType.CONTRADICTS]

        if not contradictions:
            print("✓ No contradictions found")
            return

        print(f"Found {len(contradictions)} contradictions:\n")
        for rel in contradictions:
            f1 = self.store.get_fact(rel.fact_id_1)
            f2 = self.store.get_fact(rel.fact_id_2)
            print(f"CONTRADICTION (confidence: {rel.confidence:.2f})")
            print(f"  Fact 1 ({f1.id}): {f1.statement}")
            print(f"  Fact 2 ({f2.id}): {f2.statement}")
            print(f"  Reasoning: {rel.reasoning}")
            print()

    def cmd_impact(self, fact_id: str):
        """Show impact of changing a fact"""
        fact = self.store.get_fact(fact_id)
        if not fact:
            print(f"✗ Fact not found: {fact_id}")
            return

        print(f"Impact analysis for: {fact.statement}\n")

        # Show where this fact came from
        print("Source artifacts:")
        for ref in fact.extracted_from:
            artifact = self.store.get_artifact(ref['artifact_id'])
            print(f"  - {artifact.path} ({ref['location']})")

        # Show related facts
        relationships = self.store.get_relationships_for_fact(fact_id)
        if relationships:
            print(f"\nRelated facts ({len(relationships)}):")
            for rel in relationships:
                other_id = rel.fact_id_2 if rel.fact_id_1 == fact_id else rel.fact_id_1
                other_fact = self.store.get_fact(other_id)
                print(f"  [{rel.type.value}] {other_fact.statement}")
        else:
            print("\nNo related facts found")

    def cmd_list(self, what: str = "facts"):
        """List artifacts, facts, or relationships"""
        if what == "artifacts":
            artifacts = self.store.get_artifacts()
            print(f"Artifacts ({len(artifacts)}):")
            for a in artifacts:
                print(f"  {a.id}: {a.path} ({a.type})")
        elif what == "facts":
            facts = self.store.get_facts()
            print(f"Facts ({len(facts)}):")
            for f in facts:
                print(f"  {f.id}: {f.statement[:80]}...")
        elif what == "relationships":
            rels = self.store.get_relationships()
            print(f"Relationships ({len(rels)}):")
            for r in rels:
                print(f"  {r.fact_id_1} <-{r.type.value}-> {r.fact_id_2}")
        else:
            print(f"✗ Unknown list type: {what}")

    def cmd_completeness(self):
        """Analyze completeness of fact extraction"""
        artifacts = self.store.get_artifacts()
        facts = self.store.get_facts()
        relationships = self.store.get_relationships()

        print("=== Kraang Completeness Analysis ===\n")

        # Basic stats
        print(f"📊 Basic Statistics:")
        print(f"  Artifacts: {len(artifacts)}")
        print(f"  Facts: {len(facts)}")
        print(f"  Relationships: {len(relationships)}")
        print()

        # Facts per artifact
        print(f"📈 Facts per Artifact:")
        for artifact in artifacts:
            artifact_facts = [f for f in facts if any(ref['artifact_id'] == artifact.id for ref in f.extracted_from)]
            print(f"  {artifact.id} ({artifact.type}): {len(artifact_facts)} facts")
        print()

        # Fact types distribution
        fact_types = {}
        for fact in facts:
            fact_types[fact.type] = fact_types.get(fact.type, 0) + 1
        print(f"📋 Fact Types:")
        for ftype, count in sorted(fact_types.items()):
            print(f"  {ftype}: {count}")
        print()

        # Relationship density
        if len(facts) > 0:
            density = len(relationships) / len(facts)
            print(f"🔗 Relationship Density: {density:.2f}")
            print(f"  (relationships per fact, target: >0.5)")
            if density < 0.3:
                print(f"  ⚠️  Low density - many facts may be isolated")
            elif density < 0.5:
                print(f"  ⚠️  Moderate density - consider more relationship analysis")
            else:
                print(f"  ✓ Good density - facts are well connected")
            print()

        # Constraint coverage
        constraint_facts = [f for f in facts if f.type == "constraint"]
        impl_facts = [f for f in facts if f.type == "implementation"]
        if len(constraint_facts) > 0:
            coverage = len(impl_facts) / len(constraint_facts)
            print(f"🎯 Constraint Implementation Coverage: {coverage:.2f}")
            print(f"  Constraints: {len(constraint_facts)}")
            print(f"  Implementations: {len(impl_facts)}")
            print(f"  (target: >0.8)")
            if coverage < 0.5:
                print(f"  ⚠️  Low coverage - many constraints lack implementation facts")
            elif coverage < 0.8:
                print(f"  ⚠️  Moderate coverage - some gaps remain")
            else:
                print(f"  ✓ Good coverage")
            print()

        # Orphaned facts (no relationships)
        facts_with_rels = set()
        for rel in relationships:
            facts_with_rels.add(rel.fact_id_1)
            facts_with_rels.add(rel.fact_id_2)
        orphaned = [f for f in facts if f.id not in facts_with_rels]

        print(f"🔍 Orphaned Facts: {len(orphaned)}/{len(facts)}")
        if len(orphaned) > len(facts) * 0.5:
            print(f"  ⚠️  More than 50% of facts have no relationships")
            print(f"  → Run 'kraang relate' to analyze more relationships")
        elif len(orphaned) > 0:
            print(f"  Some facts isolated, consider analyzing relationships")
        else:
            print(f"  ✓ All facts are connected")
        print()

        # Completeness score (simple heuristic)
        score = 0
        max_score = 100

        # Has facts (40 points)
        if len(facts) > 10:
            score += 40
        elif len(facts) > 5:
            score += 20

        # Has relationships (30 points)
        if density >= 0.5:
            score += 30
        elif density >= 0.3:
            score += 15

        # Coverage (30 points)
        if len(constraint_facts) > 0:
            if coverage >= 0.8:
                score += 30
            elif coverage >= 0.5:
                score += 15

        print(f"📊 Completeness Score: {score}/{max_score}")
        if score >= 80:
            print(f"  ✓ Excellent - extraction appears comprehensive")
        elif score >= 60:
            print(f"  ✓ Good - core constraints captured")
        elif score >= 40:
            print(f"  ⚠️  Moderate - consider more extraction")
        else:
            print(f"  ⚠️  Low - needs more work")
        print()

        print("💡 Recommendations:")
        if len(artifacts) < 5:
            print("  • Add more artifacts to get broader coverage")
        if density < 0.5:
            print("  • Run 'kraang relate' to analyze more relationships")
        if len(constraint_facts) == 0:
            print("  • Extract from documentation to capture constraints")
        if coverage < 0.5 and len(constraint_facts) > 0:
            print("  • Extract from more code files to verify constraint implementation")
        if score >= 80:
            print("  • Extraction looks complete - ready for queries and impact analysis!")
        print("\n  • Try 'kraang validate-queries' for query-driven completeness testing")

    def cmd_validate_queries(self):
        """Run query-driven validation to test completeness"""
        try:
            from query_validator import QueryValidator, get_lotj_question_sets
        except ImportError:
            print("✗ Query validator module not found")
            print("  Make sure query_validator.py is in the same directory")
            return

        # Get question sets
        question_sets = get_lotj_question_sets()

        # Create validator
        validator = QueryValidator(self.store, KraangExtractor(self.store))

        # Run validation
        print("Running query-driven completeness validation...")
        print(f"Testing {sum(len(qs.questions) for qs in question_sets)} questions")
        print("This may take several minutes...\n")

        score = validator.validate_all_questions(question_sets)

    def cmd_coverage(self, artifact_id: str = None, show_heatmap: bool = False, show_gaps: bool = False):
        """Analyze code coverage by facts"""
        if not COVERAGE_AVAILABLE:
            print("✗ Coverage module not available. Make sure coverage.py is in the same directory.")
            return

        analyzer = CoverageAnalyzer(self.store)

        if show_gaps:
            # Show detailed gap analysis
            report = analyzer.analyze_all()
            analyzer.print_gaps(report)
        elif artifact_id:
            # Show detail for specific artifact
            analyzer.print_artifact_detail(artifact_id)
            if show_heatmap:
                print()
                artifact = self.store.get_artifact(artifact_id)
                if artifact:
                    coverage = analyzer.analyze_artifact(artifact)
                    print(analyzer.generate_heatmap(coverage))
        else:
            # Show overall summary
            report = analyzer.analyze_all()
            analyzer.print_summary(report)

    def run(self, args: List[str]):
        """Run CLI command"""
        if len(args) < 1:
            self.print_help()
            return

        command = args[0]

        try:
            if command == "init":
                self.cmd_init()
            elif command == "add":
                if len(args) < 2:
                    print("Usage: kraang add <path> [type]")
                    return
                artifact_type = args[2] if len(args) > 2 else None
                self.cmd_add(args[1], artifact_type)
            elif command == "extract":
                if len(args) < 2:
                    print("Usage: kraang extract <artifact_id>")
                    return
                self.cmd_extract(args[1])
            elif command == "extract-multi":
                if len(args) < 2:
                    print("Usage: kraang extract-multi <artifact_id> [--max-passes N] [--budget N] [--no-diminishing-returns]")
                    return

                artifact_id = args[1]
                max_passes = 7
                budget = None
                enable_dr = True

                # Parse optional args
                i = 2
                while i < len(args):
                    if args[i] == "--max-passes" and i + 1 < len(args):
                        max_passes = int(args[i + 1])
                        i += 2
                    elif args[i] == "--budget" and i + 1 < len(args):
                        budget = int(args[i + 1])
                        i += 2
                    elif args[i] == "--no-diminishing-returns":
                        enable_dr = False
                        i += 1
                    else:
                        print(f"Unknown option: {args[i]}")
                        return

                self.cmd_extract_multi(artifact_id, max_passes, budget, enable_dr)
            elif command == "relate":
                if len(args) == 3:
                    self.cmd_relate(args[1], args[2])
                else:
                    self.cmd_relate()
            elif command == "conflicts":
                self.cmd_conflicts()
            elif command == "impact":
                if len(args) < 2:
                    print("Usage: kraang impact <fact_id>")
                    return
                self.cmd_impact(args[1])
            elif command == "list":
                what = args[1] if len(args) > 1 else "facts"
                self.cmd_list(what)
            elif command == "completeness":
                self.cmd_completeness()
            elif command == "validate-queries":
                self.cmd_validate_queries()
            elif command == "coverage":
                # Parse flags
                show_heatmap = "--heatmap" in args
                show_gaps = "--gaps" in args
                artifact_id = None
                for arg in args[1:]:
                    if not arg.startswith("--"):
                        artifact_id = arg
                        break
                self.cmd_coverage(artifact_id, show_heatmap, show_gaps)
            else:
                print(f"✗ Unknown command: {command}")
                self.print_help()
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()

    def print_help(self):
        print("""Kraang - Constraint Rationalization Engine

Usage: kraang <command> [args]

Commands:
  init                        Initialize a new Kraang project
  add <path> [type]           Add an artifact (auto-detects type)
  extract <artifact_id>       Extract facts from an artifact (single-pass)
  extract-multi <artifact_id> [options]
                              Extract facts using multi-pass strategy
  relate [fact1] [fact2]      Analyze relationships (all or specific pair)
  conflicts                   Show all contradicting facts
  impact <fact_id>            Show impact of changing a fact
  list [artifacts|facts|relationships]  List items
  completeness                Analyze extraction completeness
  validate-queries            Run query-driven completeness validation
  coverage [artifact_id] [--heatmap] [--gaps]
                              Analyze code coverage by facts

Multi-Pass Extraction Options:
  kraang extract-multi <artifact_id>
                              Run all specialized passes with defaults
  kraang extract-multi <artifact_id> --max-passes N
                              Limit number of passes to N (default: 7)
  kraang extract-multi <artifact_id> --budget N
                              Limit API calls to N (default: unlimited)
  kraang extract-multi <artifact_id> --no-diminishing-returns
                              Run all passes without early stopping

Multi-pass extraction uses specialized prompts to discover:
  - Memory management constraints
  - Concurrency requirements
  - Security policies
  - Error handling patterns
  - Performance constraints
  - Testing requirements
Typically finds 50-100% more facts than single-pass extraction.

Coverage Examples:
  kraang coverage                    Show overall coverage summary
  kraang coverage artifact_1         Show detail for specific artifact
  kraang coverage artifact_1 --heatmap  Show heat map visualization
  kraang coverage --gaps             Show files needing attention

Examples:
  kraang init
  kraang add README.md doc
  kraang add src/auth.c code
  kraang extract artifact_1          # Single-pass (fast)
  kraang extract-multi artifact_1    # Multi-pass (comprehensive)
  kraang relate
  kraang conflicts
  kraang impact fact_1
  kraang completeness
  kraang coverage
""")


if __name__ == "__main__":
    cli = KraangCLI()
    cli.run(sys.argv[1:])
