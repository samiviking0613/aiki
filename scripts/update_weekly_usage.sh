#!/bin/bash
# Oppdater weekly usage manuelt
# Bruk: ./update_weekly_usage.sh 79

if [ -z "$1" ]; then
    echo "Usage: $0 <weekly_percent>"
    echo "Eksempel: $0 79"
    exit 1
fi

CACHE_PATH="/home/jovnna/aiki/data/claude_weekly_usage_cache.json"

mkdir -p "$(dirname "$CACHE_PATH")"

echo "{
  \"weekly_percent\": $1,
  \"timestamp\": $(date +%s)
}" > "$CACHE_PATH"

echo "✅ Weekly usage oppdatert til $1%"
echo "Statusline vil nå vise: Weekly: $1%"
