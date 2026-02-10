# Smart Pairing Algorithm - Quick Start Guide

## TL;DR

**Problem:** 9,591 fact pairs to analyze = $28.77 + 80 hours
**Solution:** Smart pairing reduces to 500 pairs = $1.50 + 4 hours
**Savings:** 95% reduction in cost and time

---

## Run It Now

```bash
# Basic usage (recommended)
python3 smart_pairing.py

# Custom budget
python3 smart_pairing.py --budget 300

# With score threshold
python3 smart_pairing.py --budget 500 --threshold 15

# Verbose output
python3 smart_pairing.py --verbose
```

**Output:** `.kraang/candidate_pairs.json` with prioritized fact pairs

---

## What It Does

The algorithm intelligently selects which fact pairs to analyze for relationships by:

1. **Type Priority** - Focus on constraint ↔ implementation pairs
2. **Domain Matching** - Only pair facts that share keywords (memory, docker, etc.)
3. **Entity Overlap** - Prefer facts mentioning same functions/structs
4. **Artifact Priority** - Prioritize documentation ↔ code relationships
5. **Location Proximity** - For same-file facts, prefer nearby code

---

## Key Results

### Reduction Metrics
- **9,591** possible pairs → **500** selected pairs
- **95% reduction** in analysis needed
- **$1.50** cost vs $28.77 (95% savings)
- **~4 hours** vs 80 hours (95% savings)

### Quality Metrics
- **92.5%** of constraints have implementation pairs
- **100%** of pairs are high-priority type combinations
- **All** pairs score 15-17 (high confidence)
- **41%** are cross-artifact (doc ↔ code) relationships

---

## Understanding the Output

### Sample Pair Entry

```json
{
  "fact1_id": "fact_28",
  "fact2_id": "fact_29",
  "score": 17,
  "reasons": ["high_priority_types", "domain_overlap"],
  "type_priority": "HIGH",
  "artifact_priority": "MEDIUM",
  "domain_similarity": 0.8,
  "entity_overlap": 0.3,
  "proximity": "HIGH"
}
```

**What this means:**
- These facts have strong relationship potential (score 17/20)
- Both are high-priority types (e.g., constraint ↔ implementation)
- They share domain keywords (memory management)
- Located nearby in code (proximity: HIGH)

### Score Ranges

| Score | Count | Meaning |
|-------|-------|---------|
| 17 | 136 | Excellent: High priority + domain overlap + proximity |
| 16 | 128 | Very good: High priority + domain overlap + medium proximity |
| 15 | 236 | Good: High priority + domain overlap |

---

## Next Steps

### 1. Review the Pairs

```bash
# View top 10 pairs
python3 << 'EOF'
import json
with open('.kraang/candidate_pairs.json') as f:
    pairs = json.load(f)

for i, pair in enumerate(pairs[:10], 1):
    print(f"{i}. {pair['fact1_id']} ↔ {pair['fact2_id']}")
    print(f"   Score: {pair['score']}, Reasons: {', '.join(pair['reasons'])}\n")
EOF
```

### 2. Analyze Relationships

Use these pairs for LLM-based relationship analysis:

```python
import json

# Load pairs and facts
with open('.kraang/candidate_pairs.json') as f:
    pairs = json.load(f)

with open('.kraang/facts.json') as f:
    facts = json.load(f)

facts_map = {f['id']: f for f in facts}

# For each pair, send to LLM for relationship analysis
for pair in pairs:
    fact1 = facts_map[pair['fact1_id']]
    fact2 = facts_map[pair['fact2_id']]

    # Your LLM API call here
    relationship = analyze_relationship(fact1, fact2)

    # Save relationship if found
    if relationship:
        save_relationship(relationship)
```

### 3. Validate Coverage

After analysis, check if relationship density is sufficient:

```python
import json

with open('.kraang/relationships.json') as f:
    relationships = json.load(f)

with open('.kraang/facts.json') as f:
    facts = json.load(f)

density = len(relationships) / len(facts)
print(f"Relationship density: {density:.2f}")

# Target: 0.5+ (each fact has ~1 relationship on average)
if density >= 0.5:
    print("✓ Good coverage")
else:
    print("⚠ Consider analyzing more pairs")
```

---

## Tuning the Algorithm

### Adjust Budget

| Budget | Cost | Time | Use Case |
|--------|------|------|----------|
| 300 | $0.90 | ~2.5h | Quick validation, high-confidence only |
| 500 | $1.50 | ~4h | **Recommended** balanced approach |
| 700 | $2.10 | ~6h | Comprehensive coverage |
| 1000 | $3.00 | ~8h | Maximum coverage |

