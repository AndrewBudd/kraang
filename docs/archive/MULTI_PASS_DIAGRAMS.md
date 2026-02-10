# Multi-Pass Extraction: Visual Diagrams

## Workflow Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    START: Multi-Pass Extraction                 │
│                                                                   │
│  Input: Artifact (code, docs, config)                           │
│  Config: max_passes, budget, enable_diminishing_returns          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  PASS 1: GENERAL                                                 │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ 1. Format general prompt with artifact content            │ │
│  │ 2. Call Claude API                                        │ │
│  │ 3. Parse JSON response → 42 raw facts                     │ │
│  │ 4. Deduplicate against existing (empty) → 42 new facts    │ │
│  │ 5. Compute novelty: 1.00 → CONTINUE                       │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  Facts: 42 | New: 42 | Dupes: 0 | Novelty: 1.00                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  PASS 2: MEMORY MANAGEMENT                                       │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ 1. Format memory-specific prompt                          │ │
│  │ 2. Call Claude API                                        │ │
│  │ 3. Parse JSON response → 28 raw facts                     │ │
│  │ 4. Deduplicate:                                           │ │
│  │    - "Use CREATE macro" (0.92 sim) → MERGE with fact_5   │ │
│  │    - "Pool max 1MB" (0.35 sim) → NEW fact_43             │ │
│  │    - ... → 18 new, 10 duplicates                          │ │
│  │ 5. Compute novelty: 0.72 → CONTINUE                       │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  Facts: 60 | New: 18 | Dupes: 10 | Novelty: 0.72                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  PASS 3: CONCURRENCY                                             │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ 1. Format concurrency-specific prompt                     │ │
│  │ 2. Call Claude API                                        │ │
│  │ 3. Parse JSON response → 15 raw facts                     │ │
│  │ 4. Deduplicate → 8 new, 7 duplicates                      │ │
│  │ 5. Compute novelty: 0.48 → CONTINUE                       │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  Facts: 68 | New: 8 | Dupes: 7 | Novelty: 0.48                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                            [...]
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  PASS 6: PERFORMANCE                                             │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ 1. Format performance-specific prompt                     │ │
│  │ 2. Call Claude API                                        │ │
│  │ 3. Parse JSON response → 5 raw facts                      │ │
│  │ 4. Deduplicate → 2 new, 3 duplicates                      │ │
│  │ 5. Compute novelty: 0.16 → CONTINUE (borderline)          │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  Facts: 79 | New: 2 | Dupes: 3 | Novelty: 0.16                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  PASS 7: TESTING                                                 │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ 1. Format testing-specific prompt                         │ │
│  │ 2. Call Claude API                                        │ │
│  │ 3. Parse JSON response → 3 raw facts                      │ │
│  │ 4. Deduplicate → 1 new, 2 duplicates                      │ │
│  │ 5. Compute novelty: 0.09 → STOP (below 0.15 threshold)   │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  Facts: 80 | New: 1 | Dupes: 2 | Novelty: 0.09 ⚠ STOP          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    COMPLETE: Results Ready                       │
│                                                                   │
│  Total Facts: 80 unique facts                                    │
│  Total Passes: 7                                                 │
│  API Calls: 7                                                    │
│  Reason: Diminishing returns detected                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## Deduplication Algorithm Flow

