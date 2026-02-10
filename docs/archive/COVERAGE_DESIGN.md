# Code Coverage Analyzer Design Document

## Overview

The coverage analyzer measures which parts of a codebase are referenced by extracted facts, helping identify areas that need more extraction work and assess completeness of the knowledge base.

## Core Concept

**Coverage** = What percentage of the source code has been analyzed and captured as facts?

This differs from test coverage - we're measuring documentation/knowledge coverage, not execution paths.

## Data Model Understanding

From kraang.py analysis:

1. **Artifacts** - Source files with content
   - Have `id`, `type`, `path`, `content`
   - Content is full file text

2. **Facts** - Extracted knowledge
   - Have `extracted_from` list of `ArtifactReference` objects
   - Each reference has `artifact_id` and `location` string

3. **Location Formats** - Observed patterns:
   - `"Lines 100-120"` - Line range
   - `"Lines 100-120, Section: Foo"` - Line range with context
   - `"Line 50"` - Single line
   - `"function do_command"` - Function reference
   - `"Section: Memory Management"` - Section/heading reference

## Coverage Metrics

### 1. Line Coverage (Primary Metric)

**Definition**: Percentage of source lines referenced by at least one fact.

**Formula**:
```
line_coverage = (referenced_lines / total_lines) * 100
```

**Calculation**:
- Parse all fact locations
- Extract line numbers/ranges
- Mark lines as "covered"
- Calculate percentage

**Challenges**:
- Not all locations specify lines
- Function references need to be mapped to lines (requires parsing)
- Section references are ambiguous

### 2. Function Coverage

**Definition**: Percentage of functions referenced by facts.

**Formula**:
```
function_coverage = (referenced_functions / total_functions) * 100
```

**Calculation**:
- Parse source to identify all functions
- Extract function names from fact locations
- Calculate percentage

**Note**: Requires language-specific parsing (C, Python, Lua differ)

### 3. Artifact Coverage

**Definition**: Which artifacts have zero facts vs some facts.

**Metrics**:
- Artifacts with 0 facts (uncovered)
- Artifacts with facts (covered)
- Facts per artifact (density)

### 4. Coverage Density

**Definition**: How thoroughly covered areas are covered.

**Metrics**:
- Average facts per covered line
- Clustering (are facts clustered or distributed?)

## Coverage Targets

Different file types have different coverage expectations:

### Documentation Files (.md, .txt, .rst)

**Target: 60-80%**

Rationale:
- Docs are high-value for constraint extraction
- Not every line is meaningful (formatting, examples, etc.)
- Key sections should be covered

**Good Coverage**:
- All major sections referenced
- Key requirements/constraints extracted
- Architecture decisions documented

**Low Coverage Red Flags**:
- Large sections unreferenced
- Critical sections (MUST, SHALL, IMPORTANT) missed

### Header Files (.h)

**Target: 70-90%**

Rationale:
- Headers define interfaces and contracts
- Function signatures are constraints
- Comments often contain critical info
- Should have high coverage

**Good Coverage**:
- All public functions referenced
- Key type definitions captured
- Important comments extracted

**Low Coverage Red Flags**:
- Public API functions unreferenced
- Missing type definitions

### Implementation Files (.c, .py, .lua)

**Target: 30-50%**

Rationale:
- Not all implementation details are constraints
- Boilerplate code may not need facts
- Focus on key algorithms and business logic

**Good Coverage**:
- Major functions referenced
- Critical algorithms documented
- Key business logic captured

**Low Coverage Red Flags**:
- Zero coverage (file completely ignored)
- Main entry points unreferenced

### Configuration Files (.json, .yaml, .env)

**Target: 80-100%**

Rationale:
- Every config setting is a constraint
- Small files, should be thoroughly documented

## Location Parsing Strategy

### Phase 1: Simple Parser (MVP)

Only handle explicit line references:
- `"Lines 100-120"` -> lines 100-120
- `"Line 50"` -> line 50
- Regex: `r'Lines? (\d+)(?:-(\d+))?'`

Ignore:
- Function references
- Section references
- Ambiguous locations

### Phase 2: Advanced Parser

Add function mapping:
- Parse source files to find function definitions
- Build function -> line_range mapping
- `"function do_command"` -> lines 150-200

Add section detection:
- For docs: parse markdown headers
- Map sections to line ranges
- `"Section: Architecture"` -> lines 50-100

### Phase 3: Semantic Coverage

- Identify critical regions (MUST, SHALL, TODO, FIXME)
- Weight coverage by importance
- Track which constraints have implementing code

## Heat Map Visualization

### Text-Based Heat Map

```
Coverage Heat Map: /path/to/file.c
Lines: 1-1000 | Coverage: 35%

Legend: [  ] 0-20% | [░░] 20-40% | [▒▒] 40-60% | [▓▓] 60-80% | [██] 80-100%

    1-  50: [  ] no facts
   51- 100: [▓▓] 4 facts (function init_system)
  101- 150: [██] 6 facts (memory allocation logic)
  151- 200: [▒▒] 2 facts (helper functions)
  201- 250: [  ] no facts
  251- 300: [  ] no facts
  301- 350: [░░] 1 fact
  351- 400: [  ] no facts
  ...
```

Features:
- Group lines into buckets (50 lines each)
- Show fact density with ASCII art
- Highlight function names for context
- Show absolute fact counts

### Summary Report

