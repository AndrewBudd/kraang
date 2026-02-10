# Requirement Analysis System

## Overview

The Requirement Analyzer is a tool that **rationalizes proposed NEW requirements against existing constraints**. Before adding a feature, it automatically shows what constraints it conflicts with, what code needs to change, and whether the requirement is feasible.

### The Problem

When building software, new requirements often conflict with existing constraints:
- "Let's create new header files!" → Conflicts with architectural policy
- "Let's use malloc() for performance!" → Breaks memory tracking system
- "Let's support native development!" → Contradicts Docker-first workflow

Without systematic analysis, these conflicts are discovered late, after code is written.

### The Solution

The Requirement Analyzer performs automated feasibility analysis:

1. **Extract Facts** - Parse the proposed requirement into discrete facts
2. **Compare Against Knowledge** - Check all 3,234 existing constraints in LotJ
3. **Identify Conflicts** - Find contradictions with different severity levels
4. **Map Dependencies** - Show what existing systems are affected
5. **Calculate Feasibility** - Generate a 0-1 score based on conflicts
6. **Provide Recommendations** - Suggest alternatives or modifications

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Proposed Requirement                          │
│  "Add ability to create new header files for modularity"        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │  LLM Fact Extraction  │
              └──────────┬───────────┘
                         │
                         ▼
         ┌───────────────────────────────┐
         │   Extracted Requirement Facts  │
         │  - "Allow new header files"    │
         │  - "Improve organization"      │
         │  - "Need modularity"           │
         └───────────┬───────────────────┘
                     │
                     ▼
    ┌────────────────────────────────────────────┐
    │  Compare Against Existing Knowledge Base   │
    │         (3,234 facts from LotJ)            │
    └────────┬───────────────────────────────────┘
             │
             ├──────────────┐
             │              │
             ▼              ▼
    ┌────────────┐   ┌──────────────┐
    │ Conflicts  │   │ Dependencies │
    └─────┬──────┘   └──────┬───────┘
          │                 │
          └────────┬────────┘
                   │
                   ▼
         ┌─────────────────────┐
         │   Impact Analysis   │
         │  - What must change │
         │  - Feasibility score│
         │  - Recommendations  │
         └─────────────────────┘
```

## Components

### 1. RequirementAnalyzer (`requirement_analyzer.py`)

**Full implementation** with LLM integration:
- Extracts facts from natural language requirements
- Compares against existing knowledge base
- Identifies conflicts with severity levels
- Generates comprehensive feasibility reports
- **Requires**: Anthropic API key

```python
from requirement_analyzer import RequirementAnalyzer

analyzer = RequirementAnalyzer()
report = analyzer.analyze(
    "Add ability to create new header files",
    max_conflicts_to_check=100
)
```

### 2. Demo Version (`requirement_analyzer_demo.py`)

**Pre-computed scenarios** demonstrating the system without API calls:
- Scenario 1: New header files
- Scenario 2: Allow malloc()
- Scenario 3: Non-Docker development

```bash
# Run all scenarios
./requirement_analyzer_demo.py all

