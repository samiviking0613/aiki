#!/usr/bin/env python3
"""
ChatGPT Conversations Migration to mem0
Migrates ChatGPT text conversation dumps to mem0/Qdrant
"""

import os
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Tuple
import asyncio

from mem0 import Memory

# Paths - Only unique conversations (oppryddet is cleaned version of tråd 1)
CHATGPT_FILES = [
    Path("/run/media/jovnna/CEVAULT2TB/AIKI_v3/ChatGPT_tråd_1_oppryddet.txt"),  # Cleaned version only
    Path("/run/media/jovnna/CEVAULT2TB/AIKI_v3/chatgpt-4.1 analyser_040825.txt"),  # Separate analysis conversation
]
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


class ChatGPTConversationParser:
    """Parses ChatGPT text conversation dumps"""

    def __init__(self):
        self.user_marker = "Du sa:"
        self.assistant_marker = "ChatGPT sa:"

    def parse_file(self, filepath: Path) -> List[Tuple[str, str]]:
        """Parse conversation file into exchanges (user, assistant)"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"❌ Error reading {filepath}: {e}")
            return []

        # Split by user messages
        exchanges = []

        # Find all user messages
        user_splits = content.split(self.user_marker)

        for split in user_splits[1:]:  # Skip first empty split
            if self.assistant_marker in split:
                parts = split.split(self.assistant_marker, 1)
                user_msg = parts[0].strip()
                assistant_msg = parts[1].strip() if len(parts) > 1 else ""

                # Skip empty exchanges
                if user_msg and assistant_msg:
                    exchanges.append((user_msg, assistant_msg))

        return exchanges

    def chunk_exchanges(self, exchanges: List[Tuple[str, str]], max_exchanges: int = 5) -> List[str]:
        """Chunk exchanges into digestible conversation segments"""
        chunks = []

        for i in range(0, len(exchanges), max_exchanges):
            chunk_exchanges = exchanges[i:i + max_exchanges]

            # Build conversation text
            chunk_text = ""
            for user_msg, assistant_msg in chunk_exchanges:
                # Truncate very long messages
                user_short = user_msg[:500] + "..." if len(user_msg) > 500 else user_msg
                assistant_short = assistant_msg[:1000] + "..." if len(assistant_msg) > 1000 else assistant_msg

                chunk_text += f"User: {user_short}\n\n"
                chunk_text += f"Assistant: {assistant_short}\n\n"
                chunk_text += "---\n\n"

            chunks.append(chunk_text)

        return chunks


class ChatGPTConversationMigrator:
    """Handles migration of ChatGPT text conversations to mem0"""

    def __init__(self):
        self.memory = Memory.from_config(config)
        self.parser = ChatGPTConversationParser()
        self.stats = {
            'total_files': 0,
            'total_exchanges': 0,
            'total_chunks': 0,
            'migrated_chunks': 0,
            'failed': 0,
            'skipped_missing': 0
        }

    async def migrate_file(self, filepath: Path):
        """Migrate a single ChatGPT conversation file"""
        if not filepath.exists():
            print(f"⏭️  Skipping {filepath.name} (not found)")
            self.stats['skipped_missing'] += 1
            return

        print(f"\n📂 Migrating {filepath.name}...")

        # Parse file
        exchanges = self.parser.parse_file(filepath)
        if not exchanges:
            print(f"  ⚠️  No exchanges found")
            return

        self.stats['total_exchanges'] += len(exchanges)
        print(f"  📊 Found {len(exchanges)} exchanges")

        # Chunk exchanges
        chunks = self.parser.chunk_exchanges(exchanges, max_exchanges=5)
        self.stats['total_chunks'] += len(chunks)
        print(f"  📦 Created {len(chunks)} chunks")

        # Migrate each chunk
        migrated = 0
        for i, chunk in enumerate(chunks):
            try:
                # Extract date from filename if possible
                date_match = re.search(r'(\d{6})', filepath.name)
                date_str = date_match.group(1) if date_match else "unknown"

                # Add to mem0
                result = self.memory.add(
                    [{'role': 'user', 'content': chunk}],
                    user_id='jovnna',
                    metadata={
                        'source': 'chatgpt_web',
                        'file': str(filepath.name),
                        'chunk_index': i,
                        'total_chunks': len(chunks),
                        'conversation_date': date_str,
                        'migrated_at': datetime.now().isoformat()
                    }
                )

                if result:
                    migrated += 1
                    self.stats['migrated_chunks'] += 1
                    if i % 10 == 0:
                        print(f"    Progress: {i+1}/{len(chunks)} chunks...")
                else:
                    print(f"    ⚠️  Chunk {i} returned no result")
                    self.stats['failed'] += 1

                # Small delay to respect rate limits
                await asyncio.sleep(0.5)

            except Exception as e:
                print(f"    ❌ Error migrating chunk {i}: {e}")
                self.stats['failed'] += 1

        print(f"  ✅ {migrated}/{len(chunks)} chunks migrated")

    async def migrate_all(self):
        """Migrate all ChatGPT conversation files"""
        print("🚀 Starting ChatGPT Conversations Migration...")
        print(f"💾 Target: Qdrant @ {QDRANT_PATH}")
        print("==" * 30)

        self.stats['total_files'] = len(CHATGPT_FILES)

        for filepath in CHATGPT_FILES:
            await self.migrate_file(filepath)

        # Print final stats
        print("\n" + "==" * 30)
        print("🎉 CHATGPT MIGRATION COMPLETE!")
        print(f"📁 Files processed: {self.stats['total_files'] - self.stats['skipped_missing']}/{self.stats['total_files']}")
        print(f"💬 Exchanges found: {self.stats['total_exchanges']}")
        print(f"📦 Total chunks: {self.stats['total_chunks']}")
        print(f"✅ Chunks migrated: {self.stats['migrated_chunks']}")
        print(f"⏭️  Skipped (missing): {self.stats['skipped_missing']}")
        print(f"❌ Failed: {self.stats['failed']}")


async def main():
    """Main migration entry point"""
    migrator = ChatGPTConversationMigrator()
    await migrator.migrate_all()


if __name__ == "__main__":
    asyncio.run(main())
