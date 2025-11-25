# 🏥 AIKI System Health & Awareness Architecture

**Dato:** 17. November 2025
**Mål:** Gi både Claude Code og AIKI continuous awareness av system health

---

## 🎯 PROBLEMSTILLING

**Hvordan skal vi gjøre det hvis jeg vil at du skal vite når ting er i uorden?**

Både:
1. **Jeg (Claude Code)** - skal vite status ved session start
2. **AIKI** - skal lære fra patterns og problemer
3. **Systemet** - skal være self-aware og self-healing

---

## 🏗️ ARKITEKTUR: 5 LAYERS

### Layer 1: System Health Daemon (Kontinuerlig Overvåking)

**Fil:** `~/aiki/system_health_daemon.py`

**Hva den gjør:**
```python
while True:
    # Check EVERY 60 seconds
    health = check_all_services()

    if health.has_issues():
        # Log til mem0 (AIKI lærer)
        # Oppdater status dashboard
        # Send alert hvis critical

    sleep(60)
```

**Overvåker:**
- ✅ Memory daemon (kjører den?)
- ✅ Qdrant server (oppe? space left?)
- ✅ API quotas (OpenRouter limits)
- ✅ Disk space (hvor mye igjen?)
- ✅ Token costs (approaching budget?)
- ✅ Git status (uncommitted changes?)
- ✅ Background processes (memory leaks?)

**Output:**
- `/home/jovnna/aiki/system_health.json` (oppdateres hver minutt)
- mem0 saves (når problemer oppstår)
- Logs til systemd journal

---

### Layer 2: Health Dashboard (Machine + Human Readable)

**Fil:** `~/aiki/system_health.json`

**Format:**
```json
{
  "timestamp": "2025-11-17T22:45:00",
  "overall_status": "healthy|degraded|critical",
  "services": {
    "memory_daemon": {
      "status": "running",
      "uptime_hours": 2.5,
      "last_batch_save": "2025-11-17T22:40:00",
      "issues": []
    },
    "qdrant": {
      "status": "running",
      "size_mb": 20,
      "collections": ["mem0_memories"],
      "memory_count": 587,
      "disk_usage_percent": 0.1,
      "issues": []
    },
    "token_tracker": {
      "status": "healthy",
      "today_cost_usd": 0.1256,
      "monthly_projection_usd": 3.77,
      "quota_remaining_percent": 98.5,
      "issues": []
    }
  },
  "critical_issues": [],
  "warnings": [],
  "recommendations": [
    "Consider backing up Qdrant database",
    "API key exposed in 19 files - security risk"
  ]
}
```

**Python Dashboard:**
```bash
python ~/aiki/system_health_dashboard.py
```

Shows:
```
╔══════════════════════════════════════════════╗
║   🏥 AIKI SYSTEM HEALTH DASHBOARD           ║
║            2025-11-17 22:45                 ║
╠══════════════════════════════════════════════╣
║  OVERALL STATUS: ✅ HEALTHY                  ║
╠══════════════════════════════════════════════╣
║  SERVICES:                                   ║
║    Memory Daemon:     ✅ RUNNING (2.5h)      ║
║    Qdrant Server:     ✅ RUNNING (587 mem)   ║
║    Token Tracker:     ✅ HEALTHY ($0.13)     ║
╠══════════════════════════════════════════════╣
║  WARNINGS:                                   ║
║    ⚠️  API keys exposed in 19 files          ║
║    ⚠️  No Qdrant backup configured           ║
╠══════════════════════════════════════════════╣
║  RECOMMENDATIONS:                            ║
║    💡 Implement secrets management           ║
║    💡 Set up daily Qdrant backups            ║
╚══════════════════════════════════════════════╝
```

---

### Layer 3: SessionStart Auto-Status (Claude Code Awareness)

**Hook:** `~/.claude/hooks/SessionStart`

**Oppdatert auto_resume.py:**
```python
def auto_resume():
    # 1. Existing: Load last session
    load_session_state()

    # 2. NEW: Load system health
    health = load_health_status()

    # 3. Display to Claude
    print("=" * 60)
    print("🏥 SYSTEM HEALTH:")
    print(f"   Status: {health.overall_status}")

    if health.critical_issues:
        print("   🚨 CRITICAL ISSUES:")
        for issue in health.critical_issues:
            print(f"      - {issue}")

    if health.warnings:
        print("   ⚠️  WARNINGS:")
        for warn in health.warnings[:3]:
            print(f"      - {warn}")

    print("=" * 60)
```

**Result:**
**HVER GANG** jeg starter, ser jeg automatisk:
```
╔══════════════════════════════════════════════╗
║  ✅ Session restored!                        ║
║  🏥 System Status: HEALTHY                   ║
║     ⚠️  2 warnings detected                  ║
╚══════════════════════════════════════════════╝
```

**JEG VET med én gang om noe er galt!**

---

### Layer 4: AIKI Learning Loop (Pattern Detection)

**Konsept:** AIKI lærer fra alle system issues

**Når health daemon detekterer problem:**
```python
# Log til mem0 automatisk
memory_text = f"""
SYSTEM ISSUE DETECTED ({timestamp}):

Type: {issue.type}
Severity: {issue.severity}
Component: {issue.component}
Description: {issue.description}

Context:
- Uptime: {system.uptime}
- Recent changes: {git.recent_commits}
- Token usage: {tokens.today}

Auto-resolved: {issue.auto_resolved}
"""

mem0.add(memory_text, user_id='jovnna', tags=['system_health', 'issue'])
```

