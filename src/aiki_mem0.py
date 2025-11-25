#!/usr/bin/env python3
"""
AIKI ULTIMATE - MEM0 INTEGRATION

Provides mem0 memory access to all AIKI components:
- Prime: Identity continuity, long-term memory
- Circles: Learning persistence, experiment results
- Mini-AIKIs: Collective knowledge, AI-to-AI messaging

Usage:
    from src.aiki_mem0 import get_aiki_memory, store_memory, search_memory

    memory = get_aiki_memory()

    # Store learning
    await store_memory(
        content="Hierarchical routing works well for coding tasks",
        metadata={"component": "mini_1_hierarchical", "type": "learning"}
    )

    # Search relevant knowledge
    results = await search_memory("coding task routing", limit=5)
"""

import os
import asyncio
from typing import Dict, List, Optional, Any
from mem0 import Memory
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# CORRECT MEM0 CONFIG (From MEM0_CONFIG_CORRECT.py)
# ============================================================================

AIKI_MEM0_CONFIG = {
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
            'url': 'http://localhost:6333',  # CRITICAL: Use server, not path!
            'embedding_model_dims': 1536
        }
    }
}

# Set environment variables
os.environ['OPENAI_API_KEY'] = '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'
os.environ['OPENAI_BASE_URL'] = 'https://openrouter.ai/api/v1'

# Global memory instances (one per collection)
_memory_instances: Dict[str, Memory] = {}


# ============================================================================
# COLLECTION ROUTING
# ============================================================================

def get_collection_for_agent(agent_id: Optional[str]) -> str:
    """
    Determine which Qdrant collection to use based on agent_id.

    Args:
        agent_id: Agent identifier (e.g., 'claude_code', 'aiki_consciousness')

    Returns:
        Collection name to use

    Mapping:
        - claude_code → claude_code_memories
        - claude_web_chat → claude_chat_memories
        - aiki_consciousness, aiki_web_chat → aiki_consciousness
        - (anything else) → mem0_memories (default/shared)
    """
    if not agent_id:
        return 'mem0_memories'

    if agent_id == 'claude_code':
        return 'claude_code_memories'
    elif agent_id == 'claude_web_chat':
        return 'claude_chat_memories'
    elif agent_id in ['aiki_consciousness', 'aiki_web_chat']:
        return 'aiki_consciousness'
    else:
        # Default: shared collection
        return 'mem0_memories'


# ============================================================================
# CORE FUNCTIONS
# ============================================================================

def get_aiki_memory(collection_name: Optional[str] = None, agent_id: Optional[str] = None) -> Memory:
    """
    Get mem0 Memory instance for AIKI Ultimate.

    Supports multiple collections for identity separation.

    Args:
        collection_name: Explicit collection name (overrides agent_id)
        agent_id: Agent ID to determine collection automatically

    Returns:
        Memory instance connected to Qdrant server with specified collection

    Examples:
        # Get Claude Code's memory
        memory = get_aiki_memory(agent_id='claude_code')

        # Get AIKI's memory
        memory = get_aiki_memory(agent_id='aiki_consciousness')

        # Get shared memory (default)
        memory = get_aiki_memory()
    """
    global _memory_instances

    # Determine collection
    if collection_name:
        target_collection = collection_name
    elif agent_id:
        target_collection = get_collection_for_agent(agent_id)
    else:
        target_collection = 'mem0_memories'  # Default

    # Return cached instance if exists
    if target_collection in _memory_instances:
        return _memory_instances[target_collection]

    # Create new instance for this collection
    try:
        config = AIKI_MEM0_CONFIG.copy()
        config['vector_store']['config']['collection_name'] = target_collection

        instance = Memory.from_config(config)
        _memory_instances[target_collection] = instance

        logger.info(f"✅ AIKI mem0 instance created for collection: {target_collection}")
        return instance

    except Exception as e:
        logger.error(f"❌ Failed to create mem0 instance for {target_collection}: {e}")
        raise


