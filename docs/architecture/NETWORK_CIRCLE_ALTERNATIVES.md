# Network Circle - Arkitektur og Alternativer

**Opprettet:** 23.11.2025
**Status:** Implementert Alternativ A (Egen Circle i Prime)
**Fil:** src/circles/network_circle.py

---

## Problemstilling

AIKI-HOME må kunne:

1. **Diagnostisere** nettverksproblemer automatisk
2. **Løse** problemer der det er mulig (auto-fix)
3. **Veilede** brukeren når manuell handling kreves
4. **Lære** fra alle installasjoner for å forbedre løsninger
5. Fungere **plug-and-play** for ikke-tekniske brukere

### Typiske nettverksproblemer

| Problem | Frekvens | Kan auto-fikses? |
|---------|----------|------------------|
| Dobbel NAT | 40% | Nei |
| CGNAT (ISP-NAT) | 25% | Nei |
| UPnP deaktivert | 20% | Noen ganger |
| DNS-problemer | 10% | Ja |
| Firewall blokkerer | 5% | Noen ganger |

---

## Valgt løsning: Alternativ A - Egen Circle i Prime

```
┌─────────────────────────────────────────────────────────────────┐
│                         AIKI PRIME                              │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                   NETWORK CIRCLE                            ││
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ ││
│  │  │ISP Knowledge│  │ Pheromone   │  │ Solution Generator  │ ││
│  │  │    Base     │  │   Trails    │  │                     │ ││
│  │  │             │  │             │  │ - Auto-fix scripts  │ ││
│  │  │ - Telenor   │  │ - Problem A │  │ - User instructions │ ││
│  │  │ - Altibox   │  │   → Sol. X  │  │ - ISP contact info  │ ││
│  │  │ - Telia     │  │ - Problem B │  │                     │ ││
│  │  │ - NextGenTel│  │   → Sol. Y  │  │                     │ ││
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │ Diagnostics + Feedback
                              │
    ┌─────────────────────────┼─────────────────────────────────┐
    │                         │                                  │
┌───┴───────────────┐  ┌─────┴────────────┐  ┌─────────────────┴─┐
│  AIKI-HOME 1      │  │  AIKI-HOME 2     │  │  AIKI-HOME N      │
│  ┌─────────────┐  │  │  ┌─────────────┐ │  │  ┌─────────────┐  │
│  │Network Agent│  │  │  │Network Agent│ │  │  │Network Agent│  │
│  │             │  │  │  │             │ │  │  │             │  │
│  │-Diagnostikk │  │  │  │-Diagnostikk │ │  │  │-Diagnostikk │  │
│  │-Auto-fix    │  │  │  │-Auto-fix    │ │  │  │-Auto-fix    │  │
│  │-UI feedback │  │  │  │-UI feedback │ │  │  │-UI feedback │  │
│  └─────────────┘  │  │  └─────────────┘ │  │  └─────────────┘  │
└───────────────────┘  └──────────────────┘  └───────────────────┘
```

### Fordeler

- **Sentralisert læring**: All ISP-kunnskap samlet
- **Rask forbedring**: Ny løsning propageres til alle
- **Konsistent**: Alle får samme kvalitet på support
- **Enkel vedlikehold**: Kun én Network Circle å oppdatere

### Ulemper

- **Latency**: Må kontakte Prime for nye løsninger
- **Offline-begrenset**: Kan ikke lære uten nett
- **Single point of knowledge**: Hvis Prime er nede, ingen nye løsninger

---

## Alternativ B - Distribuert i HOME Circle (IKKE valgt)

```
┌─────────────────────────────────────────────────────────────────┐
│                         AIKI PRIME                              │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                     HOME CIRCLE                             ││
│  │  ┌─────────────────────────────────────────────────────┐   ││
│  │  │         Integrert Network-modul                     │   ││
│  │  │         (Del av HOME, ikke egen circle)             │   ││
│  │  └─────────────────────────────────────────────────────┘   ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

### Fordeler

- Enklere arkitektur
- Færre komponenter

### Ulemper

- **Blandet ansvar**: HOME Circle blir for stor
- **Vanskelig å teste**: Nettverkslogikk blandet med pheromones
- **Mindre fleksibel**: Kan ikke skalere uavhengig

**Hvorfor ikke valgt:** Brudd på Single Responsibility Principle.

---

## Alternativ C - Lokal Network Agent uten Prime (IKKE valgt)

```
┌───────────────────┐  ┌──────────────────┐  ┌───────────────────┐
│  AIKI-HOME 1      │  │  AIKI-HOME 2     │  │  AIKI-HOME N      │
│  ┌─────────────┐  │  │  ┌─────────────┐ │  │  ┌─────────────┐  │
│  │Full Network │  │  │  │Full Network │ │  │  │Full Network │  │
│  │   Engine    │  │  │  │   Engine    │ │  │  │   Engine    │  │
│  │             │  │  │  │             │ │  │  │             │  │
│  │All ISP data │  │  │  │All ISP data │ │  │  │All ISP data │  │
│  │All solutions│  │  │  │All solutions│ │  │  │All solutions│  │
│  └─────────────┘  │  │  └─────────────┘ │  │  └─────────────┘  │
└───────────────────┘  └──────────────────┘  └───────────────────┘
                              ▲
                              │ Ingen deling!
