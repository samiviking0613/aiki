#!/usr/bin/env python3
"""
AIKI Raw Conversation Store

Lagrer EKSAKT samtaledata som aldri komprimeres eller reformuleres.
Løser problemet: "Hva sa jeg NØYAKTIG om bestefar for 2 år siden?"

Arkitektur:
1. SQLite med FTS5 for full-text search
2. zstd komprimering (~90% reduksjon)
3. Qdrant-pekere: session_id linker til eksakt tekst
4. Støtter dato-filtrering

Hybrid-søk flyt:
  Bruker: "Hva sa jeg om bestefar?"
    ↓
  1. Qdrant embedding-søk → finner relevante session_ids
    ↓
  2. SQLite full-text search → henter EKSAKT tekst
    ↓
  Svar: Du sa: "Bestefar jobbet på ubåt under kald krig"

#version: 1.0.0
#created: 2025-11-23
#author: Claude (AIKI Memory System)
"""

import sqlite3
import zstandard as zstd
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ConversationSource(Enum):
    """Kilde for samtale"""
    CLAUDE_CODE = "claude_code"
    CLAUDE_DESKTOP = "claude_desktop"
    CHATGPT_WEB = "chatgpt_web"
    CHATGPT_API = "chatgpt_api"
    AIKI_ULTIMATE = "aiki_ultimate"
    AIKI_V3 = "aiki_v3"
    MANUAL = "manual"
    IMPORT = "import"


@dataclass
class ConversationMessage:
    """En enkelt melding i en samtale"""
    role: str  # user, assistant, system
    content: str
    timestamp: Optional[str] = None
    metadata: Optional[Dict] = None


@dataclass
class RawConversation:
    """Komplett rå samtale med alle meldinger"""
    session_id: str
    source: ConversationSource
    messages: List[ConversationMessage]
    created_at: str
    title: Optional[str] = None
    tags: Optional[List[str]] = None
    qdrant_ids: Optional[List[str]] = None  # Pekere til Qdrant minner
    metadata: Optional[Dict] = None


