#!/usr/bin/env python3
"""
Test script for multi-pass extraction strategy.

Demonstrates:
1. Running multi-pass extraction on a sample artifact
2. Analyzing deduplication effectiveness
3. Visualizing diminishing returns
4. Comparing single-pass vs multi-pass results
"""

import json
from pathlib import Path
from multi_pass_extraction import (
    MultiPassExtractor,
    ExtractionPromptLibrary,
    FactDeduplicator,
    ExtractedFact,
    PassType
)


def create_sample_artifact():
    """Create a sample C code artifact with various constraint types"""
    return """
/* Memory Management Module
 *
 * This module implements a custom memory allocator with the following constraints:
 * - All allocations MUST use CREATE() macro, never malloc()
 * - All deallocations MUST use DESTROY() macro, never free()
 * - Memory pools have a maximum size of 1MB
 * - Reference counting is used for shared data structures
 *
 * Threading:
 * - This module is NOT thread-safe
 * - Caller must ensure external synchronization
 * - Lock ordering: global_lock must be acquired before pool_lock
 *
 * Security:
 * - All input sizes are validated against MAX_ALLOC_SIZE
 * - Buffer overflows are prevented with bounds checking
 * - No user-controlled sizes are trusted
 *
 * Error Handling:
 * - All functions return NULL on error
 * - errno is set to indicate error type
 * - Callers MUST check return values
 *
 * Performance:
 * - Target allocation time: < 1ms for 95th percentile
 * - Pool lookup is O(1) using hash table
 * - No system calls in fast path
 */

#define MAX_ALLOC_SIZE (1024 * 1024)  // 1MB max allocation
#define MAX_POOL_SIZE (1024 * 1024)   // 1MB pool size

typedef struct memory_pool {
    void *data;
    size_t size;
    size_t used;
    int ref_count;
} memory_pool_t;

/* CREATE macro - must be used for all allocations
 * Never use malloc() directly!
 */
#define CREATE(type) \\
    (type*)pool_allocate(sizeof(type))

/* DESTROY macro - must be used for all deallocations
 * Never use free() directly!
 */
#define DESTROY(ptr) \\
    pool_deallocate(ptr)

/**
 * Allocate memory from pool
 *
 * Returns: Pointer to allocated memory, or NULL on error
 * Errors: Sets errno to ENOMEM if pool exhausted, EINVAL if size invalid
 * Performance: O(1) allocation from pool
 * Thread safety: NOT thread-safe, caller must lock
 */
void* pool_allocate(size_t size) {
    // Validate input size (security constraint)
    if (size == 0 || size > MAX_ALLOC_SIZE) {
        errno = EINVAL;
        return NULL;  // Must return NULL on error
    }

    // Check pool capacity (resource constraint)
    if (pool->used + size > MAX_POOL_SIZE) {
        errno = ENOMEM;
        return NULL;
    }

    // Allocate from pool (O(1) performance)
    void *ptr = pool->data + pool->used;
    pool->used += size;

    return ptr;
}

/**
 * Deallocate memory back to pool
 *
 * Thread safety: NOT thread-safe, caller must lock
 * Reference counting: Decrements ref_count, only frees when count reaches 0
 */
void pool_deallocate(void *ptr) {
    if (!ptr) return;  // Null pointer is safe to deallocate

    // Decrement reference count (memory management)
    pool->ref_count--;

    // Only return to pool if ref_count reaches 0
    if (pool->ref_count == 0) {
        pool->used = 0;  // Reset pool
    }
}

/**
 * Initialize memory pool
 *
 * Requirements:
 * - Must be called before any allocations
 * - Must be called exactly once
 * - Failure to initialize will result in crashes
 *
 * Testing:
 * - Unit tests must verify initialization
 * - Integration tests must verify pool boundaries
 * - Performance tests must verify < 1ms allocation time
 */
int pool_init(void) {
    // Allocate pool storage
    pool = CREATE(memory_pool_t);
    if (!pool) {
        return -1;  // Return -1 on error (error handling convention)
    }

    pool->data = malloc(MAX_POOL_SIZE);  // One-time system malloc allowed for pool
    if (!pool->data) {
        DESTROY(pool);
        return -1;
    }

    pool->size = MAX_POOL_SIZE;
    pool->used = 0;
    pool->ref_count = 1;

    return 0;  // Return 0 on success
}
"""


def demonstrate_single_pass():
    """Show results from single-pass extraction"""
    print("\n" + "="*70)
    print("SINGLE-PASS EXTRACTION (General Prompt Only)")
    print("="*70 + "\n")

    artifact = create_sample_artifact()

    # Create extractor with only general pass
    extractor = MultiPassExtractor(
        max_passes=1,  # Only general pass
        enable_diminishing_returns=False
    )

    results = extractor.run_passes(
        artifact_type="code",
        artifact_path="test_memory.c",
        artifact_content=artifact
    )

    print(f"\nSingle-Pass Results:")
    print(f"  Total Facts: {results['total_facts']}")
    print(f"  API Calls: {results['api_calls']}")
    print(f"  Cost: ~${results['tokens_used'] * 0.000003:.3f}")

    return results