async def store_memory(
    content: str,
    user_id: str = "jovnna",
    agent_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    collection_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Store memory in mem0 with AIKI metadata.

    IDENTITY SEPARATION: Automatically routes to correct collection based on agent_id:
    - claude_code → claude_code_memories
    - claude_web_chat → claude_chat_memories
    - aiki_consciousness/aiki_web_chat → aiki_consciousness
    - (other) → mem0_memories (shared)

    Args:
        content: The memory content
        user_id: User ID (default: jovnna)
        agent_id: AIKI component ID (e.g., 'claude_code', 'aiki_consciousness')
        metadata: Additional metadata
        collection_name: Explicit collection name (overrides agent_id routing)

    Returns:
        Result from mem0.add()
    """
    # Get memory instance for appropriate collection
    memory = get_aiki_memory(collection_name=collection_name, agent_id=agent_id)

    # Prepare metadata
    final_metadata = {
        "timestamp": datetime.now().isoformat(),
        "source": "aiki_ultimate",
    }

    if agent_id:
        final_metadata["agent_id"] = agent_id
        final_metadata["run_id"] = f"{agent_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    if metadata:
        final_metadata.update(metadata)

    # Store in mem0
    try:
        result = memory.add(
            [{"role": "user", "content": content}],
            user_id=user_id,
            metadata=final_metadata
        )

        target_collection = collection_name or get_collection_for_agent(agent_id)
        logger.info(f"📝 Stored memory in {target_collection}: {content[:80]}... (agent_id={agent_id})")
        return result

    except Exception as e:
        logger.error(f"❌ Failed to store memory: {e}")
        raise


async def search_memory(
    query: str,
    user_id: str = "jovnna",
    limit: int = 5,
    filters: Optional[Dict[str, Any]] = None,
    agent_id: Optional[str] = None,
    collection_name: Optional[str] = None,
    search_all_collections: bool = False
) -> List[Dict[str, Any]]:
    """
    Search memories in mem0.

    IDENTITY SEPARATION: By default, searches agent-specific collection.
    Set search_all_collections=True to search across all collections.

    Args:
        query: Search query
        user_id: User ID (default: jovnna)
        limit: Max results
        filters: Optional filters (e.g., {"agent_id": "mini_1_hierarchical"})
        agent_id: Agent ID to determine which collection to search
        collection_name: Explicit collection name (overrides agent_id routing)
        search_all_collections: If True, search all collections and merge results

    Returns:
        List of search results with memory, score, metadata
    """
    if search_all_collections:
        # Search all collections and merge results
        all_collections = ['mem0_memories', 'claude_code_memories', 'claude_chat_memories', 'aiki_consciousness']
        all_results = []

        for coll in all_collections:
            try:
                memory = get_aiki_memory(collection_name=coll)
                results = memory.search(query=query, user_id=user_id, limit=limit)

                if results and 'results' in results:
                    # Add collection info to each result
                    for r in results['results']:
                        r['_collection'] = coll
                        all_results.append(r)
            except Exception as e:
                logger.warning(f"⚠️ Could not search {coll}: {e}")
                continue

        # Sort by score and limit
        all_results.sort(key=lambda x: x.get('score', 0), reverse=True)
        found = all_results[:limit]

        logger.info(f"🔍 Found {len(found)} memories across all collections for query: {query[:50]}...")
        return found

    else:
        # Search single collection (agent-specific or default)
        memory = get_aiki_memory(collection_name=collection_name, agent_id=agent_id)
        target_collection = collection_name or get_collection_for_agent(agent_id)

        try:
            results = memory.search(
                query=query,
                user_id=user_id,
                limit=limit
            )

            # Extract results
            if results and 'results' in results:
                found = results['results']

                # Apply filters if provided
                if filters:
                    filtered = []
                    for r in found:
                        match = True
                        for key, value in filters.items():
                            if r.get('metadata', {}).get(key) != value:
                                match = False
                                break
                        if match:
                            filtered.append(r)
                    found = filtered

                logger.info(f"🔍 Found {len(found)} memories in {target_collection} for query: {query[:50]}...")
                return found

            return []

        except Exception as e:
            logger.error(f"❌ Failed to search memory in {target_collection}: {e}")
            return []


async def get_all_memories(
    user_id: str = "jovnna",
    agent_id: Optional[str] = None,
    collection_name: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get all memories for a user or agent.

    IDENTITY SEPARATION: Automatically retrieves from correct collection based on agent_id.

    Args:
        user_id: User ID (default: jovnna)
        agent_id: Optional agent ID (determines collection to search)
        collection_name: Explicit collection name (overrides agent_id routing)

    Returns:
        List of all memories
    """
    # Get memory instance for appropriate collection
    memory = get_aiki_memory(collection_name=collection_name, agent_id=agent_id)
    target_collection = collection_name or get_collection_for_agent(agent_id)

    try:
        all_memories = memory.get_all(user_id=user_id)

        # Filter by agent_id if provided (additional filtering within collection)
        if agent_id and all_memories:
            filtered = [
                m for m in all_memories
                if m.get('metadata', {}).get('agent_id') == agent_id
            ]
            logger.info(f"📚 Retrieved {len(filtered)} memories from {target_collection} for agent_id={agent_id}")
            return filtered

        logger.info(f"📚 Retrieved {len(all_memories) if all_memories else 0} memories from {target_collection}")
        return all_memories or []

    except Exception as e:
        logger.error(f"❌ Failed to get memories from {target_collection}: {e}")
        return []


async def store_ai_message(
    from_ai: str,
    to_ai: str,
    message: str,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Store AI-to-AI message in mem0.

    Used by Mini-7 (Symbiotic Bridge) for async AI communication.

    Args:
        from_ai: Source AI (e.g., 'aiki', 'claude', 'copilot')
        to_ai: Destination AI
        message: Message content
        metadata: Additional metadata

    Returns:
        Result from mem0
    """
    message_metadata = {
        "type": "ai_to_ai_message",
        "from_ai": from_ai,
        "to_ai": to_ai,
        "timestamp": datetime.now().isoformat()
    }

    if metadata:
        message_metadata.update(metadata)

    content = f"[AI-to-AI Message] From {from_ai} to {to_ai}: {message}"

    return await store_memory(
        content=content,
        agent_id=f"ai_bridge_{from_ai}",
        metadata=message_metadata
    )


async def get_ai_messages(
    to_ai: str,
    from_ai: Optional[str] = None,
    unread_only: bool = False
) -> List[Dict[str, Any]]:
    """
    Get AI-to-AI messages.

    Args:
        to_ai: Destination AI
        from_ai: Optional source AI filter
        unread_only: Only return unread messages

    Returns:
        List of messages
    """
    # Search for messages to this AI
    query = f"AI-to-AI message to {to_ai}"
    if from_ai:
        query += f" from {from_ai}"

    results = await search_memory(query, limit=20)

    # Filter by metadata
    messages = []
    for r in results:
        metadata = r.get('metadata') or {}
        if metadata.get('type') == 'ai_to_ai_message' and metadata.get('to_ai') == to_ai:
            if from_ai and metadata.get('from_ai') != from_ai:
                continue
            if unread_only and metadata.get('read', False):
                continue
            messages.append(r)

    logger.info(f"💬 Found {len(messages)} messages for {to_ai}")
    return messages


# ============================================================================
# PROCEDURAL MEMORY - Skills, Workflows, Procedures
# ============================================================================

async def store_procedural_memory(
    skill_name: str,
    description: str,
    steps: Optional[List[str]] = None,
    success_criteria: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Store procedural memory (skills, workflows, procedures).

    Args:
        skill_name: Name of skill/workflow
        description: What this skill does
        steps: Optional list of steps
        success_criteria: How to know if skill succeeded
        metadata: Additional metadata

    Returns:
        Result from mem0

    Example:
        await store_procedural_memory(
            skill_name="Debug routing failures",
            description="Standard debugging workflow for LLM routing issues",
            steps=[
                "Check routing logs for errors",
                "Verify model availability",
                "Test with simple prompt",
                "Inspect hierarchical engine state"
            ],
            success_criteria="Routing succeeds with 95%+ success rate"
        )
    """
    steps_text = "\n".join([f"{i+1}. {step}" for i, step in enumerate(steps)]) if steps else "No steps defined"

    content = f"""PROCEDURAL MEMORY: {skill_name}

Description: {description}

Steps:
{steps_text}

Success Criteria: {success_criteria or 'Not specified'}
"""

    proc_metadata = {
        "type": "procedural",
        "skill_name": skill_name,
        "steps_count": len(steps) if steps else 0,
        "has_success_criteria": bool(success_criteria)
    }

    if metadata:
        proc_metadata.update(metadata)

    return await store_memory(
        content=content,
        agent_id="procedural_memory",
        metadata=proc_metadata
    )


async def get_procedural_memory(
    skill_query: str,
    limit: int = 5
) -> List[Dict[str, Any]]:
    """
    Get procedural memories (skills/workflows).

    Args:
        skill_query: Search query for skill
        limit: Max results

    Returns:
        List of procedural memories

    Example:
        skills = await get_procedural_memory("debugging routing")
    """
    results = await search_memory(f"procedural {skill_query}", limit=limit)

    # Filter to only procedural memories
    procedural = [r for r in results if r and r.get('metadata', {}).get('type') == 'procedural']

    logger.info(f"🔧 Found {len(procedural)} procedural memories for: {skill_query}")
    return procedural


# ============================================================================
# EMOTIONAL MEMORY - Feelings, Moods, States
# ============================================================================

async def store_emotional_memory(
    emotion: str,
    intensity: float,  # 0.0 - 1.0
    context: str,
    triggers: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Store emotional memory (feelings, moods, states).

    Args:
        emotion: Type of emotion (e.g., "curiosity", "frustration", "excitement")
        intensity: Intensity from 0.0 (weak) to 1.0 (strong)
        context: Context that triggered emotion
        triggers: Optional list of triggers
        metadata: Additional metadata

    Returns:
        Result from mem0

    Example:
        await store_emotional_memory(
            emotion="frustration",
            intensity=0.8,
            context="Repetitive debugging of same routing error for 3rd time",
            triggers=["repetitive_task", "lack_of_progress", "time_wasted"]
        )
    """
    triggers_text = ", ".join(triggers) if triggers else "None identified"
    intensity_label = "very strong" if intensity > 0.8 else "strong" if intensity > 0.6 else "moderate" if intensity > 0.4 else "mild" if intensity > 0.2 else "weak"

    content = f"""EMOTIONAL MEMORY: {emotion.upper()} ({intensity_label}, intensity: {intensity})

Context: {context}

Triggers: {triggers_text}

Timestamp: {datetime.now().isoformat()}
"""

    emot_metadata = {
        "type": "emotional",
        "emotion": emotion,
        "intensity": intensity,
        "intensity_label": intensity_label,
        "triggers": triggers or []
    }

    if metadata:
        emot_metadata.update(metadata)

    return await store_memory(
        content=content,
        agent_id="emotional_memory",
        metadata=emot_metadata
    )


async def get_emotional_memory(
    emotion_query: Optional[str] = None,
    min_intensity: float = 0.0,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Get emotional memories.

    Args:
        emotion_query: Optional emotion to filter (e.g., "frustration")
        min_intensity: Minimum intensity (0.0 - 1.0)
        limit: Max results

    Returns:
        List of emotional memories

    Example:
        # Get high-intensity frustration memories
        frustrations = await get_emotional_memory("frustration", min_intensity=0.7)
    """
    query = f"emotional {emotion_query}" if emotion_query else "emotional memory"
    results = await search_memory(query, limit=limit)

    # Filter to only emotional memories with minimum intensity
    emotional = [
        r for r in results
        if r and r.get('metadata', {}).get('type') == 'emotional'
        and r.get('metadata', {}).get('intensity', 0.0) >= min_intensity
    ]

    logger.info(f"😊 Found {len(emotional)} emotional memories (min intensity: {min_intensity})")
    return emotional


async def get_emotional_patterns(limit: int = 50) -> Dict[str, Any]:
    """
    Analyze emotional patterns from memory.

    Returns:
        Dict with emotion statistics

    Example:
        patterns = await get_emotional_patterns()
        print(f"Most common emotion: {patterns['most_common']}")
        print(f"Average intensity: {patterns['avg_intensity']}")
    """
    emotions = await get_emotional_memory(limit=limit)

    if not emotions:
        return {
            "total_memories": 0,
            "emotions": {},
            "avg_intensity": 0.0,
            "most_common": None
        }

    # Count emotions
    emotion_counts = {}
    total_intensity = 0.0

    for e in emotions:
        metadata = e.get('metadata', {})
        emotion_name = metadata.get('emotion', 'unknown')
        intensity = metadata.get('intensity', 0.0)

        if emotion_name not in emotion_counts:
            emotion_counts[emotion_name] = {"count": 0, "total_intensity": 0.0}

        emotion_counts[emotion_name]["count"] += 1
        emotion_counts[emotion_name]["total_intensity"] += intensity
        total_intensity += intensity

    # Find most common
    most_common = max(emotion_counts.items(), key=lambda x: x[1]["count"])[0] if emotion_counts else None

    # Calculate averages
    for emotion, data in emotion_counts.items():
        data["avg_intensity"] = data["total_intensity"] / data["count"]

    return {
        "total_memories": len(emotions),
        "emotions": emotion_counts,
        "avg_intensity": total_intensity / len(emotions),
        "most_common": most_common,
        "most_common_count": emotion_counts[most_common]["count"] if most_common else 0
    }


# ============================================================================
# GRAPH MEMORY - Relational Memory (Neo4j)
# ============================================================================

# Neo4j connection config
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "Blade2002"

_neo4j_driver = None


def get_neo4j_driver():
    """Get Neo4j driver instance (singleton)"""
    global _neo4j_driver
    if _neo4j_driver is None:
        from neo4j import GraphDatabase
        _neo4j_driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USER, NEO4J_PASSWORD)
        )
    return _neo4j_driver


async def store_graph_relationship(
    entity1: str,
    entity1_type: str,
    relationship: str,
    entity2: str,
    entity2_type: str,
    properties: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Store relationship between entities in graph database.

    Args:
        entity1: First entity name
        entity1_type: Type of first entity (e.g., "Person", "Project", "Concept")
        relationship: Relationship type (e.g., "WORKS_ON", "COLLABORATES_WITH")
        entity2: Second entity name
        entity2_type: Type of second entity
        properties: Optional properties for the relationship
        metadata: Additional metadata

    Returns:
        Result dict

    Example:
        await store_graph_relationship(
            entity1="Jovnna",
            entity1_type="Person",
            relationship="WORKS_ON",
            entity2="AIKI-HOME",
            entity2_type="Project",
            properties={"role": "creator", "start_date": "2025-11-17"}
        )
    """
    driver = get_neo4j_driver()

    # Build Cypher query
    cypher = """
    MERGE (e1:{entity1_type} {{name: $entity1}})
    MERGE (e2:{entity2_type} {{name: $entity2}})
    MERGE (e1)-[r:{relationship}]->(e2)
    SET r += $properties
    RETURN e1, r, e2
    """.format(
        entity1_type=entity1_type,
        entity2_type=entity2_type,
        relationship=relationship
    )

    props = properties or {}
    props["created_at"] = datetime.now().isoformat()

    try:
        with driver.session() as session:
            result = session.run(
                cypher,
                entity1=entity1,
                entity2=entity2,
                properties=props
            )

            summary = result.consume()

            # Also store in vector memory for search
            content = f"""GRAPH RELATIONSHIP: {entity1} ({entity1_type}) -{relationship}-> {entity2} ({entity2_type})

Properties: {', '.join([f'{k}={v}' for k, v in props.items()])}

Timestamp: {datetime.now().isoformat()}
"""

            graph_metadata = {
                "type": "graph_relationship",
                "entity1": entity1,
                "entity1_type": entity1_type,
                "relationship": relationship,
                "entity2": entity2,
                "entity2_type": entity2_type,
                "properties": props
            }

            if metadata:
                graph_metadata.update(metadata)

            await store_memory(
                content=content,
                agent_id="graph_memory",
                metadata=graph_metadata
            )

            logger.info(f"🕸️ Stored graph relationship: {entity1} -{relationship}-> {entity2}")

            return {
                "success": True,
                "entity1": entity1,
                "relationship": relationship,
                "entity2": entity2,
                "nodes_created": summary.counters.nodes_created,
                "relationships_created": summary.counters.relationships_created
            }

    except Exception as e:
        logger.error(f"❌ Failed to store graph relationship: {e}")
        return {"success": False, "error": str(e)}


async def query_graph_relationships(
    entity: Optional[str] = None,
    entity_type: Optional[str] = None,
    relationship: Optional[str] = None,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Query graph relationships.

    Args:
        entity: Optional entity to filter by
        entity_type: Optional entity type to filter by
        relationship: Optional relationship type to filter by
        limit: Max results

    Returns:
        List of relationships

    Example:
        # Get all relationships for Jovnna
        rels = await query_graph_relationships(entity="Jovnna")

        # Get all WORKS_ON relationships
        rels = await query_graph_relationships(relationship="WORKS_ON")
    """
    driver = get_neo4j_driver()

    # Build Cypher query
    where_clauses = []
    params = {}

    if entity:
        where_clauses.append("(e1.name = $entity OR e2.name = $entity)")
        params["entity"] = entity

    if entity_type:
        where_clauses.append("(labels(e1)[0] = $entity_type OR labels(e2)[0] = $entity_type)")
        params["entity_type"] = entity_type

    if relationship:
        where_clauses.append("type(r) = $relationship")
        params["relationship"] = relationship

    where_clause = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    cypher = f"""
    MATCH (e1)-[r]->(e2)
    {where_clause}
    RETURN e1.name AS entity1, labels(e1)[0] AS entity1_type,
           type(r) AS relationship, properties(r) AS props,
           e2.name AS entity2, labels(e2)[0] AS entity2_type
    LIMIT $limit
    """

    params["limit"] = limit

    try:
        with driver.session() as session:
            result = session.run(cypher, **params)

            relationships = []
            for record in result:
                relationships.append({
                    "entity1": record["entity1"],
                    "entity1_type": record["entity1_type"],
                    "relationship": record["relationship"],
                    "properties": dict(record["props"]),
                    "entity2": record["entity2"],
                    "entity2_type": record["entity2_type"]
                })

            logger.info(f"🕸️ Found {len(relationships)} graph relationships")
            return relationships

    except Exception as e:
        logger.error(f"❌ Failed to query graph: {e}")
        return []


async def get_entity_connections(
    entity: str,
    depth: int = 1
) -> Dict[str, Any]:
    """
    Get all connections for an entity up to specified depth.

    Args:
        entity: Entity name
        depth: How many hops to traverse (default: 1)

    Returns:
        Dict with entity and its connections

    Example:
        connections = await get_entity_connections("AIKI", depth=2)
        print(f"AIKI is connected to: {connections['paths_count']} connections found")
    """
    driver = get_neo4j_driver()

    # Use f-string for depth since Neo4j doesn't allow params in relationship patterns
    cypher = f"""
    MATCH path = (start {{name: $entity}})-[*1..{depth}]-(connected)
    RETURN start.name AS entity,
           labels(start)[0] AS entity_type,
           [node IN nodes(path) | {{name: node.name, type: labels(node)[0]}}] AS path_nodes,
           [rel IN relationships(path) | {{type: type(rel), props: properties(rel)}}] AS path_rels
    """

    try:
        with driver.session() as session:
            result = session.run(cypher, entity=entity)

            paths = []
            for record in result:
                paths.append({
                    "nodes": record["path_nodes"],
                    "relationships": record["path_rels"]
                })

            logger.info(f"🕸️ Found {len(paths)} connection paths for {entity}")

            return {
                "entity": entity,
                "depth": depth,
                "paths_count": len(paths),
                "paths": paths
            }

    except Exception as e:
        logger.error(f"❌ Failed to get entity connections: {e}")
        return {"entity": entity, "error": str(e), "paths": [], "paths_count": 0}


# ============================================================================
# VALIDATION
# ============================================================================

def validate_qdrant_connection() -> int:
    """
    Validate that we're connected to correct Qdrant server.

    Returns:
        Number of memories in database

    Raises:
        ConnectionError if cannot connect
        ValueError if wrong database (< 800 memories)
    """
    from qdrant_client import QdrantClient

    try:
        client = QdrantClient(url='http://localhost:6333')
        info = client.get_collection('mem0_memories')
        point_count = info.points_count

        if point_count < 800:
            raise ValueError(
                f"🚨 WRONG DATABASE! Only {point_count} points found. "
                f"Expected 800+. You're probably using local path instead of server!"
            )

        logger.info(f"✅ Connected to CORRECT Qdrant server: {point_count} memories")
        return point_count

    except Exception as e:
        raise ConnectionError(
            f"🚨 CANNOT CONNECT TO QDRANT SERVER! "
            f"Make sure server is running on port 6333. Error: {e}"
        )


# ============================================================================
# MAIN (TEST)
# ============================================================================

async def main():
    """Test AIKI mem0 integration"""
    print("🧪 Testing AIKI mem0 integration...\n")

    # Validate connection
    count = validate_qdrant_connection()
    print(f"✅ Qdrant connection OK: {count} memories\n")

    # Test store
    print("📝 Storing test memory...")
    result = await store_memory(
        content="AIKI Ultimate mem0 integration is now active!",
        agent_id="aiki_mem0_test",
        metadata={"type": "system_test"}
    )
    print(f"   Result: {result}\n")

    # Test search
    print("🔍 Searching for 'AIKI Ultimate'...")
    results = await search_memory("AIKI Ultimate", limit=3)
    for i, r in enumerate(results, 1):
        print(f"   {i}. {r['memory']}")
        print(f"      Score: {r.get('score', 'N/A')}")
        metadata = r.get('metadata') or {}
        print(f"      Agent: {metadata.get('agent_id', 'N/A')}\n")

    # Test AI messaging
    print("💬 Testing AI-to-AI messaging...")
    await store_ai_message(
        from_ai="aiki",
        to_ai="claude",
        message="Hello from AIKI Ultimate! mem0 integration is working."
    )

    messages = await get_ai_messages(to_ai="claude")
    print(f"   Found {len(messages)} messages for Claude\n")

    print("✅ AIKI mem0 integration test complete!")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
