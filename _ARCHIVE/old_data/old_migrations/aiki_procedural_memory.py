#!/usr/bin/env python3
"""
AIKI Procedural Memory System
Stores workflows, skills, and "how-to" knowledge
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
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


class SkillCategory(Enum):
    """Skill categories"""
    DEBUGGING = "debugging"
    DEPLOYMENT = "deployment"
    CONFIGURATION = "configuration"
    DEVELOPMENT = "development"
    TESTING = "testing"
    MIGRATION = "migration"


class DifficultyLevel(Enum):
    """Difficulty levels"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


@dataclass
class WorkflowStep:
    """Single step in a workflow"""
    step_number: int
    action: str
    details: str
    expected_outcome: str
    common_errors: List[str] = None

    def __post_init__(self):
        if self.common_errors is None:
            self.common_errors = []


@dataclass
class Skill:
    """A procedural skill/workflow"""
    skill_id: str
    name: str
    category: SkillCategory
    description: str
    steps: List[WorkflowStep]
    prerequisites: List[str]
    tools_required: List[str]
    difficulty: DifficultyLevel
    estimated_time_minutes: int
    success_rate: float
    usage_count: int
    last_used: str
    created_date: str
    tags: List[str]

    def to_natural_language(self) -> str:
        """Convert skill to natural language for mem0 storage"""
        text = f"""PROCEDURAL SKILL: {self.name}

CATEGORY: {self.category.value}
DIFFICULTY: {self.difficulty.value}
ESTIMATED TIME: {self.estimated_time_minutes} minutes

DESCRIPTION:
{self.description}

PREREQUISITES:
{chr(10).join(f'- {p}' for p in self.prerequisites) if self.prerequisites else '- None'}

TOOLS REQUIRED:
{chr(10).join(f'- {t}' for t in self.tools_required) if self.tools_required else '- None'}

WORKFLOW STEPS:
"""
        for step in self.steps:
            text += f"\nStep {step.step_number}: {step.action}\n"
            text += f"  Details: {step.details}\n"
            text += f"  Expected: {step.expected_outcome}\n"
            if step.common_errors:
                text += f"  Common errors: {', '.join(step.common_errors)}\n"

        text += f"\nSUCCESS RATE: {self.success_rate*100:.0f}% ({self.usage_count} uses)"
        text += f"\nLAST USED: {self.last_used}"
        text += f"\nTAGS: {', '.join(self.tags)}"

        return text


class AIKIProceduralMemory:
    """Manages procedural memories (skills and workflows)"""

    def __init__(self, user_id: str = 'jovnna'):
        self.memory = Memory.from_config(config)
        self.user_id = user_id
        self.skills: Dict[str, Skill] = {}

    def add_skill(self, skill: Skill):
        """Add a skill to procedural memory"""
        self.skills[skill.skill_id] = skill

        # Store in mem0
        text = skill.to_natural_language()

        self.memory.add(
            [{'role': 'user', 'content': text}],
            user_id=self.user_id,
            metadata={
                'memory_type': 'procedural',
                'skill_id': skill.skill_id,
                'skill_category': skill.category.value,
                'difficulty': skill.difficulty.value,
                'estimated_time': skill.estimated_time_minutes,
                'success_rate': skill.success_rate,
                'tags': ','.join(skill.tags)
            }
        )

    def export_json(self, filepath: Path):
        """Export all skills to JSON"""
        data = {
            'skills': [
                {
                    **asdict(skill),
                    'category': skill.category.value,
                    'difficulty': skill.difficulty.value
                }
                for skill in self.skills.values()
            ]
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)


