# Kraang Rationalization - Quick Start Guide

**Goal**: Run the conflict rationalization demo in under 5 minutes

---

## Prerequisites

- LotJ data extracted (facts.json, relationships.json in .kraang/)
- Python 3.8+
- No API keys needed (uses heuristic analysis)

---

## Quick Run

```bash
# Navigate to kraang
cd /home/budda/Code/kraang

# Run the demo
python3 demo_rationalization.py

# View results
cat rationalization_results.json
```

---

## What You'll Get

### Console Output
- **Phase 1**: Data loading summary
- **Phase 2**: Conflicts detected (5 found)
- **Phase 3**: Impact analysis
- **Phase 4**: Resolution recommendations
- **Phase 5**: Visual reports and action plans

### Files Generated

1. **rationalization_results.json** - Structured data (22KB)
   - Summary statistics
   - All conflicts with details
   - Resolutions with action items

2. **demo_output.txt** - Complete console output (16KB)

3. **RATIONALIZATION_DEMO.md** - Full documentation (23KB)

---

## Key Results at a Glance

### Summary Stats
```
Total Facts: 3,234
Conflicts Found: 5
Critical Priority: 1
High Priority: 2
Medium Priority: 2
Total Technical Debt: 30.1/50
```

### The 5 Conflicts

| ID | Severity | What | Fix Effort |
|----|----------|------|------------|
| conflict_3 | CRITICAL | Memory management inconsistency | Low |
| conflict_1 | HIGH | Monolithic types.h (5,830 lines) | High |
| conflict_2 | HIGH | Monolithic functions.h (2,437 lines) | High |
| conflict_4 | MEDIUM | Docker localhost config | Low |
| conflict_5 | MEDIUM | Docker service naming | Low |

---

## Top Priority: Memory Management

**Issue**: SET_STRING uses malloc/free instead of custom CREATE/DESTROY

**Impact**: 8.5/10 technical debt

**Fix**:
1. Audit SET_STRING macro
2. Replace malloc/free with CREATE/DESTROY
3. Test all usages
4. Update docs

**Effort**: Low | **Risk**: Low

---

## Visual Reports

The demo generates 4 ASCII visualizations:

1. **Conflict Graph** - Shows which facts contradict
2. **Impact Radius** - Visual debt scores with bars
3. **Priority Matrix** - Impact vs effort quadrants
4. **Decision Tree** - Resolution strategies

---

## Understanding the Output

### Priority Levels
- **CRITICAL**: Must fix ASAP (causes bugs/security issues)
- **HIGH**: Should fix soon (impacts maintainability)
- **MEDIUM**: Nice to fix (clarifies design)
- **LOW**: Can defer (minor improvements)

### Resolution Strategies
- **REFACTOR**: Change code to resolve conflict
- **KEEP_FACT1/2**: Accept one, document the other
- **MERGE**: Reconcile both as compatible
- **INVESTIGATE**: Need more information

### Technical Debt Score
- **0-3**: Minor issue, can defer
- **4-6**: Moderate, plan to fix
- **7-10**: Severe, fix soon

---

## Customization

### Run on Different Data

```python
engine = RationalizationEngine(".kraang")  # Change directory
engine.load_data()
conflicts = engine.detect_conflicts()
```

### Add Custom Heuristics

Edit `_heuristic_analysis()` in demo_rationalization.py:

```python
def _heuristic_analysis(self, conflict):
    if "your_pattern" in conflict.reasoning.lower():
        return self._analyze_your_pattern(conflict)
```

---

## Next Steps

1. **Review** RATIONALIZATION_DEMO.md for full details
2. **Examine** rationalization_results.json for raw data
3. **Implement** top priority fixes (start with conflict_3)
4. **Track** technical debt over time
5. **Automate** conflict detection in CI/CD

---

## Integration with Kraang

To add rationalization to the main CLI:

```python
# In kraang.py
def cmd_rationalize(self):
    """Analyze and rationalize conflicting constraints"""
    from demo_rationalization import RationalizationEngine

    engine = RationalizationEngine(self.store.base_dir)
    engine.load_data()
    conflicts = engine.detect_conflicts()

    # Generate resolutions
    for conflict in conflicts:
        analysis = engine.analyze_conflict_impact(conflict)
        resolution = engine.generate_resolution_plan(conflict, analysis)
        print_resolution(resolution)
```

Then use:
```bash
./kraang.py rationalize
```

---

## Files Overview

| File | Size | Purpose |
|------|------|---------|
| demo_rationalization.py | 30KB | Main demo script (750 lines) |
| RATIONALIZATION_DEMO.md | 23KB | Complete documentation (778 lines) |
| rationalization_results.json | 22KB | Structured output data |
| RATIONALIZATION_QUICKSTART.md | This file | Quick reference |

---

## Thesis Validated

> **"The core activity of building software is rationalizing conflicting constraints."**

**Proof**:
- 5 real conflicts found in production codebase
- Concrete resolutions proposed for each
- Actionable implementation plans generated
- Technical debt quantified

**Result**: Kraang successfully rationalizes constraints! ✓

---

**Generated**: 2026-02-10
**Version**: 1.0
