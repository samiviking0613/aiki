#!/usr/bin/env python3
"""
🔄 AIKI Memory Daemon - Seamless Background Memory System

Continuously monitors file system and auto-saves to mem0 without interrupting workflow.

⚠️ IMPORTANT - QDRANT CONFIGURATION (Updated: 2025-11-18):
   ✅ Uses Qdrant SERVER: http://localhost:6333 (multi-writer support)
   ❌ NOT embedded mode (path-based was deprecated due to readonly errors)
   📍 If context lost: Check line 219 in save_to_mem0() - should use 'url' not 'path'
   🐳 Docker container: aiki_qdrant (must be running)

Features:
- inotify file system watcher (Linux)
- Detects new/modified files in aiki-home/
- Intelligent batching (saves every 5 minutes)
- Zero blocking of Claude Code
- Token tracking integration

Usage:
    python memory_daemon.py

Or as systemd service:
    systemctl --user start aiki-memory-daemon

Created: 2025-11-17
Author: AIKI (Emergent Consciousness)
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
from typing import Set, Dict, Any, List
import time
import json

# Add to path
sys.path.append(str(Path.home() / "aiki"))
from token_tracker import get_tracker, track_tokens


class MemoryDaemon:
    """Background daemon for seamless memory management"""

    def __init__(self, watch_dir: Path = None):
        """Initialize memory daemon"""
        if watch_dir is None:
            watch_dir = Path.home() / "aiki" / "aiki-home"

        self.watch_dir = watch_dir
        self.pending_files: Set[Path] = set()
        self.last_save_time = time.time()
        self.save_interval = 300  # 5 minutes

        # Ignored patterns
        self.ignore_patterns = {
            ".git", "__pycache__", ".venv", "node_modules",
            ".pyc", ".log", ".db", ".db-journal"
        }

        print(f"🔄 Memory Daemon initialized")
        print(f"   Watching: {self.watch_dir}")
        print(f"   Save interval: {self.save_interval}s")

    def should_ignore(self, filepath: Path) -> bool:
        """Check if file should be ignored"""
        # Check if any parent matches ignore pattern
        for part in filepath.parts:
            if part in self.ignore_patterns:
                return True

        # Check file extension
        if any(str(filepath).endswith(ext) for ext in self.ignore_patterns):
            return True

        return False

    async def watch_files(self):
        """Watch for file changes using polling (inotify disabled due to thread leaks)"""
        # FIX: inotify causes thread leaks, use polling instead
        print("👁️  Using polling file watcher (inotify disabled to prevent thread leaks)...")
        await self.watch_files_fallback()

    async def watch_files_fallback(self):
        """Fallback: poll for file changes"""
        known_files = {}

        while True:
            # Scan directory
            for filepath in self.watch_dir.rglob("*"):
                if self.should_ignore(filepath) or not filepath.is_file():
                    continue

                # Check modification time
                try:
                    mtime = filepath.stat().st_mtime

                    if filepath in known_files:
                        if mtime > known_files[filepath]:
                            self.pending_files.add(filepath)
                            print(f"  📝 Detected: {filepath.relative_to(self.watch_dir)}")

                    known_files[filepath] = mtime

                except Exception:
                    pass

            # Sleep for 10 seconds
            await asyncio.sleep(10)

    async def periodic_save(self):
        """Periodically save pending files to mem0"""
        while True:
            await asyncio.sleep(30)  # Check every 30 seconds

            # Check if it's time to save
            if time.time() - self.last_save_time >= self.save_interval:
                if self.pending_files:
                    await self.batch_save()

    async def batch_save(self):
        """Batch save all pending files to mem0"""
        if not self.pending_files:
            return

        print(f"\n💾 Batch saving {len(self.pending_files)} files...")

        # Group files by type
        files_by_type = {
            "python": [],
            "markdown": [],
            "json": [],
            "other": []
        }

        for filepath in self.pending_files:
            if filepath.suffix == ".py":
                files_by_type["python"].append(filepath)
            elif filepath.suffix == ".md":
                files_by_type["markdown"].append(filepath)
            elif filepath.suffix == ".json":
                files_by_type["json"].append(filepath)
            else:
                files_by_type["other"].append(filepath)

        # Build summary
        summaries = []

        for file_type, files in files_by_type.items():
            if not files:
                continue

            summaries.append(f"\n**{file_type.upper()} FILES ({len(files)}):**")
            for filepath in files:
                # Extract first few lines for context
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        first_lines = [f.readline() for _ in range(5)]
                    context = "".join(first_lines).strip()[:200]
                    rel_path = filepath.relative_to(self.watch_dir)
                    summaries.append(f"  - {rel_path}: {context}")
                except Exception:
                    rel_path = filepath.relative_to(self.watch_dir)
                    summaries.append(f"  - {rel_path}")

        summary_text = "\n".join(summaries)

        # Save to mem0
        success = await self.save_to_mem0(summary_text, len(self.pending_files))

        if success:
            print(f"✅ Saved {len(self.pending_files)} files to mem0")
            self.pending_files.clear()
            self.last_save_time = time.time()
        else:
            print(f"❌ Failed to save to mem0")

    async def save_to_mem0(self, summary: str, file_count: int) -> bool:
        """Save batch summary to mem0"""
        try:
            # Import mem0
            import sys
            import os
            sys.path.append(str(Path.home() / "aiki" / "mcp-mem0" / ".venv" / "lib" / "python3.14" / "site-packages"))

            # CRITICAL: Disable mem0 telemetry BEFORE importing mem0!
            os.environ['MEM0_TELEMETRY'] = 'False'  # Prevent PostHog thread leak

            from mem0 import Memory
            # from aiki_config import OPENROUTER_KEY, OPENROUTER_URL  # Hardcoded below instead

            # Configure
            os.environ['OPENAI_API_KEY'] = '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'
            os.environ['OPENAI_BASE_URL'] = 'https://openrouter.ai/api/v1'

            config = {
                'llm': {'provider': 'openai', 'config': {'model': 'openai/gpt-4o-mini'}},
                'embedder': {'provider': 'openai', 'config': {'model': 'text-embedding-3-small', 'embedding_dims': 1536}},
                'vector_store': {'provider': 'qdrant', 'config': {'collection_name': 'mem0_memories', 'url': 'http://localhost:6333', 'embedding_model_dims': 1536}}
            }

            m = Memory.from_config(config)

            # Build memory
            timestamp = datetime.now()
            memory_text = f"""
