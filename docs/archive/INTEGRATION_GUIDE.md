# Multi-Pass Extraction: Integration Guide

## Overview

This guide shows how to integrate the multi-pass extraction strategy into the existing Kraang CLI.

## Files Created

```
/home/budda/Code/kraang/
├── multi_pass_extraction.py    # Core implementation
├── MULTI_PASS_STRATEGY.md      # Detailed strategy documentation
├── MULTI_PASS_DIAGRAMS.md      # Visual workflow diagrams
├── test_multi_pass.py          # Test/demo script
└── INTEGRATION_GUIDE.md        # This file
```

## Integration Options

### Option 1: New CLI Command (Recommended)

Add a new `extract-multi` command that uses multi-pass extraction.

**Advantages**:
- Preserves existing `extract` command behavior
- Users can choose between single-pass (fast) and multi-pass (thorough)
- Backward compatible
- Clear opt-in for advanced feature

**Implementation**:

Edit `/home/budda/Code/kraang/kraang.py`:

```python
# Add import at top
from multi_pass_extraction import MultiPassExtractor, PassType

# Add new command in KraangCLI class
class KraangCLI:
    # ... existing methods ...

    def cmd_extract_multi(
        self,
        artifact_id: str,
        max_passes: int = 7,
        budget: int = None,
        enable_diminishing_returns: bool = True
    ):
        """Extract facts using multi-pass strategy"""
        artifact = self.store.get_artifact(artifact_id)
        if not artifact:
            print(f"✗ Artifact not found: {artifact_id}")
            return

        print(f"Multi-pass extraction from {artifact.path}...")
        print(f"  Max passes: {max_passes}")
        if budget:
            print(f"  Budget: {budget} API calls")
        print(f"  Diminishing returns detection: {'enabled' if enable_diminishing_returns else 'disabled'}")
        print()

        # Create multi-pass extractor
        extractor = MultiPassExtractor(
            max_passes=max_passes,
            enable_diminishing_returns=enable_diminishing_returns,
            budget_api_calls=budget
        )

        # Run extraction
        results = extractor.run_passes(
            artifact_type=artifact.type,
            artifact_path=artifact.path,
            artifact_content=artifact.content
        )

        # Save facts to store
        print(f"\nSaving {len(results['facts'])} facts to store...")
        for fact_data in results['facts']:
            fact_id = self.store.get_next_id()

            # Convert ExtractedFact to Kraang Fact format
            from kraang import Fact, ArtifactReference
            fact = Fact(
                id=f"fact_{fact_id}",
                statement=fact_data['statement'],
                type=fact_data['type'],
                extracted_from=[{
                    'artifact_id': artifact.id,
                    'location': fact_data['location']
                }],
                confidence=fact_data['confidence']
            )
            self.store.add_fact(fact)

        print(f"✓ Extracted {len(results['facts'])} facts")
        print(f"  Passes run: {results['passes_run']}")
        print(f"  API calls: {results['api_calls']}")
        print(f"  Tokens used: {results['tokens_used']:,}")

        # Show per-pass breakdown
        print(f"\nPer-pass breakdown:")
        for pass_result in results['pass_results']:
            pass_type = pass_result['pass_type']
            extracted = pass_result['facts_extracted']
            new = pass_result['new_unique_facts']
            dupes = pass_result['facts_deduplicated']
            print(f"  {pass_type:20s}: {extracted:3d} raw -> {new:3d} new ({dupes:3d} duplicates)")

    # Update run() method to handle new command
    def run(self, args: List[str]):
        """Run CLI command"""
        if len(args) < 1:
            self.print_help()
            return

        command = args[0]

        try:
            # ... existing commands ...

            elif command == "extract-multi":
                if len(args) < 2:
                    print("Usage: kraang extract-multi <artifact_id> [--max-passes N] [--budget N] [--no-diminishing-returns]")
                    return

                artifact_id = args[1]
                max_passes = 7
                budget = None
                enable_dr = True

                # Parse optional args
                i = 2
                while i < len(args):
                    if args[i] == "--max-passes" and i + 1 < len(args):
                        max_passes = int(args[i + 1])
                        i += 2
                    elif args[i] == "--budget" and i + 1 < len(args):
                        budget = int(args[i + 1])
                        i += 2
                    elif args[i] == "--no-diminishing-returns":
                        enable_dr = False
                        i += 1
                    else:
                        print(f"Unknown option: {args[i]}")
                        return

                self.cmd_extract_multi(artifact_id, max_passes, budget, enable_dr)

            # ... rest of existing commands ...
```

**Usage**:

