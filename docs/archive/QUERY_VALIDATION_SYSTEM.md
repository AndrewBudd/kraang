# Query-Driven Validation System for Fact Completeness

## Overview

This document defines a query-driven validation system to test whether extracted facts are "complete enough" to answer typical developer questions. The system uses developer questions as acceptance tests for fact coverage.

## Core Thesis

**Facts are complete enough when they can confidently answer the questions developers actually ask.**

This approach provides:
- Objective, measurable criteria for completeness
- Direct validation of practical utility
- Identification of specific knowledge gaps
- Prioritization of extraction work

---

## 1. Developer Question Taxonomy

### 1.1 Onboarding Questions ("How do I...")
Questions asked by new developers learning the codebase.

**Characteristics:**
- Procedural focus
- Entry-level scope
- Tools and workflow oriented
- Environment setup related

**Examples:**
- "How do I set up my local development environment?"
- "How do I build and run the project?"
- "How do I connect to test the game?"
- "How do I debug crashes?"
- "How do I run tests?"

**Required Fact Types:**
- Requirements (dependencies, tools)
- Implementation (commands, paths, ports)
- Constraints (Docker-first, never use down)

---

### 1.2 Constraint Questions ("Can I...", "Must I...", "Should I...")
Questions about rules, conventions, and limitations.

**Characteristics:**
- Boolean or bounded answers
- Rule-focused
- Often MUST/MUST NOT language
- Critical for avoiding mistakes

**Examples:**
- "Can I use malloc() directly?"
- "Must I add new structs to types.h?"
- "Can I create a new header file?"
- "Should I use snake_case or camelCase for C functions?"
- "Must I use the LINK macro for linked lists?"

**Required Fact Types:**
- Constraints (explicit rules)
- Design patterns (conventions)
- Implementation guidelines

---

### 1.3 Implementation Questions ("Where is...", "How does...", "What is...")
Questions about understanding existing code and architecture.

**Characteristics:**
- Knowledge retrieval
- Code navigation
- Understanding mechanisms
- Exploring relationships

**Examples:**
- "Where are the core headers defined?"
- "How does the memory management system work?"
- "What is the CREATE macro and when should I use it?"
- "How does language translation work?"
- "Where are logs stored?"

**Required Fact Types:**
- Implementation details
- Design patterns
- Artifact locations
- System architecture

---

### 1.4 Debugging Questions ("Why did...", "What causes...")
Questions asked when troubleshooting problems.

**Characteristics:**
- Causal reasoning
- Problem-solving focused
- Often constraint violations
- Requires relationship understanding

**Examples:**
- "Why did my build fail with warnings?"
- "What causes the database to rebuild?"
- "Why can't I use double free?"
- "What causes a crash when modifying linked lists?"
- "Why is my code not following the style guide?"

**Required Fact Types:**
- Constraints (violations)
- Relationships (causes and effects)
- Implementation (error conditions)
- Design patterns (correct usage)

---

## 2. LotJ MUD Codebase: Example Questions

### 2.1 Onboarding Questions (9 questions)

1. "How do I set up my local development environment?"
2. "How do I start the MUD server for testing?"
3. "How do I connect to the test server?"
4. "What are the default test credentials?"
5. "How do I restart the server after code changes?"
6. "How do I access the database?"
7. "How do I debug a crash?"
8. "How do I format my code properly?"
9. "What port does the game run on?"

### 2.2 Constraint Questions (12 questions)

10. "Can I use malloc() directly in C code?"
11. "Must I place new structs in types.h?"
12. "Can I create a new header file?"
13. "Must function names use snake_case?"
14. "Must global variables be prefixed with g_?"
15. "Can I have compiler warnings in my code?"
16. "Must I use the CREATE macro for memory allocation?"
17. "Can I manually set next/prev pointers in linked lists?"
18. "Must I use the LINK/UNLINK macros?"
19. "Can I use docker-compose down during development?"
20. "Should I use DISPOSE to free memory?"
21. "Must I put function prototypes in functions.h?"

### 2.3 Implementation Questions (12 questions)

22. "Where are the core header files?"
23. "What is in mud.h?"
24. "How does the memory management system work?"
25. "How do I add an item to a linked list?"
26. "What is the LINK macro and how do I use it?"
27. "Where are server logs stored?"
28. "How does the Lua integration work?"
29. "What build targets are available?"
30. "How does the testing tool work?"
31. "What is the structure of the Docker services?"
32. "Where are crash backtraces stored?"
33. "How does language translation/scrambling work?"

