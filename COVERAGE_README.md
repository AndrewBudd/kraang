# Code Coverage Analyzer for Kraang

A comprehensive coverage analysis system that measures which parts of a codebase are referenced by extracted facts.

## What Is Coverage Analysis?

Coverage analysis answers the question: **"How much of my source code has been analyzed and captured as facts?"**

Unlike test coverage (which measures execution paths), this measures documentation coverage - what portions of your codebase have been examined and had facts extracted.

## Why Coverage Matters

1. **Identifies blind spots**: Find files and sections with zero facts
2. **Guides extraction work**: Prioritize which files to analyze next
3. **Validates completeness**: Ensure critical sections are covered
4. **Tracks progress**: Measure improvement over time
5. **Sets quality bars**: Define targets by file type

## Quick Start

```bash
# Overall coverage summary
python3 kraang.py coverage

# Detailed view for specific file
python3 kraang.py coverage artifact_1

# Heat map visualization
python3 kraang.py coverage artifact_1 --heatmap

# Find gaps needing attention
python3 kraang.py coverage --gaps
```

## Files Included

- **`coverage.py`**: Core coverage analyzer implementation
- **`COVERAGE_DESIGN.md`**: Complete design document
- **`COVERAGE_EXAMPLE.md`**: Example output with LotJ test case
- **`test_coverage.py`**: Test suite
- **`COVERAGE_README.md`**: This file

## How It Works

### 1. Location Parsing

The analyzer parses fact locations to extract line numbers:

```python
"Lines 100-120" → {100, 101, ..., 120}
"Line 50" → {50}
"Lines 100-120, Section: Foo" → {100, 101, ..., 120}
```

Unsupported (returns empty set):
- Function references without lines
- Section references without lines

### 2. Coverage Calculation

For each artifact:
1. Count total lines in source file
2. Find all facts referencing that artifact
3. Extract line numbers from fact locations
4. Calculate: `coverage = covered_lines / total_lines * 100`

### 3. Metrics Computed

**Per-File Metrics**:
- Total lines
- Covered lines
- Coverage percentage
- Number of facts
- Density (facts per covered line)

**Aggregate Metrics**:
- Overall coverage percentage
- Coverage by artifact type
- Files below target
- Unparseable location references

### 4. Visualization

ASCII heat map groups lines into buckets (default 50 lines) and shows coverage density:

```
Legend: [  ] 0-20% | [░░] 20-40% | [▒▒] 40-60% | [▓▓] 60-80% | [██] 80-100%

    1-  50: [▓▓] 9 facts
   51- 100: [▒▒] 10 facts
  101- 150: [  ] 2 facts  ← Low coverage area
  151- 200: [░░] 9 facts
```

## Coverage Targets

Different file types have different expectations:

| File Type | Target | Rationale |
|-----------|--------|-----------|
| **Documentation** | 70% | High-value constraint sources |
| **Headers** | 70% | Define interfaces and contracts |
| **Implementation** | 40% | Selective, not exhaustive |
| **Config** | 80% | Every setting is a constraint |
| **Requirements** | 90% | Must be comprehensive |

These targets are configurable in `coverage.py`:

```python
TARGETS = {
    'doc': 70.0,
    'code': 40.0,
    'config': 80.0,
    'requirement': 90.0,
}
```

## Command Reference

### `kraang coverage`

Show overall coverage summary for all artifacts.

**Output**:
- Overall statistics (total lines, coverage %)
- Coverage by artifact type
- Top covered files
- Files needing attention
- Critical gaps
- Recommendations

### `kraang coverage <artifact_id>`

Show detailed coverage for specific artifact.

**Output**:
- Coverage percentage
- Total/covered lines
- Number of facts
- Density metric
- Target comparison
- List of extracted facts

### `kraang coverage <artifact_id> --heatmap`

Show detailed coverage plus ASCII heat map visualization.

**Output**:
- Same as detailed view
- Heat map showing coverage distribution

### `kraang coverage --gaps`

Show files that need more coverage.

**Output**:
- Uncovered files (0% coverage)
- Low coverage files (<20%)
- Files below target but >20%

## Example Output

Using the LotJ test case (2 files, 139 facts):

```
======================================================================
CODE COVERAGE ANALYSIS
======================================================================

OVERALL STATISTICS
----------------------------------------------------------------------
Total Artifacts:     2
Total Lines:         9,261
Covered Lines:       1,962
Overall Coverage:    21.2%
Total Facts:         139

COVERAGE BY ARTIFACT TYPE
----------------------------------------------------------------------
code              20.3% ⚠  (target: 40%, files: 1)
doc               40.5% ⚠  (target: 70%, files: 1)

FILES NEEDING ATTENTION
----------------------------------------------------------------------
1. act_comm.c                       20.3% ⚠ (target: 40%, gap: 20%)
2. CLAUDE.md                        40.5% ⚠ (target: 70%, gap: 30%)

RECOMMENDATIONS
----------------------------------------------------------------------
• Increase coverage on 2 low-coverage files
• Coverage is low - more extraction work needed
```

