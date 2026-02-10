# Ensuring Completeness of Fact Extraction

## The Challenge

**Problem:** How do we know we've extracted all relevant facts from a codebase?

**Why it's hard:**
1. "All facts" is infinite - every line of code is technically a fact
2. LLMs have attention limitations and may miss things
3. Different granularity levels (high-level constraints vs. implementation details)
4. No ground truth to compare against

## Defining "Complete Enough"

First, we need to define what completeness means:

### Levels of Facts

```
Level 1: Architectural Constraints (MUST capture)
  - Memory management rules
  - Concurrency patterns
  - Security requirements
  - Error handling patterns

Level 2: Module-Level Patterns (SHOULD capture)
  - Function naming conventions
  - Data structure usage
  - API contracts
  - Interface requirements

Level 3: Implementation Details (MAY capture)
  - Specific algorithm choices
  - Edge case handling
  - Performance optimizations
  - Helper function logic

Level 4: Line-by-Line Logic (DON'T capture)
  - Individual variable assignments
  - Loop iterations
  - Trivial calculations
```

**Goal:** Capture Levels 1-2 completely, Level 3 selectively.

## Validation Strategies

### 1. Coverage Analysis

Track which parts of the codebase are referenced by facts:

```python
# Implementation idea
def analyze_coverage(artifacts, facts):
    for artifact in artifacts:
        lines_referenced = set()
        for fact in facts:
            if fact.artifact_id == artifact.id:
                lines_referenced.update(parse_location(fact.location))

        coverage = len(lines_referenced) / artifact.total_lines

        # Flag low-coverage areas
        if coverage < 0.3:  # Less than 30% covered
            print(f"⚠️  Low coverage in {artifact.path}: {coverage:.1%}")
```

**Metrics:**
- Lines referenced by facts vs. total lines
- Functions referenced vs. total functions
- Modules with zero facts extracted
- Constraint types found (memory, concurrency, I/O, etc.)

### 2. Multi-Pass Extraction

Extract facts multiple times with different prompts and compare:

```python
# Pass 1: General extraction
facts_general = extract_facts(artifact, prompt="Extract all constraints")

# Pass 2: Focused extraction
facts_memory = extract_facts(artifact, prompt="Focus on memory management")
facts_concurrency = extract_facts(artifact, prompt="Focus on threading/concurrency")
facts_security = extract_facts(artifact, prompt="Focus on security constraints")

# Pass 3: Question-driven extraction
facts_qa = extract_facts(artifact, prompt="What would a new developer need to know?")

# Compare and merge
all_facts = deduplicate(facts_general + facts_memory + facts_concurrency + facts_security + facts_qa)
```

**Benefits:**
- Different prompts surface different aspects
- Redundancy indicates importance
- Missing categories become obvious

### 3. Cross-Validation with Related Files

Check if facts from one file explain patterns in related files:

```
Example:
1. Extract facts from header file (types.h)
   → Should include struct definitions

2. Extract facts from implementation file (memory.c)
   → Should reference those struct definitions

3. If implementation uses structs not in header facts → INCOMPLETE
```

**Implementation:**
```python
def cross_validate(header_facts, impl_facts):
    # Find structs defined in header
    header_structs = [f.statement for f in header_facts if "struct" in f.statement]

    # Find struct usage in implementation
    impl_struct_refs = [f.statement for f in impl_facts if any(s in f.statement for s in header_structs)]

    # Find orphaned structs (used but not defined in facts)
    orphans = find_undefined_references(impl_facts, header_structs)

    if orphans:
        print(f"⚠️  Missing struct definitions: {orphans}")
```

### 4. Query-Driven Validation

Test if extracted facts can answer key questions:

```python
# Define questions a developer would ask
validation_questions = [
    "How should I allocate memory in this codebase?",
    "What naming conventions should I follow?",
    "Can I create a new header file?",
    "How do I add items to a linked list?",
    "What's the error handling pattern?",
    "Are there security constraints?",
    "What testing is required?",
    "How do I handle concurrency?"
]

for question in validation_questions:
    # Query facts with LLM
    answer = query_facts(facts, question)

    if not answer or answer.confidence < 0.7:
        print(f"⚠️  Cannot answer: {question}")
        print(f"   → Missing fact coverage in this area")
```

### 5. Fact Density Analysis

Track facts-per-file to identify outliers:

```
Typical density:
- Documentation files: 5-15 facts per file
- Header files: 10-30 facts (struct definitions, constants)
- Implementation files: 20-100 facts (depends on size)

Red flags:
- Large file with very few facts (< 5 facts for >500 lines)
- Similar files with very different fact counts
- Zero facts from entire directories
```

### 6. Relationship Saturation

Measure how interconnected facts are:

```
Strong indicator of completeness:
- Most facts have 2+ relationships
- Constraint facts from docs have corresponding implementation facts
- Implementation patterns connect to documented rules

Warning signs:
- Many orphaned facts (no relationships)
- Documentation constraints with no implementation facts
- Implementation facts that contradict documentation (should find these!)
```

### 7. Human Sampling

Randomly sample code sections and check coverage:

