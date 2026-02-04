#!/bin/bash
echo "🚀 Leonardo Automation v3 - Session Continuation"
echo "⏱️  Start: $(date -u +%H:%M:%S) UTC"
echo ""

START=$(date +%s)

venv/bin/python leonardo_automation_v3.py

END=$(date +%s)
DURATION=$((END - START))
M=$((DURATION / 60))
S=$((DURATION % 60))

echo ""
echo "⏱️  Total time: ${M}m ${S}s"
