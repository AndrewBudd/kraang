# Query-Driven Validation System - Usage Guide

## Quick Start

```bash
# Run validation on existing facts
kraang validate-queries

# Results saved to .kraang/validation_results.json
```

## What It Does

The query-driven validation system tests whether your extracted facts can answer typical developer questions. This provides an objective measure of fact completeness.

## Example Output

```
=== Validating constraint questions ===

[1/12] Q: Can I use malloc() directly in C code?
✓ Confidence: 1.00 (LLM: 1.00, Secondary: 1.00)
   Answer: No, you must NOT use malloc() directly. The MUD uses a custom memory...

[2/12] Q: Must I place new structs in types.h?
✓ Confidence: 1.00 (LLM: 1.00, Secondary: 1.00)
   Answer: Yes, you MUST place all new struct definitions in types.h...

======================================================================
QUERY-DRIVEN COMPLETENESS REPORT
======================================================================

Overall Score: 0.96 (A - Excellent)

Total Questions: 41
High Confidence (>= 0.7): 41 (100.0%)
Medium Confidence (>= 0.5): 41 (100.0%)
Low Confidence (< 0.5): 0

By Question Type:
  ✓ constraint     : 0.97
  ✓ debugging      : 0.97
  ✓ implementation : 0.93
  ✓ onboarding     : 0.96

Detailed results saved to: .kraang/validation_results.json
```

## Understanding the Scores

### Overall Score (0.0 - 1.0)
- **0.90+** (A) - Gold Standard: Production-ready, comprehensive
- **0.80+** (B) - Good: Suitable for most use cases
- **0.70+** (C) - Acceptable: Basic coverage, needs improvement
- **0.60+** (D) - Needs Work: Significant gaps
- **< 0.60** (F) - Insufficient: Major extraction work needed

### Confidence Levels
- **1.00** - Perfect: Multiple supporting facts, complete answer
- **0.7-0.9** - High: Good answer, minor gaps possible
- **0.5-0.7** - Medium: Partial answer, significant gaps
- **< 0.5** - Low: Cannot answer confidently

### Dual Confidence Scoring

Each answer gets two confidence scores that are averaged:

1. **LLM Confidence:** Claude's self-assessment of answer quality
2. **Secondary Confidence:** Calculated from:
   - Number of supporting facts (0-3+ facts)
   - Answer detail level (word count)
   - Quality of supporting facts (fact confidence)

This prevents overconfidence on shallow answers.

## Question Categories

### Onboarding (30% weight)
Questions new developers ask when starting:
- "How do I set up my local development environment?"
- "How do I start the MUD server for testing?"
- "What are the default test credentials?"

### Constraint (40% weight - most critical)
Rules and limitations developers must follow:
- "Can I use malloc() directly in C code?"
- "Must I place new structs in types.h?"
- "Can I have compiler warnings in my code?"

### Implementation (20% weight)
Understanding existing code and architecture:
- "How does the memory management system work?"
- "What is the LINK macro and how do I use it?"
- "Where are server logs stored?"

### Debugging (10% weight)
Troubleshooting problems:
- "Why did my build fail with warnings?"
- "Why is my linked list code crashing?"
- "Why did the database reset?"

## JSON Output Format

Results are saved to `.kraang/validation_results.json`:

```json
{
  "score": {
    "total_questions": 41,
    "high_confidence_count": 41,
    "high_confidence_pct": 1.0,
    "medium_confidence_count": 41,
    "medium_confidence_pct": 1.0,
    "low_confidence_count": 0,
    "by_question_type": {
      "onboarding": 0.96,
      "constraint": 0.97,
      "implementation": 0.93,
      "debugging": 0.98
    },
    "weighted_score": 0.96,
    "overall_grade": "A - Excellent"
  },
  "results": [
    {
      "question": "Can I use malloc() directly?",
      "answer": "No, you must use CREATE macro...",
      "confidence": 1.0,
      "llm_confidence": 1.0,
      "secondary_confidence": 1.0,
      "supporting_facts": [
        {
          "id": "fact_15",
          "statement": "Memory allocation MUST use CREATE macro",
          "type": "constraint",
          "confidence": 1.0
        }
      ],
      "missing_categories": [],
      "gap_details": null
    }
  ]
}
```

## Gap Analysis

When confidence is below threshold (0.7), the system identifies:

1. **Missing Fact Types:** What kinds of facts are needed
2. **Missing Categories:** Specific knowledge gaps
3. **Recommendations:** What to extract next

Example gap report:
```
Missing Fact Categories:
  - design_facts: 14 questions affected
  - implementation_facts: 5 questions affected

Specific Actions:
  • Extract from design documents for design_facts
  • Extract from more code files for implementation_facts
```

## Common Use Cases

### 1. Initial Assessment
After first extraction, run validation to see baseline completeness:
```bash
kraang extract artifact_1
kraang validate-queries
```

### 2. Iterative Improvement
Use gaps to guide what to extract next:
```bash
kraang validate-queries  # Shows missing constraint_facts
kraang add docs/constraints.md
kraang extract artifact_N
kraang validate-queries  # Check improvement
```

### 3. CI/CD Integration
Fail builds if completeness drops:
```bash
#!/bin/bash
kraang validate-queries
score=$(python3 -c "import json; print(json.load(open('.kraang/validation_results.json'))['score']['weighted_score'])")
if (( $(echo "$score < 0.7" | bc -l) )); then
  echo "Completeness below threshold"
  exit 1
fi
```

### 4. Documentation Quality Gate
Before releasing documentation, verify it can answer key questions:
```bash
# Extract from all docs
for doc in docs/*.md; do
  kraang add "$doc"
  kraang extract artifact_N
done

# Validate completeness
kraang validate-queries

# Must achieve B grade or higher for release
```

## Interpreting Results

### High Score (0.9+) with Gaps
- Facts are **practically complete**
- Gaps are "nice-to-have" details
- Safe for production use
- Example: LotJ achieved 0.96 but still showed Lua API detail gaps

### Medium Score (0.7-0.8) with Gaps
- Core knowledge captured
- Some critical information missing
- Address high-priority gaps before production
- Focus on constraint and onboarding categories

### Low Score (< 0.7)
- Significant extraction work needed
- Many questions cannot be answered
- Not ready for developer onboarding
- Extract from key documentation and code

## Tips for Improvement

### To Improve Constraint Scores
Extract from:
- Coding standards documents
- CONTRIBUTING.md files
- Style guides
- Architecture decision records (ADRs)
- Code review guidelines

### To Improve Onboarding Scores
Extract from:
- README.md
- QUICKSTART.md
- Development setup guides
- Environment configuration docs
- Getting started tutorials

### To Improve Implementation Scores
Extract from:
- Source code files (.c, .h)
- API documentation
- Architecture diagrams
- System design docs
- Code comments and headers

### To Improve Debugging Scores
Extract from:
- Troubleshooting guides
- Common issues documentation
- Error message references
- Debugging procedures
- FAQ documents

## Limitations

1. **LLM-dependent:** Requires Anthropic API access
2. **Time:** Takes 5-8 minutes for 41 questions
3. **Cost:** 41 API calls per validation run
4. **Language:** Questions are LotJ MUD-specific (customize for your domain)
5. **Static questions:** Doesn't adapt to your codebase (yet)

## Customization

To add your own questions, edit `/home/budda/Code/kraang/query_validator.py`:

```python
def get_custom_question_sets() -> List[QuestionSet]:
    """Define your own validation questions."""

    onboarding = QuestionSet(
        questions=[
            "How do I set up my dev environment?",
            "How do I run tests?",
            # Add your questions...
        ],
        category=QuestionType.ONBOARDING,
        priority=1
    )

    # Define other categories...

    return [onboarding, constraint, implementation, debugging]
```

Then modify `kraang.py` to use your question set:
```python
def cmd_validate_queries(self):
    from query_validator import QueryValidator, get_custom_question_sets
    question_sets = get_custom_question_sets()  # Use custom questions
    validator = QueryValidator(self.store, KraangExtractor(self.store))
    score = validator.validate_all_questions(question_sets)
```

## Related Commands

- `kraang completeness` - Traditional metrics (fact count, relationships, etc.)
- `kraang coverage` - Line-by-line coverage analysis
- `kraang list facts` - Show all extracted facts
- `kraang relate` - Analyze fact relationships

## See Also

- [QUERY_VALIDATION_SYSTEM.md](QUERY_VALIDATION_SYSTEM.md) - Full design document
- [QUERY_VALIDATION_TEST_RESULTS.md](QUERY_VALIDATION_TEST_RESULTS.md) - Test results and analysis
- [README.md](README.md) - Main Kraang documentation
