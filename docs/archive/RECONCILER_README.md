# Constraint Reconciler

**Mission**: When facts conflict, help merge them into a single truth.

The Constraint Reconciler is a tool that analyzes conflicting constraints in your codebase
and proposes actionable resolutions based on source authority, specificity, context, and
reconciliation strategies.

---

## What It Does

The reconciler:

1. **Identifies Conflicts** - Finds facts that contradict each other
2. **Analyzes Authority** - Determines which source is more authoritative (code vs docs)
3. **Determines Specificity** - Identifies which constraint is more specific
4. **Proposes Strategy** - Selects appropriate reconciliation approach
5. **Generates Action Items** - Produces concrete steps to resolve conflicts

---

## Reconciliation Strategies

The tool uses six primary strategies to resolve conflicts:

### 1. Source Authority (Code)
**When**: Code contradicts documentation
**Action**: Code is truth, update docs
**Confidence**: 0.90

Example: Code uses malloc, docs say never use it → Check actual code

### 2. Source Authority (Docs)
**When**: Documentation is specification
**Action**: Docs are truth, fix code
**Confidence**: 0.80

Example: API spec says must validate input, code doesn't → Fix code

### 3. Temporal
**When**: Newer fact supersedes older
**Action**: Keep newer, deprecate older
**Confidence**: 0.85

Example: New constraint replaces deprecated guideline

### 4. Specificity
**When**: Specific rule vs general guideline
**Action**: Specific wins, general becomes guideline
**Confidence**: 0.85

Example: "Use X for case Y" beats "Usually use Z"

### 5. Synthesis
**When**: Both facts partially true
**Action**: Combine into unified constraint
**Confidence**: 0.75

Example: Two constraints that work together

### 6. Conditional
**When**: Both true in different contexts
**Action**: Document contexts where each applies
**Confidence**: 0.85

Example: "Docker for services" + "localhost:5432 access" → Port mapping

### 7. Escalate
**When**: Too complex for automation
**Action**: Needs human decision
**Confidence**: 0.50

Example: Architectural decision required

---

## Quick Start

### Installation

The reconciler is part of the Kraang system. No installation needed if you have Kraang.

### Basic Usage

```bash
# Find all conflicts
python reconciler.py analyze

# Generate reconciliation proposals
python reconciler.py reconcile

# Create detailed report
python reconciler.py report RECONCILIATION_REPORT.md

# Analyze specific conflict
python reconciler.py conflict fact_16 fact_19
```

### Run Demo

```bash
# Interactive demonstration
python demo_reconciler.py

# Show strategies
python demo_reconciler.py strategies

# Analyze specific conflict
python demo_reconciler.py detail conflict_fact_28_fact_31
```

---

## Example: Memory Management Conflict

### Before (Conflicting Facts)

**Fact 28** (Constraint):
> The MUD uses a custom memory management system - never use raw malloc/free

**Fact 31** (Implementation):
> SET_STRING(pointer, value) macro performs safe string assignment by freeing old and allocating new

**Conflict**: Does SET_STRING violate the malloc/free constraint?

### Analysis

**Type**: Semantic Conflict (Terminology)
**Severity**: CRITICAL
**Confidence**: 0.85

**Investigation**: Checking actual code reveals SET_STRING uses STRFREE/STRALLOC macros,
which ARE part of the custom memory system. The conflict is terminological, not actual.

### After (Reconciled)

**Strategy**: CONDITIONAL (Terminology Clarification)

**Reconciled Statement**:
> Application code must never use raw malloc(), free(). Always use custom macros: CREATE,
> DISPOSE, STRALLOC, STRFREE.
>
> SET_STRING uses STRFREE and STRALLOC (custom memory management), NOT raw free/malloc.
>
> When we say "freeing" and "allocating" in descriptions, we mean the custom memory
> management system unless explicitly stated otherwise.

**Action Items**:
- [ ] Update SET_STRING description to use specific macro names
- [ ] Add glossary distinguishing generic concepts from specific implementations
- [ ] Audit all memory docs for terminology consistency
- [ ] Add static analysis rule to flag raw memory functions

---

## Real-World Results

From LotJ codebase analysis:

- **Conflicts Found**: 5
- **Successfully Reconciled**: 4 (80%)
- **Escalated to Human**: 1 (20%)
- **Severity**: 1 critical, 4 high

**Strategy Distribution**:
- Conditional: 80% (context separation resolved most conflicts)
- Escalate: 20% (architectural decisions needed)

