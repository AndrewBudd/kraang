#!/usr/bin/env python3
"""
Comprehensive Test Suite for Kraang System

Tests all major components:
- Core data structures (Artifact, Fact, Relationship)
- Storage layer (KraangStore)
- Extraction and LLM integration (KraangExtractor)
- Multi-pass extraction
- Coverage analysis
- Query validation
- Smart pairing algorithm
- CLI commands
- Data flow between components
- Integration with real data

Usage:
    python test_kraang_complete.py [--verbose] [--skip-llm] [--real-data]

Options:
    --verbose       Show detailed test output
    --skip-llm      Skip tests requiring LLM API calls
    --real-data     Test with existing .kraang data (requires data)
"""

import sys
import json
import os
import shutil
import tempfile
import argparse
from pathlib import Path
from typing import List, Dict, Any
from unittest.mock import Mock, patch
import traceback

# Import all Kraang modules
from kraang import (
    KraangStore, KraangExtractor, KraangCLI,
    Artifact, Fact, Relationship, RelationType, ArtifactReference
)
from coverage import CoverageAnalyzer, LocationParser, CoverageLevel
from multi_pass_extraction import (
    MultiPassExtractor, FactDeduplicator, ExtractedFact,
    PassType, ExtractionPromptLibrary
)
from smart_pairing import (
    extract_domains, extract_code_entities,
    smart_pairing_algorithm, calculate_domain_similarity
)
from query_validator import (
    QueryValidator, QuestionSet, QuestionType,
    classify_question, get_lotj_question_sets
)


