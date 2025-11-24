#!/usr/bin/env python3
"""
MINI-AIKI 8: COLLECTIVE KNOWLEDGE

Purpose: "Memory management + shared wisdom"

Strategy: Stores learnings in mem0, retrieves relevant knowledge for tasks.
Builds collective intelligence across AIKI ecosystem.

NOW INTEGRATED WITH MEM0!
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, Any
import logging

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.mini_aikis.base_mini_aiki import BaseMiniAiki, MiniAikiTask
from src.aiki_mem0 import store_memory, search_memory, get_all_memories

logger = logging.getLogger(__name__)


class CollectiveKnowledge(BaseMiniAiki):
    def __init__(self):
        super().__init__(
            mini_id="mini_8_collective",
            purpose="Memory management + shared wisdom",
            parent_circle="social",
            responsibilities=["Store learnings in mem0", "Retrieve relevant knowledge", "Build knowledge graph"]
        )
        self.metrics = {'learnings_stored': 0, 'knowledge_retrieved': 0, 'wisdom_score': 0.0}

    async def _execute_task(self, task: MiniAikiTask) -> Any:
        """Execute Collective Knowledge task - NOW USES REAL MEM0!"""
        action = task.input_data.get('action', 'store_learning')

        if action == 'store_learning':
            # REAL mem0 storage!
            learning = task.input_data.get('learning', '')

            try:
                result = await store_memory(
                    content=learning,
                    agent_id=self.mini_id,
                    metadata={
                        "type": "learning",
                        "component": task.input_data.get('component', 'unknown'),
                        "parent_circle": self.parent_circle
                    }
                )

                self.metrics['learnings_stored'] += 1
                self.metrics['wisdom_score'] = min(1.0, self.metrics['learnings_stored'] / 100)

                # Extract knowledge ID from result
                knowledge_id = None
                if result and 'results' in result and len(result['results']) > 0:
                    knowledge_id = result['results'][0].get('id', f"knowledge_{len(self.tasks)}")

                logger.info(f"📚 Stored learning in mem0: {learning[:80]}...")

                return {
                    'learning': learning,
                    'stored_in_mem0': True,
                    'knowledge_id': knowledge_id,
                    'total_learnings': self.metrics['learnings_stored']
                }

            except Exception as e:
                logger.error(f"❌ Failed to store learning in mem0: {e}")
                return {
                    'learning': learning,
                    'stored_in_mem0': False,
                    'error': str(e)
                }

        elif action == 'retrieve_knowledge':
            # REAL mem0 search!
            query = task.input_data.get('query', '')
            limit = task.input_data.get('limit', 5)

            try:
                results = await search_memory(
                    query=query,
                    limit=limit,
                    filters={"type": "learning"}  # Only get learnings
                )

                self.metrics['knowledge_retrieved'] += len(results)

                relevant_knowledge = [r['memory'] for r in results]
                confidence = results[0]['score'] if results else 0.0

                logger.info(f"🔍 Retrieved {len(results)} relevant knowledge for: {query[:50]}...")

                return {
                    'query': query,
                    'relevant_knowledge': relevant_knowledge,
                    'confidence': confidence,
                    'count': len(results)
                }

            except Exception as e:
                logger.error(f"❌ Failed to retrieve knowledge from mem0: {e}")
                return {
                    'query': query,
                    'relevant_knowledge': [],
                    'confidence': 0.0,
                    'error': str(e)
                }

        elif action == 'get_all_learnings':
            # Get ALL learnings stored by this mini-AIKI
            try:
                all_memories = await get_all_memories(agent_id=self.mini_id)

                logger.info(f"📚 Retrieved {len(all_memories)} total learnings")

                return {
                    'total_learnings': len(all_memories),
                    'learnings': [m.get('memory', '') for m in all_memories[:10]],  # First 10
                    'wisdom_score': self.metrics['wisdom_score']
                }

            except Exception as e:
                logger.error(f"❌ Failed to get all learnings: {e}")
                return {'error': str(e)}

        return {}


async def main():
    knowledge = CollectiveKnowledge()
    task_id = await knowledge.assign_task('store', 'Store learning', {
        'action': 'store_learning',
        'learning': 'Swarm consensus works well for classification'
    })
    await knowledge._process_tasks()
    print(knowledge.get_task_result(task_id))


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
