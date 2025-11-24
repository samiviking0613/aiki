#!/bin/bash
# 🏥 AIKI Health Monitoring - Installation Script

set -e

echo "🏥 Installing AIKI System Health Monitoring..."
echo ""

# Sjekk at vi er i riktig directory
AIKI_DIR="$HOME/aiki"
if [ ! -d "$AIKI_DIR" ]; then
    echo "❌ FEIL: $AIKI_DIR finnes ikke!"
    exit 1
fi

cd "$AIKI_DIR"

# Sjekk at alle filer finnes
FILES=(
    "natural_logger.py"
    "system_health_daemon.py"
    "system_health_dashboard.py"
    "aiki-health-daemon.service"
)

echo "📋 Sjekker filer..."
for file in "${FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Mangler: $file"
        exit 1
    fi
    echo "   ✅ $file"
done
echo ""

# Gjør scripts executable
echo "🔧 Setter permissions..."
chmod +x natural_logger.py
chmod +x system_health_daemon.py
chmod +x system_health_dashboard.py
echo "   ✅ Scripts er executable"
echo ""

# Installer systemd service
echo "🔧 Installerer systemd service..."
SYSTEMD_DIR="$HOME/.config/systemd/user"
mkdir -p "$SYSTEMD_DIR"
cp aiki-health-daemon.service "$SYSTEMD_DIR/"
echo "   ✅ Service installert til $SYSTEMD_DIR"
echo ""

# Reload systemd
echo "🔄 Reloader systemd..."
systemctl --user daemon-reload
echo "   ✅ Systemd reloaded"
echo ""

# Enable service
echo "🚀 Aktiverer service (auto-start på boot)..."
systemctl --user enable aiki-health-daemon.service
echo "   ✅ Service enabled"
echo ""

# Start service
echo "▶️  Starter health daemon..."
systemctl --user start aiki-health-daemon.service
echo "   ✅ Service started"
echo ""

# Wait litt for daemon å kjøre første check
echo "⏳ Venter 3 sekunder på første health check..."
sleep 3
echo ""

# Sjekk status
echo "📊 Service status:"
systemctl --user status aiki-health-daemon.service --no-pager | head -10
echo ""

# Test health file
if [ -f "$HOME/aiki/system_health.json" ]; then
    echo "✅ Health file generert: $HOME/aiki/system_health.json"
else
    echo "⚠️  ADVARSEL: Health file ikke funnet ennå (venter på første check)"
fi
echo ""

# Show dashboard
echo "📊 Viser dashboard..."
echo ""
python3.11 system_health_dashboard.py
echo ""

# Success message
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                  ✅ INSTALLASJON FULLFØRT!                      ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 Kommandoer:"
echo "   systemctl --user status aiki-health-daemon    # Sjekk status"
echo "   systemctl --user stop aiki-health-daemon      # Stopp daemon"
echo "   systemctl --user start aiki-health-daemon     # Start daemon"
echo "   systemctl --user restart aiki-health-daemon   # Restart daemon"
echo "   journalctl --user -u aiki-health-daemon -f    # Se live logs"
echo ""
echo "   python3.11 system_health_dashboard.py         # Vis dashboard"
echo "   python3.11 system_health_dashboard.py -w      # Watch mode"
echo ""
echo "📁 Files:"
echo "   Health data: $HOME/aiki/system_health.json"
echo "   Token data:  $HOME/aiki/data/tokens.db"
echo "   Qdrant data: $HOME/aiki/shared_qdrant"
echo ""
echo "🎉 AIKI er nå self-aware og overvåker seg selv kontinuerlig!"
echo ""
