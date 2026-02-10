# Query Validation System - Example Usage

This document demonstrates how to use the query-driven validation system to test fact completeness.

## Quick Start

```bash
# 1. Initialize project and extract facts
./kraang.py init
./kraang.py add docs/CLAUDE.md
./kraang.py extract artifact_1

# 2. Run query validation
./kraang.py validate-queries
```

## What It Does

The query validator tests whether your extracted facts can answer typical developer questions. It:

1. Asks 41 predefined questions across 4 categories
2. Uses Claude to answer each question using only extracted facts
3. Scores confidence for each answer
4. Identifies gaps in fact coverage
5. Generates an overall completeness score

## Example Output

```
Running query-driven completeness validation...
Testing 41 questions
This may take several minutes...

=== Validating onboarding questions ===

[1/9] Q: How do I set up my local development environment?
✓ Confidence: 0.92 (LLM: 0.95, Secondary: 0.89)
   Answer: Use Docker Compose exclusively for local development. Never build or run services directly...

[2/9] Q: How do I start the MUD server for testing?
✓ Confidence: 0.87 (LLM: 0.90, Secondary: 0.84)
   Answer: Run docker-compose up to start all services including the MUD server, database, and...

[3/9] Q: How do I connect to the test server?
✓ Confidence: 0.91 (LLM: 0.95, Secondary: 0.87)
   Answer: Connect via telnet to localhost on port 5656. Use the default test credentials...

[4/9] Q: What are the default test credentials?
✓ Confidence: 0.98 (LLM: 1.00, Secondary: 0.96)
   Answer: Username: 'legend', Password: 'password'

...

=== Validating constraint questions ===

[1/12] Q: Can I use malloc() directly in C code?
✓ Confidence: 0.95 (LLM: 1.00, Secondary: 0.90)
   Answer: No, you cannot use malloc() directly. The MUD uses a custom memory management system...

[2/12] Q: Must I place new structs in types.h?
✓ Confidence: 0.98 (LLM: 1.00, Secondary: 0.96)
   Answer: Yes, ALL new struct definitions MUST be placed in types.h. This is a critical...

[3/12] Q: Can I create a new header file?
✓ Confidence: 0.94 (LLM: 1.00, Secondary: 0.88)
   Answer: No, DO NOT create new header files. Use the existing well-established header file...

...

=== Validating implementation questions ===

[1/12] Q: Where are the core header files?
✓ Confidence: 0.89 (LLM: 0.90, Secondary: 0.88)
   Answer: The core header files are: mud.h (981 lines with memory macros), const.h (716 lines)...

[2/12] Q: What is in mud.h?
✓ Confidence: 0.86 (LLM: 0.85, Secondary: 0.87)
   Answer: mud.h is the primary header containing 981 lines with memory management macros...

...

=== Validating debugging questions ===

[1/8] Q: Why did my build fail with warnings?
✓ Confidence: 0.88 (LLM: 0.85, Secondary: 0.91)
   Answer: No compiler warnings are acceptable - all builds MUST be clean. This is a strict...

[2/8] Q: Why does restarting take 10+ minutes?
✓ Confidence: 0.93 (LLM: 0.95, Secondary: 0.91)
   Answer: Using 'docker-compose down' forces a complete database rebuild which takes 10+...

[3/8] Q: Why am I getting memory corruption?
✗ Confidence: 0.62 (LLM: 0.65, Secondary: 0.59)
   Answer: Memory corruption likely occurs from incorrect memory management. You must use...
   Missing: error_handling, debugging_patterns

...

======================================================================
QUERY-DRIVEN COMPLETENESS REPORT
======================================================================

Overall Score: 0.83 (B - Good)

Total Questions: 41
High Confidence (>= 0.7): 37 (90%)
Medium Confidence (>= 0.5): 39 (95%)
Low Confidence (< 0.5): 2

By Question Type:
  ✓ onboarding     : 0.91
  ✓ constraint     : 0.94
  ✓ implementation : 0.79
  ✗ debugging      : 0.68

Missing Fact Categories:
  - error_handling: 3 questions affected
  - debugging_patterns: 2 questions affected
  - testing_patterns: 1 question affected

Recommendations:
  ✓ Good coverage. Address remaining gaps for production use.

  Specific Actions:
    • Extract from coding standards and constraint documentation
    • Extract from more code files and implementation docs

Detailed results saved to: .kraang/validation_results.json
```

## Understanding the Scores

### Confidence Levels

- **1.0**: Perfect answer with strong supporting facts
- **0.7-0.9**: Good answer, minor gaps
- **0.5-0.7**: Partial answer, significant information missing
- **0.0-0.5**: Cannot answer confidently

### Overall Score Calculation

Weighted by question importance:
- Onboarding: 30% (critical for new developers)
- Constraint: 40% (critical for avoiding mistakes)
- Implementation: 20% (nice to have)
- Debugging: 10% (can be figured out)

