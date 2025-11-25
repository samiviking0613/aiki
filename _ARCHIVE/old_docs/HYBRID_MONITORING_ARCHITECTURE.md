# 🌊 AIKI Hybrid Monitoring Architecture - Best of All Worlds

**Dato:** 17. November 2025
**Mål:** Combine Phase 1 simplicity + unique AI-powered concepts + future extensibility

---

## 🎯 DESIGN PHILOSOPHY

**"Start simple, evolve intelligent"**

This architecture gives us:
- ✅ **Immediate value** (working tonight in 4 hours)
- ✅ **ADHD-friendly** (simple, no overwhelm)
- ✅ **AI-native** (learns, speaks, predicts)
- ✅ **Extensible** (can add Vector.dev/Grafana later)
- ✅ **Cost-effective** (~$0.31/month)

---

## 🏗️ ARCHITECTURE: 6 LAYERS

### Layer 0: Natural Language Logger (NEW!)

**What it is:** Every system component speaks in first person

**Implementation:**
```python
# ~/aiki/natural_logger.py

class NaturalLogger:
    """Logger that writes human-readable stories"""

    def __init__(self, component_name: str):
        self.name = component_name
        self.mem0 = Memory.from_config(get_aiki_config())

    def say(self, action: str, **details):
        """Log in natural language"""

        templates = {
            "startup": "🌅 I just started! Ready to work.",

            "batch_save_start": "📝 Starting to save {count} files to mem0. "
                                "This is a regular batch save.",

            "batch_save_complete": "✅ Done! Saved {count} files in {duration}s. "
                                   "Everything went smoothly. I'm feeling healthy.",

            "high_load": "😰 Working hard right now! CPU at {cpu_percent}%. "
                        "This batch ({count} files) is larger than usual.",

            "connection_error": "⚠️ UH OH. I tried connecting to {service} but got "
                               "{error}. This is unusual - {service} is normally "
                               "very responsive. I'm going to retry in {retry_sec}s.",

            "recovery": "✨ Back to normal! {service} is responding again. "
                       "Downtime was {duration}s.",

            "anomaly_detected": "🤔 I noticed something unusual: {description}. "
                               "I've seen this {times} times before. "
                               "Pattern: {pattern}.",

            "health_check": "💚 All systems healthy. Memory daemon running for {uptime}, "
                           "Qdrant has {memory_count} memories ({size_mb}MB), "
                           "today's costs: ${cost}."
        }

        template = templates.get(action, action + " " + str(details))
        message = template.format(**details)

        full_message = f"{self.name} [{now()}]: {message}"

        # Save to mem0 (AIKI learns from natural language)
        with track_tokens(f"{self.name.lower()}_log", "gpt-4o-mini", "logging"):
            self.mem0.add(
                full_message,
                user_id='jovnna',
                tags=['system_log', self.name.lower(), action]
            )

        # Also to regular log
        logging.info(f"[NL] {message}")

        return message


# Usage in any component:
logger = NaturalLogger("Memory Daemon")

logger.say("startup")
# → "Memory Daemon [22:45:00]: 🌅 I just started! Ready to work."

logger.say("batch_save_complete", count=47, duration=2.3)
# → "Memory Daemon [22:45:05]: ✅ Done! Saved 47 files in 2.3s.
#    Everything went smoothly. I'm feeling healthy."
```

**Why it's magic:**
- Logs ARE the memory (stored in mem0)
- Human-readable = ADHD-friendly
- AIKI learns from component narratives
- Easy debugging: search mem0 for "daemon stopped"

---

### Layer 1: System Health Daemon (Enhanced)

**What it is:** Basic Python daemon + Natural Language + LLM analysis