**Root Causes**:
- Terminology confusion: 40%
- Prescriptive vs descriptive documentation: 40%
- Insufficient context: 20%

**Key Insight**: Most "contradictions" are actually context-dependent truths that become
compatible when contexts are clearly documented.

---

## Files Delivered

### Core Implementation
- **reconciler.py** - Main reconciliation engine (900+ lines)
  - ConstraintReconciler class
  - Six reconciliation strategies
  - Conflict analysis
  - Proposal generation
  - Report generation

### Documentation
- **RECONCILIATION_EXAMPLES.md** - Real LotJ examples with detailed analysis
  - 4 fully worked examples
  - Before/after comparisons
  - Action items for each
  - Lessons learned
  - Best practices

- **RECONCILER_README.md** - This file
  - Quick start guide
  - Strategy explanations
  - Usage examples

### Demonstration
- **demo_reconciler.py** - Interactive demonstration
  - Shows conflict analysis
  - Demonstrates strategies
  - Walks through reconciliation
  - Generates action items

---

## Integration with Kraang

The reconciler integrates seamlessly with Kraang:

```bash
# 1. Find contradictions with Kraang
python kraang.py conflicts

# 2. Analyze them with reconciler
python reconciler.py analyze

# 3. Generate proposals
python reconciler.py reconcile

# 4. Create comprehensive report
python reconciler.py report RECONCILIATION_REPORT.md
```

---

## Command Reference

### reconciler.py

```bash
# Analyze all conflicts
python reconciler.py analyze

# Generate reconciliation proposals
python reconciler.py reconcile

# Create full report
python reconciler.py report [output.md]

# Analyze specific conflict
python reconciler.py conflict <fact1> <fact2>
```

### demo_reconciler.py

```bash
# Run full interactive demo
python demo_reconciler.py

# Show conflict analysis
python demo_reconciler.py analyze

# Show available strategies
python demo_reconciler.py strategies

# Show detailed analysis
python demo_reconciler.py detail [conflict_id]

# Show full reconciliation report
python demo_reconciler.py full
```

---

## Architecture

### Core Classes

**ConstraintReconciler**
- Main reconciliation engine
- Analyzes conflicts
- Proposes strategies
- Generates reports

**ConflictAnalysis**
- Represents a conflict
- Contains severity, type, description
- Links to conflicting facts

**ReconciliationProposal**
- Proposed resolution
- Strategy used
- Before/after states
- Action items (code, docs, verification)

**ReconciliationStrategy** (Enum)
- SOURCE_AUTHORITY_CODE
- SOURCE_AUTHORITY_DOCS
- TEMPORAL_NEWER
- SPECIFICITY
- SYNTHESIS
- CONDITIONAL
- ESCALATE

**SourceAuthority** (Enum)
- CODE_IMPLEMENTATION (100)
- TESTS (90)
- API_DOCS (80)
- ARCHITECTURE_DOCS (70)
- DEVELOPER_GUIDE (60)
- COMMENTS (50)
- INFORMAL_DOCS (40)
- UNKNOWN (0)

### Decision Process

```
1. Get Conflicting Facts
   ↓
2. Determine Source Authority
   (code vs docs, tests vs guides)
   ↓
3. Calculate Specificity
   (numbers, names, paths vs general statements)
   ↓
4. Select Strategy
   (authority diff > 20? specificity diff > 30? etc.)
   ↓
5. Generate Reconciliation
   (strategy-specific resolution)
   ↓
6. Create Action Items
   (code changes, doc updates, verification)
```

---

## Best Practices

### For Constraint Authors

1. **Label Your Statements**
   - MUST = absolute requirement
   - SHOULD = strong recommendation
   - CURRENT = description of existing state
   - LEGACY = preserved for consistency

2. **Provide Context**
   - When does this apply?
   - What are exceptions?
   - Why was this decision made?

3. **Use Specific Terms**
   - Name specific functions/macros/services
   - Avoid ambiguous generic terms
   - Link to actual code examples

4. **Document Trade-offs**
   - Why this approach over alternatives?
   - What do we sacrifice?
   - When might this change?

### For Reconcilers

1. **Investigate Before Concluding**
   - Check actual code
   - Review related facts
   - Understand historical context

2. **Consider Multiple Strategies**
   - Not everything is a contradiction
   - Context often resolves conflicts
   - Synthesis can unify partial truths

