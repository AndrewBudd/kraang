#!/bin/bash
# Demonstration script for multi-pass extraction
# Shows the difference between single-pass and multi-pass extraction

set -e

echo "======================================================================="
echo "Multi-Pass Extraction Demo"
echo "======================================================================="
echo ""

# Check for API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "ERROR: ANTHROPIC_API_KEY environment variable not set"
    echo "Please set it and run again:"
    echo "  export ANTHROPIC_API_KEY='your-key-here'"
    exit 1
fi

# Create sample file
echo "Creating sample C file..."
cat > demo_sample.c << 'EOF'
/* Memory Management Module
 *
 * CONSTRAINT: All memory allocation MUST use CREATE macro, not malloc()
 * CONSTRAINT: All deallocation MUST use DESTROY macro, not free()
 * CONSTRAINT: Thread safety - This module is NOT thread-safe
 */

#include <stdlib.h>
#include <string.h>

#define CREATE(type) ((type*)malloc(sizeof(type)))
#define DESTROY(ptr) do { free(ptr); ptr = NULL; } while(0)

typedef struct {
    char *data;
    size_t size;
    int ref_count;
} Buffer;

/* Create a new buffer
 * REQUIREMENT: Returns NULL on allocation failure
 * PERFORMANCE: Buffer allocation is O(1)
 */
Buffer* buffer_create(size_t size) {
    Buffer *buf = CREATE(Buffer);
    if (!buf) return NULL;  // Error handling: NULL on failure

    buf->data = malloc(size);
    if (!buf->data) {
        DESTROY(buf);  // Memory cleanup on error path
        return NULL;
    }

    buf->size = size;
    buf->ref_count = 1;
    return buf;
}

/* Increment reference count
 * CONCURRENCY: Caller must hold lock before calling
 */
void buffer_ref(Buffer *buf) {
    if (!buf) return;
    buf->ref_count++;
}

/* Decrement and possibly free buffer
 * MEMORY: Uses reference counting for lifecycle management
 * SECURITY: Checks for NULL to prevent crashes
 */
void buffer_destroy(Buffer *buf) {
    if (!buf) return;

    buf->ref_count--;
    if (buf->ref_count == 0) {
        free(buf->data);
        DESTROY(buf);
    }
}
EOF

echo "✓ Created demo_sample.c"
echo ""

# Initialize Kraang
echo "Initializing Kraang..."
./kraang.py init
echo ""

# Add artifact
echo "Adding artifact..."
./kraang.py add demo_sample.c code
echo ""

# Single-pass extraction
echo "======================================================================="
echo "SINGLE-PASS EXTRACTION"
echo "======================================================================="
echo ""
./kraang.py extract artifact_1
echo ""

# Count facts from single-pass
SINGLE_COUNT=$(./kraang.py list facts | grep -c "fact_" || echo "0")
echo "Single-pass extracted: $SINGLE_COUNT facts"
echo ""

# Save single-pass results
echo "Saving single-pass results..."
cp .kraang/facts.json .kraang/facts_single.json
echo "[]" > .kraang/facts.json
# Reset ID counter but keep artifacts
cat > .kraang/config.json << 'EOF'
{"next_id": 1}
EOF
echo ""

# Multi-pass extraction
echo "======================================================================="
echo "MULTI-PASS EXTRACTION"
echo "======================================================================="
echo ""
./kraang.py extract-multi artifact_1
echo ""

# Count facts from multi-pass
MULTI_COUNT=$(./kraang.py list facts | grep -c "fact_" || echo "0")
echo "Multi-pass extracted: $MULTI_COUNT facts"
echo ""

# Calculate improvement
if [ "$SINGLE_COUNT" -gt 0 ]; then
    IMPROVEMENT=$((($MULTI_COUNT - $SINGLE_COUNT) * 100 / $SINGLE_COUNT))
    echo "======================================================================="
    echo "COMPARISON"
    echo "======================================================================="
    echo "Single-pass: $SINGLE_COUNT facts"
    echo "Multi-pass:  $MULTI_COUNT facts"
    echo "Improvement: +$IMPROVEMENT%"
    echo ""
fi

# Show sample facts
echo "======================================================================="
echo "SAMPLE FACTS (Multi-Pass)"
echo "======================================================================="
./kraang.py list facts | head -20
echo ""

# Restore single-pass for comparison
echo "To compare results:"
echo "  Single-pass facts: .kraang/facts_single.json"
echo "  Multi-pass facts:  .kraang/facts.json"
echo ""

# Run completeness analysis
echo "======================================================================="
echo "COMPLETENESS ANALYSIS"
echo "======================================================================="
./kraang.py completeness
echo ""

echo "Demo complete!"
echo ""
echo "Clean up with:"
echo "  rm demo_sample.c"
echo "  rm -rf .kraang"