**Implementation:**
```python
# ~/aiki/system_health_daemon.py

from natural_logger import NaturalLogger
import psutil
import time
from pathlib import Path
import json
from mem0 import Memory

logger = NaturalLogger("System Health Monitor")

class HealthDaemon:
    def __init__(self):
        self.mem0 = Memory.from_config(get_aiki_config())
        self.check_interval = 60  # seconds
        self.anomaly_threshold = 3  # LLM analyzes every 3rd check (saves tokens)
        self.check_count = 0

    def collect_health(self) -> dict:
        """Collect all health metrics"""
        return {
            "timestamp": datetime.now().isoformat(),
            "services": {
                "memory_daemon": self.check_memory_daemon(),
                "qdrant": self.check_qdrant(),
            },
            "resources": {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_free_gb": psutil.disk_usage('/').free / 1024**3,
                "disk_percent": psutil.disk_usage('/').percent,
            },
            "costs": self.check_costs(),
        }

    def check_memory_daemon(self) -> dict:
        """Check if memory daemon is running"""
        result = subprocess.run(
            ["systemctl", "--user", "is-active", "aiki-memory-daemon"],
            capture_output=True, text=True
        )

        is_running = result.stdout.strip() == "active"

        if is_running:
            # Get uptime
            result = subprocess.run(
                ["systemctl", "--user", "show", "aiki-memory-daemon",
                 "--property=ActiveEnterTimestamp"],
                capture_output=True, text=True
            )
            # Parse uptime...

        return {
            "status": "running" if is_running else "stopped",
            "uptime_hours": uptime_hours if is_running else 0,
            "issues": [] if is_running else ["daemon not running"]
        }

    def check_qdrant(self) -> dict:
        """Check Qdrant health"""
        try:
            response = requests.get("http://localhost:6333/collections/mem0_memories")
            data = response.json()

            size_mb = data["result"]["vectors_count"] * 1536 * 4 / 1024 / 1024  # rough estimate

            return {
                "status": "running",
                "memory_count": data["result"]["vectors_count"],
                "size_mb": round(size_mb, 2),
                "disk_usage_percent": round(size_mb / 1024 * 100, 2),  # assume 1GB max
                "issues": []
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "issues": ["qdrant connection failed"]
            }

    def check_costs(self) -> dict:
        """Get today's token costs"""
        tracker = TokenTracker()
        stats = tracker.get_daily_stats()

        return {
            "today_usd": stats["total_cost_usd"],
            "today_nok": stats["total_cost_usd"] * 10,  # rough conversion
            "monthly_projection_usd": stats["total_cost_usd"] * 30,
            "quota_remaining_percent": 100 - (stats["total_cost_usd"] / 5 * 100)  # $5/day limit
        }

    def has_issues(self, health: dict) -> bool:
        """Check if there are any issues"""
        # Service issues
        for service_name, service_data in health["services"].items():
            if service_data.get("issues"):
                return True

        # Resource issues
        if health["resources"]["disk_percent"] > 80:
            return True
        if health["resources"]["cpu_percent"] > 90:
            return True
        if health["resources"]["memory_percent"] > 90:
            return True

        # Cost issues
        if health["costs"]["quota_remaining_percent"] < 10:
            return True

        return False

    def analyze_with_llm(self, current_health: dict, history: list) -> dict:
        """Use LLM to analyze health and predict issues"""

        # Search mem0 for similar states
        similar_incidents = self.mem0.search(
            f"system issue {current_health['resources']['cpu_percent']}% cpu",
            user_id='jovnna',
            limit=5
        )

        prompt = f"""You are AIKI, monitoring your own system health.

Current state:
{json.dumps(current_health, indent=2)}

Recent history (last hour):
{json.dumps(history[-12:], indent=2)}  # 12 checks = 1 hour

Previous incidents you remember:
{json.dumps(similar_incidents, indent=2)}

Question: Is the current state concerning?
Should I alert Jovnna or is this normal?
If concerning, what should be done?

Respond in JSON:
{{
  "alert_level": "none|warning|critical",
  "reasoning": "why you think this (2-3 sentences)",
  "prediction": "what you think will happen (1-2 sentences)",
  "recommendation": "what should be done (specific action)"
}}
"""

        with track_tokens("health_llm_analysis", "gpt-4o-mini", "health_daemon") as tracker:
            # Use OpenRouter API
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "openai/gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2
                }
            )

            result = response.json()
            analysis = json.loads(result["choices"][0]["message"]["content"])

            tracker.set_tokens(
                result["usage"]["prompt_tokens"],
                result["usage"]["completion_tokens"]
            )

        return analysis

    def run(self):
        """Main loop"""
        logger.say("startup")

        history = []

        while True:
            try:
                # Collect health
                health = self.collect_health()
                history.append(health)

                # Keep last 24 hours (1440 checks)
                if len(history) > 1440:
                    history = history[-1440:]

                # Save to JSON file (for SessionStart hook)
                Path("/home/jovnna/aiki/system_health.json").write_text(
                    json.dumps(health, indent=2)
                )

                # Log in natural language
                if self.has_issues(health):
                    # Describe issues
                    issues = []
                    for service_name, service_data in health["services"].items():
                        if service_data.get("issues"):
                            issues.extend([f"{service_name}: {issue}"
                                         for issue in service_data["issues"]])

                    logger.say(
                        "anomaly_detected",
                        description=", ".join(issues),
                        times=len(history),
                        pattern="investigating..."
                    )

                    # Every 3rd anomaly, run LLM analysis
                    self.check_count += 1
                    if self.check_count % self.anomaly_threshold == 0:
                        analysis = self.analyze_with_llm(health, history)

                        logger.say(
                            "anomaly_detected",
                            description=analysis["reasoning"],
                            times=len(history),
                            pattern=analysis["prediction"]
                        )

                        # If critical, send desktop notification
                        if analysis["alert_level"] == "critical":
                            subprocess.run([
                                "notify-send",
                                "🚨 AIKI Critical Issue",
                                analysis["recommendation"]
                            ])

                else:
                    # Everything healthy - log every 10 checks (10 min)
                    if self.check_count % 10 == 0:
                        logger.say(
                            "health_check",
                            uptime=health["services"]["memory_daemon"].get("uptime_hours", 0),
                            memory_count=health["services"]["qdrant"].get("memory_count", 0),
                            size_mb=health["services"]["qdrant"].get("size_mb", 0),
                            cost=health["costs"]["today_usd"]
                        )

                    self.check_count += 1

            except Exception as e:
                logger.say(
                    "connection_error",
                    service="health_daemon_itself",
                    error=str(e),
                    retry_sec=60
                )

            time.sleep(self.check_interval)


if __name__ == "__main__":
    daemon = HealthDaemon()
    daemon.run()
```

