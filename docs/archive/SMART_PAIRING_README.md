# Smart Pairing Algorithm - Implementation Summary

## Overview

The Smart Pairing Algorithm reduces relationship analysis from O(n²) to a manageable subset by intelligently filtering fact pairs based on multiple heuristics. This implementation achieves a **94.8% cost reduction** while maintaining high-quality relationship discovery.

## Results

### Quantitative Results

```
Total facts:           139
Total possible pairs:  9,591
Candidate pairs:       1,682 (17.5% of total)
Top pairs (budget):    500   (5.2% of total)

Cost:                  $1.50  (vs $28.77 for full analysis)
Savings:               $27.27 (94.8% reduction)
Time estimate:         ~4.2 hours (vs 80 hours)
```

### Quality Metrics

- **66.7%** of pairs are HIGH-priority type combinations (constraint ↔ implementation)
- **52.4%** of pairs are cross-artifact (documentation ↔ code)
- **97.0%** of pairs have domain overlap
- Score range: 15-17 (average: 15.80)

### Filtering Effectiveness

| Filter Stage | Pairs Remaining | Reduction |
|--------------|-----------------|-----------|
| Initial      | 9,591           | 0%        |
| After filtering | 1,682        | 82.5%     |
| After budget | 500             | 94.8%     |

## Usage

### Standalone Tool

Run the smart pairing algorithm on your facts:

```bash
# Basic usage (generates top 500 pairs)
python3 smart_pairing.py

# With custom budget
python3 smart_pairing.py --budget 300

# With minimum score threshold
python3 smart_pairing.py --budget 500 --threshold 10

# With verbose output
python3 smart_pairing.py --verbose

# Custom output file
python3 smart_pairing.py --output my_pairs.json
```

**Output:**
- Generates `.kraang/candidate_pairs.json` with prioritized pairs
- Shows statistics and sample pairs
- Provides cost/time estimates

### As Python Module

Import and use programmatically:

```python
from smart_pairing import SmartPairingAlgorithm
import json

# Load your facts
with open('.kraang/facts.json') as f:
    facts = json.load(f)

# Initialize algorithm
algorithm = SmartPairingAlgorithm(facts)

# Generate pairs
pairs = algorithm.generate_pairs(budget=500, threshold=10)

# Get statistics
stats = algorithm.get_statistics()
print(f"Generated {stats['candidate_pairs']} pairs")
print(f"Reduction: {stats['reduction_ratio']*100:.1f}%")

# Get details for a specific pair
details = algorithm.get_pair_details('fact_2', 'fact_6')
print(details['fact1']['statement'])
print(details['fact2']['statement'])
```

## Algorithm Design

### Core Filtering Rules

1. **Type-Based Priority** (Rule 1)
   - HIGH: constraint ↔ implementation, requirement ↔ implementation, design ↔ implementation
   - MEDIUM: constraint ↔ constraint, constraint ↔ requirement
   - LOW: implementation ↔ implementation

2. **Artifact Priority** (Rule 2)
   - HIGH: Cross-artifact pairs (documentation ↔ code)
   - MEDIUM: Same-artifact pairs

3. **Domain Similarity** (Rule 3)
   - Jaccard similarity on 11 domain categories:
     - memory_management, linked_lists, communication
     - database, docker_dev, code_structure
     - game_mechanics, security_auth, networking
     - lua_scripting, testing_debug

4. **Confidence Filtering** (Rule 4)
   - Skip if both facts < 0.85 confidence
   - Skip if either fact < 0.75 confidence

5. **Location Proximity** (Rule 5)
   - HIGH: Within 50 lines
   - MEDIUM: Within 200 lines
   - LOW: Further apart

6. **Entity Overlap** (Rule 6)
   - Extracts: function names, macros, structs, header files
   - Calculates overlap ratio

### Scoring System

```python
# High priority type pairs
score = 10  # base
score += 5  # if domain overlap
score += 3  # if entity overlap (alternative to domain)

# Cross-artifact pairs
score = 8   # base
score += 5  # if domain overlap
score += 3  # if entity overlap

# Medium priority types
score = 5   # base
score += 5  # if domain AND entity overlap

# Low priority types
score = 3   # base (only if proximity HIGH + domain + entity overlap)

# Proximity bonus
score += 2  # if HIGH proximity
score += 1  # if MEDIUM proximity
```

## File Structure

```
smart_pairing.py              # Main algorithm implementation
test_smart_pairing.py         # Comprehensive test suite
.kraang/candidate_pairs.json  # Generated output (top 500 pairs)
SMART_PAIRING_ALGORITHM.md    # Detailed design document
SMART_PAIRING_README.md       # This file
```

## Testing

Run the comprehensive test suite:

```bash
python3 test_smart_pairing.py
```

