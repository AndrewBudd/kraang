# Query-Driven Validation System - Quick Reference

## TL;DR

Test if your extracted facts are "complete enough" by checking if they can answer typical developer questions.

```bash
./kraang.py validate-queries
```

## The Problem

How do you know when you've extracted enough facts? Traditional metrics (lines covered, file count) don't tell you if facts are actually useful.

## The Solution

**Query-driven validation**: Test whether facts can answer questions developers actually ask.

## How It Works

1. **Define Question Taxonomy** - 4 categories of developer questions:
   - Onboarding ("How do I...")
   - Constraint ("Can I...", "Must I...")
   - Implementation ("Where is...", "How does...")
   - Debugging ("Why did...", "What causes...")

2. **Create Question Sets** - 41 specific questions for LotJ MUD codebase

3. **Query with LLM** - For each question:
   - Send question + facts to Claude
   - Get answer + confidence score
   - Identify missing fact categories

4. **Calculate Completeness** - Weighted score across categories:
   - Onboarding: 30% (critical)
   - Constraint: 40% (critical)
   - Implementation: 20% (important)
   - Debugging: 10% (nice-to-have)

## Quick Start

```bash
# After extracting facts
./kraang.py validate-queries

# Output shows:
# - 41 question results with confidence scores
# - Overall completeness score (0.0-1.0)
# - Letter grade (A-F)
# - Missing fact categories
# - Specific recommendations
```

## Example Question Set (LotJ MUD)

### Onboarding (9 questions)
- "How do I set up my local development environment?"
- "How do I start the MUD server for testing?"
- "What are the default test credentials?"
- ...

### Constraint (12 questions)
- "Can I use malloc() directly in C code?"
- "Must I place new structs in types.h?"
- "Must I use the LINK/UNLINK macros?"
- ...

### Implementation (12 questions)
- "Where are the core header files?"
- "How does the memory management system work?"
- "Where are server logs stored?"
- ...

### Debugging (8 questions)
- "Why did my build fail with warnings?"
- "Why am I getting memory corruption?"
- "Why is my linked list code crashing?"
- ...

## Acceptance Criteria

### Minimum Viable (C grade, 0.70)
- Onboarding: 80%+ questions answered confidently
- Constraint: 80%+ questions answered confidently
- Implementation: 60%+ questions answered confidently
- Debugging: 50%+ questions answered confidently

### Production Ready (B grade, 0.85)
- Onboarding: 95%+
- Constraint: 90%+
- Implementation: 75%+
- Debugging: 70%+

### Gold Standard (A grade, 0.90)
- All categories: 90%+ with average confidence >= 0.85

## Key Features

