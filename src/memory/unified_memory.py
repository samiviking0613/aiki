"""
AIKI Unified Memory System

Samler alle minne-operasjoner i ett API med async graf-oppdatering.
Lagring føles umiddelbar - graf oppdateres i bakgrunnen.

Usage:
    from src.memory.unified_memory import UnifiedMemory

    memory = UnifiedMemory()

    # Lagre samtale (graf oppdateres automatisk i bakgrunnen)
    await memory.store_conversation(conversation)

    # Søk på tre måter
    results = await memory.search("AIKI arkitektur")  # Hybrid: Qdrant + SQLite
    results = memory.search_graph("ADHD")  # Graf: Topics, Projects
    results = memory.search_exact("hva sa jeg")  # SQLite FTS5
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from .raw_conversation_store import (
    RawConversationStore,
    RawConversation,
    ConversationMessage,
    ConversationSource,
    hybrid_search
)
from .graph_memory import MemoryGraph, get_memory_graph
from .keyword_extractor import (
    KeywordExtractor,
    get_keyword_extractor,
    extract_keywords
)

logger = logging.getLogger(__name__)


class UnifiedMemory:
    """
    Unified API for alle minne-operasjoner.
    Automatisk graf-oppdatering i bakgrunnen.

    Args:
        use_llm_extraction: Bruk LLM for smart keyword-ekstraksjon.
            True = oppdager nye topics/projects automatisk (koster ~$0.001/kall)
            False = kun hardkodede keywords (gratis, raskere)
    """

    def __init__(self, use_llm_extraction: bool = False):
        self.raw_store = RawConversationStore()
        self._graph: Optional[MemoryGraph] = None
        self._executor = ThreadPoolExecutor(max_workers=2)
        self._pending_graph_updates: List[str] = []
        self._keyword_extractor = get_keyword_extractor(use_llm=use_llm_extraction)
        self.use_llm_extraction = use_llm_extraction

    @property
    def graph(self) -> MemoryGraph:
        """Lazy-load graf"""
        if self._graph is None:
            self._graph = get_memory_graph()
        return self._graph

    # ==================== STORE ====================

    async def store_conversation(
        self,
        conversation: RawConversation,
        update_graph: bool = True
    ) -> str:
        """
        Lagre samtale i SQLite + oppdater graf i bakgrunnen.

        Returns:
            session_id
        """
        # 1. Synkron lagring til SQLite (rask)
        success = self.raw_store.store_conversation(conversation)

        if not success:
            logger.error(f"Feil ved lagring av {conversation.session_id}")
            return ""

        # 2. Async graf-oppdatering (i bakgrunnen)
        if update_graph:
            asyncio.create_task(
                self._update_graph_async(conversation)
            )

        return conversation.session_id

    async def _update_graph_async(self, conversation: RawConversation):
        """Oppdater graf i bakgrunnen"""
        try:
            # Kjør i thread pool for å ikke blokkere
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self._executor,
                self._update_graph_sync,
                conversation
            )
            logger.debug(f"Graf oppdatert for {conversation.session_id}")
        except Exception as e:
            logger.error(f"Graf-oppdatering feilet: {e}")

    def _update_graph_sync(self, conversation: RawConversation):
        """Synkron graf-oppdatering (kjøres i thread)"""
        session_id = conversation.session_id

        # Opprett Conversation-node
        self.graph.create_conversation_node(
            session_id=session_id,
            title=conversation.title or "Untitled",
            source=conversation.source.value,
            created_at=conversation.created_at,
            message_count=len(conversation.messages)
        )

        # Ekstraher keywords fra innholdet
        full_text = " ".join([m.content for m in conversation.messages[:10]])
        full_text += " " + (conversation.title or "")

        # Bruk smart ekstraksjon (fast path først, LLM kun ved behov)
        projects, topics = self._keyword_extractor.extract(
            full_text,
            use_llm_if_no_matches=self.use_llm_extraction
        )

        # Link til prosjekter
        for project in projects:
            self.graph.link_conversation_to_project(session_id, project)

        # Link til topics
        for topic in topics:
            self.graph.link_conversation_to_topic(session_id, topic)

        if projects or topics:
            logger.debug(f"Graf-linket {session_id}: {len(projects)} projects, {len(topics)} topics")

    def store_conversation_sync(
        self,
        conversation: RawConversation,
        update_graph: bool = True
    ) -> str:
        """Synkron versjon for ikke-async kontekst"""
        success = self.raw_store.store_conversation(conversation)

        if success and update_graph:
            self._update_graph_sync(conversation)

        return conversation.session_id if success else ""

    # ==================== SEARCH ====================

    async def search(
        self,
        query: str,
        limit: int = 10,
        user_id: str = "jovnna"
    ) -> List[Dict]:
        """
        Hybrid søk: Qdrant semantisk → SQLite eksakt tekst.
        """
        return await hybrid_search(query, user_id=user_id, limit=limit)

    def search_sync(
        self,
        query: str,
        limit: int = 10
    ) -> List[Dict]:
        """Synkron versjon av hybrid søk"""
        from .raw_conversation_store import hybrid_search_sync
        return hybrid_search_sync(query, limit=limit)

    def search_exact(
        self,
        query: str,
        limit: int = 20
    ) -> List[Dict]:
        """SQLite FTS5 eksakt tekst-søk"""
        return self.raw_store.search_exact_text(query, limit=limit)

    def search_graph_topics(
        self,
        topic: str,
        limit: int = 20
    ) -> List[Dict]:
        """Finn samtaler om et topic via graf"""
        return self.graph.get_conversations_by_topic(topic, limit=limit)

    def search_graph_project(
        self,
        project: str,
        limit: int = 50
    ) -> List[Dict]:
        """Finn samtaler tilknyttet et prosjekt"""
        return self.graph.get_project_conversations(project)[:limit]

    def find_related(
        self,
        session_id: str,
        max_depth: int = 2,
        limit: int = 10
    ) -> List[Dict]:
        """Finn relaterte samtaler via graf"""
        return self.graph.get_related_conversations(
            session_id, max_depth=max_depth, limit=limit
        )

    def get_conversation_context(self, session_id: str) -> Dict:
        """Hent full kontekst for en samtale (topics, entities, related)"""
        return self.graph.get_conversation_context(session_id)

    # ==================== STATS ====================

    def get_stats(self) -> Dict:
        """Hent statistikk fra alle systemer"""
        sqlite_stats = self.raw_store.get_stats()
        graph_stats = self.graph.get_stats()

        return {
            "sqlite": sqlite_stats,
            "graph": graph_stats,
            "total_conversations": sqlite_stats["total_conversations"],
            "total_messages": sqlite_stats["total_messages"],
            "graph_nodes": graph_stats["total_nodes"],
            "graph_edges": graph_stats["total_edges"]
        }

    def close(self):
        """Lukk tilkoblinger"""
        self._executor.shutdown(wait=False)
        if self._graph:
            self._graph.close()


# ==================== SINGLETON ====================

_unified_memory: Optional[UnifiedMemory] = None

def get_unified_memory() -> UnifiedMemory:
    """Singleton for UnifiedMemory"""
    global _unified_memory
    if _unified_memory is None:
        _unified_memory = UnifiedMemory()
    return _unified_memory


# ==================== CONVENIENCE FUNCTIONS ====================

async def store_memory(
    content: str,
    source: str = "claude_code",
    title: Optional[str] = None
) -> str:
    """
    Enkel funksjon for å lagre et minne.

    Usage:
        session_id = await store_memory("Jovnna foretrekker visuelle forklaringer")
    """
    import hashlib
    from datetime import datetime

    session_id = f"{source}-{hashlib.md5(content[:100].encode()).hexdigest()[:12]}"

    conversation = RawConversation(
        session_id=session_id,
        source=ConversationSource(source) if source in [s.value for s in ConversationSource] else ConversationSource.CLAUDE_CODE,
        messages=[ConversationMessage(role="user", content=content)],
        created_at=datetime.now().isoformat(),
        title=title
    )

    memory = get_unified_memory()
    return await memory.store_conversation(conversation)


def store_memory_sync(
    content: str,
    source: str = "claude_code",
    title: Optional[str] = None
) -> str:
    """Synkron versjon av store_memory"""
    import hashlib
    from datetime import datetime

    session_id = f"{source}-{hashlib.md5(content[:100].encode()).hexdigest()[:12]}"

    conversation = RawConversation(
        session_id=session_id,
        source=ConversationSource(source) if source in [s.value for s in ConversationSource] else ConversationSource.CLAUDE_CODE,
        messages=[ConversationMessage(role="user", content=content)],
        created_at=datetime.now().isoformat(),
        title=title
    )

    memory = get_unified_memory()
    return memory.store_conversation_sync(conversation)
