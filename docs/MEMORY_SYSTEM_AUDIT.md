# AIKI Minne-System Audit

**Dato:** 23.11.2025
**Status:** KRITISK - Mangler struktur og relasjoner

---

## Sammendrag

Minne-systemet fungerer som en **stor boks med løse lapper** - vi kan søke etter lignende lapper via vektorsøk, men det finnes **ingen struktur, ingen koblinger, ingen hierarki**.

**Hovedfunn:**
- 5 collections med totalt ~2140 points
- Inkonsistent payload-struktur (minst 5 ulike formater)
- **INGEN edges/relasjoner mellom minner**
- **INGEN tags-system**
- Kun 9 av 1662 minner har `project`-felt
- Kun 70 av 1662 har `category`-felt

---

## Collections Oversikt

| Collection | Points | Formål |
|------------|--------|--------|
| mem0_memories | 1662 | Hovedminne (mem0) |
| aiki_consciousness | 473 | Migrerte ChatGPT-samtaler + AIKI v3 |
| claude_code_memories | 1 | Claude Code spesifikk |
| claude_chat_memories | 0 | Tom |
| mem0migrations | 2 | Migrasjonsdata |

---

## mem0_memories - Detaljert Analyse

### Payload-felter (av 1662 points)

**Alltid til stede (100%):**
- `user_id` - Hvem minnet tilhører
- `data` - Selve innholdet
- `hash` - Unik identifikator
- `created_at` - Opprettelsestidspunkt

**Ofte til stede (20-50%):**
- `agent_id` - 782 points (47%) - Hvilken agent som lagret
- `source` - 757 points (45%) - Hvor data kom fra
- `run_id` - 754 points (45%) - Session-ID
- `timestamp` - 347 points (20%)
- `type` - 327 points (19%)

**Sjelden til stede (<5%):**
- `category` - 70 points (4%)
- `project` - 9 points (<1%)
- `importance` - 23 points (1%)

### Agenter som lagrer

| Agent | Minner |
|-------|--------|
| system_health_monitor | 305 |
| aiki_consciousness | 212 |
| ultimate_self_healing | 97 |
| claude_code | 58 |
| aiki_v3_migration | 16 |

### Kilder

| Kilde | Minner |
|-------|--------|
| aiki_ultimate | 296 |
| chatgpt_web | 223 |
| claude_desktop | 180 |
| aiki_v3 | 23 |

### Typer

| Type | Minner |
|------|--------|
| aiki_conversation | 211 |
| session_summary | 13 |
| consciousness_discovery | 12 |
| system_status | 11 |
| milestone | 9 |

---

## aiki_consciousness - Detaljert Analyse

Denne collection inneholder migrerte data:
- **323 ChatGPT-samtaler** (chunked)
- **147 AIKI v3 direkte** data
- **3 AIKI Ultimate** conversations

Har bedre struktur med:
- `conversation_title`
- `conversation_date`
- `chunk_index` / `total_chunks`
- `category`

Men fortsatt **ingen relasjoner mellom chunks**.

---

## HVA MANGLER (Kritisk)

### 1. Edges / Relasjoner
Ingen måte å si "dette minnet er relatert til det":
- `parent_id` - MANGLER
- `related_to` - MANGLER
- `edges` - MANGLER
- `links` - MANGLER
- `references` - MANGLER

### 2. Strukturert Kategorisering
- `tags` - MANGLER helt
- `category` - Kun 4% har dette
- `project` - Kun 0.5% har dette

### 3. Hierarki
Ingen måte å bygge tre-struktur:
- "Dette er en detalj under dette konseptet"
- "Denne samtalen er del av dette prosjektet"

### 4. Temporal Relasjoner
- Ingen "dette kom etter dette"
- Ingen "dette er oppfølging av dette"

### 5. Konsistent Schema
Minst 5 ulike payload-strukturer brukes, noe som gjør queries vanskelig.

---

## Eksempler på Inkonsistens

**Struktur 1:** (minimal)
```json
{
  "user_id": "jovnna",
  "data": "...",
  "hash": "...",
  "created_at": "..."
}
```

**Struktur 2:** (agent-basert)
```json
{
  "user_id": "jovnna",
  "agent_id": "system_health_monitor",
  "run_id": "...",
  "data": "...",
  "hash": "...",
  "created_at": "..."
}
```

**Struktur 3:** (full metadata)
```json
{
  "timestamp": "...",
  "source": "aiki_ultimate",
  "agent_id": "...",
  "run_id": "...",
  "type": "aiki_conversation",
  "category": "...",
  "user_id": "jovnna",
  "data": "...",
  "hash": "...",
  "created_at": "..."
}
```

---

## Konsekvenser

1. **Søk er begrenset** - Kun vektorsøk, ingen strukturerte queries
2. **Kontekst går tapt** - Vet ikke hva som hører sammen
3. **Duplikater** - Kan ikke oppdage relaterte minner
4. **ADHD-utfordring** - Uten struktur gjentar vi arbeid

---

## Anbefalinger

### Kortsiktig (Quick Wins)

1. **Standardiser payload** - Definer obligatoriske felter
2. **Legg til tags** - Enkel liste med nøkkelord
3. **Legg til project** - Hvilket prosjekt tilhører minnet

### Mellomsiktig

4. **Implementer parent_id** - Hierarki
5. **Legg til related_to** - Liste med relaterte minne-IDer
6. **Migrere eksisterende** - Oppdater gamle minner med ny struktur

### Langsiktig

7. **Graf-database** - Neo4j eller mem0graph for ekte relasjoner
8. **Automatisk linking** - AI som foreslår relasjoner
9. **Kategori-ontologi** - Definert taksonomi

---

## Foreslått Ny Payload-Struktur

```json
{
  // Obligatoriske (100%)
  "user_id": "jovnna",
  "data": "Innholdet",
  "hash": "unik-hash",
  "created_at": "2025-11-23T...",

  // Anbefalt (bør være med)
  "type": "learning|preference|fact|conversation|decision",
  "source": "claude_code|aiki|chatgpt|manual",
  "project": "aiki-home|aiki-ultimate|personal",
  "tags": ["adhd", "arkitektur", "mitm"],

  // Relasjoner
  "parent_id": "uuid-av-forelder",
  "related_to": ["uuid1", "uuid2"],

  // Valgfritt
  "importance": 1-5,
  "expires_at": null,
  "agent_id": "...",
  "session_id": "..."
}
```

---

## Neste Steg

1. [ ] Beslutt: Utvide mem0 eller bytte til graf?
2. [ ] Definer standard schema
3. [ ] Lag migreringsplan for eksisterende 2140 minner
4. [ ] Implementer validering ved lagring
5. [ ] Lag verktøy for å legge til relasjoner manuelt
