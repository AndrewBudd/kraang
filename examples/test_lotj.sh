#!/bin/bash
# Test Kraang on LotJ codebase

set -e

echo "=== Testing Kraang on LotJ Codebase ==="
echo ""

# Check for API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "Error: ANTHROPIC_API_KEY environment variable not set"
    exit 1
fi

# Clean up any existing test
rm -rf .kraang

echo "1. Initializing Kraang..."
./kraang.py init
echo ""

echo "2. Adding LotJ documentation artifacts..."
./kraang.py add ~/Code/LotJ/CLAUDE.md doc
./kraang.py add ~/Code/LotJ/README.md doc
echo ""

echo "3. Adding a sample C source file..."
# Find a small-ish C file to test with
./kraang.py add ~/Code/LotJ/src/act_comm.c code
echo ""

echo "4. Listing artifacts..."
./kraang.py list artifacts
echo ""

echo "5. Extracting facts from CLAUDE.md..."
./kraang.py extract artifact_1
echo ""

echo "6. Extracting facts from act_comm.c..."
./kraang.py extract artifact_3
echo ""

echo "7. Listing extracted facts..."
./kraang.py list facts
echo ""

echo "8. Analyzing relationships between facts..."
./kraang.py relate
echo ""

echo "9. Checking for contradictions..."
./kraang.py conflicts
echo ""

echo "10. Impact analysis for first fact..."
./kraang.py impact fact_1
echo ""

echo "=== Test Complete ==="
echo ""
echo "Data stored in .kraang/ directory:"
ls -lh .kraang/
