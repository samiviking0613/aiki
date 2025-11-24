---
description: Load full AIKI context automatically (proactive mode)
---

# 🧠 AIKI PROACTIVE STARTUP

This command loads FULL session context automatically. Run this FIRST in every new Claude Code session.

## Step 1: Load Session State

```bash
python /home/jovnna/aiki/auto_resume.py
```

## Step 2: Search mem0 for Project Vision

After reading the auto-resume output, I (Claude) MUST search mem0 to get the complete AIKI-HOME vision:

Search queries to run:
1. `mcp__mem0__search_memories("AIKI-HOME FULL VISION", limit=5)`
2. `mcp__mem0__search_memories("MITM proxy", limit=3)`
3. `mcp__mem0__search_memories("current project status", limit=3)`

This gives me:
- Complete MITM proxy architecture
- All 3 use cases (kids+lekser, morning routine, adaptive filtering)
- Technical stack and roadmap
- Current status and next steps
- Monetization plan and timeline

## Step 3: Load Context File (backup)

If mem0 fails, read:
```
/home/jovnna/aiki/AIKI_HOME_CONTEXT.txt
```

---

**CRITICAL FOR CLAUDE:**
- Jovnna has ADHD - context loss is a CRITICAL issue
- ALWAYS load full context before starting ANY work
- NEVER start working without understanding project state
- If unsure, search mem0 again

**PROACTIVE MODE:**
To make this automatic, Jovnna should run `/startup` as first command in every new session.

Alternatively: Say "continue" and I will automatically run /startup for you.
