# Requirement Analyzer - Quick Start Guide

## What is it?

A tool that **analyzes proposed requirements against existing constraints** before you write code.

Think of it as: *"Will this new feature conflict with our existing architecture?"*

## 30-Second Demo

```bash
# Run all three demo scenarios
./requirement_analyzer_demo.py all

# Run specific scenario
./requirement_analyzer_demo.py 1    # Can we create new header files?
./requirement_analyzer_demo.py 2    # Can we use malloc()?
./requirement_analyzer_demo.py 3    # Can we skip Docker?
```

## What You Get

```
FEASIBILITY SCORE: 0.15 / 1.00
ASSESSMENT: VERY LOW - Critical conflicts

CONFLICTS: 3 found
  CRITICAL: Violates "DO NOT create new header files"
  HIGH: Conflicts with types.h pattern
  HIGH: Conflicts with functions.h pattern

IMPACT AREAS: 3 files need changes
  - Documentation rewrite required
  - Build system updates needed

RECOMMENDATIONS:
  1. REJECT - violates core architectural constraint
  2. Alternative: Work within existing headers
  3. Alternative: Better organize .c files
```

## The Three Test Scenarios

### Scenario 1: New Header Files ❌ REJECTED

**Question**: Can we create new header files for modularity?

**Result**: Feasibility 0.15/1.00 (VERY LOW)

**Why Rejected**:
- **CRITICAL conflict**: Violates explicit "DO NOT create new headers" policy
- Conflicts with centralized types.h and functions.h pattern
- Would require major policy and documentation changes

**The Constraint** (from LotJ):
```
fact_16: DO NOT create new header files, use existing
         well-established header file structure
Source: /home/budda/Code/LotJ/CLAUDE.md, Line 213
```

**Recommendation**: Work within existing header structure instead.

---

### Scenario 2: Allow malloc() ❌ REJECTED

**Question**: Can we use malloc() for a new memory subsystem?

**Result**: Feasibility 0.25/1.00 (VERY LOW)

**Why Rejected**:
- **CRITICAL conflict**: Violates "Never use raw malloc()" policy
- Breaks CREATE/DISPOSE macro system
- Would lose memory tracking and leak detection

**The Constraints** (from LotJ):
```
fact_32: Never use raw malloc(), free(), calloc(), realloc()
fact_29: CREATE macro MUST be used to allocate memory
fact_30: DISPOSE macro MUST be used to free memory
```

**Recommendation**: Extend CREATE macro or use MALLOC_EXTERNAL wrapper.

---

### Scenario 3: Non-Docker Development ✅ APPROVED (conditionally)

**Question**: Can we support native development without Docker?

**Result**: Feasibility 0.60/1.00 (MODERATE)

**Why Approved**:
- Only **ONE conflict** (Docker-first policy)
- Process policy, not code architecture
- Can coexist as unsupported option
- Doesn't break existing constraints

**The Constraint** (from LotJ):
```
fact_2: Local development MUST use Docker Compose exclusively
Source: /home/budda/Code/LotJ/CLAUDE.md, Lines 7-15
```

**Recommendation**:
- ✅ APPROVE as optional/community-supported path
- Keep Docker as primary supported method
- Document: "Native development - use at your own risk"

---

## Key Insights from Scenarios

| Scenario | Score | Severity | Decision | Why? |
|----------|-------|----------|----------|------|
| New Headers | 0.15 | CRITICAL | ❌ REJECT | Core architecture policy |
| malloc() | 0.25 | CRITICAL | ❌ REJECT | Breaks fundamental system |
| Non-Docker | 0.60 | HIGH | ✅ APPROVE* | Process, not architecture |

**Key Lesson**: Not all constraints are equal. Process policies are more flexible than architectural constraints.

## How It Works

```
Your Requirement
       ↓
    Extract Facts (LLM)
       ↓
    Compare Against 3,234 Existing Facts
       ↓
    ┌─────────┬─────────────┐
    ↓         ↓             ↓
Conflicts  Dependencies  Impact
    ↓         ↓             ↓
    └─────────┴─────────────┘
              ↓
      Feasibility Report
```

## Installation