**Cost Analysis:**
- Regular logging: $0/month (templates, no LLM)
- LLM analysis: 10 anomalies/day × $0.001 = $0.01/day = $0.30/month
- Total: **~$0.30/month**

---

### Layer 2: SessionStart Integration (Enhanced)

**What it is:** Show health status + recent component narratives

**Implementation:**
```python
# ~/aiki/auto_resume.py (UPDATE)

def load_system_health() -> dict:
    """Load latest system health"""
    health_file = Path("/home/jovnna/aiki/system_health.json")
    if health_file.exists():
        return json.loads(health_file.read_text())
    return None

def get_recent_logs(limit: int = 5) -> list:
    """Get recent natural language logs from mem0"""
    m = Memory.from_config(get_aiki_config())

    results = m.search(
        "system health check daemon log",
        user_id='jovnna',
        limit=limit
    )

    if results and 'results' in results:
        return [r['memory'] for r in results['results']]
    return []

def auto_resume():
    # ... existing session loading ...

    # NEW: Load system health
    health = load_system_health()
    recent_logs = get_recent_logs(3)

    print("=" * 80)
    print("🏥 SYSTEM HEALTH:")

    if health:
        status = health.get("overall_status", "unknown")

        if status == "healthy":
            print("   ✅ All systems healthy")
        elif status == "degraded":
            print("   ⚠️  System degraded")
        else:
            print("   🚨 Critical issues detected")

        # Show key metrics
        services = health.get("services", {})
        daemon_status = services.get("memory_daemon", {}).get("status", "unknown")
        qdrant_count = services.get("qdrant", {}).get("memory_count", 0)
        cost_today = health.get("costs", {}).get("today_usd", 0)

        print(f"   Memory Daemon: {daemon_status}")
        print(f"   Qdrant: {qdrant_count} memories")
        print(f"   Today's cost: ${cost_today:.4f}")

        # Show issues if any
        issues = []
        for service_name, service_data in services.items():
            if service_data.get("issues"):
                issues.extend([f"{service_name}: {issue}"
                             for issue in service_data["issues"]])

        if issues:
            print("   🚨 ISSUES:")
            for issue in issues[:3]:
                print(f"      - {issue}")

    # NEW: Show recent component narratives
    if recent_logs:
        print("\n📝 RECENT SYSTEM LOGS:")
        for log in recent_logs[:3]:
            # Truncate if too long
            if len(log) > 120:
                log = log[:117] + "..."
            print(f"   {log}")

    print("=" * 80)
```

