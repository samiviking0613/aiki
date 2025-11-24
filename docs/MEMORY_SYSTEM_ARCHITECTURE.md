# AIKI Memory System Architecture

**Dato:** 23. november 2025
**Status:** OPERATIV - Graf og relasjoner implementert

---

## Oversikt

AIKI Memory System bruker en **hybrid 3-lags arkitektur** som kombinerer:

1. **SQLite + FTS5** - Rå samtaler med eksakt tekst-søk
2. **Qdrant (mem0)** - Semantisk vektorsøk
3. **Neo4j** - Graf for relasjoner mellom minner

```
┌─────────────────────────────────────────────────────────────┐
│                    UNIFIED MEMORY API                        │
│                 src/memory/unified_memory.py                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  store_conversation()  →  SQLite (sync) + Neo4j (async)     │
│  search()              →  Qdrant + SQLite hybrid            │
│  search_exact()        →  SQLite FTS5                       │
│  search_graph_*()      →  Neo4j                             │
│  find_related()        →  Neo4j traversal                   │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   SQLite     │  │   Qdrant     │  │   Neo4j      │       │
│  │   + FTS5     │  │   (mem0)     │  │   Graf       │       │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤       │
│  │ 193 samtaler │  │ ~2140 vecs   │  │ 219 noder    │       │
│  │ 9305 msgs    │  │ Semantic     │  │ 556 edges    │       │
│  │ Exact match  │  │ search       │  │ Relasjoner   │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Komponenter

### 1. Raw Conversation Store (SQLite + FTS5)

**Fil:** `src/memory/raw_conversation_store.py`
**Database:** `data/raw_conversations.db`

Lagrer komplette samtaler med zstd-komprimering (~90% reduksjon).

**Tabeller:**
- `conversations` - Metadata (session_id, source, title, created_at)
- `messages` - Komprimerte meldinger (content_compressed, role)
- `messages_fts` - FTS5 virtuell tabell for full-tekst søk

**Kilder:**
- ChatGPT eksport (148 samtaler)
- Claude Code sesjoner
- AIKI v3 sessions (38)

### 2. Qdrant Vector Store (via mem0)

**Konfigurasjon:** OpenRouter + text-embedding-3-small
**Collection:** `mem0_memories`

Semantisk søk for å finne "lignende" minner basert på mening, ikke eksakte ord.

### 3. Neo4j Graf

**Fil:** `src/memory/graph_memory.py`
**Tilkobling:** `bolt://localhost:7687`

**Node-typer:**
| Type | Antall | Beskrivelse |
|------|--------|-------------|
| Conversation | 193 | Hver samtale |
| Topic | 18 | Emner (ADHD, nettverk, minne...) |
| Project | 4 | Prosjekter (AIKI, AIKI-HOME...) |
| Entity | 2 | Personer, organisasjoner |

**Edge-typer:**
| Type | Antall | Relasjon |
|------|--------|----------|
| ABOUT | 265 | Conversation → Topic |
| FOLLOWS | 187 | Conversation → Conversation (temporal) |
| PART_OF | 99 | Conversation → Project |

---

## Unified Memory API

**Fil:** `src/memory/unified_memory.py`

### Bruk

```python
from src.memory import get_unified_memory, store_memory_sync

# Hent singleton
memory = get_unified_memory()

# Lagre minne (graf oppdateres automatisk i bakgrunnen)
store_memory_sync("Jovnna foretrekker visuelle forklaringer", title="Preferanse")

# Søk
results = memory.search_exact("visuell")           # SQLite FTS5
results = memory.search_graph_project("AIKI")      # Neo4j
results = memory.search_graph_topics("ADHD")       # Neo4j
results = memory.find_related("session-123")       # Neo4j traversal

# Statistikk
stats = memory.get_stats()
# → {total_conversations: 193, total_messages: 9305, graph_nodes: 219, graph_edges: 556}
```

### Async Graf-oppdatering

Når du lagrer en samtale:
1. SQLite lagres **synkront** (umiddelbart)
2. Neo4j oppdateres **asynkront** i bakgrunnen via `ThreadPoolExecutor`

Dette gir umiddelbar respons mens grafen oppdateres uten å blokkere.

---

## Keyword Extractor

**Fil:** `src/memory/keyword_extractor.py`

Automatisk deteksjon av prosjekter og emner for graf-linking.

### To-trinns strategi:

1. **Fast path** (~0ms, gratis)
   - String matching med word boundaries
   - 48 baseline keywords + lærte keywords

2. **Slow path** (~500ms, ~$0.001/kall)
   - LLM via OpenRouter/gpt-4o-mini
   - Brukes kun hvis fast path gir 0 treff
   - Nye keywords lagres automatisk for fremtidig fast path

**Lærte keywords:** `data/learned_keywords.json`

```json
{
  "projects": ["GitOps", "Kubernetes", "Terraform"],
  "topics": ["automatisering", "cloud computing", "infrastruktur"]
}
```

### Aktivere LLM-læring:

```python
from src.memory.unified_memory import UnifiedMemory

# Med LLM-læring (oppdager nye topics automatisk)
memory = UnifiedMemory(use_llm_extraction=True)
```

---

## Filer

```
src/memory/
├── __init__.py                 # Exports
├── unified_memory.py           # Unified API (ANBEFALT)
├── raw_conversation_store.py   # SQLite + FTS5
├── graph_memory.py             # Neo4j graf
├── keyword_extractor.py        # Smart keyword-ekstraksjon
└── hierarchical_memory.py      # Legacy 10-type minne-system

data/
├── raw_conversations.db        # SQLite database (~21MB)
├── learned_keywords.json       # Lærte keywords fra LLM
└── shared_qdrant/              # Qdrant persistent storage

scripts/
├── migrate_memories.py         # Import ChatGPT/Claude samtaler
└── populate_graph.py           # Bygg graf fra SQLite
```

---

## Historikk

| Dato | Hendelse |
|------|----------|
| 23.11.2025 | Audit identifiserte mangel på relasjoner |
| 23.11.2025 | Implementert SQLite + FTS5 raw storage |
| 23.11.2025 | Migrert 148 ChatGPT + 38 AIKI v3 samtaler |
| 23.11.2025 | Implementert Neo4j graf med 219 noder |
| 23.11.2025 | Implementert UnifiedMemory med async oppdatering |
| 23.11.2025 | Implementert smart keyword-ekstraksjon med læring |

---

## Fremtidige forbedringer

- [ ] Procedural memory (workflows, skills)
- [ ] Emotional memory markers
- [ ] Cross-session entity tracking
- [ ] Memory consolidation (compress old memories)
- [ ] Memory importance scoring
