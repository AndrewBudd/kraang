# LotJ Relationship Graph - Quick Reference Guide

## Current Status Commands

### Check Processing Status
```bash
python3 check_status.py
```
Shows: Current relationships, progress %, type distribution

### Generate Full Report
```bash
python3 final_report.py
```
Shows: Comprehensive analysis with all metrics

### View Existing Reports
```bash
cat RELATIONSHIP_ANALYSIS_SUMMARY.md  # Complete summary
cat RELATIONSHIP_GRAPH_REPORT.txt     # Detailed statistics
```

## Key Metrics to Monitor

### Relationship Count
- **Current:** 77+ (growing)
- **Target:** 1,000 pairs analyzed
- **Progress:** ~7.7% complete

### Relationship Quality
- **High Confidence (≥0.95):** ~40%
- **Medium Confidence (0.85-0.94):** ~56%
- **Low Confidence (<0.85):** ~4%
- **Goal:** >90% with confidence ≥0.85 ✓ ACHIEVED (95.7%)

### Type Distribution
- **Supports:** ~65% (good - shows alignment)
- **Extends:** ~30% (good - shows elaboration)
- **Contradicts:** ~5% (requires attention)

## Critical Findings

### Contradictions: 4 found
1. Header file structure contradiction
2. Monolithic functions.h issue
3. Memory management inconsistency
4. Additional contradiction in progress

### Orphaned Constraints: 211 (93%)
Need implementation validation

### Relationship Density: 3.9%
Will improve as processing completes

## Files Generated

### Reports
- `RELATIONSHIP_ANALYSIS_SUMMARY.md` - **START HERE**
- `RELATIONSHIP_GRAPH_REPORT.txt` - Detailed stats
- `.kraang/relationship_stats.json` - Machine-readable

### Data
- `.kraang/candidate_pairs.json` - 1,000 prioritized pairs
- `.kraang/relationships.json` - Growing relationship DB
- `.kraang/facts.json` - 1,174 extracted facts

## Background Processing

**Status:** Active (running)
**Progress:** ~7.7% (77/1000 pairs)
**ETA:** 4-5 hours
**Monitor:** `python3 check_status.py`

---

*Last updated: 2026-02-10 17:09*
