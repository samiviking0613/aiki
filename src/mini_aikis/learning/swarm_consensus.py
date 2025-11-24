#!/usr/bin/env python3
"""
MINI-AIKI 5: SWARM CONSENSUS

Purpose: "Run swarm of 7 small models, combine via voting"

Strategy: Run 7× small/cheap models simultaneously, combine via majority/weighted voting.
Cheap but accurate due to diversity of perspectives.

Models in swarm (configurable):
- haiku-3.5
- gemini-flash
- llama-3.3-70b
- deepseek-v3
- qwen-2.5
- phi-3-mini
- mistral-nemo

Voting Methods:
- majority: Simple majority wins (4/7 or more)
- weighted: Weight by historical accuracy
- ice: Iterative Consensus (outliers discarded, re-vote)
"""

import asyncio
import sys
import random
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.mini_aikis.base_mini_aiki import BaseMiniAiki, MiniAikiTask


@dataclass
class SwarmModel:
    """A model in the swarm"""
    name: str
    provider: str
    cost_per_1k: float  # NOK per 1k tokens
    historical_accuracy: float = 0.75
    response_time_avg: float = 1.0  # seconds


class SwarmConsensus(BaseMiniAiki):
    """
    Swarm Consensus - Runs 7 small models and combines via voting

    Key insight: Diverse cheap models often outperform single expensive model.
    """

    def __init__(self):
        super().__init__(
            mini_id="mini_5_swarm",
            purpose="Run swarm of 7 small models, combine via voting",
            parent_circle="learning",
            responsibilities=[
                "Run 7 small models in parallel",
                "Combine responses via voting",
                "Track swarm accuracy over time",
                "Optimize model selection based on task type",
                "Handle model failures gracefully"
            ]
        )

        # Available models for swarm
        self.available_models = [
            SwarmModel("haiku-3.5", "anthropic", 0.011, 0.78, 0.8),
            SwarmModel("gemini-flash", "google", 0.008, 0.75, 0.6),
            SwarmModel("llama-3.3-70b", "openrouter", 0.012, 0.76, 1.2),
            SwarmModel("deepseek-v3", "openrouter", 0.005, 0.74, 1.5),
            SwarmModel("qwen-2.5-max", "openrouter", 0.007, 0.73, 1.0),
            SwarmModel("phi-3-mini", "openrouter", 0.003, 0.68, 0.5),
            SwarmModel("mistral-nemo", "openrouter", 0.004, 0.71, 0.7),
        ]

        # Metrics
        self.metrics = {
            'swarms_completed': 0,
            'total_consensus_achieved': 0,
            'average_agreement_rate': 0.0,
            'average_confidence': 0.0,
            'model_accuracies': {m.name: m.historical_accuracy for m in self.available_models}
        }

        # Pheromone trails (stigmergy) - learned preferences
        self.pheromone_trails = {
            'code_generation': {'haiku-3.5': 0.9, 'gemini-flash': 0.8},
            'parsing': {'phi-3-mini': 0.85, 'mistral-nemo': 0.8},
            'reasoning': {'llama-3.3-70b': 0.9, 'deepseek-v3': 0.85},
            'general': {m.name: 0.7 for m in self.available_models}
        }

    async def _execute_task(self, task: MiniAikiTask) -> Any:
        """
        Execute swarm consensus task

        Input: {
            'action': 'run_swarm',
            'prompt': str,
            'voting_method': 'majority' | 'weighted' | 'ice',
            'task_type': str (optional - for model selection),
            'num_models': int (optional, default 7)
        }

        Output: {
            'consensus_result': str,
            'confidence': float,
            'agreement_rate': float,
            'individual_responses': List[Dict],
            'cost': float
        }
        """
        action = task.input_data.get('action', 'run_swarm')

        if action == 'run_swarm':
            return await self._run_swarm(
                prompt=task.input_data.get('prompt', ''),
                voting_method=task.input_data.get('voting_method', 'majority'),
                task_type=task.input_data.get('task_type', 'general'),
                num_models=task.input_data.get('num_models', 7)
            )
        elif action == 'get_model_stats':
            return self._get_model_stats()
        elif action == 'update_accuracy':
            return self._update_model_accuracy(
                model_name=task.input_data.get('model_name'),
                was_correct=task.input_data.get('was_correct', True)
            )
        else:
            return {'error': f'Unknown action: {action}'}

    async def _run_swarm(
        self,
        prompt: str,
        voting_method: str = 'majority',
        task_type: str = 'general',
        num_models: int = 7
    ) -> Dict[str, Any]:
        """Run the swarm and combine results"""

        # Select models based on task type and pheromones
        selected_models = self._select_models(task_type, num_models)

        # Run all models in parallel (simulated for now)
        responses = await self._query_models_parallel(selected_models, prompt)

        # Combine via voting
        consensus = self._combine_responses(responses, voting_method)

        # Calculate cost
        total_cost = sum(r.get('cost', 0) for r in responses)

        # Update metrics
        self.metrics['swarms_completed'] += 1
        if consensus['confidence'] > 0.7:
            self.metrics['total_consensus_achieved'] += 1

        # Update running average
        n = self.metrics['swarms_completed']
        self.metrics['average_agreement_rate'] = (
            (self.metrics['average_agreement_rate'] * (n - 1) + consensus['agreement_rate']) / n
        )
        self.metrics['average_confidence'] = (
            (self.metrics['average_confidence'] * (n - 1) + consensus['confidence']) / n
        )

        # Deposit pheromones for successful models
        if consensus['confidence'] > 0.8:
            self._deposit_pheromones(task_type, consensus['agreeing_models'])

        return {
            'consensus_result': consensus['result'],
            'confidence': consensus['confidence'],
            'agreement_rate': consensus['agreement_rate'],
            'voting_method': voting_method,
            'models_used': [m.name for m in selected_models],
            'individual_responses': responses,
            'cost': total_cost,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

    def _select_models(self, task_type: str, num_models: int) -> List[SwarmModel]:
        """Select models based on task type and pheromone trails"""
        # Get pheromone scores for this task type
        pheromones = self.pheromone_trails.get(task_type, self.pheromone_trails['general'])

        # Score each model
        scored_models = []
        for model in self.available_models:
            score = (
                pheromones.get(model.name, 0.5) * 0.4 +  # Pheromone weight
                model.historical_accuracy * 0.4 +         # Accuracy weight
                (1 / model.cost_per_1k) * 0.1 +          # Cost efficiency
                (1 / model.response_time_avg) * 0.1      # Speed
            )
            scored_models.append((model, score))

        # Sort by score and select top N
        scored_models.sort(key=lambda x: x[1], reverse=True)
        return [m for m, _ in scored_models[:num_models]]

    async def _query_models_parallel(
        self,
        models: List[SwarmModel],
        prompt: str
    ) -> List[Dict[str, Any]]:
        """Query all models in parallel"""
        # For now, simulate responses
        # In production, this would make actual API calls

        responses = []
        possible_answers = ['A', 'B', 'C']  # Simulated discrete answers

        for model in models:
            # Simulate model response with some variance
            if random.random() < model.historical_accuracy:
                answer = 'A'  # "Correct" answer
            else:
                answer = random.choice(['B', 'C'])

            response = {
                'model': model.name,
                'answer': answer,
                'confidence': random.uniform(0.6, 0.95),
                'cost': model.cost_per_1k * 0.5,  # ~500 tokens
                'latency': model.response_time_avg * random.uniform(0.8, 1.2)
            }
            responses.append(response)

            # Simulate async delay
            await asyncio.sleep(0.01)

        return responses

    def _combine_responses(
        self,
        responses: List[Dict[str, Any]],
        method: str
    ) -> Dict[str, Any]:
        """Combine responses using specified voting method"""

        if method == 'majority':
            return self._majority_vote(responses)
        elif method == 'weighted':
            return self._weighted_vote(responses)
        elif method == 'ice':
            return self._ice_vote(responses)
        else:
            return self._majority_vote(responses)

    def _majority_vote(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Simple majority voting"""
        answers = [r['answer'] for r in responses]
        counter = Counter(answers)

        most_common = counter.most_common(1)[0]
        result = most_common[0]
        count = most_common[1]

        agreement_rate = count / len(responses)
        confidence = agreement_rate * 0.9 + 0.1  # Scale to 0.1-1.0

        agreeing_models = [r['model'] for r in responses if r['answer'] == result]

        return {
            'result': result,
            'agreement_rate': agreement_rate,
            'confidence': confidence,
            'agreeing_models': agreeing_models,
            'vote_distribution': dict(counter)
        }

    def _weighted_vote(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Weighted voting by historical accuracy"""
        weighted_scores = {}

        for r in responses:
            model_name = r['model']
            answer = r['answer']
            weight = self.metrics['model_accuracies'].get(model_name, 0.7)

            if answer not in weighted_scores:
                weighted_scores[answer] = 0
            weighted_scores[answer] += weight

        # Find winner
        result = max(weighted_scores, key=weighted_scores.get)
        total_weight = sum(weighted_scores.values())

        agreement_rate = weighted_scores[result] / total_weight
        confidence = min(agreement_rate * 1.1, 1.0)  # Slightly boost weighted confidence

        agreeing_models = [r['model'] for r in responses if r['answer'] == result]

        return {
            'result': result,
            'agreement_rate': agreement_rate,
            'confidence': confidence,
            'agreeing_models': agreeing_models,
            'weighted_scores': weighted_scores
        }

    def _ice_vote(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Iterative Consensus Estimation (ICE)

        1. Get initial majority
        2. Identify outliers (responses far from majority)
        3. Discard outliers
        4. Re-vote with remaining
        5. Repeat until consensus or minimum models reached
        """
        working_responses = responses.copy()
        min_models = 3  # Minimum models to keep

        for iteration in range(3):  # Max 3 iterations
            if len(working_responses) <= min_models:
                break

            # Get current majority
            answers = [r['answer'] for r in working_responses]
            counter = Counter(answers)
            majority_answer = counter.most_common(1)[0][0]
            majority_count = counter.most_common(1)[0][1]

            # If strong consensus, stop
            if majority_count / len(working_responses) >= 0.8:
                break

            # Remove outliers (those not in majority)
            working_responses = [r for r in working_responses if r['answer'] == majority_answer]

        # Final vote on remaining
        return self._majority_vote(working_responses)

    def _deposit_pheromones(self, task_type: str, agreeing_models: List[str]):
        """Deposit pheromones for models that agreed with consensus"""
        if task_type not in self.pheromone_trails:
            self.pheromone_trails[task_type] = {}

        for model_name in agreeing_models:
            current = self.pheromone_trails[task_type].get(model_name, 0.5)
            # Increase pheromone (with decay toward 1.0)
            self.pheromone_trails[task_type][model_name] = min(current + 0.05, 1.0)

    def _update_model_accuracy(self, model_name: str, was_correct: bool) -> Dict:
        """Update model accuracy based on feedback"""
        if model_name not in self.metrics['model_accuracies']:
            return {'error': f'Unknown model: {model_name}'}

        current = self.metrics['model_accuracies'][model_name]
        # Exponential moving average
        alpha = 0.1
        new_accuracy = current * (1 - alpha) + (1.0 if was_correct else 0.0) * alpha
        self.metrics['model_accuracies'][model_name] = new_accuracy

        return {
            'model': model_name,
            'old_accuracy': current,
            'new_accuracy': new_accuracy
        }

    def _get_model_stats(self) -> Dict[str, Any]:
        """Get statistics for all models"""
        return {
            'model_accuracies': self.metrics['model_accuracies'],
            'pheromone_trails': self.pheromone_trails,
            'swarms_completed': self.metrics['swarms_completed'],
            'average_confidence': self.metrics['average_confidence']
        }


async def main():
    """Test Swarm Consensus"""
    import logging
    logging.basicConfig(level=logging.INFO)

    swarm = SwarmConsensus()

    # Test 1: Run swarm with majority voting
    print("\n=== Test 1: Majority Voting ===")
    task_id = await swarm.assign_task(
        task_type='swarm',
        description='Run swarm consensus',
        input_data={
            'action': 'run_swarm',
            'prompt': 'What is 2+2?',
            'voting_method': 'majority',
            'task_type': 'reasoning'
        }
    )
    await swarm._process_tasks()
    result = swarm.get_task_result(task_id)
    print(f"Result: {result}")

    # Test 2: Weighted voting
    print("\n=== Test 2: Weighted Voting ===")
    task_id = await swarm.assign_task(
        task_type='swarm',
        description='Run weighted swarm',
        input_data={
            'action': 'run_swarm',
            'prompt': 'Parse this JSON',
            'voting_method': 'weighted',
            'task_type': 'parsing'
        }
    )
    await swarm._process_tasks()
    result = swarm.get_task_result(task_id)
    print(f"Result: {result}")

    # Test 3: ICE voting
    print("\n=== Test 3: ICE Voting ===")
    task_id = await swarm.assign_task(
        task_type='swarm',
        description='Run ICE consensus',
        input_data={
            'action': 'run_swarm',
            'prompt': 'Complex reasoning task',
            'voting_method': 'ice',
            'task_type': 'reasoning'
        }
    )
    await swarm._process_tasks()
    result = swarm.get_task_result(task_id)
    print(f"Result: {result}")

    # Print final metrics
    print(f"\n=== Final Metrics ===")
    print(f"Swarms completed: {swarm.metrics['swarms_completed']}")
    print(f"Average confidence: {swarm.metrics['average_confidence']:.2f}")
    print(f"Average agreement: {swarm.metrics['average_agreement_rate']:.2f}")


if __name__ == "__main__":
    asyncio.run(main())