### Grades

- **A (0.9+)**: Excellent - facts are comprehensive
- **B (0.8-0.9)**: Good - production ready with minor gaps
- **C (0.7-0.8)**: Acceptable - minimum viable completeness
- **D (0.6-0.7)**: Needs work - significant gaps remain
- **F (<0.6)**: Insufficient - major extraction work needed

## Interpreting Results

### High Confidence Answer Example

```
Q: Can I use malloc() directly in C code?
✓ Confidence: 0.95

Supporting Facts:
- fact_28: The MUD uses a custom memory management system - never use raw malloc/free
- fact_29: CREATE(result, type, number) macro MUST be used to allocate memory
- fact_32: Never use raw malloc(), free(), calloc(), realloc(), or str_dup()

Answer: No, you cannot use malloc() directly. The MUD uses a custom memory
management system with macros. Use CREATE() for allocation and DISPOSE() for
deallocation. Raw malloc/free/calloc/realloc are forbidden.
```

This indicates excellent fact coverage for memory management constraints.

### Low Confidence Answer Example

```
Q: Why am I getting memory corruption?
✗ Confidence: 0.62

Supporting Facts:
- fact_28: Custom memory management system
- fact_29: CREATE macro usage

Missing Categories:
- error_handling
- debugging_patterns
- common_pitfalls

Answer: Memory corruption likely occurs from incorrect memory management. You must
use CREATE/DISPOSE macros. However, I cannot provide specific debugging steps or
common causes without more information.
```

This indicates a gap - we have constraints but lack debugging guidance.

## Improving Coverage

### Step 1: Identify Gaps

Look at questions with confidence < 0.7:

```bash
./kraang.py validate-queries | grep "✗"
```

### Step 2: Extract More Facts

Based on missing categories:

```bash
# If missing error_handling:
./kraang.py add docs/ERROR_HANDLING.md
./kraang.py extract artifact_N

# If missing implementation details:
./kraang.py add src/core_module.c
./kraang.py extract artifact_N

# If missing debugging patterns:
./kraang.py add docs/DEBUGGING_GUIDE.md
./kraang.py extract artifact_N
```

### Step 3: Re-validate

```bash
./kraang.py validate-queries
```

Repeat until score >= 0.80 (B grade).

## Viewing Detailed Results

The validation results are saved to `.kraang/validation_results.json`:

```json
{
  "score": {
    "total_questions": 41,
    "high_confidence_count": 37,
    "high_confidence_pct": 0.90,
    "weighted_score": 0.83,
    "overall_grade": "B - Good",
    "by_question_type": {
      "onboarding": 0.91,
      "constraint": 0.94,
      "implementation": 0.79,
      "debugging": 0.68
    }
  },
  "results": [
    {
      "question": "How do I set up my local development environment?",
      "answer": "Use Docker Compose exclusively...",
      "confidence": 0.92,
      "supporting_facts": [
        {
          "id": "fact_2",
          "statement": "Local development MUST use Docker Compose...",
          "type": "constraint"
        }
      ],
      "missing_categories": []
    },
    ...
  ]
}
```

## Custom Question Sets

You can create custom questions for your specific codebase:

```python
# custom_validator.py
from query_validator import QuestionSet, QuestionType, QueryValidator
from kraang import KraangStore, KraangExtractor

# Define custom questions
custom_questions = QuestionSet(
    questions=[
        "How do I add a new API endpoint?",
        "What authentication mechanism is used?",
        "How do I run integration tests?",
    ],
    category=QuestionType.IMPLEMENTATION,
    priority=1
)

# Run validation
store = KraangStore()
validator = QueryValidator(store, KraangExtractor(store))
score = validator.validate_all_questions([custom_questions])
```

## Integration with CI/CD

Add to your CI pipeline:

```bash
#!/bin/bash
# validate-facts.sh

./kraang.py validate-queries

# Parse score from output
SCORE=$(grep "Overall Score:" .kraang/validation_results.json | grep -o "[0-9]\.[0-9]*")

# Fail if below threshold
if (( $(echo "$SCORE < 0.70" | bc -l) )); then
  echo "❌ Fact completeness below threshold: $SCORE"
  exit 1
else
  echo "✅ Fact completeness acceptable: $SCORE"
  exit 0
fi
```

## Question Categories Explained

### 1. Onboarding Questions (Priority: Critical)

**Purpose**: Help new developers get started quickly

**Coverage Target**: 95%+

**Examples**:
- Setup and installation
- Running and testing
- Basic workflows
- Tool usage

**Why Important**: First impression matters. If new devs can't answer these, they'll struggle.

### 2. Constraint Questions (Priority: Critical)

**Purpose**: Prevent developers from making mistakes

**Coverage Target**: 90%+

**Examples**:
- What's forbidden (malloc, header creation)
- What's required (LINK macros, types.h)
- Naming conventions
- Code standards