### 2.4 Debugging Questions (8 questions)

34. "Why did my build fail with warnings?"
35. "Why does restarting take 10+ minutes?"
36. "Why am I getting memory corruption?"
37. "Why is my linked list code crashing?"
38. "Why can't I find the function prototype?"
39. "Why is my code style wrong?"
40. "Why did the database reset?"
41. "Why is my speech appearing as gibberish to some players?"

**Total: 41 example questions across 4 categories**

---

## 3. Query Validation Algorithm

### 3.1 High-Level Flow

```
Input: Question (string), Facts (list), Relationships (list)
Output: Answer (string), Confidence (0.0-1.0), Missing Fact Categories (list)

1. Query Phase
   - Send question + facts to LLM
   - Request structured answer with confidence
   - Extract supporting fact IDs

2. Confidence Scoring
   - LLM self-assessment (primary)
   - Fact coverage analysis (secondary)
   - Answer completeness check (tertiary)

3. Gap Analysis (if confidence < threshold)
   - Identify question type
   - Determine expected fact types
   - Compare to available facts
   - Report missing categories

4. Return Results
   - Answer text
   - Overall confidence score
   - List of supporting facts
   - List of missing fact categories
```

### 3.2 Detailed Algorithm

```python
def validate_question(question: str,
                     facts: List[Fact],
                     relationships: List[Relationship],
                     confidence_threshold: float = 0.7) -> ValidationResult:
    """
    Validate if facts can answer a developer question.

    Returns:
        ValidationResult with answer, confidence, and gap analysis
    """

    # Step 1: Prepare context for LLM
    facts_context = format_facts_for_query(facts)
    relationships_context = format_relationships(relationships)

    # Step 2: Query LLM with structured prompt
    prompt = f"""You are a technical documentation assistant analyzing a codebase.

Facts extracted from codebase:
{facts_context}

Relationships between facts:
{relationships_context}

Developer Question: {question}

Please answer this question based ONLY on the provided facts. Provide:

1. ANSWER: Your answer to the question
2. CONFIDENCE: Your confidence in the answer (0.0 to 1.0)
   - 1.0: Complete, confident answer with multiple supporting facts
   - 0.7-0.9: Good answer but may miss some details
   - 0.4-0.7: Partial answer, significant gaps
   - 0.0-0.4: Cannot answer, insufficient facts
3. SUPPORTING_FACTS: List of fact IDs that support your answer
4. MISSING_INFO: What information is missing (if confidence < 0.7)

Return as JSON:
{{
  "answer": "Your answer here",
  "confidence": 0.9,
  "supporting_facts": ["fact_1", "fact_2"],
  "missing_info": ["category1", "category2"] or []
}}
"""

    # Step 3: Get LLM response
    response = query_llm(prompt)
    result = parse_json_response(response)

    # Step 4: Secondary confidence scoring (validation)
    secondary_confidence = calculate_secondary_confidence(
        question=question,
        answer=result["answer"],
        supporting_facts=result["supporting_facts"],
        all_facts=facts
    )

    # Average primary and secondary confidence
    final_confidence = (result["confidence"] + secondary_confidence) / 2

    # Step 5: Gap analysis if confidence is low
    if final_confidence < confidence_threshold:
        gap_analysis = analyze_gaps(
            question=question,
            supporting_facts=result["supporting_facts"],
            missing_info=result["missing_info"],
            all_facts=facts
        )
    else:
        gap_analysis = None

    # Step 6: Return structured result
    return ValidationResult(
        question=question,
        answer=result["answer"],
        confidence=final_confidence,
        llm_confidence=result["confidence"],
        secondary_confidence=secondary_confidence,
        supporting_facts=get_facts_by_ids(result["supporting_facts"], facts),
        missing_categories=gap_analysis.missing_categories if gap_analysis else [],
        gap_details=gap_analysis
    )
```

### 3.3 Secondary Confidence Calculation

```python
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
        facts_obj = get_facts_by_ids(supporting_facts, all_facts)
        avg_fact_confidence = sum(f.confidence for f in facts_obj) / len(facts_obj)
        score += avg_fact_confidence * 0.3

    return min(score, 1.0)
```