```
┌──────────────────────────────────────────────────────────────────┐
│  New Fact from Pass N                                            │
│  "All memory allocation MUST use CREATE macro, not malloc"       │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  Step 1: Normalize Statement                                     │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  • Lowercase                                               │ │
│  │  • Remove extra whitespace                                 │ │
│  │  • Remove trailing punctuation                             │ │
│  │                                                              │ │
│  │  Result: "all memory allocation must use create macro      │ │
│  │           not malloc"                                       │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  Step 2: Extract Keywords                                        │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  • Filter stop words (the, a, must, etc.)                  │ │
│  │  • Keep words with length >= 3                             │ │
│  │                                                              │ │
│  │  Keywords: {memory, allocation, create, macro, malloc}     │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  Step 3: Compare Against Existing Facts                          │
│                                                                    │
│  For each existing fact:                                          │
└──────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
        ┌─────────────────┐   ┌─────────────────┐
        │   Existing #5   │   │  Existing #12   │
        │   "Use CREATE   │   │  "Lock ordering │
        │    for alloc"   │   │   must be..."   │
        └─────────────────┘   └─────────────────┘
                    │                   │
                    ▼                   ▼
        ┌─────────────────────────────────────────┐
        │  Compute Similarity                     │
        │  ┌───────────────────────────────────┐ │
        │  │ String Similarity (60% weight)    │ │
        │  │   SequenceMatcher: 0.88           │ │
        │  │                                     │ │
        │  │ Keyword Overlap (30% weight)      │ │
        │  │   Jaccard: 4/6 = 0.67             │ │
        │  │                                     │ │
        │  │ Type Match Bonus (+0.10)          │ │
        │  │   Both "constraint" → +0.10       │ │
        │  │                                     │ │
        │  │ Location Bonus (+0.05)            │ │
        │  │   Different → +0.00                │ │
        │  │                                     │ │
        │  │ Combined: 0.60*0.88 + 0.30*0.67   │ │
        │  │           + 0.10 + 0.00 = 0.83    │ │
        │  └───────────────────────────────────┘ │
        │                                         │
        │  Result: 0.83 (HIGH SIMILARITY)        │
        └─────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │  Decision: DUPLICATE (>= 0.80)         │
        └─────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  Step 4: Merge Facts                                             │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Existing #5:                                              │ │
│  │    Statement: "Use CREATE for alloc"                       │ │
│  │    Confidence: 0.80                                        │ │
│  │    Keywords: {create, alloc}                               │ │
│  │                                                              │ │
│  │  New Fact:                                                 │ │
│  │    Statement: "All memory allocation MUST use CREATE..."   │ │
│  │    Confidence: 0.95                                        │ │
│  │    Keywords: {memory, allocation, create, macro, malloc}   │ │
│  │                                                              │ │
│  │  Merged:                                                   │ │
│  │    Statement: "All memory allocation MUST use CREATE..."   │ │
│  │              (higher confidence → keep new statement)      │ │
│  │    Confidence: 1.00 (max(0.80, 0.95) + 0.05 boost)        │ │
│  │    Keywords: {memory, allocation, create, macro,           │ │
│  │               malloc, alloc} (union)                        │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  Result: Existing fact #5 updated with merged information        │
│  Deduplication count: +1                                         │
└──────────────────────────────────────────────────────────────────┘
```

---

## Diminishing Returns Detection

