#!/bin/bash
#
# Start AIKI Autonomous Resolver Daemon
#

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PID_FILE="$SCRIPT_DIR/logs/autonomous_resolver.pid"
LOG_FILE="$SCRIPT_DIR/logs/autonomous_resolver.log"

echo "🤖 Starting AIKI Autonomous Resolver Daemon..."

# Check if already running
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null 2>&1; then
        echo "❌ Daemon already running (PID: $PID)"
        exit 1
    else
        echo "⚠️  Stale PID file found, removing..."
        rm "$PID_FILE"
    fi
fi

# Start daemon
nohup python3.11 "$SCRIPT_DIR/aiki_autonomous_resolver.py" --daemon \
    > "$LOG_FILE" 2>&1 &

PID=$!
echo $PID > "$PID_FILE"

echo "✅ Daemon started (PID: $PID)"
echo "📝 Logs: $LOG_FILE"
echo ""
echo "Monitor: tail -f $LOG_FILE"
echo "Stop: kill $PID"
