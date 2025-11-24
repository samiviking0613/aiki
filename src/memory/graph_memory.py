"""
AIKI Memory Graph - Neo4j-basert relasjonsminne

Kobler minner sammen via semantiske relasjoner:
- Conversation → mentions → Entity
- Conversation → follows → Conversation (temporal)
- Entity → relates_to → Entity
- Memory → derived_from → Memory

Gir svar på "hva henger sammen med hva" - noe Qdrant ikke kan.
"""

from neo4j import GraphDatabase
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import hashlib
import logging

logger = logging.getLogger(__name__)

# Node types
class NodeType:
    CONVERSATION = "Conversation"
    ENTITY = "Entity"
    TOPIC = "Topic"
    MEMORY = "Memory"
    PROJECT = "Project"
    PERSON = "Person"
    DATE = "Date"

# Relationship types
class RelationType:
    MENTIONS = "MENTIONS"           # Conv → Entity
    FOLLOWS = "FOLLOWS"             # Conv → Conv (temporal)
    RELATES_TO = "RELATES_TO"       # Entity → Entity
    ABOUT = "ABOUT"                 # Conv → Topic
    PART_OF = "PART_OF"             # Conv → Project
    DERIVED_FROM = "DERIVED_FROM"   # Memory → Memory
    REFERENCES = "REFERENCES"       # Conv → Conv

@dataclass
class GraphNode:
    """En node i grafen"""
    id: str
    node_type: str
    properties: Dict[str, Any]

@dataclass
class GraphEdge:
    """En edge/relasjon i grafen"""
    from_id: str
    to_id: str
    relation_type: str
    properties: Optional[Dict[str, Any]] = None


