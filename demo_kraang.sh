#!/bin/bash
# Kraang Complete System Demo
# Demonstrates the full workflow of the Kraang system

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print section headers
print_header() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
}

# Function to print step info
print_step() {
    echo -e "${GREEN}>>> $1${NC}"
}

# Function to print warnings
print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Function to print errors
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Function to prompt for continue
prompt_continue() {
    echo ""
    read -p "Press Enter to continue..."
    echo ""
}

# Check prerequisites
print_header "Kraang System Demo - Prerequisites Check"

# Check for API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    print_error "ANTHROPIC_API_KEY environment variable not set"
    echo "Export your API key: export ANTHROPIC_API_KEY='your-key-here'"
    exit 1
fi
print_step "✓ API key found"

# Check for Python modules
python3 -c "import anthropic" 2>/dev/null || {
    print_error "anthropic module not found"
    echo "Install it: pip install anthropic"
    exit 1
}
print_step "✓ Python modules available"

# Make sure we're in the right directory
if [ ! -f "kraang.py" ]; then
    print_error "kraang.py not found - run this script from the kraang directory"
    exit 1
fi
print_step "✓ In correct directory"

# Check if we should use existing data
USE_EXISTING=false
if [ -d ".kraang" ] && [ -f ".kraang/artifacts.json" ]; then
    echo ""
    echo "Found existing .kraang directory with data"
    read -p "Use existing data? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        USE_EXISTING=true
        print_step "Using existing data"
    else
        print_step "Will create fresh data"
        rm -rf .kraang
    fi
fi

print_header "Demo Overview"
echo "This demo will showcase:"
echo "  1. Project initialization"
echo "  2. Adding artifacts (code and documentation)"
echo "  3. Extracting facts using multi-pass extraction"
echo "  4. Analyzing coverage"
echo "  5. Running smart pairing"
echo "  6. Finding relationships"
echo "  7. Detecting contradictions"
echo "  8. Query-driven validation"
echo "  9. Generating final report"
echo ""
echo "This will take approximately 5-10 minutes."
prompt_continue

# ========================================================================
# STEP 1: Initialize Project
# ========================================================================

if [ "$USE_EXISTING" = false ]; then
    print_header "Step 1: Initialize Kraang Project"
    print_step "Creating .kraang directory and initializing storage..."
    ./kraang.py init
    prompt_continue

    # ========================================================================
    # STEP 2: Add Artifacts
    # ========================================================================

    print_header "Step 2: Add Sample Artifacts"

    # Create a test code file
    print_step "Creating sample C code file..."
    cat > /tmp/memory_manager.c << 'EOF'
/*
 * Memory Manager Module
 *
 * Constraints:
 * - All memory allocation MUST use CREATE() macro
 * - All memory deallocation MUST use DESTROY() macro
 * - Never use malloc() or free() directly
 * - Maximum allocation size is 1MB
 *
 * Thread Safety:
 * - This module is NOT thread-safe
 * - Caller must provide external synchronization
 * - Lock ordering: global_lock before pool_lock
 */

#define MAX_ALLOC_SIZE (1024 * 1024)

#define CREATE(type) pool_allocate(sizeof(type))
#define DESTROY(ptr) pool_deallocate(ptr)

typedef struct memory_pool {
    void *data;
    size_t size;
    size_t used;
    int ref_count;
} memory_pool_t;

/* Allocate memory from pool
 * Returns: Pointer to allocated memory, or NULL on error
 * Thread safety: NOT thread-safe
 */
void* pool_allocate(size_t size) {
    if (size == 0 || size > MAX_ALLOC_SIZE) {
        return NULL;
    }
    // ... allocation logic
}

/* Deallocate memory back to pool
 * Thread safety: NOT thread-safe
 */
void pool_deallocate(void *ptr) {
    if (!ptr) return;
    // ... deallocation logic
}
EOF

    # Create a test documentation file
    print_step "Creating sample documentation file..."
    cat > /tmp/coding_standards.md << 'EOF'
# Coding Standards

## Memory Management

All memory operations must follow these rules:

1. **Allocation**: Always use the `CREATE()` macro. Never use `malloc()` directly.
2. **Deallocation**: Always use the `DESTROY()` macro. Never use `free()` directly.
3. **Size Limits**: Maximum allocation size is 1MB (1024 * 1024 bytes).
4. **Error Handling**: All allocation functions must return NULL on error and set errno.

