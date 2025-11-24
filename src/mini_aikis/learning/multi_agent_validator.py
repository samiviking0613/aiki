#!/usr/bin/env python3
"""
MINI-AIKI 6: MULTI-AGENT VALIDATOR

Purpose: "Adversarial debate between models for validation"

Strategy: Two models debate opposite sides, third judges.
Increases accuracy through adversarial validation.

Debate Structure:
1. Proposer: Generates initial solution
2. Critic: Finds flaws and counterarguments
3. Judge: Evaluates both sides, makes final decision

This mirrors how human experts validate important decisions.
"""

import asyncio
import sys
import random
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.mini_aikis.base_mini_aiki import BaseMiniAiki, MiniAikiTask


class DebateRole(Enum):
    """Roles in adversarial debate"""
    PROPOSER = "proposer"
    CRITIC = "critic"
    JUDGE = "judge"


@dataclass
class DebateModel:
    """A model that can participate in debates"""
    name: str
    provider: str
    cost_per_1k: float
    reasoning_strength: float  # 0-1, how good at argumentation
    objectivity: float  # 0-1, how neutral (important for judge)


@dataclass
class DebateRound:
    """A single round of debate"""
    round_number: int
    proposer_argument: str
    critic_argument: str
    judge_score: float  # 0-1, how much judge agrees with proposer


