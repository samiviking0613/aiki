#!/usr/bin/env python3
"""
MINI-AIKI 1: HIERARCHICAL DECISION ENGINE

Purpose: "Route tasks hierarchically: CEO → Manager → Worker"

Strategy:
- CEO level: Opus-4 (very complex, strategic decisions)
- Manager level: Sonnet-4.5 (medium complexity, tactical)
- Worker level: Haiku-4.5 (trivial/simple, operational)

Target: 70% Worker, 20% Manager, 10% CEO

Responsibilities:
- Classify task complexity
- Route to appropriate tier
- Optimize for 70/20/10 distribution
- Track accuracy per tier
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, Any

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.mini_aikis.base_mini_aiki import BaseMiniAiki, MiniAikiTask


class HierarchicalEngine(BaseMiniAiki):
    """
    Hierarchical Decision Engine - Routes tasks CEO → Manager → Worker

    Uses 3-tier routing inspired by organizational hierarchy.
    Optimizes for cost while maintaining quality.
    """

    def __init__(self):
        super().__init__(
            mini_id="mini_1_hierarchical",
            purpose="Route tasks hierarchically: CEO → Manager → Worker",
            parent_circle="economic",
            responsibilities=[
                "Classify task complexity into 3 tiers",
                "Route trivial/simple to Worker (Haiku)",
                "Route medium to Manager (Sonnet)",
                "Route complex/strategic to CEO (Opus)",
                "Optimize for 70% Worker, 20% Manager, 10% CEO",
                "Track accuracy and cost per tier"
            ]
        )

        # Tier definitions
        self.tiers = {
            'worker': {
                'model': 'haiku-4.5',
                'cost_per_1k': 0.011,
                'target_pct': 70,
                'examples': ['simple parsing', 'classification', 'yes/no questions']
            },
            'manager': {
                'model': 'sonnet-4.5',
                'cost_per_1k': 0.033,
                'target_pct': 20,
                'examples': ['code generation', 'debugging', 'analysis']
            },
            'ceo': {
                'model': 'opus-4',
                'cost_per_1k': 0.165,
                'target_pct': 10,
                'examples': ['architecture', 'strategic decisions', 'system design']
            }
        }

        # Metrics
        self.metrics = {
            'total_routed': 0,
            'worker_pct': 0.0,
            'manager_pct': 0.0,
            'ceo_pct': 0.0,
            'worker_count': 0,
            'manager_count': 0,
            'ceo_count': 0
        }

    async def _execute_task(self, task: MiniAikiTask) -> Any:
        """
        Execute hierarchical routing task

        Input: {'task_description': str, 'estimated_tokens': int}
        Output: {'tier': str, 'model': str, 'cost_estimate': float, 'rationale': str}
        """
        task_desc = task.input_data.get('task_description', '')
        tokens = task.input_data.get('estimated_tokens', 1000)

        # Classify tier
        tier = self._classify_tier(task_desc, tokens)

        # Get tier info
        tier_info = self.tiers[tier]
        model = tier_info['model']
        cost = (tokens / 1000.0) * tier_info['cost_per_1k']

        # Update metrics
        self.metrics['total_routed'] += 1
        self.metrics[f'{tier}_count'] += 1

        # Update percentages
        total = self.metrics['total_routed']
        self.metrics['worker_pct'] = (self.metrics['worker_count'] / total) * 100
        self.metrics['manager_pct'] = (self.metrics['manager_count'] / total) * 100
        self.metrics['ceo_pct'] = (self.metrics['ceo_count'] / total) * 100

        return {
            'tier': tier,
            'model': model,
            'cost_estimate': cost,
            'rationale': f"Hierarchical routing: {tier.upper()} tier ({model})",
            'distribution': {
                'worker': self.metrics['worker_pct'],
                'manager': self.metrics['manager_pct'],
                'ceo': self.metrics['ceo_pct']
            }
        }

    def _classify_tier(self, task_desc: str, tokens: int) -> str:
        """
        Classify task into Worker, Manager, or CEO tier

        Simple heuristics for now - can be improved with ML.
        """
        desc_lower = task_desc.lower()

        # CEO indicators (complex, strategic)
        if any(word in desc_lower for word in [
            'architecture', 'system design', 'strategic',
            'entire codebase', 'comprehensive analysis'
        ]):
            return 'ceo'

        # Manager indicators (medium complexity)
        if any(word in desc_lower for word in [
            'code generation', 'debugging', 'refactor',
            'analyze', 'explain', 'implement'
        ]):
            return 'manager'

        # Worker indicators (simple, operational)
        if any(word in desc_lower for word in [
            'classify', 'parse', 'yes/no', 'true/false',
            'simple', 'quick', 'trivial'
        ]):
            return 'worker'

        # Default based on tokens
        if tokens < 1000:
            return 'worker'
        elif tokens < 5000:
            return 'manager'
        else:
            return 'ceo'


async def main():
    """Test Hierarchical Engine"""
    engine = HierarchicalEngine()

    # Assign some test tasks
    task_id_1 = await engine.assign_task(
        task_type='hierarchical_routing',
        description='Route simple classification task',
        input_data={
            'task_description': 'Classify this input as positive or negative',
            'estimated_tokens': 500
        }
    )

    task_id_2 = await engine.assign_task(
        task_type='hierarchical_routing',
        description='Route code generation task',
        input_data={
            'task_description': 'Generate a Python function for sorting',
            'estimated_tokens': 3000
        }
    )

    task_id_3 = await engine.assign_task(
        task_type='hierarchical_routing',
        description='Route architecture task',
        input_data={
            'task_description': 'Design comprehensive system architecture',
            'estimated_tokens': 10000
        }
    )

    # Process tasks
    await engine._process_tasks()

    # Get results
    result1 = engine.get_task_result(task_id_1)
    result2 = engine.get_task_result(task_id_2)
    result3 = engine.get_task_result(task_id_3)

    print(f"\nTask 1 (simple): {result1}")
    print(f"Task 2 (medium): {result2}")
    print(f"Task 3 (complex): {result3}")
    print(f"\nMetrics: {engine.metrics}")


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
