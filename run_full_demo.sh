#!/bin/bash
set -e

echo "🚀 Full Demo Pipeline: AgentMail at ClawCon"
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

# Phase 2: Generate single image
echo "📍 Phase 2: Generating image..."
python3 leonardo/generate_single.py "$RESULTS_FILE" "AgentMail is at ClawCon, vibrant logo design, professional branding, modern tech aesthetic, high quality"

echo ""
echo "✅ Phase 2 complete!"
echo ""

# Find the generated image
IMAGE_FILE=$(ls -t agentmail_clawcon_*.jpg 2>/dev/null | head -1)

if [ -z "$IMAGE_FILE" ]; then
    echo "❌ No image file found"
    exit 1
fi

echo "==========================================="
echo "🎉 COMPLETE!"
echo ""
echo "📸 Your image: $IMAGE_FILE"
echo ""
echo "Total time: ~3-5 minutes"
echo "==========================================="