class MultiAgentValidator(BaseMiniAiki):
    """
    Multi-Agent Validator - Adversarial debate for validation

    Key insight: Having AI debate itself catches errors single models miss.
    """

    def __init__(self):
        super().__init__(
            mini_id="mini_6_validator",
            purpose="Adversarial debate between models for validation",
            parent_circle="learning",
            responsibilities=[
                "Run adversarial debates",
                "Select appropriate models for each role",
                "Track validation accuracy",
                "Provide confidence scores",
                "Learn from debate outcomes"
            ]
        )

        # Available debate models
        self.available_models = [
            DebateModel("sonnet-4.5", "anthropic", 0.033, 0.92, 0.85),
            DebateModel("opus-4", "anthropic", 0.165, 0.95, 0.90),
            DebateModel("gemini-pro", "google", 0.025, 0.88, 0.82),
            DebateModel("gpt-4o", "openai", 0.055, 0.90, 0.87),
            DebateModel("llama-3.3-70b", "openrouter", 0.012, 0.85, 0.80),
            DebateModel("deepseek-v3", "openrouter", 0.005, 0.82, 0.78),
        ]

        # Role preferences (learned over time)
        self.role_preferences = {
            'proposer': {'sonnet-4.5': 0.9, 'gpt-4o': 0.85},
            'critic': {'opus-4': 0.95, 'gemini-pro': 0.85},
            'judge': {'opus-4': 0.9, 'sonnet-4.5': 0.85}  # Need high objectivity
        }

        # Metrics
        self.metrics = {
            'debates_completed': 0,
            'validation_accuracy': 0.0,
            'average_confidence': 0.0,
            'proposer_win_rate': 0.5,
            'debates_by_topic': {}
        }

    async def _execute_task(self, task: MiniAikiTask) -> Any:
        """
        Execute validation task

        Input: {
            'action': 'validate',
            'claim': str,  # The claim/solution to validate
            'context': str,  # Background context
            'rounds': int,  # Number of debate rounds (default 2)
            'topic': str  # Topic for learning preferences
        }

        Output: {
            'verdict': 'valid' | 'invalid' | 'uncertain',
            'confidence': float,
            'reasoning': str,
            'debate_transcript': List[DebateRound],
            'cost': float
        }
        """
        action = task.input_data.get('action', 'validate')

        if action == 'validate':
            return await self._run_validation(
                claim=task.input_data.get('claim', ''),
                context=task.input_data.get('context', ''),
                rounds=task.input_data.get('rounds', 2),
                topic=task.input_data.get('topic', 'general')
            )
        elif action == 'get_stats':
            return self._get_stats()
        elif action == 'update_preferences':
            return self._update_role_preferences(
                role=task.input_data.get('role'),
                model=task.input_data.get('model'),
                performance=task.input_data.get('performance', 0.8)
            )
        else:
            return {'error': f'Unknown action: {action}'}

    async def _run_validation(
        self,
        claim: str,
        context: str,
        rounds: int = 2,
        topic: str = 'general'
    ) -> Dict[str, Any]:
        """Run adversarial debate for validation"""

        # Select models for each role
        proposer = self._select_model_for_role('proposer', topic)
        critic = self._select_model_for_role('critic', topic)
        judge = self._select_model_for_role('judge', topic)

        # Run debate rounds
        debate_transcript = []
        total_cost = 0.0
        judge_scores = []

        for round_num in range(1, rounds + 1):
            round_result = await self._run_debate_round(
                round_num=round_num,
                claim=claim,
                context=context,
                proposer=proposer,
                critic=critic,
                judge=judge,
                previous_rounds=debate_transcript
            )

            debate_transcript.append(round_result['round'])
            total_cost += round_result['cost']
            judge_scores.append(round_result['round'].judge_score)

        # Final verdict based on judge scores
        avg_score = sum(judge_scores) / len(judge_scores)
        verdict, confidence = self._determine_verdict(avg_score, judge_scores)

        # Update metrics
        self.metrics['debates_completed'] += 1
        n = self.metrics['debates_completed']
        self.metrics['average_confidence'] = (
            (self.metrics['average_confidence'] * (n - 1) + confidence) / n
        )

        if verdict == 'valid':
            self.metrics['proposer_win_rate'] = (
                (self.metrics['proposer_win_rate'] * (n - 1) + 1) / n
            )
        elif verdict == 'invalid':
            self.metrics['proposer_win_rate'] = (
                (self.metrics['proposer_win_rate'] * (n - 1) + 0) / n
            )

        # Track by topic
        if topic not in self.metrics['debates_by_topic']:
            self.metrics['debates_by_topic'][topic] = {'count': 0, 'valid': 0}
        self.metrics['debates_by_topic'][topic]['count'] += 1
        if verdict == 'valid':
            self.metrics['debates_by_topic'][topic]['valid'] += 1

        return {
            'verdict': verdict,
            'confidence': confidence,
            'reasoning': self._generate_reasoning(debate_transcript, verdict),
            'models_used': {
                'proposer': proposer.name,
                'critic': critic.name,
                'judge': judge.name
            },
            'debate_transcript': [
                {
                    'round': r.round_number,
                    'proposer': r.proposer_argument,
                    'critic': r.critic_argument,
                    'judge_score': r.judge_score
                }
                for r in debate_transcript
            ],
            'average_judge_score': avg_score,
            'cost': total_cost,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

    def _select_model_for_role(self, role: str, topic: str) -> DebateModel:
        """Select best model for a given role"""
        preferences = self.role_preferences.get(role, {})

        # Score each model
        scored_models = []
        for model in self.available_models:
            base_score = preferences.get(model.name, 0.5)

            # Role-specific bonuses
            if role == 'proposer':
                score = base_score * 0.6 + model.reasoning_strength * 0.4
            elif role == 'critic':
                score = base_score * 0.5 + model.reasoning_strength * 0.5
            elif role == 'judge':
                score = base_score * 0.4 + model.objectivity * 0.6
            else:
                score = base_score

            scored_models.append((model, score))

        # Select best (with some randomness for exploration)
        scored_models.sort(key=lambda x: x[1], reverse=True)

        # 80% chance of best, 20% chance of second best
        if len(scored_models) > 1 and random.random() < 0.2:
            return scored_models[1][0]
        return scored_models[0][0]

    async def _run_debate_round(
        self,
        round_num: int,
        claim: str,
        context: str,
        proposer: DebateModel,
        critic: DebateModel,
        judge: DebateModel,
        previous_rounds: List[DebateRound]
    ) -> Dict[str, Any]:
        """Run a single debate round"""

        # Simulate proposer argument
        proposer_argument = await self._generate_argument(
            model=proposer,
            role='proposer',
            claim=claim,
            context=context,
            round_num=round_num,
            previous_rounds=previous_rounds
        )

        # Simulate critic argument
        critic_argument = await self._generate_argument(
            model=critic,
            role='critic',
            claim=claim,
            context=context,
            round_num=round_num,
            previous_rounds=previous_rounds,
            opposing_argument=proposer_argument
        )

        # Judge evaluates
        judge_score = await self._judge_round(
            judge=judge,
            proposer_argument=proposer_argument,
            critic_argument=critic_argument,
            claim=claim
        )

        # Calculate cost
        cost = (proposer.cost_per_1k + critic.cost_per_1k + judge.cost_per_1k) * 0.8

        round_result = DebateRound(
            round_number=round_num,
            proposer_argument=proposer_argument,
            critic_argument=critic_argument,
            judge_score=judge_score
        )

        return {
            'round': round_result,
            'cost': cost
        }

    async def _generate_argument(
        self,
        model: DebateModel,
        role: str,
        claim: str,
        context: str,
        round_num: int,
        previous_rounds: List[DebateRound],
        opposing_argument: Optional[str] = None
    ) -> str:
        """Generate argument for a role (simulated)"""
        # In production, this would call the actual LLM API

        await asyncio.sleep(0.01)  # Simulate API call

        if role == 'proposer':
            arguments = [
                f"The claim '{claim[:50]}...' is valid because the evidence supports it.",
                f"Analysis shows strong correlation supporting this conclusion.",
                f"Multiple data points confirm the validity of this statement.",
                f"The logical structure of this claim is sound and defensible."
            ]
        else:  # critic
            arguments = [
                f"The claim may be flawed due to insufficient evidence.",
                f"There are alternative explanations not considered.",
                f"The methodology has potential weaknesses.",
                f"Counter-evidence suggests this conclusion is premature."
            ]

        # Add round-specific context
        base_arg = random.choice(arguments)
        if round_num > 1 and previous_rounds:
            base_arg += f" Building on round {round_num-1} discussion."

        return base_arg

    async def _judge_round(
        self,
        judge: DebateModel,
        proposer_argument: str,
        critic_argument: str,
        claim: str
    ) -> float:
        """Judge evaluates the round (simulated)"""
        await asyncio.sleep(0.01)

        # Simulate judge decision based on model objectivity
        # Higher objectivity = more balanced scoring
        base_score = random.uniform(0.3, 0.7)

        # Adjust based on argument "quality" (simulated)
        prop_quality = random.uniform(0.6, 0.9)
        crit_quality = random.uniform(0.5, 0.8)

        score = base_score * 0.3 + prop_quality * 0.35 + (1 - crit_quality) * 0.35
        score = score * judge.objectivity + (1 - judge.objectivity) * random.uniform(0.4, 0.6)

        return max(0.0, min(1.0, score))

    def _determine_verdict(
        self,
        avg_score: float,
        scores: List[float]
    ) -> tuple[str, float]:
        """Determine final verdict and confidence"""
        # Calculate variance in scores
        variance = sum((s - avg_score) ** 2 for s in scores) / len(scores)
        consistency = 1 - min(variance * 4, 1)  # Higher consistency = lower variance

        if avg_score >= 0.65:
            verdict = 'valid'
            confidence = avg_score * 0.7 + consistency * 0.3
        elif avg_score <= 0.35:
            verdict = 'invalid'
            confidence = (1 - avg_score) * 0.7 + consistency * 0.3
        else:
            verdict = 'uncertain'
            confidence = consistency * 0.5  # Uncertain = lower confidence

        return verdict, min(confidence, 0.99)

    def _generate_reasoning(
        self,
        transcript: List[DebateRound],
        verdict: str
    ) -> str:
        """Generate human-readable reasoning"""
        avg_score = sum(r.judge_score for r in transcript) / len(transcript)

        if verdict == 'valid':
            return (
                f"After {len(transcript)} rounds of adversarial debate, "
                f"the judge consistently favored the proposer (avg score: {avg_score:.2f}). "
                f"The critic's counterarguments were not sufficient to invalidate the claim."
            )
        elif verdict == 'invalid':
            return (
                f"After {len(transcript)} rounds of adversarial debate, "
                f"the judge consistently favored the critic (avg score: {avg_score:.2f}). "
                f"Significant flaws were identified in the original claim."
            )
        else:
            return (
                f"After {len(transcript)} rounds of adversarial debate, "
                f"the outcome was inconclusive (avg score: {avg_score:.2f}). "
                f"Both sides presented compelling arguments. Further analysis recommended."
            )

    def _update_role_preferences(
        self,
        role: str,
        model: str,
        performance: float
    ) -> Dict[str, Any]:
        """Update role preferences based on performance"""
        if role not in self.role_preferences:
            self.role_preferences[role] = {}

        current = self.role_preferences[role].get(model, 0.5)
        # Exponential moving average
        alpha = 0.2
        new_pref = current * (1 - alpha) + performance * alpha
        self.role_preferences[role][model] = new_pref

        return {
            'role': role,
            'model': model,
            'old_preference': current,
            'new_preference': new_pref
        }

    def _get_stats(self) -> Dict[str, Any]:
        """Get validation statistics"""
        return {
            'debates_completed': self.metrics['debates_completed'],
            'average_confidence': self.metrics['average_confidence'],
            'proposer_win_rate': self.metrics['proposer_win_rate'],
            'debates_by_topic': self.metrics['debates_by_topic'],
            'role_preferences': self.role_preferences
        }


async def main():
    """Test Multi-Agent Validator"""
    import logging
    logging.basicConfig(level=logging.INFO)

    validator = MultiAgentValidator()

    # Test 1: Validate a claim
    print("\n=== Test 1: Basic Validation ===")
    task_id = await validator.assign_task(
        task_type='validate',
        description='Validate a technical claim',
        input_data={
            'action': 'validate',
            'claim': 'Using async/await improves Python performance for I/O-bound tasks',
            'context': 'Discussing Python optimization strategies',
            'rounds': 2,
            'topic': 'programming'
        }
    )
    await validator._process_tasks()
    result = validator.get_task_result(task_id)
    print(f"Verdict: {result['verdict']}")
    print(f"Confidence: {result['confidence']:.2f}")
    print(f"Models: {result['models_used']}")
    print(f"Cost: {result['cost']:.3f} NOK")

    # Test 2: Validate another claim
    print("\n=== Test 2: Second Validation ===")
    task_id = await validator.assign_task(
        task_type='validate',
        description='Validate a questionable claim',
        input_data={
            'action': 'validate',
            'claim': 'All bugs can be found through static analysis alone',
            'context': 'Discussing software testing strategies',
            'rounds': 3,
            'topic': 'testing'
        }
    )
    await validator._process_tasks()
    result = validator.get_task_result(task_id)
    print(f"Verdict: {result['verdict']}")
    print(f"Confidence: {result['confidence']:.2f}")
    print(f"Reasoning: {result['reasoning']}")

    # Print final stats
    print("\n=== Final Statistics ===")
    stats = validator._get_stats()
    print(f"Debates completed: {stats['debates_completed']}")
    print(f"Average confidence: {stats['average_confidence']:.2f}")
    print(f"Proposer win rate: {stats['proposer_win_rate']:.2f}")


if __name__ == "__main__":
    asyncio.run(main())