### 3.4 Gap Analysis

```python
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
        fact = get_fact_by_id(fact_id, all_facts)
        if fact:
            available_fact_types.add(fact.type)

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
        question_type=question_type,
        expected_fact_types=expected_fact_types,
        available_fact_types=available_fact_types,
        missing_fact_types=missing_fact_types,
        missing_categories=missing_categories,
        recommendations=recommendations
    )


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
```

---

## 4. Acceptance Criteria

### 4.1 Overall Completeness Score

```python
def calculate_completeness_score(validation_results: List[ValidationResult]) -> CompletenessScore:
    """
    Calculate overall completeness based on question validation results.
    """

    total_questions = len(validation_results)

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
        type_results = [r for r in validation_results if r.gap_details and r.gap_details.question_type == qtype]
        if type_results:
            type_avg = sum(r.confidence for r in type_results) / len(type_results)
            by_type[qtype.value] = type_avg

    # Overall score (weighted)
    # - Onboarding: 30% (critical for new devs)
    # - Constraint: 40% (critical for avoiding mistakes)
    # - Implementation: 20% (nice to have)
    # - Debugging: 10% (can be figured out)
    weights = {
        QuestionType.ONBOARDING: 0.30,
        QuestionType.CONSTRAINT: 0.40,
        QuestionType.IMPLEMENTATION: 0.20,
        QuestionType.DEBUGGING: 0.10,
    }

    weighted_score = 0.0
    for qtype, weight in weights.items():
        if qtype.value in by_type:
            weighted_score += by_type[qtype.value] * weight

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
```

### 4.2 Specific Acceptance Criteria

**Minimum Viable Completeness:**
- Overall weighted score: >= 0.70 (C grade)
- Onboarding questions: >= 80% with confidence > 0.7
- Constraint questions: >= 80% with confidence > 0.7
- Implementation questions: >= 60% with confidence > 0.7
- Debugging questions: >= 50% with confidence > 0.7

**Production-Ready Completeness:**
- Overall weighted score: >= 0.85 (B+ grade)
- Onboarding questions: >= 95% with confidence > 0.7
- Constraint questions: >= 90% with confidence > 0.7
- Implementation questions: >= 75% with confidence > 0.7
- Debugging questions: >= 70% with confidence > 0.7

**Gold Standard Completeness:**
- Overall weighted score: >= 0.90 (A grade)
- All question types: >= 90% with confidence > 0.7
- Average confidence across all questions: >= 0.85

### 4.3 Gap-Specific Criteria

**Critical Gaps** (require immediate extraction):
- Any constraint question with confidence < 0.5
- Any onboarding question with confidence < 0.6
- Missing facts in core areas: memory management, header structure, build system

**Important Gaps** (should address soon):
- Implementation questions with confidence < 0.5
- Debugging questions with confidence < 0.4
- Missing relationships between constraints and implementations

**Nice-to-Have Gaps** (lower priority):
- Edge case debugging questions
- Advanced implementation details
- Optional tooling questions

---

## 5. Python Implementation

### 5.1 Data Classes

```python
from dataclasses import dataclass
from typing import List, Optional, Dict, Set
from enum import Enum


class QuestionType(Enum):
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
    supporting_facts: List[Fact]
    missing_categories: List[str]
    gap_details: Optional['GapAnalysis']


@dataclass
class GapAnalysis:
    """Analysis of missing facts for a question."""
    question_type: QuestionType
    expected_fact_types: Set[str]
    available_fact_types: Set[str]
    missing_fact_types: Set[str]
    missing_categories: List[str]
    recommendations: List[str]


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


@dataclass
class QuestionSet:
    """A set of validation questions."""
    questions: List[str]
    category: QuestionType
    priority: int  # 1=critical, 2=important, 3=nice-to-have
```

### 5.2 Main Validator Class

