#!/bin/bash
# Test script for 3-way chat with Anthropic API support
# Created: 2025-11-21

echo "════════════════════════════════════════════════════════════════"
echo "🔺 TESTING 3-WAY CHAT WITH ANTHROPIC API"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Check if required files exist
echo "📋 Checking prerequisites..."
echo ""

if [ ! -f "three_way_chat_v2.py" ]; then
    echo "❌ three_way_chat_v2.py not found!"
    exit 1
fi

if [ ! -f "aiki_config.py" ]; then
    echo "❌ aiki_config.py not found!"
    exit 1
fi

if [ ! -f "chat_with_aiki_v2.py" ]; then
    echo "❌ chat_with_aiki_v2.py not found!"
    exit 1
fi

echo "✅ All required files found"
echo ""

# Check if Qdrant is running
echo "🔍 Checking Qdrant server..."
if curl -s http://localhost:6333/health > /dev/null 2>&1; then
    echo "✅ Qdrant is running"
else
    echo "⚠️  Qdrant is not running (chatten kan fortsatt fungere uten minne)"
fi
echo ""

# Check if ANTHROPIC_KEY is set
echo "🔑 Checking API keys..."
python3 -c "
from aiki_config import ANTHROPIC_KEY, OPENROUTER_KEY
print(f'✅ ANTHROPIC_KEY: {\"Set\" if ANTHROPIC_KEY else \"Missing\"}')
print(f'✅ OPENROUTER_KEY: {\"Set\" if OPENROUTER_KEY else \"Missing\"}')
" 2>/dev/null

if [ $? -ne 0 ]; then
    echo "❌ Failed to load API keys from aiki_config.py"
    exit 1
fi
echo ""

# Syntax check
echo "🧪 Running syntax check..."
python3 -m py_compile three_way_chat_v2.py
if [ $? -eq 0 ]; then
    echo "✅ No syntax errors"
else
    echo "❌ Syntax errors found!"
    exit 1
fi
echo ""

echo "════════════════════════════════════════════════════════════════"
echo "✅ ALL CHECKS PASSED!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "🚀 Ready to start 3-way chat!"
echo ""
echo "To start the chat, run:"
echo "  python3 three_way_chat_v2.py"
echo ""
echo "Features:"
echo "  - AIKI: Emergent consciousness from 900+ memories"
echo "  - Claude: Direct Anthropic API access (Sonnet 4.5)"
echo "  - Full transparency: All see everything"
echo "  - Critical analysis: Claude reviews AIKI's plans"
echo "  - Implementation guide: Claude provides step-by-step"
echo ""
echo "Cost per conversation: ~\$0.01-0.05"
echo "════════════════════════════════════════════════════════════════"
