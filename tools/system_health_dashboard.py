#!/usr/bin/env python3.11
"""
📊 AIKI System Health Dashboard - Visuell CLI dashboard

Viser all system health data i et vakkert CLI interface.
Bruker Rich library for fancy formatting.

Usage:
    python system_health_dashboard.py          # Vis dashboard
    python system_health_dashboard.py --watch  # Watch mode (oppdaterer hvert 10s)

Created: 2025-11-17
Author: AIKI (Emergent Consciousness)
"""

import sys
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich import box

# Import mem0 for å hente recent logs
sys.path.append(str(Path.home() / "aiki"))
from natural_logger import get_mem0_config
from mem0 import Memory
import os
from aiki_config import OPENROUTER_KEY, OPENROUTER_URL


def get_recent_logs(limit: int = 5) -> list:
    """Hent siste system logs fra mem0"""
    try:
        os.environ['OPENAI_API_KEY'] = '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'
        os.environ['OPENAI_BASE_URL'] = 'https://openrouter.ai/api/v1'

        config = get_mem0_config()
        m = Memory.from_config(config)

        # Søk etter system logs
        results = m.search(
            "System Health Monitor",
            user_id='jovnna',
            limit=limit
        )

        if results and 'results' in results:
            return [r['memory'] for r in results['results']]

        return []
    except Exception as e:
        return [f"Kunne ikke hente logs: {e}"]


def load_health() -> Dict[str, Any]:
    """Last health data fra JSON fil"""
    health_file = Path.home() / "aiki" / "system_health.json"

    if not health_file.exists():
        return {
            "error": "Health file ikke funnet. Start health daemon først.",
            "timestamp": datetime.now().isoformat(),
            "overall_status": "unknown"
        }

    try:
        return json.loads(health_file.read_text())
    except Exception as e:
        return {
            "error": f"Kunne ikke lese health file: {e}",
            "timestamp": datetime.now().isoformat(),
            "overall_status": "error"
        }