```
                     NOVELTY SCORE CALCULATION

┌──────────────────────────────────────────────────────────────────┐
│  Input Metrics from Pass N                                       │
│  • new_facts: 4                                                  │
│  • total_facts: 75                                               │
│  • new_categories: {design}                                      │
│  • previous_categories: {constraint, implementation, requirement}│
└──────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
        ┌─────────────────┐   ┌─────────────────┐
        │  Fact Score     │   │  Category Score │
        │  (60% weight)   │   │  (25% weight)   │
        └─────────────────┘   └─────────────────┘
                    │                   │
                    ▼                   ▼
        ┌─────────────────┐   ┌─────────────────┐
        │ 4 new facts     │   │ 1 new category  │
        │                 │   │                 │
        │ Score curve:    │   │ 1 × 0.2 = 0.2   │
        │ 2-4 facts →     │   │                 │
        │ 0.2 + (4-2)*0.1 │   │                 │
        │ = 0.4           │   │                 │
        └─────────────────┘   └─────────────────┘
                    │                   │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  Unique Ratio   │
                    │  (15% weight)   │
                    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  4 / 75 = 0.05  │
                    └─────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  Combined Novelty Score                                          │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  novelty = 0.60 × 0.4 + 0.25 × 0.2 + 0.15 × 0.05          │ │
│  │          = 0.24 + 0.05 + 0.008                              │ │
│  │          = 0.298 ≈ 0.30                                     │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  Decision Logic                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Check 1: new_facts < 2?                                   │ │
│  │           4 < 2 → NO                                        │ │
│  │                                                              │ │
│  │  Check 2: novelty_score < 0.15?                            │ │
│  │           0.30 < 0.15 → NO                                  │ │
│  │                                                              │ │
│  │  Check 3: pass_number >= 7?                                │ │
│  │           5 >= 7 → NO                                       │ │
│  │                                                              │ │
│  │  Result: CONTINUE                                           │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘


                     STOPPING DECISION EXAMPLE

┌──────────────────────────────────────────────────────────────────┐
│  Input Metrics from Pass 7                                       │
│  • new_facts: 1                                                  │
│  • total_facts: 80                                               │
│  • new_categories: {} (none)                                     │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  Score Calculation                                               │
│  • fact_score: 1 × 0.1 = 0.1                                     │
│  • category_score: 0 × 0.2 = 0.0                                 │
│  • unique_ratio: 1/80 = 0.0125                                   │
│  • novelty: 0.60×0.1 + 0.25×0.0 + 0.15×0.0125 = 0.062          │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│  Decision Logic                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Check 1: new_facts < 2?                                   │ │
│  │           1 < 2 → YES ✗ FAIL                               │ │
│  │                                                              │ │
│  │  Check 2: novelty_score < 0.15?                            │ │
│  │           0.062 < 0.15 → YES ✗ FAIL                        │ │
│  │                                                              │ │
│  │  Result: STOP                                               │ │
│  │  Reason: "Only 1 new facts (threshold: 2);                 │ │
│  │           Low novelty score 0.06 (threshold: 0.15)"        │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

---

## Pass Progression Visualization

```
                     FACTS EXTRACTED PER PASS

Pass 1 (General)       ████████████████████████████████████ 42 new
                       (42 total)

Pass 2 (Memory)        ███████████████████ 18 new (10 dupes)
                       (60 total)

Pass 3 (Concurrency)   ████████ 8 new (7 dupes)
                       (68 total)

Pass 4 (Security)      ████ 4 new (4 dupes)
                       (72 total)

Pass 5 (Error)         ██████ 5 new (5 dupes)
                       (77 total)

Pass 6 (Performance)   ██ 2 new (3 dupes)
                       (79 total)

Pass 7 (Testing)       █ 1 new (2 dupes) ← STOP
                       (80 total)


                     NOVELTY SCORE DECAY

 1.00 │ ●                   Pass 1: Perfect novelty
      │
 0.80 │   ●                 Pass 2: Strong novelty
      │
 0.60 │     ●               Pass 3: Moderate novelty
      │
 0.40 │       ●             Pass 4: Declining novelty
      │         ●           Pass 5: Low novelty
 0.20 │           ●         Pass 6: Near threshold
      │ ─ ─ ─ ─ ─ ─ ○ ─ ─  Pass 7: Below threshold (0.15) → STOP
 0.00 └───┴───┴───┴───┴───┴───┴───┴───
       1   2   3   4   5   6   7   8   Pass Number


                     DEDUPLICATION RATE

100% │               ┌───┬───┐
     │               │ 3 │ 2 │           Duplicates (red)
 75% │           ┌───┼───┼───┤           New facts (green)
     │       ┌───┤ 5 │ 3 │   │
 50% │   ┌───┤ 7 ├───┤   │   │
     │   │10 ├───┤   │   │   │
 25% │   ├───┤   │   │   │   │
     │   │   │   │   │   │   │
  0% └───┴───┴───┴───┴───┴───┴───
       2   3   4   5   6   7      Pass Number
```

---

## Cost vs. Value Analysis

```
                     SINGLE-PASS vs MULTI-PASS

SINGLE-PASS (General Only)
┌────────────────────────────────────────────────────────────┐
│                                                            │
│  API Calls: 1                                              │
│  Cost: $0.06                                               │
│                                                            │
│  Facts Extracted: ██████████████████████████ 42            │
│                                                            │
│  Categories:                                               │
│    Constraint:      ████████ 12                            │
│    Implementation:  ████████████ 18                        │
│    Requirement:     ████ 5                                 │
│    Design:          0                                      │
│                                                            │
└────────────────────────────────────────────────────────────┘


