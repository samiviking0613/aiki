# 🤖 AIKI Autonomous Chiaki Setup

## Hva er dette?

Dette er et **fullt autonomt** oppsett-script for Chiaki PS5 Remote Play, designet i tråd med AIKI autonomi-prinsippene:

- **INGEN GUI automation** nødvendig
- **INGEN sudo-tilgang** kreves
- **Minimal manuell interaksjon** - kun PS5 PIN-kode

## Hvordan det fungerer

Scriptet bruker AIKI v3 autonomous patterns til å:

1. ✅ **Verifisere PS5 nettverk** - Sjekker at PS5 er tilgjengelig på 10.42.0.223
2. ✅ **Hente PSN AccountID** - Bruker Selenium automation (krever kun login)
3. ✅ **Manipulere Chiaki config** - Direkte filredigering (INGEN GUI!)
4. ✅ **Verifisere oppsett** - Sjekker at alt er korrekt konfigurert

## Kjøre scriptet

### Metode 1: Semi-Autonom (anbefalt første gang)

```bash
python3 ~/aiki/autonomous_chiaki_setup.py
```

Du vil bli bedt om:
- Logg inn på PSN (én gang, Selenium browser)
- PS5 PIN-kode (8 sifre fra PS5)

### Metode 2: FULLT Autonom (null interaksjon)

For 100% autonomi, lag filen `~/aiki/ps5_registration_pin.txt` først:

```bash
# På PS5: Settings > System > Remote Play > Link Device
# Noter 8-sifret PIN, så kjør:
echo "12345678" > ~/aiki/ps5_registration_pin.txt

# Deretter kjør scriptet - det finner PIN automatisk!
python3 ~/aiki/autonomous_chiaki_setup.py
```

PSN AccountID caches også automatisk, så andre gang er det 100% autonomt!

## Output og Logging

- **Live status** - Colored terminal output med emojis
- **Logg-fil** - `/home/jovnna/aiki/autonomous_chiaki.log`
- **Config sammendrag** - `/home/jovnna/aiki/chiaki_config_summary.json`
- **PSN AccountID cache** - `/home/jovnna/aiki/psn_accountid.txt`

## Feilsøking

### PS5 ikke funnet

```bash
# Sjekk at PS5 er koblet til og powered on
~/aiki/check_ps5.sh

# Verifiser IP
ping -c 1 10.42.0.223
```

### PSN AccountID feil

```bash
# Slett cache og prøv igjen
rm ~/aiki/psn_accountid.txt
python3 ~/aiki/autonomous_chiaki_setup.py
```

### Chiaki config ikke funker

```bash
# Se på config-fil
cat ~/.var/app/io.github.streetpea.Chiaki4deck/config/Chiaki/Chiaki.conf

# Sjekk logg
tail -f ~/aiki/autonomous_chiaki.log
```

## Arkitektur

```
┌─────────────────────────────────────────────┐
│   AIKI Autonomous Chiaki Setup Pipeline    │
└─────────────────────────────────────────────┘
           │
           ├─> 1. Verify PS5 (ping)
           │
           ├─> 2. Get PSN AccountID
           │      ├─> Check cache (psn_accountid.txt)
           │      └─> Run Selenium if needed
           │
           ├─> 3. Get Registration PIN
           │      ├─> Check file (ps5_registration_pin.txt)
           │      └─> Prompt user if needed
           │
           ├─> 4. Configure Chiaki
           │      └─> Direct INI file manipulation
           │
           └─> 5. Verify & Report
```

## AIKI v3 Patterns Brukt

- **Safe file operations** (helpers.py patterns)
- **Async execution** (asyncio pipeline)
- **Intelligent error handling** (retry, fallback, logging)
- **Progress tracking** (colored status output)
- **Config manipulation** (direct file edit, no GUI)
- **Autonomous workflows** (minimal human interaction)

## Neste Steg Mot Full Autonomi

For å oppnå 100% autonomi for ALLE oppgaver:

1. **GUI Automation** - Install xdotool/ydotool (krever sudo)
2. **Passwordless sudo** - For package management
3. **Non-intrusive screenshots** - For AIKI Vision (scrot/maim)

Se: `/home/jovnna/aiki/AIKI_AUTONOMY_PLAN.md`

## Suksess-kriterier

✅ Script kjører uten feil
✅ PSN AccountID hentet og cachet
✅ Chiaki.conf oppdatert med PS5 info
✅ PS5 vises i Chiaki
✅ Remote Play connection fungerer

## Credits

Laget av AIKI (Claude Code) ved hjelp av:
- AIKI v3 autonomous patterns
- Chiaki4deck Flatpak
- Python asyncio + Selenium
- AIKI autonomi-filosofi 🤖
