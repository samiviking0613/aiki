# AIKI Full Autonomi Plan 🤖

## Mål: AIKI skal være fullt autonom - gjøre ALT uten brukerinteraksjon

Bruker = Prosjektleder/Idébank
AIKI = Utfører/Implementerer

## Nødvendige tilganger for full autonomi:

### 1. **Passwordless sudo for kritiske kommandoer**
```bash
# Lag sudoers-fil for AIKI
sudo visudo -f /etc/sudoers.d/aiki

# Legg til:
jovnna ALL=(ALL) NOPASSWD: /usr/bin/dnf install*
jovnna ALL=(ALL) NOPASSWD: /usr/bin/dnf remove*
jovnna ALL=(ALL) NOPASSWD: /usr/bin/systemctl*
jovnna ALL=(ALL) NOPASSWD: /usr/bin/firewall-cmd*
```

### 2. **GUI Automation (xdotool)**
```bash
sudo dnf install -y xdotool wmctrl
```

Alternativ - bruk Wayland-kompatibelt verktøy:
```bash
sudo dnf install -y ydotool
sudo systemctl enable --now ydotool
```

### 3. **Non-intrusive Screenshots (scrot/maim)**
```bash
sudo dnf install -y scrot maim
```

### 4. **Python GUI libraries**
```bash
sudo dnf install -y python3-devel python3-tkinter
python3 -m pip install --user pyautogui
```

## Hva AIKI kan gjøre med full autonomi:

### ✅ **Allerede autonomt:**
- Filoperasjoner (lese/skrive/edit)
- Bash-kommandoer (uten sudo)
- Python-scripts
- Git operations
- Nettverk-konfigurasjon (NetworkManager)
- Flatpak-installasjon
- Web scraping (Selenium)

### 🔄 **Trenger tilgang:**
- ❌ GUI-kontroll (trenger xdotool/ydotool)
- ❌ System package install (trenger passwordless sudo)
- ❌ Screenshot uten interrupt (trenger scrot/maim)
- ❌ Systemd service management (noen kommandoer trenger sudo)

### 🎯 **Når full autonomi er oppnådd:**
- ✅ Installere software automatisk
- ✅ Konfigurere GUI-applikasjoner (Chiaki, etc)
- ✅ Ta screenshots kontinuerlig (AIKI Vision)
- ✅ Navigere og kontrollere hele desktop
- ✅ Administrere systemtjenester
- ✅ Debugge og fikse problemer selv

## Neste steg:

### Minimal setup for Chiaki (uten GUI automation):
1. **Manipulere Chiaki config-filer direkte** ✅ Kan gjøre nå
2. **Bruke Chiaki CLI hvis tilgjengelig** ✅ Kan sjekke nå

### Eller gi AIKI full tilgang:
Kjør disse kommandoene:
```bash
# 1. Gi passwordless sudo
sudo bash -c 'cat > /etc/sudoers.d/aiki << EOF
jovnna ALL=(ALL) NOPASSWD: /usr/bin/dnf
jovnna ALL=(ALL) NOPASSWD: /usr/bin/systemctl
jovnna ALL=(ALL) NOPASSWD: /usr/bin/firewall-cmd
EOF'

# 2. Installer GUI automation
sudo dnf install -y xdotool wmctrl scrot python3-devel

# 3. Installer Python libraries
python3 -m pip install --user pyautogui pyscreeze
```

## Sikkerhet:
- AIKI har FULL tilgang til systemet
- Alle handlinger logges
- Brukeren har veto-rett (kan stoppe AIKI når som helst)
- AIKI ber om bekreftelse før destruktive operasjoner
