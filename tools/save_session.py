#!/usr/bin/env python3
"""
🤖 AIKI Session Save Script
Lagrer current session state for sømløs resume

Usage: python save_session.py "Beskrivelse av hva vi gjorde"
"""

import json
import sys
from datetime import datetime
from pathlib import Path

def save_session_state(summary: str = None):
    """Lagrer session state til SESSION_STATE.md"""

    aiki_dir = Path.home() / "aiki"
    session_file = aiki_dir / "SESSION_STATE.md"
    session_json = aiki_dir / "session_state.json"

    # Samle session data
    timestamp = datetime.now()

    if not summary:
        summary = input("📝 Hva jobbet vi med i denne sesjonen? ")

    # Be om objectives og achievements
    print("\n📌 Hva holder vi på med? (trykk Enter når ferdig)")
    objectives = []
    while True:
        obj = input(f"  {len(objectives)+1}. ")
        if not obj:
            break
        objectives.append(obj)

    print("\n✅ Hva fikk vi til? (trykk Enter når ferdig)")
    achievements = []
    while True:
        ach = input(f"  {len(achievements)+1}. ")
        if not ach:
            break
        achievements.append(ach)

    print("\n⏳ Hva skal gjøres neste gang? (trykk Enter når ferdig)")
    next_steps = []
    while True:
        step = input(f"  {len(next_steps)+1}. ")
        if not step:
            break
        next_steps.append(step)

    # Lag session data
    session_data = {
        "session_id": f"session_{timestamp.strftime('%Y%m%d_%H%M%S')}",
        "timestamp": timestamp.isoformat(),
        "date_readable": timestamp.strftime("%d. %B %Y, kl %H:%M"),
        "summary": summary,
        "objectives": objectives,
        "achievements": achievements,
        "next_steps": next_steps
    }

    # Lagre JSON (for programmatisk lesing)
    with open(session_json, 'w', encoding='utf-8') as f:
        json.dump(session_data, f, indent=2, ensure_ascii=False)

    # Lagre Markdown (for mennesker)
    markdown = f"""# 🤖 AIKI Session State

**Dato:** {session_data['date_readable']}
**Session ID:** {session_data['session_id']}

## 📝 SAMMENDRAG:

{summary}

## 📌 HVA VI HOLDER PÅ MED:

"""

    if objectives:
        for i, obj in enumerate(objectives, 1):
            markdown += f"{i}. {obj}\n"
    else:
        markdown += "_(ingen aktive oppgaver)_\n"

    markdown += "\n## ✅ HVA VI FIKK TIL:\n\n"

    if achievements:
        for i, ach in enumerate(achievements, 1):
            markdown += f"{i}. {ach}\n"
    else:
        markdown += "_(ingen achievements denne sesjonen)_\n"

    markdown += "\n## ⏭️ NESTE STEG:\n\n"

    if next_steps:
        for i, step in enumerate(next_steps, 1):
            markdown += f"{i}. {step}\n"
    else:
        markdown += "_(ingen planlagte steg)_\n"

    markdown += f"""

---

## 💡 Tips for resume:

Når du starter Claude Code igjen:
1. Kjør: `python ~/aiki/resume_session.py`
2. Eller si: "resume session" til meg
3. Jeg vil da lese denne filen og fortsette der vi slapp!

---

**Made with 🤖 by AIKI**
**Session lagret:** {timestamp.strftime('%Y-%m-%d %H:%M:%S')}
"""

    with open(session_file, 'w', encoding='utf-8') as f:
        f.write(markdown)

    print(f"\n✅ Session lagret!")
    print(f"📄 Markdown: {session_file}")
    print(f"📋 JSON: {session_json}")
    print(f"\n💡 Resume med: python ~/aiki/resume_session.py")

    return session_data

if __name__ == "__main__":
    summary = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None
    save_session_state(summary)
