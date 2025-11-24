# AIKI Memory System
"""
Hierarchical, token-efficient memory system with 10 memory types + raw storage + graph.

Usage:
    from src.memory import (
        # Unified API (ANBEFALT)
        UnifiedMemory,
        get_unified_memory,
        store_memory,
        store_memory_sync,

        # Legacy imports
        HierarchicalMemory,
        get_sensory_context,
        get_efficient_context,
        RawConversationStore,
        hybrid_search
    )

    # ANBEFALT: Unified Memory med auto graf-oppdatering
    memory = get_unified_memory()
    await memory.store_conversation(conversation)  # Graf oppdateres automatisk i bakgrunnen
    results = await memory.search("AIKI arkitektur")  # Hybrid søk
    related = memory.find_related(session_id)  # Graf-søk

    # Enkel lagring
    session_id = await store_memory("Jovnna foretrekker visuelle forklaringer")

    # Quick sensory lookup (instant, 0 API tokens)
    sensory = get_sensory_context("jeg føler meg kald")

    # Hybrid search: Qdrant semantic → SQLite exact text
    results = await hybrid_search("hva sa jeg om bestefar?")

Memory Types (10/10 = 100% human coverage):
1. Semantic - Facts, concepts (mem0 vector search)
2. Episodic - Sessions, events (run_id, metadata)
3. Procedural - Skills, workflows (store_procedural_memory)
4. Emotional - Feelings, moods (store_emotional_memory)
5. Graph/Associative - Relations (Neo4j)
6. Prospective - Future plans (prospective_memory_system)
7. Working Memory - Active context (session state)
8. AI-to-AI - Inter-AI messaging (store_ai_message)
9. Historical Patterns - Pattern recognition (learning loop)
10. Sensory - Physical sensation→meaning mappings

Raw Storage (supplement):
- SQLite + FTS5 for exact text retrieval
- zstd compression (~90% reduction)
- Hybrid search: Qdrant → SQLite
"""

from .hierarchical_memory import (
    HierarchicalMemory,
    SensoryCategory,
    SensoryMemory,
    SENSORY_MAPPINGS,
    store_sensory_memory,
    get_sensory_context,
    get_efficient_context,
    initialize_sensory_memories
)

from .raw_conversation_store import (
    RawConversationStore,
    RawConversation,
    ConversationMessage,
    ConversationSource,
    hybrid_search,
    hybrid_search_sync
)

from .unified_memory import (
    UnifiedMemory,
    get_unified_memory,
    store_memory,
    store_memory_sync
)

from .graph_memory import (
    MemoryGraph,
    get_memory_graph,
    find_related_memories,
    search_by_topic,
    search_by_entity
)

__all__ = [
    # Unified Memory (ANBEFALT)
    'UnifiedMemory',
    'get_unified_memory',
    'store_memory',
    'store_memory_sync',
    # Graph Memory
    'MemoryGraph',
    'get_memory_graph',
    'find_related_memories',
    'search_by_topic',
    'search_by_entity',
    # Hierarchical Memory
    'HierarchicalMemory',
    'SensoryCategory',
    'SensoryMemory',
    'SENSORY_MAPPINGS',
    'store_sensory_memory',
    'get_sensory_context',
    'get_efficient_context',
    'initialize_sensory_memories',
    # Raw Conversation Store
    'RawConversationStore',
    'RawConversation',
    'ConversationMessage',
    'ConversationSource',
    'hybrid_search',
    'hybrid_search_sync'
]