## Thread Safety

This codebase is NOT thread-safe by default:
- External synchronization is required
- Lock ordering must be respected: acquire global_lock before pool_lock
- Document thread-safety assumptions in function comments

## Development Environment

Local development MUST use Docker Compose:
- Never build services directly in local environment
- All dependencies are managed in docker-compose.yml
- Database runs on localhost:5432

## Testing

All code changes require:
- Unit tests with >80% coverage
- Integration tests for critical paths
- Performance benchmarks for allocation code (target: <1ms)
EOF

    print_step "Adding artifacts to Kraang..."
    ./kraang.py add /tmp/memory_manager.c code
    ./kraang.py add /tmp/coding_standards.md doc

    echo ""
    print_step "Current artifacts:"
    ./kraang.py list artifacts

    prompt_continue

    # ========================================================================
    # STEP 3: Extract Facts
    # ========================================================================

    print_header "Step 3: Extract Facts from Artifacts"
    print_step "Extracting facts from code file (this will call Claude API)..."
    ./kraang.py extract artifact_1

    echo ""
    print_step "Extracting facts from documentation (this will call Claude API)..."
    ./kraang.py extract artifact_2

    echo ""
    print_step "All extracted facts:"
    ./kraang.py list facts

    prompt_continue
else
    print_header "Using Existing Data"
    print_step "Artifacts:"
    ./kraang.py list artifacts
    echo ""
    print_step "Facts:"
    ./kraang.py list facts | head -20
    echo "... (showing first 20 lines)"
    prompt_continue
fi

# ========================================================================
# STEP 4: Coverage Analysis
# ========================================================================

print_header "Step 4: Analyze Code Coverage"
print_step "Running coverage analysis to see which code is referenced by facts..."

./kraang.py coverage

echo ""
print_step "Detailed coverage for first artifact:"
./kraang.py coverage artifact_1

prompt_continue

# ========================================================================
# STEP 5: Smart Pairing (if not already done)
# ========================================================================

print_header "Step 5: Smart Pairing Analysis"

if [ ! -f ".kraang/candidate_pairs.json" ]; then
    print_step "Running smart pairing to find high-value fact pairs..."
    print_step "This reduces O(n²) comparisons using intelligent filtering..."
    python3 smart_pairing.py --budget 100 --verbose
else
    print_step "Smart pairing already completed"
    echo "Candidate pairs found:"
    python3 -c "import json; data=json.load(open('.kraang/candidate_pairs.json')); print(f\"  Total possible pairs: {data['total_pairs']}\"); print(f\"  Candidate pairs: {len(data['candidate_pairs'])}\"); print(f\"  Reduction: {100*(1-len(data['candidate_pairs'])/data['total_pairs']):.1f}%\")"
fi

prompt_continue

# ========================================================================
# STEP 6: Analyze Relationships
# ========================================================================

print_header "Step 6: Analyze Fact Relationships"

# Check if we have relationships already
REL_COUNT=$(python3 -c "import json; print(len(json.load(open('.kraang/relationships.json'))))" 2>/dev/null || echo "0")