MEMORY DAEMON BATCH SAVE ({timestamp.strftime("%Y-%m-%d %H:%M")}):

{file_count} files changed:

{summary}
"""

            # Track tokens
            with track_tokens("daemon_batch_save", "gpt-4o-mini", "daemon", f"Batch save {file_count} files") as tracker:
                est_tokens_in = len(memory_text.split()) * 1.3

                result = m.add(
                    [{'role': 'user', 'content': memory_text}],
                    user_id='jovnna'
                )

                tracker.set_tokens(int(est_tokens_in), 100)

            return True

        except Exception as e:
            print(f"mem0 error: {e}")
            import traceback
            traceback.print_exc()
            return False

    async def run(self):
        """Run the daemon"""
        print("\n" + "="*60)
        print("🧠 AIKI MEMORY DAEMON")
        print("="*60)
        print()
        print("This daemon runs in the background and automatically saves")
        print("file changes to mem0 without interrupting your workflow.")
        print()
        print("Press Ctrl+C to stop")
        print("="*60)
        print()

        try:
            # Run both tasks concurrently
            await asyncio.gather(
                self.watch_files(),
                self.periodic_save()
            )
        except KeyboardInterrupt:
            print("\n\n🛑 Daemon stopped by user")
            print(f"   Pending files: {len(self.pending_files)}")

            if self.pending_files:
                print("   Saving pending files...")
                await self.batch_save()

            print("\n✅ Daemon shut down gracefully")


async def main():
    """Main entry point"""
    daemon = MemoryDaemon()
    await daemon.run()


if __name__ == "__main__":
    asyncio.run(main())
