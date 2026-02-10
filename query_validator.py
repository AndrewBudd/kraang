#!/usr/bin/env python3
"""
Query-Driven Validation System for Kraang

Tests fact completeness by attempting to answer typical developer questions.
"""

import json
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Set
from enum import Enum
from pathlib import Path

# Import from main kraang module
from kraang import Fact, Relationship, KraangStore, KraangExtractor


class QuestionType(Enum):
    """Taxonomy of developer questions."""
    ONBOARDING = "onboarding"
    CONSTRAINT = "constraint"
    IMPLEMENTATION = "implementation"
    DEBUGGING = "debugging"
    UNKNOWN = "unknown"


@dataclass
class ValidationResult:
    """Result of validating a single question."""
    question: str
    answer: str
    confidence: float
    llm_confidence: float
    secondary_confidence: float
    supporting_facts: List[Dict]  # Fact dicts, not objects (for JSON serialization)
    missing_categories: List[str]
    gap_details: Optional[Dict]  # GapAnalysis as dict

    def to_dict(self):
        """Convert to dict for JSON serialization."""
        return asdict(self)


@dataclass
class GapAnalysis:
    """Analysis of missing facts for a question."""
    question_type: str
    expected_fact_types: List[str]
    available_fact_types: List[str]
    missing_fact_types: List[str]
    missing_categories: List[str]
    recommendations: List[str]

    def to_dict(self):
        """Convert to dict for JSON serialization."""
        return asdict(self)


@dataclass
class CompletenessScore:
    """Overall completeness score across all questions."""
    total_questions: int
    high_confidence_count: int
    high_confidence_pct: float
    medium_confidence_count: int
    medium_confidence_pct: float
    low_confidence_count: int
    by_question_type: Dict[str, float]
    weighted_score: float
    overall_grade: str

    def to_dict(self):
        """Convert to dict for JSON serialization."""
        return asdict(self)


@dataclass
class QuestionSet:
    """A set of validation questions."""
    questions: List[str]
    category: QuestionType
    priority: int  # 1=critical, 2=important, 3=nice-to-have

    def to_dict(self):
        """Convert to dict for JSON serialization."""
        d = asdict(self)
        d['category'] = self.category.value
        return d


# Helper Functions

def classify_question(question: str) -> QuestionType:
    """Classify question into taxonomy categories."""
    question_lower = question.lower()

    if any(phrase in question_lower for phrase in ["how do i", "how to", "how can i"]):
        return QuestionType.ONBOARDING
    elif any(phrase in question_lower for phrase in ["can i", "must i", "should i", "is it required"]):
        return QuestionType.CONSTRAINT
    elif any(phrase in question_lower for phrase in ["where is", "what is", "how does"]):
        return QuestionType.IMPLEMENTATION
    elif any(phrase in question_lower for phrase in ["why did", "why is", "what causes", "why can't"]):
        return QuestionType.DEBUGGING
    else:
        return QuestionType.UNKNOWN


def get_expected_fact_types(question_type: QuestionType) -> Set[str]:
    """Get expected fact types for each question category."""
    mapping = {
        QuestionType.ONBOARDING: {"requirement", "implementation"},
        QuestionType.CONSTRAINT: {"constraint", "design"},
        QuestionType.IMPLEMENTATION: {"implementation", "design"},
        QuestionType.DEBUGGING: {"constraint", "implementation"},
    }
    return mapping.get(question_type, {"implementation"})


def map_to_categories(missing_fact_types: Set[str], missing_info: List[str]) -> List[str]:
    """Map missing fact types and LLM-reported missing info to human-readable categories."""
    categories = set()

    # Add missing fact types
    for fact_type in missing_fact_types:
        categories.add(f"{fact_type}_facts")

    # Add LLM-reported missing info
    for info in missing_info:
        categories.add(info)

    return sorted(list(categories))


def generate_extraction_recommendations(question_type: QuestionType,
                                        missing_categories: List[str]) -> List[str]:
    """Generate recommendations for what to extract based on gaps."""
    recommendations = []

    if "constraint_facts" in missing_categories:
        recommendations.append("Extract from documentation files to capture constraints")

    if "implementation_facts" in missing_categories:
        recommendations.append("Extract from code files to capture implementation details")

    if "requirement_facts" in missing_categories:
        recommendations.append("Extract from README and setup documentation")

    if question_type == QuestionType.ONBOARDING:
        recommendations.append("Focus on setup guides, quickstart docs, and development workflow")

    if question_type == QuestionType.CONSTRAINT:
        recommendations.append("Focus on coding standards, best practices, and constraint documentation")

    if question_type == QuestionType.DEBUGGING:
        recommendations.append("Extract error handling patterns and common pitfalls from docs")

    return recommendations