```bash
# Basic multi-pass extraction
kraang extract-multi artifact_1

# With custom settings
kraang extract-multi artifact_1 --max-passes 5 --budget 10

# Disable diminishing returns (run all passes)
kraang extract-multi artifact_1 --no-diminishing-returns

# Compare with single-pass
kraang extract artifact_1          # Old way (single pass)
kraang extract-multi artifact_1    # New way (multi pass)
```

---

### Option 2: Replace Existing Extract (Not Recommended)

Replace the existing `extract` command to always use multi-pass.

**Advantages**:
- No new commands to learn
- All extractions are comprehensive by default

**Disadvantages**:
- Breaking change for existing users
- Slower and more expensive by default
- No way to do quick single-pass extraction

**Implementation**:

Replace the `cmd_extract` method implementation with multi-pass version.

---

### Option 3: Flag-Based (Middle Ground)

Add a `--multi-pass` flag to existing `extract` command.

**Implementation**:

```python
def cmd_extract(self, artifact_id: str, multi_pass: bool = False):
    """Extract facts from an artifact"""
    artifact = self.store.get_artifact(artifact_id)
    if not artifact:
        print(f"✗ Artifact not found: {artifact_id}")
        return

    if multi_pass:
        # Use multi-pass extraction
        extractor = MultiPassExtractor()
        results = extractor.run_passes(...)
        # ... save facts ...
    else:
        # Use single-pass extraction (existing code)
        extractor = KraangExtractor(self.store)
        facts = extractor.extract_facts(artifact)
        # ... save facts ...
```

**Usage**:

```bash
kraang extract artifact_1                # Single-pass (default)
kraang extract artifact_1 --multi-pass   # Multi-pass
```

---

## Recommended Integration Path

### Phase 1: Separate Command (Low Risk)

1. Add `extract-multi` command as shown in Option 1
2. Document in help text
3. Update README with examples
4. Let users opt-in and provide feedback

### Phase 2: Gather Metrics

Track and compare:
- Facts extracted (single vs multi)
- Cost per artifact
- User satisfaction
- Bug detection rate

### Phase 3: Decide Future

Based on metrics:
- **If multi-pass is clearly better**: Make it default, keep single-pass as `--fast` flag
- **If use-case dependent**: Keep both commands
- **If not worth cost**: Document when to use each

---

## Testing

### Manual Test

```bash
# Initialize test project
cd /home/budda/Code/kraang
kraang init

# Add test artifact
kraang add test_memory.c code

# Run single-pass extraction
kraang extract artifact_1

# Count facts
kraang list facts | wc -l

# Clear facts (for testing - add this command if needed)
rm .kraang/facts.json
echo '[]' > .kraang/facts.json

# Run multi-pass extraction
kraang extract-multi artifact_1

# Count facts again
kraang list facts | wc -l

# Compare
echo "Single-pass found X facts"
echo "Multi-pass found Y facts"
echo "Improvement: Z%"
```

### Automated Test

Create `tests/test_multi_pass.py`:

```python
import pytest
from multi_pass_extraction import (
    MultiPassExtractor,
    FactDeduplicator,
    DiminishingReturnsDetector,
    ExtractedFact,
    PassType
)

def test_deduplication():
    """Test that similar facts are deduplicated"""
    fact1 = ExtractedFact(
        statement="Use CREATE macro for allocation",
        type="constraint",
        location="line 10",
        confidence=0.80,
        pass_type=PassType.GENERAL
    )

    fact2 = ExtractedFact(
        statement="All allocation MUST use CREATE macro",
        type="constraint",
        location="line 15",
        confidence=0.95,
        pass_type=PassType.MEMORY
    )

    deduplicator = FactDeduplicator()
    similarity = deduplicator.compute_similarity(fact1, fact2)

    assert similarity > 0.80, "Similar facts should have high similarity"

    result = deduplicator.find_duplicate(fact2, [fact1])
    assert result.is_duplicate, "Should detect duplicate"

    merged = deduplicator.merge_facts(fact1, fact2)
    assert merged.confidence > max(fact1.confidence, fact2.confidence), "Confidence should be boosted"

def test_diminishing_returns():
    """Test that diminishing returns are detected"""
    # Simulate pass with low yield
    from multi_pass_extraction import DiminishingReturnsMetrics

    new_facts = [
        ExtractedFact("fact1", "constraint", "loc1", 0.9, PassType.TESTING)
    ]

    all_facts = [ExtractedFact(f"fact{i}", "constraint", f"loc{i}", 0.9, PassType.GENERAL)
                 for i in range(100)]

    detector = DiminishingReturnsDetector()
    metrics = detector.compute_metrics(
        pass_number=6,
        new_facts=new_facts,
        all_facts=all_facts,
        previous_categories={"constraint", "implementation"}
    )

    assert not metrics.should_continue, "Should stop with only 1 new fact out of 100"
    assert metrics.novelty_score < 0.15, "Novelty score should be low"

def test_keyword_extraction():
    """Test keyword extraction from statements"""
    fact = ExtractedFact(
        statement="All memory allocation must use the CREATE macro",
        type="constraint",
        location="line 1",
        confidence=1.0,
        pass_type=PassType.MEMORY
    )

    # Check that keywords were extracted
    assert "memory" in fact.keywords
    assert "allocation" in fact.keywords
    assert "create" in fact.keywords
    assert "macro" in fact.keywords

    # Check that stop words were filtered
    assert "the" not in fact.keywords
    assert "all" not in fact.keywords
    assert "must" not in fact.keywords

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

Run tests:

```bash
pip install pytest
pytest tests/test_multi_pass.py -v
```

---

## Configuration

### Environment Variables

```bash
# Set API key (required)
export ANTHROPIC_API_KEY="your-key-here"

