# SESJON 13. NOVEMBER 2025 - MEM0 INTEGRASJON OG KRITISKE FUNN

## Dato og Tid
- Sesjon: 13. november 2025
- Tidsperiode: Ettermiddag/kveld
- Deltakere: Jovnna + Claude Code

---

## HVA VI GJORDE

### 1. Satte opp mem0 med OpenRouter
- **LLM:** `openai/gpt-4o-mini` (via OpenRouter)
- **Embeddings:** `text-embedding-3-small` (1536 dimensjoner)
- **API-nøkkel:** `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`
- **Base URL:** `https://openrouter.ai/api/v1`
- **Versjon:** mem0 1.0.0

### 2. Opprettet Delt Qdrant Database
- **Sti:** `/home/jovnna/aiki/shared_qdrant/`
- **Collection:** `mem0_memories`
- **Mål:** Delt minne på tvers av:
  - Claude Code (via MCP-server)
  - Open Interpreter
  - Andre AIKI-komponenter

### 3. Installerte MCP-server
- **Repo:** `coleam00/mcp-mem0`
- **Lokasjon:** `/home/jovnna/aiki/mcp-mem0/`
- **Konfig:** `/home/jovnna/aiki/.mcp.json`
- **Status:** Installert men ikke aktivert (krever Claude Code restart)
- **Transport:** stdio (Claude Code starter serveren)

### 4. Kartla Eksisterende AIKI Minne-system
- **Lokasjon:** `/run/media/jovnna/CEVAULT2TB/AIKI_v3/`
- **Innhold:**
  - 200+ JSON minnefiler
  - 1,234 sesjoner dokumentert
  - 21,000+ autonome handlinger logget
- **Strukturer:** identity, sessions, claude, collaboration, development, experiences
- **Minnetyper allerede implementert:**
  - Episodic memory (sesjonsminner)
  - Semantic memory (kunnskapsminner)
  - Working memory (aktiv kontekst)

---

## KRITISK PROBLEM OPPDAGET 🚨

### mem0 1.0.0 persisterer IKKE data til fil-basert Qdrant!

#### Symptomer:
1. ✅ `m.add(text, user_id='jovnna')` returnerer SUCCESS
2. ✅ `m.get_all()` fungerer MENS Python-scriptet lever
3. ✅ `m.search()` fungerer MENS Python-scriptet lever
4. ❌ Når scriptet avsluttes, forsvinner ALL data
5. ❌ Ny kjøring av `m.get_all()` returnerer tom liste
6. ❌ `storage.sqlite` har 0 rader (verifisert med sqlite3)

#### Tekniske Detaljer:
```python
# DETTE FUNGERER IKKE FOR PERSISTERING:
config = {
    'llm': {...},
    'embedder': {...},
    'vector_store': {
        'provider': 'qdrant',
        'config': {
            'collection_name': 'mem0_memories',
            'path': '/home/jovnna/aiki/shared_qdrant',  # Fil-basert = PROBLEM!
            'embedding_model_dims': 1536
        }
    }
}
m = Memory.from_config(config)
m.add('test', user_id='jovnna')  # Sier SUCCESS men persisterer IKKE
```

#### Verifisering:
```bash
# Qdrant database eksisterer:
$ ls shared_qdrant/collection/mem0_memories/
storage.sqlite  # 12KB fil

# Men er tom:
$ python3 -c "import sqlite3; conn = sqlite3.connect('...'); ..."
points: 0 rows  # INGEN DATA!
```

#### Tilleggsfunn:
- mem0 lagrer data i nøkkel `"data"` men søker etter nøkkel `"memory"` (inkonsistent)
- MCP-serveren bruker samme metode som ikke fungerer: `m.add([{'role': 'user', 'content': text}], user_id=...)`
- Qdrant-filen låses under kjøring (kan ikke åpnes av flere prosesser samtidig)

---

## MCP-SERVER KONFIGURASJON

### .mcp.json
```json
{
  "mcpServers": {
    "mem0": {
      "command": "uv",
      "args": [
        "--directory",
        "/home/jovnna/aiki/mcp-mem0",
        "run",
        "mcp-mem0"
      ],
      "env": {
        "TRANSPORT": "stdio"
      }
    }
  }
}
```

