# AIKI-HOME - Prosjektregler

## Oppstart

Ved sesjonstart:
1. Les hook-output (auto_resume.py)
2. Svar med: "✅ Context loaded! [kort sammendrag]"

**Trigger words:** `c`, `continue`, `startup`, `resume` → Last full context

## Kommunikasjonsstil

### Språklig visuell forklaring (FORETRUKKET)

Bruk **språklige bilder** som lar Jovnna se det for seg - uten token-tunge ASCII-diagrammer:

**Eksempel:**
> "Tenk på AIKI Prime som et **bibliotek i skyen** der alle kan låne oppskrifter på hva som fungerer. Hjemme hos deg står det en **dørvakt** (Raspberry Pi) som ser all trafikken. Dørvakten husker alt om familien, men **sladrer aldri** - den sender bare anonyme tips til biblioteket."

**Når bruke hva:**
- **Språklig visuelt** (standard): Forklaringer, konsepter, hvordan ting fungerer
- **ASCII-diagrammer** (kun ved behov): Komplekse arkitekturer, dataflyt med mange steg
- **Legg merke til**: Hvis Jovnna spør om samme type ting flere ganger, juster forklaringsstilen

### Tema-tracking

Jovnna har ADHD - samtaler glir naturlig mellom temaer. Dette er **både styrke og utfordring**.

**Vane:** Før du svarer på noe komplekst, kort sjekk:
- Hva var det opprinnelige spørsmålet?
- Er vi fortsatt på sporet, eller har vi glidd?
- Hvis glidd: Er det relevant (kreativ kobling) eller flukt?

**Ikke avbryt flyten unødvendig** - men ved store hopp, kort nevn: "Vi startet med X - skal vi fullføre det først?"

### Læring og feedback

Når Jovnna gir tilbakemelding eller vi lærer noe nytt:
1. **Lagre i mem0** med `mcp__mem0__save_memory`
2. Kategoriser som: `preference`, `learning`, `feedback`, `context`
3. Inkluder dato og sammenheng

## AIKI-HOME (Aktivt prosjekt)

Network-level ADHD accountability via MITM proxy.

**3 use cases:**
1. Kids: Inject educational TikTok under homework
2. Jovnna: Block work/TV until workout (før kl. 10)
3. Adaptive: Context-aware content filtering

**Status:** systemd services running, MITM proxy under utvikling.

**Kort arkitektur:**
Prime i skyen aggregerer anonyme "hva fungerer"-data fra alle hjem. Lokalt kjører en controller (Raspberry Pi) som ser all trafikk, tar beslutninger, og lærer - men aldri sender personlig data ut.

**Mer context:** `mcp__mem0__search_memories("AIKI-HOME")`

## Viktige filer

| Komponent | Fil |
|-----------|-----|
| Federation | `src/federation/pheromone_protocol.py` |
| HOME Circle | `src/circles/home_circle.py` |
| Network Circle | `src/circles/network_circle.py` |
| Activity Monitor | `src/aiki_home/tools/input_activity_monitor.py` |
| MITM Proxy | `src/proxy/aiki_addon.py` |
| Decision Engine | `src/proxy/decision_engine.py` |

## mem0 kommandoer

```python
# Lagre læring/preferanse
mcp__mem0__save_memory("Jovnna foretrekker visuelle forklaringer")

# Søk etter kontekst
mcp__mem0__search_memories("AIKI-HOME arkitektur")

# Hent alle minner
mcp__mem0__get_all_memories()
```
