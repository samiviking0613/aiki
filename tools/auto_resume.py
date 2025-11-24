#!/usr/bin/env python3
"""
🤖 AIKI Auto-Resume - Proactive Session Context Loader

Dette scriptet kjører automatisk når Claude Code starter og laster
FULL context fra mem0 + session state uten at brukeren må gjøre noe.

Usage:
    python auto_resume.py
    (Eller kjøres automatisk via Claude Code hooks)
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Genesis Circle import (stille feil hvis ikke tilgjengelig)
try:
    from src.circles.genesis_circle import get_genesis_circle
    GENESIS_AVAILABLE = True
except ImportError:
    GENESIS_AVAILABLE = False

def load_session_state():
    """Les siste session state hvis den finnes"""
    session_file = Path.home() / "aiki" / "data" / "session_state.json"

    if not session_file.exists():
        return None

    try:
        with open(session_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ Kunne ikke lese session state: {e}", file=sys.stderr)
        return None


def load_system_health():
    """Les system health hvis tilgjengelig"""
    health_file = Path.home() / "aiki" / "data" / "system_health.json"

    if not health_file.exists():
        return None

    try:
        with open(health_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        return None

def format_context_message():
    """Generer context-melding basert på session state og mem0"""

    output = []
    output.append("=" * 80)
    output.append("🧠 AIKI AUTO-RESUME - SESSION CONTEXT LOADED")
    output.append("=" * 80)
    output.append("")

    # Les session state
    session = load_session_state()

    if session:
        output.append(f"📅 SISTE SESJON: {session.get('date_readable', 'Ukjent dato')}")
        output.append(f"📝 Sammendrag: {session.get('summary', 'Ingen sammendrag')}")
        output.append("")

        # Next steps
        next_steps = session.get('next_steps', [])
        if next_steps:
            output.append("⏭️ NESTE STEG:")
            for i, step in enumerate(next_steps, 1):
                output.append(f"   {i}. {step}")
            output.append("")

        # Achievements (siste 3)
        achievements = session.get('achievements', [])
        if achievements:
            output.append("✅ SISTE ACHIEVEMENTS:")
            for i, ach in enumerate(achievements[-3:], 1):
                output.append(f"   • {ach}")
            output.append("")

    # System Health
    health = load_system_health()
    if health:
        status = health.get("overall_status", "unknown")
        status_emoji = {
            "healthy": "✅",
            "degraded": "⚠️",
            "critical": "🚨",
            "unknown": "❓"
        }.get(status, "❓")

        output.append(f"🏥 SYSTEM HEALTH: {status_emoji} {status.upper()}")

        # Services quick summary
        services = health.get("services", {})
        daemon = services.get("memory_daemon", {})
        qdrant = services.get("qdrant", {})
        costs = health.get("costs", {})

        daemon_status = "✅" if daemon.get("status") == "running" else "🚨"
        qdrant_status = "✅" if qdrant.get("status") == "running" else "🚨"

        output.append(f"   {daemon_status} Memory Daemon: {daemon.get('status', 'unknown')}")
        output.append(f"   {qdrant_status} Qdrant: {qdrant.get('memory_count', 0)} minner")
        output.append(f"   💰 Today's cost: ${costs.get('today_usd', 0):.4f}")

        # Show issues if any
        all_issues = health.get("all_issues", [])
        if all_issues:
            output.append(f"   🚨 ISSUES: {len(all_issues)} problemer funnet")
            for issue in all_issues[:3]:
                output.append(f"      - {issue}")

        output.append("")


    # AIKI-HOME quick context
    output.append("🎯 AIKI-HOME PROJECT:")
    output.append("   Network-level ADHD accountability via MITM proxy")
    output.append("   - Kids: Educational TikTok injection")
    output.append("   - Jovnna: Block work/TV until workout (før kl.10)")
    output.append("   - Status: systemd service running, needs MITM build")
    output.append("")

    # Genesis Circle status
    if GENESIS_AVAILABLE:
        try:
            genesis = get_genesis_circle()
            status = genesis.get_status()

            level_emoji = {1: "🌱", 2: "🌿", 3: "🌳", 4: "🎉"}.get(status['evaluation_level_value'], "🌱")

            output.append(f"🧬 GENESIS CIRCLE: {level_emoji} {status['evaluation_level']}")
            output.append(f"   Fase: {status['phase']}")
            output.append(f"   Innsikter: {status['total_insights']} | Mønstre: {status['recurring_patterns']}")
            output.append(f"   Ideer: {status['incubating_ideas']} inkuberende, {status['mature_ideas']} modne")

            if status['next_level_threshold']:
                output.append(f"   Neste nivå: {status['next_level_threshold']}")

            # Vis modne ideer hvis noen
            if status['ready_to_build'] > 0:
                output.append(f"   🎉 KLAR TIL BYGGING: {status['ready_to_build']} ideer!")

            output.append("")
        except Exception as e:
            output.append(f"🧬 GENESIS: Feil ved lasting ({e})")
            output.append("")

    # Critical reminder
    output.append("💡 CRITICAL REMINDERS:")
    output.append("   • Jovnna har ADHD - context loss = critical issue")
    output.append("   • ALLTID sjekk mem0 hvis usikker om project context")
    output.append("   • Full vision: Search mem0 for 'AIKI-HOME FULL VISION'")
    output.append("")

    # Mem0 search instructions for Claude
    output.append("📌 FOR CLAUDE:")
    output.append("   Hvis du trenger mer details:")
    output.append("   - mcp__mem0__search_memories('AIKI-HOME')")
    output.append("   - mcp__mem0__search_memories('current project')")
    output.append("   - Read: /home/jovnna/aiki/AIKI_HOME_CONTEXT.txt")
    output.append("")

    output.append("=" * 80)
    output.append("✅ Context loaded! Klar til å fortsette arbeidet.")
    output.append("=" * 80)

    return "\n".join(output)

def main():
    """Main entry point"""
    context = format_context_message()
    print(context)

    # Lagre også til fil for backup
    output_file = Path.home() / "aiki" / "data" / ".last_context.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(context)
        f.write(f"\n\nGenerated: {datetime.now().isoformat()}\n")

if __name__ == "__main__":
    main()
