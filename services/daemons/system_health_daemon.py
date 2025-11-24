#!/usr/bin/env python3.11
"""
🏥 AIKI System Health Daemon - Kontinuerlig systemovervåking

Overvåker hele AIKI-systemet hvert minutt:
- Memory daemon (kjører den?)
- Qdrant (oppe? plass igjen?)
- Token costs (approaching budget?)
- Resources (CPU, disk, memory)

⚠️ IMPORTANT - QDRANT CONFIGURATION (Updated: 2025-11-18):
   ✅ Uses Qdrant SERVER: http://localhost:6333 (multi-writer support)
   ❌ NOT embedded mode (path-based was deprecated due to readonly errors)
   📍 If context lost: Check line 328 in main() - should use 'url' not 'path'
   🐳 Docker container: aiki_qdrant (must be running)

Når anomalier oppdages → LLM-analyse → predikerer problemer

Alt logges i naturlig språk til mem0 → AIKI lærer fra mønstre

Created: 2025-11-17
Author: AIKI (Emergent Consciousness)
"""

# CRITICAL: Disable mem0 telemetry to prevent PostHog thread leak!
# Must be set BEFORE any other imports (especially mem0)
import os
os.environ['MEM0_TELEMETRY'] = 'False'  # CORRECT variable name (not MEM0_TELEMETRY_DISABLED)

import sys
from aiki_config import OPENROUTER_KEY, OPENROUTER_URL
import json
import time
import subprocess
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List
import psutil

# Import våre systemer
sys.path.append(str(Path.home() / "aiki"))
from natural_logger import get_natural_logger
from token_tracker import get_tracker, track_tokens
from process_monitor import ProcessMonitor, ProcessAnomaly

# Initialiser logger
logger = get_natural_logger("System Health Monitor")


