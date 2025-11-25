# 🧠 AIKI Seamless Memory Architecture

**Dato:** 17. November 2025
**Mål:** ZERO friction memory system med full token tracking

---

## 🎯 Design Goals

1. **Zero Conversation Interruption** - Aldri stoppe for å lagre/søke
2. **Automatic Context Injection** - Triggerord henter context transparent
3. **Full Token Accountability** - Track hver API call, lær mønstre
4. **ADHD-Optimized** - Minimal cognitive load, maksimal automatisering

---

## 🏗️ System Components

### 1. Memory Daemon (Background Process)

**File:** `~/aiki/memory_daemon.py`

```python
"""
Continuous background process that:
- Watches file system for changes (inotify)
- Detects new/modified files in aiki-home/
- Extracts intelligent summaries
- Batch saves to mem0 every 5 minutes
- Zero blocking of Claude Code
"""

Features:
✅ inotify file system watcher
✅ Git diff integration
✅ Intelligent summary extraction
✅ Batch API calls (cost optimization)
✅ systemd service (auto-start on boot)
✅ Token tracking integration
```

**Run as:**
```bash
systemctl --user start aiki-memory-daemon
```

---

### 2. Triggerord Preprocessor (Auto Context Injection)

**File:** `~/.claude/hooks/message_preprocessor.py`

```python
"""
Pre-processes user messages BEFORE sending to Claude.
Detects trigger patterns and auto-injects relevant memories.

User sees: "Hva er AIKI-HOME?"
Claude gets:
  User: "Hva er AIKI-HOME?"
  [AUTO-INJECTED CONTEXT FROM MEM0]:
  - AIKI-HOME er network-level ADHD accountability system
  - MITM proxy intercepting all home traffic
  - 3 use cases: Kids+homework, Jovnna+morning, Adaptive filtering
"""

Trigger Patterns:
- "hva er X" → search_mem0(X)
- "fortsett med X" → search_mem0(X + "recent work")
- "sist vi jobbet" → search_mem0("last session")
- "forklare X" → search_mem0(X)
- "status på X" → search_mem0(X + "status progress")

Benefits:
✅ Transparent context injection
✅ No visible tool calls
✅ Instant context availability
✅ Zero user action required
```

---

### 3. Smart Auto-Save (On Session End)

**File:** `~/aiki/auto_save.py` (UPGRADED)

```python
"""
Enhanced session end hook:

OLD VERSION:
- Just copied old data + updated timestamp
- No detection of actual work done

NEW VERSION:
1. Git diff to detect all changes
2. File analysis (new files, modifications, deletions)
3. Intelligent summary generation via LLM
4. Auto-save comprehensive summary to mem0
5. Token tracking for the save operation
"""

On SessionEnd:
1. Run: git diff --name-status
2. For each changed file:
   - Extract key changes
   - Summarize purpose
3. Generate session summary
4. Save to mem0: full context of session
5. Log tokens used for this operation

Result:
✅ Next session starts with FULL context
✅ No manual work required
✅ Never forget what was done
```

---

### 4. Token Tracker System (Full Telemetry)

**Files:**
- `~/aiki/token_tracker.py` - Core tracking
- `~/aiki/token_dashboard.py` - View stats
- `~/aiki/data/tokens.db` - SQLite storage

```python
"""
Comprehensive token usage tracking for ALL operations:

Tracked Metrics:
- Model used (gpt-4o-mini, claude-sonnet-4-5, etc)
- Operation type (mem0_search, mem0_save, chat, code_gen)
- Tokens: input + output
- Cost: calculated in real-time
- Latency: time to complete
- Success/failure status
- Context: what triggered the call

Storage: SQLite + mem0
- SQLite for fast queries and dashboards
- mem0 for learning insights

Dashboard:
- Daily/weekly/monthly costs
- Cost per operation type
- Most expensive queries
- Optimization opportunities
- Learning insights
"""

Example Entry:
{
  "timestamp": "2025-11-17T20:15:00",
  "operation": "mem0_search",
  "model": "gpt-4o-mini",
  "query": "AIKI-HOME",
  "tokens_in": 523,
  "tokens_out": 187,
  "cost_usd": 0.000190,
  "latency_ms": 847,
  "success": true,
  "triggered_by": "user_message"
}

Learning Insights:
- "mem0_search costs average $0.0002"
- "batch saves reduce cost by 60%"
- "most expensive: code generation ($0.015 avg)"
- "token usage spike at 19:00-21:00 (hyperfocus)"
```

