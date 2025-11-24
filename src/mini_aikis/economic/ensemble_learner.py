#!/usr/bin/env python3
"""
MINI-AIKI 2: ENSEMBLE LEARNER

Purpose: "Combine multiple models weighted by expertise"

Strategy:
- Run multiple models in parallel (ensemble)
- Weight responses by model expertise for task type
- Learn optimal weights over time
- Higher accuracy than single model

Responsibilities:
- Maintain expertise scores per model per task type
- Route tasks to ensemble of 3-5 models
- Combine results via weighted voting
- Update weights based on ground truth feedback
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, Any, List
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.mini_aikis.base_mini_aiki import BaseMiniAiki, MiniAikiTask


class EnsembleLearner(BaseMiniAiki):
    """
    Ensemble Learner - Combines multiple models weighted by expertise

    Learns which models are best for which task types.
    Uses weighted voting to combine predictions.
    """

    def __init__(self):
        super().__init__(
            mini_id="mini_2_ensemble",
            purpose="Combine multiple models weighted by expertise",
            parent_circle="economic",
            responsibilities=[
                "Maintain expertise scores (model × task_type)",
                "Select ensemble of 3-5 models per task",
                "Combine results via weighted voting",
                "Update weights based on feedback",
                "Track ensemble accuracy vs single model"
            ]
        )

        # Expertise matrix: expertise[task_type][model] = score (0.0-1.0)
        self.expertise: Dict[str, Dict[str, float]] = defaultdict(lambda: {
            'haiku-4.5': 0.6,
            'sonnet-4.5': 0.8,
            'opus-4': 0.9,
            'gemini-flash': 0.7,
            'gpt-4o-mini': 0.65
        })

        # Metrics
        self.metrics = {
            'total_ensemble_tasks': 0,
            'average_ensemble_accuracy': 0.0,
            'average_single_accuracy': 0.0,
            'ensemble_improvement': 0.0
        }

    async def _execute_task(self, task: MiniAikiTask) -> Any:
        """
        Execute ensemble learning task

        Input: {
            'task_type': str,
            'task_description': str,
            'ensemble_size': int (3-5)
        }
        Output: {
            'ensemble': List[str],  # Models selected
            'weights': Dict[str, float],  # Weight per model
            'rationale': str
        }
        """
        task_type = task.input_data.get('task_type', 'general')
        ensemble_size = task.input_data.get('ensemble_size', 3)

        # Get expertise scores for this task type
        expertise_scores = self.expertise[task_type]

        # Select top N models by expertise
        sorted_models = sorted(
            expertise_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:ensemble_size]

        ensemble = [model for model, _ in sorted_models]
        weights = {model: score for model, score in sorted_models}

        # Normalize weights
        total_weight = sum(weights.values())
        weights = {m: w / total_weight for m, w in weights.items()}

        # Update metrics
        self.metrics['total_ensemble_tasks'] += 1

        return {
            'ensemble': ensemble,
            'weights': weights,
            'rationale': f"Ensemble of {ensemble_size} models for {task_type}",
            'task_type': task_type
        }

    async def update_expertise(
        self,
        task_type: str,
        model: str,
        accuracy: float
    ):
        """
        Update expertise score based on feedback

        Called after ground truth is known.
        Uses exponential moving average.
        """
        if model not in self.expertise[task_type]:
            self.expertise[task_type][model] = 0.5

        # Exponential moving average (alpha=0.3)
        alpha = 0.3
        current = self.expertise[task_type][model]
        self.expertise[task_type][model] = alpha * accuracy + (1 - alpha) * current


async def main():
    """Test Ensemble Learner"""
    learner = EnsembleLearner()

    # Assign ensemble task
    task_id = await learner.assign_task(
        task_type='ensemble_selection',
        description='Select ensemble for classification task',
        input_data={
            'task_type': 'classification',
            'task_description': 'Classify sentiment',
            'ensemble_size': 3
        }
    )

    # Process
    await learner._process_tasks()

    # Get result
    result = learner.get_task_result(task_id)
    print(f"\nEnsemble result: {result}")

    # Update expertise (simulated feedback)
    await learner.update_expertise('classification', 'haiku-4.5', 0.85)
    await learner.update_expertise('classification', 'sonnet-4.5', 0.92)
    await learner.update_expertise('classification', 'opus-4', 0.88)

    print(f"\nUpdated expertise: {dict(learner.expertise['classification'])}")
    print(f"Metrics: {learner.metrics}")


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