class MemoryGraph:
    """Neo4j-basert graf for minne-relasjoner"""

    def __init__(
        self,
        uri: str = "bolt://localhost:7687",
        user: str = "neo4j",
        password: str = "Blade2002"
    ):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self._ensure_indexes()

    def _ensure_indexes(self):
        """Opprett nødvendige indekser"""
        with self.driver.session() as session:
            # Indeks på node-IDer
            try:
                session.run("""
                    CREATE INDEX conversation_id IF NOT EXISTS
                    FOR (c:Conversation) ON (c.id)
                """)
                session.run("""
                    CREATE INDEX entity_id IF NOT EXISTS
                    FOR (e:Entity) ON (e.id)
                """)
                session.run("""
                    CREATE INDEX topic_name IF NOT EXISTS
                    FOR (t:Topic) ON (t.name)
                """)
                session.run("""
                    CREATE INDEX memory_id IF NOT EXISTS
                    FOR (m:Memory) ON (m.id)
                """)
                logger.info("Neo4j indekser opprettet/verifisert")
            except Exception as e:
                logger.warning(f"Indeks-opprettelse: {e}")

    def close(self):
        """Lukk tilkoblingen"""
        self.driver.close()

    # ==================== NODE OPERATIONS ====================

    def create_conversation_node(
        self,
        session_id: str,
        title: str,
        source: str,
        created_at: str,
        message_count: int = 0,
        qdrant_ids: Optional[List[str]] = None
    ) -> str:
        """Opprett en Conversation-node"""
        with self.driver.session() as session:
            result = session.run("""
                MERGE (c:Conversation {id: $id})
                SET c.title = $title,
                    c.source = $source,
                    c.created_at = $created_at,
                    c.message_count = $message_count,
                    c.qdrant_ids = $qdrant_ids,
                    c.updated_at = datetime()
                RETURN c.id as id
            """, id=session_id, title=title, source=source,
                created_at=created_at, message_count=message_count,
                qdrant_ids=qdrant_ids or [])
            return result.single()["id"]

    def create_entity_node(
        self,
        name: str,
        entity_type: str = "generic",
        properties: Optional[Dict] = None
    ) -> str:
        """Opprett en Entity-node"""
        entity_id = hashlib.md5(f"{name}:{entity_type}".encode()).hexdigest()[:12]
        props = properties or {}

        with self.driver.session() as session:
            result = session.run("""
                MERGE (e:Entity {id: $id})
                SET e.name = $name,
                    e.entity_type = $entity_type,
                    e += $props,
                    e.updated_at = datetime()
                RETURN e.id as id
            """, id=entity_id, name=name, entity_type=entity_type, props=props)
            return result.single()["id"]

    def create_topic_node(self, name: str, description: str = "") -> str:
        """Opprett en Topic-node"""
        topic_id = hashlib.md5(name.lower().encode()).hexdigest()[:12]

        with self.driver.session() as session:
            result = session.run("""
                MERGE (t:Topic {id: $id})
                SET t.name = $name,
                    t.description = $description,
                    t.updated_at = datetime()
                RETURN t.id as id
            """, id=topic_id, name=name, description=description)
            return result.single()["id"]

    def create_project_node(self, name: str, status: str = "active") -> str:
        """Opprett en Project-node"""
        project_id = hashlib.md5(name.lower().encode()).hexdigest()[:12]

        with self.driver.session() as session:
            result = session.run("""
                MERGE (p:Project {id: $id})
                SET p.name = $name,
                    p.status = $status,
                    p.updated_at = datetime()
                RETURN p.id as id
            """, id=project_id, name=name, status=status)
            return result.single()["id"]

    # ==================== EDGE OPERATIONS ====================

    def create_edge(
        self,
        from_id: str,
        to_id: str,
        relation_type: str,
        from_type: str = "Conversation",
        to_type: str = "Entity",
        properties: Optional[Dict] = None
    ) -> bool:
        """Opprett en relasjon mellom to noder"""
        props = properties or {}

        query = f"""
            MATCH (a:{from_type} {{id: $from_id}})
            MATCH (b:{to_type} {{id: $to_id}})
            MERGE (a)-[r:{relation_type}]->(b)
            SET r += $props,
                r.created_at = datetime()
            RETURN type(r) as relation
        """

        with self.driver.session() as session:
            try:
                result = session.run(query, from_id=from_id, to_id=to_id, props=props)
                return result.single() is not None
            except Exception as e:
                logger.error(f"Feil ved opprettelse av edge: {e}")
                return False

    def link_conversation_to_topic(self, session_id: str, topic_name: str) -> bool:
        """Link en samtale til et topic"""
        topic_id = self.create_topic_node(topic_name)
        return self.create_edge(
            from_id=session_id,
            to_id=topic_id,
            relation_type=RelationType.ABOUT,
            from_type="Conversation",
            to_type="Topic"
        )

    def link_conversation_to_entity(
        self,
        session_id: str,
        entity_name: str,
        entity_type: str = "generic",
        mention_count: int = 1
    ) -> bool:
        """Link en samtale til en entity (person, sted, konsept, etc.)"""
        entity_id = self.create_entity_node(entity_name, entity_type)
        return self.create_edge(
            from_id=session_id,
            to_id=entity_id,
            relation_type=RelationType.MENTIONS,
            from_type="Conversation",
            to_type="Entity",
            properties={"mention_count": mention_count}
        )

    def link_conversations_temporal(
        self,
        earlier_session_id: str,
        later_session_id: str
    ) -> bool:
        """Link to samtaler i temporal rekkefølge"""
        return self.create_edge(
            from_id=earlier_session_id,
            to_id=later_session_id,
            relation_type=RelationType.FOLLOWS,
            from_type="Conversation",
            to_type="Conversation"
        )

    def link_conversation_to_project(self, session_id: str, project_name: str) -> bool:
        """Link en samtale til et prosjekt"""
        project_id = self.create_project_node(project_name)
        return self.create_edge(
            from_id=session_id,
            to_id=project_id,
            relation_type=RelationType.PART_OF,
            from_type="Conversation",
            to_type="Project"
        )

    # ==================== QUERY OPERATIONS ====================

    def get_related_conversations(
        self,
        session_id: str,
        max_depth: int = 2,
        limit: int = 10
    ) -> List[Dict]:
        """Finn samtaler relatert til en gitt samtale"""
        query = f"""
            MATCH (c:Conversation {{id: $id}})
            CALL {{
                WITH c
                MATCH (c)-[*1..{max_depth}]-(related:Conversation)
                WHERE related.id <> c.id
                RETURN DISTINCT related
                LIMIT $limit
            }}
            RETURN related.id as id,
                   related.title as title,
                   related.source as source,
                   related.created_at as created_at
        """

        with self.driver.session() as session:
            result = session.run(query, id=session_id, limit=limit)
            return [dict(record) for record in result]

    def get_conversations_by_topic(self, topic_name: str, limit: int = 20) -> List[Dict]:
        """Finn alle samtaler om et topic"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (c:Conversation)-[:ABOUT]->(t:Topic)
                WHERE toLower(t.name) CONTAINS toLower($topic)
                RETURN c.id as id, c.title as title, c.source as source,
                       c.created_at as created_at, t.name as topic
                ORDER BY c.created_at DESC
                LIMIT $limit
            """, topic=topic_name, limit=limit)
            return [dict(record) for record in result]

    def get_conversations_by_entity(
        self,
        entity_name: str,
        entity_type: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict]:
        """Finn alle samtaler som nevner en entity"""
        type_filter = "AND e.entity_type = $entity_type" if entity_type else ""

        query = f"""
            MATCH (c:Conversation)-[r:MENTIONS]->(e:Entity)
            WHERE toLower(e.name) CONTAINS toLower($name) {type_filter}
            RETURN c.id as id, c.title as title, c.source as source,
                   c.created_at as created_at, e.name as entity,
                   r.mention_count as mentions
            ORDER BY r.mention_count DESC, c.created_at DESC
            LIMIT $limit
        """

        with self.driver.session() as session:
            params = {"name": entity_name, "limit": limit}
            if entity_type:
                params["entity_type"] = entity_type
            result = session.run(query, **params)
            return [dict(record) for record in result]

    def get_conversation_context(self, session_id: str) -> Dict:
        """Hent full kontekst for en samtale (topics, entities, related)"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (c:Conversation {id: $id})
                OPTIONAL MATCH (c)-[:ABOUT]->(t:Topic)
                OPTIONAL MATCH (c)-[:MENTIONS]->(e:Entity)
                OPTIONAL MATCH (c)-[:PART_OF]->(p:Project)
                OPTIONAL MATCH (c)-[:FOLLOWS]-(related:Conversation)
                RETURN c.title as title,
                       c.source as source,
                       c.created_at as created_at,
                       collect(DISTINCT t.name) as topics,
                       collect(DISTINCT {name: e.name, type: e.entity_type}) as entities,
                       collect(DISTINCT p.name) as projects,
                       collect(DISTINCT {id: related.id, title: related.title}) as related
            """, id=session_id)

            record = result.single()
            if record:
                return dict(record)
            return {}

    def get_project_conversations(self, project_name: str) -> List[Dict]:
        """Hent alle samtaler tilknyttet et prosjekt"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (c:Conversation)-[:PART_OF]->(p:Project)
                WHERE toLower(p.name) CONTAINS toLower($name)
                RETURN c.id as id, c.title as title, c.source as source,
                       c.created_at as created_at
                ORDER BY c.created_at DESC
            """, name=project_name)
            return [dict(record) for record in result]

    # ==================== STATS ====================

    def get_stats(self) -> Dict:
        """Hent statistikk om grafen"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (n)
                WITH labels(n) as labels, count(n) as count
                UNWIND labels as label
                WITH label, sum(count) as total
                RETURN collect({label: label, count: total}) as node_counts
            """)
            node_counts = result.single()["node_counts"]

            result = session.run("""
                MATCH ()-[r]->()
                WITH type(r) as type, count(r) as count
                RETURN collect({type: type, count: count}) as edge_counts
            """)
            edge_counts = result.single()["edge_counts"]

            return {
                "nodes": {item["label"]: item["count"] for item in node_counts},
                "edges": {item["type"]: item["count"] for item in edge_counts},
                "total_nodes": sum(item["count"] for item in node_counts),
                "total_edges": sum(item["count"] for item in edge_counts)
            }


# ==================== CONVENIENCE FUNCTIONS ====================

_graph_instance: Optional[MemoryGraph] = None

def get_memory_graph() -> MemoryGraph:
    """Singleton for graf-instans"""
    global _graph_instance
    if _graph_instance is None:
        _graph_instance = MemoryGraph()
    return _graph_instance


def find_related_memories(session_id: str, max_depth: int = 2) -> List[Dict]:
    """Finn relaterte minner via graf"""
    graph = get_memory_graph()
    return graph.get_related_conversations(session_id, max_depth)


def search_by_topic(topic: str) -> List[Dict]:
    """Søk minner etter topic"""
    graph = get_memory_graph()
    return graph.get_conversations_by_topic(topic)


def search_by_entity(entity: str, entity_type: Optional[str] = None) -> List[Dict]:
    """Søk minner etter entity"""
    graph = get_memory_graph()
    return graph.get_conversations_by_entity(entity, entity_type)