def demonstrate_multi_pass():
    """Show results from multi-pass extraction"""
    print("\n" + "="*70)
    print("MULTI-PASS EXTRACTION (All Specialized Prompts)")
    print("="*70 + "\n")

    artifact = create_sample_artifact()

    # Create extractor with all passes
    extractor = MultiPassExtractor(
        max_passes=7,
        enable_diminishing_returns=True
    )

    results = extractor.run_passes(
        artifact_type="code",
        artifact_path="test_memory.c",
        artifact_content=artifact
    )

    print(f"\nMulti-Pass Results:")
    print(f"  Total Facts: {results['total_facts']}")
    print(f"  API Calls: {results['api_calls']}")
    print(f"  Cost: ~${results['tokens_used'] * 0.000003:.3f}")

    return results


def analyze_deduplication():
    """Demonstrate deduplication algorithm"""
    print("\n" + "="*70)
    print("DEDUPLICATION ANALYSIS")
    print("="*70 + "\n")

    # Create sample facts that should be deduplicated
    fact1 = ExtractedFact(
        statement="All memory allocation MUST use CREATE macro",
        type="constraint",
        location="lines 10-15",
        confidence=0.85,
        pass_type=PassType.GENERAL
    )

    fact2 = ExtractedFact(
        statement="Memory allocation must use CREATE() macro, never malloc()",
        type="constraint",
        location="comment block",
        confidence=0.95,
        pass_type=PassType.MEMORY
    )

    fact3 = ExtractedFact(
        statement="Database connections use pooling",
        type="implementation",
        location="lines 50-60",
        confidence=0.90,
        pass_type=PassType.GENERAL
    )

    # Test similarity
    deduplicator = FactDeduplicator()

    print("Fact 1 (General pass):")
    print(f"  '{fact1.statement}'")
    print(f"  Keywords: {fact1.keywords}\n")

    print("Fact 2 (Memory pass):")
    print(f"  '{fact2.statement}'")
    print(f"  Keywords: {fact2.keywords}\n")

    similarity = deduplicator.compute_similarity(fact1, fact2)
    print(f"Similarity Score: {similarity:.3f}")

    result = deduplicator.find_duplicate(fact2, [fact1])
    print(f"Is Duplicate: {result.is_duplicate}")
    print(f"Reason: {result.reason}\n")

    if result.is_duplicate:
        merged = deduplicator.merge_facts(fact1, fact2)
        print("Merged Fact:")
        print(f"  Statement: '{merged.statement}'")
        print(f"  Confidence: {merged.confidence:.2f} (boosted from {max(fact1.confidence, fact2.confidence):.2f})")
        print(f"  Keywords: {merged.keywords}")

    print("\n" + "-"*70 + "\n")

    print("Fact 1 vs Fact 3:")
    similarity = deduplicator.compute_similarity(fact1, fact3)
    print(f"Similarity Score: {similarity:.3f}")
    result = deduplicator.find_duplicate(fact3, [fact1])
    print(f"Is Duplicate: {result.is_duplicate}")
    print(f"Reason: {result.reason}")


def visualize_diminishing_returns():
    """Visualize diminishing returns across passes"""
    print("\n" + "="*70)
    print("DIMINISHING RETURNS VISUALIZATION")
    print("="*70 + "\n")

    # Simulate realistic pass results
    passes = [
        {"pass": 1, "name": "General", "raw": 35, "new": 35, "dupes": 0},
        {"pass": 2, "name": "Memory", "raw": 22, "new": 15, "dupes": 7},
        {"pass": 3, "name": "Concurrency", "raw": 12, "new": 8, "dupes": 4},
        {"pass": 4, "name": "Security", "raw": 8, "new": 4, "dupes": 4},
        {"pass": 5, "name": "Error", "raw": 10, "new": 5, "dupes": 5},
        {"pass": 6, "name": "Performance", "raw": 5, "new": 2, "dupes": 3},
        {"pass": 7, "name": "Testing", "raw": 3, "new": 1, "dupes": 2},
    ]

    total_facts = 0

    print("Pass | Name         | Raw | New | Dupes | Total | Novelty | Continue?")
    print("-" * 75)

    for p in passes:
        total_facts += p["new"]

        # Simple novelty calculation
        if p["new"] >= 10:
            novelty = 1.0
        elif p["new"] >= 5:
            novelty = 0.5 + (p["new"] - 5) * 0.1
        elif p["new"] >= 2:
            novelty = 0.2 + (p["new"] - 2) * 0.1
        else:
            novelty = p["new"] * 0.1

        should_continue = novelty >= 0.15 and p["new"] >= 2

        print(f"{p['pass']:4d} | {p['name']:12s} | {p['raw']:3d} | {p['new']:3d} | "
              f"{p['dupes']:5d} | {total_facts:5d} | {novelty:7.2f} | "
              f"{'Yes' if should_continue else 'STOP'}")

        if not should_continue:
            print("\n✓ Diminishing returns detected - would stop here")
            break

    print("\n" + "-"*70 + "\n")

    # Show the value curve
    print("Cumulative Facts Over Passes:")
    cumulative = 0
    for p in passes[:6]:  # Exclude last pass that would be stopped
        cumulative += p["new"]
        bar_length = cumulative // 2
        print(f"Pass {p['pass']}: {'█' * bar_length} {cumulative}")


