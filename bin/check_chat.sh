#!/bin/bash
# Quick check for new chat messages

echo "📬 Sjekker for nye meldinger..."
tail -n 50 /tmp/chat_monitor_output.log | grep -A 10 "NY MELDING" | tail -30