MULTI-PASS (All Specialized)
┌────────────────────────────────────────────────────────────┐
│                                                            │
│  API Calls: 7                                              │
│  Cost: $0.42                                               │
│                                                            │
│  Facts Extracted: ████████████████████████████████████████ 80 │
│                                                            │
│  Categories:                                               │
│    Constraint:      ████████████████████ 28 (+16)          │
│    Implementation:  ██████████████████ 25 (+7)             │
│    Requirement:     ████████ 12 (+7)                       │
│    Design:          ████ 5 (+5)                            │
│                                                            │
└────────────────────────────────────────────────────────────┘


INCREMENTAL VALUE
┌────────────────────────────────────────────────────────────┐
│                                                            │
│  Additional Facts: 38 (+90%)                               │
│  Additional Cost: $0.36 (6× more)                          │
│  Cost per Incremental Fact: $0.009                         │
│                                                            │
│  Critical Facts Missed by Single-Pass:                     │
│    • 16 additional constraints                             │
│    • 7 additional requirements                             │
│    • 5 design decisions                                    │
│                                                            │
│  ROI: High - prevents bugs, security issues, violations    │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## State Transitions

```
┌────────────────────────────────────────────────────────────────┐
│                   EXTRACTOR STATE MACHINE                      │
└────────────────────────────────────────────────────────────────┘

         ┌─────────┐
    ────→│ INITIAL │
         └─────────┘
              │
              │ init()
              ▼
         ┌──────────┐
         │ READY    │
         └──────────┘
              │
              │ start_pass()
              ▼
    ┌────────────────────┐
    │ EXTRACTING         │◄────────┐
    │                    │         │
    │ • Format prompt    │         │ more passes needed
    │ • Call API         │         │
    │ • Parse response   │         │
    └────────────────────┘         │
              │                    │
              │ extract_complete   │
              ▼                    │
    ┌────────────────────┐         │
    │ DEDUPLICATING      │         │
    │                    │         │
    │ • Compare facts    │         │
    │ • Merge duplicates │         │
    │ • Update fact base │         │
    └────────────────────┘         │
              │                    │
              │ dedup_complete     │
              ▼                    │
    ┌────────────────────┐         │
    │ ANALYZING          │         │
    │                    │         │
    │ • Compute metrics  │         │
    │ • Check thresholds │         │
    │ • Decide continue  │         │
    └────────────────────┘         │
              │                    │
              │                    │
         ┌────┴────┐               │
         ▼         ▼               │
    ┌────────┐  ┌────────┐         │
    │ STOP   │  │CONTINUE├─────────┘
    └────────┘  └────────┘
         │
         │ finalize()
         ▼
    ┌─────────┐
    │COMPLETE │
    └─────────┘
```

---

## Architecture Integration

```
┌──────────────────────────────────────────────────────────────────┐
│                      KRAANG ARCHITECTURE                         │
│                  (with Multi-Pass Integration)                   │
└──────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│                         Kraang CLI                             │
│                                                                 │
│  Commands:                                                      │
│    kraang extract <artifact_id>         (single-pass)          │
│    kraang extract-multi <artifact_id>   (multi-pass) ← NEW    │
│    kraang relate                                                │
│    kraang conflicts                                             │
└────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
        ┌────────────────────┐  ┌───────────────────────┐
        │  KraangExtractor   │  │ MultiPassExtractor    │
        │  (existing)        │  │ (new)                 │
        │                    │  │                        │
        │  • extract_facts() │  │ • run_passes()        │
        │    (single pass)   │  │ • deduplicate()       │
        │                    │  │ • check_diminishing() │
        └────────────────────┘  └───────────────────────┘
                    │                   │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  Claude API     │
                    │  (Sonnet 4.5)   │
                    └─────────────────┘
                              │
                              ▼
        ┌───────────────────────────────────────────┐
        │         Facts (with provenance)           │
        │                                            │
        │  fact_1: "Use CREATE" (from: general)     │
        │  fact_2: "Max 1MB pool" (from: memory)    │
        │  fact_3: "Not thread-safe" (from: conc)   │
        │  ...                                       │
        └───────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  KraangStore    │
                    │                 │
                    │  .kraang/       │
                    │    facts.json   │
                    └─────────────────┘
```

