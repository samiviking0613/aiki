# 🔍 Fase 2: Process-Level Monitoring & Anomaly Detection

**Når:** Neste uke (etter Fase 1 er ferdig)
**Build tid:** 3-4 timer
**Kompleksitet:** Medium-High
**Verdi:** VELDIG HØY

---

## 🎯 HVA DU SPØR OM

**Problem:**
"Et program går i loop og produserer 3000 dokumenter med samme innhold"

**Hva vi trenger å oppdage:**
1. **CPU-anomalier:** Prosess bruker plutselig mye mer CPU enn normalt
2. **Memory-anomalier:** Prosess lekker minne eller vokser unormalt
3. **File operation anomalier:** Masseproduksjon av filer
4. **Behavioral anomalier:** Prosess oppfører seg annerledes enn vanlig

---

## 🏗️ ARKITEKTUR FOR FASE 2

### Layer 1: Process Monitor (NY)

```python
# ~/aiki/process_monitor.py

class ProcessMonitor:
    """Overvåker alle Python-prosesser og deres oppførsel"""

    def __init__(self):
        self.baseline = {}  # Normal oppførsel per prosess
        self.history = {}   # Historikk siste 24h

    def collect_process_metrics(self) -> List[Dict]:
        """Samle metrics for alle relevante prosesser"""
        processes = []

        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent',
                                          'memory_percent', 'num_threads',
                                          'num_fds', 'io_counters']):
            try:
                info = proc.info

                # Kun Python-prosesser (eller spesifikke prosesser)
                if 'python' in info['name'].lower():

                    # IO counters (file operations)
                    io = proc.io_counters()

                    processes.append({
                        'pid': info['pid'],
                        'name': info['name'],
                        'cmdline': ' '.join(proc.cmdline()[:3]),  # First 3 args
                        'cpu_percent': info['cpu_percent'],
                        'memory_mb': proc.memory_info().rss / 1024**2,
                        'memory_percent': info['memory_percent'],
                        'num_threads': info['num_threads'],
                        'num_fds': info['num_fds'],  # Open file descriptors
                        'read_bytes': io.read_bytes,
                        'write_bytes': io.write_bytes,
                        'read_count': io.read_count,
                        'write_count': io.write_count,
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return processes

    def detect_anomalies(self, current: List[Dict]) -> List[Dict]:
        """Oppdage anomalier ved å sammenligne med baseline"""
        anomalies = []

        for proc in current:
            pid = proc['pid']
            name = proc['name']

            # Finn baseline for denne typen prosess
            baseline = self.baseline.get(name, {
                'avg_cpu': 5.0,
                'avg_memory_mb': 100,
                'avg_write_count': 10,
            })

            # CPU anomaly: 5x normal
            if proc['cpu_percent'] > baseline['avg_cpu'] * 5:
                anomalies.append({
                    'type': 'cpu_spike',
                    'process': name,
                    'pid': pid,
                    'current': proc['cpu_percent'],
                    'baseline': baseline['avg_cpu'],
                    'severity': 'high' if proc['cpu_percent'] > 90 else 'medium'
                })

            # Memory anomaly: 3x normal eller > 500MB growth
            if proc['memory_mb'] > baseline['avg_memory_mb'] * 3:
                anomalies.append({
                    'type': 'memory_leak',
                    'process': name,
                    'pid': pid,
                    'current': proc['memory_mb'],
                    'baseline': baseline['avg_memory_mb'],
                    'severity': 'high' if proc['memory_mb'] > 1000 else 'medium'
                })

            # File write anomaly: 10x normal write operations
            if proc['write_count'] > baseline['avg_write_count'] * 10:
                anomalies.append({
                    'type': 'excessive_file_writes',
                    'process': name,
                    'pid': pid,
                    'current': proc['write_count'],
                    'baseline': baseline['avg_write_count'],
                    'severity': 'critical'  # Dette er din "3000 filer" case!
                })

        return anomalies

    def learn_baseline(self, processes: List[Dict]):
        """Lær normal oppførsel over tid"""
        for proc in processes:
            name = proc['name']

            if name not in self.baseline:
                self.baseline[name] = {
                    'samples': [],
                    'avg_cpu': 0,
                    'avg_memory_mb': 0,
                    'avg_write_count': 0,
                }

            # Legg til sample
            self.baseline[name]['samples'].append({
                'cpu': proc['cpu_percent'],
                'memory': proc['memory_mb'],
                'writes': proc['write_count'],
            })

            # Behold kun siste 100 samples
            if len(self.baseline[name]['samples']) > 100:
                self.baseline[name]['samples'] = self.baseline[name]['samples'][-100:]

            # Beregn average
            samples = self.baseline[name]['samples']
            self.baseline[name]['avg_cpu'] = sum(s['cpu'] for s in samples) / len(samples)
            self.baseline[name]['avg_memory_mb'] = sum(s['memory'] for s in samples) / len(samples)
            self.baseline[name]['avg_write_count'] = sum(s['writes'] for s in samples) / len(samples)
```