3. **Escalate Appropriately**
   - Some decisions need human judgment
   - Provide decision framework
   - Don't force automated resolution

4. **Document the Resolution**
   - Explain the reasoning
   - Update all affected facts
   - Verify with code/tests

---

## Lessons Learned from LotJ

### 1. Terminology Needs Precision
**Problem**: Generic terms like "allocate" mean both concepts and specific implementations.

**Solution**: Use specific names (STRALLOC) in descriptions, create glossaries.

### 2. Context Makes Contradictions Compatible
**Problem**: "Never create headers" + "5,830-line header exists" seem to contradict.

**Solution**: Distinguish prescriptive (what to do) from descriptive (what exists).

### 3. Legacy Systems Have Preservation Constraints
**Problem**: Constraints preserve consistency even when suboptimal.

**Solution**: Label preservation rules separately from best practices.

### 4. Infrastructure Needs Topology Documentation
**Problem**: "localhost:5432" unclear without network context.

**Solution**: Include network diagrams, document all access patterns.

### 5. Not Everything Can Be Automated
**Problem**: Some conflicts need architectural decisions.

**Solution**: Recognize when to escalate, provide decision framework.

---

## Extending the Reconciler

### Adding New Strategies

```python
class ReconciliationStrategy(Enum):
    # ... existing strategies ...
    YOUR_STRATEGY = "your_strategy"

# In ConstraintReconciler class:
def _select_strategy(self, fact1, fact2, auth1, auth2, spec1, spec2, conflict):
    # ... existing logic ...
    if your_condition:
        return ReconciliationStrategy.YOUR_STRATEGY

def _generate_reconciliation(self, strategy, fact1, fact2, ...):
    # ... existing strategies ...
    elif strategy == ReconciliationStrategy.YOUR_STRATEGY:
        return self._reconcile_your_way(fact1, fact2, conflict)

def _reconcile_your_way(self, fact1, fact2, conflict):
    return ReconciliationProposal(...)
```

### Custom Authority Levels

```python
class SourceAuthority(Enum):
    # ... existing levels ...
    YOUR_LEVEL = 85  # Between TESTS and API_DOCS

# In _get_source_authority:
if "your_pattern" in path:
    return SourceAuthority.YOUR_LEVEL.value
```

---

## Troubleshooting

### No Conflicts Found

**Issue**: `reconciler.py analyze` returns 0 conflicts

**Solutions**:
1. Check that relationships have been analyzed: `python kraang.py relate`
2. Verify contradictions exist: `python kraang.py conflicts`
3. Ensure facts are loaded: `python kraang.py list facts`

### Low Confidence Proposals

**Issue**: All proposals have confidence < 0.60

**Solutions**:
1. Add more context to fact sources
2. Improve artifact type detection
3. Add specificity markers (numbers, names, paths)

### Incorrect Strategy Selection

**Issue**: Strategy doesn't make sense for conflict

**Solutions**:
1. Review authority calculation in `_get_source_authority`
2. Check specificity calculation in `_get_fact_specificity`
3. Adjust strategy selection thresholds in `_select_strategy`

---

## Future Enhancements

Potential improvements:

1. **Machine Learning**: Train model to recognize conflict patterns
2. **Temporal Analysis**: Use git history to determine fact age
3. **Embedding Similarity**: Use semantic similarity for better conflict detection
4. **Interactive Resolution**: CLI wizard to guide human decisions
5. **Automated Testing**: Generate tests to verify reconciliation
6. **Visualization**: Graph showing conflicts and resolutions
7. **Batch Processing**: Apply reconciliations automatically with approval

---

## Contributing

To contribute to the reconciler:

1. Add test cases in LotJ or other codebases
2. Propose new reconciliation strategies
3. Improve authority/specificity heuristics
4. Add visualization tools
5. Create integration tests

---

## Summary

The Constraint Reconciler successfully:

✓ **Identifies conflicts** - Finds contradicting facts in knowledge base
✓ **Analyzes authority** - Determines source trustworthiness (code vs docs)
✓ **Determines specificity** - Identifies more specific constraints
✓ **Proposes strategies** - Six strategies covering most conflict types
✓ **Generates action items** - Concrete steps for code, docs, verification
✓ **Demonstrates results** - Real LotJ examples with 80% resolution rate

**Key Achievement**: Reconciler understands that "truth" is often context-dependent.
The goal is not eliminating contradictions but making them understandable and actionable.

---

*Built for Kraang - Constraint Rationalization Engine*