```python
def human_validation_sample():
    # Pick 10 random files
    sample_files = random.sample(all_files, 10)

    for file in sample_files:
        # Pick 5 random functions
        functions = extract_functions(file)
        sample_funcs = random.sample(functions, min(5, len(functions)))

        for func in sample_funcs:
            print(f"\nFunction: {func.name} in {file}")
            print(f"Facts referencing this function: ")

            related_facts = [f for f in facts if func.name in f.location or func.name in f.statement]

            if not related_facts:
                print(f"  ⚠️  NO FACTS - Is this function important? Should it be extracted?")
            else:
                for f in related_facts:
                    print(f"  ✓ {f.statement[:80]}...")

            # Ask human
            response = input("Is coverage adequate? (y/n/skip): ")
            if response == 'n':
                print("  → Manual extraction needed")
```

### 8. Differential Analysis

Compare against similar projects:

```
If analyzing a MUD codebase:
1. Extract facts from LotJ
2. Extract facts from another MUD codebase
3. Compare constraint categories:
   - Both should have: memory management, networking, game logic
   - If one has security constraints but other doesn't → investigate

This helps identify "expected" constraint types.
```

### 9. Constraint Type Checklist

Define expected constraint categories for your domain:

```yaml
expected_constraints:
  memory_management:
    - allocation patterns
    - deallocation patterns
    - ownership rules

  concurrency:
    - locking patterns
    - thread safety
    - race condition prevention

  security:
    - input validation
    - authentication
    - authorization

  error_handling:
    - error propagation
    - cleanup on failure
    - invariant preservation

  performance:
    - caching policies
    - algorithmic complexity constraints
    - resource limits

  testing:
    - required test coverage
    - testing patterns
    - mocking strategies

# After extraction, check:
coverage_report = check_constraint_categories(facts, expected_constraints)
# Reports which categories have no facts extracted
```

## Practical Completeness Metrics

### Metric 1: Question Coverage Score

```
Score = (Questions Answered / Total Questions) * 100

Questions Answered = queries that return confident answers (>0.7)
Total Questions = validation_questions from domain experts

Target: >80% for production use
```

### Metric 2: Relationship Density

```
Density = Total Relationships / Total Facts

Good: 0.5+ (each fact related to at least 1 other on average)
Warning: <0.3 (many isolated facts)
Critical: <0.1 (facts not connected to constraints)
```

### Metric 3: Constraint Implementation Coverage

```
Coverage = Implementation Facts / Constraint Facts

Good: >0.8 (most constraints have implementation facts)
Warning: <0.5 (many undocumented constraints or unimplemented docs)
```

### Metric 4: Code Coverage

```
Coverage = Lines Referenced in Facts / Total Lines

Documentation: 50-80% (not every line matters)
Headers: 70-90% (most definitions should be captured)
Implementation: 30-60% (capture patterns, not every detail)
```

## Recommended Completeness Workflow

### Initial Extraction
1. Extract facts from all artifacts
2. Calculate baseline metrics
3. Identify low-coverage areas

### Multi-Pass Enrichment
4. Run focused extraction on low-coverage areas
5. Run domain-specific prompts (memory, security, etc.)
6. Cross-validate related files

### Validation
7. Run query-driven validation
8. Human sampling of 10-20 random code sections
9. Check constraint type checklist

### Iteration
10. If metrics below target, extract more
11. If human sampling finds gaps, re-prompt those areas
12. If queries can't be answered, identify missing fact types

### Acceptance Criteria

Consider extraction "complete enough" when:
- ✅ Question coverage >80%
- ✅ Relationship density >0.5
- ✅ Constraint-implementation coverage >0.7
- ✅ Human sampling approval >90%
- ✅ All expected constraint categories have facts
- ✅ No large files with zero facts
- ✅ Cross-validation passes (related files reference same concepts)

## Diminishing Returns

Important: **Perfect completeness is impossible and not necessary.**

Watch for diminishing returns:
- Adding 10th file finds 5 new facts → keep going
- Adding 50th file finds 0 new constraint types → probably complete enough
- Re-extraction of same file with different prompt finds nothing new → saturated

## Future: Active Learning

For production system, implement active learning:

```python
while not is_complete_enough(metrics):
    # Identify gaps
    gaps = find_coverage_gaps(facts, codebase)

    # Prioritize gaps by importance
    critical_gaps = [g for g in gaps if g.importance > 0.8]

    # Targeted extraction
    for gap in critical_gaps:
        new_facts = extract_facts(gap.artifact,
                                  prompt=f"Focus on {gap.category}")
        facts.extend(new_facts)

    # Re-evaluate
    metrics = calculate_metrics(facts, codebase)
```

## Conclusion

**You'll never have "all" facts, but you can have "enough" facts.**

Key insight: Completeness is domain-specific and use-case-specific.

For constraint validation (Kraang's purpose):
- Level 1 constraints: MUST be 100% complete
- Level 2 patterns: SHOULD be 80%+ complete
- Level 3 details: Can be sparse, extracted on-demand

**Practical answer:** You're "complete enough" when:
1. You can answer the questions developers actually ask
2. You can detect violations of documented constraints
3. Impact analysis returns useful information
4. Relationships form a connected graph (not many orphans)

The validation strategies above help you measure and achieve this.
