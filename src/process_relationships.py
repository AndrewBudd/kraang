#!/usr/bin/env python3
"""
Batch process relationship pairs from candidate_pairs.json
Systematically analyzes relationships using kraang.py relate
"""

import json
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Set

def load_json(path: str) -> any:
    """Load JSON from file."""
    with open(path) as f:
        return json.load(f)

def save_json(path: str, data: any):
    """Save JSON to file."""
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def get_processed_pairs(relationships: List[Dict]) -> Set[tuple]:
    """Extract already processed pairs from relationships."""
    processed = set()
    for rel in relationships:
        pair = tuple(sorted([rel['fact_id_1'], rel['fact_id_2']]))
        processed.add(pair)
    return processed

def process_pair(fact1_id: str, fact2_id: str) -> bool:
    """Process a single fact pair using kraang.py relate."""
    try:
        cmd = ['./kraang.py', 'relate', fact1_id, fact2_id]
        result = subprocess.run(
            cmd,
            cwd='/home/budda/Code/kraang',
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout per pair
        )

        # Check for success indicators in output
        if result.returncode == 0:
            # Look for relationship indicators in output
            output = result.stdout.lower()
            if 'supports' in output or 'contradicts' in output or 'extends' in output or 'no relationship' in output:
                return True

        # Check stderr for errors
        if result.stderr:
            if 'error' in result.stderr.lower():
                print(f"  ⚠ Error processing {fact1_id} ↔ {fact2_id}: {result.stderr[:100]}")
                return False

        return True

    except subprocess.TimeoutExpired:
        print(f"  ⏱ Timeout processing {fact1_id} ↔ {fact2_id}")
        return False
    except Exception as e:
        print(f"  ✗ Exception processing {fact1_id} ↔ {fact2_id}: {str(e)}")
        return False

def main():
    """Main processing loop."""
    print("=" * 70)
    print("BATCH RELATIONSHIP PROCESSING")
    print("=" * 70)

    # Load candidate pairs
    pairs_file = '/home/budda/Code/kraang/.kraang/candidate_pairs.json'
    candidate_pairs = load_json(pairs_file)
    print(f"\nLoaded {len(candidate_pairs)} candidate pairs")

    # Load existing relationships
    rel_file = '/home/budda/Code/kraang/.kraang/relationships.json'
    try:
        relationships = load_json(rel_file)
        print(f"Found {len(relationships)} existing relationships")
    except FileNotFoundError:
        relationships = []
        print("No existing relationships found")

    # Get already processed pairs
    processed_pairs = get_processed_pairs(relationships)
    print(f"Already processed: {len(processed_pairs)} pairs")

    # Filter out already processed pairs
    remaining_pairs = []
    for pair in candidate_pairs:
        pair_tuple = tuple(sorted([pair['fact1_id'], pair['fact2_id']]))
        if pair_tuple not in processed_pairs:
            remaining_pairs.append(pair)

    print(f"Remaining to process: {len(remaining_pairs)} pairs")

    if len(remaining_pairs) == 0:
        print("\n✓ All pairs already processed!")
        return

    print(f"\n{'='*70}")
    print("PROCESSING RELATIONSHIPS")
    print(f"{'='*70}\n")

    # Process in batches
    batch_size = 50
    success_count = 0
    error_count = 0
    start_time = time.time()

    for i, pair in enumerate(remaining_pairs, 1):
        fact1_id = pair['fact1_id']
        fact2_id = pair['fact2_id']
        score = pair['score']

        print(f"[{i}/{len(remaining_pairs)}] Processing {fact1_id} ↔ {fact2_id} (score: {score})")

        success = process_pair(fact1_id, fact2_id)

        if success:
            success_count += 1
            print(f"  ✓ Success")
        else:
            error_count += 1

        # Save progress every batch_size items
        if i % batch_size == 0:
            elapsed = time.time() - start_time
            rate = i / elapsed if elapsed > 0 else 0
            remaining_time = (len(remaining_pairs) - i) / rate if rate > 0 else 0

            # Reload relationships to get current count
            try:
                relationships = load_json(rel_file)
            except:
                pass

            print(f"\n{'='*70}")
            print(f"PROGRESS CHECKPOINT (Batch {i//batch_size})")
            print(f"{'='*70}")
            print(f"  Processed: {i}/{len(remaining_pairs)} pairs ({i/len(remaining_pairs)*100:.1f}%)")
            print(f"  Success: {success_count} | Errors: {error_count}")
            print(f"  Total relationships in DB: {len(relationships)}")
            print(f"  Processing rate: {rate:.2f} pairs/sec")
            print(f"  Elapsed time: {elapsed/60:.1f} minutes")
            print(f"  Estimated remaining: {remaining_time/60:.1f} minutes")
            print(f"{'='*70}\n")

            # Brief pause between batches
            time.sleep(2)

    # Final summary
    elapsed = time.time() - start_time

    # Reload final relationships
    try:
        relationships = load_json(rel_file)
    except:
        pass

    print(f"\n{'='*70}")
    print("PROCESSING COMPLETE")
    print(f"{'='*70}")
    print(f"  Total pairs processed: {len(remaining_pairs)}")
    print(f"  Successful: {success_count}")
    print(f"  Errors: {error_count}")
    print(f"  Total relationships in DB: {len(relationships)}")
    print(f"  Total time: {elapsed/60:.1f} minutes")
    print(f"  Average rate: {len(remaining_pairs)/elapsed:.2f} pairs/sec")
    print(f"{'='*70}\n")

if __name__ == '__main__':
    main()
