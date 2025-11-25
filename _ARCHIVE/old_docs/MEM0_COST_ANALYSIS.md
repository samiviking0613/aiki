# 💰 mem0 Token Cost Analysis

**Dato:** 17. November 2025

## 📊 OpenRouter Pricing (2025)

### Current Setup:
- **LLM:** `openai/gpt-4o-mini`
- **Embedding:** `text-embedding-3-small`
- **Vector DB:** Qdrant (local, gratis)

### Costs:

| Component | Input | Output |
|-----------|-------|--------|
| GPT-4o-mini | $0.15 / 1M tokens | $0.60 / 1M tokens |
| text-embedding-3-small | $0.02 / 1M tokens | $0 (no output) |

**Conversion:**
- GPT-4o-mini: $0.00015/1k input, $0.00060/1k output
- Embeddings: $0.00002/1k tokens

---

## 🔍 Actual Costs per Operation

### 1. Memory Search (`mcp__mem0__search_memories`)

**What happens:**
1. Your query gets embedded (~50-100 tokens)
2. Qdrant vector search (local, free)
3. LLM extracts relevant memories (~500 tokens input + 200 output)

**Cost per search:**
```
Embedding: 100 tokens × $0.00002/1k = $0.000002
LLM input: 500 tokens × $0.00015/1k = $0.000075
LLM output: 200 tokens × $0.00060/1k = $0.000120
----------------------------------------
TOTAL: ~$0.0002 per search (~0.02 øre)
```

### 2. Memory Save (`mcp__mem0__save_memory`)

**What happens:**
1. Content gets embedded (~500-1000 tokens)
2. LLM extracts/processes memory (~1000 input + 300 output)
3. Qdrant stores vector (local, free)

**Cost per save:**
```
Embedding: 1000 tokens × $0.00002/1k = $0.00002
LLM input: 1000 tokens × $0.00015/1k = $0.00015
LLM output: 300 tokens × $0.00060/1k = $0.00018
----------------------------------------
TOTAL: ~$0.00035 per save (~0.035 øre)
```

### 3. Get All Memories (`mcp__mem0__get_all_memories`)

**What happens:**
1. Direct database fetch (Qdrant local, free)
2. Optional LLM formatting (~500 input + 200 output)

**Cost:**
```
LLM input: 500 tokens × $0.00015/1k = $0.000075
LLM output: 200 tokens × $0.00060/1k = $0.000120
----------------------------------------
TOTAL: ~$0.0002 per get_all (~0.02 øre)
```

---

## 📈 Monthly Estimates

**Scenario: Active AIKI usage**

| Activity | Operations/day | Cost/op | Daily | Monthly |
|----------|----------------|---------|-------|---------|
| Search memories | 50 | $0.0002 | $0.01 | $0.30 |
| Save memories | 20 | $0.00035 | $0.007 | $0.21 |
| Get all | 5 | $0.0002 | $0.001 | $0.03 |
| **TOTAL** | | | **$0.018** | **$0.54** |

**~5.50 kr/måned** (~54 øre/dag)

---

## 🎯 Optimalisering

### Problem med current flow:
- ❌ Claude Code må STOPPE og VENTE på mem0 operasjoner
- ❌ Hver search/save blokkerer conversation flow
- ❌ Context switches distraherer (ADHD problem!)

### Løsning: Bakgrunnsprosess + Triggerord

#### 1. **Background Memory Daemon**
```python
# ~/aiki/memory_daemon.py
# Kjører i bakgrunnen, lytter på file changes
# Auto-lagrer til mem0 uten å blokkere Claude Code
```

**Benefits:**
- ✅ Zero interruption til conversation
- ✅ Auto-save på file changes
- ✅ Async processing (ikke blokkerende)
- ✅ Batch operations (billigere!)

#### 2. **Triggerord for Auto-Search**

**Konsept:** Claude Code detekterer keywords og søker mem0 automatisk

**Eksempler:**
- User: "Hva er AIKI-HOME?" → Auto-search: "AIKI-HOME"
- User: "Fortsett med input monitor" → Auto-search: "input monitor"
- User: "Sist vi jobbet med..." → Auto-search: "last session"

**Implementation:**
```python
# I Claude Code hook (pre-prompt processing)
TRIGGER_PATTERNS = {
    r"hva er (\w+)": lambda m: f"search: {m.group(1)}",
    r"fortsett med (\w+)": lambda m: f"search: {m.group(1)}",
    r"sist vi jobbet": lambda: "search: last session recent work"
}

# Auto-inject search results into context
# Claude sees results WITHOUT explicit tool call
```

#### 3. **Batch Embeddings**

**Current:** Each save = 1 embedding call
**Better:** Batch multiple saves

```python
# Instead of:
save("memory 1")  # $0.00035
save("memory 2")  # $0.00035
save("memory 3")  # $0.00035

# Do:
batch_save(["memory 1", "memory 2", "memory 3"])  # $0.00040
# 60% kostnad reduksjon!
```

---

## 🚀 Proposed Architecture

```
┌─────────────────────────────────────────┐
│         Claude Code Session             │
│  (No mem0 blocking - seamless flow!)    │
└─────────────────┬───────────────────────┘
                  │
                  │ File changes detected
                  ↓
┌─────────────────────────────────────────┐
│       Memory Daemon (background)        │
│  - Watch file system (inotify)          │
│  - Detect new/changed files             │
│  - Extract summaries                    │
│  - Batch save to mem0                   │
└─────────────────┬───────────────────────┘
                  │
                  │ Async writes
                  ↓
┌─────────────────────────────────────────┐
│              mem0 + Qdrant              │
│  - Embeddings generated in batch        │
│  - Stored locally (instant access)      │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│      Triggerord Preprocessor            │
│  - Scan user messages for keywords      │
│  - Auto-inject relevant memories        │
│  - Zero user action required            │
└─────────────────────────────────────────┘
```

---

## 💎 Implementation Plan

### Phase 1: Background Daemon (2-3 timer)
1. `memory_daemon.py` - watch aiki-home/ for changes
2. Auto-extract summaries from modified files
3. Batch save to mem0 every 5 minutes
4. systemd service for auto-start

### Phase 2: Triggerord System (1-2 timer)
1. Add pre-processing hook to Claude Code
2. Pattern matching for common queries
3. Auto-inject search results into context
4. Transparent to user (no tool calls visible)

### Phase 3: Cost Optimization (1 time)
1. Batch embedding calls
2. Cache frequent searches (Redis?)
3. Use cheaper models for simple extractions

---

## 📉 Expected Savings

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Conversation interruptions | 10-20/session | 0 | 100% |
| Time to context | 5-10 sec | 0 sec | Instant |
| Token cost | $0.54/month | $0.30/month | 45% savings |
| ADHD-friendliness | 3/10 | 10/10 | 🚀 |

---

## ✅ Conclusion

**Current cost: Neglisjerbar (~5 kr/måned)**

**Real problem: IKKE kostnad, men FLOW!**
- Stopping to save/search breaks ADHD flow
- Manual operations create friction
- Context switches hurt productivity

**Solution: Background automation**
- Memory daemon handles saves automatically
- Triggerord system injects context seamlessly
- Zero user action = zero friction = ADHD heaven

**Next step:** Build memory daemon + triggerord preprocessor

---

**Made with 🧠 by AIKI**
