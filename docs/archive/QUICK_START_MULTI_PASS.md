# Quick Start: Multi-Pass Extraction

## Installation

Multi-pass extraction is already integrated. No additional installation needed.

## Basic Usage

```bash
# Initialize project
./kraang.py init

# Add a file
./kraang.py add src/example.c code

# Run multi-pass extraction
./kraang.py extract-multi artifact_1
```

## Common Commands

### Default (All Passes)
```bash
./kraang.py extract-multi artifact_1
```
Runs up to 7 specialized passes with automatic early stopping.

### Limited Passes
```bash
./kraang.py extract-multi artifact_1 --max-passes 3
```
Run only the first 3 passes (General, Memory, Concurrency).

### Budget Control
```bash
./kraang.py extract-multi artifact_1 --budget 5
```
Stop after 5 API calls maximum.

### No Early Stopping
```bash
./kraang.py extract-multi artifact_1 --no-diminishing-returns
```
Run all configured passes regardless of yields.

## When to Use

### Use Multi-Pass When:
- Analyzing critical systems (safety, security, compliance)
- First-time extraction of a complex codebase
- Need comprehensive constraint coverage
- Acceptable to spend ~$0.30-0.50 per file

### Use Single-Pass When:
- Quick checks during development
- Simple configuration files
- Iterative re-extraction of frequently changed files
- Tight budget constraints

## Expected Results

### Single-Pass
- Fast (1 API call)
- Cheap (~$0.06 per file)
- Captures obvious constraints
- May miss specialized concerns

### Multi-Pass
- Thorough (3-7 API calls)
- Moderate cost (~$0.40 per file)
- Captures 50-100% more facts
- Finds domain-specific constraints

## Specialized Passes

Multi-pass extraction uses these specialized prompts:

1. **General** - Baseline coverage of all constraint types
2. **Memory** - Allocation, deallocation, ownership, leaks
3. **Concurrency** - Threading, locks, race conditions
4. **Security** - Authentication, validation, encryption
5. **Error Handling** - Return codes, exceptions, cleanup
6. **Performance** - Latency, throughput, complexity
7. **Testing** - Coverage, test strategies, requirements

Each pass focuses deeply on its domain, catching facts that a general prompt might miss.

## Example Output

```
======================================================================
Multi-Pass Extraction: src/memory.c
======================================================================

Pass 1: GENERAL
  Extracting...
  ✓ Extracted 42 raw facts
  Deduplicating...
  ✓ 42 new unique facts, 0 duplicates merged
  Novelty Score: 1.00

Pass 2: MEMORY
  Extracting...
  ✓ Extracted 28 raw facts
  Deduplicating...
  ✓ 18 new unique facts, 10 duplicates merged
  Novelty Score: 0.72

[... more passes ...]

======================================================================
EXTRACTION COMPLETE
======================================================================
Total Passes: 7
Total Facts Extracted: 80
API Calls: 7
Tokens Used: 125,384

Per-pass breakdown:
  general      : 42 raw -> 42 new (0 duplicates)
  memory       : 28 raw -> 18 new (10 duplicates)
  concurrency  : 15 raw ->  8 new (7 duplicates)
  security     :  8 raw ->  3 new (5 duplicates)
  error_handling: 12 raw -> 6 new (6 duplicates)
  performance  :  5 raw ->  2 new (3 duplicates)
  testing      :  3 raw ->  1 new (2 duplicates)
```

## Comparison Example

```bash
# Single-pass
$ ./kraang.py extract artifact_1
✓ Extracted 42 facts

# Multi-pass
$ ./kraang.py extract-multi artifact_1
✓ Extracted 80 facts
  Passes run: 7
  API calls: 7
  Tokens used: 125,384

# Improvement: +90% more facts
```

## Tips

1. **Start with multi-pass** for initial extraction of a project
2. **Use single-pass** for quick updates during development
3. **Set budgets** for large projects: `--budget 5`
4. **Limit passes** for simple files: `--max-passes 3`
5. **Review completeness** after extraction: `./kraang.py completeness`

## Testing

Verify the integration works:

```bash
# Run tests
python3 test_integration.py
python3 test_cli_integration.py

# Run demo (requires API key)
export ANTHROPIC_API_KEY='your-key-here'
./demo_multi_pass.sh
```

## Help

```bash
# Show all commands
./kraang.py

# Show usage
./kraang.py extract-multi
```

## More Information

- Full design: `MULTI_PASS_STRATEGY.md`
- Integration details: `INTEGRATION_GUIDE.md`
- Visual diagrams: `MULTI_PASS_DIAGRAMS.md`
- Completion summary: `MULTI_PASS_INTEGRATION_COMPLETE.md`
