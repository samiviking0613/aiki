#!/usr/bin/env python3
"""
Lærende system for å finne faktiske Claude token limits.

Tracker faktisk bruk og lærer seg:
1. Session limit (5-timers vindu)
2. Weekly limit
3. Auto-justerer basert på når limits nås
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path


LIMITS_FILE = Path.home() / "aiki" / "data" / "claude_learned_limits.json"


def load_limits():
    """Last lagrede limits eller initialiser med community-estimater."""
    if LIMITS_FILE.exists():
        with open(LIMITS_FILE) as f:
            return json.load(f)

    # Initialiser med community-bekreftede estimater
    return {
        "session_limit": {
            "estimated": 88000,
            "confidence": 0.5,  # 50% sikker (community data)
            "actual_hits": [],  # Timestamps når limit nås
            "last_updated": None
        },
        "weekly_limit": {
            "estimated": 88000 * 28,  # 88K × 28 sessions (140h/5h)
            "confidence": 0.3,  # 30% sikker (estimert)
            "actual_hits": [],
            "last_updated": None
        },
        "context_window": {
            "estimated": 200000,
            "confidence": 1.0,  # 100% sikker (dokumentert)
            "last_updated": None
        },
        "measurements": []
    }


def save_limits(limits):
    """Lagre learned limits."""
    LIMITS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LIMITS_FILE, 'w') as f:
        json.dump(limits, f, indent=2)


def add_measurement(limits, tokens_used, session_duration_hours, hit_limit=False):
    """
    Legg til ny måling og juster estimates.

    Args:
        tokens_used: Totalt tokens brukt i session
        session_duration_hours: Hvor lenge session varte
        hit_limit: Om session endte pga limit hit
    """
    now = datetime.utcnow()

    measurement = {
        "timestamp": now.isoformat(),
        "tokens_used": tokens_used,
        "duration_hours": session_duration_hours,
        "hit_limit": hit_limit
    }

    limits["measurements"].append(measurement)

    # Hvis vi nådde limit, vi har et datapunkt!
    if hit_limit:
        limits["session_limit"]["actual_hits"].append({
            "timestamp": now.isoformat(),
            "tokens_at_limit": tokens_used
        })

        # Oppdater estimate basert på faktisk data
        all_hits = [h["tokens_at_limit"] for h in limits["session_limit"]["actual_hits"]]
        avg_limit = sum(all_hits) / len(all_hits)

        # Øk confidence jo flere målinger vi har
        num_measurements = len(all_hits)
        confidence = min(0.9, 0.5 + (num_measurements * 0.1))

        limits["session_limit"]["estimated"] = int(avg_limit)
        limits["session_limit"]["confidence"] = confidence
        limits["session_limit"]["last_updated"] = now.isoformat()

    # Behold bare siste 100 målinger
    if len(limits["measurements"]) > 100:
        limits["measurements"] = limits["measurements"][-100:]

    save_limits(limits)
    return limits


def get_current_limits():
    """Hent current best estimates."""
    limits = load_limits()

    return {
        "session": {
            "limit": limits["session_limit"]["estimated"],
            "confidence": limits["session_limit"]["confidence"],
            "measurements": len(limits["session_limit"]["actual_hits"])
        },
        "weekly": {
            "limit": limits["weekly_limit"]["estimated"],
            "confidence": limits["weekly_limit"]["confidence"],
            "measurements": len(limits["weekly_limit"]["actual_hits"])
        },
        "context": {
            "limit": limits["context_window"]["estimated"],
            "confidence": limits["context_window"]["confidence"]
        }
    }


def print_limits():
    """Print current learned limits."""
    current = get_current_limits()

    print("\n" + "="*60)
    print("🧠 LEARNED CLAUDE LIMITS")
    print("="*60)

    print(f"\n📍 SESSION LIMIT (5-timers vindu):")
    print(f"  Estimate: {current['session']['limit']:>10,} tokens")
    print(f"  Confidence: {current['session']['confidence']*100:>6.1f}%")
    print(f"  Measurements: {current['session']['measurements']}")

    print(f"\n📍 WEEKLY LIMIT:")
    print(f"  Estimate: {current['weekly']['limit']:>10,} tokens")
    print(f"  Confidence: {current['weekly']['confidence']*100:>6.1f}%")
    print(f"  Measurements: {current['weekly']['measurements']}")

    print(f"\n📍 CONTEXT WINDOW:")
    print(f"  Limit: {current['context']['limit']:>10,} tokens")
    print(f"  Confidence: {current['context']['confidence']*100:>6.1f}% (dokumentert)")

    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "show":
        print_limits()
    else:
        print("Usage:")
        print("  python3 learn_claude_limits.py show")
        print("  python3 learn_claude_limits.py add <tokens> <hours> [hit_limit]")
