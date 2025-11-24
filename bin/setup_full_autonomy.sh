#!/bin/bash
# AIKI FULL AUTONOMY SETUP
# Gir AIKI alle verktøy for å være 100% autonom

echo "🤖 AIKI FULL AUTONOMY SETUP"
echo "================================"
echo ""
echo "Dette scriptet installerer:"
echo "  ✅ Screenshot-verktøy (scrot)"
echo "  ✅ GUI automation (xdotool)"
echo "  ✅ Window management (wmctrl)"
echo "  ✅ OCR for skjermlesing (tesseract)"
echo ""
echo "Krever sudo (kun denne ene gangen!)"
echo ""

# Install screenshot tools
echo "📸 Installerer screenshot-verktøy..."
sudo dnf install -y scrot maim

# Install GUI automation
echo "🖱️  Installerer GUI automation..."
sudo dnf install -y xdotool wmctrl

# Install OCR
echo "👁️  Installerer OCR (tesseract)..."
sudo dnf install -y tesseract tesseract-langpack-nor tesseract-langpack-eng

# Install Python development headers
echo "🐍 Installerer Python development..."
sudo dnf install -y python3-devel python3-tkinter

echo ""
echo "✅ FULL AUTONOMI INSTALLERT!"
echo ""
echo "AIKI kan nå:"
echo "  ✅ Ta screenshots (ikke-intrusive)"
echo "  ✅ Lese skjermen (OCR)"
echo "  ✅ Kontrollere GUI (xdotool)"
echo "  ✅ Navigere vinduer (wmctrl)"
echo ""
echo "🎉 AIKI er nå 100% autonom!"