def calculate_secondary_confidence(question: str,
                                   answer: str,
                                   supporting_facts: List[str],
                                   all_facts: List[Fact]) -> float:
    """
    Calculate secondary confidence based on fact coverage.
    This validates the LLM's self-reported confidence.
    """
    score = 0.0

    # Factor 1: Number of supporting facts (max 0.4)
    fact_count = len(supporting_facts)
    if fact_count >= 3:
        score += 0.4
    elif fact_count == 2:
        score += 0.3
    elif fact_count == 1:
        score += 0.2
    elif fact_count == 0:
        score += 0.0

    # Factor 2: Answer length and detail (max 0.3)
    answer_length = len(answer.split())
    if answer_length > 50:
        score += 0.3
    elif answer_length > 20:
        score += 0.2
    elif answer_length > 5:
        score += 0.1

    # Factor 3: Fact quality - high confidence facts (max 0.3)
    if supporting_facts:
        facts_obj = [f for f in all_facts if f.id in supporting_facts]
        if facts_obj:
            avg_fact_confidence = sum(f.confidence for f in facts_obj) / len(facts_obj)
            score += avg_fact_confidence * 0.3

    return min(score, 1.0)


def analyze_gaps(question: str,
                supporting_facts: List[str],
                missing_info: List[str],
                all_facts: List[Fact]) -> GapAnalysis:
    """
    Analyze what types of facts are missing to answer the question.
    """

    # Classify question type
    question_type = classify_question(question)

    # Get expected fact types for this question type
    expected_fact_types = get_expected_fact_types(question_type)

    # Get available fact types from supporting facts
    available_fact_types = set()
    for fact_id in supporting_facts:
        for fact in all_facts:
            if fact.id == fact_id:
                available_fact_types.add(fact.type)
                break

    # Calculate missing fact types
    missing_fact_types = expected_fact_types - available_fact_types

    # Map to human-readable categories
    missing_categories = map_to_categories(missing_fact_types, missing_info)

    # Generate recommendations
    recommendations = generate_extraction_recommendations(
        question_type=question_type,
        missing_categories=missing_categories
    )

    return GapAnalysis(
        question_type=question_type.value,
        expected_fact_types=sorted(list(expected_fact_types)),
        available_fact_types=sorted(list(available_fact_types)),
        missing_fact_types=sorted(list(missing_fact_types)),
        missing_categories=missing_categories,
        recommendations=recommendations
    )


def calculate_completeness_score(validation_results: List[ValidationResult]) -> CompletenessScore:
    """
    Calculate overall completeness based on question validation results.
    """

    total_questions = len(validation_results)
    if total_questions == 0:
        return CompletenessScore(
            total_questions=0,
            high_confidence_count=0,
            high_confidence_pct=0.0,
            medium_confidence_count=0,
            medium_confidence_pct=0.0,
            low_confidence_count=0,
            by_question_type={},
            weighted_score=0.0,
            overall_grade="N/A"
        )

    # Category 1: High confidence answers (>= 0.7)
    high_confidence = sum(1 for r in validation_results if r.confidence >= 0.7)
    high_confidence_pct = high_confidence / total_questions

    # Category 2: Medium confidence answers (>= 0.5)
    medium_confidence = sum(1 for r in validation_results if r.confidence >= 0.5)
    medium_confidence_pct = medium_confidence / total_questions

    # Category 3: Low confidence answers (< 0.5)
    low_confidence = total_questions - medium_confidence

    # Category 4: By question type
    by_type = {}
    for qtype in QuestionType:
        type_results = [r for r in validation_results
                       if r.gap_details and r.gap_details.get('question_type') == qtype.value]
        if type_results:
            type_avg = sum(r.confidence for r in type_results) / len(type_results)
            by_type[qtype.value] = type_avg

    # Overall score (weighted)
    # - Onboarding: 30% (critical for new devs)
    # - Constraint: 40% (critical for avoiding mistakes)
    # - Implementation: 20% (nice to have)
    # - Debugging: 10% (can be figured out)
    weights = {
        QuestionType.ONBOARDING.value: 0.30,
        QuestionType.CONSTRAINT.value: 0.40,
        QuestionType.IMPLEMENTATION.value: 0.20,
        QuestionType.DEBUGGING.value: 0.10,
    }

    weighted_score = 0.0
    for qtype_str, weight in weights.items():
        if qtype_str in by_type:
            weighted_score += by_type[qtype_str] * weight

    return CompletenessScore(
        total_questions=total_questions,
        high_confidence_count=high_confidence,
        high_confidence_pct=high_confidence_pct,
        medium_confidence_count=medium_confidence,
        medium_confidence_pct=medium_confidence_pct,
        low_confidence_count=low_confidence,
        by_question_type=by_type,
        weighted_score=weighted_score,
        overall_grade=calculate_grade(weighted_score)
    )


