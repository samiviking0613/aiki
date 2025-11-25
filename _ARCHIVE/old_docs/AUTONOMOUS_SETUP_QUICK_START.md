# 🚀 AIKI Autonomous Chiaki - Quick Start

## TL;DR - Kjør dette:

```bash
python3 ~/aiki/autonomous_chiaki_setup.py
```

## Hva skjer automatisk:

1. ✅ Verifiserer PS5 er på nettverk (10.42.0.223)
2. 🌐 Åpner browser for PSN login (én gang)
3. ⌨️  Ber om PS5 PIN (fra Settings > Remote Play)
4. 📝 Konfigurerer Chiaki automatisk
5. ✅ Verifiserer og rapporterer suksess

## For 100% autonomi (ingen prompts):

### Steg 1: Hent PSN AccountID (én gang)
```bash
python3 ~/aiki/get_psn_accountid.py
# Logg inn når browser åpner
# AccountID lagres automatisk i ~/aiki/psn_accountid.txt
```

### Steg 2: Hent PS5 PIN og lagre
```bash
# På PS5: Settings > System > Remote Play > Link Device
# Du ser en 8-sifret PIN, for eksempel: 01234567

echo "01234567" > ~/aiki/ps5_registration_pin.txt
```

### Steg 3: Kjør autonomt setup
```bash
python3 ~/aiki/autonomous_chiaki_setup.py
# Ingen prompts! Alt skjer automatisk! 🤖
```

## Etter setup er ferdig:

```bash
# Start Chiaki
flatpak run io.github.streetpea.Chiaki4deck

# Din PS5 skal vises automatisk
# Klikk på den for å starte Remote Play!
```

## Status og logging:

```bash
# Se live logg
tail -f ~/aiki/autonomous_chiaki.log

# Sjekk config
cat ~/.var/app/io.github.streetpea.Chiaki4deck/config/Chiaki/Chiaki.conf

# Sjekk PS5 tilkobling
~/aiki/check_ps5.sh
```

## Feilsøking:

### Problem: "PS5 not reachable"
**Løsning:**
```bash
# Sjekk at Ethernet-kabel er koblet
# Sjekk at PS5 er powered on (ikke i rest mode)
ping 10.42.0.223
```

### Problem: "Failed to get PSN AccountID"
**Løsning:**
```bash
# Kjør PSN fetcher manuelt
python3 ~/aiki/get_psn_accountid.py
# Sørg for å logge inn når browser åpner
```

### Problem: "No registration PIN provided"
**Løsning:**
```bash
# Lag PIN-fil manuelt (erstatt med din faktiske PIN)
echo "12345678" > ~/aiki/ps5_registration_pin.txt
```

## Veien til full autonomi:

Dette scriptet demonstrerer AIKI autonomi-prinsippene:

- ✅ **Config file manipulation** - Ingen GUI automation nødvendig
- ✅ **Minimal user interaction** - Kun nødvendig login/PIN
- ✅ **Intelligent caching** - PSN AccountID lagres for gjenbruk
- ✅ **Autonomous workflows** - Async pipeline with error handling
- ✅ **No sudo required** - Alt kan gjøres som vanlig bruker

**Neste nivå:** Med passwordless sudo + xdotool kan AIKI:
- Automatisk navigere PS5 menyer
- Hente PIN fra skjerm (OCR)
- Fullstendig zero-touch setup

Se: `~/aiki/AIKI_AUTONOMY_PLAN.md`

---

**Made with 🤖 by AIKI - Your Autonomous AI Assistant**
