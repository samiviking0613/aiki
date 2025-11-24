#!/usr/bin/env python3
"""
🤖 AIKI Session Resume Script
Leser forrige session state og gir deg oversikt

Usage: python resume_session.py
"""

import json
from datetime import datetime
from pathlib import Path

def resume_session():
    """Leser og viser forrige session state"""

    aiki_dir = Path.home() / "aiki"
    session_file = aiki_dir / "SESSION_STATE.md"
    session_json = aiki_dir / "session_state.json"

    # Sjekk om session finnes
    if not session_json.exists() and not session_file.exists():
        print("⚠️ Ingen lagret session funnet.")
        print("💡 Lagre en session med: python ~/aiki/save_session.py")
        return None

    # Les JSON hvis tilgjengelig
    session_data = None
    if session_json.exists():
        try:
            with open(session_json, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
        except Exception as e:
            print(f"⚠️ Kunne ikke lese JSON: {e}")

    # Vis oversikt
    print("\n" + "="*60)
    print("🤖 AIKI SESSION RESUME")
    print("="*60 + "\n")

    if session_data:
        # Beregn tid siden sist
        session_time = datetime.fromisoformat(session_data['timestamp'])
        time_since = datetime.now() - session_time

        hours = int(time_since.total_seconds() / 3600)
        minutes = int((time_since.total_seconds() % 3600) / 60)

        time_ago = ""
        if hours > 0:
            time_ago = f"{hours} time(r) og {minutes} minutt(er) siden"
        else:
            time_ago = f"{minutes} minutt(er) siden"

        print(f"📅 Forrige session: {session_data['date_readable']}")
        print(f"⏰ Tid siden: {time_ago}\n")

        print("📝 SAMMENDRAG:")
        print(f"   {session_data['summary']}\n")

        if session_data.get('objectives'):
            print("📌 HVA VI HOLDER PÅ MED:")
            for i, obj in enumerate(session_data['objectives'], 1):
                print(f"   {i}. {obj}")
            print()

        if session_data.get('achievements'):
            print("✅ HVA VI FIKK TIL:")
            for i, ach in enumerate(session_data['achievements'], 1):
                print(f"   {i}. {ach}")
            print()

        if session_data.get('next_steps'):
            print("⏭️ NESTE STEG:")
            for i, step in enumerate(session_data['next_steps'], 1):
                print(f"   {i}. {step}")
            print()

    else:
        # Fallback til markdown hvis JSON ikke finnes
        print(f"📄 SESSION_STATE.md finnes på: {session_file}")
        print("💡 Åpne filen for å se detaljer\n")

    print("="*60)
    print("💡 Klar til å fortsette der vi slapp!")
    print("="*60 + "\n")

    return session_data

def get_session_summary():
    """Returnerer kort sammendrag for Claude Code"""

    aiki_dir = Path.home() / "aiki"
    session_json = aiki_dir / "session_state.json"

    if session_json.exists():
        try:
            with open(session_json, 'r', encoding='utf-8') as f:
                data = json.load(f)

            summary = f"Forrige session: {data['summary']}"

            if data.get('next_steps'):
                summary += f"\nNeste steg: {data['next_steps'][0]}"

            return summary
        except:
            pass

    return "Ingen tidligere session funnet."

if __name__ == "__main__":
    resume_session()