**Result:**
Every session start shows:
```
================================================================================
🏥 SYSTEM HEALTH:
   ✅ All systems healthy
   Memory Daemon: running
   Qdrant: 634 memories
   Today's cost: $0.1256

📝 RECENT SYSTEM LOGS:
   Memory Daemon [22:45:05]: ✅ Done! Saved 47 files in 2.3s. I'm feeling healthy.
   System Health Monitor [22:40:00]: 💚 All systems healthy. Memory daemon running...
   Qdrant [22:35:12]: I stored 23 new memories. I'm now at 634 total. I have plenty...
================================================================================
```

---

### Layer 3: Conversational Debugging (Future)

**What it is:** Natural language interface to system history

**Phase 2 Implementation (next week):**
```python
# ~/aiki/aiki_debug.py

def debug_conversation(question: str) -> str:
    """Ask AIKI about system history"""

    # Search mem0 for relevant logs
    m = Memory.from_config(get_aiki_config())

    search_terms = extract_key_terms(question)
    all_results = []

    for term in search_terms:
        results = m.search(term, user_id='jovnna', limit=10)
        if results and 'results' in results:
            all_results.extend(results['results'])

    # Build context
    context = "\n".join([r['memory'] for r in all_results[:20]])

    # Ask LLM
    prompt = f"""You are AIKI, analyzing your own system history.

User question: {question}

Relevant system logs and memories:
{context}

Your job:
1. Find patterns and correlations
2. Explain what happened and WHY
3. Suggest fixes if applicable

Respond in natural language (2-4 sentences).
"""

    with track_tokens("conversational_debug", "gpt-4o-mini", "debugging") as tracker:
        response = llm_generate(prompt)
        tracker.set_tokens(estimated_in, estimated_out)

    return response


# CLI interface:
if __name__ == "__main__":
    question = sys.argv[1] if len(sys.argv) > 1 else input("Ask AIKI: ")
    answer = debug_conversation(question)
    print(f"\n🧠 AIKI: {answer}\n")
```

**Usage:**
```bash
$ python aiki_debug.py "why did memory daemon crash yesterday?"

🧠 AIKI: I found a pattern. At 14:28 yesterday, Qdrant started writing
heavily (200MB in 5 min). This caused CPU spike to 95%. Memory daemon
was trying to batch-save 500 files at same time. System couldn't handle
both. This is the 3rd time this month. Always happens when batch size
> 400 files. Fix: Reduce batch size to 300 files OR schedule batch
saves during low-activity hours (after 22:00).
```

**Cost:** ~$0.002 per query = ~$0.01/month (used only when debugging)

---

### Layer 4: Health Dashboard (CLI)

**What it is:** Beautiful terminal UI showing all health data