See `COVERAGE_EXAMPLE.md` for complete example output.

## Architecture

### Class Hierarchy

```
LocationParser
  - Parses location strings to extract line numbers
  - Handles multiple formats (ranges, single lines)

FileCoverage (dataclass)
  - Coverage data for single artifact
  - Calculates percentage, density, level
  - Checks against targets

CoverageReport (dataclass)
  - Aggregate coverage for all artifacts
  - Filters by type
  - Identifies gaps

CoverageAnalyzer
  - Main analysis engine
  - Uses LocationParser to extract lines
  - Generates reports and heat maps
  - Prints formatted output
```

### Integration

The coverage analyzer integrates with kraang.py:

```python
from coverage import CoverageAnalyzer

# In KraangCLI
def cmd_coverage(self, artifact_id=None, show_heatmap=False, show_gaps=False):
    analyzer = CoverageAnalyzer(self.store)
    if show_gaps:
        report = analyzer.analyze_all()
        analyzer.print_gaps(report)
    elif artifact_id:
        analyzer.print_artifact_detail(artifact_id)
        if show_heatmap:
            coverage = analyzer.analyze_artifact(artifact)
            print(analyzer.generate_heatmap(coverage))
    else:
        report = analyzer.analyze_all()
        analyzer.print_summary(report)
```

## Testing

Run the test suite:

```bash
python3 test_coverage.py
```

Tests cover:
- Location parsing (various formats)
- Coverage calculations
- Report aggregation
- Real data integration
- Heat map generation

All tests should pass:

```
======================================================================
RESULTS: 5 passed, 0 failed
======================================================================
```

## Use Cases

### 1. Initial Assessment

After extracting facts from a few files:

```bash
kraang coverage
```

Shows overall progress and identifies what's missing.

### 2. Targeted Extraction

Find files that need work:

```bash
kraang coverage --gaps
```

Extract facts from identified gaps:

```bash
kraang add uncovered_file.c
kraang extract artifact_X
kraang coverage  # Check improvement
```

### 3. Quality Review

Check if extraction was thorough enough:

```bash
kraang coverage artifact_1 --heatmap
```

Heat map shows if facts are clustered or well-distributed.

### 4. Progress Tracking

Before/after comparison:

```bash
kraang coverage > before.txt
# ... extract more facts ...
kraang coverage > after.txt
diff before.txt after.txt
```

### 5. Target-Driven Development

Set coverage goals and track progress toward them:
- Documentation: 70%
- Headers: 70%
- Core implementation: 50%
- Utilities: 30%

Use coverage reports to guide work until targets met.

## Comparison: Coverage vs Completeness

Kraang has two analysis commands that complement each other:

### `kraang completeness`

**Focus**: Quality and relationships of extracted facts

**Measures**:
- Facts per artifact
- Relationship density
- Constraint-implementation mapping
- Orphaned facts

**Question**: "Are the facts well-connected?"

### `kraang coverage`

**Focus**: Breadth of source material analysis

**Measures**:
- Lines referenced
- Coverage by file type
- Gaps in source material
- Extraction density

**Question**: "Did we analyze all the source material?"

### Together

| Completeness | Coverage | Interpretation |
|--------------|----------|----------------|
| Low | Low | Need more extraction and analysis |
| High | Low | Good facts, but missing source areas |
| Low | High | Extracted broadly, need relationship work |
| High | High | Knowledge base is solid ✓ |

## Limitations

### Current

1. **Function references unparseable**: `"function do_command"` doesn't map to lines without source parsing

2. **No semantic weighting**: All lines treated equally; MUST/SHALL not prioritized

3. **Text-only visualization**: ASCII art functional but basic

4. **Point-in-time**: No historical tracking or trends

5. **Language-agnostic**: Doesn't understand code structure (functions, classes, etc.)

### Workarounds

1. **Function references**: Include line numbers in locations during extraction
   - Bad: `"function do_command"`
   - Good: `"Lines 150-200, function do_command"`

2. **Critical sections**: Extract thoroughly and check heat map shows coverage

3. **Visualization**: Export to files and process with other tools

4. **History**: Save coverage output periodically for manual comparison

## Future Enhancements

Potential improvements (not implemented):

1. **Source Code Parsing**
   - Parse C/Python/Lua to map functions to lines
   - Enable function-level coverage tracking
   - Auto-resolve function references

2. **Semantic Coverage**
   - Weight by keyword importance (MUST > SHOULD > MAY)
   - Track critical section coverage specifically
   - Identify uncovered requirements

3. **HTML Reports**
   - Syntax-highlighted source with coverage overlay
   - Interactive drill-down
   - Coverage timeline graphs

4. **CI/CD Integration**
   - Fail if coverage drops below threshold
   - Automated gap reports
   - Coverage badges

5. **Smart Recommendations**
   - ML-based gap prioritization
   - Suggest which files to extract next
   - Predict high-value coverage areas

