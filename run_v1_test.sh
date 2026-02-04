#!/bin/bash
echo "🚀 Leonardo Automation v1 Test"
echo "⏱️  Start: $(date +%H:%M:%S)"
echo ""

START=$(date +%s)

venv/bin/python leonardo_full_automation.py

END=$(date +%s)
DURATION=$((END - START))
M=$((DURATION / 60))
S=$((DURATION % 60))

echo ""
echo "⏱️  Total: ${M}m ${S}s"
