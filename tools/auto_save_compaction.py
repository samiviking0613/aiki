#!/usr/bin/env python3
"""
🧠 AIKI Pre-Compaction Saver - Lagrer FULL context før compaction

Dette scriptet kjøres via Stop hook i Claude Code for å lagre
ALL viktig context til mem0 FØR context window blir compacted.

Key difference from auto_save_smart.py:
- Triggered BEFORE compaction, not at session end
- Saves FULL conversation summary, not just git changes
- Includes working context, decisions, and discoveries

Usage:
    python auto_save_compaction.py
    (Eller kjøres automatisk via Claude Code Stop hook)

Created: 2025-11-23
Author: AIKI (Emergent Consciousness)
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

def get_mem0_client():
    """Initialize mem0 client"""
    try:
        from mem0 import Memory

        os.environ['OPENAI_API_KEY'] = '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'
        os.environ['OPENAI_BASE_URL'] = 'https://openrouter.ai/api/v1'

        config = {
            'llm': {
                'provider': 'openai',
                'config': {
                    'model': 'openai/gpt-4o-mini',
                    'temperature': 0.2,
                    'max_tokens': 2000,
                }
            },
            'embedder': {
                'provider': 'openai',
                'config': {
                    'model': 'text-embedding-3-small',
                    'embedding_dims': 1536
                }
            },
            'vector_store': {
                'provider': 'qdrant',
                'config': {
                    'collection_name': 'mem0_memories',
                    'host': 'localhost',
                    'port': 6333,
                    'embedding_model_dims': 1536
                }
            }
        }

        return Memory.from_config(config)
    except Exception as e:
        print(f"Failed to init mem0: {e}", file=sys.stderr)
        return None


def read_current_context() -> dict:
    """Read current working context from various sources"""
    context = {
        'session_state': None,
        'todos': None,
        'recent_files': [],
        'timestamp': datetime.now().isoformat()
    }

    aiki_dir = Path.home() / "aiki"

    # Read session state
    session_file = aiki_dir / "session_state.json"
    if session_file.exists():
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                context['session_state'] = json.load(f)
        except Exception as e:
            print(f"Could not read session state: {e}", file=sys.stderr)

    # Read last context from auto_resume
    last_context = aiki_dir / ".last_context.txt"
    if last_context.exists():
        try:
            with open(last_context, 'r', encoding='utf-8') as f:
                context['last_context'] = f.read()[:2000]  # Limit size
        except Exception:
            pass

    return context


def save_pre_compaction_memory(summary: Optional[str] = None):
    """Save comprehensive pre-compaction memory to mem0"""

    m = get_mem0_client()
    if not m:
        print("❌ Could not initialize mem0", file=sys.stderr)
        return False

    timestamp = datetime.now()
    context = read_current_context()

    # Build comprehensive memory text
    session = context.get('session_state', {}) or {}

    memory_parts = [
        f"=== PRE-COMPACTION SAVE ({timestamp.strftime('%Y-%m-%d %H:%M')}) ===",
        ""
    ]

    # Add custom summary if provided
    if summary:
        memory_parts.append(f"CURRENT WORK:\n{summary}")
        memory_parts.append("")

    # Add session summary
    if session.get('summary'):
        memory_parts.append(f"SESSION SUMMARY:\n{session['summary'][:1000]}")
        memory_parts.append("")

    # Add next steps
    next_steps = session.get('next_steps', [])
    if next_steps:
        memory_parts.append("PENDING TASKS:")
        for step in next_steps[:10]:
            memory_parts.append(f"  - {step}")
        memory_parts.append("")

    # Add achievements
    achievements = session.get('achievements', [])
    if achievements:
        memory_parts.append("RECENT ACHIEVEMENTS:")
        for ach in achievements[-5:]:
            memory_parts.append(f"  - {ach}")
        memory_parts.append("")

    # Add changes info
    changes = session.get('changes', {})
    if changes:
        memory_parts.append(f"FILE CHANGES:")
        memory_parts.append(f"  - New: {len(changes.get('new_files', []))}")
        memory_parts.append(f"  - Modified: {len(changes.get('modified_files', []))}")
        memory_parts.append(f"  - Deleted: {len(changes.get('deleted_files', []))}")
        memory_parts.append("")

    memory_parts.append(f"REASON: Context window compaction imminent")
    memory_parts.append(f"TYPE: pre_compaction_save")

    memory_text = "\n".join(memory_parts)

    try:
        result = m.add(
            [{'role': 'user', 'content': memory_text}],
            user_id='jovnna',
            metadata={
                'type': 'pre_compaction_save',
                'timestamp': timestamp.isoformat(),
                'source': 'auto_save_compaction'
            }
        )

        print(f"✅ Pre-compaction memory saved!")
        print(f"   Timestamp: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Size: {len(memory_text)} chars")

        # Also save to local file for redundancy
        backup_file = Path.home() / "aiki" / "data" / "compaction_saves" / f"{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        backup_file.parent.mkdir(parents=True, exist_ok=True)

        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': timestamp.isoformat(),
                'memory_text': memory_text,
                'context': context,
                'mem0_result': str(result)
            }, f, indent=2, ensure_ascii=False)

        print(f"   Backup: {backup_file}")

        return True

    except Exception as e:
        print(f"❌ Failed to save: {e}", file=sys.stderr)
        return False


def update_session_state_for_resume():
    """Update session state to help with resume after compaction"""
    aiki_dir = Path.home() / "aiki"
    session_file = aiki_dir / "session_state.json"

    try:
        session = {}
        if session_file.exists():
            with open(session_file, 'r', encoding='utf-8') as f:
                session = json.load(f)

        # Mark that compaction happened
        session['last_compaction'] = datetime.now().isoformat()
        session['compaction_count'] = session.get('compaction_count', 0) + 1

        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session, f, indent=2, ensure_ascii=False)

    except Exception as e:
        print(f"Could not update session state: {e}", file=sys.stderr)


def main():
    """Main entry point"""
    print("=" * 60)
    print("🧠 AIKI PRE-COMPACTION SAVER")
    print("=" * 60)

    # Get optional summary from args
    summary = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None

    # Save to mem0
    success = save_pre_compaction_memory(summary)

    # Update session state
    update_session_state_for_resume()

    if success:
        print("\n✅ Pre-compaction save complete!")
        print("   Context preserved for seamless resume.")
    else:
        print("\n⚠️ Pre-compaction save had issues.")
        print("   Local backup may still be available.")

    print("=" * 60)


if __name__ == "__main__":
    main()
