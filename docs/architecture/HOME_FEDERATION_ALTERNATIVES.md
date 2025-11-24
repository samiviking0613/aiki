# AIKI-HOME Federation - Arkitektur og Alternativer

**Opprettet:** 23.11.2025
**Status:** Implementert Alternativ B (Føderert)
**Fil:** src/circles/home_circle.py

---

## Problemstilling

AIKI-HOME skal kunne installeres i mange hjem (på Raspberry Pi eller lignende).
Systemet må:

1. Fungere lokalt uten internett-tilkobling
2. Dele læring på tvers av installasjoner (pheromones)
3. Respektere GDPR - aldri sende personlig data
4. Være plug-and-play for ikke-tekniske brukere
5. Skalere til tusenvis av installasjoner

---

## Valgt løsning: Alternativ B - Føderert System

```
┌─────────────────────────────────────────────────────────────────┐
│                        AIKI PRIME (Sky)                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   HOME Circle   │  │  Network Circle │  │  Learning Circle│ │
│  │  (Aggregator)   │  │   (ISP KB)      │  │  (Global AI)    │ │
│  └────────┬────────┘  └────────┬────────┘  └─────────────────┘ │
└───────────┼─────────────────────┼───────────────────────────────┘
            │ Pheromone Protocol  │
            │ (GDPR-compliant)    │
    ┌───────┼─────────────────────┼───────┐
    │       ▼                     ▼       │
┌───┴───────────┐  ┌───────────────┐  ┌───┴───────────┐
│  AIKI-HOME 1  │  │  AIKI-HOME 2  │  │  AIKI-HOME N  │
│  (Raspberry Pi)│  │  (Raspberry Pi)│  │  (Raspberry Pi)│
│               │  │               │  │               │
│  ┌─────────┐  │  │  ┌─────────┐  │  │  ┌─────────┐  │
│  │ Local   │  │  │  │ Local   │  │  │  │ Local   │  │
│  │ Learning│  │  │  │ Learning│  │  │  │ Learning│  │
│  └─────────┘  │  │  └─────────┘  │  │  └─────────┘  │
│               │  │               │  │               │
│  ALL PERSONAL │  │  ALL PERSONAL │  │  ALL PERSONAL │
│  DATA STAYS   │  │  DATA STAYS   │  │  DATA STAYS   │
│  HERE         │  │  HERE         │  │  HERE         │
└───────────────┘  └───────────────┘  └───────────────┘
```

### Fordeler

- **Personvern**: All personlig data forblir lokalt
- **Offline-first**: Fungerer uten internett
- **Distribuert læring**: Pheromones sprer gode løsninger
- **Skalerbar**: Prime håndterer kun metadata
- **Resilient**: Hvert hjem er autonomt

### Ulemper

- **Kompleksitet**: Krever sync-protokoll
- **Eventuell konsistens**: Ikke alle har nyeste anbefalinger
- **Deployment**: Må deploye Prime + lokale instanser

---

## Alternativ A - Sentralisert (IKKE valgt)

```
┌─────────────────────────────────────────────────────────────────┐
│                     AIKI PRIME (Alt i sky)                      │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │ All Data    │  │ All Rules   │  │ All Learning            │ │
│  │ (GDPR risk!)│  │             │  │                         │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │ API calls
                              │
    ┌─────────────────────────┼─────────────────────────┐
    │                         │                         │
┌───┴───────────┐  ┌─────────┴─────┐  ┌───────────────┴─┐
│  Hjem 1       │  │  Hjem 2       │  │  Hjem N         │
│  (Thin client)│  │  (Thin client)│  │  (Thin client)  │
└───────────────┘  └───────────────┘  └─────────────────┘
```

### Fordeler

- Enklere arkitektur
- Enkel deployment
- Alltid synkronisert

### Ulemper

- **GDPR-KATASTROFE**: Personlig data i sky
- **Single point of failure**: Prime nede = alt nede
- **Krever alltid internett**
- **Kostnad**: Mye mer server-ressurser

**Hvorfor ikke valgt:** GDPR-risiko og offline-krav.

---

## Alternativ C - Peer-to-Peer (IKKE valgt)

```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│  AIKI-HOME 1  │◄───►│  AIKI-HOME 2  │◄───►│  AIKI-HOME 3  │
│               │     │               │     │               │
│  (Peer node)  │     │  (Peer node)  │     │  (Peer node)  │
└───────┬───────┘     └───────────────┘     └───────┬───────┘
        │                                           │
        └────────────────────┬──────────────────────┘
                             │
                    ┌────────┴────────┐
                    │  AIKI-HOME 4    │
                    │  (Peer node)    │
                    └─────────────────┘
```

### Fordeler

- Ingen sentral server nødvendig
- Maksimal desentralisering
- Ingen single point of failure

### Ulemper