# Run specific scenario
./requirement_analyzer_demo.py 1    # New headers
./requirement_analyzer_demo.py 2    # malloc()
./requirement_analyzer_demo.py 3    # Non-Docker
```

## Real Examples from LotJ

### Example 1: New Header Files (REJECTED)

**Requirement**: "Add ability to create new header files for better code organization and modularity"

**Feasibility Score**: 0.15 / 1.00 (VERY LOW)

**Conflicts Found**: 3
- **CRITICAL**: Direct contradiction with `fact_16` - "DO NOT create new header files"
- **HIGH**: Conflicts with centralized struct pattern (`types.h`)
- **HIGH**: Conflicts with centralized function pattern (`functions.h`)

**Source of Constraints**:
- `/home/budda/Code/LotJ/CLAUDE.md` (Line 213): Explicit policy against new headers
- Established architectural pattern for maintainability

**Impact Areas**:
1. Documentation needs major rewrite
2. Build system needs header dependency tracking
3. Policy change required

**Recommendations**:
- ✗ **REJECT** - Violates core architectural principle
- ✓ **Alternative**: Work within existing header structure
- ✓ **Alternative**: Better organize code within .c files
- ✓ **If critical**: Get architectural approval first

**Why This Constraint Exists**:
- Prevents header proliferation
- Ensures consistent organization
- Simplifies dependency management
- Easier onboarding for new developers

---

### Example 2: Allow malloc() (REJECTED)

**Requirement**: "Allow malloc() in new memory subsystem for performance optimization and compatibility with external libraries"

**Feasibility Score**: 0.25 / 1.00 (VERY LOW)

**Conflicts Found**: 3
- **CRITICAL**: `fact_32` - "Never use raw malloc(), free(), calloc(), realloc()"
- **HIGH**: `fact_29` - "CREATE macro MUST be used for allocation"
- **HIGH**: `fact_30` - "DISPOSE macro MUST be used for freeing"

**Source of Constraints**:
- `/home/budda/Code/LotJ/CLAUDE.md` (Lines 264-279): Memory management section
- Custom memory tracking and debugging system

**Impact Areas**:
1. Memory tracking system (`src/memory.c`)
2. Debug infrastructure (`src/debug.c`)
3. Core macros (`src/mud.h`)
4. Memory leak detection would break

**Recommendations**:
- ✗ **REJECT** - Breaks fundamental architecture
- ✓ **Alternative**: Extend CREATE macro for performance
- ✓ **Alternative**: Create `MALLOC_EXTERNAL` for libraries only
- ✓ **Alternative**: Wrap library calls to use CREATE internally
- ⚠ **If approved**: Strict isolation + maintain tracking

**Why This Constraint Exists**:
- Memory leak detection
- Automatic NULL-setting after free
- Debug tracing capabilities
- Consistent memory management

---

### Example 3: Non-Docker Development (APPROVED with conditions)

**Requirement**: "Support non-Docker local development for developers who prefer native tooling and faster iteration cycles"

**Feasibility Score**: 0.60 / 1.00 (MODERATE)

**Conflicts Found**: 1
- **HIGH**: `fact_2` - "Local development MUST use Docker Compose exclusively"

**Source of Constraints**:
- `/home/budda/Code/LotJ/CLAUDE.md` (Lines 7-15): Docker-First Development
- Process policy, not architectural constraint

**Dependencies Found**: 1
- **EXTENDS**: Would extend build system to support both methods

**Impact Areas**:
1. Documentation updates
2. Makefile targets for native builds
3. CI/CD test matrix expansion
4. Native dependency documentation

**Recommendations**:
- ✓ **APPROVE** - As optional/unsupported path
- ✓ Keep Docker as PRIMARY and SUPPORTED method
- ✓ Mark native as COMMUNITY-SUPPORTED
- ✓ Clear documentation: "Use at your own risk"
- ✓ No guarantee of native build stability

**Why More Feasible**:
- Process policy, not code architecture
- Doesn't break existing constraints
- Adds optional path without removing primary
- No code changes required (just documentation + build targets)

---

## Conflict Severity Levels

### CRITICAL
**Impact**: Cannot proceed without removing constraint
**Example**: "Allow new headers" vs "DO NOT create new headers"
**Action**: REJECT or require architectural policy change

### HIGH
**Impact**: Major conflict, significant redesign needed
**Example**: "Use malloc()" vs "MUST use CREATE macro"
**Action**: Find alternatives or extensive refactoring

### MEDIUM
**Impact**: Moderate conflict, workarounds possible
**Example**: New feature vs existing design pattern
**Action**: Adapt design to work within constraints

### LOW
**Impact**: Minor conflict, easy to resolve
**Example**: Naming convention differences
**Action**: Simple code adjustments

### INFO
**Impact**: Not a conflict, just related information
**Example**: Related constraint that provides context
**Action**: Be aware during implementation

## Feasibility Scoring

Score calculation (0.0 to 1.0):

```
Starting score: 1.0

For each CRITICAL conflict:  -0.30 * confidence
For each HIGH conflict:      -0.20 * confidence
For each MEDIUM conflict:    -0.10 * confidence
For each LOW conflict:       -0.05 * confidence

If dependencies > 10:        -0.10
If dependencies > 20:        -0.20
If impact_areas > 5:         -0.05
If impact_areas > 10:        -0.10

Final score: max(0.0, min(1.0, score))
```

**Score Interpretation**:
- **0.8 - 1.0**: HIGH - Feasible with minor conflicts
- **0.6 - 0.8**: MODERATE - Feasible with careful planning
- **0.4 - 0.6**: LOW - Significant conflicts, major effort
- **0.0 - 0.4**: VERY LOW - Critical conflicts or infeasible

## Usage

### Basic Usage

```bash
# Analyze a requirement
./requirement_analyzer.py "Add real-time notifications system"