### 1. Dual Confidence Scoring
- **Primary**: LLM self-assessment
- **Secondary**: Fact coverage analysis (# facts, answer length, fact quality)
- **Final**: Average of both

Prevents overconfident answers from sparse facts.

### 2. Gap Analysis
When confidence < 0.7, system identifies:
- Question type
- Expected vs available fact types
- Missing categories (e.g., "error_handling", "testing_patterns")
- Specific extraction recommendations

### 3. Iterative Improvement
```bash
# 1. Validate
./kraang.py validate-queries

# 2. See gaps (e.g., "missing: error_handling")
# 3. Extract more facts
./kraang.py add docs/ERROR_HANDLING.md
./kraang.py extract artifact_N

# 4. Re-validate
./kraang.py validate-queries

# 5. Repeat until score >= 0.80
```

## Implementation

### Core Algorithm
```python
def validate_question(question, facts, relationships):
    # 1. Build prompt with question + facts
    prompt = build_prompt(question, facts, relationships)

    # 2. Query LLM
    response = llm.query(prompt)

    # 3. Parse structured response
    answer = response["answer"]
    llm_confidence = response["confidence"]
    supporting_facts = response["supporting_facts"]
    missing_info = response["missing_info"]

    # 4. Calculate secondary confidence
    secondary = score_coverage(answer, supporting_facts, facts)

    # 5. Average confidences
    final_confidence = (llm_confidence + secondary) / 2

    # 6. Gap analysis if low confidence
    if final_confidence < 0.7:
        gaps = analyze_gaps(question, supporting_facts, missing_info)

    return ValidationResult(
        question, answer, final_confidence, gaps
    )
```

### Main Components

1. **QuestionType Enum** - Taxonomy categories
2. **ValidationResult** - Per-question results
3. **GapAnalysis** - Missing fact analysis
4. **CompletenessScore** - Overall metrics
5. **QueryValidator** - Main validation engine

## Files Created

1. **QUERY_VALIDATION_SYSTEM.md** - Complete design document
   - Full taxonomy definition
   - 41 LotJ example questions
   - Detailed algorithm with pseudocode
   - Acceptance criteria
   - Implementation plan

2. **query_validator.py** - Full Python implementation
   - All data classes
   - Complete validation algorithm
   - Gap analysis logic
   - CLI integration
   - LotJ question sets

3. **QUERY_VALIDATION_EXAMPLE.md** - Usage guide
   - Quick start tutorial
   - Example output
   - Score interpretation
   - Troubleshooting
   - Best practices
   - Advanced usage

## Usage in Kraang

```bash
# New command added
./kraang.py validate-queries

# Integrated with completeness command
./kraang.py completeness
# → Suggests: "Try 'kraang validate-queries' for query-driven testing"

# Results saved to
.kraang/validation_results.json
```

## Why This Approach Works

### Objective Measurement
- Clear numeric scores (0.0-1.0)
- Letter grades (A-F)
- Specific thresholds (>0.7 = good)

### Practical Focus
- Tests real developer needs
- Prioritizes critical questions (constraints > debugging)
- Validates utility, not just coverage

### Actionable Feedback
- Identifies specific gaps ("missing: error_handling")
- Recommends what to extract next
- Shows which questions fail

### Continuous Improvement
- Run after every extraction
- Track progress over time
- Iterate until acceptable score

### Flexible
- Works with any codebase
- Custom question sets supported
- Adjustable thresholds

## Advantages Over Traditional Metrics

| Traditional | Query-Driven |
|-------------|--------------|
| Lines covered | Questions answered |
| Files extracted | Developer needs met |
| Abstract percentage | Confidence score |
| "80% of lines" | "Can answer 'How do I...?'" |
| Hard to interpret | Clear pass/fail |

## Integration Points

### With Completeness Analysis
```bash
./kraang.py completeness
# Shows fact counts, density, coverage

./kraang.py validate-queries
# Shows practical utility via questions
```

### With CI/CD
```bash
# Fail build if completeness < 0.70
./kraang.py validate-queries || exit 1
```

### With Documentation Generation
```python
# Generate FAQ from high-confidence Q&A
results = validator.validate_all_questions(questions)
faq = [r for r in results if r.confidence >= 0.8]
write_faq_doc(faq)
```

## Limitations

1. **Time**: 41 questions × LLM calls = 5-10 minutes
2. **Cost**: Each validation costs ~$0.10-0.50 in API fees
3. **LLM-dependent**: Requires Claude API access
4. **Question quality**: Only as good as your question set

## Future Extensions

### 1. Active Learning
Use low-confidence questions to guide extraction:
```python
gaps = find_gaps(validation_results)
suggested_files = map_gaps_to_files(gaps, codebase)
# → "Extract src/error.c to answer debugging questions"
```

### 2. Custom Question Sets
```python
# Load questions from YAML
questions = load_questions("custom_questions.yaml")
validator.validate_all_questions(questions)
```

### 3. Regression Testing
```python
# Track scores over time
baseline = load_score("baseline.json")
current = validator.validate_all_questions(questions)
alert_if_degraded(baseline, current)
```

### 4. Interactive Query
```bash
./kraang.py query "How do I add a new command?"
# Uses validation system for ad-hoc questions
```

## Success Story (Hypothetical)

```
Day 1: Extract from README
→ Score: 0.42 (F) - Can't answer most questions

Day 2: Extract from setup docs, coding standards
→ Score: 0.68 (D) - Onboarding ok, constraints weak

Day 3: Extract from header files, core C files
→ Score: 0.78 (C) - Most questions answered

Day 4: Extract from error handling docs, debugging guides
→ Score: 0.86 (B) - Production ready!

Day 5: Extract from advanced implementation files
→ Score: 0.92 (A) - Comprehensive coverage!
```

## When to Use

**Use query-driven validation when:**
- You need objective completeness metrics
- You want to prioritize extraction work
- You're building documentation for a team
- You want to track quality over time
- You need to justify "we're done extracting"

**Don't use when:**
- Codebase is tiny (<5 files)
- No typical questions exist
- API costs are prohibitive
- You need instant feedback (use basic completeness instead)

## Bottom Line

**Query-driven validation answers the critical question:**

> "Are my extracted facts useful enough to help developers?"

Not just "Do I have lots of facts?" but "Can developers actually use them?"

## Next Steps

1. **Read full design**: See `QUERY_VALIDATION_SYSTEM.md`
2. **Try it out**: Run `./kraang.py validate-queries`
3. **Customize**: Create your own question sets
4. **Integrate**: Add to your workflow/CI

## Questions?

- **"How long does it take?"** - 5-10 minutes for 41 questions
- **"What's a good score?"** - 0.70+ minimum, 0.85+ for production
- **"Can I customize questions?"** - Yes, see `query_validator.py`
- **"Does it work for non-C code?"** - Yes, questions are generic
- **"How accurate is it?"** - Confidence scores are conservative
- **"What if it's wrong?"** - Check supporting facts, may need more extraction

---

**Key Takeaway**: Facts are complete enough when they can confidently answer the questions developers actually ask.
