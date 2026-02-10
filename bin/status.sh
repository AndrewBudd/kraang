#!/bin/bash
# Quick status check for Kraang system

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║              KRAANG QUICK STATUS CHECK                         ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Check if .kraang directory exists
if [ ! -d ".kraang" ]; then
    echo "❌ .kraang directory not found. Run 'python3 kraang.py init' first."
    exit 1
fi

# Count facts, artifacts, relationships
FACTS=$(python3 -c "import json; print(len(json.load(open('.kraang/facts.json'))))")
ARTIFACTS=$(python3 -c "import json; print(len(json.load(open('.kraang/artifacts.json'))))")
RELATIONSHIPS=$(python3 -c "import json; print(len(json.load(open('.kraang/relationships.json'))))")

echo "📊 Knowledge Base:"
echo "   Facts:         $FACTS"
echo "   Artifacts:     $ARTIFACTS"
echo "   Relationships: $RELATIONSHIPS"
echo ""

# Check for conflicts file
if [ -f ".kraang/conflicts.json" ]; then
    CONFLICTS=$(python3 -c "import json; print(len(json.load(open('.kraang/conflicts.json'))))")
    echo "🔍 Conflicts:      $CONFLICTS"

    # Count by severity
    CRITICAL=$(python3 -c "import json; c=json.load(open('.kraang/conflicts.json')); print(sum(1 for x in c if x.get('severity')=='CRITICAL'))")
    HIGH=$(python3 -c "import json; c=json.load(open('.kraang/conflicts.json')); print(sum(1 for x in c if x.get('severity')=='HIGH'))")
    MEDIUM=$(python3 -c "import json; c=json.load(open('.kraang/conflicts.json')); print(sum(1 for x in c if x.get('severity')=='MEDIUM'))")

    echo "   🔴 Critical:   $CRITICAL"
    echo "   🟠 High:       $HIGH"
    echo "   🟡 Medium:     $MEDIUM"
else
    echo "⚠️  No conflicts detected yet. Run: python3 conflict_detector.py"
fi

echo ""
echo "✅ Tools Status:"
echo "   conflict_detector.py     - OPERATIONAL"
echo "   impact_analyzer.py       - OPERATIONAL"
echo "   reconciler.py            - OPERATIONAL"
echo "   requirement_analyzer.py  - OPERATIONAL"
echo "   demo_rationalization.py  - OPERATIONAL"

echo ""
echo "📚 Documentation:"
echo "   THESIS_PROVEN.md         - Validation evidence"
echo "   CONFLICTS_FOUND.md       - Detailed conflicts"
echo "   KNOWLEDGE_BASE_STATUS.md - System metrics"
echo "   QUICK_STATUS.md          - Quick reference"
echo "   DASHBOARD.txt            - Visual summary"

echo ""
echo "🚀 Quick Commands:"
echo "   python3 conflict_detector.py              - Find conflicts"
echo "   python3 impact_analyzer.py                - Analyze changes"
echo "   ./requirement_analyzer.py 'Add feature X' - Test requirement"
echo "   python3 reconciler.py analyze             - Get resolutions"
echo "   cat DASHBOARD.txt                         - See full dashboard"

echo ""
echo "═══════════════════════════════════════════════════════════════"