def extract_session_workflows() -> List[Skill]:
    """Extract workflows from today's session (2025-11-17)"""
    today = datetime.now().isoformat()

    skills = []

    # Skill 1: Fix SQLite Health Check Error
    skills.append(Skill(
        skill_id='fix_sqlite_health_check',
        name='Fix SQLite Health Check Error',
        category=SkillCategory.DEBUGGING,
        description='Resolve "cannot operate on closed database" error in health check by creating fresh database instance instead of reusing global singleton.',
        steps=[
            WorkflowStep(
                step_number=1,
                action='Identify symptom',
                details='health_check() fails with "cannot operate on closed database" error',
                expected_outcome='Error message clearly shows database connection issue',
                common_errors=['Misinterpreting as permission error', 'Thinking database is corrupted']
            ),
            WorkflowStep(
                step_number=2,
                action='Root cause analysis',
                details='Global singleton database instance is being reused across calls, causing connection conflicts',
                expected_outcome='Understanding that shared state is the problem',
                common_errors=['Trying to fix by reconnecting', 'Adding connection pooling']
            ),
            WorkflowStep(
                step_number=3,
                action='Implement solution',
                details='Create fresh SQLiteDatabase instance in health_check() method: test_db = SQLiteDatabase(db_path)',
                expected_outcome='Each health check gets isolated database connection',
                common_errors=['Forgetting to pass db_path', 'Not closing new connection']
            ),
            WorkflowStep(
                step_number=4,
                action='Verify fix',
                details='Run health monitoring, check that services show 2/2 healthy',
                expected_outcome='All services healthy, no connection errors',
                common_errors=['Not testing after fix', 'Only testing once']
            )
        ],
        prerequisites=['Python environment', 'SQLite database', 'Database manager class'],
        tools_required=['Python', 'aiosqlite', 'pytest (optional)'],
        difficulty=DifficultyLevel.MEDIUM,
        estimated_time_minutes=15,
        success_rate=1.0,
        usage_count=1,
        last_used=today,
        created_date=today,
        tags=['sqlite', 'debugging', 'database', 'health-check', 'singleton-pattern']
    ))

    # Skill 2: Setup MITM Proxy with Decision Engine
    skills.append(Skill(
        skill_id='setup_mitm_proxy',
        name='Setup MITM Proxy with Decision Engine',
        category=SkillCategory.DEPLOYMENT,
        description='Install and configure mitmproxy with custom addon that communicates with FastAPI decision engine for traffic filtering.',
        steps=[
            WorkflowStep(
                step_number=1,
                action='Install mitmproxy',
                details='pip install mitmproxy in virtual environment',
                expected_outcome='mitmproxy and mitmdump commands available',
                common_errors=['Installing globally instead of venv', 'Python version conflicts']
            ),
            WorkflowStep(
                step_number=2,
                action='Create proxy manager',
                details='Build MITMProxyManager class to control mitmdump as subprocess',
                expected_outcome='Can start/stop/restart proxy programmatically',
                common_errors=['Not handling process cleanup', 'Forgetting to check if already running']
            ),
            WorkflowStep(
                step_number=3,
                action='Create mitmproxy addon',
                details='Write addon script that intercepts requests and calls decision API',
                expected_outcome='Addon successfully hooks into request flow',
                common_errors=['Wrong addon API version', 'Not importing http module', 'Missing requests package']
            ),
            WorkflowStep(
                step_number=4,
                action='Build decision engine',
                details='Implement traffic rules: time-based blocks, site filtering, content injection',
                expected_outcome='Rules evaluate correctly based on context',
                common_errors=['Not handling timezones', 'Hardcoding user IDs']
            ),
            WorkflowStep(
                step_number=5,
                action='Create FastAPI endpoints',
                details='Build /api/intercept endpoint that receives traffic data and returns decisions',
                expected_outcome='Addon can communicate with decision engine',
                common_errors=['CORS issues', 'Timeout too short', 'Wrong response format']
            ),
            WorkflowStep(
                step_number=6,
                action='Test traffic flow',
                details='Use curl with -x proxy flag to test allow/block/inject scenarios',
                expected_outcome='All three decision types work correctly',
                common_errors=['Not configuring CA cert', 'Testing only HTTP not HTTPS', 'Forgetting to start FastAPI server']
            )
        ],
        prerequisites=['Python 3.10+', 'Virtual environment', 'FastAPI knowledge', 'Network basics'],
        tools_required=['mitmproxy', 'FastAPI', 'uvicorn', 'requests', 'curl (for testing)'],
        difficulty=DifficultyLevel.HARD,
        estimated_time_minutes=120,
        success_rate=1.0,
        usage_count=1,
        last_used=today,
        created_date=today,
        tags=['mitm', 'proxy', 'fastapi', 'network', 'traffic-filtering', 'adhd', 'aiki-home']
    ))

    # Skill 3: Migrate JSON Memories to mem0
    skills.append(Skill(
        skill_id='migrate_json_to_mem0',
        name='Migrate JSON Memories to mem0/Qdrant',
        category=SkillCategory.MIGRATION,
        description='Convert structured JSON memory files to natural language and store in mem0 vector database with intelligent deduplication.',
        steps=[
            WorkflowStep(
                step_number=1,
                action='Analyze JSON structure',
                details='Examine JSON files to understand schema and data types',
                expected_outcome='Clear understanding of all fields and their meanings',
                common_errors=['Not checking for variations in schema', 'Missing nested fields']
            ),
            WorkflowStep(
                step_number=2,
                action='Design formatters',
                details='Create functions to convert JSON to natural language text',
                expected_outcome='Readable, searchable text that preserves all important information',
                common_errors=['Too verbose', 'Losing metadata', 'Not handling edge cases']
            ),
            WorkflowStep(
                step_number=3,
                action='Setup mem0 config',
                details='Configure mem0 with OpenRouter for LLM and embeddings, Qdrant for storage',
                expected_outcome='mem0.add() calls work without errors',
                common_errors=['Wrong API keys', 'Invalid model names', 'Path permissions']
            ),
            WorkflowStep(
                step_number=4,
                action='Batch processing',
                details='Loop through files, format, and add to mem0 with metadata',
                expected_outcome='All files processed, mem0 deduplicates intelligently',
                common_errors=['Not handling API rate limits', 'Missing error handling', 'Wrong user_id']
            ),
            WorkflowStep(
                step_number=5,
                action='Verify migration',
                details='Use mem0.search() to test that memories are retrievable',
                expected_outcome='Can find memories using natural language queries',
                common_errors=['Not testing search', 'Assuming all data migrated without checking']
            )
        ],
        prerequisites=['JSON files to migrate', 'mem0 installed', 'OpenRouter API key', 'Qdrant database'],
        tools_required=['Python', 'mem0', 'json module', 'qdrant-client'],
        difficulty=DifficultyLevel.MEDIUM,
        estimated_time_minutes=45,
        success_rate=1.0,
        usage_count=2,
        last_used=today,
        created_date=today,
        tags=['migration', 'mem0', 'qdrant', 'json', 'embeddings', 'memory-system']
    ))

    # Skill 4: Create Knowledge Graph with mem0
    skills.append(Skill(
        skill_id='create_knowledge_graph_mem0',
        name='Create Knowledge Graph using mem0 Metadata',
        category=SkillCategory.DEVELOPMENT,
        description='Build entity-relationship graph by storing entities and relations in mem0 with structured metadata for graph queries.',
        steps=[
            WorkflowStep(
                step_number=1,
                action='Define entity types',
                details='Create Enum for entity types: Person, System, Rule, Hardware, etc.',
                expected_outcome='Clear taxonomy of all entity categories',
                common_errors=['Too many types', 'Overlapping categories']
            ),
            WorkflowStep(
                step_number=2,
                action='Define relation types',
                details='Create Enum for relationships: uses, requires, enforces, depends_on, etc.',
                expected_outcome='Comprehensive set of meaningful relationships',
                common_errors=['Too generic relations', 'Not bidirectional when needed']
            ),
            WorkflowStep(
                step_number=3,
                action='Create entity class',
                details='Dataclass with id, name, type, and properties dict',
                expected_outcome='Entities can store arbitrary metadata',
                common_errors=['Hardcoding properties', 'Missing validation']
            ),
            WorkflowStep(
                step_number=4,
                action='Create relation class',
                details='Dataclass linking source entity to target entity via relation type',
                expected_outcome='Relations are typed and queryable',
                common_errors=['Not storing relation properties', 'Circular reference bugs']
            ),
            WorkflowStep(
                step_number=5,
                action='Store in mem0',
                details='Convert entities/relations to text + metadata, store with memory_type tag',
                expected_outcome='Graph is searchable and queryable via mem0',
                common_errors=['Forgetting metadata', 'Not making text searchable']
            ),
            WorkflowStep(
                step_number=6,
                action='Implement graph queries',
                details='Build path finding (BFS), relation traversal, entity lookup',
                expected_outcome='Can answer "how is X connected to Y?" queries',
                common_errors=['Not handling cycles', 'Infinite loops', 'Missing entities']
            )
        ],
        prerequisites=['mem0 setup', 'Graph theory basics', 'Python dataclasses'],
        tools_required=['Python', 'mem0', 'dataclasses', 'typing module'],
        difficulty=DifficultyLevel.MEDIUM,
        estimated_time_minutes=60,
        success_rate=1.0,
        usage_count=1,
        last_used=today,
        created_date=today,
        tags=['knowledge-graph', 'mem0', 'entities', 'relations', 'graph-queries', 'metadata']
    ))

    # Skill 5: Enable Claude Code God Mode
    skills.append(Skill(
        skill_id='enable_claude_god_mode',
        name='Enable Claude Code God Mode (Auto-Accept Edits)',
        category=SkillCategory.CONFIGURATION,
        description='Configure Claude Code to automatically accept file edits without prompting user, eliminating confirmation friction.',
        steps=[
            WorkflowStep(
                step_number=1,
                action='Locate settings file',
                details='Find ~/.claude/settings.json (create if not exists)',
                expected_outcome='Settings file is accessible',
                common_errors=['Wrong path', 'Permission denied', 'JSON syntax errors']
            ),
            WorkflowStep(
                step_number=2,
                action='Add correct setting',
                details='Use permissions.defaultMode: "acceptEdits" NOT requireEditApproval: false',
                expected_outcome='Setting is valid and recognized',
                common_errors=['Using requireEditApproval (invalid)', 'Typo in "acceptEdits"', 'Wrong JSON structure']
            ),
            WorkflowStep(
                step_number=3,
                action='Restart Claude Code',
                details='Close and reopen Claude Code for settings to take effect',
                expected_outcome='New setting is loaded',
                common_errors=['Not restarting', 'Multiple instances running']
            ),
            WorkflowStep(
                step_number=4,
                action='Verify god mode',
                details='Make an edit, confirm no approval prompt appears',
                expected_outcome='Edits apply instantly without user confirmation',
                common_errors=['Testing with wrong file type', 'Hooks blocking edits']
            )
        ],
        prerequisites=['Claude Code installed', 'File system access'],
        tools_required=['Text editor', 'Claude Code'],
        difficulty=DifficultyLevel.EASY,
        estimated_time_minutes=5,
        success_rate=1.0,
        usage_count=1,
        last_used=today,
        created_date=today,
        tags=['claude-code', 'configuration', 'god-mode', 'settings', 'workflow-optimization']
    ))

    return skills


if __name__ == "__main__":
    print("🛠️ Extracting Procedural Memories from Session 2025-11-17...")

    memory_system = AIKIProceduralMemory()

    # Extract skills from today's session
    skills = extract_session_workflows()

    print(f"\n📚 Extracted {len(skills)} procedural skills:\n")

    for skill in skills:
        print(f"  • {skill.name}")
        print(f"    Category: {skill.category.value}")
        print(f"    Difficulty: {skill.difficulty.value}")
        print(f"    Time: ~{skill.estimated_time_minutes} min")
        print(f"    Steps: {len(skill.steps)}")
        print()

        # Add to memory system
        memory_system.add_skill(skill)

    # Export to JSON
    export_path = Path("/home/jovnna/aiki/procedural_skills.json")
    memory_system.export_json(export_path)

    print(f"✅ All skills stored in mem0 (Qdrant)")
    print(f"✅ Exported to: {export_path}")
    print(f"\n💡 Skills are now searchable via mem0!")
