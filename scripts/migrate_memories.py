#!/usr/bin/env python3
"""
AIKI Memory Migration Script

Migrerer alle minnekilder til:
1. Qdrant (embeddings for semantisk søk)
2. SQLite (rå tekst for eksakt søk)

Flytter originale filer til /CEVAULT2TB/migrerte_minner/ etter migrering.

Kilder:
- ChatGPT conversations.json (148 samtaler)
- AIKI v3 sessions (38 filer)
- AIKI v3 andre mapper (claude, collaboration, development, experiences, identity)

#version: 1.0.0
#created: 2025-11-23
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import hashlib
import logging
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
CEVAULT = Path("/run/media/jovnna/CEVAULT2TB")
AIKI_V3 = CEVAULT / "AIKI_v3"
MIGRERTE = CEVAULT / "migrerte_minner"

# Source paths
CHATGPT_JSON = AIKI_V3 / "AIKI_INTERFACE" / "chat" / "conversations.json"
AIKI_MEMORY = AIKI_V3 / "AIKI_MEMORY"
SESSIONS_DIR = AIKI_MEMORY / "sessions"

# Import our memory systems
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.memory.raw_conversation_store import (
    RawConversationStore,
    RawConversation,
    ConversationMessage,
    ConversationSource
)


class MemoryMigrator:
    """Migrerer minner fra ulike kilder til Qdrant + SQLite"""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.raw_store = RawConversationStore()
        self.mem0 = None
        self.stats = {
            "chatgpt_migrated": 0,
            "chatgpt_skipped": 0,
            "aiki_sessions_migrated": 0,
            "aiki_other_migrated": 0,
            "errors": [],
            "files_moved": []
        }

        # Opprett migrerte_minner mapper
        self._create_migration_dirs()

    def _create_migration_dirs(self):
        """Opprett mappestruktur for migrerte filer"""
        dirs = [
            MIGRERTE / "chatgpt",
            MIGRERTE / "aiki_v3" / "sessions",
            MIGRERTE / "aiki_v3" / "claude",
            MIGRERTE / "aiki_v3" / "collaboration",
            MIGRERTE / "aiki_v3" / "development",
            MIGRERTE / "aiki_v3" / "experiences",
            MIGRERTE / "aiki_v3" / "identity",
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
        logger.info(f"Opprettet migreringsmapper i {MIGRERTE}")

    def _init_mem0(self):
        """Initialiser mem0 for Qdrant"""
        if self.mem0 is not None:
            return

        from mem0 import Memory

        os.environ['OPENAI_API_KEY'] = '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'
        os.environ['OPENAI_BASE_URL'] = 'https://openrouter.ai/api/v1'

        config = {
            'llm': {'provider': 'openai', 'config': {'model': 'openai/gpt-4o-mini'}},
            'embedder': {'provider': 'openai', 'config': {'model': 'text-embedding-3-small', 'embedding_dims': 1536}},
            'vector_store': {'provider': 'qdrant', 'config': {
                'collection_name': 'mem0_memories',
                'host': 'localhost',
                'port': 6333,
                'embedding_model_dims': 1536
            }}
        }
        self.mem0 = Memory.from_config(config)
        logger.info("mem0 initialisert")

    def _extract_chatgpt_messages(self, conversation: Dict) -> List[ConversationMessage]:
        """Ekstraher meldinger fra ChatGPT conversation format"""
        messages = []
        mapping = conversation.get("mapping", {})

        # Finn rot-noden og traverser
        def traverse(node_id: str, visited: set):
            if node_id in visited or node_id not in mapping:
                return
            visited.add(node_id)

            node = mapping[node_id]
            msg_data = node.get("message")

            if msg_data and msg_data.get("content"):
                content = msg_data["content"]
                parts = content.get("parts", [])
                text = " ".join(str(p) for p in parts if isinstance(p, str))

                if text.strip():
                    author = msg_data.get("author", {})
                    role = author.get("role", "unknown")

                    # Normaliser roller
                    if role == "assistant":
                        role = "assistant"
                    elif role == "user":
                        role = "user"
                    else:
                        role = "system"

                    create_time = msg_data.get("create_time")
                    timestamp = None
                    if create_time:
                        try:
                            timestamp = datetime.fromtimestamp(create_time).isoformat()
                        except:
                            pass

                    messages.append(ConversationMessage(
                        role=role,
                        content=text,
                        timestamp=timestamp
                    ))

            # Traverser barn
            for child_id in node.get("children", []):
                traverse(child_id, visited)

        # Start fra root
        for node_id, node in mapping.items():
            if node.get("parent") is None:
                traverse(node_id, set())
                break

        return messages

    def migrate_chatgpt(self, limit: Optional[int] = None) -> int:
        """
        Migrer ChatGPT conversations.json

        Args:
            limit: Maks antall samtaler å migrere (None = alle)

        Returns:
            Antall migrerte samtaler
        """
        if not CHATGPT_JSON.exists():
            logger.error(f"ChatGPT fil ikke funnet: {CHATGPT_JSON}")
            return 0

        logger.info(f"Leser {CHATGPT_JSON}...")
        with open(CHATGPT_JSON, 'r', encoding='utf-8') as f:
            conversations = json.load(f)

        total = len(conversations)
        if limit:
            conversations = conversations[:limit]

        logger.info(f"Migrerer {len(conversations)} av {total} ChatGPT samtaler...")

        self._init_mem0()
        migrated = 0

        for i, conv in enumerate(conversations):
            try:
                title = conv.get("title", "Untitled")
                create_time = conv.get("create_time", 0)

                # Generer session_id fra tittel + tid
                session_id = f"chatgpt-{hashlib.md5(f'{title}{create_time}'.encode()).hexdigest()[:12]}"

                # Ekstraher meldinger
                messages = self._extract_chatgpt_messages(conv)

                if not messages:
                    logger.warning(f"  [{i+1}/{len(conversations)}] Ingen meldinger i '{title}' - hopper over")
                    self.stats["chatgpt_skipped"] += 1
                    continue

                # Opprett RawConversation
                created_at = datetime.fromtimestamp(create_time).isoformat() if create_time else datetime.now().isoformat()

                raw_conv = RawConversation(
                    session_id=session_id,
                    source=ConversationSource.CHATGPT_WEB,
                    messages=messages,
                    created_at=created_at,
                    title=title,
                    tags=["chatgpt", "migrert"],
                    metadata={"original_create_time": create_time}
                )

                if not self.dry_run:
                    # Lagre i SQLite (rå tekst)
                    self.raw_store.store_conversation(raw_conv)

                    # Lagre sammendrag i Qdrant
                    summary = f"ChatGPT samtale: {title}. {len(messages)} meldinger fra {created_at[:10]}."
                    if messages:
                        # Legg til første brukermelding for kontekst
                        user_msgs = [m for m in messages if m.role == "user"]
                        if user_msgs:
                            summary += f" Første spørsmål: {user_msgs[0].content[:200]}..."

                    self.mem0.add(
                        [{"role": "user", "content": summary}],
                        user_id="jovnna",
                        metadata={
                            "source": "chatgpt_migration",
                            "session_id": session_id,
                            "type": "conversation_summary",
                            "original_title": title,
                            "message_count": len(messages)
                        }
                    )

                migrated += 1
                self.stats["chatgpt_migrated"] += 1

                if (i + 1) % 10 == 0:
                    logger.info(f"  [{i+1}/{len(conversations)}] Migrert {migrated} samtaler...")

                # Rate limiting for OpenRouter
                time.sleep(0.5)

            except Exception as e:
                logger.error(f"  Feil ved migrering av samtale {i}: {e}")
                self.stats["errors"].append(f"ChatGPT {i}: {e}")

        logger.info(f"ChatGPT migrering ferdig: {migrated} samtaler")
        return migrated

    def migrate_aiki_sessions(self) -> int:
        """Migrer AIKI v3 session-filer (systemstatus-snapshots)"""
        if not SESSIONS_DIR.exists():
            logger.error(f"Sessions mappe ikke funnet: {SESSIONS_DIR}")
            return 0

        session_files = list(SESSIONS_DIR.glob("*.json"))
        logger.info(f"Migrerer {len(session_files)} AIKI session-filer...")

        self._init_mem0()
        migrated = 0

        for i, session_file in enumerate(session_files):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                session_id = f"aiki-v3-{session_file.stem}"

                # AIKI v3 sessions er systemstatus-snapshots, ikke samtaler
                # Konverter hele JSON til en systemmelding
                if isinstance(data, dict) and "session_id" in data:
                    # Dette er et session-snapshot
                    timestamp = data.get("timestamp", "")
                    services = data.get("services_status", {})
                    files = data.get("file_modifications", [])

                    # Lag en lesbar sammendrag
                    summary_parts = [f"AIKI v3 Session Snapshot: {data.get('session_id', session_file.stem)}"]
                    summary_parts.append(f"Tidspunkt: {timestamp}")

                    if services:
                        running = [k for k, v in services.items() if v.get("status") == "running"]
                        summary_parts.append(f"Kjørende services: {', '.join(running) if running else 'ingen'}")

                    if files:
                        summary_parts.append(f"Modifiserte filer: {len(files)}")

                    content = "\n".join(summary_parts) + "\n\nFull data:\n" + json.dumps(data, indent=2, ensure_ascii=False)

                    messages = [ConversationMessage(
                        role="system",
                        content=content,
                        timestamp=timestamp
                    )]
                else:
                    # Fallback: Behandle som før for andre formater
                    messages = []
                    for entry in data if isinstance(data, list) else [data]:
                        if isinstance(entry, dict):
                            content = entry.get("content") or entry.get("message") or entry.get("text", "")
                            role = entry.get("role", "user")
                            timestamp = entry.get("timestamp") or entry.get("created_at")

                            if content:
                                messages.append(ConversationMessage(
                                    role=role,
                                    content=str(content),
                                    timestamp=timestamp
                                ))

                if not messages:
                    logger.warning(f"  Ingen meldinger i {session_file.name}")
                    continue

                # Hent tidsstempel fra filnavn
                created_at = datetime.now().isoformat()
                if "_" in session_file.stem:
                    try:
                        # Format: aiki_session_20250803_050140
                        date_part = session_file.stem.split("_")[2]
                        if len(date_part) == 8:
                            created_at = f"{date_part[:4]}-{date_part[4:6]}-{date_part[6:8]}T00:00:00"
                    except:
                        pass

                raw_conv = RawConversation(
                    session_id=session_id,
                    source=ConversationSource.AIKI_V3,
                    messages=messages,
                    created_at=created_at,
                    title=f"AIKI Session {session_file.stem}",
                    tags=["aiki-v3", "session", "migrert"]
                )

                if not self.dry_run:
                    self.raw_store.store_conversation(raw_conv)

                    # Lagre i Qdrant
                    summary = f"AIKI v3 session fra {created_at[:10]}. {len(messages)} meldinger."
                    self.mem0.add(
                        [{"role": "user", "content": summary}],
                        user_id="jovnna",
                        metadata={
                            "source": "aiki_v3_migration",
                            "session_id": session_id,
                            "type": "session"
                        }
                    )

                    # Flytt original fil
                    dest = MIGRERTE / "aiki_v3" / "sessions" / session_file.name
                    shutil.copy2(session_file, dest)
                    self.stats["files_moved"].append(str(session_file))

                migrated += 1
                self.stats["aiki_sessions_migrated"] += 1
                time.sleep(0.3)

            except Exception as e:
                logger.error(f"  Feil ved {session_file.name}: {e}")
                self.stats["errors"].append(f"AIKI session {session_file.name}: {e}")

        logger.info(f"AIKI sessions migrering ferdig: {migrated} filer")
        return migrated

    def migrate_aiki_other(self) -> int:
        """Migrer andre AIKI v3 mapper (claude, collaboration, etc.)"""
        other_dirs = ["claude", "collaboration", "development", "experiences", "identity"]
        migrated = 0

        self._init_mem0()

        for dir_name in other_dirs:
            dir_path = AIKI_MEMORY / dir_name
            if not dir_path.exists():
                continue

            json_files = list(dir_path.glob("*.json"))
            logger.info(f"Migrerer {len(json_files)} filer fra {dir_name}/...")

            for json_file in json_files:
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    session_id = f"aiki-v3-{dir_name}-{json_file.stem}"

                    # Konverter til meldinger
                    messages = []
                    if isinstance(data, dict):
                        content = json.dumps(data, ensure_ascii=False, indent=2)
                        messages.append(ConversationMessage(
                            role="system",
                            content=content
                        ))
                    elif isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict):
                                content = item.get("content") or json.dumps(item, ensure_ascii=False)
                                messages.append(ConversationMessage(
                                    role=item.get("role", "system"),
                                    content=content
                                ))

                    if messages:
                        raw_conv = RawConversation(
                            session_id=session_id,
                            source=ConversationSource.AIKI_V3,
                            messages=messages,
                            created_at=datetime.now().isoformat(),
                            title=f"AIKI {dir_name}: {json_file.stem}",
                            tags=["aiki-v3", dir_name, "migrert"]
                        )

                        if not self.dry_run:
                            self.raw_store.store_conversation(raw_conv)

                            summary = f"AIKI v3 {dir_name} data: {json_file.stem}"
                            self.mem0.add(
                                [{"role": "user", "content": summary}],
                                user_id="jovnna",
                                metadata={
                                    "source": "aiki_v3_migration",
                                    "category": dir_name,
                                    "type": "metadata"
                                }
                            )

                            # Flytt original
                            dest = MIGRERTE / "aiki_v3" / dir_name / json_file.name
                            shutil.copy2(json_file, dest)

                        migrated += 1
                        self.stats["aiki_other_migrated"] += 1
                        time.sleep(0.3)

                except Exception as e:
                    logger.error(f"  Feil ved {json_file}: {e}")
                    self.stats["errors"].append(f"{dir_name}/{json_file.name}: {e}")

        return migrated

    def run_full_migration(self, chatgpt_limit: Optional[int] = None):
        """Kjør full migrering av alle kilder"""
        logger.info("=" * 60)
        logger.info("STARTER FULL MINNEMIGRERING")
        logger.info("=" * 60)

        if self.dry_run:
            logger.info("DRY RUN MODE - ingen endringer lagres")

        # 1. ChatGPT
        logger.info("\n[1/3] ChatGPT conversations.json")
        self.migrate_chatgpt(limit=chatgpt_limit)

        # 2. AIKI sessions
        logger.info("\n[2/3] AIKI v3 sessions")
        self.migrate_aiki_sessions()

        # 3. Andre AIKI mapper
        logger.info("\n[3/3] AIKI v3 andre mapper")
        self.migrate_aiki_other()

        # Rapport
        self._print_report()

    def _print_report(self):
        """Skriv ut migrasjonsrapport"""
        logger.info("\n" + "=" * 60)
        logger.info("MIGRASJONSRAPPORT")
        logger.info("=" * 60)
        logger.info(f"ChatGPT samtaler migrert:  {self.stats['chatgpt_migrated']}")
        logger.info(f"ChatGPT samtaler hoppet:   {self.stats['chatgpt_skipped']}")
        logger.info(f"AIKI sessions migrert:     {self.stats['aiki_sessions_migrated']}")
        logger.info(f"AIKI andre filer migrert:  {self.stats['aiki_other_migrated']}")
        logger.info(f"Filer flyttet til backup:  {len(self.stats['files_moved'])}")
        logger.info(f"Feil:                      {len(self.stats['errors'])}")

        if self.stats["errors"]:
            logger.info("\nFeil detaljer:")
            for err in self.stats["errors"][:10]:
                logger.info(f"  - {err}")

        # SQLite statistikk
        stats = self.raw_store.get_stats()
        logger.info(f"\nSQLite status:")
        logger.info(f"  Samtaler: {stats['total_conversations']}")
        logger.info(f"  Meldinger: {stats['total_messages']}")
        logger.info(f"  Database: {stats['db_size_mb']:.2f} MB")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="AIKI Memory Migration")
    parser.add_argument("--dry-run", action="store_true", help="Simuler uten å lagre")
    parser.add_argument("--chatgpt-only", action="store_true", help="Kun ChatGPT")
    parser.add_argument("--limit", type=int, default=None, help="Maks ChatGPT samtaler")
    parser.add_argument("--test", action="store_true", help="Test med 5 samtaler")

    args = parser.parse_args()

    migrator = MemoryMigrator(dry_run=args.dry_run)

    if args.test:
        migrator.migrate_chatgpt(limit=5)
    elif args.chatgpt_only:
        migrator.migrate_chatgpt(limit=args.limit)
    else:
        migrator.run_full_migration(chatgpt_limit=args.limit)
