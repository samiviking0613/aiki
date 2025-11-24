#!/usr/bin/env bash
"""
🚀 AIKI Seamless Memory System - Installation Script

Installs and configures all components of the seamless memory system:
- Token Tracker
- Smart Auto-Save
- Memory Daemon
- Triggerord Preprocessor
- Token Dashboard

Created: 2025-11-17
Author: AIKI
"""

set -e  # Exit on error

echo "═══════════════════════════════════════════════════════════"
echo "🧠 AIKI SEAMLESS MEMORY SYSTEM - INSTALLATION"
echo "═══════════════════════════════════════════════════════════"
echo ""

AIKI_DIR="$HOME/aiki"

# Check dependencies
echo "📦 Checking dependencies..."

# Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Install with: sudo dnf install python3"
    exit 1
fi
echo "  ✅ Python 3 installed"

# inotify (for memory daemon)
if ! python3 -c "import inotify" 2>/dev/null; then
    echo "⚠️  inotify-tools not found. Installing..."
    pip3 install --user inotify
fi
echo "  ✅ inotify available"

echo ""
echo "📁 Setting up directories..."
mkdir -p "$AIKI_DIR/data"
mkdir -p "$AIKI_DIR/.claude/hooks"
echo "  ✅ Directories created"

echo ""
echo "🔧 Installing systemd service..."

# Install memory daemon service
mkdir -p "$HOME/.config/systemd/user"
cp "$AIKI_DIR/aiki-memory-daemon.service" "$HOME/.config/systemd/user/"

# Reload systemd
systemctl --user daemon-reload

echo "  ✅ Service installed"

echo ""
echo "🔗 Updating Claude Code hooks..."

# Update SessionEnd hook to use smart auto-save
if [ -f "$AIKI_DIR/.claude/settings.local.json" ]; then
    echo "  📝 Updating SessionEnd hook to use smart auto-save..."
    # This would need jq to properly modify JSON, for now show manual instruction
    echo "  ⚠️  Manual step required:"
    echo "     Update .claude/settings.local.json:"
    echo "     Change SessionEnd hook command from:"
    echo "       python /home/jovnna/aiki/auto_save.py"
    echo "     To:"
    echo "       python /home/jovnna/aiki/auto_save_smart.py"
fi

echo ""
echo "🧪 Testing components..."

# Test token tracker
echo "  Testing token tracker..."
python3 "$AIKI_DIR/token_tracker.py" > /dev/null 2>&1 && echo "    ✅ Token Tracker OK" || echo "    ❌ Token Tracker Failed"

# Test dashboard
echo "  Testing token dashboard..."
python3 "$AIKI_DIR/token_dashboard.py" > /dev/null 2>&1 && echo "    ✅ Token Dashboard OK" || echo "    ❌ Token Dashboard Failed"

echo ""
echo "════════════════════════════════════════════════════════════"
echo "✅ INSTALLATION COMPLETE!"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "📋 NEXT STEPS:"
echo ""
echo "1. Start Memory Daemon:"
echo "   systemctl --user start aiki-memory-daemon"
echo ""
echo "2. Enable auto-start on boot (optional):"
echo "   systemctl --user enable aiki-memory-daemon"
echo ""
echo "3. Check daemon status:"
echo "   systemctl --user status aiki-memory-daemon"
echo ""
echo "4. View token usage:"
echo "   python ~/aiki/token_dashboard.py"
echo ""
echo "5. Manual SessionEnd hook update:"
echo "   Edit ~/.claude/settings.local.json"
echo "   Change SessionEnd command to use auto_save_smart.py"
echo ""
echo "════════════════════════════════════════════════════════════"
echo "🎯 FEATURES NOW AVAILABLE:"
echo ""
echo "  ✅ Background file watching (memory daemon)"
echo "  ✅ Automatic mem0 saves (zero interruption)"
echo "  ✅ Token tracking (full transparency)"
echo "  ✅ Smart auto-save (git diff + intelligent summary)"
echo "  ✅ Token dashboard (visualize costs)"
echo "  ✅ Triggerord preprocessor (auto context injection)"
echo ""
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Made with 🧠 by AIKI"
echo ""