if [ "$REL_COUNT" -lt 5 ] && [ "$USE_EXISTING" = false ]; then
    print_step "Analyzing relationships between facts (using smart pairing)..."
    print_warning "This will make API calls - analyzing first few pairs only for demo"

    # Get first 3 candidate pairs
    PAIRS=$(python3 -c "
import json
data = json.load(open('.kraang/candidate_pairs.json'))
for i, pair in enumerate(data['candidate_pairs'][:3]):
    print(f\"{pair['fact1_id']} {pair['fact2_id']}\")
" 2>/dev/null || echo "")

    if [ -n "$PAIRS" ]; then
        while IFS=' ' read -r fact1 fact2; do
            echo "  Analyzing: $fact1 <-> $fact2"
            ./kraang.py relate "$fact1" "$fact2" 2>/dev/null || true
        done <<< "$PAIRS"
    else
        print_step "Analyzing all relationships (limited set)..."
        ./kraang.py relate 2>/dev/null || print_warning "Relationship analysis requires API access"
    fi
else
    print_step "Relationships already analyzed"
fi

echo ""
print_step "Current relationships:"
./kraang.py list relationships

prompt_continue

# ========================================================================
# STEP 7: Find Contradictions
# ========================================================================

print_header "Step 7: Detect Contradictions"
print_step "Checking for contradicting facts..."

./kraang.py conflicts

prompt_continue

# ========================================================================
# STEP 8: Impact Analysis
# ========================================================================

print_header "Step 8: Impact Analysis"
print_step "Analyzing impact of changing a fact..."

# Get first fact ID
FIRST_FACT=$(python3 -c "import json; facts=json.load(open('.kraang/facts.json')); print(facts[0]['id'])" 2>/dev/null || echo "fact_1")

./kraang.py impact "$FIRST_FACT"

prompt_continue

# ========================================================================
# STEP 9: Completeness Analysis
# ========================================================================

print_header "Step 9: Completeness Analysis"
print_step "Analyzing extraction completeness..."

./kraang.py completeness

prompt_continue

# ========================================================================
# STEP 10: Coverage Gaps
# ========================================================================

print_header "Step 10: Coverage Gap Analysis"
print_step "Finding areas needing more fact extraction..."

./kraang.py coverage --gaps

prompt_continue

# ========================================================================
# STEP 11: Query Validation (optional)
# ========================================================================

print_header "Step 11: Query-Driven Validation (Optional)"
print_step "This tests if the system can answer typical developer questions"
print_warning "This requires API access and can take several minutes"

read -p "Run query validation? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    ./kraang.py validate-queries || print_warning "Query validation requires API access"
else
    print_step "Skipped query validation"
fi

# ========================================================================
# FINAL REPORT
# ========================================================================

print_header "Final System Report"

# Generate comprehensive report
print_step "Generating comprehensive report..."

REPORT_FILE=".kraang/demo_report.txt"

cat > "$REPORT_FILE" << EOF
Kraang System Demo Report
Generated: $(date)
========================================

ARTIFACTS
========================================
EOF

./kraang.py list artifacts >> "$REPORT_FILE"

cat >> "$REPORT_FILE" << EOF

FACTS SUMMARY
========================================
EOF

FACT_COUNT=$(python3 -c "import json; print(len(json.load(open('.kraang/facts.json'))))" 2>/dev/null || echo "0")
echo "Total facts extracted: $FACT_COUNT" >> "$REPORT_FILE"

python3 -c "
import json
facts = json.load(open('.kraang/facts.json'))
types = {}
for fact in facts:
    types[fact['type']] = types.get(fact['type'], 0) + 1
print('\nFacts by type:')
for ftype, count in sorted(types.items()):
    print(f'  {ftype}: {count}')
" >> "$REPORT_FILE" 2>/dev/null || true

cat >> "$REPORT_FILE" << EOF

RELATIONSHIPS
========================================
EOF

./kraang.py list relationships >> "$REPORT_FILE" 2>/dev/null || echo "No relationships found" >> "$REPORT_FILE"

cat >> "$REPORT_FILE" << EOF

COVERAGE ANALYSIS
========================================
EOF

./kraang.py coverage >> "$REPORT_FILE" 2>/dev/null || echo "Coverage data not available" >> "$REPORT_FILE"

cat >> "$REPORT_FILE" << EOF

COMPLETENESS SCORE
========================================
EOF

./kraang.py completeness >> "$REPORT_FILE" 2>/dev/null || echo "Completeness data not available" >> "$REPORT_FILE"

# Display report
cat "$REPORT_FILE"

print_header "Demo Complete!"

echo ""
echo -e "${GREEN}✓ Demo completed successfully!${NC}"
echo ""
echo "Report saved to: $REPORT_FILE"
echo ""
echo "What's been demonstrated:"
echo "  ✓ Project initialization and artifact management"
echo "  ✓ Multi-source fact extraction (code + docs)"
echo "  ✓ Coverage analysis showing code referenced by facts"
echo "  ✓ Smart pairing to reduce comparison complexity"
echo "  ✓ Relationship analysis between facts"
echo "  ✓ Contradiction detection"
echo "  ✓ Impact analysis"
echo "  ✓ Completeness scoring"
echo ""
echo "Next steps:"
echo "  • Add more artifacts: ./kraang.py add <file> <type>"
echo "  • Extract more facts: ./kraang.py extract <artifact_id>"
echo "  • Analyze relationships: ./kraang.py relate"
echo "  • Run query validation: ./kraang.py validate-queries"
echo "  • View heat maps: ./kraang.py coverage <artifact_id> --heatmap"
echo ""
echo "All data is stored in: .kraang/"
echo ""
