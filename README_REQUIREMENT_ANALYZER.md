# Requirement Analyzer

## What Is It?

A tool that **analyzes proposed requirements against existing constraints** before you write code.

**Input**: "Add ability to create new header files"  
**Output**: Feasibility 0.15/1.00, 3 conflicts (1 CRITICAL), REJECT with alternatives

## Quick Demo (30 seconds)

```bash
./requirement_analyzer_demo.py all
```

## What You Get

```
FEASIBILITY SCORE: 0.15 / 1.00
ASSESSMENT: VERY LOW

CONFLICTS: 3 found
  CRITICAL: Violates "DO NOT create new header files" (fact_16)
  HIGH: Conflicts with types.h pattern (fact_20)
  HIGH: Conflicts with functions.h pattern (fact_22)

IMPACT: 3 areas need changes
  - /home/budda/Code/LotJ/CLAUDE.md (remove constraint)
  - Makefile (track dependencies)
  - docs/ (rewrite guidelines)

RECOMMENDATIONS:
  1. REJECT - violates core architectural principle
  2. Alternative: Work within existing headers
  3. Alternative: Better organize .c files
```

## Files

| File | Purpose | Size | Status |
|------|---------|------|--------|
| `requirement_analyzer.py` | Core implementation | 25 KB | ✅ Complete |
| `requirement_analyzer_demo.py` | Demo (no API) | 17 KB | ✅ Working |
| `test_requirement_analyzer.py` | Test suite | 14 KB | ✅ 43/43 pass |
| `REQUIREMENT_ANALYSIS.md` | Full docs | 20 KB | ✅ Complete |
| `REQUIREMENT_ANALYZER_QUICKSTART.md` | Quick start | 12 KB | ✅ Complete |
| `REQUIREMENT_ANALYZER_DELIVERABLES.md` | Summary | 15 KB | ✅ Complete |
| `scenario*.json` | Analysis reports | 14 KB | ✅ 3 scenarios |
| `EXAMPLE_ANALYSIS_REPORT.txt` | Sample output | 4 KB | ✅ Complete |

**Total**: 9 files, ~121 KB

## Three Real Test Scenarios from LotJ

### 1. New Header Files ❌ REJECTED (0.15)
**Question**: Can we create new header files?  
**Answer**: No - violates fact_16 "DO NOT create new header files"  
**Why**: Core architectural principle for consistency

### 2. Allow malloc() ❌ REJECTED (0.25)
**Question**: Can we use malloc() for performance?  
**Answer**: No - violates fact_32 "Never use raw malloc()"  
**Why**: Breaks memory tracking and debugging system

### 3. Non-Docker Development ✅ APPROVED (0.60)
**Question**: Can we support native development?  
**Answer**: Yes (as optional) - only process policy conflict  
**Why**: Can coexist without breaking architecture

## Key Insight

**Not all constraints are equal**:
- Architecture constraints (headers, malloc) → ❌ Rigid
- Process constraints (Docker-first) → ⚠️ Flexible

## How It Works

```
Requirement → Extract Facts → Compare vs 3,234 Facts → Find Conflicts → Calculate Score → Report
```

## Knowledge Base

- **3,234 facts** from LotJ codebase
- **110 documented constraints** across 12 categories
- Includes: memory management, headers, workflow, standards, git, limits

## Usage

### Demo (No API Key)
```bash
./requirement_analyzer_demo.py all          # All scenarios
./requirement_analyzer_demo.py 1            # Scenario 1
./requirement_analyzer_demo.py 2 -o out.json
```

### Full System (With Anthropic API)
```bash
export ANTHROPIC_API_KEY="..."
./requirement_analyzer.py "Add feature X"
./requirement_analyzer.py --file req.txt --output report.json
```

### Run Tests
```bash
./test_requirement_analyzer.py
# Expected: Total: 43, Passed: 43, Failed: 0
```

## Feasibility Scores

| Score | Meaning | Action |
|-------|---------|--------|
| 0.8-1.0 | HIGH | ✅ Proceed |
| 0.6-0.8 | MODERATE | ⚠️ Plan carefully |
| 0.4-0.6 | LOW | ⚠️ Major work |
| 0.0-0.4 | VERY LOW | ❌ Likely reject |

## Conflict Severity

- **CRITICAL**: Cannot proceed without removing constraint
- **HIGH**: Major redesign needed
- **MEDIUM**: Workarounds possible
- **LOW**: Easy to resolve
- **INFO**: Just related information

## Benefits

1. ✅ Find conflicts **before** coding
2. ✅ Understand **full impact**
3. ✅ Get **alternatives** automatically
4. ✅ Ensure **policy alignment**
5. ✅ **Quantified** feasibility

## Real Results

```
Scenario               Score   Decision    Reason
─────────────────────  ──────  ──────────  ──────────────────────
New Header Files       0.15    ❌ REJECT   Architecture violation
Allow malloc()         0.25    ❌ REJECT   Core system violation  
Non-Docker Dev         0.60    ✅ APPROVE  Process policy only
```

## Documentation

- **REQUIREMENT_ANALYZER_QUICKSTART.md** - Start here (10 min read)
- **REQUIREMENT_ANALYSIS.md** - Complete documentation (30 min)
- **REQUIREMENT_ANALYZER_DELIVERABLES.md** - Summary of everything
- **EXAMPLE_ANALYSIS_REPORT.txt** - Sample output

## Next Steps

1. **Try demo**: `./requirement_analyzer_demo.py all`
2. **Read quickstart**: Open `REQUIREMENT_ANALYZER_QUICKSTART.md`
3. **Run tests**: `./test_requirement_analyzer.py`
4. **Test real requirement**: `./requirement_analyzer.py "Your idea"`

## Status

✅ **COMPLETE** - All features implemented, tested, and documented

- Implementation: Complete
- Demo: Working without API
- Tests: 43/43 passing
- Documentation: Complete with examples
- Real scenarios: 3 tested with LotJ constraints

---

**Built for**: Kraang Constraint Rationalization Engine  
**Purpose**: Rationalize new requirements against existing constraints  
**Method**: LLM-powered fact extraction + systematic conflict analysis  
**Result**: Data-driven feasibility decisions before coding begins
