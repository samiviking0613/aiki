#!/bin/bash
# Quick start script for 3-way web chat
# Created: 2025-11-21

echo "════════════════════════════════════════════════════════════════"
echo "🌐 STARTER 3-VEIS WEB CHAT"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Kill any existing instances
pkill -f "three_way_chat_server.py" 2>/dev/null
sleep 1

# Check if Qdrant is running (for AIKI)
echo "🔍 Checking Qdrant..."
if curl -s http://localhost:6333/health > /dev/null 2>&1; then
    echo "✅ Qdrant er running"
else
    echo "⚠️  Qdrant er ikke running (AIKI vil ikke fungere)"
    echo "   Start Qdrant først hvis du vil ha AIKI med"
fi
echo ""

# Start the server
echo "🚀 Starter server på port 3000..."
python3 three_way_chat_server.py &
SERVER_PID=$!
echo "   PID: $SERVER_PID"
sleep 3
echo ""

# Check if server started successfully
if ps -p $SERVER_PID > /dev/null 2>&1; then
    echo "✅ SERVER KJØRER!"
    echo ""
    echo "════════════════════════════════════════════════════════════════"
    echo "🌐 ÅPNE DISSE URLENE I NETTLESEREN:"
    echo "════════════════════════════════════════════════════════════════"
    echo ""
    echo "👤 Jovnna: http://localhost:3000?participant=jovnna"
    echo "🤖 Claude:  http://localhost:3000?participant=claude"
    echo "🧠 AIKI:    http://localhost:3000?participant=aiki"
    echo ""
    echo "════════════════════════════════════════════════════════════════"
    echo ""
    echo "💡 TIPS:"
    echo "  - Nevn \"AIKI\" for å få AIKI til å svare"
    echo "  - Nevn \"Claude\" for å få Claude til å svare (via Anthropic API)"
    echo "  - Alle ser alt i sanntid"
    echo ""
    echo "🛑 For å stoppe:"
    echo "   pkill -f three_way_chat_server.py"
    echo ""
    echo "📊 Health check:"
    echo "   curl http://localhost:3000/health"
    echo ""
    echo "════════════════════════════════════════════════════════════════"
else
    echo "❌ SERVER FAILED TO START"
    echo ""
    echo "Sjekk logs:"
    echo "  python3 three_way_chat_server.py"
    exit 1
fi