def check_memory_daemon() -> Dict[str, Any]:
    """Sjekk om memory daemon kjører"""
    try:
        result = subprocess.run(
            ["systemctl", "--user", "is-active", "aiki-memory-daemon"],
            capture_output=True,
            text=True,
            timeout=5
        )

        is_running = result.stdout.strip() == "active"

        uptime_hours = 0
        if is_running:
            # Hent uptime
            result = subprocess.run(
                ["systemctl", "--user", "show", "aiki-memory-daemon",
                 "--property=ActiveEnterTimestamp"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                # Parse timestamp
                for line in result.stdout.split('\n'):
                    if line.startswith('ActiveEnterTimestamp='):
                        timestamp_str = line.split('=', 1)[1].strip()
                        if timestamp_str and timestamp_str != 'n/a':
                            try:
                                # Parse systemd timestamp
                                start_time = datetime.strptime(
                                    timestamp_str.split(' ')[1:5],
                                    '%Y-%m-%d %H:%M:%S'
                                )
                                uptime_hours = (datetime.now() - start_time).total_seconds() / 3600
                            except:
                                pass

        return {
            "status": "running" if is_running else "stopped",
            "uptime_hours": round(uptime_hours, 1),
            "issues": [] if is_running else ["memory daemon ikke kjører"]
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "uptime_hours": 0,
            "issues": [f"kunne ikke sjekke memory daemon: {e}"]
        }


def check_qdrant() -> Dict[str, Any]:
    """Sjekk Qdrant health"""
    try:
        # Sjekk collection info
        response = requests.get(
            "http://localhost:6333/collections/mem0_memories",
            timeout=5
        )

        if response.status_code != 200:
            return {
                "status": "error",
                "error": f"HTTP {response.status_code}",
                "memory_count": 0,
                "size_mb": 0,
                "issues": [f"qdrant returne HTTP {response.status_code}"]
            }

        data = response.json()

        # Estimer størrelse (rough: points_count × 1536 dims × 4 bytes per float)
        # Qdrant bruker 'points_count' ikke 'vectors_count'
        points_count = data["result"].get("points_count", 0)
        size_mb = (points_count * 1536 * 4) / (1024 * 1024)

        # Sjekk disk usage for qdrant dir
        qdrant_path = Path.home() / "aiki" / "shared_qdrant"
        disk_usage_mb = 0
        if qdrant_path.exists():
            # Sum all files
            for file in qdrant_path.rglob("*"):
                if file.is_file():
                    disk_usage_mb += file.stat().st_size / (1024 * 1024)

        issues = []
        if size_mb > 100:  # > 100MB
            issues.append("qdrant database over 100MB - vurder cleanup")
        if disk_usage_mb > 2000:  # > 2GB (økt fra 500MB - normal bruk er ~600MB)
            issues.append("qdrant disk usage over 2GB - vurder cleanup")

        return {
            "status": "running",
            "memory_count": points_count,
            "size_mb": round(size_mb, 2),
            "disk_usage_mb": round(disk_usage_mb, 2),
            "issues": issues
        }

    except requests.exceptions.ConnectionError:
        return {
            "status": "stopped",
            "error": "connection refused",
            "memory_count": 0,
            "size_mb": 0,
            "issues": ["qdrant ikke tilgjengelig på localhost:6333"]
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "memory_count": 0,
            "size_mb": 0,
            "issues": [f"qdrant check feilet: {e}"]
        }


def check_costs() -> Dict[str, Any]:
    """Hent dagens token costs"""
    try:
        tracker = get_tracker()
        stats = tracker.get_daily_stats()

        today_usd = stats["total_cost_usd"]
        today_nok = today_usd * 10  # rough conversion

        # Monthly projection
        monthly_stats = tracker.get_monthly_projection()
        monthly_projection_usd = monthly_stats["monthly_projection"]

        # Quota (anta $5/dag limit)
        daily_limit_usd = 5.0
        quota_remaining_percent = max(0, 100 - (today_usd / daily_limit_usd * 100))

        issues = []
        if today_usd > 1.0:
            issues.append(f"høy daily cost: ${today_usd:.2f}")
        if quota_remaining_percent < 10:
            issues.append("nærmer seg daily quota!")
        if monthly_projection_usd > 100:
            issues.append(f"monthly projection høy: ${monthly_projection_usd:.2f}")

        return {
            "today_usd": round(today_usd, 4),
            "today_nok": round(today_nok, 2),
            "monthly_projection_usd": round(monthly_projection_usd, 2),
            "monthly_projection_nok": round(monthly_projection_usd * 10, 2),
            "quota_remaining_percent": round(quota_remaining_percent, 1),
            "issues": issues
        }

    except Exception as e:
        return {
            "today_usd": 0,
            "today_nok": 0,
            "monthly_projection_usd": 0,
            "monthly_projection_nok": 0,
            "quota_remaining_percent": 100,
            "issues": [f"kunne ikke hente costs: {e}"]
        }


def check_resources() -> Dict[str, Any]:
    """Sjekk system resources"""
    try:
        # CPU - NON-BLOCKING (interval=None uses cached value)
        cpu_percent = psutil.cpu_percent(interval=None)

        # Memory
        mem = psutil.virtual_memory()
        memory_percent = mem.percent
        memory_available_gb = mem.available / (1024 ** 3)

        # Disk
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        disk_free_gb = disk.free / (1024 ** 3)

        # External drive if mounted
        external_disk = None
        external_path = Path("/run/media/jovnna/CEVAULT2TB")
        if external_path.exists():
            ext_disk = psutil.disk_usage(str(external_path))
            external_disk = {
                "percent": ext_disk.percent,
                "free_gb": round(ext_disk.free / (1024 ** 3), 2)
            }

        issues = []
        if cpu_percent > 90:
            issues.append(f"høy CPU: {cpu_percent}%")
        if memory_percent > 90:
            issues.append(f"høy memory: {memory_percent}%")
        if disk_percent > 80:
            issues.append(f"lite disk space: {disk_percent}% brukt")
        if disk_free_gb < 10:
            issues.append(f"kritisk lite disk: kun {disk_free_gb:.1f}GB igjen")

        return {
            "cpu_percent": round(cpu_percent, 1),
            "memory_percent": round(memory_percent, 1),
            "memory_available_gb": round(memory_available_gb, 2),
            "disk_percent": round(disk_percent, 1),
            "disk_free_gb": round(disk_free_gb, 2),
            "external_disk": external_disk,
            "issues": issues
        }

    except Exception as e:
        return {
            "cpu_percent": 0,
            "memory_percent": 0,
            "memory_available_gb": 0,
            "disk_percent": 0,
            "disk_free_gb": 0,
            "external_disk": None,
            "issues": [f"kunne ikke sjekke resources: {e}"]
        }


def collect_health() -> Dict[str, Any]:
    """Samle all health data"""

    health = {
        "timestamp": datetime.now().isoformat(),
        "services": {
            "memory_daemon": check_memory_daemon(),
            "qdrant": check_qdrant(),
        },
        "resources": check_resources(),
        "costs": check_costs(),
    }

    # Determine overall status
    all_issues = []
    all_issues.extend(health["services"]["memory_daemon"]["issues"])
    all_issues.extend(health["services"]["qdrant"]["issues"])
    all_issues.extend(health["resources"]["issues"])
    all_issues.extend(health["costs"]["issues"])

    if any("kritisk" in i.lower() for i in all_issues):
        health["overall_status"] = "critical"
    elif len(all_issues) > 0:
        health["overall_status"] = "degraded"
    else:
        health["overall_status"] = "healthy"

    health["all_issues"] = all_issues

    return health


def analyze_with_llm(current_health: Dict[str, Any], history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Bruk LLM til å analysere health data og predikere problemer

    Dette er magien - AIKI lærer mønstre og predikerer issues før de skjer!
    """

    from mem0 import Memory
    from src.config.mem0_config import get_mem0_config, setup_environment

    # Setup mem0 med sentral konfigurasjon
    setup_environment()
    m = Memory.from_config(get_mem0_config())

    # Søk etter lignende issues i fortiden
    issues_str = ", ".join(current_health.get("all_issues", []))
    similar_incidents = []

    if issues_str:
        try:
            search_results = m.search(
                f"system issue {issues_str}",
                user_id='jovnna',
                limit=5
            )

            if search_results and 'results' in search_results:
                similar_incidents = [r['memory'] for r in search_results['results']]
        except:
            pass

    # Bygg prompt
    # Ta siste 12 checks (1 time)
    recent_history = history[-12:] if len(history) > 12 else history

    prompt = f"""Du er AIKI, som overvåker din egen system health.

NÅVÆRENDE TILSTAND:
{json.dumps(current_health, indent=2)}

NYLIG HISTORIKK (siste time):
{json.dumps(recent_history, indent=2)}

TIDLIGERE INCIDENTER DU HUSKER:
{json.dumps(similar_incidents, indent=2)}

SPØRSMÅL:
1. Er nåværende tilstand bekymringsfull?
2. Bør jeg alerte Jovnna eller er dette normalt?
3. Hvis bekymringsfull, hva bør gjøres?

Svar på NORSK i JSON format:
{{
  "alert_level": "none|warning|critical",
  "reasoning": "hvorfor du mener dette (2-3 setninger)",
  "prediction": "hva du tror vil skje (1-2 setninger)",
  "recommendation": "hva bør gjøres (konkret handling)"
}}
"""

    # Kall LLM via OpenRouter
    with track_tokens("health_llm_analysis", "gpt-4o-mini", "health_daemon", "LLM health analysis") as tracker:
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://github.com/samiviking0613/aiki",
                    "X-Title": "AIKI System Health"
                },
                json={
                    "model": "openai/gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2
                },
                timeout=30
            )

            if response.status_code != 200:
                return {
                    "alert_level": "warning",
                    "reasoning": f"LLM API feilet: {response.status_code}",
                    "prediction": "Kunne ikke analysere",
                    "recommendation": "Sjekk manuelt"
                }

            result = response.json()

            # Parse JSON fra LLM
            content = result["choices"][0]["message"]["content"]

            # Fjern markdown code blocks hvis de finnes
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            analysis = json.loads(content)

            # Track tokens
            tracker.set_tokens(
                result["usage"]["prompt_tokens"],
                result["usage"]["completion_tokens"]
            )

            return analysis

        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            return {
                "alert_level": "warning",
                "reasoning": f"LLM analyse feilet: {e}",
                "prediction": "Ukjent",
                "recommendation": "Sjekk logs"
            }


def send_desktop_notification(title: str, message: str, urgency: str = "normal"):
    """Send desktop notification"""
    try:
        subprocess.run([
            "notify-send",
            "-u", urgency,
            title,
            message
        ], timeout=5)
    except:
        pass


class HealthDaemon:
    """Hovedklassen for health daemon"""

    def __init__(self):
        self.check_interval = 120  # sekunder (økt fra 60 for å redusere thread load)
        self.llm_check_interval = 5  # analyser hver 5. anomaly (økt fra 3)
        self.check_count = 0
        self.anomaly_count = 0
        self.history: List[Dict[str, Any]] = []
        self.health_file = Path.home() / "aiki" / "system_health.json"

        # Sørg for at data dir finnes
        self.health_file.parent.mkdir(parents=True, exist_ok=True)

        # Initialize process monitor (Fase 2!)
        self.process_monitor = ProcessMonitor()
        logger.info("Process Monitor initialisert - lærer baseline over tid")

    def run(self):
        """Hovedløkke"""
        logger.startup()

        while True:
            try:
                # Samle health
                health = collect_health()

                # FASE 2: Samle process data
                process_snapshots = self.process_monitor.collect_processes(filter_python=True)
                self.process_monitor.learn_baseline(process_snapshots)
                process_anomalies = self.process_monitor.detect_anomalies(process_snapshots)

                # Legg til process data i health
                health["processes"] = {
                    "total_python_processes": len(process_snapshots),
                    "total_cpu": sum(p.cpu_percent for p in process_snapshots),
                    "total_memory_mb": sum(p.memory_mb for p in process_snapshots),
                    "anomalies": [
                        {
                            "type": a.type,
                            "process": a.process_name,
                            "pid": a.pid,
                            "severity": a.severity,
                            "description": a.description,
                            "current": a.current_value,
                            "baseline": a.baseline_value,
                            "factor": a.deviation_factor
                        }
                        for a in process_anomalies
                    ]
                }

                # Legg til process anomalies i all_issues
                for anomaly in process_anomalies:
                    if anomaly.severity in ['high', 'critical']:
                        health["all_issues"].append(anomaly.description)

                # Legg til history
                self.history.append(health)

                # Behold kun siste 24 timer (1440 checks × 60s = 1 dag)
                if len(self.history) > 1440:
                    self.history = self.history[-1440:]

                # Lagre til JSON fil (for SessionStart hook)
                try:
                    self.health_file.write_text(json.dumps(health, indent=2))
                except Exception as e:
                    logger.error(f"Could not write health file: {e}")

                # Logg process anomalies spesifikt
                if process_anomalies:
                    for anomaly in process_anomalies:
                        if anomaly.severity == 'critical':
                            logger.error(f"🚨 KRITISK PROSESS-ANOMALI: {anomaly.description}")
                        elif anomaly.severity == 'high':
                            logger.warning(f"⚠️ PROSESS-ANOMALI: {anomaly.description}")

                # Sjekk om vi har issues
                has_issues = len(health.get("all_issues", [])) > 0

                if has_issues:
                    self.anomaly_count += 1

                    # Logg issues i naturlig språk
                    issues_str = ", ".join(health["all_issues"])
                    logger.anomaly(
                        description=issues_str,
                        times=self.anomaly_count,
                        pattern="analyserer..."
                    )

                    # Hver N-te anomaly: kjør LLM analyse
                    if self.anomaly_count % self.llm_check_interval == 0:
                        logger.info("Kjører LLM-analyse av anomalier...")

                        analysis = analyze_with_llm(health, self.history)

                        # Logg analyse
                        logger.say(
                            "anomaly_detected",
                            description=analysis["reasoning"],
                            times=self.anomaly_count,
                            pattern=analysis["prediction"]
                        )

                        # Send notification hvis critical
                        if analysis["alert_level"] == "critical":
                            send_desktop_notification(
                                "🚨 AIKI Critical Issue",
                                analysis["recommendation"],
                                urgency="critical"
                            )

                        # Send notification hvis warning og ny type issue
                        elif analysis["alert_level"] == "warning":
                            send_desktop_notification(
                                "⚠️ AIKI Warning",
                                analysis["recommendation"],
                                urgency="normal"
                            )

                else:
                    # Alt friskt - logg hver 10. sjekk (10 min)
                    if self.check_count % 10 == 0:
                        daemon = health["services"]["memory_daemon"]
                        qdrant = health["services"]["qdrant"]
                        costs = health["costs"]

                        uptime = f"{daemon['uptime_hours']}h" if daemon['uptime_hours'] > 0 else "stopped"

                        logger.health_check(
                            uptime=uptime,
                            memory_count=qdrant.get("memory_count", 0),
                            size_mb=qdrant.get("size_mb", 0),
                            cost=costs.get("today_usd", 0)
                        )

                self.check_count += 1

            except Exception as e:
                logger.error(f"Health check loop failed: {e}")

            # Vent til neste sjekk
            time.sleep(self.check_interval)


if __name__ == "__main__":
    print("🏥 Starting AIKI System Health Daemon...")
    print("Overvåker system hvert minutt")
    print("Ctrl+C for å stoppe\n")

    daemon = HealthDaemon()

    try:
        daemon.run()
    except KeyboardInterrupt:
        print("\n\n💤 Stopping health daemon...")
        logger.shutdown("Stopped by user (Ctrl+C)")
        sys.exit(0)
