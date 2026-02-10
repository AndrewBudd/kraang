#!/bin/bash
# Coverage Analysis Walkthrough
# Demonstrates all coverage commands with LotJ data

echo "========================================================================"
echo "KRAANG COVERAGE ANALYSIS WALKTHROUGH"
echo "========================================================================"
echo ""

echo "1. OVERALL COVERAGE SUMMARY"
echo "   Shows project-wide statistics, coverage by type, and recommendations"
echo "------------------------------------------------------------------------"
python3 ../kraang.py coverage
echo ""
echo "Press Enter to continue..."
read

echo ""
echo "2. DETAILED ARTIFACT COVERAGE"
echo "   Shows coverage detail for CLAUDE.md documentation"
echo "------------------------------------------------------------------------"
python3 ../kraang.py coverage artifact_1
echo ""
echo "Press Enter to continue..."
read

echo ""
echo "3. HEAT MAP VISUALIZATION"
echo "   Visual representation of coverage distribution"
echo "------------------------------------------------------------------------"
python3 ../kraang.py coverage artifact_1 --heatmap
echo ""
echo "Press Enter to continue..."
read

echo ""
echo "4. COVERAGE GAPS ANALYSIS"
echo "   Identifies files needing attention"
echo "------------------------------------------------------------------------"
python3 ../kraang.py coverage --gaps
echo ""
echo "Press Enter to continue..."
read

echo ""
echo "5. CODE FILE HEAT MAP"
echo "   Heat map for act_comm.c (8,863 lines of C code)"
echo "------------------------------------------------------------------------"
python3 ../kraang.py coverage artifact_78 --heatmap | head -60
echo "   ... (output truncated) ..."
echo ""

echo ""
echo "========================================================================"
echo "WALKTHROUGH COMPLETE"
echo "========================================================================"
echo ""
echo "Key Insights:"
echo "• Overall coverage: 21.2% (needs improvement)"
echo "• CLAUDE.md: 40.5% (below 70% target)"
echo "• act_comm.c: 20.3% (below 40% target)"
echo "• Only 2% of locations are unparseable (excellent)"
echo "• Coverage is clustered in specific sections (gaps exist)"
echo ""
echo "Recommendations:"
echo "• Extract more facts from later sections of CLAUDE.md"
echo "• Focus on middle/end of act_comm.c (lines 1000+)"
echo "• All files have some coverage (no 0% files)"
echo ""
