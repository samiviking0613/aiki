# Archived Migration Scripts

**Date**: 2025-11-17
**Reason**: Replaced by MASTER_MIGRATION.py

## What happened

These scripts were part of the initial memory migration work. They wrote to the **wrong database** (file-based Qdrant) instead of the Qdrant server.

User caught this issue and we created a unified solution: `MASTER_MIGRATION.py`

## Archived files:

- `aiki_memory_migration.py` - AIKI v3 JSON migration (superseded)
- `claude_conversations_migration.py` - Claude chats migration (superseded)
- `chatgpt_conversations_migration.py` - ChatGPT migration (superseded)
- `aiki_memory_graph.py` - Knowledge graph builder (superseded)
- `aiki_procedural_memory.py` - Procedural skills extractor (superseded)
- `aiki_home_graph.json` - Generated graph data
- `procedural_skills.json` - Generated skills data

## Active files (in ~/aiki/):

- `MASTER_MIGRATION.py` - Unified migration script (CORRECT)
- `CORRECT_CONFIG.py` - Correct Qdrant server config
- `memory_coverage_analyzer.py` - Memory coverage checker

## Final result:

587 memories in ONE database: `localhost:6333/mem0_memories`

NO memories in wrong database: `shared_qdrant/aiki_memories` = 0

User's catch prevented massive duplication and chaos!