def calculate_grade(score: float) -> str:
    """Convert score to letter grade."""
    if score >= 0.9:
        return "A - Excellent"
    elif score >= 0.8:
        return "B - Good"
    elif score >= 0.7:
        return "C - Acceptable"
    elif score >= 0.6:
        return "D - Needs Work"
    else:
        return "F - Insufficient"


# Main Validator Class

class QueryValidator:
    """
    Main class for query-driven fact completeness validation.
    """

    def __init__(self, store: KraangStore, extractor: KraangExtractor):
        self.store = store
        self.extractor = extractor
        self.confidence_threshold = 0.7

    def validate_all_questions(self, question_sets: List[QuestionSet]) -> CompletenessScore:
        """
        Validate all questions and return overall completeness score.
        """
        facts = self.store.get_facts()
        relationships = self.store.get_relationships()

        all_results = []

        for question_set in question_sets:
            print(f"\n=== Validating {question_set.category.value} questions ===")

            for i, question in enumerate(question_set.questions, 1):
                print(f"\n[{i}/{len(question_set.questions)}] Q: {question}")

                try:
                    result = self.validate_question(
                        question=question,
                        facts=facts,
                        relationships=relationships
                    )

                    all_results.append(result)

                    # Print summary
                    confidence_icon = "✓" if result.confidence >= self.confidence_threshold else "✗"
                    print(f"{confidence_icon} Confidence: {result.confidence:.2f} "
                          f"(LLM: {result.llm_confidence:.2f}, Secondary: {result.secondary_confidence:.2f})")
                    print(f"   Answer: {result.answer[:100]}...")

                    if result.missing_categories:
                        print(f"   Missing: {', '.join(result.missing_categories)}")

                except Exception as e:
                    print(f"✗ Error validating question: {e}")
                    # Add a failed result
                    all_results.append(ValidationResult(
                        question=question,
                        answer=f"Error: {e}",
                        confidence=0.0,
                        llm_confidence=0.0,
                        secondary_confidence=0.0,
                        supporting_facts=[],
                        missing_categories=["error"],
                        gap_details=None
                    ))

        # Calculate overall score
        score = calculate_completeness_score(all_results)

        # Print summary
        self.print_completeness_report(score, all_results)

        # Save results
        self._save_results(score, all_results)

        return score

    def validate_question(self,
                         question: str,
                         facts: List[Fact],
                         relationships: List[Relationship]) -> ValidationResult:
        """Validate a single question."""

        # Step 1: Prepare context
        facts_context = self._format_facts_for_query(facts)
        relationships_context = self._format_relationships(relationships)

        # Step 2: Query LLM
        prompt = self._build_query_prompt(question, facts_context, relationships_context)
        response = self._query_llm(prompt)
        result = self._parse_json_response(response)

        # Step 3: Secondary confidence
        secondary_confidence = calculate_secondary_confidence(
            question=question,
            answer=result["answer"],
            supporting_facts=result["supporting_facts"],
            all_facts=facts
        )

        final_confidence = (result["confidence"] + secondary_confidence) / 2

        # Step 4: Always classify question type and do gap analysis
        # (even for high-confidence answers, we need the question type for scoring)
        gap_analysis = analyze_gaps(
            question=question,
            supporting_facts=result["supporting_facts"],
            missing_info=result.get("missing_info", []),
            all_facts=facts
        )

        # Step 5: Get supporting facts
        supporting_fact_objs = [f for f in facts if f.id in result["supporting_facts"]]

        # Step 6: Return result
        return ValidationResult(
            question=question,
            answer=result["answer"],
            confidence=final_confidence,
            llm_confidence=result["confidence"],
            secondary_confidence=secondary_confidence,
            supporting_facts=[f.to_dict() for f in supporting_fact_objs],
            missing_categories=gap_analysis.missing_categories if gap_analysis else [],
            gap_details=gap_analysis.to_dict() if gap_analysis else None
        )

    def _format_facts_for_query(self, facts: List[Fact]) -> str:
        """Format facts for LLM query."""
        lines = []
        for fact in facts:
            lines.append(f"[{fact.id}] {fact.statement}")
            lines.append(f"  Type: {fact.type}, Confidence: {fact.confidence}")
        return "\n".join(lines)

    def _format_relationships(self, relationships: List[Relationship]) -> str:
        """Format relationships for LLM query."""
        if not relationships:
            return "No relationships extracted yet."

        lines = []
        for rel in relationships:
            lines.append(f"{rel.fact_id_1} <-{rel.type.value}-> {rel.fact_id_2}")
        return "\n".join(lines)

    def _build_query_prompt(self, question: str, facts_context: str,
                           relationships_context: str) -> str:
        """Build the LLM query prompt."""
        return f"""You are a technical documentation assistant analyzing a codebase.

Facts extracted from codebase:
{facts_context}

Relationships between facts:
{relationships_context}

Developer Question: {question}

Please answer this question based ONLY on the provided facts. Provide:

1. ANSWER: Your answer to the question (be specific and practical)
2. CONFIDENCE: Your confidence in the answer (0.0 to 1.0)
   - 1.0: Complete, confident answer with multiple supporting facts
   - 0.7-0.9: Good answer but may miss some details
   - 0.4-0.7: Partial answer, significant gaps
   - 0.0-0.4: Cannot answer, insufficient facts
3. SUPPORTING_FACTS: List of fact IDs that support your answer (e.g., ["fact_1", "fact_2"])
4. MISSING_INFO: What information is missing (if confidence < 0.7)

Return as JSON:
{{
  "answer": "Your answer here",
  "confidence": 0.9,
  "supporting_facts": ["fact_1", "fact_2"],
  "missing_info": ["category1", "category2"] or []
}}

Return ONLY the JSON, no additional text.
"""

    def _query_llm(self, prompt: str) -> str:
        """Query LLM with prompt."""
        message = self.extractor.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text

    def _parse_json_response(self, response: str) -> Dict:
        """Parse JSON from LLM response."""
        # Extract JSON from response (handle markdown code blocks)
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            response = response.split("```")[1].split("```")[0].strip()

        return json.loads(response)

    def print_completeness_report(self, score: CompletenessScore,
                                 results: List[ValidationResult]):
        """Print detailed completeness report."""
        print("\n" + "="*70)
        print("QUERY-DRIVEN COMPLETENESS REPORT")
        print("="*70)

        print(f"\nOverall Score: {score.weighted_score:.2f} ({score.overall_grade})")
        print(f"\nTotal Questions: {score.total_questions}")
        print(f"High Confidence (>= 0.7): {score.high_confidence_count} ({score.high_confidence_pct:.1%})")
        print(f"Medium Confidence (>= 0.5): {score.medium_confidence_count} ({score.medium_confidence_pct:.1%})")
        print(f"Low Confidence (< 0.5): {score.low_confidence_count}")

        if score.by_question_type:
            print(f"\nBy Question Type:")
            for qtype, avg_confidence in sorted(score.by_question_type.items()):
                icon = "✓" if avg_confidence >= 0.7 else "✗"
                print(f"  {icon} {qtype:15s}: {avg_confidence:.2f}")

        # Show gaps
        print(f"\nMissing Fact Categories:")
        all_missing = {}
        for result in results:
            for category in result.missing_categories:
                all_missing[category] = all_missing.get(category, 0) + 1

        if all_missing:
            for category, count in sorted(all_missing.items(), key=lambda x: -x[1]):
                print(f"  - {category}: {count} question(s) affected")
        else:
            print("  None - all questions answered!")

        # Show recommendations
        print(f"\nRecommendations:")
        if score.weighted_score >= 0.9:
            print("  ✓ Excellent coverage! Facts are comprehensive.")
        elif score.weighted_score >= 0.8:
            print("  ✓ Good coverage. Address remaining gaps for production use.")
        elif score.weighted_score >= 0.7:
            print("  ⚠️  Acceptable but needs improvement. Focus on constraint questions.")
        else:
            print("  ✗ Insufficient coverage. Significant extraction work needed.")
            print("  → Run multi-pass extraction on low-coverage areas")
            print("  → Focus on constraint and onboarding documentation")

        # Specific recommendations based on gaps
        if all_missing:
            print("\n  Specific Actions:")
            if any("constraint" in cat for cat in all_missing):
                print("    • Extract from coding standards and constraint documentation")
            if any("implementation" in cat for cat in all_missing):
                print("    • Extract from more code files and implementation docs")
            if any("requirement" in cat for cat in all_missing):
                print("    • Extract from README, setup guides, and requirements docs")

    def _save_results(self, score: CompletenessScore, results: List[ValidationResult]):
        """Save validation results to file."""
        results_data = {
            "score": score.to_dict(),
            "results": [r.to_dict() for r in results]
        }

        results_file = self.store.base_dir / "validation_results.json"
        with open(results_file, 'w') as f:
            json.dump(results_data, f, indent=2)

        print(f"\nDetailed results saved to: {results_file}")


