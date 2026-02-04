#!/bin/bash
# Test run script with timing

echo "🚀 Starting Leonardo Automation v2 Test"
echo "⏱️  Timer started at $(date -u +%H:%M:%S) UTC"
echo ""

START_TIME=$(date +%s)

# Run automation
venv/bin/python leonardo_automation_v2.py

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
MINUTES=$((DURATION / 60))
SECONDS=$((DURATION % 60))

echo ""
echo "⏱️  Total time: ${MINUTES}m ${SECONDS}s"
