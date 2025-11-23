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

echo "Installed: pre-commit (README auto-generation)"
echo "Done!"