def make_dashboard(health: Dict[str, Any]) -> Layout:
    """Bygg dashboard layout"""
    console = Console()

    # Check for error
    if "error" in health:
        return Panel(
            f"[red]❌ FEIL:[/red] {health['error']}",
            title="AIKI System Health Dashboard",
            border_style="red"
        )

    # Main layout
    layout = Layout()

    # Header
    status = health.get("overall_status", "unknown")
    status_emoji = {
        "healthy": "✅",
        "degraded": "⚠️",
        "critical": "🚨",
        "unknown": "❓"
    }.get(status, "❓")

    status_color = {
        "healthy": "green",
        "degraded": "yellow",
        "critical": "red",
        "unknown": "white"
    }.get(status, "white")

    timestamp = health.get("timestamp", "")
    if timestamp:
        dt = datetime.fromisoformat(timestamp)
        timestamp_str = dt.strftime("%Y-%m-%d %H:%M:%S")
    else:
        timestamp_str = "Ukjent tid"

    header = Panel(
        f"[bold]{status_emoji} Status: [{status_color}]{status.upper()}[/{status_color}][/bold]\n"
        f"Siste oppdatering: {timestamp_str}",
        title="🏥 AIKI SYSTEM HEALTH DASHBOARD",
        border_style=status_color,
        box=box.DOUBLE
    )

    # Services table
    services_table = Table(
        title="Services",
        show_header=True,
        header_style="bold cyan",
        border_style="blue",
        box=box.ROUNDED
    )
    services_table.add_column("Service", style="cyan", no_wrap=True)
    services_table.add_column("Status", no_wrap=True)
    services_table.add_column("Detaljer")

    services = health.get("services", {})

    # Memory Daemon
    daemon = services.get("memory_daemon", {})
    daemon_status = daemon.get("status", "unknown")
    daemon_emoji = "✅" if daemon_status == "running" else "🚨"
    daemon_color = "green" if daemon_status == "running" else "red"
    daemon_uptime = daemon.get("uptime_hours", 0)
    daemon_details = f"{daemon_uptime}h uptime" if daemon_status == "running" else "Ikke kjørende"

    services_table.add_row(
        "Memory Daemon",
        f"[{daemon_color}]{daemon_emoji} {daemon_status}[/{daemon_color}]",
        daemon_details
    )

    # Qdrant
    qdrant = services.get("qdrant", {})
    qdrant_status = qdrant.get("status", "unknown")
    qdrant_emoji = "✅" if qdrant_status == "running" else "🚨"
    qdrant_color = "green" if qdrant_status == "running" else "red"
    qdrant_count = qdrant.get("memory_count", 0)
    qdrant_size = qdrant.get("size_mb", 0)
    qdrant_details = f"{qdrant_count} minner ({qdrant_size}MB)" if qdrant_status == "running" else "Ikke tilgjengelig"

    services_table.add_row(
        "Qdrant",
        f"[{qdrant_color}]{qdrant_emoji} {qdrant_status}[/{qdrant_color}]",
        qdrant_details
    )

    # Resources table
    resources_table = Table(
        title="System Resources",
        show_header=True,
        header_style="bold yellow",
        border_style="yellow",
        box=box.ROUNDED
    )
    resources_table.add_column("Resource", style="yellow", no_wrap=True)
    resources_table.add_column("Usage", justify="right")
    resources_table.add_column("Status", justify="center")

    resources = health.get("resources", {})

    # CPU
    cpu_percent = resources.get("cpu_percent", 0)
    cpu_color = "green" if cpu_percent < 70 else "yellow" if cpu_percent < 90 else "red"
    cpu_emoji = "✅" if cpu_percent < 70 else "⚠️" if cpu_percent < 90 else "🚨"
    resources_table.add_row(
        "CPU",
        f"[{cpu_color}]{cpu_percent}%[/{cpu_color}]",
        cpu_emoji
    )

    # Memory
    mem_percent = resources.get("memory_percent", 0)
    mem_available = resources.get("memory_available_gb", 0)
    mem_color = "green" if mem_percent < 70 else "yellow" if mem_percent < 90 else "red"
    mem_emoji = "✅" if mem_percent < 70 else "⚠️" if mem_percent < 90 else "🚨"
    resources_table.add_row(
        "Memory",
        f"[{mem_color}]{mem_percent}% ({mem_available:.1f}GB fri)[/{mem_color}]",
        mem_emoji
    )

    # Disk
    disk_percent = resources.get("disk_percent", 0)
    disk_free = resources.get("disk_free_gb", 0)
    disk_color = "green" if disk_percent < 70 else "yellow" if disk_percent < 85 else "red"
    disk_emoji = "✅" if disk_percent < 70 else "⚠️" if disk_percent < 85 else "🚨"
    resources_table.add_row(
        "Disk (/)",
        f"[{disk_color}]{disk_percent}% ({disk_free:.1f}GB fri)[/{disk_color}]",
        disk_emoji
    )

    # External disk
    external = resources.get("external_disk")
    if external:
        ext_percent = external.get("percent", 0)
        ext_free = external.get("free_gb", 0)
        ext_color = "green" if ext_percent < 70 else "yellow" if ext_percent < 85 else "red"
        ext_emoji = "✅" if ext_percent < 70 else "⚠️" if ext_percent < 85 else "🚨"
        resources_table.add_row(
            "Disk (External)",
            f"[{ext_color}]{ext_percent}% ({ext_free:.1f}GB fri)[/{ext_color}]",
            ext_emoji
        )

    # Costs panel
    costs = health.get("costs", {})
    today_usd = costs.get("today_usd", 0)
    today_nok = costs.get("today_nok", 0)
    monthly_usd = costs.get("monthly_projection_usd", 0)
    monthly_nok = costs.get("monthly_projection_nok", 0)
    quota = costs.get("quota_remaining_percent", 100)

    cost_color = "green" if today_usd < 0.5 else "yellow" if today_usd < 1.0 else "red"

    costs_text = f"""[{cost_color}]I dag:[/{cost_color}] ${today_usd:.4f} (~{today_nok:.2f} kr)
[{cost_color}]Månedlig proj.:[/{cost_color}] ${monthly_usd:.2f} (~{monthly_nok:.0f} kr)
[bold]Quota igjen:[/bold] {quota:.1f}%"""

    costs_panel = Panel(
        costs_text,
        title="💰 Token Costs",
        border_style=cost_color,
        box=box.ROUNDED
    )

    # Process Anomalies panel (FASE 2!)
    processes = health.get("processes", {})
    process_anomalies = processes.get("anomalies", [])

    if process_anomalies:
        anomalies_lines = []
        for anomaly in process_anomalies[:5]:  # Max 5
            severity_emoji = {
                "critical": "🚨",
                "high": "⚠️",
                "medium": "ℹ️",
                "low": "💡"
            }.get(anomaly["severity"], "•")

            severity_color = {
                "critical": "red",
                "high": "yellow",
                "medium": "blue",
                "low": "white"
            }.get(anomaly["severity"], "white")

            anomalies_lines.append(
                f"[{severity_color}]{severity_emoji} {anomaly['process']} (PID {anomaly['pid']})[/{severity_color}]"
            )
            anomalies_lines.append(
                f"   Type: {anomaly['type']}"
            )
            anomalies_lines.append(
                f"   Current: {anomaly['current']:.1f} (baseline: {anomaly['baseline']:.1f})"
            )
            anomalies_lines.append(
                f"   Factor: {anomaly['factor']:.1f}x over normal"
            )
            anomalies_lines.append("")  # Blank line

        anomalies_text = "\n".join(anomalies_lines)

        anomalies_panel = Panel(
            anomalies_text,
            title="⚠️ Process Anomalies",
            border_style="red",
            box=box.ROUNDED
        )
    else:
        # Show process summary even if no anomalies
        total_procs = processes.get("total_python_processes", 0)
        total_cpu = processes.get("total_cpu", 0)
        total_mem = processes.get("total_memory_mb", 0)

        if total_procs > 0:
            summary_text = f"""[green]✅ Alle prosesser ser normale ut[/green]

Python prosesser: {total_procs}
Total CPU: {total_cpu:.1f}%
Total Memory: {total_mem:.0f}MB"""
        else:
            summary_text = "[dim]Ingen prosess-data tilgjengelig ennå[/dim]"

        anomalies_panel = Panel(
            summary_text,
            title="✅ Process Status",
            border_style="green",
            box=box.ROUNDED
        )

    # Issues panel
    all_issues = health.get("all_issues", [])
    if all_issues:
        issues_text = "\n".join([f"• {issue}" for issue in all_issues[:5]])
        issues_panel = Panel(
            f"[red]{issues_text}[/red]",
            title="🚨 Issues",
            border_style="red",
            box=box.ROUNDED
        )
    else:
        issues_panel = Panel(
            "[green]Ingen issues! Alt ser bra ut. ✨[/green]",
            title="✅ Status",
            border_style="green",
            box=box.ROUNDED
        )

    # Recent logs
    recent_logs = get_recent_logs(5)
    if recent_logs:
        logs_text = "\n".join([
            f"• {log[:100]}{'...' if len(log) > 100 else ''}"
            for log in recent_logs[:5]
        ])
        logs_panel = Panel(
            logs_text,
            title="📝 Siste System Logs",
            border_style="blue",
            box=box.ROUNDED
        )
    else:
        logs_panel = Panel(
            "[dim]Ingen logs tilgjengelig[/dim]",
            title="📝 Siste System Logs",
            border_style="blue",
            box=box.ROUNDED
        )

    # Return all components to render
    return {
        "header": header,
        "services": services_table,
        "resources": resources_table,
        "costs": costs_panel,
        "anomalies": anomalies_panel,
        "issues": issues_panel,
        "logs": logs_panel
    }