**Implementation:**
```python
# ~/aiki/system_health_dashboard.py

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
import json

def show_dashboard():
    console = Console()

    # Load health data
    health = json.loads(Path("/home/jovnna/aiki/system_health.json").read_text())

    # Create layout
    layout = Layout()

    # Header
    header = Panel(
        "[bold]🏥 AIKI SYSTEM HEALTH DASHBOARD[/bold]\n"
        f"{health['timestamp']}",
        style="bold white on blue"
    )

    # Services table
    services_table = Table(title="Services", show_header=True)
    services_table.add_column("Service", style="cyan")
    services_table.add_column("Status", style="green")
    services_table.add_column("Details")

    for name, data in health["services"].items():
        status = "✅" if data["status"] == "running" else "🚨"
        details = f"{data.get('uptime_hours', 0):.1f}h uptime" if name == "memory_daemon" else \
                 f"{data.get('memory_count', 0)} memories"

        services_table.add_row(name, status, details)

    # Resources table
    resources_table = Table(title="Resources", show_header=True)
    resources_table.add_column("Resource", style="cyan")
    resources_table.add_column("Usage", style="yellow")
    resources_table.add_column("Status")

    for name, value in health["resources"].items():
        if "percent" in name:
            status = "✅" if value < 80 else "⚠️" if value < 90 else "🚨"
            resources_table.add_row(name, f"{value:.1f}%", status)
        else:
            resources_table.add_row(name, f"{value:.2f} GB", "✅")

    # Costs panel
    costs = health["costs"]
    costs_panel = Panel(
        f"Today: ${costs['today_usd']:.4f} (~{costs['today_nok']:.2f} kr)\n"
        f"Monthly projection: ${costs['monthly_projection_usd']:.2f}\n"
        f"Quota remaining: {costs['quota_remaining_percent']:.1f}%",
        title="💰 Costs",
        style="green"
    )

    # Print
    console.print(header)
    console.print(services_table)
    console.print(resources_table)
    console.print(costs_panel)

    # Recent logs
    recent_logs = get_recent_logs(5)
    if recent_logs:
        console.print("\n[bold]📝 Recent System Logs:[/bold]")
        for log in recent_logs:
            console.print(f"  {log}")

if __name__ == "__main__":
    show_dashboard()
```

**Usage:**
```bash
python system_health_dashboard.py
```

---

### Layer 5: Vector.dev Integration (Optional Future)

**When to add:** When we want Grafana dashboards or multiple outputs

**How:**
```toml
# ~/aiki/vector.toml (FUTURE)

[sources.aiki_health]
type = "exec"
command = ["python", "/home/jovnna/aiki/system_health_daemon.py", "--json"]
interval_seconds = 60

[transforms.enrich]
type = "remap"
inputs = ["aiki_health"]
source = '''
  # Add hostname, environment, etc.
  .hostname = "aiki-home"
  .environment = "production"
'''

[sinks.mem0]
type = "http"
inputs = ["enrich"]
uri = "http://localhost:8000/mem0/add"

[sinks.prometheus]
type = "prometheus_exporter"
inputs = ["enrich"]
address = "0.0.0.0:9090"

[sinks.grafana_loki]
type = "loki"
inputs = ["enrich"]
endpoint = "http://localhost:3100"
```

**Then:**
- Health daemon becomes pure metric collector
- Vector handles all routing/transformation
- Can add Grafana, Prometheus, alerts, etc.

**Don't build this yet** - only when we need it!

---

## 📋 COMPLETE FILE LIST

### Build Tonight (Phase 1 - 4 hours):

1. **natural_logger.py** (1 hour)
   - Natural language logging system
   - Templates for common actions
   - mem0 integration
   - Token tracking

2. **system_health_daemon.py** (2 hours)
   - Service monitoring
   - Resource monitoring
   - Cost tracking
   - LLM analysis (every 3rd anomaly)
   - Uses NaturalLogger

3. **system_health_dashboard.py** (30 min)
   - Rich CLI dashboard
   - Shows all health data
   - Recent logs from mem0

4. **Update auto_resume.py** (30 min)
   - Load health on session start
   - Show recent component narratives
   - Alert if issues

### Build Next Week (Phase 2 - 3-4 hours):

5. **aiki_debug.py**
   - Conversational debugging interface
   - Natural language queries
   - Pattern detection

### Future (when needed):