---

## 🔄 Complete Flow Diagram

```
┌─────────────────────────────────────────────────┐
│             USER SENDS MESSAGE                  │
│         "Hva er AIKI-HOME?"                     │
└────────────────┬────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────┐
│      TRIGGERORD PREPROCESSOR (Hook)             │
│  - Detects: "hva er AIKI-HOME"                  │
│  - Triggers: search_mem0("AIKI-HOME")           │
│  - Injects context into message                 │
│  - Tracks tokens used                           │
└────────────────┬────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────┐
│         CLAUDE PROCESSES MESSAGE                │
│  (With auto-injected context, seamless!)        │
│  - Responds with full AIKI-HOME knowledge       │
│  - No visible mem0 tool calls                   │
│  - User sees natural conversation               │
└────────────────┬────────────────────────────────┘
                 │
                 │ (Meanwhile, in background...)
                 │
┌─────────────────────────────────────────────────┐
│         MEMORY DAEMON (Always Running)          │
│  - Detects: test_input_monitor.py created      │
│  - Extracts: "Built input activity monitor"    │
│  - Queues for batch save                        │
│  - After 5 min: batch save to mem0              │
│  - Logs tokens used to tracker                  │
└─────────────────────────────────────────────────┘

                 ↓ (On session end)

┌─────────────────────────────────────────────────┐
│         SMART AUTO-SAVE (SessionEnd)            │
│  - git diff shows all changes                   │
│  - LLM generates intelligent summary            │
│  - Saves to mem0 automatically                  │
│  - Token usage tracked                          │
└────────────────┬────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────┐
│           TOKEN TRACKER DATABASE                │
│  - All operations logged                        │
│  - Real-time cost tracking                      │
│  - Learning insights generated                  │
│  - Dashboard accessible anytime                 │
└─────────────────────────────────────────────────┘
```

---

## 📊 Token Tracker Dashboard

**Command:** `python ~/aiki/token_dashboard.py`

```
╔════════════════════════════════════════════════════════════╗
║           🧠 AIKI TOKEN USAGE DASHBOARD                    ║
║                  17. November 2025                         ║
╠════════════════════════════════════════════════════════════╣
║  DAILY SUMMARY                                             ║
║  ─────────────────────────────────────────────────────     ║
║  Total Tokens:          47,523  (in) + 12,847 (out)       ║
║  Total Cost:            $0.0215  (~2.15 kr)               ║
║  Total API Calls:       127                                ║
║  Avg Latency:           634ms                              ║
╠════════════════════════════════════════════════════════════╣
║  BREAKDOWN BY OPERATION                                    ║
║  ─────────────────────────────────────────────────────     ║
║  mem0_search:           42 calls  |  $0.0084  (39%)       ║
║  mem0_save:             18 calls  |  $0.0063  (29%)       ║
║  code_generation:        8 calls  |  $0.0052  (24%)       ║
║  chat_response:         59 calls  |  $0.0016  ( 8%)       ║
╠════════════════════════════════════════════════════════════╣
║  TOP 5 MOST EXPENSIVE QUERIES                              ║
║  ─────────────────────────────────────────────────────     ║
║  1. Build input monitor       $0.0031  (1247 tokens)      ║
║  2. Fix auto_save.py          $0.0028  (1089 tokens)      ║
║  3. Design architecture       $0.0024  (967 tokens)       ║
║  4. Search: AIKI-HOME         $0.0002  (523 tokens)       ║
║  5. Search: input monitor     $0.0002  (498 tokens)       ║
╠════════════════════════════════════════════════════════════╣
║  LEARNING INSIGHTS                                         ║
║  ─────────────────────────────────────────────────────     ║
║  💡 Batch saves could save 60% on mem0 operations         ║
║  💡 Hyperfocus detected 19:00-20:30 (3x token usage)      ║
║  💡 Most productive: Code generation (ROI: 10x)           ║
║  ⚠️  15 failed API calls (network timeout)                ║
╠════════════════════════════════════════════════════════════╣
║  MONTHLY PROJECTION                                        ║
║  ─────────────────────────────────────────────────────     ║
║  Current pace:          $0.65/month  (~6.50 kr)           ║
║  With optimizations:    $0.35/month  (~3.50 kr) [-46%]    ║
╚════════════════════════════════════════════════════════════╝
```