```python
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

            for question in question_set.questions:
                print(f"\nQ: {question}")

                result = self.validate_question(
                    question=question,
                    facts=facts,
                    relationships=relationships
                )

                all_results.append(result)

                # Print summary
                confidence_icon = "✓" if result.confidence >= self.confidence_threshold else "✗"
                print(f"{confidence_icon} Confidence: {result.confidence:.2f}")
                print(f"   Answer: {result.answer[:100]}...")

                if result.missing_categories:
                    print(f"   Missing: {', '.join(result.missing_categories)}")

        # Calculate overall score
        score = calculate_completeness_score(all_results)

        # Print summary
        self.print_completeness_report(score, all_results)

        return score

    def validate_question(self,
                         question: str,
                         facts: List[Fact],
                         relationships: List[Relationship]) -> ValidationResult:
        """Validate a single question (implements algorithm from 3.2)."""

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

        # Step 4: Gap analysis
        if final_confidence < self.confidence_threshold:
            gap_analysis = analyze_gaps(
                question=question,
                supporting_facts=result["supporting_facts"],
                missing_info=result["missing_info"],
                all_facts=facts
            )
        else:
            gap_analysis = None

        # Step 5: Return result
        return ValidationResult(
            question=question,
            answer=result["answer"],
            confidence=final_confidence,
            llm_confidence=result["confidence"],
            secondary_confidence=secondary_confidence,
            supporting_facts=self._get_facts_by_ids(result["supporting_facts"], facts),
            missing_categories=gap_analysis.missing_categories if gap_analysis else [],
            gap_details=gap_analysis
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

1. ANSWER: Your answer to the question
2. CONFIDENCE: Your confidence in the answer (0.0 to 1.0)
   - 1.0: Complete, confident answer with multiple supporting facts
   - 0.7-0.9: Good answer but may miss some details
   - 0.4-0.7: Partial answer, significant gaps
   - 0.0-0.4: Cannot answer, insufficient facts
3. SUPPORTING_FACTS: List of fact IDs that support your answer
4. MISSING_INFO: What information is missing (if confidence < 0.7)

Return as JSON:
{{
  "answer": "Your answer here",
  "confidence": 0.9,
  "supporting_facts": ["fact_1", "fact_2"],
  "missing_info": ["category1", "category2"] or []
}}
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
        import json

        # Extract JSON from response (handle markdown code blocks)
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            response = response.split("```")[1].split("```")[0].strip()

        return json.loads(response)

    def _get_facts_by_ids(self, fact_ids: List[str], all_facts: List[Fact]) -> List[Fact]:
        """Get fact objects by IDs."""
        return [f for f in all_facts if f.id in fact_ids]

    def print_completeness_report(self, score: CompletenessScore,
                                 results: List[ValidationResult]):
        """Print detailed completeness report."""
        print("\n" + "="*60)
        print("QUERY-DRIVEN COMPLETENESS REPORT")
        print("="*60)

        print(f"\nOverall Score: {score.weighted_score:.2f} ({score.overall_grade})")
        print(f"\nTotal Questions: {score.total_questions}")
        print(f"High Confidence (>= 0.7): {score.high_confidence_count} ({score.high_confidence_pct:.1%})")
        print(f"Medium Confidence (>= 0.5): {score.medium_confidence_count} ({score.medium_confidence_pct:.1%})")
        print(f"Low Confidence (< 0.5): {score.low_confidence_count}")

        print(f"\nBy Question Type:")
        for qtype, avg_confidence in score.by_question_type.items():
            icon = "✓" if avg_confidence >= 0.7 else "✗"
            print(f"  {icon} {qtype}: {avg_confidence:.2f}")

        # Show gaps
        print(f"\nMissing Fact Categories:")
        all_missing = {}
        for result in results:
            for category in result.missing_categories:
                all_missing[category] = all_missing.get(category, 0) + 1

        if all_missing:
            for category, count in sorted(all_missing.items(), key=lambda x: -x[1]):
                print(f"  - {category}: {count} questions affected")
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
```

### 5.3 Question Sets for LotJ

```python
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
```

### 5.4 CLI Integration

```python
# Add to KraangCLI class

def cmd_validate_queries(self):
    """Run query-driven validation to test completeness."""

    # Get question sets
    question_sets = get_lotj_question_sets()

    # Create validator
    validator = QueryValidator(self.store, KraangExtractor(self.store))

    # Run validation
    print("Running query-driven completeness validation...")
    print(f"Testing {sum(len(qs.questions) for qs in question_sets)} questions\n")

    score = validator.validate_all_questions(question_sets)

    # Save results
    results_file = self.store.base_dir / "validation_results.json"
    with open(results_file, 'w') as f:
        json.dump(asdict(score), f, indent=2)

    print(f"\nResults saved to {results_file}")


# Update CLI command handler
def run(self, args: List[str]):
    # ... existing commands ...
    elif command == "validate-queries":
        self.cmd_validate_queries()
```

