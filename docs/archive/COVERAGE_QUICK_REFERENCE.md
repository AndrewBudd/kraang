# Coverage Analysis - Quick Reference

## Commands

### Show Overall Coverage
```bash
kraang coverage
```
Shows project-wide statistics, coverage by type, top files, and recommendations.

### Show Artifact Detail
```bash
kraang coverage artifact_1
```
Shows detailed coverage for specific artifact including facts extracted.

### Show Heat Map
```bash
kraang coverage artifact_1 --heatmap
```
Generates visual heat map showing coverage distribution across the file.

### Show Gaps
```bash
kraang coverage --gaps
```
Identifies files with 0% coverage, <20% coverage, and files below target.

## Understanding the Output

### Coverage Percentage
- **Calculation**: (covered_lines / total_lines) * 100
- **Good**: Varies by file type (see targets below)

### Coverage Targets
| File Type | Target | Rationale |
|-----------|--------|-----------|
| Documentation (.md, .txt) | 70% | High-value for constraint extraction |
| Code (.c, .py, .lua) | 40% | Selective - focus on key logic |
| Headers (.h) | 70% | Interfaces and contracts are critical |
| Config (.json, .yaml) | 80% | Every setting is a constraint |

### Status Indicators
- ✓ = Meets target
- ⚠ = Below target (minor gap)
- ⚠⚠ = Well below target (significant gap)
- ⚠⚠⚠ = Zero coverage (critical gap)

### Heat Map Legend
```
[  ] = 0-20% coverage in this section
[░░] = 20-40% coverage
[▒▒] = 40-60% coverage
[▓▓] = 60-80% coverage
[██] = 80-100% coverage
```

## Coverage Metrics

### Line Coverage
Percentage of source lines referenced by at least one fact.

### Fact Density
Average number of facts per covered line. Higher density means more thorough analysis.
- **1.0-1.5**: Good (each covered line has 1-1.5 facts)
- **>1.5**: Excellent (multiple facts per line, overlapping coverage)
- **<1.0**: May indicate sparse coverage

### Coverage Level
Categorical assessment:
- **NONE**: 0-10% (essentially uncovered)
- **LOW**: 10-30% (minimal coverage)
- **MODERATE**: 30-60% (partial coverage)
- **GOOD**: 60-80% (solid coverage)
- **EXCELLENT**: 80-100% (comprehensive coverage)

## Workflow

### Initial Assessment
1. Run `kraang coverage` to see overall state
2. Note overall coverage percentage
3. Identify file types below target
4. Check critical gaps section

### Gap Analysis
1. Run `kraang coverage --gaps`
2. Address 0% files first (critical)
3. Then <20% files (high priority)
4. Then files below target (medium priority)

### Detailed Investigation
1. Run `kraang coverage artifact_X --heatmap`
2. Identify sections with low coverage ([ ] or [░░])
3. Read those sections in the source file
4. Extract missing facts with `kraang extract`

### Progress Tracking
1. Re-run `kraang coverage` after each extraction
2. Watch coverage percentage increase
3. Goal: All files meet target, overall >40%

## Example Session

```bash
# Check overall state
$ kraang coverage
Overall Coverage: 21.2%
Files needing attention: 2

# Identify gaps
$ kraang coverage --gaps
UNCOVERED FILES (0% coverage)
  (none)

FILES BELOW TARGET (>20% but under target)
• CLAUDE.md - 40.5% (target: 70%, gap: 30%)
• act_comm.c - 20.3% (target: 40%, gap: 20%)

# Investigate CLAUDE.md
$ kraang coverage artifact_1 --heatmap
Coverage Heat Map: CLAUDE.md
Lines: 1-398 | Coverage: 40.5%

  101-150: [  ] 2 facts   # ← Gap found!
  351-398: [  ] 5 facts   # ← Another gap!

# Extract more facts
$ kraang extract artifact_1

# Re-check coverage
$ kraang coverage
Overall Coverage: 45.2%  # ← Improved!
```

## Tips

### For Better Location Parsing
Encourage fact extraction with line-based locations:
- **Good**: "Lines 100-120"
- **Good**: "Line 50"
- **Good**: "Lines 100-120, Section: Memory Management"
- **Poor**: "function do_command" (not parsed)
- **Poor**: "Section: Architecture" (not parsed)

### For Complete Coverage
- Don't aim for 100% - not every line needs facts
- Focus on critical sections (MUST, SHALL, IMPORTANT)
- Balance between completeness and quality
- Multiple facts per important line is good (increases density)

### For Efficient Work
- Use heat maps to find specific gaps quickly
- Work on one artifact at a time
- Re-run coverage frequently to track progress
- Prioritize: 0% files → <20% files → below target

## Common Issues

### "Coverage percentage seems low"
- This is normal - not every line needs facts
- Check coverage level (MODERATE/GOOD is often sufficient)
- Focus on meeting targets, not 100%

### "Many unparseable locations"
- Check fact extraction quality
- Encourage "Lines X-Y" format
- If >20% unparseable, consider re-extraction

### "Coverage not increasing"
- Check that facts have line-based locations
- Verify artifact_id matches in extracted_from
- Use `kraang list facts` to see recent extractions

### "Artifact not found"
- Run `kraang list artifacts` to see available IDs
- Artifact IDs are like "artifact_1", "artifact_78"
- Not file paths or names

## Performance Notes

- Analysis is fast (<1 second for typical projects)
- Heat maps are instant
- Safe to run frequently
- No external dependencies required

## Related Commands

```bash
# Add a new artifact
kraang add path/to/file.md doc

# Extract facts from artifact
kraang extract artifact_1

# List all artifacts
kraang list artifacts

# List all facts
kraang list facts

# Check overall completeness
kraang completeness
```

## Success Criteria

Your coverage is **good** if:
- ✓ Overall coverage >40%
- ✓ No files with 0% coverage
- ✓ Most files meet type-specific targets
- ✓ <10% unparseable locations
- ✓ Fact density >1.0

Your coverage is **excellent** if:
- ✓ Overall coverage >60%
- ✓ All files meet targets
- ✓ <5% unparseable locations
- ✓ Fact density >1.5

Remember: Coverage is a means to an end. The goal is comprehensive constraint capture, not 100% coverage.
