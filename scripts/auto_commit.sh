#!/bin/bash
# AIKI Auto-commit script
# Kjøres av cron og SessionEnd hook

AIKI_DIR="$HOME/aiki"
cd "$AIKI_DIR" || exit 1

# Sjekk om det er endringer
if [ -z "$(git status --porcelain)" ]; then
    exit 0  # Ingen endringer
fi

# Generer README-filer
python3 "$AIKI_DIR/tools/generate_readmes.py" > /dev/null 2>&1

# Stage alle endringer
git add -A

# Lag commit-melding basert på endringer
CHANGED=$(git diff --cached --stat | tail -1)
TIMESTAMP=$(date +"%Y-%m-%d %H:%M")

# Commit
git commit -m "Auto-save: $TIMESTAMP

$CHANGED" --quiet

# Push i bakgrunnen
git push origin main --quiet 2>/dev/null &

echo "[$TIMESTAMP] Auto-committed and pushed"