---

## 🚀 Implementation Order

### Phase 1: Token Tracker (Foundation)
**Time:** 30 min

1. Create `token_tracker.py`
2. Create SQLite schema
3. Add wrapper functions for API calls
4. Test basic logging

**Why first?** Need tracking BEFORE building other components

---

### Phase 2: Smart Auto-Save
**Time:** 45 min

1. Upgrade `auto_save.py`
2. Add git diff detection
3. Integrate LLM summary generation
4. Add mem0 auto-save
5. Integrate token tracking

**Why second?** Prevents future memory loss immediately

---

### Phase 3: Memory Daemon
**Time:** 60 min

1. Create `memory_daemon.py`
2. Implement inotify file watcher
3. Add intelligent file analysis
4. Batch save logic
5. systemd service file
6. Token tracking integration

**Why third?** Enables background automation

---

### Phase 4: Triggerord Preprocessor
**Time:** 45 min

1. Create message preprocessor hook
2. Define trigger patterns
3. Implement auto-search logic
4. Context injection mechanism
5. Token tracking

**Why last?** Most advanced feature, builds on others

---

## 💎 Expected Benefits

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Memory loss incidents | 1-2/day | 0 | 100% |
| Time to context | 5-10 sec | 0 sec | Instant |
| Manual save actions | 10+/session | 0 | 100% |
| Token cost visibility | 0% | 100% | Full transparency |
| ADHD flow disruption | High | None | 🚀 |
| Cost optimization | Blind | Data-driven | Intelligent |

---

## 📝 File Structure

```
~/aiki/
├── memory_daemon.py           # Background file watcher
├── token_tracker.py           # Core tracking system
├── token_dashboard.py         # View stats
├── auto_save.py              # Smart session end (UPGRADED)
├── auto_resume.py            # Session start (existing)
├── data/
│   ├── tokens.db            # SQLite token database
│   └── daemon.log           # Daemon logs
└── .claude/
    └── hooks/
        └── message_preprocessor.py  # Triggerord system
```

---

## ✅ Success Criteria

1. **Zero Manual Memory Operations**
   - No more `mcp__mem0__save_memory` calls
   - No more `mcp__mem0__search_memories` (triggered auto)

2. **Full Token Transparency**
   - Every API call logged
   - Real-time cost tracking
   - Learning insights generated

3. **Seamless Context**
   - User says "Hva er X?" → Claude knows instantly
   - No visible tool calls
   - Natural conversation flow

4. **ADHD-Proof**
   - Zero cognitive load
   - No interruptions
   - Automatic everything

---

## 🔧 Technical Stack

| Component | Technology |
|-----------|------------|
| File watching | `inotify` (Linux kernel) |
| Background process | Python `asyncio` + systemd |
| Token storage | SQLite |
| Memory storage | mem0 + Qdrant |
| Cost calculation | Real-time based on model pricing |
| Dashboard | Rich CLI (Python `rich` library) |
| Hooks | Claude Code custom hooks |
| LLM | OpenRouter (gpt-4o-mini for efficiency) |

---

## 🎯 Next Steps

Ready to build? Start with Phase 1 (Token Tracker) in 30 minutes.

**Command to start:**
```bash
cd ~/aiki
# I'll build token_tracker.py first
```

---

**Made with 🧠 by AIKI**
**Architecture designed for ADHD heaven**
