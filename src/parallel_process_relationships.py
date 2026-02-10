#!/usr/bin/env python3
"""
Parallel batch processor for relationship pairs
Uses multiprocessing to analyze multiple pairs simultaneously
"""

import json
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Set
from multiprocessing import Pool, cpu_count
import sys

def load_json(path: str) -> any:
    """Load JSON from file."""
    with open(path) as f:
        return json.load(f)

def get_processed_pairs(relationships: List[Dict]) -> Set[tuple]:
    """Extract already processed pairs from relationships."""
    processed = set()
    for rel in relationships:
        pair = tuple(sorted([rel['fact_id_1'], rel['fact_id_2']]))
        processed.add(pair)
    return processed

def process_single_pair(args):
    """Process a single fact pair using kraang.py relate. Worker function for multiprocessing."""
    fact1_id, fact2_id, pair_num, total = args

    try:
        cmd = ['./kraang.py', 'relate', fact1_id, fact2_id]
        result = subprocess.run(
            cmd,
            cwd='/home/budda/Code/kraang',
            capture_output=True,
            text=True,
            timeout=90  # 90 second timeout per pair
        )

        # Check for success
        success = result.returncode == 0
        output_lower = result.stdout.lower() if result.stdout else ""

        # Look for relationship indicators
        has_relationship = any(word in output_lower for word in
                              ['supports', 'contradicts', 'extends', 'no relationship'])

        status = '✓' if success and has_relationship else '✗'
        return {
            'success': success and has_relationship,
            'fact1': fact1_id,
            'fact2': fact2_id,
            'status': status,
            'pair_num': pair_num,
            'total': total
        }

    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'fact1': fact1_id,
            'fact2': fact2_id,
            'status': '⏱',
            'pair_num': pair_num,
            'total': total
        }
    except Exception as e:
        return {
            'success': False,
            'fact1': fact1_id,
            'fact2': fact2_id,
            'status': '✗',
            'pair_num': pair_num,
            'total': total,
            'error': str(e)
        }

def main():
    """Main parallel processing function."""
    print("=" * 80)
    print("PARALLEL RELATIONSHIP PROCESSING")
    print("=" * 80)

    # Determine optimal worker count (use 50% of CPUs to avoid overload)
    num_workers = max(2, cpu_count() // 2)
    print(f"\nUsing {num_workers} parallel workers (CPU count: {cpu_count()})")

    # Load candidate pairs
    pairs_file = '/home/budda/Code/kraang/.kraang/candidate_pairs.json'
    candidate_pairs = load_json(pairs_file)
    print(f"Loaded {len(candidate_pairs)} candidate pairs")

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

    # Limit to first 200 pairs for this batch (to avoid overwhelming)
    batch_size = 200
    if len(remaining_pairs) > batch_size:
        print(f"\n⚠ Limiting to first {batch_size} pairs for this batch")
        remaining_pairs = remaining_pairs[:batch_size]

    print(f"\n{'='*80}")
    print("PROCESSING RELATIONSHIPS IN PARALLEL")
    print(f"{'='*80}\n")

    # Prepare work items
    work_items = [
        (pair['fact1_id'], pair['fact2_id'], i+1, len(remaining_pairs))
        for i, pair in enumerate(remaining_pairs)
    ]

    # Process in parallel with progress tracking
    start_time = time.time()
    success_count = 0
    error_count = 0

    # Process in smaller batches to show progress
    chunk_size = 20
    chunks = [work_items[i:i+chunk_size] for i in range(0, len(work_items), chunk_size)]

    for chunk_idx, chunk in enumerate(chunks, 1):
        print(f"Processing batch {chunk_idx}/{len(chunks)} ({len(chunk)} pairs)...")

        with Pool(processes=num_workers) as pool:
            results = pool.map(process_single_pair, chunk)

        # Tally results
        for result in results:
            if result['success']:
                success_count += 1
            else:
                error_count += 1

            # Print compact status
            sys.stdout.write(f"{result['status']}")
            sys.stdout.flush()

        print(f" [{success_count + error_count}/{len(work_items)}]")

        # Show progress checkpoint
        elapsed = time.time() - start_time
        rate = (success_count + error_count) / elapsed if elapsed > 0 else 0
        remaining = len(work_items) - (success_count + error_count)
        eta = remaining / rate if rate > 0 else 0

        # Reload relationships to get current count
        try:
            relationships = load_json(rel_file)
            rel_count = len(relationships)
        except:
            rel_count = 0

        print(f"  Progress: {success_count + error_count}/{len(work_items)} pairs " +
              f"| Success: {success_count} | Errors: {error_count}")
        print(f"  Relationships in DB: {rel_count}")
        print(f"  Rate: {rate:.1f} pairs/sec | ETA: {eta/60:.1f} min\n")

        # Brief pause between chunks
        if chunk_idx < len(chunks):
            time.sleep(1)

    # Final summary
    elapsed = time.time() - start_time

    # Reload final relationships
    try:
        relationships = load_json(rel_file)
        final_rel_count = len(relationships)
    except:
        final_rel_count = 0

    print(f"\n{'='*80}")
    print("BATCH PROCESSING COMPLETE")
    print(f"{'='*80}")
    print(f"  Pairs processed: {len(work_items)}")
    print(f"  Successful: {success_count}")
    print(f"  Errors: {error_count}")
    print(f"  Total relationships in DB: {final_rel_count}")
    print(f"  Processing time: {elapsed/60:.1f} minutes")
    print(f"  Average rate: {len(work_items)/elapsed:.2f} pairs/sec")
    print(f"{'='*80}\n")

    # Calculate remaining work
    remaining_total = len(candidate_pairs) - final_rel_count
    if remaining_total > 0:
        print(f"Remaining pairs to process: {remaining_total}")
        print(f"Run this script again to process the next batch")
    else:
        print("✓ All candidate pairs have been processed!")

if __name__ == '__main__':
    main()