```

### Fordeler

- Fullstendig offline-kapabel
- Ingen avhengighet til Prime

### Ulemper

- **Ingen læring på tvers**: Løsninger deles ikke
- **Duplisert data**: Hver enhet har all data
- **Vanskelig oppdatering**: Må pushe til alle enheter

**Hvorfor ikke valgt:** Mister fordelen med distribuert læring.

---

## Alternativ D - Per-Region Network Circles (MULIG FREMTIDIG)

```
┌─────────────────┐
│   AIKI PRIME    │
│  (Koordinator)  │
└────────┬────────┘
         │
    ┌────┼────┬────────────┐
    │    │    │            │
┌───┴────┴─┐ ┌┴─────────┐ ┌┴─────────┐
│ Network  │ │ Network  │ │ Network  │
│ Circle   │ │ Circle   │ │ Circle   │
│ (Norge)  │ │ (Sverige)│ │ (Danmark)│
│          │ │          │ │          │
│ Telenor  │ │ Telia SE │ │ TDC      │
│ Altibox  │ │ Bahnhof  │ │ YouSee   │
│ Telia NO │ │ Bredband │ │ Stofa    │
└──────────┘ └──────────┘ └──────────┘
```

### Fordeler

- ISP-spesifikk ekspertise per land
- Bedre latency til lokal circle
- Kan ha lokale "eksperter" per region

### Ulemper

- Mer kompleks infrastruktur
- Krever kritisk masse per region
- Hvem drifter regionale circles?

**Status:** Kan implementeres når vi har mange brukere per land.

---

## ISP Knowledge Base - Hvordan det fungerer

### Eksempel: Telenor-bruker med problem

```
1. AIKI-HOME kjører diagnostikk lokalt
   → Oppdager: NAT type = symmetric, UPnP = unavailable

2. Sender til Network Circle (anonymisert):
   {
     "problem": "nat_traversal_failed",
     "isp": "telenor",
     "nat_type": "symmetric",
     "upnp": false
   }

3. Network Circle sjekker ISP Knowledge Base:
   - Telenor har kjent problem med symmetric NAT på ZTE-rutere
   - Pheromone trail viser: 78% løst ved å kontakte support

4. Returnerer løsning:
   {
     "solution_type": "isp_contact",
     "instructions": "Ring Telenor 915 09 000, be om bridge mode",
     "success_rate": 0.78,
     "alternative": "Kjøp egen ruter, koble i bridge mode"
   }

5. Bruker gir feedback etter løsning:
   - SUCCESS → Pheromone forsterkes
   - FAILED → Pheromone svekkes, prøv alternativ
```

### Pheromone Trails for Network

```python
# Problem → Løsning mapping med styrke
pheromone_trails = {
    ('telenor', 'double_nat'): {
        'isp_contact_bridge_mode': 0.78,  # Mest effektiv
        'own_router_bridge': 0.65,
        'accept_limitation': 0.20
    },
    ('altibox', 'upnp_disabled'): {
        'enable_in_router': 0.92,  # Nesten alltid løsbart
        'manual_port_forward': 0.85
    }
}
```

---

## Når bør vi vurdere å bytte?

### Bytt til Alternativ C (Lokal) hvis:

- [ ] Offline-modus blir kritisk viktig
- [ ] Prime har høy nedetid
- [ ] Brukerne ikke vil sende noen data

### Bytt til Alternativ D (Regional) hvis:

- [ ] 500+ brukere i et land
- [ ] Landsspesifikke ISP-problemer dominerer
- [ ] Latency til Prime blir problem

### Kombiner med Alternativ B hvis:

- [ ] Network-kompleksiteten øker dramatisk
- [ ] HOME Circle trenger tight integration

---

## Implementasjonsdetaljer

### Hovedfil

`src/circles/network_circle.py` - ~450 linjer

### Kjerneklasser

```python
class NetworkProblem(Enum):
    DOUBLE_NAT = "double_nat"
    CGNAT = "cgnat"
    UPN_UNAVAILABLE = "upnp_unavailable"
    DNS_ISSUES = "dns_issues"
    FIREWALL_BLOCKING = "firewall_blocking"
    SLOW_CONNECTION = "slow_connection"
    INTERMITTENT = "intermittent"

class SolutionType(Enum):
    AUTO_FIX = "auto_fix"         # Kan fikses automatisk
    USER_ACTION = "user_action"   # Bruker må gjøre noe
    ISP_CONTACT = "isp_contact"   # Må kontakte ISP
    HARDWARE_CHANGE = "hardware"   # Trenger ny hardware
    WORKAROUND = "workaround"     # Kan ikke fikses, men omgås
```

### Eksempel ISP-profil

```python
ISPProfile(
    name='Telenor',
    country='NO',
    common_problems={
        NetworkProblem.DOUBLE_NAT: 0.35,
        NetworkProblem.CGNAT: 0.15
    },
    known_solutions={
        NetworkProblem.DOUBLE_NAT: NetworkSolution(
            solution_type=SolutionType.ISP_CONTACT,
            description='Ring Telenor support, be om bridge mode',
            instructions=['Ring 915 09 000', 'Be om "bridge mode"'],
            success_rate=0.78
        )
    }
)
```

---

## Referanser

- [NAT Traversal Techniques](https://en.wikipedia.org/wiki/NAT_traversal)
- [UPnP IGD Protocol](https://en.wikipedia.org/wiki/Internet_Gateway_Device_Protocol)
- [CGNAT - Carrier-grade NAT](https://en.wikipedia.org/wiki/Carrier-grade_NAT)
- [Norske ISP-er oversikt](https://www.telecom.no/oversikter/internett/)