### mcp-mem0/.env
```env
TRANSPORT=stdio
LLM_PROVIDER=openrouter
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_API_KEY=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
LLM_CHOICE=openai/gpt-4o-mini
EMBEDDING_MODEL_CHOICE=text-embedding-3-small
QDRANT_PATH=/home/jovnna/aiki/shared_qdrant
```

### MCP-server Problem
FastMCP versjonsinkompatibilitet:
```
TypeError: FastMCP.__init__() got an unexpected keyword argument 'description'
```

---

## NESTE STEG / LØSNINGER

### Alternativer for å fikse persisterings-problemet:

1. **Bruk Qdrant Server (anbefalt)**
   ```bash
   docker run -p 6333:6333 -v $(pwd)/qdrant_storage:/qdrant/storage qdrant/qdrant
   ```
   - Endre config til: `url: 'http://localhost:6333'` istedenfor `path:`

2. **Bytt til PostgreSQL backend**
   - mem0 støtter også PostgreSQL som vector store
   - Krever PostgreSQL + pgvector extension

3. **Debug mem0's fil-baserte persistering**
   - Sjekk om det er en bug i mem0 1.0.0
   - Rapporter issue til mem0 GitHub
   - Vent på fix eller prøv annen versjon

4. **Bruk annen minneløsning**
   - LangChain Memory
   - ChromaDB
   - Custom JSON + embeddings

### Planlagte oppgaver (IKKE FULLFØRT):
- [ ] Restart Claude Code for å aktivere MCP-server
- [ ] Fikse persisterings-problemet
- [ ] Teste at minner faktisk lagres permanent
- [ ] Migrere eksisterende AIKI JSON-minne til mem0
- [ ] Integrere mem0graph for relasjonsminne
- [ ] Koble Open Interpreter til samme database
- [ ] Importere ChatGPT/Claude samtalehistorikk

---

## OVERORDNET MÅL

Oppnå **90%+ dekning av menneskelige hukommelsestyper** via multi-minne arkitektur:

### Planlagt System:
1. **mem0** - Semantic + Episodic memory
2. **mem0graph** - Relational + Associative memory
3. **Tredje system?** - Procedural + Skill memory

### Dagens Status:
- ⚠️ mem0 oppsett fullført, men persistering virker IKKE
- ⏸️ mem0graph ikke påbegynt
- ⏸️ Tredje system ikke valgt
- ✅ Eksisterende JSON-system fungerer (1,234 sesjoner dokumentert)

---

## VIKTIGE LÆRDOMMER

1. **Alltid verifiser persistering!**
   - Test at data overlever etter prosess-avslutning
   - Ikke stol på SUCCESS-meldinger alene

2. **Fil-basert Qdrant kan være problematisk**
   - Funker for dev/test, men kanskje ikke production
   - Server-modus er mer pålitelig

3. **mem0 er fortsatt ung (1.0.0)**
   - Kan ha bugs og inkompatibiliteter
   - Dokumentasjon kan være utdatert

4. **MCP-integrasjon krever kompatible versjoner**
   - FastMCP API endrer seg
   - coleam00/mcp-mem0 kan være utdatert

---

## FILER OPPRETTET/ENDRET I DAG

```
/home/jovnna/aiki/
├── .mcp.json                          # MCP-server konfigurasjon
├── mcp-mem0/                          # MCP-server installasjon
│   ├── .env                           # OpenRouter konfig
│   ├── src/main.py                    # Server kode (har bugs)
│   └── src/utils.py                   # mem0 client setup
├── shared_qdrant/                     # Delt database (TOM!)
│   ├── collection/mem0_memories/
│   │   └── storage.sqlite            # 0 rader
│   └── meta.json
├── memory_test/                       # Tidligere tester
│   └── .venv/
└── SESSION_2025-11-13_mem0_findings.md  # DENNE FILEN
```

---

## KONTAKT/REFERANSER

- mem0 docs: https://docs.mem0.ai/
- mem0 GitHub: https://github.com/mem0ai/mem0
- coleam00/mcp-mem0: https://github.com/coleam00/mcp-mem0
- Qdrant docs: https://qdrant.tech/documentation/
- OpenRouter: https://openrouter.ai/

---

**Lagret av:** Claude Code
**Grunn:** Backup utenfor mem0 siden persistering ikke fungerer
**Neste sesjon:** Start med å lese denne filen først!
