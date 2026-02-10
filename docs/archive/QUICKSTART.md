# Kraang Quick Start

Get started with Kraang in 5 minutes.

## Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt

# Set your Anthropic API key
export ANTHROPIC_API_KEY="your-key-here"
```

## Basic Usage

```bash
# 1. Initialize Kraang
./kraang.py init

# 2. Add some artifacts
./kraang.py add ~/Code/LotJ/CLAUDE.md doc
./kraang.py add ~/Code/LotJ/src/act_comm.c code

# 3. Extract facts (uses Claude API)
./kraang.py extract artifact_1
./kraang.py extract artifact_2

# 4. Analyze relationships (uses Claude API)
./kraang.py relate

# 5. Check for conflicts
./kraang.py conflicts

# 6. Analyze impact
./kraang.py impact fact_1
```

## What You Get

After running these commands, you'll have:

- `.kraang/artifacts.json` - Your registered files
- `.kraang/facts.json` - Extracted constraints and facts
- `.kraang/relationships.json` - How facts relate to each other

## Example: Finding Documentation Drift

```bash
# Extract constraints from documentation
./kraang.py add docs/ARCHITECTURE.md doc
./kraang.py extract artifact_1

# Extract implementation from code
./kraang.py add src/auth.py code
./kraang.py extract artifact_2

# Find conflicts
./kraang.py relate
./kraang.py conflicts
```

If the code doesn't match the docs, you'll see contradictions like:

```
CONTRADICTION (confidence: 0.92)
  Fact 1 (fact_3): Documentation states authentication requires email verification
  Fact 2 (fact_8): Implementation allows login without email verification
  Reasoning: The documented requirement conflicts with actual implementation
```

## Example: Impact Analysis for Refactoring

Before changing a constraint, see what would be affected:

```bash
./kraang.py impact fact_2
```

Output:
```
Impact analysis for: Memory allocation must use CREATE macro

Source artifacts:
  - docs/CLAUDE.md (lines 255-270)

Related facts (4):
  [extends] Use DISPOSE() to free memory
  [supports] do_say() uses DISPOSE()
  [supports] Use LINK/UNLINK for linked lists
  [contradicts] legacy.c uses raw malloc
```

Now you know:
- Where the constraint is documented
- What code follows it
- What code violates it
- What other constraints depend on it

## Running the LotJ Test

```bash
# Full integration test on LotJ codebase
./test_lotj.sh
```

This will:
1. Initialize Kraang
2. Add LotJ documentation
3. Add sample C code
4. Extract facts from all artifacts
5. Analyze relationships
6. Show conflicts
7. Demonstrate impact analysis

## Tips

- Start with documentation (easier to extract clean constraints)
- Add code files next to find implementation facts
- Use `list facts` to see what's been extracted
- Use `list relationships` to see the constraint graph
- The .kraang/ directory is git-friendly JSON

## Next Steps

- Read [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- Read [TESTING.md](TESTING.md) for validation strategy
- Read [EXAMPLE_OUTPUT.md](EXAMPLE_OUTPUT.md) for sample outputs
- Read [README.md](README.md) for full documentation

## Cost Estimate

Using Claude Sonnet 4.5:
- Extracting facts: ~$0.01-0.05 per artifact
- Analyzing relationships: ~$0.001 per pair
- For small project (10 files): ~$1-2 total

## Troubleshooting

**"ANTHROPIC_API_KEY not set"**
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

**"JSON decode error"**
- Claude sometimes returns markdown-wrapped JSON
- The code handles this, but if you see errors, check the API response

**"Too many relationships"**
- Use `kraang relate fact_1 fact_2` to analyze specific pairs
- The O(n²) all-pairs analysis can be expensive for many facts

**"Extraction seems inaccurate"**
- Try with different artifact types
- Documentation usually extracts better than code
- Consider breaking large files into smaller logical chunks