class TestResults:
    """Track test results"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.errors = []

    def record_pass(self, test_name: str):
        self.passed += 1
        print(f"  ✓ {test_name}")

    def record_fail(self, test_name: str, error: str):
        self.failed += 1
        self.errors.append((test_name, error))
        print(f"  ✗ {test_name}: {error}")

    def record_skip(self, test_name: str, reason: str):
        self.skipped += 1
        print(f"  ⊘ {test_name}: {reason}")

    def summary(self):
        total = self.passed + self.failed + self.skipped
        print(f"\n{'='*70}")
        print(f"TEST SUMMARY: {self.passed}/{total} passed, {self.failed} failed, {self.skipped} skipped")
        print(f"{'='*70}")

        if self.errors:
            print(f"\nFailed Tests:")
            for test_name, error in self.errors:
                print(f"  • {test_name}: {error}")

        return self.failed == 0


class TestSuite:
    """Main test suite"""

    def __init__(self, verbose=False, skip_llm=False, use_real_data=False):
        self.verbose = verbose
        self.skip_llm = skip_llm
        self.use_real_data = use_real_data
        self.results = TestResults()
        self.temp_dir = None

    def setup(self):
        """Setup test environment"""
        if not self.use_real_data:
            # Create temporary directory for tests
            self.temp_dir = tempfile.mkdtemp(prefix="kraang_test_")
            os.chdir(self.temp_dir)
            if self.verbose:
                print(f"Test directory: {self.temp_dir}")
        else:
            if self.verbose:
                print(f"Using real data in current directory")

    def teardown(self):
        """Cleanup test environment"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            if self.verbose:
                print(f"Cleaned up: {self.temp_dir}")

    def log(self, message: str):
        """Log verbose output"""
        if self.verbose:
            print(f"    {message}")

    # ========================================================================
    # CORE DATA STRUCTURE TESTS
    # ========================================================================

    def test_artifact_creation(self):
        """Test Artifact creation and serialization"""
        try:
            artifact = Artifact(
                id="test_1",
                type="code",
                path="/test.py",
                content="print('hello')"
            )

            assert artifact.id == "test_1"
            assert artifact.type == "code"

            # Test to_dict
            d = artifact.to_dict()
            assert d["id"] == "test_1"

            # Test from_dict
            artifact2 = Artifact.from_dict(d)
            assert artifact2.id == artifact.id
            assert artifact2.content == artifact.content

            self.results.record_pass("Artifact creation and serialization")
        except Exception as e:
            self.results.record_fail("Artifact creation and serialization", str(e))

    def test_fact_creation(self):
        """Test Fact creation and serialization"""
        try:
            ref = ArtifactReference(artifact_id="test_1", location="line 10")
            fact = Fact(
                id="fact_1",
                statement="Code must use Python 3.8+",
                type="constraint",
                extracted_from=[ref.to_dict()],
                confidence=0.95
            )

            assert fact.id == "fact_1"
            assert fact.confidence == 0.95

            # Test to_dict
            d = fact.to_dict()
            assert d["statement"] == fact.statement

            # Test from_dict
            fact2 = Fact.from_dict(d)
            assert fact2.id == fact.id

            self.results.record_pass("Fact creation and serialization")
        except Exception as e:
            self.results.record_fail("Fact creation and serialization", str(e))

    def test_relationship_creation(self):
        """Test Relationship creation and serialization"""
        try:
            rel = Relationship(
                fact_id_1="fact_1",
                fact_id_2="fact_2",
                type=RelationType.SUPPORTS,
                confidence=0.8,
                reasoning="Both are memory constraints"
            )

            assert rel.type == RelationType.SUPPORTS

            # Test to_dict
            d = rel.to_dict()
            assert d["type"] == "supports"

            # Test from_dict
            rel2 = Relationship.from_dict(d)
            assert rel2.type == RelationType.SUPPORTS

            self.results.record_pass("Relationship creation and serialization")
        except Exception as e:
            self.results.record_fail("Relationship creation and serialization", str(e))

    # ========================================================================
    # STORAGE LAYER TESTS
    # ========================================================================

    def test_store_init(self):
        """Test KraangStore initialization"""
        try:
            store = KraangStore(".kraang_test")
            store.init()

            assert Path(".kraang_test").exists()
            assert Path(".kraang_test/artifacts.json").exists()
            assert Path(".kraang_test/facts.json").exists()
            assert Path(".kraang_test/relationships.json").exists()

            self.results.record_pass("Store initialization")
        except Exception as e:
            self.results.record_fail("Store initialization", str(e))

    def test_store_artifacts(self):
        """Test artifact storage and retrieval"""
        try:
            store = KraangStore(".kraang_test")
            store.init()

            artifact = Artifact(
                id="test_1",
                type="code",
                path="/test.py",
                content="test"
            )

            store.add_artifact(artifact)
            artifacts = store.get_artifacts()

            assert len(artifacts) == 1
            assert artifacts[0].id == "test_1"

            retrieved = store.get_artifact("test_1")
            assert retrieved is not None
            assert retrieved.path == "/test.py"

            self.results.record_pass("Artifact storage and retrieval")
        except Exception as e:
            self.results.record_fail("Artifact storage and retrieval", str(e))

    def test_store_facts(self):
        """Test fact storage and retrieval"""
        try:
            store = KraangStore(".kraang_test")
            store.init()

            ref = ArtifactReference(artifact_id="test_1", location="line 10")
            fact = Fact(
                id="fact_1",
                statement="Test constraint",
                type="constraint",
                extracted_from=[ref.to_dict()],
                confidence=0.9
            )

            store.add_fact(fact)
            facts = store.get_facts()

            assert len(facts) == 1
            assert facts[0].statement == "Test constraint"

            retrieved = store.get_fact("fact_1")
            assert retrieved is not None

            self.results.record_pass("Fact storage and retrieval")
        except Exception as e:
            self.results.record_fail("Fact storage and retrieval", str(e))

    def test_store_relationships(self):
        """Test relationship storage and retrieval"""
        try:
            store = KraangStore(".kraang_test")
            store.init()

            rel = Relationship(
                fact_id_1="fact_1",
                fact_id_2="fact_2",
                type=RelationType.CONTRADICTS,
                confidence=0.85,
                reasoning="Test"
            )

            store.add_relationship(rel)
            rels = store.get_relationships()

            assert len(rels) == 1
            assert rels[0].type == RelationType.CONTRADICTS

            fact_rels = store.get_relationships_for_fact("fact_1")
            assert len(fact_rels) == 1

            self.results.record_pass("Relationship storage and retrieval")
        except Exception as e:
            self.results.record_fail("Relationship storage and retrieval", str(e))

    def test_store_id_generation(self):
        """Test ID generation"""
        try:
            store = KraangStore(".kraang_test")
            store.init()

            id1 = store.get_next_id()
            id2 = store.get_next_id()
            id3 = store.get_next_id()

            assert id1 == "1"
            assert id2 == "2"
            assert id3 == "3"

            self.results.record_pass("ID generation")
        except Exception as e:
            self.results.record_fail("ID generation", str(e))

    # ========================================================================
    # COVERAGE ANALYZER TESTS
    # ========================================================================

    def test_location_parser(self):
        """Test location parsing"""
        try:
            parser = LocationParser()

            # Test line range
            lines = parser.parse_location("Lines 10-15")
            assert lines == set(range(10, 16))

            # Test single line
            lines = parser.parse_location("Line 42")
            assert lines == {42}

            # Test with section
            lines = parser.parse_location("Lines 100-120, Section: Memory")
            assert lines == set(range(100, 121))

            # Test function reference (no line numbers)
            lines = parser.parse_location("function do_command")
            assert lines == set()

            self.results.record_pass("Location parser")
        except Exception as e:
            self.results.record_fail("Location parser", str(e))

    def test_coverage_analyzer(self):
        """Test coverage analyzer with mock data"""
        try:
            store = KraangStore(".kraang_test")
            store.init()

            # Add artifact
            artifact = Artifact(
                id="test_1",
                type="code",
                path="/test.c",
                content="\n".join([f"line {i}" for i in range(1, 101)])
            )
            store.add_artifact(artifact)

            # Add facts
            ref = ArtifactReference(artifact_id="test_1", location="Lines 10-15")
            fact = Fact(
                id="fact_1",
                statement="Test",
                type="constraint",
                extracted_from=[ref.to_dict()],
                confidence=0.9
            )
            store.add_fact(fact)

            # Analyze coverage
            analyzer = CoverageAnalyzer(store)
            coverage = analyzer.analyze_artifact(artifact)

            assert coverage.total_lines == 100
            assert len(coverage.covered_lines) == 6  # Lines 10-15
            assert coverage.coverage_percentage() == 6.0

            self.results.record_pass("Coverage analyzer")
        except Exception as e:
            self.results.record_fail("Coverage analyzer", str(e))

    # ========================================================================
    # MULTI-PASS EXTRACTION TESTS
    # ========================================================================

    def test_fact_deduplicator(self):
        """Test fact deduplication"""
        try:
            fact1 = ExtractedFact(
                statement="Memory allocation MUST use CREATE macro",
                type="constraint",
                location="lines 10-15",
                confidence=0.85,
                pass_type=PassType.GENERAL
            )

            fact2 = ExtractedFact(
                statement="Memory allocation must use CREATE() macro, never malloc()",
                type="constraint",
                location="comment block",
                confidence=0.95,
                pass_type=PassType.MEMORY
            )

            fact3 = ExtractedFact(
                statement="Database connections use pooling",
                type="implementation",
                location="lines 50-60",
                confidence=0.90,
                pass_type=PassType.GENERAL
            )

            deduplicator = FactDeduplicator()

            # Test similarity
            similarity = deduplicator.compute_similarity(fact1, fact2)
            self.log(f"Similarity (fact1, fact2): {similarity:.2f}")
            assert similarity > 0.5  # Should be similar

            # Test duplicate detection
            result = deduplicator.find_duplicate(fact2, [fact1])
            assert result.is_duplicate

            # Test non-duplicates
            result = deduplicator.find_duplicate(fact3, [fact1])
            assert not result.is_duplicate

            # Test merging
            merged = deduplicator.merge_facts(fact1, fact2)
            assert merged.confidence > max(fact1.confidence, fact2.confidence)

            self.results.record_pass("Fact deduplicator")
        except Exception as e:
            self.results.record_fail("Fact deduplicator", str(e))

    def test_extraction_prompt_library(self):
        """Test extraction prompt library"""
        try:
            library = ExtractionPromptLibrary()

            # Get all passes
            passes = library.get_all_passes()
            assert len(passes) > 0

            # Check pass priorities
            for pass_config in passes:
                assert hasattr(pass_config, 'pass_type')
                assert hasattr(pass_config, 'priority')
                assert hasattr(pass_config, 'prompt_template')

            # Verify they're sorted by priority
            priorities = [p.priority for p in passes]
            assert priorities == sorted(priorities)

            self.results.record_pass("Extraction prompt library")
        except Exception as e:
            self.results.record_fail("Extraction prompt library", str(e))

    # ========================================================================
    # SMART PAIRING TESTS
    # ========================================================================

    def test_domain_extraction(self):
        """Test domain extraction"""
        try:
            statement1 = "Memory allocation MUST use CREATE macro"
            domains1 = extract_domains(statement1)
            assert "memory_management" in domains1

            statement2 = "Docker Compose must be used for local development"
            domains2 = extract_domains(statement2)
            assert "docker_dev" in domains2

            self.results.record_pass("Domain extraction")
        except Exception as e:
            self.results.record_fail("Domain extraction", str(e))

    def test_code_entity_extraction(self):
        """Test code entity extraction"""
        try:
            statement = "The do_command() function uses CREATE macro for allocation"
            entities = extract_code_entities(statement)

            assert "do_command" in entities  # Function name
            assert "CREATE" in entities  # Macro

            self.results.record_pass("Code entity extraction")
        except Exception as e:
            self.results.record_fail("Code entity extraction", str(e))

    def test_pair_scoring(self):
        """Test pair scoring using domain similarity"""
        try:
            # Create mock facts
            fact1 = {
                "id": "fact_1",
                "statement": "Memory allocation uses CREATE macro",
                "type": "constraint",
                "extracted_from": [{"artifact_id": "artifact_1"}],
                "confidence": 0.9
            }

            fact2 = {
                "id": "fact_2",
                "statement": "Memory deallocation uses DESTROY macro",
                "type": "constraint",
                "extracted_from": [{"artifact_id": "artifact_1"}],
                "confidence": 0.9
            }

            fact3 = {
                "id": "fact_3",
                "statement": "Docker Compose is required for local development",
                "type": "requirement",
                "extracted_from": [{"artifact_id": "artifact_2"}],
                "confidence": 0.9
            }

            # Score related facts (both about memory management)
            score1 = calculate_domain_similarity(fact1, fact2)
            self.log(f"Domain similarity (related): {score1:.2f}")
            assert score1 > 0

            # Score unrelated facts
            score2 = calculate_domain_similarity(fact1, fact3)
            self.log(f"Domain similarity (unrelated): {score2:.2f}")
            assert score1 > score2  # Related should score higher

            self.results.record_pass("Pair scoring")
        except Exception as e:
            self.results.record_fail("Pair scoring", str(e))

    # ========================================================================
    # QUERY VALIDATOR TESTS
    # ========================================================================

    def test_question_classification(self):
        """Test question classification"""
        try:
            q1 = "How do I set up local development?"
            assert classify_question(q1) == QuestionType.ONBOARDING

            q2 = "Can I use malloc() directly?"
            assert classify_question(q2) == QuestionType.CONSTRAINT

            q3 = "What function handles user commands?"
            assert classify_question(q3) == QuestionType.IMPLEMENTATION

            q4 = "Why is the program crashing?"
            assert classify_question(q4) == QuestionType.DEBUGGING

            self.results.record_pass("Question classification")
        except Exception as e:
            self.results.record_fail("Question classification", str(e))

    def test_question_sets(self):
        """Test question set structure"""
        try:
            question_sets = get_lotj_question_sets()

            assert len(question_sets) > 0

            for qs in question_sets:
                assert isinstance(qs, QuestionSet)
                assert len(qs.questions) > 0
                assert isinstance(qs.category, QuestionType)
                assert qs.priority in [1, 2, 3]

            self.results.record_pass("Question sets")
        except Exception as e:
            self.results.record_fail("Question sets", str(e))

    # ========================================================================
    # CLI COMMAND TESTS
    # ========================================================================

    def test_cli_init(self):
        """Test CLI init command"""
        try:
            cli = KraangCLI()
            cli.cmd_init()

            assert Path(".kraang").exists()
            assert Path(".kraang/artifacts.json").exists()

            self.results.record_pass("CLI init command")
        except Exception as e:
            self.results.record_fail("CLI init command", str(e))

    def test_cli_add(self):
        """Test CLI add command"""
        try:
            cli = KraangCLI()
            cli.cmd_init()

            # Create test file
            test_file = Path("test_code.py")
            test_file.write_text("# Test code\nprint('hello')")

            cli.cmd_add(str(test_file), "code")

            artifacts = cli.store.get_artifacts()
            assert len(artifacts) == 1
            assert artifacts[0].type == "code"

            self.results.record_pass("CLI add command")
        except Exception as e:
            self.results.record_fail("CLI add command", str(e))

    def test_cli_list(self):
        """Test CLI list commands"""
        try:
            cli = KraangCLI()
            cli.cmd_init()

            # Add test data
            test_file = Path("test.py")
            test_file.write_text("print('test')")
            cli.cmd_add(str(test_file))

            # List artifacts
            cli.cmd_list("artifacts")

            # List facts (should be empty)
            cli.cmd_list("facts")

            # List relationships (should be empty)
            cli.cmd_list("relationships")

            self.results.record_pass("CLI list commands")
        except Exception as e:
            self.results.record_fail("CLI list commands", str(e))

    # ========================================================================
    # DATA FLOW INTEGRATION TESTS
    # ========================================================================

    def test_artifact_to_fact_flow(self):
        """Test data flow from artifact to fact"""
        try:
            store = KraangStore(".kraang_test")
            store.init()

            # Add artifact
            artifact = Artifact(
                id="test_1",
                type="code",
                path="/test.py",
                content="# Constraint: Must use Python 3.8+"
            )
            store.add_artifact(artifact)

            # Add fact referencing artifact
            ref = ArtifactReference(artifact_id="test_1", location="line 1")
            fact = Fact(
                id="fact_1",
                statement="Must use Python 3.8+",
                type="constraint",
                extracted_from=[ref.to_dict()],
                confidence=0.9
            )
            store.add_fact(fact)

            # Verify linkage
            retrieved_artifact = store.get_artifact(fact.extracted_from[0]["artifact_id"])
            assert retrieved_artifact is not None
            assert retrieved_artifact.id == "test_1"

            self.results.record_pass("Artifact to fact flow")
        except Exception as e:
            self.results.record_fail("Artifact to fact flow", str(e))

    def test_fact_to_relationship_flow(self):
        """Test data flow from facts to relationships"""
        try:
            store = KraangStore(".kraang_test")
            store.init()

            # Add facts
            ref = ArtifactReference(artifact_id="test_1", location="line 1")
            fact1 = Fact(
                id="fact_1",
                statement="Use CREATE for allocation",
                type="constraint",
                extracted_from=[ref.to_dict()],
                confidence=0.9
            )
            fact2 = Fact(
                id="fact_2",
                statement="Use DESTROY for deallocation",
                type="constraint",
                extracted_from=[ref.to_dict()],
                confidence=0.9
            )
            store.add_fact(fact1)
            store.add_fact(fact2)

            # Add relationship
            rel = Relationship(
                fact_id_1="fact_1",
                fact_id_2="fact_2",
                type=RelationType.SUPPORTS,
                confidence=0.85,
                reasoning="Both are memory management constraints"
            )
            store.add_relationship(rel)

            # Verify linkage
            fact1_rels = store.get_relationships_for_fact("fact_1")
            assert len(fact1_rels) == 1

            fact2_rels = store.get_relationships_for_fact("fact_2")
            assert len(fact2_rels) == 1

            self.results.record_pass("Fact to relationship flow")
        except Exception as e:
            self.results.record_fail("Fact to relationship flow", str(e))

    def test_coverage_integration(self):
        """Test coverage analysis integration"""
        try:
            store = KraangStore(".kraang_test")
            store.init()

            # Add artifact with content
            content = "\n".join([f"// Line {i}" for i in range(1, 51)])
            artifact = Artifact(
                id="test_1",
                type="code",
                path="/test.c",
                content=content
            )
            store.add_artifact(artifact)

            # Add facts covering different parts
            for i, (start, end) in enumerate([(10, 15), (20, 25), (30, 35)]):
                ref = ArtifactReference(artifact_id="test_1", location=f"Lines {start}-{end}")
                fact = Fact(
                    id=f"fact_{i+1}",
                    statement=f"Constraint {i+1}",
                    type="constraint",
                    extracted_from=[ref.to_dict()],
                    confidence=0.9
                )
                store.add_fact(fact)

            # Analyze coverage
            analyzer = CoverageAnalyzer(store)
            coverage = analyzer.analyze_artifact(artifact)

            # Verify coverage
            assert coverage.total_lines == 50
            assert len(coverage.covered_lines) == 18  # 6+6+6 lines
            assert coverage.coverage_percentage() == 36.0
            assert coverage.total_facts == 3

            self.results.record_pass("Coverage integration")
        except Exception as e:
            self.results.record_fail("Coverage integration", str(e))

    # ========================================================================
    # REAL DATA TESTS (if available)
    # ========================================================================

    def test_real_data_load(self):
        """Test loading real .kraang data"""
        if not self.use_real_data:
            self.results.record_skip("Real data load", "Real data not requested")
            return

        try:
            kraang_dir = Path(".kraang")
            if not kraang_dir.exists():
                self.results.record_skip("Real data load", ".kraang directory not found")
                return

            store = KraangStore()

            artifacts = store.get_artifacts()
            facts = store.get_facts()
            relationships = store.get_relationships()

            self.log(f"Loaded {len(artifacts)} artifacts")
            self.log(f"Loaded {len(facts)} facts")
            self.log(f"Loaded {len(relationships)} relationships")

            assert len(artifacts) > 0, "No artifacts found"
            assert len(facts) > 0, "No facts found"

            self.results.record_pass("Real data load")
        except Exception as e:
            self.results.record_fail("Real data load", str(e))

    def test_real_data_coverage(self):
        """Test coverage analysis on real data"""
        if not self.use_real_data:
            self.results.record_skip("Real data coverage", "Real data not requested")
            return

        try:
            kraang_dir = Path(".kraang")
            if not kraang_dir.exists():
                self.results.record_skip("Real data coverage", ".kraang directory not found")
                return

            store = KraangStore()
            analyzer = CoverageAnalyzer(store)

            report = analyzer.analyze_all()

            self.log(f"Overall coverage: {report.overall_percentage():.1f}%")
            self.log(f"Files: {len(report.file_coverages)}")

            assert report.overall_percentage() >= 0
            assert len(report.file_coverages) > 0

            self.results.record_pass("Real data coverage")
        except Exception as e:
            self.results.record_fail("Real data coverage", str(e))

    def test_real_data_smart_pairing(self):
        """Test smart pairing on real data"""
        if not self.use_real_data:
            self.results.record_skip("Real data smart pairing", "Real data not requested")
            return

        try:
            kraang_dir = Path(".kraang")
            if not kraang_dir.exists():
                self.results.record_skip("Real data smart pairing", ".kraang directory not found")
                return

            # Check if candidate_pairs.json exists
            pairs_file = Path(".kraang/candidate_pairs.json")
            if not pairs_file.exists():
                self.results.record_skip("Real data smart pairing", "candidate_pairs.json not found")
                return

            with open(pairs_file) as f:
                data = json.load(f)

            self.log(f"Total pairs: {data['total_pairs']}")
            self.log(f"Candidate pairs: {len(data['candidate_pairs'])}")

            assert data['total_pairs'] > 0
            assert len(data['candidate_pairs']) > 0

            self.results.record_pass("Real data smart pairing")
        except Exception as e:
            self.results.record_fail("Real data smart pairing", str(e))

    # ========================================================================
    # LLM INTEGRATION TESTS (optional)
    # ========================================================================

    def test_llm_extraction(self):
        """Test LLM fact extraction (requires API key)"""
        if self.skip_llm:
            self.results.record_skip("LLM extraction", "LLM tests disabled")
            return

        if not os.getenv("ANTHROPIC_API_KEY"):
            self.results.record_skip("LLM extraction", "No API key")
            return

        try:
            store = KraangStore(".kraang_test")
            store.init()

            # Create simple test artifact
            artifact = Artifact(
                id="test_1",
                type="code",
                path="/test.c",
                content="""
/* Memory Management
 * All allocations MUST use CREATE() macro
 * All deallocations MUST use DESTROY() macro
 */
#define CREATE(type) pool_allocate(sizeof(type))
#define DESTROY(ptr) pool_deallocate(ptr)
"""
            )
            store.add_artifact(artifact)

            # Extract facts
            extractor = KraangExtractor(store)
            facts = extractor.extract_facts(artifact)

            self.log(f"Extracted {len(facts)} facts")
            assert len(facts) > 0

            # Verify facts have required fields
            for fact in facts:
                assert fact.statement
                assert fact.type
                assert fact.extracted_from

            self.results.record_pass("LLM extraction")
        except Exception as e:
            self.results.record_fail("LLM extraction", str(e))

    # ========================================================================
    # RUN ALL TESTS
    # ========================================================================

    def run_all(self):
        """Run all tests"""
        print(f"{'='*70}")
        print(f"KRAANG COMPREHENSIVE TEST SUITE")
        print(f"{'='*70}")
        print(f"Verbose: {self.verbose}")
        print(f"Skip LLM: {self.skip_llm}")
        print(f"Real Data: {self.use_real_data}")
        print()

        test_groups = [
            ("Core Data Structures", [
                self.test_artifact_creation,
                self.test_fact_creation,
                self.test_relationship_creation,
            ]),
            ("Storage Layer", [
                self.test_store_init,
                self.test_store_artifacts,
                self.test_store_facts,
                self.test_store_relationships,
                self.test_store_id_generation,
            ]),
            ("Coverage Analyzer", [
                self.test_location_parser,
                self.test_coverage_analyzer,
            ]),
            ("Multi-Pass Extraction", [
                self.test_fact_deduplicator,
                self.test_extraction_prompt_library,
            ]),
            ("Smart Pairing", [
                self.test_domain_extraction,
                self.test_code_entity_extraction,
                self.test_pair_scoring,
            ]),
            ("Query Validator", [
                self.test_question_classification,
                self.test_question_sets,
            ]),
            ("CLI Commands", [
                self.test_cli_init,
                self.test_cli_add,
                self.test_cli_list,
            ]),
            ("Data Flow Integration", [
                self.test_artifact_to_fact_flow,
                self.test_fact_to_relationship_flow,
                self.test_coverage_integration,
            ]),
            ("Real Data Tests", [
                self.test_real_data_load,
                self.test_real_data_coverage,
                self.test_real_data_smart_pairing,
            ]),
            ("LLM Integration", [
                self.test_llm_extraction,
            ]),
        ]

        for group_name, tests in test_groups:
            print(f"\n{group_name}:")
            for test in tests:
                try:
                    test()
                except Exception as e:
                    self.results.record_fail(test.__name__, f"Unexpected error: {str(e)}")
                    if self.verbose:
                        traceback.print_exc()

        return self.results.summary()


def main():
    parser = argparse.ArgumentParser(description="Comprehensive Kraang test suite")
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")
    parser.add_argument("--skip-llm", action="store_true", help="Skip LLM tests")
    parser.add_argument("--real-data", action="store_true", help="Test with real .kraang data")
    args = parser.parse_args()

    suite = TestSuite(
        verbose=args.verbose,
        skip_llm=args.skip_llm,
        use_real_data=args.real_data
    )

    suite.setup()

    try:
        success = suite.run_all()
        return 0 if success else 1
    finally:
        suite.teardown()


if __name__ == "__main__":
    sys.exit(main())
