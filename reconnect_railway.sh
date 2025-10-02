#!/bin/bash
# Reconnect Railway CLI to AI Nurse Florence Project

echo "=========================================="
echo "Railway CLI Reconnection"
echo "=========================================="
echo ""

echo "Current Railway status:"
railway whoami
echo ""

echo "Available projects:"
railway list
echo ""

echo "To reconnect to your project, you need to run this interactively:"
echo ""
echo "  railway link"
echo ""
echo "Then select:"
echo "  1. Workspace: Patrick Roebuck's Projects"
echo "  2. Project: AI Nurse Florence"
echo "  3. Environment: production"
echo ""
echo "After linking, verify with:"
echo "  railway status"
echo ""
echo "Your service IS running (confirmed via curl)."
echo "The dashboard issue is likely just a UI sync problem."
echo ""