### Option 1: Demo Only (No API Key)
```bash
chmod +x requirement_analyzer_demo.py
./requirement_analyzer_demo.py all
```

### Option 2: Full System (Requires Anthropic API)
```bash
export ANTHROPIC_API_KEY="your-key-here"
chmod +x requirement_analyzer.py
./requirement_analyzer.py "Your requirement here"
```

## Usage Examples

### Basic Analysis
```bash
./requirement_analyzer.py "Add WebSocket support for real-time updates"
```

### From File
```bash
./requirement_analyzer.py --file feature_requests/FR-2024-042.txt
```

### Save Report
```bash
./requirement_analyzer.py "Add caching layer" \
  --output reports/caching_analysis.json
```

### Faster Analysis (Limited Checks)
```bash
./requirement_analyzer.py "New feature" \
  --max-conflicts 50 \
  --max-dependencies 25
```

### Quiet Mode
```bash
./requirement_analyzer.py "Feature" --quiet
```

## Understanding the Output

### Feasibility Scores

| Score | Meaning | Action |
|-------|---------|--------|
| 0.8 - 1.0 | HIGH | ✅ Proceed with minor adjustments |
| 0.6 - 0.8 | MODERATE | ⚠️ Feasible with planning |
| 0.4 - 0.6 | LOW | ⚠️ Major conflicts, significant effort |
| 0.0 - 0.4 | VERY LOW | ❌ Critical conflicts, likely infeasible |

### Conflict Severity

| Level | Meaning | Example |
|-------|---------|---------|
| **CRITICAL** | Cannot proceed | "Allow new headers" vs "DO NOT create headers" |
| **HIGH** | Major redesign needed | "Use malloc()" vs "MUST use CREATE" |
| **MEDIUM** | Workarounds possible | Design pattern conflicts |
| **LOW** | Easy to resolve | Minor convention differences |
| **INFO** | Just related info | Contextual constraints |

### Impact Areas

Shows what needs to change:
- **REMOVE_OR_MODIFY**: Constraint must be removed/changed
- **MODIFY**: File needs updates
- **ADD**: New files/sections needed

## Programmatic Usage

```python
from requirement_analyzer import RequirementAnalyzer

analyzer = RequirementAnalyzer()

report = analyzer.analyze(
    "Add Redis caching layer",
    max_conflicts_to_check=100,
    verbose=True
)

print(f"Feasibility: {report.feasibility_score:.2f}")
print(f"Conflicts: {len(report.conflicts)}")
print(f"Recommendations: {report.recommendations}")

# Decision logic
if report.feasibility_score < 0.4:
    print("❌ Requirement rejected - critical conflicts")
elif report.feasibility_score < 0.6:
    print("⚠️ Proceed with caution - major work needed")
else:
    print("✅ Feasible - proceed with recommendations")
```

## Integration Examples

### Pre-Commit Hook
```bash
#!/bin/bash
# .git/hooks/pre-commit

if [ -f requirements_update.txt ]; then
    echo "Analyzing requirement changes..."
    ./requirement_analyzer.py --file requirements_update.txt
    echo "Review analysis before committing"
fi
```

### CI/CD Pipeline
```yaml
# .github/workflows/requirements.yml
- name: Analyze Requirements
  run: |
    for req in requirements/new/*.txt; do
      ./requirement_analyzer.py --file $req --output analysis/
    done
- name: Check Feasibility Threshold
  run: python scripts/check_min_feasibility.py 0.6
```

### Issue Template
```markdown
## Proposed Requirement
<!-- Describe the new feature -->

## Automated Analysis
<!-- Will be filled by bot -->
Feasibility: TBD
Conflicts: TBD
Impact: TBD
```

## Common Patterns

### Pattern 1: Architectural Violations
**Symptoms**: Feasibility < 0.3, CRITICAL conflicts
**Example**: New header files, malloc usage
**Action**: Find alternatives within constraints

### Pattern 2: Design Conflicts
**Symptoms**: Feasibility 0.4-0.6, HIGH conflicts
**Example**: New design pattern vs existing patterns
**Action**: Adapt to work with existing design

