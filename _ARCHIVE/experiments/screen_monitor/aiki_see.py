#!/usr/bin/env python3
"""
AIKI See - Vis hva AIKI ser akkurat nå
"""

import json
from pathlib import Path
from datetime import datetime

LATEST_SCREENSHOT = Path.home() / "aiki" / "screen_monitor" / "latest.png"
WINDOW_LOG = Path.home() / "aiki" / "screen_monitor" / "window_activity.jsonl"

def get_latest_activity():
    """Hent siste aktivitet fra loggen"""
    try:
        with open(WINDOW_LOG, 'r') as f:
            lines = f.readlines()
            if lines:
                return json.loads(lines[-1])
    except FileNotFoundError:
        return None
    return None

def main():
    print("👁️  AIKI Vision - Siste observasjon\n")
    print("=" * 60)

    # Sjekk om screenshot eksisterer
    if not LATEST_SCREENSHOT.exists():
        print("❌ Ingen screenshot tilgjengelig ennå")
        print("   Start AIKI Vision Monitor først!")
        return

    # Hent aktivitetsinfo
    activity = get_latest_activity()

    if activity:
        timestamp = datetime.fromisoformat(activity['timestamp'])
        print(f"⏰ Tidspunkt: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🪟 Aktivt vindu: {activity['active_window']}")
        print(f"📊 Antall åpne vinduer: {activity['window_count']}")

        if activity['open_windows']:
            print(f"\n📋 Åpne vinduer:")
            for i, window in enumerate(activity['open_windows'][:10], 1):
                print(f"   {i}. {window}")
            if len(activity['open_windows']) > 10:
                print(f"   ... og {len(activity['open_windows']) - 10} flere")

    print(f"\n📸 Screenshot: {LATEST_SCREENSHOT}")
    print("=" * 60)

    # For Claude Code: Dette er stien til siste screenshot
    print(f"\n🤖 Claude kan lese: {LATEST_SCREENSHOT}")

if __name__ == "__main__":
    main()