---

## 6. Usage Workflow

### 6.1 Initial Validation

```bash
# After extracting facts
kraang validate-queries

# Output:
# === Validating onboarding questions ===
# Q: How do I set up my local development environment?
# ✓ Confidence: 0.92
#    Answer: Use Docker Compose exclusively for local development...
#
# Q: How do I start the MUD server?
# ✓ Confidence: 0.85
#    Answer: Run docker-compose up to start all services...
#
# ...
#
# === COMPLETENESS REPORT ===
# Overall Score: 0.78 (C - Acceptable)
# High Confidence: 28/41 (68%)
# Missing Categories:
#   - error_handling: 5 questions
#   - testing_patterns: 3 questions
```

### 6.2 Iterative Improvement

```bash
# 1. Identify gaps
kraang validate-queries

# 2. Extract more facts from identified areas
kraang add src/error.c
kraang extract artifact_N

# 3. Re-validate
kraang validate-queries

# 4. Repeat until score >= 0.80
```

### 6.3 Continuous Validation

```bash
# Add to CI/CD pipeline
# Fail if score drops below threshold

./kraang.py validate-queries
if [ $SCORE -lt 0.80 ]; then
  echo "Completeness score below threshold"
  exit 1
fi
```

---

## 7. Extensions and Future Work

### 7.1 Custom Question Sets

Allow users to define custom question sets for their domain:

```python
# custom_questions.yaml
onboarding:
  - "How do I configure authentication?"
  - "How do I add a new API endpoint?"

constraint:
  - "Can I use async/await in this codebase?"
  - "Must all endpoints have rate limiting?"
```

### 7.2 Active Learning

Use validation results to guide extraction:

```python
def suggest_next_extraction(validation_results: List[ValidationResult]) -> List[str]:
    """
    Suggest which files to extract next based on gaps.

    Returns:
        List of file paths prioritized by impact
    """
    # Analyze missing categories
    # Map to likely source files
    # Prioritize by question importance
    # Return ranked list
```

### 7.3 Regression Testing

Track validation scores over time:

```python
# Save validation results with timestamp
# Compare to previous runs
# Alert on score degradation
# Useful for detecting when code changes invalidate facts
```

### 7.4 Interactive Query Mode

```python
kraang query "How do I allocate memory?"
# Uses validation system to answer ad-hoc questions
# Shows confidence and supporting facts
# Suggests related facts to extract if confidence is low
```

---

## 8. Summary

### Key Advantages of Query-Driven Validation

1. **Objective Measurement**: Clear metrics for completeness
2. **Practical Focus**: Tests real developer needs
3. **Gap Identification**: Pinpoints exactly what's missing
4. **Prioritization**: Weights critical questions higher
5. **Continuous Improvement**: Enables iterative refinement

### Implementation Checklist

- [ ] Define question taxonomy (4 categories)
- [ ] Create domain-specific question sets (41 for LotJ)
- [ ] Implement validation algorithm with LLM querying
- [ ] Add secondary confidence scoring
- [ ] Build gap analysis system
- [ ] Define acceptance criteria
- [ ] Create CLI integration
- [ ] Test on LotJ codebase
- [ ] Iterate based on results

### Success Metrics

**Validation System Quality:**
- Can classify questions into taxonomy: 100%
- LLM confidence aligns with secondary confidence: > 80%
- Gap analysis identifies correct missing categories: > 90%

**Fact Completeness:**
- Minimum viable: 70% overall score
- Production ready: 85% overall score
- Gold standard: 90% overall score

---

## Conclusion

Query-driven validation provides a practical, measurable approach to determining fact completeness. By testing whether facts can answer real developer questions, we ensure that extraction efforts focus on practical utility rather than abstract coverage metrics.

The system is:
- **Objective**: Clear scoring and acceptance criteria
- **Actionable**: Identifies specific gaps to address
- **Flexible**: Works with any question set or domain
- **Continuous**: Can be run repeatedly to track progress

For the LotJ MUD codebase, this system provides 41 validation questions across 4 categories, enabling systematic testing of fact extraction completeness.