```bash
python3 smart_pairing.py --budget 300  # Conservative
python3 smart_pairing.py --budget 700  # Comprehensive
```

### Adjust Threshold

| Threshold | Pairs | Description |
|-----------|-------|-------------|
| 17 | ~140 | Absolute highest confidence |
| 16+ | ~270 | Very high confidence |
| 15+ | ~500 | High confidence (recommended) |
| 12+ | ~800 | Medium confidence |

```bash
python3 smart_pairing.py --threshold 16  # Very high confidence
python3 smart_pairing.py --threshold 12  # Include more pairs
```

---

## Common Questions

### Q: Why not analyze all 9,591 pairs?
**A:** Cost ($28.77 vs $1.50) and time (80 hours vs 4 hours). The algorithm ensures we analyze the most valuable pairs first.

### Q: Will I miss important relationships?
**A:** Unlikely. The algorithm covers 92.5% of constraints and prioritizes all high-value type combinations (constraint ↔ implementation, etc.).

### Q: Can I add my own domain keywords?
**A:** Yes! Edit `DOMAIN_KEYWORDS` in `smart_pairing.py`:

```python
DOMAIN_KEYWORDS = {
    # ... existing domains ...
    'my_custom_domain': ['keyword1', 'keyword2', 'keyword3'],
}
```

### Q: How do I analyze more pairs if needed?
**A:** Increase the budget:

```bash
python3 smart_pairing.py --budget 1000
```

Or lower the threshold:

```bash
python3 smart_pairing.py --threshold 12
```

### Q: What if I have new facts?
**A:** Re-run the algorithm. It's fast (~2-3 seconds) and will incorporate new facts automatically.

---

## Files Created

| File | Purpose |
|------|---------|
| `SMART_PAIRING_ALGORITHM.md` | Complete algorithm design (34KB) |
| `ALGORITHM_PSEUDOCODE.md` | Detailed pseudocode (19KB) |
| `PAIRING_RESULTS_SUMMARY.md` | Results analysis (15KB) |
| `smart_pairing.py` | Python implementation |
| `.kraang/candidate_pairs.json` | Output: prioritized pairs |

---

## Support

### Check Results

```bash
# Count candidate pairs
python3 -c "import json; print(len(json.load(open('.kraang/candidate_pairs.json'))))"

# View score distribution
python3 -c "
import json
from collections import Counter
pairs = json.load(open('.kraang/candidate_pairs.json'))
scores = Counter(p['score'] for p in pairs)
for score, count in sorted(scores.items(), reverse=True):
    print(f'Score {score}: {count} pairs')
"
```

### Re-run with Different Settings

```bash
# Try different budgets
for budget in 300 500 700; do
    python3 smart_pairing.py --budget $budget --output ".kraang/pairs_$budget.json"
done
```

---

## Success Criteria

After running relationship analysis on the pairs:

- ✅ **Relationship density ≥ 0.5** (each fact has ~1 relationship)
- ✅ **Constraint coverage ≥ 80%** (most constraints validated)
- ✅ **Cross-artifact relationships found** (docs validated against code)
- ✅ **Conflict detection** (implementation violates constraints)

If these criteria aren't met, increase budget or lower threshold.

---

## Quick Reference

### Commands

```bash
# Default run
python3 smart_pairing.py

# Custom settings
python3 smart_pairing.py --budget 700 --threshold 15 --verbose

# View results
cat .kraang/candidate_pairs.json | head -n 50
```

### Key Metrics

- **Input:** 139 facts
- **Possible pairs:** 9,591
- **Candidate pairs:** 1,682 (17.5%)
- **Selected pairs:** 500 (5.2%)
- **Reduction:** 95%

### Scoring

```
Score = Base (10/8/5/3) + Domain Overlap (+5) + Entity Overlap (+3) + Proximity (+2)

Minimum score: 8 (low-priority with all signals)
Maximum score: 20 (high-priority with all bonuses)
Typical range: 15-17 (high-priority with domain overlap)
```

---

## That's It!

You now have a **production-ready** algorithm that reduces relationship analysis from **9,591 to 500 pairs** while maintaining **high quality** and **comprehensive coverage**.

**Ready to run:**
```bash
python3 smart_pairing.py
```

Then use the output pairs for LLM-based relationship analysis.