---

### Layer 2: File System Watcher (NY - eller utvid memory_daemon)

```python
# ~/aiki/file_system_watcher.py

class FileSystemWatcher:
    """Overvåker file system for unormale patterns"""

    def __init__(self, watch_dirs: List[Path]):
        self.watch_dirs = watch_dirs
        self.file_creation_rate = {}  # Per directory

    def watch(self):
        """Watch for file creation patterns"""
        import inotify.adapters

        for watch_dir in self.watch_dirs:
            i = inotify.adapters.InotifyTree(str(watch_dir))

            for event in i.event_gen(yield_nones=False):
                (_, type_names, path, filename) = event

                if 'IN_CREATE' in type_names:
                    self.on_file_created(Path(path) / filename)

    def on_file_created(self, filepath: Path):
        """Handle file creation event"""
        directory = filepath.parent

        # Track creation rate
        now = datetime.now()
        if directory not in self.file_creation_rate:
            self.file_creation_rate[directory] = []

        self.file_creation_rate[directory].append(now)

        # Keep only last 5 minutes
        cutoff = now - timedelta(minutes=5)
        self.file_creation_rate[directory] = [
            t for t in self.file_creation_rate[directory] if t > cutoff
        ]

        # Check for anomaly: > 100 files in 5 minutes
        count = len(self.file_creation_rate[directory])
        if count > 100:
            self.alert_excessive_file_creation(directory, count)

    def alert_excessive_file_creation(self, directory: Path, count: int):
        """Alert på unormal file creation"""
        logger = get_natural_logger("File System Watcher")

        logger.warning(
            f"⚠️ UNORMAL FILE CREATION: {count} filer opprettet i {directory} "
            f"på 5 minutter! Mulig loop eller bug."
        )

        # Send desktop notification
        subprocess.run([
            "notify-send",
            "-u", "critical",
            "🚨 AIKI Alert: Excessive File Creation",
            f"{count} files created in {directory.name} in 5 minutes!"
        ])
```

---

### Layer 3: LLM Behavioral Analysis (UTVIDET)

