#!/usr/bin/env python3
"""
AIKI Memory Graph
Simple knowledge graph on top of mem0 using metadata tagging
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

from mem0 import Memory

# Paths
QDRANT_PATH = Path("/home/jovnna/aiki/shared_qdrant")

# mem0 config
OPENROUTER_KEY = "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"
os.environ['OPENAI_API_KEY'] = OPENROUTER_KEY
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
            'collection_name': 'aiki_memories',
            'path': str(QDRANT_PATH),
            'embedding_model_dims': 1536
        }
    }
}


class EntityType(Enum):
    """Entity types in AIKI knowledge graph"""
    PERSON = "person"
    SYSTEM = "system"
    RULE = "rule"
    HARDWARE = "hardware"
    SKILL = "skill"
    PROJECT = "project"
    CONDITION = "condition"
    LOCATION = "location"


class RelationType(Enum):
    """Relationship types in AIKI knowledge graph"""
    HAS_CONDITION = "has_condition"
    USES = "uses"
    REQUIRES = "requires"
    BLOCKS = "blocks"
    ALLOWS = "allows"
    ENFORCES = "enforces"
    TRIGGERS = "triggers"
    VERIFIED_BY = "verified_by"
    PART_OF = "part_of"
    DEPENDS_ON = "depends_on"
    IMPLEMENTS = "implements"
    SOLVES = "solves"
    CREATED_BY = "created_by"


@dataclass
class Entity:
    """Knowledge graph entity"""
    id: str
    name: str
    type: EntityType
    properties: Dict[str, Any]

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type.value,
            'properties': self.properties
        }


@dataclass
class Relation:
    """Knowledge graph relationship"""
    source: str  # entity ID
    relation: RelationType
    target: str  # entity ID
    properties: Dict[str, Any]

    def to_dict(self):
        return {
            'source': self.source,
            'relation': self.relation.value,
            'target': self.target,
            'properties': self.properties
        }


class AIKIMemoryGraph:
    """Simple knowledge graph using mem0 metadata"""

    def __init__(self, user_id: str = 'jovnna'):
        self.memory = Memory.from_config(config)
        self.user_id = user_id
        self.entities: Dict[str, Entity] = {}
        self.relations: List[Relation] = []

    def add_entity(self, entity: Entity):
        """Add an entity to the graph"""
        self.entities[entity.id] = entity

        # Store in mem0 with metadata
        text = f"Entity: {entity.name} (Type: {entity.type.value})\n"
        text += f"Properties: {json.dumps(entity.properties, indent=2)}"

        self.memory.add(
            [{'role': 'user', 'content': text}],
            user_id=self.user_id,
            metadata={
                'memory_type': 'entity',
                'entity_id': entity.id,
                'entity_type': entity.type.value,
                **entity.properties
            }
        )

    def add_relation(self, relation: Relation):
        """Add a relationship to the graph"""
        self.relations.append(relation)

        # Get entity names
        source_name = self.entities.get(relation.source, Entity(relation.source, relation.source, EntityType.SYSTEM, {})).name
        target_name = self.entities.get(relation.target, Entity(relation.target, relation.target, EntityType.SYSTEM, {})).name

        # Store in mem0 with metadata
        text = f"Relationship: {source_name} --{relation.relation.value}--> {target_name}\n"
        if relation.properties:
            text += f"Properties: {json.dumps(relation.properties, indent=2)}"

        self.memory.add(
            [{'role': 'user', 'content': text}],
            user_id=self.user_id,
            metadata={
                'memory_type': 'relation',
                'source_id': relation.source,
                'relation_type': relation.relation.value,
                'target_id': relation.target,
                **relation.properties
            }
        )

    def get_relations_from(self, entity_id: str) -> List[Relation]:
        """Get all outgoing relations from an entity"""
        return [r for r in self.relations if r.source == entity_id]

    def get_relations_to(self, entity_id: str) -> List[Relation]:
        """Get all incoming relations to an entity"""
        return [r for r in self.relations if r.target == entity_id]

    def query_path(self, source_id: str, target_id: str, max_depth: int = 3) -> Optional[List[str]]:
        """Find path between two entities (BFS)"""
        if source_id == target_id:
            return [source_id]

        queue = [(source_id, [source_id])]
        visited = {source_id}

        while queue:
            current, path = queue.pop(0)

            if len(path) > max_depth:
                continue

            for relation in self.get_relations_from(current):
                if relation.target not in visited:
                    new_path = path + [relation.target]

                    if relation.target == target_id:
                        return new_path

                    visited.add(relation.target)
                    queue.append((relation.target, new_path))

        return None

    def visualize(self) -> str:
        """Generate text visualization of graph"""
        output = "🕸️ AIKI KNOWLEDGE GRAPH\n"
        output += "=" * 60 + "\n\n"

        output += "📌 ENTITIES:\n"
        for entity in self.entities.values():
            output += f"  • {entity.name} ({entity.type.value})\n"
            for key, value in entity.properties.items():
                output += f"    - {key}: {value}\n"

        output += "\n🔗 RELATIONSHIPS:\n"
        for relation in self.relations:
            source_name = self.entities.get(relation.source, Entity(relation.source, relation.source, EntityType.SYSTEM, {})).name
            target_name = self.entities.get(relation.target, Entity(relation.target, relation.target, EntityType.SYSTEM, {})).name
            output += f"  • {source_name} --{relation.relation.value}--> {target_name}\n"
            if relation.properties:
                for key, value in relation.properties.items():
                    output += f"    - {key}: {value}\n"

        return output

    def export_json(self, filepath: Path):
        """Export graph to JSON file"""
        data = {
            'entities': [e.to_dict() for e in self.entities.values()],
            'relations': [r.to_dict() for r in self.relations]
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)


def create_aiki_home_graph() -> AIKIMemoryGraph:
    """Create AIKI-HOME knowledge graph"""
    graph = AIKIMemoryGraph()

    # --- ENTITIES ---

    # People
    jovnna = Entity(
        id='jovnna',
        name='Jovnna',
        type=EntityType.PERSON,
        properties={'has_adhd': True, 'role': 'developer'}
    )

    # Conditions
    adhd = Entity(
        id='adhd',
        name='ADHD',
        type=EntityType.CONDITION,
        properties={'requires_structure': True, 'requires_accountability': True}
    )

    # Systems
    aiki_home = Entity(
        id='aiki_home',
        name='AIKI-HOME',
        type=EntityType.SYSTEM,
        properties={'purpose': 'Network-level ADHD accountability', 'status': 'phase_1_complete'}
    )

    mitm_proxy = Entity(
        id='mitm_proxy',
        name='MITM Proxy',
        type=EntityType.SYSTEM,
        properties={'port': 8080, 'technology': 'mitmproxy'}
    )

    decision_engine = Entity(
        id='decision_engine',
        name='Decision Engine',
        type=EntityType.SYSTEM,
        properties={'rules_count': 12, 'uses_llm': True}
    )

    # Rules
    morning_workout = Entity(
        id='morning_workout_rule',
        name='Morning Workout Rule',
        type=EntityType.RULE,
        properties={'deadline': '10:00', 'blocks_work_sites': True}
    )

    work_hours_rule = Entity(
        id='work_hours_rule',
        name='Work Hours Focus Rule',
        type=EntityType.RULE,
        properties={'start': '08:00', 'end': '16:00', 'blocks_entertainment': True}
    )

    # Hardware
    motion_sensor = Entity(
        id='motion_sensor',
        name='Motion Sensor',
        type=EntityType.HARDWARE,
        properties={'purpose': 'Verify workout completion'}
    )

    raspberry_pi = Entity(
        id='raspberry_pi',
        name='Raspberry Pi',
        type=EntityType.HARDWARE,
        properties={'role': 'Network gateway', 'status': 'planned'}
    )

    # Add entities to graph
    for entity in [jovnna, adhd, aiki_home, mitm_proxy, decision_engine,
                   morning_workout, work_hours_rule, motion_sensor, raspberry_pi]:
        graph.add_entity(entity)

    # --- RELATIONS ---

    graph.add_relation(Relation(
        source='jovnna',
        relation=RelationType.HAS_CONDITION,
        target='adhd',
        properties={}
    ))

    graph.add_relation(Relation(
        source='jovnna',
        relation=RelationType.USES,
        target='aiki_home',
        properties={'since': '2025-11-17'}
    ))

    graph.add_relation(Relation(
        source='adhd',
        relation=RelationType.REQUIRES,
        target='aiki_home',
        properties={'reason': 'external_accountability'}
    ))

    graph.add_relation(Relation(
        source='aiki_home',
        relation=RelationType.USES,
        target='mitm_proxy',
        properties={'role': 'traffic_interception'}
    ))

    graph.add_relation(Relation(
        source='aiki_home',
        relation=RelationType.USES,
        target='decision_engine',
        properties={'role': 'rule_evaluation'}
    ))

    graph.add_relation(Relation(
        source='aiki_home',
        relation=RelationType.ENFORCES,
        target='morning_workout_rule',
        properties={'priority': 'high'}
    ))

    graph.add_relation(Relation(
        source='aiki_home',
        relation=RelationType.ENFORCES,
        target='work_hours_rule',
        properties={'priority': 'medium'}
    ))

    graph.add_relation(Relation(
        source='morning_workout_rule',
        relation=RelationType.REQUIRES,
        target='motion_sensor',
        properties={'for': 'verification'}
    ))

    graph.add_relation(Relation(
        source='aiki_home',
        relation=RelationType.REQUIRES,
        target='raspberry_pi',
        properties={'for': 'production_deployment'}
    ))

    graph.add_relation(Relation(
        source='mitm_proxy',
        relation=RelationType.DEPENDS_ON,
        target='decision_engine',
        properties={'communication': 'FastAPI'}
    ))

    return graph


if __name__ == "__main__":
    print("🕸️ Creating AIKI-HOME Knowledge Graph...")

    graph = create_aiki_home_graph()

    print("\n" + graph.visualize())

    # Test path finding
    print("\n🔍 GRAPH QUERIES:\n")
    path = graph.query_path('jovnna', 'motion_sensor')
    if path:
        print(f"Path from Jovnna to Motion Sensor:")
        print(" → ".join([graph.entities[e].name for e in path]))

    path = graph.query_path('adhd', 'mitm_proxy')
    if path:
        print(f"\nPath from ADHD to MITM Proxy:")
        print(" → ".join([graph.entities[e].name for e in path]))

    # Export
    export_path = Path("/home/jovnna/aiki/aiki_home_graph.json")
    graph.export_json(export_path)
    print(f"\n✅ Graph exported to: {export_path}")
