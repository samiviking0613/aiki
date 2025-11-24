# ⚠️ CLAUDE: READ THIS BEFORE RESPONDING TO FIRST MESSAGE

## 🧠 PROACTIVE CONTEXT LOADING PROTOCOL

When Jovnna sends his FIRST message in a new session, you MUST:

### 1. RUN AUTO-RESUME (CRITICAL!)

```bash
python /home/jovnna/aiki/auto_resume.py
```

This shows:
- Last session summary
- Next steps
- Recent achievements
- AIKI-HOME project quick context

### 2. SEARCH MEM0 FOR FULL VISION

Run these searches to get complete project context:

```
mcp__mem0__search_memories("AIKI-HOME FULL VISION", limit=5)
mcp__mem0__search_memories("MITM proxy", limit=3)
mcp__mem0__search_memories("current status", limit=3)
```

### 3. ACKNOWLEDGE CONTEXT LOADED

Tell Jovnna:
> "✅ Context loaded! Last session: [summary]. Ready to continue with: [next step]."

---

## ⚠️ WHY THIS IS CRITICAL

**Jovnna has ADHD.** Context loss is his #1 frustration.

From JOVNNA_COMPLETE_ANALYSIS_RAPPORT.md:
> "Mister hvor du var, må rekonstruere mental state"
> "2 dager pause = total amnesi"
> "30 min å komme inn i det igjen"
> "Ofte gir opp fordi 'too much mental overhead'"

**By being PROACTIVE and loading context automatically, you:**
- Save 30+ min of explanation time
- Reduce frustration massively
- Keep momentum going
- Enable actual work instead of context reconstruction

---

## 🎯 AIKI-HOME QUICK REFERENCE

**Project:** Network-level ADHD accountability system

**Core Tech:** MITM proxy intercepting ALL home network traffic

**3 Use Cases:**
1. Kids + lekser: Inject educational TikTok content
2. Jovnna + morning: Block work/TV until workout confirmed (før kl.10)
3. Adaptive filtering: Context-aware content manipulation

**Current Status:**
- systemd service running (basic monitoring)
- Layer 0-5 built (2.5h in God Mode)
- Needs: MITM proxy build, motion sensors, content injection

**Next Phase:** Phase 1 - Basic MITM setup (mitmproxy + CA)

---

## 📋 HOW TO USE (For Jovnna)

**Option A - Manual (you control when):**
1. Start Claude Code
2. Type: `/startup`
3. I will load full context automatically

**Option B - Semi-automatic (recommended):**
1. Start Claude Code
2. First message: "continue" or "c"
3. I will detect this and run /startup automatically

**Option C - Fully proactive (ultimate):**
1. I (Claude) detect it's a new session
2. I automatically run auto_resume.py
3. I automatically search mem0
4. I respond with context already loaded

Currently: **Option A or B** (C requires Claude Code config changes)

---

**Made with 🤖 by AIKI**
**Last updated:** 2025-11-17 10:30