**Why Important**: Violations cause bugs, crashes, and technical debt.

### 3. Implementation Questions (Priority: Important)

**Purpose**: Help developers understand existing code

**Coverage Target**: 75%+

**Examples**:
- Where things are located
- How systems work
- What macros/functions do
- Architecture patterns

**Why Important**: Enables effective modification and extension.

### 4. Debugging Questions (Priority: Nice-to-Have)

**Purpose**: Help troubleshoot problems

**Coverage Target**: 70%+

**Examples**:
- Why did X fail?
- What causes Y?
- Common pitfalls

**Why Important**: Speeds up problem-solving, but can often be figured out through investigation.

## Best Practices

### 1. Run Early and Often

Run validation after every extraction session to track progress:

```bash
./kraang.py extract artifact_1
./kraang.py validate-queries
```

### 2. Focus on Critical Categories First

Get onboarding and constraint questions to 90%+ before worrying about debugging questions.

### 3. Use Gaps to Guide Extraction

Don't randomly extract files. Let validation tell you what's missing:

```
Missing: error_handling
→ Extract error handling documentation

Missing: testing_patterns
→ Extract test files and testing docs
```

### 4. Track Progress Over Time

Save validation results with timestamps:

```bash
./kraang.py validate-queries
cp .kraang/validation_results.json .kraang/validation_$(date +%Y%m%d).json
```

### 5. Validate After Major Changes

When code changes significantly, re-run validation to ensure facts are still accurate.

## Troubleshooting

### "Module not found" error

```
✗ Query validator module not found
```

**Solution**: Ensure `query_validator.py` is in the same directory as `kraang.py`.

### Low confidence on all questions

```
Overall Score: 0.22 (F - Insufficient)
```

**Solution**: Not enough facts extracted. Extract from key documentation files first:
- README
- Setup guides
- Coding standards
- Core implementation files

### Inconsistent confidence scores

```
LLM: 0.90, Secondary: 0.40 → Final: 0.65
```

**Solution**: LLM is overconfident. The answer may be plausible but lacks supporting facts. Extract more facts in that area.

### Validation takes too long

Each question requires an LLM call, so 41 questions can take 5-10 minutes.

**Solution**: Create a subset of critical questions for quick validation:

```python
# quick_validate.py
critical_questions = QuestionSet(
    questions=[
        "Can I use malloc()?",
        "Must I use types.h?",
        "How do I allocate memory?",
    ],
    category=QuestionType.CONSTRAINT,
    priority=1
)
```

## Advanced Usage

### Compare Different Extractions

```bash
# Baseline
./kraang.py validate-queries
cp .kraang/validation_results.json baseline.json

# After extracting more facts
./kraang.py add src/new_file.c
./kraang.py extract artifact_N
./kraang.py validate-queries
cp .kraang/validation_results.json improved.json

# Compare scores
diff baseline.json improved.json
```

### A/B Test Different Prompts

Test whether different extraction prompts yield better completeness:

```python
# Extract with prompt A
extractor.extraction_prompt = "Extract all constraints..."
facts_a = extractor.extract_facts(artifact)

# Extract with prompt B
extractor.extraction_prompt = "Focus on MUST/MUST NOT rules..."
facts_b = extractor.extract_facts(artifact)

# Validate both
score_a = validator.validate_all_questions(questions)
score_b = validator.validate_all_questions(questions)

# Compare
```

### Generate Question Sets from Issues

Create validation questions from GitHub issues or support tickets:

```python
# Parse issues labeled "documentation" or "onboarding"
issues = github.get_issues(label="documentation")

questions = []
for issue in issues:
    if "how do i" in issue.title.lower():
        questions.append(issue.title)

# Create question set
custom_set = QuestionSet(
    questions=questions,
    category=QuestionType.ONBOARDING,
    priority=1
)

# Validate
validator.validate_all_questions([custom_set])
```

## Success Metrics

### Minimum Viable Completeness

Suitable for personal projects or early development:

- Overall score: >= 0.70 (C)
- Onboarding: >= 80%
- Constraint: >= 80%
- Implementation: >= 60%
- Debugging: >= 50%

### Production-Ready Completeness

Suitable for team projects:

- Overall score: >= 0.85 (B)
- Onboarding: >= 95%
- Constraint: >= 90%
- Implementation: >= 75%
- Debugging: >= 70%

### Gold Standard Completeness

Suitable for open-source or complex projects:

- Overall score: >= 0.90 (A)
- All categories: >= 90%
- Average confidence: >= 0.85

## Conclusion

Query-driven validation provides objective, actionable metrics for fact completeness. By testing whether facts can answer real developer questions, you ensure practical utility rather than abstract coverage.

Use it to:
- Measure extraction progress
- Identify gaps systematically
- Prioritize extraction work
- Validate before releasing documentation
- Track quality over time

For questions or issues, see the main documentation in `QUERY_VALIDATION_SYSTEM.md`.