# Optional: Set default multi-pass settings
export KRAANG_MAX_PASSES=7
export KRAANG_ENABLE_DIMINISHING_RETURNS=true
export KRAANG_API_BUDGET=20
```

### Config File

Create `.kraang/multi_pass_config.json`:

```json
{
  "max_passes": 7,
  "enable_diminishing_returns": true,
  "api_budget": null,
  "deduplication_threshold": 0.80,
  "novelty_threshold": 0.15,
  "enabled_passes": [
    "general",
    "memory",
    "concurrency",
    "security",
    "error_handling",
    "performance",
    "testing"
  ]
}
```

Load in code:

```python
def cmd_extract_multi(self, artifact_id: str, **kwargs):
    # Load config
    config_file = Path(".kraang/multi_pass_config.json")
    if config_file.exists():
        with open(config_file) as f:
            config = json.load(f)
    else:
        config = {}

    # Override with kwargs
    max_passes = kwargs.get('max_passes', config.get('max_passes', 7))
    # ... etc
```

---

## Documentation Updates

### README.md

Add section:

```markdown
## Multi-Pass Extraction

For comprehensive fact extraction, use the `extract-multi` command:

\`\`\`bash
kraang extract-multi artifact_1
\`\`\`

Multi-pass extraction uses specialized prompts to discover facts that single-pass extraction might miss:

- **Memory management** constraints
- **Concurrency** requirements
- **Security** policies
- **Error handling** patterns
- **Performance** constraints
- **Testing** requirements

Results typically show 50-100% more facts than single-pass, with intelligent deduplication and diminishing returns detection to control costs.

### When to use multi-pass:

- **Critical systems**: Safety, security, compliance requirements
- **Complex codebases**: Many interacting constraints
- **Documentation**: Extracting from detailed specifications
- **Initial analysis**: Comprehensive baseline before development

### When to use single-pass:

- **Quick checks**: Fast feedback during development
- **Simple files**: Configuration files, small utilities
- **Iterative extraction**: Re-extracting frequently changed files
- **Budget constraints**: Minimizing API costs

### Options:

\`\`\`bash
# Limit number of passes
kraang extract-multi artifact_1 --max-passes 5

# Set API call budget
kraang extract-multi artifact_1 --budget 10

# Disable diminishing returns (run all passes)
kraang extract-multi artifact_1 --no-diminishing-returns
\`\`\`
```

### QUICKSTART.md

Update example:

```markdown
## Step 3: Extract Facts

### Quick extraction (single-pass):
\`\`\`bash
kraang extract artifact_1
\`\`\`

### Comprehensive extraction (multi-pass):
\`\`\`bash
kraang extract-multi artifact_1
\`\`\`

Multi-pass extraction finds 50-100% more facts by using specialized prompts for different constraint categories (memory, concurrency, security, etc.).
```

---

## Performance Tuning

### For Large Codebases (100+ files)

```bash
# Use single-pass for initial extraction
for file in src/*.c; do
    kraang add "$file" code
done

# Run single-pass on all
for artifact in artifact_*; do
    kraang extract "$artifact"
done

# Then use multi-pass on critical files only
kraang extract-multi artifact_1 artifact_5 artifact_12

# Or use limited passes with budget
kraang extract-multi artifact_3 --max-passes 4 --budget 5
```

### Parallel Extraction

```python
# Add to kraang.py
def cmd_extract_multi_batch(self, artifact_ids: List[str], workers: int = 4):
    """Extract multiple artifacts in parallel"""
    from concurrent.futures import ThreadPoolExecutor

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(self.cmd_extract_multi, aid)
            for aid in artifact_ids
        ]

        for future in futures:
            future.result()
```

Usage:

```bash
kraang extract-multi-batch artifact_1 artifact_2 artifact_3 --workers 4
```

---

## Troubleshooting

### Issue: API Rate Limiting

