#!/usr/bin/env python3
"""
AIKI Memory Migration Pipeline
Migrates JSON memories from AIKI v3 to mem0/Qdrant
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import asyncio

# mem0 imports
from mem0 import Memory

# Paths
AIKI_V3_MEMORY = Path("/run/media/jovnna/CEVAULT2TB/AIKI_v3/AIKI_MEMORY")
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


class AIKIMemoryMigrator:
    """Handles migration of AIKI v3 JSON memories to mem0"""

    def __init__(self):
        self.memory = Memory.from_config(config)
        self.stats = {
            'total_files': 0,
            'migrated': 0,
            'failed': 0,
            'skipped': 0,
            'categories': {}
        }

    def load_json(self, filepath: Path) -> Dict[str, Any]:
        """Load and parse JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading {filepath}: {e}")
            return None

    def format_session_memory(self, data: Dict[str, Any]) -> str:
        """Format session JSON into natural text for mem0"""
        session_id = data.get('session_id', 'unknown')
        timestamp = data.get('timestamp', '')
        objectives = data.get('current_objectives', [])
        achievements = data.get('recent_achievements', [])
        summary = data.get('conversation_summary', '')

        text = f"""AIKI Session {session_id} ({timestamp})

Objectives:
{chr(10).join(f'- {obj}' for obj in objectives)}

Achievements:
{chr(10).join(f'- {ach.get("description", str(ach))}' for ach in achievements)}

Summary: {summary}

Services: {json.dumps(data.get('services_status', {}))}
Modified Files: {len(data.get('file_modifications', []))} files
"""
        return text

    def format_experience_memory(self, data: Dict[str, Any]) -> str:
        """Format experience JSON into natural text"""
        title = data.get('title', 'Untitled')
        description = data.get('description', '')
        lessons = data.get('lessons_learned', [])
        category = data.get('category', 'general')

        text = f"""Experience: {title}

{description}

Lessons Learned:
{chr(10).join(f'- {lesson}' for lesson in lessons)}

Category: {category}
"""
        return text

    def format_identity_memory(self, data: Dict[str, Any]) -> str:
        """Format identity JSON into natural text"""
        name = data.get('system_name', 'AIKI')
        version = data.get('version', '3.0.0')
        traits = data.get('traits', [])
        capabilities = data.get('capabilities', [])
        partners = data.get('collaboration_partners', [])

        text = f"""System Identity: {name} v{version}

Traits:
{chr(10).join(f'- {trait}' for trait in traits)}

Capabilities:
{chr(10).join(f'- {cap}' for cap in capabilities)}

Collaboration Partners:
{chr(10).join(f'- {partner}' for partner in partners)}

Philosophy: {data.get('development_philosophy', '')}
"""
        return text

    async def migrate_category(self, category: str, formatter_func):
        """Migrate all files in a category"""
        category_path = AIKI_V3_MEMORY / category

        if not category_path.exists():
            print(f"⏭️  Skipping {category} (not found)")
            return

        print(f"\n📂 Migrating {category.upper()}...")

        files = list(category_path.glob("*.json"))
        self.stats['categories'][category] = {
            'total': len(files),
            'migrated': 0,
            'failed': 0
        }

        for filepath in files:
            try:
                data = self.load_json(filepath)
                if not data:
                    self.stats['failed'] += 1
                    self.stats['categories'][category]['failed'] += 1
                    continue

                # Format as natural text
                text = formatter_func(data)

                # Add to mem0
                result = self.memory.add(
                    [{'role': 'user', 'content': text}],
                    user_id='aiki_v3_migration',
                    metadata={
                        'source': 'aiki_v3',
                        'category': category,
                        'original_file': str(filepath),
                        'migrated_at': datetime.now().isoformat()
                    }
                )

                # Verify result
                if result:
                    print(f"  ✅ {filepath.name} (result: {result})")
                    self.stats['migrated'] += 1
                    self.stats['categories'][category]['migrated'] += 1
                else:
                    print(f"  ⚠️  {filepath.name} (no result returned)")
                    self.stats['failed'] += 1
                    self.stats['categories'][category]['failed'] += 1

            except Exception as e:
                print(f"  ❌ {filepath.name}: {e}")
                self.stats['failed'] += 1
                self.stats['categories'][category]['failed'] += 1

        print(f"  📊 {category}: {self.stats['categories'][category]['migrated']}/{len(files)} migrated")

    async def migrate_all(self):
        """Migrate all memory categories"""
        print("🚀 Starting AIKI Memory Migration...")
        print(f"📁 Source: {AIKI_V3_MEMORY}")
        print(f"💾 Target: Qdrant @ {QDRANT_PATH}")
        print("=" * 60)

        # Count total files
        self.stats['total_files'] = len(list(AIKI_V3_MEMORY.glob("**/*.json")))
        print(f"📊 Total files found: {self.stats['total_files']}\n")

        # Migrate each category
        await self.migrate_category('identity', self.format_identity_memory)
        await self.migrate_category('sessions', self.format_session_memory)
        await self.migrate_category('experiences', self.format_experience_memory)
        await self.migrate_category('development', self.format_experience_memory)  # Same format
        await self.migrate_category('collaboration', self.format_experience_memory)  # Same format
        await self.migrate_category('claude', self.format_experience_memory)  # Same format

        # Print final stats
        print("\n" + "=" * 60)
        print("🎉 MIGRATION COMPLETE!")
        print(f"✅ Migrated: {self.stats['migrated']}")
        print(f"❌ Failed: {self.stats['failed']}")
        print(f"📊 Total: {self.stats['total_files']}")
        print("\nCategory Breakdown:")
        for cat, stats in self.stats['categories'].items():
            print(f"  {cat}: {stats['migrated']}/{stats['total']}")


async def main():
    """Main migration entry point"""
    migrator = AIKIMemoryMigrator()
    await migrator.migrate_all()


if __name__ == "__main__":
    asyncio.run(main())
