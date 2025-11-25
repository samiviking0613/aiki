# PS5 Remote Play - Direkte Ethernet Setup Guide

## ✅ PC Setup Ferdig!

**Nettverkskonfigurasjon:**
- PC Ethernet IP: `10.42.0.1`
- PS5 vil få IP: `10.42.0.2` - `10.42.0.254` (automatisk)
- Internet deles fra WiFi til PS5 via Ethernet

## 📋 Neste steg:

### 1. Koble fysisk Ethernet-kabel
- Koble Ethernet-kabel fra **PC** (enp4s0) til **PS5** LAN-port
- PS5 vil automatisk oppdage kablet tilkobling

### 2. Konfigurer PS5 (på TV/skjerm)
Gå til PS5:

**Steg 1: Aktiver Remote Play**
```
Settings → System → Remote Play
├─ Enable Remote Play: ON
├─ Enable Remote Play over Internet: ON (valgfritt)
└─ Link Device → Vis 8-sifret kode (trenger dette senere)
```

**Steg 2: Sett opp kablet nettverk**
```
Settings → Network → Settings
├─ Set Up Internet Connection
└─ Velg: "Wired LAN (Ethernet)"
    ├─ IP Address Settings: Automatic (DHCP)
    ├─ DNS Settings: Automatic
    └─ Test Connection
```

**Steg 3: Sjekk IP-adresse**
```
Settings → Network → View Connection Status
└─ Noter IP-adressen (skal være 10.42.0.x)
```

### 3. Konfigurer Chiaki (på PC)

**Steg 1: Åpne Chiaki**
```bash
flatpak run io.github.streetpea.Chiaki4deck
```

**Steg 2: Registrer PS5**
- Klikk **"+"** eller hamburger-meny
- Velg **"Register new PS5"**

**Steg 3: Fyll inn:**
```
┌─────────────────────────────────────────┐
│ Host (PS5 IP):  10.42.0.x              │ ← Fra PS5 Connection Status
│ Registration Code: xxxxxxxx             │ ← 8-sifret kode fra PS5
│ PSN AccountID: (se under)               │
└─────────────────────────────────────────┘
```

### 4. Få PSN AccountID

**Metode 1: Via browser (enklest)**
1. Gå til: https://ca.account.sony.com/api/v1/ssocookie
2. Logg inn med PSN
3. Se etter `accountId` i responsen

**Metode 2: Via Chiaki helper**
```bash
# Kommer i Chiaki4deck - bruk remote assist
```

**Metode 3: Manuelt via PS5**
- Komplisert, bruk Metode 1

## 🔧 Feilsøking

### PS5 får ikke IP-adresse
```bash
# Restart PC network
nmcli connection down "PS5-Direct"
nmcli connection up "PS5-Direct"

# Sjekk DHCP leases
sudo cat /var/lib/NetworkManager/dnsmasq-enp4s0.leases
```

### Kan ikke finne PS5 i Chiaki
```bash
# Ping PS5 (erstatt X med PS5 IP)
ping 10.42.0.X

# Sjekk firewall
sudo firewall-cmd --list-all
```

### Remote Play kobler ikke
- Sjekk at PS5 Remote Play er aktivert
- Restart PS5
- Sjekk at PS5 ikke er i hvile-modus (må være påslått)

## 📊 Forventet ytelse

**Med direkte Ethernet:**
- Latency: 1-5 ms (ekstremt lavt!)
- Bitrate: Op til 1 Gbps
- Ingen WiFi-interferens
- Perfekt for konkurransespill

## 🎮 Start Remote Play

Når alt er satt opp:
1. Start Chiaki
2. Velg PS5-tilkoblingen
3. Spill!

## ⚙️ Avanserte innstillinger

### Øk video quality i Chiaki:
```
Settings:
├─ Video Quality: High
├─ Resolution: 1080p
├─ FPS: 60
└─ Bitrate: 20000+ kbps
```

### Automatisk koble til PS5 ved oppstart:
```bash
# PS5-Direct startes automatisk (allerede konfigurert)
systemctl --user status NetworkManager
```