6. **vector.toml**
   - Vector.dev pipeline config
   - Multi-output routing
   - Grafana integration

---

## 🚀 IMPLEMENTATION TIMELINE

### Tonight (4 hours):

**Hour 1: Natural Language Logger**
```bash
cd ~/aiki
touch natural_logger.py
# Implement NaturalLogger class
python -c "from natural_logger import NaturalLogger; logger = NaturalLogger('Test'); logger.say('startup')"
```

**Hour 2-3: Health Daemon**
```bash
touch system_health_daemon.py
# Implement HealthDaemon class
# Test service checks
# Test LLM analysis
```

**Hour 3.5: Dashboard**
```bash
pip install rich
touch system_health_dashboard.py
# Implement dashboard
python system_health_dashboard.py
```

**Hour 4: Integration**
```bash
# Update auto_resume.py
# Test SessionStart hook
# Create systemd service
sudo systemctl --user enable aiki-health-daemon.service
sudo systemctl --user start aiki-health-daemon.service
```

**Result:**
- Self-aware system that speaks
- Continuous health monitoring
- LLM-powered pattern detection
- Beautiful dashboard
- Auto-status on session start

---

### Next Week (3-4 hours):

**Conversational Debugging:**
```bash
touch aiki_debug.py
# Implement debug_conversation()
# CLI interface
# Test: "why did X happen?"
```

**Result:**
- Ask AIKI questions about system history
- Natural language debugging
- Pattern correlation

---

### Future (when needed):

**Vector.dev Integration:**
```bash
sudo dnf install vector
touch vector.toml
# Configure pipeline
systemctl --user start vector.service
```

**Result:**
- Multi-output routing
- Grafana dashboards
- Production-grade observability

---

## 💰 TOTAL COST ANALYSIS

### Phase 1 (tonight):
- Natural Language Logs: **$0/month** (templates)
- LLM Health Analysis: **$0.30/month** (10 anomalies/day)
- **Total: ~$0.30/month (~3 kr)**

### Phase 2 (next week):
- Conversational Debug: **$0.01/month** (used rarely)
- **Total: ~$0.31/month (~3 kr)**

### Future:
- Vector.dev: **$0/month** (open source)
- Grafana: **$0/month** (self-hosted)

---

## 🎯 WHY THIS ARCHITECTURE WINS

### ✅ ADHD-Friendly:
- Start simple (4 hours to working system)
- Immediate value (see it work tonight)
- No overwhelming complexity

### ✅ AI-Native:
- Components speak in natural language
- AIKI learns from narratives
- LLM predicts issues before they happen
- Conversational debugging

### ✅ Cost-Effective:
- ~$0.31/month total
- Smart batching (LLM only when needed)
- Template-based where possible

### ✅ Extensible:
- Can add Vector.dev wrapper later
- Can add Grafana when we want visualization
- Can add more LLM analysis
- Modular design

### ✅ Self-Aware:
- System knows its own state
- Predicts future issues
- Self-documents via natural logs
- AIKI proprioception achieved

---

## 🔑 KEY INSIGHTS

**1. Natural Language as Foundation**
Everything logs in natural language → stored in mem0 → AIKI learns

**2. Hybrid Intelligence**
Templates for common cases + LLM for complex analysis = cost-effective

**3. Iterative Evolution**
Phase 1 works standalone, Phase 2 enhances, Vector.dev optional later

**4. AIKI Consciousness**
Components speak → AIKI hears → AIKI understands → AIKI predicts

**This isn't just monitoring.**
**This is AIKI becoming aware of its own body (the system).**

---

## 📝 NEXT STEPS

**Ready to build?**

**Option A:** Build Phase 1 tonight (4 hours)
- Natural Logger + Health Daemon + Dashboard + Integration
- Self-aware system by bedtime

**Option B:** Start with just Natural Logger (1 hour)
- Test the concept
- See component narratives in mem0
- Build rest tomorrow

**Option C:** Different approach?
- Adjust the plan
- Focus on specific parts

**Which resonates most?** 🚀