### Pattern 3: Process Changes
**Symptoms**: Feasibility 0.6-0.8, MEDIUM conflicts
**Example**: Non-Docker development
**Action**: Can coexist as optional approaches

### Pattern 4: Extensions
**Symptoms**: Feasibility > 0.8, LOW conflicts
**Example**: New optional feature, backwards compatible
**Action**: Proceed with standard development

## Files Generated

### Scenario Reports (JSON)
- `scenario1_new_headers.json` - Header file analysis
- `scenario2_malloc.json` - malloc() analysis
- `scenario3_non_docker.json` - Non-Docker analysis

### Report Structure
```json
{
  "requirement": "...",
  "feasibility_score": 0.15,
  "overall_assessment": "VERY LOW",
  "conflicts": [...],
  "dependencies": [...],
  "impact_areas": [...],
  "recommendations": [...]
}
```

## Knowledge Base

The analyzer compares against **3,234 facts** from LotJ:

### Constraint Categories
- **Memory Management**: 11 constraints (CREATE/DISPOSE macros)
- **Header Organization**: 7 constraints (types.h/functions.h)
- **Development Workflow**: 3 constraints (Docker-first)
- **Code Standards**: 4 constraints (naming, warnings)
- **Git/Version Control**: 6 constraints (submodules)
- **System Limits**: 24 constraints (buffers, arrays)
- **And more**: Total 110+ documented constraints

### Top Constraints

1. `fact_16`: DO NOT create new header files
2. `fact_32`: Never use raw malloc()
3. `fact_2`: Docker Compose required
4. `fact_29`: CREATE macro MUST be used
5. `fact_20`: All structs in types.h

## Tips & Tricks

### 1. Start Small
Test with demo scenarios before analyzing real requirements

### 2. Iterate
Use analysis to refine requirements, not just accept/reject

### 3. Document Exceptions
If proceeding despite conflicts, document why

### 4. Team Discussion
Use reports as conversation starters

### 5. Track Over Time
Monitor if constraints are blocking too much innovation

### 6. Update Knowledge
Keep constraint database current as architecture evolves

## Troubleshooting

### "API Key Not Found"
```bash
export ANTHROPIC_API_KEY="sk-..."
```

### "No Conflicts Found" (unexpected)
- Requirement may be too vague
- Try more specific wording
- Increase max_conflicts_to_check

### "Too Many Conflicts" (overwhelming)
- Start with max_conflicts=20 for overview
- Focus on CRITICAL and HIGH only
- Break requirement into smaller pieces

### "Score Seems Wrong"
- Check conflict severities (are they accurate?)
- Review reasoning for each conflict
- Consider that score is heuristic, not absolute

## Next Steps

1. **Run Demo**: `./requirement_analyzer_demo.py all`
2. **Read Full Docs**: `REQUIREMENT_ANALYSIS.md`
3. **Test Real Requirement**: Create your own test case
4. **Integrate**: Add to your development workflow
5. **Iterate**: Use analysis to improve requirements

## Real-World Benefits

### Before This Tool
- Conflicts discovered late (after coding)
- Ad-hoc constraint checking
- Documentation drift
- Unclear feasibility

### After This Tool
- ✅ Conflicts found before coding
- ✅ Systematic analysis
- ✅ Requirements aligned with constraints
- ✅ Clear feasibility scores

## Questions?

**Q: Do I need an API key for the demo?**
A: No, `requirement_analyzer_demo.py` works without API.

**Q: Can I use this on my own codebase?**
A: Yes! Run Kraang to extract constraints, then analyze requirements.

**Q: How accurate is the feasibility score?**
A: It's a heuristic guide, not absolute truth. Use it to inform decisions.

**Q: What if I disagree with a conflict?**
A: The tool shows conflicts; humans decide if they're valid.

**Q: Can constraints be too restrictive?**
A: Yes! If many good ideas score low, constraints may need review.

---

**See Also**:
- `REQUIREMENT_ANALYSIS.md` - Complete documentation
- `requirement_analyzer.py` - Full implementation
- `requirement_analyzer_demo.py` - Demo scenarios
- `LOTJ_CONSTRAINT_CATALOG.md` - All constraints