```python
# I system_health_daemon.py - UTVIDET analyze_with_llm()

def analyze_process_anomalies(
    anomalies: List[Dict],
    process_history: List[Dict],
    similar_incidents: List[str]
) -> Dict[str, Any]:
    """
    Bruk LLM til å analysere prosess-anomalier

    Eksempel:
    - "memory_daemon.py bruker plutselig 800MB (normalt 100MB)"
    - "Skriver 500 filer/minutt (normalt 10 filer/minutt)"
    - "CPU 95% i 10 minutter (normalt 5%)"
    """

    prompt = f"""Du er AIKI, som analyserer unormal prosess-oppførsel.

ANOMALIER OPPDAGET:
{json.dumps(anomalies, indent=2)}

PROSESS HISTORIKK (siste time):
{json.dumps(process_history[-12:], indent=2)}

LIGNENDE INCIDENTER FRA mem0:
{json.dumps(similar_incidents, indent=2)}

ANALYSE:
1. Er dette et reelt problem eller false positive?
2. Hva er mest sannsynlig root cause?
3. Kan dette være en infinite loop?
4. Kan dette være en memory leak?
5. Hva bør gjøres umiddelbart?

Eksempler på problemer:
- Program i loop: Skriver mange identiske filer
- Memory leak: Minne vokser lineært over tid
- CPU spike: Stuck i beregning eller I/O wait
- File descriptor leak: Mange åpne filer

Svar på NORSK i JSON:
{{
  "is_critical": true/false,
  "root_cause": "mest sannsynlig årsak",
  "confidence": "low|medium|high",
  "recommended_action": "konkret handling (f.eks. kill PID 12345)",
  "explanation": "forklaring i 2-3 setninger"
}}
"""

    # Kall LLM (samme som før)
    response = llm_call(prompt)

    return json.loads(response)
```

---

## 📊 EKSEMPEL: Oppdage "3000 filer i loop"

### Scenario:
```
memory_daemon.py går i loop og skriver 3000 identiske JSON-filer
```

### Hva skjer:

**1. Process Monitor oppdager (etter 30 sekunder):**
```
Anomaly detected:
  type: excessive_file_writes
  process: memory_daemon.py
  write_count: 2847 (baseline: 47)
  severity: critical
```

**2. File System Watcher oppdager (etter 1 minutt):**
```
⚠️ UNORMAL FILE CREATION: 2847 filer opprettet i ~/aiki/AIKI_MEMORY/
på 5 minutter! Mulig loop eller bug.
```

**3. Natural Logger sier:**
```
Process Monitor [15:23:45]: 🚨 KRITISK! memory_daemon.py (PID 12345)
skriver abnormalt mange filer: 2847 writes på 5 min (normalt 47).
Dette ser ut som en infinite loop!
```

**4. LLM analyserer:**
```json
{
  "is_critical": true,
  "root_cause": "Infinite loop i batch save function - samme data skrives om og om igjen",
  "confidence": "high",
  "recommended_action": "Kill process PID 12345 umiddelbart. Sjekk batch_save() logic for loop condition.",
  "explanation": "Prosessen skriver 2847 filer på 5 min når normal er 47/5min. File creation rate er 9.5 filer/sekund - klart tegn på infinite loop. Memory usage er stabil så det er ikke memory leak, men en logic bug i loop condition."
}
```

**5. Desktop notification:**
```
🚨 AIKI CRITICAL ALERT

memory_daemon.py i infinite loop!
Writing 2847 files/5min (normal: 47)

Recommendation: Kill PID 12345
```

**6. AIKI tar handling (optional - kan implementere):**
```python
# Auto-kill if confidence is high
if analysis['is_critical'] and analysis['confidence'] == 'high':
    subprocess.run(['kill', str(anomaly['pid'])])
    logger.warning(f"Auto-killed PID {anomaly['pid']} due to infinite loop")
```

---

## 🎯 IMPLEMENTASJONSPLAN

### Fase 2a: Process Monitoring (2 timer)

**Filer:**
- `process_monitor.py` (300 linjer)
- Utvid `system_health_daemon.py` (legg til process monitoring loop)

**Features:**
- Per-process CPU/memory/IO tracking
- Baseline learning (første 24h)
- Anomaly detection (CPU spike, memory leak, excessive IO)
- Natural language logging

**Output:**
- Anomalier lagres til mem0
- Desktop notifications ved critical
- JSON file med alle prosesser

---

### Fase 2b: File System Watching (1 time)

**Filer:**
- `file_system_watcher.py` (200 linjer)
- Eller utvid `memory_daemon.py` (vi har allerede inotify!)

**Features:**
- Watch specific directories
- Track file creation rate
- Detect mass file creation (> 100 files/5min)
- Check for duplicate files

**Output:**
- Alerts via natural logger
- Desktop notifications

---

