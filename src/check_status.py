#!/usr/bin/env python3
"""Quick status check for relationship processing"""

import json
import time
from datetime import datetime

def load_json(path):
    with open(path) as f:
        return json.load(f)

# Load data
relationships = load_json('/home/budda/Code/kraang/.kraang/relationships.json')
candidate_pairs = load_json('/home/budda/Code/kraang/.kraang/candidate_pairs.json')

rel_count = len(relationships)
total_pairs = len(candidate_pairs)
progress_pct = (rel_count / total_pairs * 100) if total_pairs > 0 else 0

# Count relationship types
type_counts = {}
for r in relationships:
    rtype = r['type']
    type_counts[rtype] = type_counts.get(rtype, 0) + 1

print("=" * 60)
print(f"RELATIONSHIP PROCESSING STATUS - {datetime.now().strftime('%H:%M:%S')}")
print("=" * 60)
print(f"  Relationships found: {rel_count:4d} / {total_pairs} pairs")
print(f"  Progress:            {progress_pct:5.1f}%")
print(f"  Remaining:           {total_pairs - rel_count:4d} pairs")
print()
print("  Type distribution:")
for rtype, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
    pct = count / rel_count * 100 if rel_count > 0 else 0
    print(f"    {rtype:12s}: {count:3d} ({pct:4.1f}%)")
print("=" * 60)