# Limit checks for faster analysis
./requirement_analyzer.py "Add new feature" \
  --max-conflicts 50 \
  --max-dependencies 25

# Save report to JSON
./requirement_analyzer.py "Add feature" \
  --output analysis_report.json

# Read requirement from file
./requirement_analyzer.py --file requirements/new_feature.txt
```

### Programmatic Usage

```python
from requirement_analyzer import RequirementAnalyzer
from kraang import KraangStore

# Initialize
store = KraangStore()
analyzer = RequirementAnalyzer(store)

# Analyze requirement
requirement = """
Add a new caching layer using Redis for session management
and query result caching to improve performance.
"""

report = analyzer.analyze(
    requirement,
    max_conflicts_to_check=100,
    max_dependencies_to_check=50,
    verbose=True
)

# Access results
print(f"Feasibility: {report.feasibility_score:.2f}")
print(f"Assessment: {report.overall_assessment}")

for conflict in report.conflicts:
    print(f"Conflict: {conflict.reasoning}")
    print(f"Severity: {conflict.severity.value}")

for recommendation in report.recommendations:
    print(f"- {recommendation}")
```

### Integration with Development Workflow

```bash
# Pre-planning phase
./requirement_analyzer.py --file feature_requests/FR-2024-042.txt \
  --output analysis/FR-2024-042-analysis.json

# Review analysis before starting implementation
# If feasibility < 0.6, discuss with team before proceeding
```

## Report Structure

A complete feasibility report includes:

1. **Requirement**: Original proposed requirement text
2. **Extracted Facts**: Facts parsed from the requirement
3. **Conflicts**: Contradictions with existing constraints
4. **Dependencies**: Related existing facts
5. **Impact Areas**: Code/docs that need changes
6. **Feasibility Score**: 0-1 numerical score
7. **Assessment**: HIGH/MODERATE/LOW/VERY LOW
8. **Recommendations**: Actionable next steps

### Sample Report Output

```
================================================================================
REQUIREMENT FEASIBILITY ANALYSIS
================================================================================

PROPOSED REQUIREMENT:
  Add ability to create new header files for better code organization

FEASIBILITY SCORE: 0.15 / 1.00
ASSESSMENT: VERY LOW - Critical constraint violation makes this infeasible

--------------------------------------------------------------------------------
EXTRACTED FACTS FROM REQUIREMENT
--------------------------------------------------------------------------------
Found 4 facts in proposed requirement:

1. [requirement] System should allow developers to create new header files
   Confidence: 1.00

2. [design] Code organization would benefit from additional header files
   Confidence: 0.90

--------------------------------------------------------------------------------
CONFLICTS WITH EXISTING CONSTRAINTS
--------------------------------------------------------------------------------

CRITICAL SEVERITY (1 conflicts):

  Requirement: System should allow developers to create new header files
  Conflicts with [fact_16]: DO NOT create new header files
  Reasoning: Direct contradiction - cannot proceed without policy change
  Confidence: 1.00
  Source: /home/budda/Code/LotJ/CLAUDE.md (Line 213)

--------------------------------------------------------------------------------
RECOMMENDATIONS
--------------------------------------------------------------------------------

1. CRITICAL: This requirement directly violates documented constraint
2. Alternative: Work within existing header structure
3. Recommendation: REJECT this requirement
```

## Knowledge Base

The analyzer compares against **3,234 facts** extracted from LotJ:

### Fact Distribution

- **Constraints**: 110 hard requirements (from LOTJ_CONSTRAINT_CATALOG.md)
- **Implementation**: Code-level details
- **Design**: Architectural decisions
- **Requirements**: Feature requirements

### Key Constraint Categories

1. **Memory Management** (11 constraints)
   - Custom CREATE/DISPOSE macros
   - No raw malloc/free
   - Automatic NULL-setting

2. **Header File Organization** (7 constraints)
   - No new headers allowed
   - types.h for all structs
   - functions.h for all prototypes

3. **Development Workflow** (3 constraints)
   - Docker Compose required
   - Avoid docker-compose down
   - 10+ minute database rebuild

4. **Code Standards** (4 constraints)
   - snake_case functions
   - ALL_CAPS constants
   - Zero compiler warnings

5. **Git/Version Control** (6 constraints)
   - Never stage submodule changes
   - Pre-commit hooks required

## Benefits

### 1. Early Conflict Detection
Identify constraint violations **before** code is written

### 2. Informed Decision Making
Understand the **full impact** of architectural changes

### 3. Alternative Discovery
System suggests **alternatives** that work within constraints

### 4. Documentation Drift Prevention
Ensures new requirements align with **documented policies**

### 5. Onboarding Aid
Helps new developers understand **why constraints exist**

### 6. Technical Debt Visibility
Shows **exactly what** needs to change for new features

## Advanced Features

### Custom Conflict Checking

```python
# Check specific fact pairs
conflict = analyzer.analyze_conflict(
    requirement_fact,
    existing_fact
)