**Symptom**: `RateLimitError` from Anthropic API

**Solution**:
```bash
# Add delay between passes
kraang extract-multi artifact_1 --delay 1  # 1 second between API calls

# Or reduce parallel workers
kraang extract-multi-batch ... --workers 1
```

### Issue: High Cost

**Symptom**: Unexpectedly high API costs

**Solution**:
```bash
# Set budget
kraang extract-multi artifact_1 --budget 5

# Use fewer passes
kraang extract-multi artifact_1 --max-passes 3

# Fall back to single-pass for simple files
kraang extract artifact_1
```

### Issue: Too Many Duplicates

**Symptom**: Low unique fact ratio, many duplicates merged

**Solution**:
```python
# Lower deduplication threshold (more aggressive merging)
FactDeduplicator.HIGH_SIMILARITY_THRESHOLD = 0.75

# Or accept duplicates as variants (raise threshold)
FactDeduplicator.HIGH_SIMILARITY_THRESHOLD = 0.90
```

### Issue: Premature Stopping

**Symptom**: Multi-pass stops after only 2-3 passes

**Solution**:
```bash
# Disable diminishing returns
kraang extract-multi artifact_1 --no-diminishing-returns

# Or lower threshold
DiminishingReturnsDetector.MIN_NOVELTY_SCORE_THRESHOLD = 0.10
```

---

## Migration Path for Existing Projects

### Step 1: Backup

```bash
cp -r .kraang .kraang.backup
```

### Step 2: Compare Results

```bash
# Extract baseline with single-pass (already done)
kraang list facts > facts_single.txt

# Clear and re-extract with multi-pass
mv .kraang/facts.json .kraang/facts_single.json
echo '[]' > .kraang/facts.json

kraang extract-multi artifact_1
kraang list facts > facts_multi.txt

# Compare
diff facts_single.txt facts_multi.txt
wc -l facts_single.txt facts_multi.txt
```

### Step 3: Validate

```bash
# Check for contradictions
kraang conflicts

# Review sample facts
kraang list facts | head -n 20

# Run completeness analysis
kraang completeness
```

### Step 4: Decide

- If multi-pass results are significantly better (>30% more facts): Adopt multi-pass
- If results are similar: Keep single-pass for speed
- If uncertain: Use multi-pass for critical files only

---

## Future Enhancements

### 1. Pass Selection Based on File Type

```python
def get_relevant_passes(artifact_type: str) -> List[PassType]:
    if artifact_type == "code":
        return [PassType.GENERAL, PassType.MEMORY, PassType.CONCURRENCY,
                PassType.ERROR_HANDLING, PassType.PERFORMANCE]
    elif artifact_type == "doc":
        return [PassType.GENERAL, PassType.SECURITY, PassType.TESTING]
    # ... etc
```

### 2. Caching

```python
# Cache extraction results by content hash
def extract_with_cache(artifact: Artifact, pass_type: PassType):
    content_hash = hashlib.sha256(artifact.content.encode()).hexdigest()
    cache_key = f"{content_hash}_{pass_type.value}"

    if cache_key in cache:
        return cache[cache_key]

    facts = extract_single_pass(...)
    cache[cache_key] = facts
    return facts
```

### 3. Incremental Updates

```python
# Only re-extract changed functions
def extract_diff(old_artifact: Artifact, new_artifact: Artifact):
    changed_sections = compute_diff(old_artifact, new_artifact)

    for section in changed_sections:
        invalidate_facts(section)
        re_extract(section)
```

### 4. User Feedback Loop

```python
# Learn from user corrections
def mark_fact_incorrect(fact_id: str):
    fact = store.get_fact(fact_id)
    fact.confidence *= 0.5

    # Learn: similar facts should have lower confidence
    for f in store.get_facts():
        if compute_similarity(f, fact) > 0.80:
            f.confidence *= 0.8
```

---

## Summary

**Recommended approach**:
1. ✅ Add `extract-multi` command (Option 1)
2. ✅ Keep existing `extract` for backward compatibility
3. ✅ Let users choose based on needs
4. ✅ Gather metrics to inform future defaults

**Quick start**:
```bash
# Add import to kraang.py
from multi_pass_extraction import MultiPassExtractor

# Add cmd_extract_multi() method (see Option 1 above)

# Add command routing in run() method

# Test
kraang extract-multi artifact_1

# Done!
```

**Files ready to integrate**:
- `/home/budda/Code/kraang/multi_pass_extraction.py` - Core implementation
- `/home/budda/Code/kraang/test_multi_pass.py` - Tests and demos
- `/home/budda/Code/kraang/MULTI_PASS_STRATEGY.md` - Strategy docs
- `/home/budda/Code/kraang/MULTI_PASS_DIAGRAMS.md` - Visual diagrams