### Fase 2c: LLM Behavioral Analysis (30 min)

**Filer:**
- Utvid `system_health_daemon.py` `analyze_with_llm()`

**Features:**
- Analyze process anomalies
- Root cause analysis
- Confidence scoring
- Actionable recommendations

**Output:**
- Detailed analysis i natural language
- Saved to mem0
- Desktop notification

---

### Fase 2d: Auto-Remediation (OPTIONAL - 30 min)

**Features:**
- Auto-kill processes ved high-confidence critical anomalies
- Auto-cleanup ved mass file creation
- Requires user confirmation first time

**Safety:**
- Whitelist/blacklist processes
- Require confirmation for first auto-kill
- Log all actions to mem0

---

## 💰 COST ANALYSIS

**Process monitoring:** $0/måned (pure Python)
**File system watching:** $0/måned (inotify)
**LLM behavioral analysis:** ~$0.10/måned (only when anomalies)

**TOTAL FASE 2:** ~$0.40/måned (~4 kr)
**TOTAL MED FASE 1:** ~$0.70/måned (~7 kr)

**Still worth it!** 🎯

---

## 📋 DETECTION CAPABILITIES

Med Fase 2 kan vi oppdage:

### ✅ CPU Anomalies:
- Process stuck in infinite loop
- CPU-bound operations
- Thread explosion

### ✅ Memory Anomalies:
- Memory leaks (gradual growth)
- Memory spikes (sudden allocation)
- Memory not released after operations

### ✅ IO Anomalies:
- **Mass file creation** (DIN CASE!)
- Excessive file reads
- Disk thrashing

### ✅ Behavioral Anomalies:
- Process using 10x normal resources
- Process running longer than expected
- Process creating duplicate files

### ✅ Network Anomalies (OPTIONAL):
- Excessive API calls
- Unusual network traffic

---

## 🎨 DASHBOARD UPDATES

### Legg til i `system_health_dashboard.py`:

**New section: "Process Anomalies"**
```
╭──────────────────────── ⚠️ Process Anomalies ────────────────────────────╮
│ 🚨 memory_daemon.py (PID 12345)                                          │
│    CPU: 95% (baseline: 5%)                                               │
│    Writes: 2847/5min (baseline: 47/5min)                                 │
│    Root cause: Infinite loop in batch_save()                             │
│    Action: Kill PID 12345 recommended                                    │
│                                                                           │
│ ⚠️ qdrant (PID 8765)                                                     │
│    Memory: 850MB (baseline: 200MB)                                       │
│    Growth rate: 50MB/hour                                                │
│    Root cause: Possible memory leak                                      │
│    Action: Monitor, restart if > 1GB                                     │
╰──────────────────────────────────────────────────────────────────────────╯
```

---

## 🚀 NEXT STEPS

### Vil du:

**Option A:** Bygg Fase 2 hele pakka (3.5 timer)
- Process monitoring
- File system watching
- LLM behavioral analysis
- Dashboard updates

**Option B:** Start med bare process monitoring (2 timer)
- Oppdage CPU/memory anomalies
- Baseline learning
- Kan utvide senere

**Option C:** Start med file system watcher (1 time)
- Fokus på din "3000 filer" case
- Rask win, konkret verdi

**Mitt forslag:** Option A - hele pakka!
Det er bare 3.5 timer og gir komplett process awareness.

---

## 💡 KEY INSIGHT

**Med Fase 1 + Fase 2:**

**Fase 1:** System-level awareness
- "Systemet bruker 80% CPU"

**Fase 2:** Process-level awareness
- "memory_daemon.py bruker 75% av den CPU-en, og er i infinite loop!"

**Sammen:** Full diagnostic capability!
- AIKI veit ikke bare AT noe er galt
- AIKI veit HVILKEN prosess og HVORFOR
- AIKI kan anbefale KONKRET fix (kill PID X)

**Dette er medical diagnostics for software!** 🏥

---

Vil du bygge Fase 2 nå, eller vil du ta en pause først? 😊