def compare_strategies():
    """Compare single-pass vs multi-pass"""
    print("\n" + "="*70)
    print("STRATEGY COMPARISON")
    print("="*70 + "\n")

    # Simulated results (would come from actual extraction in production)
    single_pass = {
        "facts": 35,
        "api_calls": 1,
        "cost": 0.06,
        "categories": {"constraint": 12, "implementation": 18, "requirement": 5}
    }

    multi_pass = {
        "facts": 70,
        "api_calls": 7,
        "cost": 0.42,
        "categories": {
            "constraint": 28,
            "implementation": 25,
            "requirement": 12,
            "design": 5
        }
    }

    print("Metric                    | Single-Pass | Multi-Pass  | Delta")
    print("-" * 70)
    print(f"Total Facts              | {single_pass['facts']:11d} | {multi_pass['facts']:11d} | +{multi_pass['facts'] - single_pass['facts']:3d} (+{100 * (multi_pass['facts'] - single_pass['facts']) / single_pass['facts']:.0f}%)")
    print(f"API Calls                | {single_pass['api_calls']:11d} | {multi_pass['api_calls']:11d} | +{multi_pass['api_calls'] - single_pass['api_calls']:3d} (×{multi_pass['api_calls'] / single_pass['api_calls']:.1f})")
    print(f"Cost (USD)               | ${single_pass['cost']:10.2f} | ${multi_pass['cost']:10.2f} | +${multi_pass['cost'] - single_pass['cost']:.2f} (×{multi_pass['cost'] / single_pass['cost']:.1f})")

    print("\nFact Categories:")
    all_categories = set(single_pass['categories'].keys()) | set(multi_pass['categories'].keys())
    for cat in sorted(all_categories):
        s = single_pass['categories'].get(cat, 0)
        m = multi_pass['categories'].get(cat, 0)
        delta = m - s
        print(f"  {cat:20s} | {s:11d} | {m:11d} | {delta:+4d}")

    incremental_facts = multi_pass['facts'] - single_pass['facts']
    incremental_cost = multi_pass['cost'] - single_pass['cost']
    cost_per_fact = incremental_cost / incremental_facts if incremental_facts > 0 else 0

    print(f"\nValue Analysis:")
    print(f"  Incremental Facts: {incremental_facts}")
    print(f"  Incremental Cost: ${incremental_cost:.2f}")
    print(f"  Cost per Incremental Fact: ${cost_per_fact:.3f}")

    print(f"\nConclusion:")
    print(f"  Multi-pass extraction provides {100 * incremental_facts / single_pass['facts']:.0f}% more facts")
    print(f"  at {100 * (multi_pass['cost'] / single_pass['cost'] - 1):.0f}% higher cost.")
    print(f"  The additional facts include critical constraints in:")
    print(f"    - Memory management (+{multi_pass['categories']['constraint'] - single_pass['categories']['constraint']} constraints)")
    print(f"    - Implementation details (+{multi_pass['categories']['implementation'] - single_pass['categories']['implementation']} implementations)")
    print(f"    - Requirements (+{multi_pass['categories']['requirement'] - single_pass['categories']['requirement']} requirements)")


def main():
    """Run all demonstrations"""
    print("\n" + "="*70)
    print("MULTI-PASS EXTRACTION STRATEGY DEMONSTRATION")
    print("="*70)

    print("\nThis demonstration shows:")
    print("1. Deduplication algorithm in action")
    print("2. Diminishing returns detection")
    print("3. Single-pass vs multi-pass comparison")
    print("4. Value analysis\n")

    input("Press Enter to continue...")

    # Run demonstrations
    analyze_deduplication()

    input("\nPress Enter to continue...")

    visualize_diminishing_returns()

    input("\nPress Enter to continue...")

    compare_strategies()

    print("\n" + "="*70)
    print("DEMONSTRATION COMPLETE")
    print("="*70)

    print("\nTo run real extraction:")
    print("  python multi_pass_extraction.py <file_path>")
    print("\nTo integrate with Kraang:")
    print("  See integration instructions in MULTI_PASS_STRATEGY.md")


if __name__ == "__main__":
    main()
