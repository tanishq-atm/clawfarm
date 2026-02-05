#!/bin/bash
set -e

echo "🦞 ClawCon Lobster Generator"
echo "==========================================="
echo ""
echo "Full autonomous flow:"
echo "  1. Create AgentMail inbox"
echo "  2. Browser automation Leonardo signup"
echo "  3. Extract API key"
echo "  4. Generate ClawCon lobster image"
echo ""
echo "==========================================="
echo ""

cd /home/exedev/.openclaw/workspace

# Phase 1: Create Leonardo account
echo "📍 Phase 1: Creating Leonardo account..."
PYTHONPATH=/home/exedev/.openclaw/workspace:$PYTHONPATH python3 -u leonardo/create_accounts.py

# Find the results file (most recent)
RESULTS_FILE=$(ls -t leonardo_parallel_results_*.json 2>/dev/null | head -1)

if [ -z "$RESULTS_FILE" ]; then
    echo "❌ No results file found"
    exit 1
fi

echo ""
echo "✅ Phase 1 complete!"
echo ""

# Phase 2: Generate ClawCon image
echo "📍 Phase 2: Generating ClawCon lobster image..."
python3 leonardo/generate_clawcon.py "$RESULTS_FILE"

IMAGE_FILE=$(ls -t clawcon_*.jpg 2>/dev/null | head -1)

echo ""
echo "✅ Phase 2 complete!"
echo ""

if [ -z "$IMAGE_FILE" ]; then
    echo "❌ No image file found"
    exit 1
fi

echo "==========================================="
echo "🎉 CLAWCON GENERATED!"
echo ""
echo "📸 Your image: $IMAGE_FILE"
echo ""
echo "Model: Leonardo Phoenix 1.0"
echo "Resolution: 1024×1024"
echo "Total time: ~4 minutes"
echo "==========================================="
