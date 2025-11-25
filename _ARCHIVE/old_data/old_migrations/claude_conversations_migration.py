#!/usr/bin/env python3
"""
Claude Conversations Migration to mem0
Migrates Claude Desktop conversations to mem0/Qdrant
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import asyncio

from mem0 import Memory

# Paths
CLAUDE_CHATS = Path("/home/jovnna/aiki/ClaudeChats/conversations.json")
BATCH1 = Path("/home/jovnna/aiki/batch1_conversations.json")
BATCH2 = Path("/home/jovnna/aiki/batch2_conversations.json")
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


class ClaudeConversationMigrator:
    """Handles migration of Claude Desktop conversations to mem0"""

    def __init__(self):
        self.memory = Memory.from_config(config)
        self.stats = {
            'total_conversations': 0,
            'total_messages': 0,
            'migrated_conversations': 0,
            'migrated_messages': 0,
            'failed': 0,
            'skipped_empty': 0
        }

    def load_json(self, filepath: Path) -> List[Dict[str, Any]]:
        """Load and parse JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading {filepath}: {e}")
            return []

    def extract_conversation_summary(self, conversation: Dict[str, Any], format_type: str) -> str:
        """Extract key information from conversation for memory storage"""

        if format_type == 'full':  # ClaudeChats format
            name = conversation.get('name', 'Untitled')
            created = conversation.get('created_at', '')
            messages = conversation.get('chat_messages', [])

            # Build conversation text
            conv_text = f"Conversation: {name}\nDate: {created}\n\n"

            # Add sample messages (first 2 exchanges)
            for i, msg in enumerate(messages[:4]):  # First 2 human + 2 assistant
                sender = msg.get('sender', 'unknown')
                text = msg.get('text', '')
                conv_text += f"{sender}: {text[:500]}...\n\n" if len(text) > 500 else f"{sender}: {text}\n\n"

            if len(messages) > 4:
                conv_text += f"[...{len(messages) - 4} more messages]\n"

            return conv_text

        else:  # batch format
            name = conversation.get('name', 'Untitled')
            created = conversation.get('created', '')
            messages = conversation.get('messages', '')
            message_count = conversation.get('message_count', 0)

            conv_text = f"Conversation: {name}\nDate: {created}\nMessages: {message_count}\n\n"

            # messages is already a string in batch format
            if messages:
                conv_text += messages[:1000] + ("..." if len(messages) > 1000 else "")

            return conv_text

    async def migrate_file(self, filepath: Path, format_type: str):
        """Migrate conversations from a single file"""
        print(f"\n📂 Migrating {filepath.name} ({format_type} format)...")

        data = self.load_json(filepath)
        if not data:
            print(f"  ⚠️  No data found")
            return

        self.stats['total_conversations'] += len(data)

        migrated = 0
        for i, conversation in enumerate(data):
            try:
                # Skip empty conversations
                if format_type == 'full':
                    messages = conversation.get('chat_messages', [])
                    msg_count = len(messages)
                    self.stats['total_messages'] += msg_count
                else:
                    msg_count = conversation.get('message_count', 0)
                    self.stats['total_messages'] += msg_count

                if msg_count == 0:
                    self.stats['skipped_empty'] += 1
                    continue

                # Extract conversation text
                conv_text = self.extract_conversation_summary(conversation, format_type)

                # Add to mem0
                result = self.memory.add(
                    [{'role': 'user', 'content': conv_text}],
                    user_id='jovnna',
                    metadata={
                        'source': 'claude_desktop',
                        'file': str(filepath.name),
                        'format': format_type,
                        'conversation_name': conversation.get('name', 'Untitled'),
                        'migrated_at': datetime.now().isoformat()
                    }
                )

                if result:
                    migrated += 1
                    self.stats['migrated_conversations'] += 1
                    if i % 10 == 0:  # Progress every 10 conversations
                        print(f"  📊 Progress: {i+1}/{len(data)} conversations...")

            except Exception as e:
                print(f"  ❌ Error migrating conversation {i}: {e}")
                self.stats['failed'] += 1

        print(f"  ✅ {migrated}/{len(data)} conversations migrated from {filepath.name}")

    async def migrate_all(self):
        """Migrate all Claude conversation files"""
        print("🚀 Starting Claude Conversations Migration...")
        print(f"💾 Target: Qdrant @ {QDRANT_PATH}")
        print("=" * 60)

        # Migrate ClaudeChats (full format)
        if CLAUDE_CHATS.exists():
            await self.migrate_file(CLAUDE_CHATS, 'full')
        else:
            print(f"⚠️  {CLAUDE_CHATS} not found")

        # Migrate batch files (simplified format)
        if BATCH1.exists():
            await self.migrate_file(BATCH1, 'batch')

        if BATCH2.exists():
            await self.migrate_file(BATCH2, 'batch')

        # Print final stats
        print("\n" + "=" * 60)
        print("🎉 CLAUDE CONVERSATIONS MIGRATION COMPLETE!")
        print(f"✅ Conversations migrated: {self.stats['migrated_conversations']}/{self.stats['total_conversations']}")
        print(f"📊 Total messages: {self.stats['total_messages']}")
        print(f"⏭️  Skipped (empty): {self.stats['skipped_empty']}")
        print(f"❌ Failed: {self.stats['failed']}")


async def main():
    """Main migration entry point"""
    migrator = ClaudeConversationMigrator()
    await migrator.migrate_all()


if __name__ == "__main__":
    asyncio.run(main())