---

## Example: Fact Journey Through Pipeline

```
┌──────────────────────────────────────────────────────────────────┐
│  SOURCE CODE (memory.c)                                          │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ /* All allocations MUST use CREATE macro, not malloc */   │ │
│  │ #define CREATE(type) pool_allocate(sizeof(type))          │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
        ┌─────────────────┐   ┌─────────────────┐
        │  PASS 1: GEN    │   │  PASS 2: MEM    │
        └─────────────────┘   └─────────────────┘
                    │                   │
                    ▼                   ▼
        ┌─────────────────┐   ┌─────────────────┐
        │ Extracted Fact  │   │ Extracted Fact  │
        │                 │   │                 │
        │ "Use CREATE     │   │ "All allocation │
        │  macro for      │   │  MUST use       │
        │  allocation"    │   │  CREATE macro,  │
        │                 │   │  not malloc"    │
        │ Type: impl      │   │ Type: constraint│
        │ Conf: 0.80      │   │ Conf: 0.95      │
        └─────────────────┘   └─────────────────┘
                    │                   │
                    │                   │
                    │                   ▼
                    │         ┌─────────────────┐
                    │         │ Deduplication   │
                    │         │                 │
                    │         │ Similarity: 0.85│
                    │         │ → DUPLICATE     │
                    │         └─────────────────┘
                    │                   │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  Merged Fact    │
                    │                 │
                    │ "All allocation │
                    │  MUST use       │
                    │  CREATE macro,  │
                    │  not malloc"    │
                    │                 │
                    │ Type: constraint│
                    │ Conf: 1.00      │
                    │ (boosted)       │
                    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Stored in DB    │
                    │                 │
                    │ fact_5          │
                    │ .kraang/        │
                    │ facts.json      │
                    └─────────────────┘
```

This fact now has:
- Higher confidence (1.00) due to multiple confirmations
- More specific statement (from memory pass)
- Combined keywords from both passes
- Provenance tracking (came from 2 passes)

---

## Performance Characteristics

```
                     SCALABILITY ANALYSIS

Time Complexity:
┌────────────────────────────────────────────────────────────┐
│ Per Pass:                                                  │
│   • API call: O(1) per pass                                │
│   • JSON parsing: O(n) where n = response size             │
│   • Deduplication: O(n × m) where n = new facts,           │
│                                   m = existing facts        │
│                                                             │
│ Total: O(P × N × M) where P = passes, N = facts per pass,  │
│                           M = accumulated facts            │
│                                                             │
│ Example: 7 passes, ~20 facts per pass, ~80 total facts     │
│          7 × 20 × 40 (avg) = 5,600 comparisons             │
│          (acceptable for most use cases)                    │
└────────────────────────────────────────────────────────────┘

Space Complexity:
┌────────────────────────────────────────────────────────────┐
│ • Fact storage: O(N) where N = total unique facts          │
│ • Pass results: O(P) where P = number of passes            │
│ • Temporary: O(N) for deduplication comparisons            │
│                                                             │
│ Total: O(N) - linear in number of facts                    │
└────────────────────────────────────────────────────────────┘

API Cost:
┌────────────────────────────────────────────────────────────┐
│ Per file: ~7 API calls (one per pass)                      │
│ Per call: ~15K input tokens, ~3K output tokens             │
│ Total per file: ~105K input + ~21K output = 126K tokens    │
│                                                             │
│ At Sonnet pricing ($3/$15 per MTok):                       │
│   Input: 0.105 × $3 = $0.315                               │
│   Output: 0.021 × $15 = $0.315                             │
│   Total: ~$0.63 per file                                   │
│                                                             │
│ 100 files = ~$63 (with early stopping, ~$40-50)           │
└────────────────────────────────────────────────────────────┘
```