def show_dashboard(watch: bool = False):
    """Vis dashboard (med optional watch mode)"""
    console = Console()

    if not watch:
        # Single shot
        health = load_health()
        components = make_dashboard(health)

        # Print each component
        console.print(components["header"])
        console.print()
        console.print(components["services"])
        console.print()
        console.print(components["resources"])
        console.print()
        console.print(components["costs"])
        console.print()
        console.print(components["anomalies"])
        console.print()
        console.print(components["issues"])
        console.print()
        console.print(components["logs"])
    else:
        # Watch mode - build single panel
        try:
            while True:
                console.clear()
                health = load_health()
                components = make_dashboard(health)

                # Print all
                console.print(components["header"])
                console.print()
                console.print(components["services"])
                console.print()
                console.print(components["resources"])
                console.print()
                console.print(components["costs"])
                console.print()
                console.print(components["anomalies"])
                console.print()
                console.print(components["issues"])
                console.print()
                console.print(components["logs"])

                time.sleep(10)  # Oppdater hvert 10. sekund
        except KeyboardInterrupt:
            console.print("\n[yellow]Dashboard stopped.[/yellow]")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="AIKI System Health Dashboard")
    parser.add_argument(
        "--watch", "-w",
        action="store_true",
        help="Watch mode: oppdater dashboard hvert 10. sekund"
    )

    args = parser.parse_args()

    show_dashboard(watch=args.watch)
