#!/bin/bash
# Install git hooks for AIKI repo

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AIKI_DIR="$(dirname "$SCRIPT_DIR")"
HOOKS_DIR="$AIKI_DIR/.git/hooks"

echo "Installing git hooks..."

# Create pre-commit hook
cat > "$HOOKS_DIR/pre-commit" << 'EOF'
#!/bin/bash
# AIKI Pre-commit hook - Auto-generate READMEs

AIKI_DIR="$(git rev-parse --show-toplevel)"

echo "Generating README files..."
python3 "$AIKI_DIR/tools/generate_readmes.py" > /dev/null 2>&1

# Check if any README files changed
CHANGED_READMES=$(git diff --name-only | grep README.md || true)

if [ -n "$CHANGED_READMES" ]; then
    echo "Auto-adding updated README files:"
    echo "$CHANGED_READMES"
    git add $CHANGED_READMES
fi

exit 0
EOF

chmod +x "$HOOKS_DIR/pre-commit"

# Create post-commit hook for auto-push
cat > "$HOOKS_DIR/post-commit" << 'EOF'
#!/bin/bash
# AIKI Post-commit hook - Auto-push to GitHub

# Only push if remote exists
if git remote | grep -q origin; then
    echo "Auto-pushing to GitHub..."
    git push origin main --quiet 2>/dev/null &
fi
EOF

chmod +x "$HOOKS_DIR/post-commit"

echo "Installed: pre-commit (README auto-generation)"
echo "Installed: post-commit (auto-push to GitHub)"
echo "Done!"