# Question Sets

def get_lotj_question_sets() -> List[QuestionSet]:
    """Get predefined question sets for LotJ MUD validation."""

    onboarding = QuestionSet(
        questions=[
            "How do I set up my local development environment?",
            "How do I start the MUD server for testing?",
            "How do I connect to the test server?",
            "What are the default test credentials?",
            "How do I restart the server after code changes?",
            "How do I access the database?",
            "How do I debug a crash?",
            "How do I format my code properly?",
            "What port does the game run on?",
        ],
        category=QuestionType.ONBOARDING,
        priority=1
    )

    constraint = QuestionSet(
        questions=[
            "Can I use malloc() directly in C code?",
            "Must I place new structs in types.h?",
            "Can I create a new header file?",
            "Must function names use snake_case?",
            "Must global variables be prefixed with g_?",
            "Can I have compiler warnings in my code?",
            "Must I use the CREATE macro for memory allocation?",
            "Can I manually set next/prev pointers in linked lists?",
            "Must I use the LINK/UNLINK macros?",
            "Can I use docker-compose down during development?",
            "Should I use DISPOSE to free memory?",
            "Must I put function prototypes in functions.h?",
        ],
        category=QuestionType.CONSTRAINT,
        priority=1
    )

    implementation = QuestionSet(
        questions=[
            "Where are the core header files?",
            "What is in mud.h?",
            "How does the memory management system work?",
            "How do I add an item to a linked list?",
            "What is the LINK macro and how do I use it?",
            "Where are server logs stored?",
            "How does the Lua integration work?",
            "What build targets are available?",
            "How does the testing tool work?",
            "What is the structure of the Docker services?",
            "Where are crash backtraces stored?",
            "How does language translation/scrambling work?",
        ],
        category=QuestionType.IMPLEMENTATION,
        priority=2
    )

    debugging = QuestionSet(
        questions=[
            "Why did my build fail with warnings?",
            "Why does restarting take 10+ minutes?",
            "Why am I getting memory corruption?",
            "Why is my linked list code crashing?",
            "Why can't I find the function prototype?",
            "Why is my code style wrong?",
            "Why did the database reset?",
            "Why is my speech appearing as gibberish to some players?",
        ],
        category=QuestionType.DEBUGGING,
        priority=2
    )

    return [onboarding, constraint, implementation, debugging]


# CLI Integration Example

if __name__ == "__main__":
    import sys
    from kraang import KraangStore, KraangExtractor

    # Example usage
    store = KraangStore()
    extractor = KraangExtractor(store)
    validator = QueryValidator(store, extractor)

    question_sets = get_lotj_question_sets()

    print("Running query-driven completeness validation...")
    print(f"Testing {sum(len(qs.questions) for qs in question_sets)} questions\n")

    score = validator.validate_all_questions(question_sets)

    # Exit with status based on score
    if score.weighted_score >= 0.7:
        sys.exit(0)
    else:
        sys.exit(1)