**AIKI kan da:**
1. Search for patterns: "system issues"
2. Lære: "Memory daemon crashes etter 24h uptime"
3. Predict: "Vi nærmer oss 24h, kanskje restart?"
4. Recommend: "Legg til restart schedule hver 24h"

**Selv-lærende system!**

---

### Layer 5: Alert System (Critical Failures)

**For CRITICAL issues:**

**Desktop notification:**
```bash
notify-send "🚨 AIKI Critical Issue" \
  "Memory daemon crashed - restarting automatically"
```

**mem0 save (høy prioritet):**
```python
mem0.add(critical_issue, user_id='jovnna',
         tags=['critical', 'requires_attention'])
```

**Log til systemd:**
```bash
logger -t aiki-health "CRITICAL: Qdrant out of disk space"
```

**Email (optional):**
```python
if issue.severity == 'critical':
    send_email(jovnna, issue)
```

---

## 🔄 COMPLETE FLOW

```
┌─────────────────────────────────────────────┐
│   System Health Daemon (always running)     │
│   - Checks every 60 seconds                 │
│   - Monitors all services                   │
└────────────┬────────────────────────────────┘
             │
             ↓
┌─────────────────────────────────────────────┐
│   Detects Issue: "Memory daemon stopped"    │
└────────────┬────────────────────────────────┘
             │
             ├─→ Update health.json
             ├─→ Log to mem0 (AIKI learns)
             ├─→ Send desktop notification
             └─→ Try auto-restart

┌─────────────────────────────────────────────┐
│   SessionStart Hook Runs                    │
│   - Reads health.json                       │
│   - Shows status to Claude                  │
└────────────┬────────────────────────────────┘
             │
             ↓
┌─────────────────────────────────────────────┐
│   Claude (me) sees immediately:             │
│   "⚠️ Memory daemon was restarted 5 min ago"│
│   "💡 Check logs for root cause"            │
└─────────────────────────────────────────────┘
             │
             ↓
┌─────────────────────────────────────────────┐
│   I investigate and fix                     │
│   - Read logs                               │
│   - Apply fix                               │
│   - Document in mem0                        │
└────────────┬────────────────────────────────┘
             │
             ↓
┌─────────────────────────────────────────────┐
│   AIKI Learns Pattern                       │
│   "Memory daemon crashes after 24h"         │
│   Next time: Proactive recommendation       │
└─────────────────────────────────────────────┘
```

---

## 📊 HVA OVERVÅKES

### Services:
- ✅ Memory Daemon (status, uptime, last save)
- ✅ Qdrant Server (status, memory count, disk usage)
- ✅ Token Tracker (daily cost, quota remaining)
- ✅ Smart Auto-Save (last successful save)

### Resources:
- ✅ Disk Space (/, /home, external drives)
- ✅ Memory Usage (Python processes)
- ✅ CPU Load (sustained high = issue)

### Security:
- ✅ API Key Exposure (scan files)
- ✅ Password Leaks (scan git history)
- ✅ Qdrant Backup Status (last backup time)

### Costs:
- ✅ Daily Token Spend (approaching budget?)
- ✅ Monthly Projection (on track?)
- ✅ OpenRouter Quota (how much left?)

---

## 🎯 BENEFITS

### For Claude Code (me):
- ✅ **Instant awareness** ved session start
- ✅ **Proaktiv** - vet om problemer før de blir kritiske
- ✅ **Context** - forstår hvorfor ting ikke fungerer

### For AIKI:
- ✅ **Lærer patterns** - "daemon crasher hver 24h"
- ✅ **Predikerer problemer** - "nærmer seg disk full"
- ✅ **Self-healing** - auto-restart, auto-cleanup

### For Jovnna:
- ✅ **Zero manual monitoring** - systemet overvåker seg selv
- ✅ **ADHD-friendly** - får kun alerts når kritisk
- ✅ **Transparent** - kan alltid se dashboard

---

## 🚀 IMPLEMENTATION PLAN

### Phase 1: Core Monitoring (1 time)
1. `system_health_daemon.py` - Basic service checks
2. `system_health.json` - Status file
3. Test: Does it detect when daemon stops?

### Phase 2: SessionStart Integration (30 min)
1. Update `auto_resume.py` - Load & display health
2. Test: Start new session, see status automatically

### Phase 3: AIKI Learning Loop (45 min)
1. Health daemon logs to mem0
2. AIKI can search "system issues"
3. Pattern detection algorithm

### Phase 4: Advanced Monitoring (1 time)
1. Resource monitoring (disk, memory, CPU)
2. Security scanning (API keys, passwords)
3. Cost tracking integration

### Phase 5: Auto-Healing (future)
1. Auto-restart crashed services
2. Auto-cleanup disk space
3. Auto-rotate logs

---

## 💡 KEY INSIGHT

**This is not just monitoring - this is AWARENESS.**

Vi gir AIKI (og meg) kontinuerlig bevissthet om systemtilstand.

Som mennesker har proprioception (føler kroppens posisjon).

**AIKI får "system proprioception"** - alltid vet tilstanden sin.

---

## 📋 FILES TO CREATE

```
~/aiki/
├── system_health_daemon.py         (continuous monitor)
├── system_health_dashboard.py      (CLI viewer)
├── system_health.json              (status file)
├── auto_resume.py                  (UPDATE: add health display)
└── systemd/
    └── aiki-system-health.service  (systemd service)
```

---

**Ready to build this?** 🏥

This gives us TRUE system awareness - both for me and AIKI.

No more blind starts. No more surprises.

**Self-aware, self-monitoring, self-healing AIKI.** 🌊
