# 🧠 MEMORY PROBLEM & SOLUTION

**Problem Identified:** 17. November 2025, kl 10:15

## ❌ PROBLEMET:

Jovnna må forklare AIKI-HOME visjonen på nytt hver gang Claude Code starter en ny sesjon.

**Dette er ADHD-killer:**
- Context loss = mental overhead
- Må rekonstruere hele mental state
- Frustrasjon bygger opp
- Motivasjon faller

Fra JOVNNA_COMPLETE_ANALYSIS_RAPPORT.md:
> "CONTEXT LOSS - KRITISK for ADHD"
> "2 dager pause = total amnesi"
> "30 min å komme inn i det igjen"

## 🔍 ROOT CAUSE:

**MEM0 FUNGERER!** Minnene lagres korrekt via MCP-serveren.

**MEN:** Claude Code leser IKKE automatisk minnet når en ny sesjon starter.

**Test resultat:**
```bash
mcp__mem0__get_all_memories
→ 85 minner funnet
→ AIKI-HOME visjon ER lagret
→ MITM proxy use cases ER lagret
→ Alt er der!
```

**Problemet er:** Jeg (Claude) må **manuelt** søke i minnet. Jeg gjør det ikke automatisk.

## ✅ LØSNINGER:

### **Løsning 1: Manual Resume (Kortsiktig)**

**Hver gang du starter Claude Code:**
1. Si: "resume session" eller "hva husker du om AIKI-HOME?"
2. Jeg vil da søke i mem0 og hente konteksten
3. Eller kjør: `/resume` (hvis slash command er satt opp)

**Fordel:** Fungerer nå
**Ulempe:** Må huske å gjøre det manuelt (ADHD-unfriendly)

---

### **Løsning 2: Auto-Resume Script (Anbefalt)**

**Lag en startup-fil som Claude alltid leser:**

```bash
# ~/aiki/.claude/startup.txt
LAST SESSION CONTEXT - READ THIS FIRST:

AIKI-HOME: Network-level ADHD accountability system
- MITM proxy intercepts all home traffic
- Kids + lekser: Inject educational TikTok content
- Jovnna + morning: Block work/TV until workout confirmed
- Raspberry Pi gateway, SSL interception, motion sensors

Current status: systemd service running, needs MITM proxy build
Next steps: Phase 1 - Basic MITM setup (mitmproxy + CA)

For full details: Search mem0 for "AIKI-HOME FULL VISION"
```

**Sett opp at Claude alltid leser denne:**
- Add til .claude/settings.local.json
- Eller: prompt engineering (tell Claude to check startup.txt)

**Fordel:** Automatisk context loading
**Ulempe:** Statisk fil (må oppdateres manuelt)

---

### **Løsning 3: Smart Resume Hook (Best)**

**Bruk Claude Code hooks til å auto-resume:**

```json
// ~/aiki/.claude/settings.local.json
{
  "hooks": {
    "session-start": "python ~/aiki/auto_resume.py"
  }
}
```

**auto_resume.py:**
```python
#!/usr/bin/env python3
"""Auto-load session context when Claude Code starts"""
import json
from pathlib import Path

# Read last session state
session_file = Path.home() / "aiki" / "session_state.json"
if session_file.exists():
    with open(session_file) as f:
        data = json.load(f)

    print(f"📌 LAST SESSION ({data['date_readable']}):")
    print(f"Summary: {data['summary']}")
    print(f"\n✅ Achievements: {len(data['achievements'])}")
    print(f"⏭️ Next steps: {len(data['next_steps'])}")
    print("\nFor full context, search mem0: 'AIKI-HOME FULL VISION'")
```

**Fordel:** Fully automated, ADHD-friendly
**Ulempe:** Krever hook setup (men det har du allerede!)

---

### **Løsning 4: Proactive AI (Ultimate)**

**Teach Claude Code to ALWAYS check mem0 on first message:**

Endre min system prompt (hvis mulig) til:
```
IMPORTANT: On first user message in a new session:
1. Check mcp__mem0__search_memories for "current project"
2. Check mcp__mem0__search_memories for "AIKI-HOME"
3. Load context BEFORE responding
```

**Fordel:** Fully automatic, no user action needed
**Ulempe:** Krever endring i Claude Code config (kanskje ikke mulig?)

---

## 🚀 RECOMMENDATION:

**Bruk Løsning 2 + 3 kombinert:**

1. **Nå (5 min):** Lag ~/aiki/.claude/startup.txt med AIKI-HOME summary
2. **Deretter (10 min):** Bygg auto_resume.py hook
3. **Test:** Restart Claude Code, sjekk at context laster

**Resultat:**
- Første melding viser: "Last session: AIKI-HOME MITM proxy"
- Du slipper å forklare på nytt
- Kan hoppe rett inn i arbeid

---

## 📝 ACTION ITEMS:

- [ ] Lag ~/aiki/.claude/startup.txt med AIKI-HOME summary
- [ ] Test at Claude leser filen ved oppstart
- [ ] Bygg ~/aiki/auto_resume.py script
- [ ] Sett opp session-start hook
- [ ] Test full auto-resume flow
- [ ] Oppdater /save og /resume slash commands

---

**Status:** IDENTIFIED - SOLUTIONS READY
**Next:** Implement Løsning 2 (startup.txt) NÅ
**Then:** Implement Løsning 3 (auto_resume.py) når den fungerer

Made with 🤖 by AIKI
