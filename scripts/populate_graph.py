#!/usr/bin/env python3
"""
Populer Neo4j graf fra SQLite raw_conversations.

Oppretter:
- Conversation-noder for hver samtale
- Topic-noder basert på keywords
- Entity-noder for personer, prosjekter, etc.
- Edges mellom relaterte samtaler
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import re
import logging
import sqlite3
from collections import Counter

from src.memory.raw_conversation_store import RawConversationStore
from src.memory.graph_memory import MemoryGraph, RelationType

# Database path
DB_PATH = Path(__file__).parent.parent / "data" / "raw_conversations.db"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Kjente topics og entities å ekstrahere
KNOWN_PROJECTS = [
    "AIKI", "AIKI-HOME", "AIKI Ultimate", "AIKI Prime",
    "MITM proxy", "mem0", "Qdrant", "Neo4j"
]

KNOWN_TOPICS = [
    "ADHD", "minne", "memory", "arkitektur", "architecture",
    "WiFi", "nettverk", "network", "proxy", "VPN",
    "TikTok", "YouTube", "accountability",
    "lån", "bank", "Innovasjon Norge",
    "traktor", "bil", "OBD2", "CAN bus"
]

def extract_keywords(text: str) -> list:
    """Enkel keyword-ekstraksjon"""
    # Normaliser
    text_lower = text.lower()

    found_projects = []
    for proj in KNOWN_PROJECTS:
        if proj.lower() in text_lower:
            found_projects.append(proj)

    found_topics = []
    for topic in KNOWN_TOPICS:
        if topic.lower() in text_lower:
            found_topics.append(topic)

    return found_projects, found_topics


def populate_graph():
    """Hovedfunksjon for å populere grafen"""
    graph = MemoryGraph()

    # Åpne SQLite direkte
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    # Hent antall samtaler
    cursor.execute("SELECT COUNT(*) FROM conversations")
    total = cursor.fetchone()[0]

    logger.info(f"Starter populering av graf med {total} samtaler...")

    # Hent alle samtaler
    cursor.execute("""
        SELECT session_id, source, title, created_at
        FROM conversations
        ORDER BY created_at
    """)
    conversations = cursor.fetchall()

    created_nodes = 0
    created_edges = 0
    previous_session = None

    for i, (session_id, source, title, created_at) in enumerate(conversations):
        # Opprett Conversation-node
        graph.create_conversation_node(
            session_id=session_id,
            title=title or "Untitled",
            source=source,
            created_at=created_at,
            message_count=0  # Kan utvides
        )
        created_nodes += 1

        # Hent meldingsinnhold for keyword-ekstraksjon (fra FTS-tabell)
        cursor.execute("""
            SELECT content FROM messages_fts
            WHERE session_id = ?
            LIMIT 10
        """, (session_id,))
        messages = [row[0] for row in cursor.fetchall()]
        full_text = " ".join(messages) + " " + (title or "")

        # Ekstraher keywords
        projects, topics = extract_keywords(full_text)

        # Link til prosjekter
        for project in projects:
            if graph.link_conversation_to_project(session_id, project):
                created_edges += 1

        # Link til topics
        for topic in topics:
            if graph.link_conversation_to_topic(session_id, topic):
                created_edges += 1

        # Temporal linking (samtaler i rekkefølge)
        if previous_session and source == conversations[i-1][1]:  # Same source
            if graph.link_conversations_temporal(previous_session, session_id):
                created_edges += 1

        previous_session = session_id

        if (i + 1) % 20 == 0:
            logger.info(f"  [{i+1}/{total}] {created_nodes} noder, {created_edges} edges...")

    # Hent statistikk
    graph_stats = graph.get_stats()

    logger.info("")
    logger.info("=" * 50)
    logger.info("GRAF POPULERING FULLFØRT")
    logger.info("=" * 50)
    logger.info(f"Noder opprettet: {created_nodes}")
    logger.info(f"Edges opprettet: {created_edges}")
    logger.info(f"Graf statistikk: {graph_stats}")

    graph.close()
    return created_nodes, created_edges


if __name__ == "__main__":
    populate_graph()
