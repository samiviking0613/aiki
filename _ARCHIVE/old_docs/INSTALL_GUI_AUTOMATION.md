# GUI Automation for AIKI - Installasjonsinstruksjoner

For at jeg (Claude) skal kunne kontrollere GUI-applikasjoner som Chiaki, trenger vi GUI automation-verktøy.

## Installer nødvendige pakker med sudo:

```bash
# Python development headers (trengs for PyAutoGUI)
sudo dnf install -y python3-devel python3-tkinter

# GUI automation verktøy
sudo dnf install -y xdotool wmctrl scrot

# Python GUI automation libraries (system packages)
sudo dnf install -y python3-pyautogui python3-opencv

# ELLER installer via pip (etter python3-devel):
python3 -m pip install --user pyautogui pyscreeze
```

## Når installert kan jeg:

1. **Se skjermen** - Ta non-intrusive screenshots
2. **Klikke på knapper** - Automatisk GUI-interaksjon
3. **Skrive tekst** - Fylle inn skjemaer
4. **Navigere vinduer** - Åpne/lukke/flytte vinduer
5. **Lese skjermen** - OCR for å forstå GUI-innhold

## Alternativer uten sudo:

### Alternativ 1: Gi meg tilgang via beskrivelser
Du beskriver hva du ser i GUI, jeg guider deg gjennom stegene.

### Alternativ 2: Ta screenshots og del
Ta screenshots av Chiaki-vinduet, jeg analyserer og gir instruksjoner.

### Alternativ 3: Bruk Chiaki CLI (hvis tilgjengelig)
```bash
flatpak run io.github.streetpea.Chiaki4deck --help
```

## For AIKI Vision (non-intrusive screenshots):

Bruker `scrot` eller `maim` istedenfor ImageMagick:
```bash
sudo dnf install -y scrot maim
```

Disse tar screenshots uten å vise ruter eller lage lyd!