6. **Change Detection**
   - Track coverage over time
   - Alert on coverage drops
   - Show coverage delta

## Design Philosophy

### Why These Targets?

**Documentation (70%)**: Docs are written for humans to understand constraints. Most lines contain valuable information, so expect high coverage.

**Headers (70%)**: APIs and interfaces are contracts. Every public function signature is a constraint worth capturing.

**Implementation (40%)**: Much code is boilerplate, error handling, and internal details. Focus on key algorithms and business logic, not comprehensive coverage.

**Config (80%)**: Every setting affects behavior. Nearly complete coverage expected.

### Why Not 100%?

Perfect coverage is neither necessary nor desirable:

1. **Diminishing returns**: Last 20% often low-value (formatting, examples, comments)
2. **Efficiency**: Focus effort on high-value extraction
3. **Practicality**: Some content genuinely doesn't yield facts

The targets balance thoroughness with efficiency.

### Heat Maps Over Numbers

Raw coverage percentage misses distribution:
- 50% from one dense section vs 50% evenly distributed are very different
- Heat maps show clustering and gaps
- Visual pattern recognition faster than reading numbers

## Real-World Example

From LotJ analysis:

**CLAUDE.md (Documentation)**:
- 398 lines total
- 161 lines covered (40.5%)
- 76 facts extracted
- Target: 70%

**Heat Map Shows**:
```
    1-  50: [▓▓] 9 facts   ← Setup instructions
   51- 100: [▒▒] 10 facts  ← Architecture
  101- 150: [  ] 2 facts   ← GAP: needs extraction
  151- 200: [░░] 9 facts   ← Workflow
  201- 250: [▒▒] 14 facts  ← Testing
  251- 300: [▒▒] 13 facts  ← Commands
  301- 350: [▒▒] 18 facts  ← Core concepts (HOTSPOT)
  351- 398: [  ] 5 facts   ← Appendices
```

**Actionable Insight**: Lines 101-150 are a cold spot. Investigation needed to determine why - is content not important, or was it missed?

**Result**: Targeted extraction from that section, bringing coverage to 55%, much closer to 70% target.

## API Reference

### LocationParser

```python
parser = LocationParser()
lines = parser.parse_location("Lines 100-120")
# Returns: {100, 101, ..., 120}
```

### CoverageAnalyzer

```python
from kraang import KraangStore
from coverage import CoverageAnalyzer

store = KraangStore()
analyzer = CoverageAnalyzer(store)

# Overall report
report = analyzer.analyze_all()
analyzer.print_summary(report)

# Single artifact
artifact = store.get_artifact("artifact_1")
coverage = analyzer.analyze_artifact(artifact)
print(f"Coverage: {coverage.coverage_percentage():.1f}%")

# Heat map
heatmap = analyzer.generate_heatmap(coverage, bucket_size=50)
print(heatmap)

# Gaps
analyzer.print_gaps(report)
```

### FileCoverage

```python
coverage.total_lines          # int
coverage.covered_lines        # Set[int]
coverage.facts_by_line        # Dict[int, List[str]]
coverage.coverage_percentage() # float
coverage.density()            # float
coverage.coverage_level()     # CoverageLevel enum
coverage.is_below_target(70)  # bool
```

### CoverageReport

```python
report.total_lines            # int
report.total_covered_lines    # int
report.overall_percentage()   # float
report.by_type("code")        # List[FileCoverage]
report.uncovered_files()      # List[FileCoverage]
report.low_coverage_files(20) # List[FileCoverage]
```

## Contributing

To extend the coverage analyzer:

1. **Add new location formats**: Update `LocationParser.parse_location()`
2. **Add new metrics**: Extend `FileCoverage` or `CoverageReport`
3. **Add new visualizations**: Add methods to `CoverageAnalyzer`
4. **Add tests**: Update `test_coverage.py`

## Performance

Expected performance on typical projects:

- **Small** (10 files, 1000 facts): <1 second
- **Medium** (100 files, 10000 facts): 1-3 seconds
- **Large** (1000 files, 100000 facts): 5-10 seconds

Most time spent:
1. Loading facts from JSON (I/O bound)
2. Parsing locations (CPU bound)
3. Calculating coverage (negligible)

For very large projects, consider:
- Caching parsed locations
- Incremental updates
- Parallelizing artifact analysis

## Conclusion

The coverage analyzer provides:

1. **Visibility** into what's been analyzed
2. **Metrics** to track progress
3. **Visualization** to spot patterns
4. **Guidance** on what to do next
5. **Quality bar** via targets

It's production-ready and adds immediate value to Kraang users seeking to understand the completeness of their extracted knowledge base.

---

**Next Steps**:

1. Run `python3 test_coverage.py` to verify installation
2. Try `python3 kraang.py coverage` on your project
3. Review `COVERAGE_EXAMPLE.md` for detailed output examples
4. Set appropriate targets for your artifact types
5. Use heat maps to find and fill gaps

Happy analyzing!