- **NAT-problemer**: De fleste hjemmenettverk er bak NAT
- **Kompleks routing**: Krever DHT eller lignende
- **GDPR-utfordring**: Hvem er databehandler?
- **Latency**: Kan ta lang tid å synce via peers

**Hvorfor ikke valgt:** NAT-problemer gjør P2P upraktisk for hjemmenettverk.

---

## Alternativ D - Hybrid Hub-and-Spoke (MULIG FREMTIDIG)

```
                        ┌─────────────────┐
                        │   AIKI PRIME    │
                        │  (Global Hub)   │
                        └────────┬────────┘
                                 │
            ┌────────────────────┼────────────────────┐
            │                    │                    │
    ┌───────┴───────┐   ┌───────┴───────┐   ┌───────┴───────┐
    │ Regional Hub  │   │ Regional Hub  │   │ Regional Hub  │
    │   (Norge)     │   │   (Sverige)   │   │   (Danmark)   │
    └───────┬───────┘   └───────┬───────┘   └───────────────┘
            │                   │
    ┌───────┼───────┐   ┌───────┼───────┐
    │       │       │   │       │       │
  Home1   Home2   Home3  Home4  Home5
```

### Fordeler

- Bedre latency via regionale hubs
- ISP-spesifikk kunnskap per region
- Gradvis skalering

### Ulemper

- Mer kompleks infrastruktur
- Hvem driver regionale hubs?
- Krever kritisk masse per region

**Status:** Kan implementeres senere hvis vi får mange brukere per region.

---

## Pheromone-mekanismen

Inspirert av maur-kolonier (stigmergy):

```
Hjem A:                          Prime:                           Hjem B:
┌─────────────┐                 ┌─────────────┐                  ┌─────────────┐
│ Regel: block│ ─→ METADATA ─→ │ Aggregerer  │ ─→ ANBEFALING ─→ │ Ny bruker   │
│ social AM   │    (kun %)     │ 73% success │                  │ får forslag │
│ 73% success │                └─────────────┘                  └─────────────┘
└─────────────┘

GDPR-FIREWALL: Kun effektivitetstall sendes, aldri:
- Hvilke apper som blokkeres
- Når brukeren prøver å åpne dem
- Brukerens identitet
```

### Data som SENDES til Prime

```json
{
  "home_id": "anonymized-hash",
  "profile_type": "adhd_adult_wfh",
  "rule_effectiveness": {
    "block_social_morning": 0.73,
    "medication_reminder_8am": 0.95
  }
}
```

### Data som ALDRI sendes

- Navn, e-post, telefon
- IP-adresse, MAC-adresse
- Nettleserhistorikk
- Appbruk-detaljer
- Lokasjonsdata
- Helsedata (medisin-tidspunkter er OK, men ikke hvilken medisin)

---

## Når bør vi vurdere å bytte?

### Bytt til Alternativ A (Sentralisert) hvis:

- [ ] GDPR endres drastisk
- [ ] Alle brukere aktivt samtykker til datalagring
- [ ] Vi trenger real-time ML som krever all data

### Bytt til Alternativ C (P2P) hvis:

- [ ] IPv6 blir universelt
- [ ] NAT traversal blir enkelt (WebRTC forbedres)
- [ ] Vi vil eliminere server-kostnader helt

### Bytt til Alternativ D (Hybrid) hvis:

- [ ] 1000+ brukere i en region
- [ ] ISP-spesifikke problemer dominerer support
- [ ] Latency blir kritisk problem

---

## Implementasjonsdetaljer

### Filer

| Komponent | Fil | Beskrivelse |
|-----------|-----|-------------|
| HOME Circle | `src/circles/home_circle.py` | Federation coordinator |
| Network Circle | `src/circles/network_circle.py` | Nettverksdiagnostikk |
| Pheromone Protocol | `src/federation/pheromone_protocol.py` | Sync-protokoll |

### GDPR-validering

```python
# Alle meldinger valideres mot forbidden_fields
gdpr_forbidden_fields = {
    'name', 'email', 'phone', 'address', 'ip_address',
    'browsing_history', 'search_queries', 'messages',
    'location', 'device_id', 'mac_address', 'ssn',
    'bank_account', 'credit_card', 'health_records'
}
```

### Sync-intervaller

| Event | Intervall |
|-------|-----------|
| Heartbeat | 5 min |
| Pheromone update | 1 time |
| Full sync | 24 timer |
| Network diagnostic | Ved problem |

---

## Referanser

- [Stigmergy in Ant Colonies](https://en.wikipedia.org/wiki/Stigmergy)
- [GDPR Art. 5 - Data Minimization](https://gdpr-info.eu/art-5-gdpr/)
- [Federation Architecture Patterns](https://martinfowler.com/articles/patterns-of-distributed-systems/)
