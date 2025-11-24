#!/usr/bin/env python3
"""
🤖 AIKI Auto-Save - Automatic Session State Saver

Kjøres automatisk når Claude Code avsluttes via SessionEnd hook.
Lagrer minimal session state uten user interaction.

Usage:
    python auto_save.py [optional summary]
"""

import json
import sys
from datetime import datetime
from pathlib import Path

def auto_save_session(summary: str = None):
    """Auto-save session state på session end"""

    aiki_dir = Path.home() / "aiki"
    session_file = aiki_dir / "SESSION_STATE.md"
    session_json = aiki_dir / "session_state.json"

    # Read existing session if it exists
    existing_data = {}
    if session_json.exists():
        try:
            with open(session_json, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        except:
            pass

    # Create minimal update
    timestamp = datetime.now()

    # If no summary provided, use existing or default
    if not summary:
        summary = existing_data.get('summary', 'Session ended - state auto-saved')

    # Update session data with end timestamp
    session_data = existing_data.copy()
    session_data['last_saved'] = timestamp.isoformat()
    session_data['last_saved_readable'] = timestamp.strftime("%d. %B %Y, kl %H:%M")
    session_data['auto_saved'] = True

    # Save JSON
    with open(session_json, 'w', encoding='utf-8') as f:
        json.dump(session_data, f, indent=2, ensure_ascii=False)

    # Create minimal markdown update
    markdown = f"""# 🤖 AIKI Session State

**Dato:** {session_data.get('date_readable', timestamp.strftime("%d. %B %Y, kl %H:%M"))}
**Session ID:** {session_data.get('session_id', 'unknown')}
**Last Saved:** {session_data['last_saved_readable']}

## 📝 SAMMENDRAG:

{summary}

## ⏭️ NESTE STEG:

"""

    # Add next steps if they exist
    next_steps = session_data.get('next_steps', [])
    if next_steps:
        for i, step in enumerate(next_steps, 1):
            markdown += f"{i}. {step}\n"
    else:
        markdown += "_(se forrige session state for detaljer)_\n"

    markdown += """

---

## 💡 Tips for resume:

Når du starter Claude Code igjen:
1. SessionStart hook kjører automatisk → auto_resume.py viser context
2. CLAUDE.md lastes inn → AIKI-HOME context i system prompt
3. God mode aktiv → alle edits auto-accepted
4. Send én melding (hva som helst) → jeg responderer med full context

---

**Made with 🤖 by AIKI**
**Auto-saved on session end:** {timestamp.strftime('%Y-%m-%d %H:%M:%S')}
"""

    with open(session_file, 'w', encoding='utf-8') as f:
        f.write(markdown)

    # Silent success (no output needed for hook)
    return True

if __name__ == "__main__":
    summary = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None
    auto_save_session(summary)
