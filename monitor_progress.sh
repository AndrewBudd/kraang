#!/bin/bash
# Monitor relationship processing progress

echo "=========================================="
echo "RELATIONSHIP PROCESSING MONITOR"
echo "=========================================="
echo ""

while true; do
    # Get current relationship count
    rel_count=$(cat /home/budda/Code/kraang/.kraang/relationships.json | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")

    # Get total candidate pairs
    total_pairs=$(cat /home/budda/Code/kraang/.kraang/candidate_pairs.json | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "1000")

    # Calculate progress
    if [ "$total_pairs" -gt 0 ]; then
        pct=$(echo "scale=1; ($rel_count * 100) / $total_pairs" | bc)
    else
        pct="0.0"
    fi

    # Get file size
    size=$(ls -lh /home/budda/Code/kraang/.kraang/relationships.json 2>/dev/null | awk '{print $5}')

    # Display status
    clear
    echo "=========================================="
    echo "RELATIONSHIP PROCESSING MONITOR"
    echo "=========================================="
    echo ""
    echo "Target pairs:        $total_pairs"
    echo "Relationships found: $rel_count"
    echo "Progress:            $pct%"
    echo "File size:           $size"
    echo ""
    echo "Last updated: $(date '+%H:%M:%S')"
    echo ""
    echo "Press Ctrl+C to exit"
    echo "=========================================="

    sleep 10
done