class RawConversationStore:
    """
    SQLite-basert lagring av rå samtaledata.

    Nøkkelfunksjoner:
    - FTS5 full-text search for eksakt tekst-søk
    - zstd komprimering (~90% plassbesparelse)
    - Dato-range queries
    - Linker til Qdrant via session_id
    """

    def __init__(self, db_path: str = None):
        """
        Initialiser raw conversation store.

        Args:
            db_path: Sti til SQLite database. Default: ~/aiki/data/raw_conversations.db
        """
        if db_path is None:
            db_path = str(Path.home() / "aiki" / "data" / "raw_conversations.db")

        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # zstd kompressor for effektiv lagring
        self.compressor = zstd.ZstdCompressor(level=3)
        self.decompressor = zstd.ZstdDecompressor()

        self._init_db()

    def _init_db(self):
        """Opprett database-tabeller og FTS5 indeks"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # Hovedtabell for samtaler
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                session_id TEXT PRIMARY KEY,
                source TEXT NOT NULL,
                title TEXT,
                tags TEXT,  -- JSON array
                qdrant_ids TEXT,  -- JSON array med pekere til Qdrant
                metadata TEXT,  -- JSON
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                message_count INTEGER DEFAULT 0
            );
        """)

        # Meldinger - komprimert lagring
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                message_index INTEGER NOT NULL,
                role TEXT NOT NULL,
                content_compressed BLOB NOT NULL,  -- zstd komprimert
                content_hash TEXT NOT NULL,  -- For deduplisering
                timestamp TEXT,
                metadata TEXT,  -- JSON
                created_at TEXT NOT NULL,

                FOREIGN KEY (session_id) REFERENCES conversations(session_id),
                UNIQUE(session_id, message_index)
            );
        """)

        # FTS5 virtuell tabell for full-text search
        # Note: Standalone FTS table (not contentless) for enklere queries
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS messages_fts USING fts5(
                session_id,
                role,
                content
            );
        """)

        # Indekser for ytelse
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_session_id
            ON messages(session_id);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_conversations_created_at
            ON conversations(created_at);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_conversations_source
            ON conversations(source);
        """)

        # Tabell for Qdrant->Session mapping
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS qdrant_mappings (
                qdrant_id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                message_index INTEGER,  -- Null = hele samtalen
                summary TEXT,  -- Hva Qdrant-minnet handler om
                created_at TEXT NOT NULL,

                FOREIGN KEY (session_id) REFERENCES conversations(session_id)
            );
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_qdrant_mappings_session
            ON qdrant_mappings(session_id);
        """)

        conn.commit()
        conn.close()

        logger.info(f"Database initialized: {self.db_path}")

    def _compress(self, text: str) -> bytes:
        """Komprimer tekst med zstd"""
        return self.compressor.compress(text.encode('utf-8'))

    def _decompress(self, data: bytes) -> str:
        """Dekomprimer zstd data"""
        return self.decompressor.decompress(data).decode('utf-8')

    def _content_hash(self, content: str) -> str:
        """Generer hash for deduplisering"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]

    def store_conversation(self, conversation: RawConversation) -> bool:
        """
        Lagre en komplett samtale.

        Args:
            conversation: RawConversation objekt

        Returns:
            bool: True hvis vellykket
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        try:
            now = datetime.now().isoformat()

            # Sjekk om samtale allerede eksisterer
            cursor.execute(
                "SELECT session_id FROM conversations WHERE session_id = ?",
                (conversation.session_id,)
            )
            exists = cursor.fetchone() is not None

            if exists:
                # Oppdater eksisterende
                cursor.execute("""
                    UPDATE conversations
                    SET title = ?, tags = ?, qdrant_ids = ?, metadata = ?,
                        updated_at = ?, message_count = ?
                    WHERE session_id = ?
                """, (
                    conversation.title,
                    json.dumps(conversation.tags) if conversation.tags else None,
                    json.dumps(conversation.qdrant_ids) if conversation.qdrant_ids else None,
                    json.dumps(conversation.metadata) if conversation.metadata else None,
                    now,
                    len(conversation.messages),
                    conversation.session_id
                ))

                # Slett gamle meldinger og FTS data
                cursor.execute(
                    "DELETE FROM messages WHERE session_id = ?",
                    (conversation.session_id,)
                )
                cursor.execute(
                    "DELETE FROM messages_fts WHERE session_id = ?",
                    (conversation.session_id,)
                )
            else:
                # Ny samtale
                cursor.execute("""
                    INSERT INTO conversations
                    (session_id, source, title, tags, qdrant_ids, metadata,
                     created_at, updated_at, message_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    conversation.session_id,
                    conversation.source.value if isinstance(conversation.source, ConversationSource) else conversation.source,
                    conversation.title,
                    json.dumps(conversation.tags) if conversation.tags else None,
                    json.dumps(conversation.qdrant_ids) if conversation.qdrant_ids else None,
                    json.dumps(conversation.metadata) if conversation.metadata else None,
                    conversation.created_at,
                    now,
                    len(conversation.messages)
                ))

            # Lagre meldinger
            for idx, msg in enumerate(conversation.messages):
                compressed = self._compress(msg.content)
                content_hash = self._content_hash(msg.content)

                cursor.execute("""
                    INSERT INTO messages
                    (session_id, message_index, role, content_compressed,
                     content_hash, timestamp, metadata, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    conversation.session_id,
                    idx,
                    msg.role,
                    compressed,
                    content_hash,
                    msg.timestamp,
                    json.dumps(msg.metadata) if msg.metadata else None,
                    now
                ))

                # Legg også til i FTS-tabellen for full-text søk
                cursor.execute("""
                    INSERT INTO messages_fts (session_id, role, content)
                    VALUES (?, ?, ?)
                """, (conversation.session_id, msg.role, msg.content))

            conn.commit()
            logger.info(f"Stored conversation {conversation.session_id} with {len(conversation.messages)} messages")
            return True

        except Exception as e:
            logger.error(f"Error storing conversation: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def link_qdrant_memory(
        self,
        qdrant_id: str,
        session_id: str,
        message_index: Optional[int] = None,
        summary: Optional[str] = None
    ) -> bool:
        """
        Link et Qdrant minne til en samtale.

        Args:
            qdrant_id: ID fra Qdrant
            session_id: Session ID i raw store
            message_index: Spesifikk melding (None = hele samtalen)
            summary: Kort beskrivelse av hva minnet handler om

        Returns:
            bool: True hvis vellykket
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT OR REPLACE INTO qdrant_mappings
                (qdrant_id, session_id, message_index, summary, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                qdrant_id,
                session_id,
                message_index,
                summary,
                datetime.now().isoformat()
            ))

            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error linking Qdrant memory: {e}")
            return False
        finally:
            conn.close()

    def get_conversation(self, session_id: str) -> Optional[RawConversation]:
        """
        Hent en komplett samtale med alle meldinger.

        Args:
            session_id: Session ID

        Returns:
            RawConversation eller None
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        try:
            # Hent samtale-metadata
            cursor.execute("""
                SELECT source, title, tags, qdrant_ids, metadata, created_at
                FROM conversations WHERE session_id = ?
            """, (session_id,))

            row = cursor.fetchone()
            if not row:
                return None

            source, title, tags_json, qdrant_ids_json, metadata_json, created_at = row

            # Hent meldinger
            cursor.execute("""
                SELECT role, content_compressed, timestamp, metadata
                FROM messages
                WHERE session_id = ?
                ORDER BY message_index
            """, (session_id,))

            messages = []
            for role, content_compressed, timestamp, msg_metadata_json in cursor.fetchall():
                content = self._decompress(content_compressed)
                messages.append(ConversationMessage(
                    role=role,
                    content=content,
                    timestamp=timestamp,
                    metadata=json.loads(msg_metadata_json) if msg_metadata_json else None
                ))

            return RawConversation(
                session_id=session_id,
                source=ConversationSource(source) if source in [e.value for e in ConversationSource] else source,
                messages=messages,
                created_at=created_at,
                title=title,
                tags=json.loads(tags_json) if tags_json else None,
                qdrant_ids=json.loads(qdrant_ids_json) if qdrant_ids_json else None,
                metadata=json.loads(metadata_json) if metadata_json else None
            )

        except Exception as e:
            logger.error(f"Error getting conversation: {e}")
            return None
        finally:
            conn.close()

    def search_exact_text(
        self,
        query: str,
        role: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        source: Optional[ConversationSource] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Søk etter eksakt tekst via FTS5.

        Args:
            query: Søketekst (støtter FTS5 syntax: "word1 word2", word1 OR word2, etc.)
            role: Filtrer på rolle (user, assistant)
            date_from: Fra dato (ISO format)
            date_to: Til dato (ISO format)
            source: Filtrer på kilde
            limit: Maks antall resultater

        Returns:
            Liste med treff: [{"session_id", "role", "content", "snippet", "rank"}]
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        results = []

        try:
            # Bygg FTS5 query
            # Escape spesialtegn for sikkerhet
            safe_query = query.replace('"', '""')

            # Først søk i FTS for å finne matchende rader
            sql = """
                SELECT
                    fts.session_id,
                    fts.role,
                    fts.content,
                    c.title,
                    c.source,
                    c.created_at,
                    snippet(messages_fts, 2, '>>>', '<<<', '...', 32) as snippet,
                    bm25(messages_fts) as rank
                FROM messages_fts fts
                JOIN conversations c ON fts.session_id = c.session_id
                WHERE messages_fts MATCH ?
            """
            params = [safe_query]

            if role:
                sql += " AND fts.role = ?"
                params.append(role)

            if source:
                sql += " AND c.source = ?"
                params.append(source.value if isinstance(source, ConversationSource) else source)

            if date_from:
                sql += " AND c.created_at >= ?"
                params.append(date_from)

            if date_to:
                sql += " AND c.created_at <= ?"
                params.append(date_to)

            sql += " ORDER BY rank LIMIT ?"
            params.append(limit)

            cursor.execute(sql, params)

            for row in cursor.fetchall():
                (session_id, msg_role, content, title, src, created_at, snippet, rank) = row

                results.append({
                    "session_id": session_id,
                    "role": msg_role,
                    "content": content,  # Allerede ukomprimert fra FTS
                    "conversation_title": title,
                    "source": src,
                    "created_at": created_at,
                    "snippet": snippet,
                    "rank": rank
                })

        except Exception as e:
            logger.error(f"FTS search error: {e}")
        finally:
            conn.close()

        return results

    def get_sessions_by_qdrant_ids(
        self,
        qdrant_ids: List[str]
    ) -> List[RawConversation]:
        """
        Hent samtaler basert på Qdrant IDs.
        Dette er broen mellom Qdrant semantisk søk og eksakt tekst.

        Args:
            qdrant_ids: Liste med Qdrant memory IDs

        Returns:
            Liste med RawConversation objekter
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        conversations = []

        try:
            # Finn session_ids fra mappings
            placeholders = ','.join('?' * len(qdrant_ids))
            cursor.execute(f"""
                SELECT DISTINCT session_id
                FROM qdrant_mappings
                WHERE qdrant_id IN ({placeholders})
            """, qdrant_ids)

            session_ids = [row[0] for row in cursor.fetchall()]

            # Hent samtaler
            for session_id in session_ids:
                conv = self.get_conversation(session_id)
                if conv:
                    conversations.append(conv)

        except Exception as e:
            logger.error(f"Error getting sessions by Qdrant IDs: {e}")
        finally:
            conn.close()

        return conversations

    def get_stats(self) -> Dict[str, Any]:
        """Hent statistikk om lagret data"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        stats = {}

        try:
            # Antall samtaler
            cursor.execute("SELECT COUNT(*) FROM conversations")
            stats["total_conversations"] = cursor.fetchone()[0]

            # Antall meldinger
            cursor.execute("SELECT COUNT(*) FROM messages")
            stats["total_messages"] = cursor.fetchone()[0]

            # Etter kilde
            cursor.execute("""
                SELECT source, COUNT(*)
                FROM conversations
                GROUP BY source
            """)
            stats["by_source"] = dict(cursor.fetchall())

            # Antall Qdrant mappings
            cursor.execute("SELECT COUNT(*) FROM qdrant_mappings")
            stats["qdrant_mappings"] = cursor.fetchone()[0]

            # Database størrelse
            stats["db_size_mb"] = self.db_path.stat().st_size / (1024 * 1024)

            # Dato-range
            cursor.execute("""
                SELECT MIN(created_at), MAX(created_at)
                FROM conversations
            """)
            min_date, max_date = cursor.fetchone()
            stats["date_range"] = {"from": min_date, "to": max_date}

        except Exception as e:
            logger.error(f"Error getting stats: {e}")
        finally:
            conn.close()

        return stats

    def list_conversations(
        self,
        source: Optional[ConversationSource] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List samtaler med filtrering.

        Returns:
            Liste med samtale-metadata (uten meldinger)
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        results = []

        try:
            sql = """
                SELECT session_id, source, title, tags, created_at,
                       updated_at, message_count
                FROM conversations
                WHERE 1=1
            """
            params = []

            if source:
                sql += " AND source = ?"
                params.append(source.value if isinstance(source, ConversationSource) else source)

            if date_from:
                sql += " AND created_at >= ?"
                params.append(date_from)

            if date_to:
                sql += " AND created_at <= ?"
                params.append(date_to)

            sql += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            cursor.execute(sql, params)

            for row in cursor.fetchall():
                session_id, src, title, tags_json, created_at, updated_at, msg_count = row
                results.append({
                    "session_id": session_id,
                    "source": src,
                    "title": title,
                    "tags": json.loads(tags_json) if tags_json else [],
                    "created_at": created_at,
                    "updated_at": updated_at,
                    "message_count": msg_count
                })

        except Exception as e:
            logger.error(f"Error listing conversations: {e}")
        finally:
            conn.close()

        return results


# ============================================================================
# Hybrid Search: Qdrant + SQLite
# ============================================================================

async def hybrid_search(
    query: str,
    user_id: str = "jovnna",
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    limit: int = 5
) -> List[Dict[str, Any]]:
    """
    Hybrid søk: Qdrant semantisk → SQLite eksakt tekst.

    Flyt:
    1. Søk i Qdrant for semantisk match
    2. Hent session_ids fra resultatene
    3. Hent eksakt tekst fra SQLite

    Args:
        query: Søketekst
        user_id: Bruker-ID for Qdrant
        date_from: Fra dato
        date_to: Til dato
        limit: Maks resultater

    Returns:
        Liste med resultater som inkluderer EKSAKT tekst
    """
    from mem0 import Memory
    import os

    # Konfigurer mem0 med host/port for å unngå permission issues
    os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY', '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')
    os.environ['OPENAI_BASE_URL'] = os.getenv('OPENAI_BASE_URL', 'https://openrouter.ai/api/v1')

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

    store = RawConversationStore()

    try:
        m = Memory.from_config(config)

        # Steg 1: Semantisk søk i Qdrant
        qdrant_results = m.search(query, user_id=user_id, limit=limit * 2)

        if not qdrant_results or 'results' not in qdrant_results:
            # Fallback til ren FTS søk
            return store.search_exact_text(query, date_from=date_from, date_to=date_to, limit=limit)

        # Steg 2: Samle session_ids og qdrant_ids
        qdrant_ids = []
        for result in qdrant_results.get('results', []):
            if result and 'id' in result:
                qdrant_ids.append(result['id'])

        # Steg 3: Hent eksakt tekst fra SQLite via mappings
        conversations = store.get_sessions_by_qdrant_ids(qdrant_ids)

        if conversations:
            # Returner med eksakt tekst
            results = []
            for conv in conversations:
                for msg in conv.messages:
                    if query.lower() in msg.content.lower():
                        results.append({
                            "session_id": conv.session_id,
                            "source": conv.source.value if isinstance(conv.source, ConversationSource) else conv.source,
                            "title": conv.title,
                            "role": msg.role,
                            "exact_text": msg.content,
                            "created_at": conv.created_at,
                            "match_type": "hybrid_qdrant_sqlite"
                        })
                        if len(results) >= limit:
                            break
                if len(results) >= limit:
                    break
            if results:
                return results

    except Exception as e:
        logger.warning(f"Qdrant search failed, falling back to FTS: {e}")

    # Fallback: Direkte FTS søk
    return store.search_exact_text(query, date_from=date_from, date_to=date_to, limit=limit)


def hybrid_search_sync(
    query: str,
    user_id: str = "jovnna",
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    limit: int = 5
) -> List[Dict[str, Any]]:
    """
    Synkron versjon av hybrid_search for enklere bruk.
    """
    import asyncio
    return asyncio.run(hybrid_search(query, user_id, date_from, date_to, limit))


# ============================================================================
# CLI for testing
# ============================================================================

if __name__ == "__main__":
    import sys

    store = RawConversationStore()

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python raw_conversation_store.py stats")
        print("  python raw_conversation_store.py search <query>")
        print("  python raw_conversation_store.py list [limit]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "stats":
        stats = store.get_stats()
        print("\n📊 Raw Conversation Store Statistics:")
        print(f"   Conversations: {stats.get('total_conversations', 0)}")
        print(f"   Messages: {stats.get('total_messages', 0)}")
        print(f"   Qdrant mappings: {stats.get('qdrant_mappings', 0)}")
        print(f"   Database size: {stats.get('db_size_mb', 0):.2f} MB")
        if stats.get('date_range'):
            print(f"   Date range: {stats['date_range']['from']} → {stats['date_range']['to']}")
        print(f"\n   By source: {stats.get('by_source', {})}")

    elif cmd == "search" and len(sys.argv) > 2:
        query = ' '.join(sys.argv[2:])
        print(f"\n🔍 Searching for: '{query}'")
        results = store.search_exact_text(query, limit=10)

        if not results:
            print("   No results found")
        else:
            for i, r in enumerate(results, 1):
                print(f"\n{i}. [{r['source']}] {r.get('conversation_title', 'Untitled')}")
                print(f"   Role: {r['role']}")
                print(f"   Snippet: {r['snippet']}")
                print(f"   Date: {r['created_at']}")

    elif cmd == "list":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        convs = store.list_conversations(limit=limit)

        print(f"\n📝 Last {len(convs)} conversations:")
        for c in convs:
            print(f"   [{c['source']}] {c.get('title', c['session_id'][:20])} - {c['message_count']} msgs ({c['created_at'][:10]})")

    else:
        print(f"Unknown command: {cmd}")
