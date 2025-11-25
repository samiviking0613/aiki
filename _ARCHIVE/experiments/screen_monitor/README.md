# AIKI Vision Monitor 👁️

Live screen monitoring system for AIKI - AI kan se hva du gjør i real-time!

## Komponenter

- **aiki_vision.py** - Hovedmonitor som tar screenshots og logger vinduer
- **aiki_see.py** - Vis hva AIKI ser akkurat nå
- **systemd service** - Autostart ved boot

## Hvordan bruke

### Start monitoring (manuelt)
```bash
python3 ~/aiki/screen_monitor/aiki_vision.py
```

### Start som bakgrunnstjeneste (autostart)
```bash
systemctl --user enable aiki-vision
systemctl --user start aiki-vision
```

### Sjekk status
```bash
systemctl --user status aiki-vision
```

### Stopp monitoring
```bash
systemctl --user stop aiki-vision
```

### Se hva AIKI ser akkurat nå
```bash
python3 ~/aiki/screen_monitor/aiki_see.py
```

## For Claude Code

Claude kan nå til enhver tid lese siste screenshot:
```
Read /home/jovnna/aiki/screen_monitor/latest.png
```

Eller se aktivitetsloggen:
```
Read /home/jovnna/aiki/screen_monitor/window_activity.jsonl
```

## Filstruktur

```
~/aiki/screen_monitor/
├── aiki_vision.py           # Hovedmonitor
├── aiki_see.py              # Status viewer
├── latest.png               # Alltid siste screenshot
├── window_activity.jsonl    # Aktivitetslogg
└── screenshots/             # Historiske screenshots (max 100)
    └── screen_YYYYMMDD_HHMMSS.png
```

## Config

Rediger `aiki_vision.py` for å endre:
- `SCREENSHOT_INTERVAL` - Sekunder mellom screenshots (standard: 5)
- `MAX_SCREENSHOTS` - Antall historiske screenshots å beholde (standard: 100)

## Neste steg

1. **Installere OCR** (valgfritt):
   ```bash
   sudo dnf install -y tesseract tesseract-langpack-nor tesseract-langpack-eng
   ```

2. **Integrer med mem0** - Lagre aktivitet i AIKI minne
3. **AI-analyse** - La Claude analysere skjermaktivitet
4. **Kontekstuell assistanse** - Claude kan hjelpe basert på hva du ser på