```
=== Coverage Analysis Summary ===

Overall Coverage: 42%
Files Analyzed: 5
Total Lines: 12,450
Covered Lines: 5,229

Coverage by File Type:
  Documentation (.md):  78% ✓ (target: 60-80%)
  Headers (.h):         45% ⚠ (target: 70-90%)
  Implementation (.c):  38% ✓ (target: 30-50%)

Top 5 Covered Files:
  1. CLAUDE.md              95% (378/398 lines)
  2. src/memory.h           82% (150/183 lines)
  3. src/act_comm.c         65% (5,760/8,863 lines)
  ...

Bottom 5 (Need Attention):
  1. src/utils.h             0% (0/245 lines) ⚠⚠⚠
  2. src/network.c           5% (50/1000 lines) ⚠⚠
  3. docs/API.md            12% (30/250 lines) ⚠⚠
  ...

Critical Gaps:
  - 3 header files with 0% coverage
  - 5 functions never referenced
  - 2 documentation sections unreferenced
```

## Coverage Commands

Add to KraangCLI:

```python
# Overall summary
kraang coverage

# Detailed report for specific artifact
kraang coverage artifact_1

# Heat map visualization
kraang coverage artifact_1 --heatmap

# Find gaps
kraang coverage --gaps

# Set custom targets
kraang coverage --target-doc 70 --target-code 40
```

## Implementation Strategy

### Data Structures

```python
@dataclass
class FileCoverage:
    artifact_id: str
    path: str
    total_lines: int
    covered_lines: Set[int]  # Line numbers with facts
    facts_by_line: Dict[int, List[str]]  # Line -> fact_ids

    def coverage_percentage(self) -> float:
        return len(self.covered_lines) / self.total_lines * 100

    def density(self) -> float:
        # Average facts per covered line
        if not self.covered_lines:
            return 0.0
        total_facts = sum(len(fids) for fids in self.facts_by_line.values())
        return total_facts / len(self.covered_lines)

@dataclass
class CoverageReport:
    file_coverages: List[FileCoverage]
    total_lines: int
    covered_lines: int
    total_facts: int

    def overall_percentage(self) -> float:
        return (self.covered_lines / self.total_lines) * 100

    def by_type(self, artifact_type: str) -> List[FileCoverage]:
        # Filter by artifact type
        pass
```

### Location Parser

```python
class LocationParser:
    """Parses fact locations to extract line numbers"""

    LINE_PATTERN = re.compile(r'Lines? (\d+)(?:-(\d+))?')

    def parse_location(self, location: str) -> Set[int]:
        """
        Parse location string and return set of line numbers.

        Examples:
            "Lines 100-120" -> {100, 101, ..., 120}
            "Line 50" -> {50}
            "function foo" -> set() (not supported in v1)
        """
        lines = set()

        # Try line pattern
        match = self.LINE_PATTERN.search(location)
        if match:
            start = int(match.group(1))
            end = int(match.group(2)) if match.group(2) else start
            lines = set(range(start, end + 1))

        return lines
```

### Coverage Analyzer

```python
class CoverageAnalyzer:
    """Analyzes coverage of facts across artifacts"""

    def __init__(self, store: KraangStore):
        self.store = store
        self.parser = LocationParser()

    def analyze_artifact(self, artifact: Artifact) -> FileCoverage:
        """Analyze coverage for a single artifact"""

        # Count total lines
        total_lines = artifact.content.count('\n') + 1

        # Find all facts referencing this artifact
        all_facts = self.store.get_facts()
        relevant_facts = [
            f for f in all_facts
            if any(ref['artifact_id'] == artifact.id
                   for ref in f.extracted_from)
        ]

        # Parse locations to get covered lines
        covered_lines = set()
        facts_by_line = defaultdict(list)

        for fact in relevant_facts:
            for ref in fact.extracted_from:
                if ref['artifact_id'] == artifact.id:
                    lines = self.parser.parse_location(ref['location'])
                    covered_lines.update(lines)
                    for line in lines:
                        facts_by_line[line].append(fact.id)

        return FileCoverage(
            artifact_id=artifact.id,
            path=artifact.path,
            total_lines=total_lines,
            covered_lines=covered_lines,
            facts_by_line=dict(facts_by_line)
        )

    def analyze_all(self) -> CoverageReport:
        """Analyze coverage for all artifacts"""
        pass

    def generate_heatmap(self, coverage: FileCoverage,
                         bucket_size: int = 50) -> str:
        """Generate ASCII heat map"""
        pass
```

## Validation Strategy

Test with LotJ dataset:
1. Run coverage analysis on existing facts
2. Verify line parsing accuracy
3. Check coverage percentages make sense
4. Generate heat map for act_comm.c
5. Identify gaps in CLAUDE.md

Expected Results:
- CLAUDE.md: ~60-80% (lots of facts extracted)
- act_comm.c: ~20-40% (some facts, but large file)
- Overall: ~30-50%

## Future Enhancements

1. **Semantic Coverage**
   - Weight by keyword importance (MUST > SHOULD > MAY)
   - Track critical section coverage

2. **Change Detection**
   - Track coverage over time
   - Alert on coverage drops

3. **Interactive Mode**
   - `kraang coverage --interactive`
   - Show uncovered sections
   - Prompt to extract facts

4. **Coverage Goals**
   - Set per-file targets
   - Track toward goals
   - CI/CD integration

5. **Visual Output**
   - HTML reports with syntax highlighting
   - Color-coded heat maps
   - Interactive drill-down

## Success Metrics

Coverage analyzer is successful if it:
1. Accurately identifies low-coverage files
2. Helps prioritize extraction work
3. Provides actionable insights
4. Takes <5 seconds to run on typical projects
5. Integrates smoothly with existing commands

Target: Reduce "unknown unknowns" by highlighting what hasn't been analyzed yet.
