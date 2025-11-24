#!/bin/bash
# 📊 HEALTH DAEMON MONITORING SCRIPT
# Created: 2025-11-20
# Purpose: Monitor system_health_daemon.py threads over 24-48 timer

DAEMON_PID=$(pgrep -f "python3.11.*system_health_daemon.py" | head -1)

if [ -z "$DAEMON_PID" ]; then
    echo "❌ Health daemon ikke kjørende! Starter den..."
    python3.11 /home/jovnna/aiki/system_health_daemon.py > /tmp/health_monitor.log 2>&1 &
    sleep 5
    DAEMON_PID=$(pgrep -f "python3.11.*system_health_daemon.py" | head -1)
fi

echo "🔍 Monitoring health daemon PID: $DAEMON_PID"
echo "Tid: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Initial thread count
THREADS=$(ps -eLf | grep "^jovnna.*$DAEMON_PID" | wc -l)
echo "📊 Current threads: $THREADS"

# Log til fil
LOG_FILE="/home/jovnna/aiki/data/health_daemon_monitoring.log"
mkdir -p /home/jovnna/aiki/data
echo "$(date '+%Y-%m-%d %H:%M:%S'),PID:$DAEMON_PID,Threads:$THREADS" >> $LOG_FILE

# Check for validation errors
ERROR_COUNT=$(grep -c "validation error\|Error processing memory action" /tmp/health_monitor.log 2>/dev/null || echo 0)
echo "⚠️  Validation errors: $ERROR_COUNT"

# Uptime
UPTIME=$(ps -p $DAEMON_PID -o etime= | xargs)
echo "⏱️  Uptime: $UPTIME"

echo ""
echo "📝 Monitoring log: $LOG_FILE"
echo "🔄 Kjør dette scriptet igjen for å sjekke status"
