# Smart Pairing Algorithm - Quick Start Guide

## 30-Second Start

```bash
# Run with defaults (generates 500 pairs)
python3 smart_pairing.py

# Check the output
cat .kraang/candidate_pairs.json
```

## Common Commands

```bash
# Standard usage (500 pairs)
python3 smart_pairing.py

# Quick test (50 pairs)
python3 smart_pairing.py --budget 50 --threshold 15

# Comprehensive (1000 pairs)
python3 smart_pairing.py --budget 1000 --threshold 10

# Ultra-focused (100 highest quality)
python3 smart_pairing.py --budget 100 --threshold 16

# Custom output
python3 smart_pairing.py --output my_pairs.json

# Verbose mode
python3 smart_pairing.py --verbose
```

## Python Module Usage

```python
from smart_pairing import SmartPairingAlgorithm
import json

# Load facts
with open('.kraang/facts.json') as f:
    facts = json.load(f)

# Generate pairs
algorithm = SmartPairingAlgorithm(facts)
pairs = algorithm.generate_pairs(budget=500, threshold=10)

# Get statistics
stats = algorithm.get_statistics()
print(f"Generated {len(pairs)} pairs")
print(f"Reduction: {(1-stats['reduction_ratio'])*100:.1f}%")
```

## What You Get

**Input:**
- 139 facts from `.kraang/facts.json`
- 9,591 possible pairs (O(n²))

**Output:**
- `.kraang/candidate_pairs.json` with top pairs
- Statistics showing reduction
- Cost/time estimates
- Sample pairs

**Results:**
- 94.8% cost reduction ($28.77 → $1.50)
- 94.8% time reduction (80 hours → 4.2 hours)
- High-quality pairs only (score 15-17)

## Output Format

Each pair in `candidate_pairs.json`:

```json
{
  "fact1_id": "fact_2",
  "fact2_id": "fact_6",
  "score": 17,
  "reasons": ["high_priority_types", "domain_overlap"],
  "type_priority": "HIGH",
  "artifact_priority": "MEDIUM",
  "domain_similarity": 0.5,
  "entity_overlap": 0.0,
  "proximity": "HIGH"
}
```

## Parameters Explained

- **--budget N**: Maximum number of pairs to return (default: 500)
- **--threshold N**: Minimum score to include (default: 0)
- **--output FILE**: Output JSON file (default: .kraang/candidate_pairs.json)
- **--verbose**: Show detailed progress

## Score Guide

- **17**: Highest quality - HIGH priority types + domain overlap + proximity
- **16**: Very high - HIGH priority types + entity overlap + proximity
- **15**: High - HIGH priority types + domain overlap
- **13**: Good - Cross-artifact + domain overlap
- **10-12**: Medium - Various combinations
- **5-9**: Lower - Specific narrow matches

## Typical Workflows

### Quick Exploration
```bash
python3 smart_pairing.py --budget 50 --threshold 15
# Fast: 50 ultra-high-quality pairs
```

### Standard Analysis
```bash
python3 smart_pairing.py
# Default: 500 high-quality pairs, $1.50 cost
```

### Comprehensive Coverage
```bash
python3 smart_pairing.py --budget 1000 --threshold 10
# Broad: 1000 good-quality pairs, $3.00 cost
```

### Deep Dive
```bash
python3 smart_pairing.py --budget 1682 --threshold 5
# All: Every candidate pair, $5.05 cost
```

## Testing

```bash
# Run test suite
python3 test_smart_pairing.py

# Run example
python3 example_smart_pairing.py
```

## Files

- `smart_pairing.py` - Main implementation
- `test_smart_pairing.py` - Test suite
- `example_smart_pairing.py` - Example usage
- `SMART_PAIRING_ALGORITHM.md` - Detailed design
- `SMART_PAIRING_README.md` - Full documentation
- `SMART_PAIRING_VERIFICATION.md` - Verification report
- `SMART_PAIRING_QUICKSTART.md` - This guide

## Next Steps

1. Run: `python3 smart_pairing.py`
2. Review: `.kraang/candidate_pairs.json`
3. Analyze: Use pairs for relationship discovery
4. Tune: Adjust budget/threshold as needed

## Help

```bash
python3 smart_pairing.py --help
```

## Questions?

See full documentation in `SMART_PAIRING_README.md`