**Tests:**
- Domain extraction
- Entity extraction
- Type priority classification
- Algorithm reduction effectiveness
- Score distribution
- High-priority pair identification
- Module interface
- Quality metrics

All 8 tests pass with 100% success rate.

## Sample Output

### Top 5 Pairs

```
1. fact_2 ↔ fact_6 (Score: 17)
   Reasons: high_priority_types, domain_overlap
   Type: HIGH | Artifact: MEDIUM
   Fact 1 (constraint): Local development MUST use Docker Compose exclusively...
   Fact 2 (implementation): Telnet-based connectivity uses port 5656...

2. fact_2 ↔ fact_61 (Score: 17)
   Reasons: high_priority_types, domain_overlap
   Type: HIGH | Artifact: MEDIUM
   Fact 1 (constraint): Local development MUST use Docker Compose exclusively...
   Fact 2 (implementation): Docker services include: mud, db, mosquitto...

3. fact_3 ↔ fact_4 (Score: 17)
   Reasons: high_priority_types, domain_overlap
   Type: HIGH | Artifact: MEDIUM
   Fact 1 (design): LotJ is a MUD (Multi-User Dungeon) game based on Star Wars...
   Fact 2 (implementation): Core game engine is written in C with Lua scripting...
```

## Statistics Breakdown

### Score Distribution (Top 500)
- Score 17: 136 pairs (27.2%)
- Score 16: 128 pairs (25.6%)
- Score 15: 236 pairs (47.2%)

### Reason Distribution
- domain_overlap: 500 pairs (100%)
- high_priority_types: 500 pairs (100%)
- cross_artifact: 205 pairs (41%)
- entity_overlap: Varies

### Type Priority
- HIGH: 500 pairs (100% of top 500)
- MEDIUM: 0 pairs
- LOW: 0 pairs

### Artifact Priority
- HIGH (cross-artifact): 205 pairs (41%)
- MEDIUM (same-artifact): 295 pairs (59%)

## Implementation Features

### Class-Based Interface

The `SmartPairingAlgorithm` class provides:

- `__init__(facts)` - Initialize with fact list
- `generate_pairs(budget, threshold, verbose)` - Generate candidate pairs
- `get_statistics()` - Get comprehensive statistics
- `get_pair_details(fact1_id, fact2_id)` - Get detailed info for a pair

### Standalone Functions

All core functions can be imported individually:

```python
from smart_pairing import (
    extract_domains,
    extract_code_entities,
    get_type_priority,
    calculate_domain_similarity,
    calculate_entity_overlap,
    calculate_location_proximity,
    smart_pairing_algorithm,
)
```

## Next Steps

1. **Run relationship analysis** on the 500 candidate pairs
2. **Monitor relationship density** - aim for 0.5+ (each fact should have ~1 relationship)
3. **Adjust budget** if needed:
   - Increase budget for more coverage
   - Decrease budget for lower cost
4. **Tune threshold** to filter by minimum score
5. **Active learning** - use discovered relationships to improve filtering

## Validation Strategy

After relationship analysis:

1. **Spot-check skipped pairs** - Verify filtered pairs don't have relationships
2. **Domain coverage** - Ensure each domain has sufficient pairs
3. **Relationship density** - Check each fact has appropriate relationships
4. **Manual review** - Review constraints without implementation relationships

## Future Enhancements

### Active Learning
```python
def learn_from_relationships(existing_relationships):
    """Use discovered relationships to improve filtering."""
    # Analyze patterns in successful relationships
    # Adjust scoring weights based on patterns
    # Improve domain keywords and entity extraction
```

### Incremental Analysis
```python
def analyze_new_fact(new_fact, existing_facts):
    """Only analyze new fact against existing facts."""
    # Apply same filtering logic
    # Only generate N new pairs instead of O(N²)
```

## Performance

- **Memory**: ~5MB for 139 facts and 1,682 pairs
- **Runtime**: ~2 seconds for full analysis of 9,591 potential pairs
- **Scalability**: O(n²) iteration but with aggressive filtering

## Troubleshooting

### No pairs generated
- Check fact types (need constraints, requirements, or design + implementation)
- Lower threshold: `--threshold 0`
- Check domain keywords match your facts

### Too many pairs
- Increase threshold: `--threshold 12`
- Decrease budget: `--budget 300`

### Too few pairs
- Decrease threshold: `--threshold 5`
- Increase budget: `--budget 1000`
- Check domain keywords coverage

### Poor quality pairs
- Increase threshold to focus on high-scoring pairs
- Review domain keywords - add more for your specific domain
- Review entity extraction patterns

## Contact & Support

For issues or questions:
1. Check `SMART_PAIRING_ALGORITHM.md` for detailed design
2. Run `python3 test_smart_pairing.py` to verify installation
3. Review sample output and adjust parameters

## License

Part of the Kraang knowledge extraction system.