if conflict and conflict.severity == ConflictSeverity.CRITICAL:
    print("Cannot proceed!")
```

### Dependency Analysis

```python
# Find what existing systems are affected
dependency = analyzer.analyze_dependencies(
    requirement_fact,
    existing_fact
)

if dependency.dependency_type == 'modifies':
    print(f"Would modify: {existing_fact.statement}")
```

### Impact Mapping

```python
# Identify what artifacts need changes
impact_areas = analyzer.identify_impact_areas(
    requirement,
    conflicts,
    dependencies
)

for area in impact_areas:
    print(f"{area.change_type}: {area.artifact_path}")
```

## Integration Points

### With Kraang Core

The analyzer builds on Kraang's foundation:
- Uses `KraangStore` for fact persistence
- Leverages `Fact` and `Relationship` models
- Extends with conflict-specific types

### With CI/CD

```yaml
# .github/workflows/requirement-check.yml
name: Requirement Feasibility Check

on:
  pull_request:
    paths:
      - 'requirements/**'

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Analyze Requirements
        run: |
          for req in requirements/*.txt; do
            ./requirement_analyzer.py --file $req \
              --output analysis/$(basename $req .txt).json
          done
      - name: Check Feasibility
        run: |
          python3 scripts/check_min_feasibility.py 0.6
```

### With Issue Tracking

```python
# Auto-comment on issues with feasibility analysis
def analyze_github_issue(issue_body):
    analyzer = RequirementAnalyzer()
    report = analyzer.analyze(issue_body)

    comment = f"""
    ## Automated Feasibility Analysis

    Score: {report.feasibility_score:.2f}
    Assessment: {report.overall_assessment}

    ### Conflicts Found: {len(report.conflicts)}
    [Full analysis attached]
    """

    return comment
```

## Limitations

### 1. LLM Dependency
Full analyzer requires Anthropic API (demo version doesn't)

### 2. Fact Coverage
Analysis quality depends on knowledge base completeness

### 3. Heuristic Scoring
Feasibility scores are estimates, not guarantees

### 4. Natural Language Ambiguity
Vague requirements may produce less accurate analysis

### 5. Context Limits
May not catch all implicit dependencies

## Future Enhancements

- [ ] Multi-requirement batch analysis
- [ ] Conflict resolution suggestions (auto-generate alternatives)
- [ ] Historical analysis (how constraints evolved)
- [ ] Constraint relaxation impact (what if we remove constraint X?)
- [ ] Requirement similarity search (has this been proposed before?)
- [ ] Visual conflict graphs
- [ ] Integration with project management tools
- [ ] Machine learning for better severity classification
- [ ] Constraint negotiation mode (find minimum changes needed)
- [ ] Cost estimation based on impact areas

## Best Practices

### 1. Run Early
Analyze requirements **before** starting implementation

### 2. Iterate on Requirements
Use analysis to **refine** requirements, not just reject them

### 3. Document Exceptions
If proceeding despite conflicts, **document why**

### 4. Update Knowledge Base
Keep constraint knowledge **current** as architecture evolves

### 5. Team Discussion
Use reports as **conversation starters**, not final decisions

### 6. Consider Alternatives
System suggestions are starting points for **creative solutions**

### 7. Track Feasibility Over Time
Monitor if constraint **rigidity is blocking innovation**

## Conclusion

The Requirement Analyzer transforms constraint rationalization from an **implicit, error-prone process** into an **explicit, automated analysis**.

By systematically comparing proposed requirements against existing constraints, teams can:
- Make **informed decisions** about new features
- Understand **full impact** before coding begins
- Find **alternatives** that work within constraints
- Prevent **documentation drift** and technical debt

The system doesn't make decisions - it provides the **data needed** for humans to make better decisions faster.

---

**See Also**:
- `requirement_analyzer.py` - Full implementation
- `requirement_analyzer_demo.py` - Demo scenarios
- `LOTJ_CONSTRAINT_CATALOG.md` - All 110 LotJ constraints
- `kraang.py` - Core constraint rationalization engine
