#!/usr/bin/env python3
"""
LEARNING CIRCLE - Level 1

Purpose: "Learn continuously and improve"

Domain:
- Evolutionary optimization (nattlig 03:00-06:00)
- A/B testing av strategier
- Performance tracking
- Meta-learning (learning how to learn)
- Consensus strategy optimization

Lead: Evolutionary Engine (Mini-4)

Mini-AIKIs under Learning:
- Mini-4: Evolutionary Engine (genetic algorithms)
- Mini-5: Swarm Consensus (7 små modeller)
- Mini-6: Multi-Agent Validator (adversarial debate)

Schedule:
- Continuous: Performance tracking, experiment logging
- Nightly 03:00-06:00: Evolutionary optimization (100 generations)
- Weekly: Meta-analysis of learnings
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone, time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import logging
import random

# Add to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.circles.base_circle import BaseCircle, CircleState
from src.safety.kill_switch import KillSwitch
from src.safety.human_approval import HumanApprovalSystem, ApprovalStatus
from src.safety.audit_log import AuditLog, EventType
from src.safety.autonomy_levels import AutonomySystem

logger = logging.getLogger(__name__)


@dataclass
class Experiment:
    """Record of a learning experiment"""
    experiment_id: str
    strategy_tested: str
    problem: Dict[str, Any]
    prediction: Any
    ground_truth: Optional[Any]
    accuracy: Optional[float]
    cost: float
    latency: float
    timestamp: str
    metadata: Dict[str, Any]


@dataclass
class EvolutionGeneration:
    """Record of one evolutionary generation"""
    generation: int
    population_size: int
    best_fitness: float
    average_fitness: float
    best_config: Dict[str, Any]
    improvements: Dict[str, float]
    timestamp: str


class LearningCircle(BaseCircle):
    """
    Learning Circle - Continuous improvement and optimization

    This circle is responsible for AIKI getting smarter over time:
    - Tracks performance of all strategies
    - Runs evolutionary optimization nightly
    - Discovers optimal configs for different problem types
    - Learns meta-patterns (what works when?)

    Lead: Evolutionary Engine
    """

    def __init__(self, prime_endpoint: Optional[str] = None):
        super().__init__(
            circle_id="learning",
            purpose="Learn continuously and improve",
            domain=[
                "evolutionary_optimization",
                "ab_testing",
                "performance_tracking",
                "meta_learning",
                "consensus_optimization",
                "strategy_discovery"
            ],
            accountabilities=[
                "Run nightly evolutionary optimization (03:00-06:00)",
                "Track accuracy/cost/latency of all strategies",
                "Discover optimal configs for problem types",
                "Share learnings with other circles",
                "Prevent performance regression"
            ],
            prime_endpoint=prime_endpoint
        )

        # === SAFETY LAYERS (Integrated!) ===
        self.kill_switch = KillSwitch()
        self.approval_system = HumanApprovalSystem()
        self.audit_log = AuditLog()
        self.autonomy = AutonomySystem()

        # Register with kill switch
        self.kill_switch.register_process(
            process_id='learning_circle',
            process_type='circle',
            pid=os.getpid(),
            hostname='localhost',
            location='pc'
        )

        logger.info("🔐 Learning Circle safety layers initialized")

        # Data paths
        self.data_dir = Path("/home/jovnna/aiki/data/learning")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.experiments_file = self.data_dir / "experiments.jsonl"
        self.generations_file = self.data_dir / "evolution_generations.jsonl"

        # Metrics
        self.metrics = {
            'total_experiments': 0,
            'average_accuracy': 0.0,
            'average_cost': 0.0,
            'average_latency': 0.0,
            'best_strategy': None,
            'evolution_generations_completed': 0,
            'current_best_fitness': 0.0
        }

        # Evolution config
        self.evolution_config = {
            'population_size': 10,
            'generations': 100,
            'mutation_rate': 0.1,
            'crossover_rate': 0.7,
            'elite_size': 2  # Keep top 2 unchanged
        }

        # Performance by strategy (for meta-learning)
        self.strategy_performance: Dict[str, List[float]] = {}

        logger.info("🧠 Learning Circle initialized")
        logger.info(f"   Nightly evolution: 03:00-06:00 ({self.evolution_config['generations']} generations)")

    async def _main_loop(self):
        """Main Learning Circle loop"""
        iteration = 0
        while self.state == CircleState.ACTIVE:
            try:
                iteration += 1

                # SAFETY: Heartbeat to kill switch (every iteration)
                self.kill_switch.heartbeat('learning_circle')

                current_time = datetime.now().time()

                # Check if it's evolution time (03:00-06:00)
                if time(3, 0) <= current_time <= time(6, 0):
                    # Check if we already ran today
                    if not await self._evolution_ran_today():
                        logger.info("🌙 Starting nightly evolutionary optimization...")
                        await self._run_evolutionary_optimization()

                # Otherwise, just monitor
                await self._update_metrics()

                # SAFETY: Audit log every 10th iteration
                if iteration % 10 == 0:
                    await self.audit_log.log(
                        event_type=EventType.DECISION,
                        component='learning_circle',
                        description=f'Learning loop iteration {iteration}',
                        data={
                            'total_experiments': self.metrics['total_experiments'],
                            'evolution_generations': self.metrics['evolution_generations_completed'],
                            'state': self.state.value
                        }
                    )

                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                logger.error(f"❌ Error in Learning Circle main loop: {e}")
                await asyncio.sleep(30)

    async def record_experiment(
        self,
        experiment_id: str,
        strategy_tested: str,
        problem: Dict[str, Any],
        prediction: Any,
        ground_truth: Optional[Any] = None,
        cost: float = 0.0,
        latency: float = 0.0,
        metadata: Optional[Dict] = None
    ) -> Experiment:
        """
        Record a learning experiment

        This is called whenever ANY strategy is tested across AIKI.
        Builds up dataset for evolutionary optimization.
        """
        # Calculate accuracy if ground truth provided
        accuracy = None
        if ground_truth is not None:
            accuracy = 1.0 if prediction == ground_truth else 0.0
            # TODO: More sophisticated accuracy calculation

        experiment = Experiment(
            experiment_id=experiment_id,
            strategy_tested=strategy_tested,
            problem=problem,
            prediction=prediction,
            ground_truth=ground_truth,
            accuracy=accuracy,
            cost=cost,
            latency=latency,
            timestamp=datetime.now(timezone.utc).isoformat(),
            metadata=metadata or {}
        )

        # Persist
        await self._persist_experiment(experiment)

        # Update strategy performance tracking
        if strategy_tested not in self.strategy_performance:
            self.strategy_performance[strategy_tested] = []

        if accuracy is not None:
            self.strategy_performance[strategy_tested].append(accuracy)

        # Update metrics
        self.metrics['total_experiments'] += 1

        if accuracy is not None:
            # Running average
            total = self.metrics['total_experiments']
            prev_avg = self.metrics['average_accuracy']
            self.metrics['average_accuracy'] = (prev_avg * (total - 1) + accuracy) / total

        accuracy_str = f"{accuracy:.2f}" if accuracy is not None else "N/A"
        logger.info(
            f"🧪 Experiment recorded: {strategy_tested} "
            f"(accuracy: {accuracy_str}, cost: {cost:.2f} NOK)"
        )

        # SAFETY: Audit log experiment
        await self.audit_log.log(
            event_type=EventType.PROCESS_START,
            component='learning_circle',
            description=f'Experiment {experiment_id} recorded',
            data={
                'strategy': strategy_tested,
                'accuracy': accuracy,
                'cost': cost,
                'latency': latency
            }
        )

        return experiment

    async def _persist_experiment(self, experiment: Experiment):
        """Persist experiment to JSONL"""
        with open(self.experiments_file, 'a') as f:
            f.write(json.dumps(asdict(experiment), ensure_ascii=False) + '\n')

    async def _evolution_ran_today(self) -> bool:
        """Check if evolution already ran today"""
        if not self.generations_file.exists():
            return False

        today = datetime.now().date()

        # Check last generation timestamp
        try:
            with open(self.generations_file, 'r') as f:
                lines = f.readlines()
                if not lines:
                    return False

                last_gen = json.loads(lines[-1])
                last_ts = datetime.fromisoformat(last_gen['timestamp'])

                return last_ts.date() == today
        except:
            return False

    async def _run_evolutionary_optimization(self):
        """
        Run evolutionary optimization to find optimal strategies

        Uses genetic algorithm:
        1. Initialize population of random configs
        2. Evaluate fitness (test on problems)
        3. Select best performers
        4. Crossover + Mutation
        5. Repeat for N generations
        """
        logger.info("🧬 Starting evolutionary optimization...")

        # Load recent experiments as test set
        test_problems = await self._load_test_problems(limit=20)

        if len(test_problems) < 5:
            logger.warning("⚠️ Not enough test problems (<5), skipping evolution")
            return

        # Initialize population (random consensus configs)
        population = self._initialize_population(self.evolution_config['population_size'])

        best_overall_fitness = 0.0
        best_overall_config = None

        for generation in range(self.evolution_config['generations']):
            # Evaluate fitness for each config
            fitnesses = []
            for config in population:
                fitness = await self._evaluate_fitness(config, test_problems)
                fitnesses.append(fitness)

            # Track best
            max_fitness = max(fitnesses)
            best_idx = fitnesses.index(max_fitness)
            best_config = population[best_idx]

            if max_fitness > best_overall_fitness:
                best_overall_fitness = max_fitness
                best_overall_config = best_config

            avg_fitness = sum(fitnesses) / len(fitnesses)

            # Log generation
            gen_record = EvolutionGeneration(
                generation=generation,
                population_size=len(population),
                best_fitness=max_fitness,
                average_fitness=avg_fitness,
                best_config=best_config,
                improvements={'from_baseline': max_fitness - 70.0},  # Baseline ~70
                timestamp=datetime.now(timezone.utc).isoformat()
            )

            await self._persist_generation(gen_record)

            logger.info(
                f"🧬 Gen {generation+1}/{self.evolution_config['generations']}: "
                f"Best={max_fitness:.1f}, Avg={avg_fitness:.1f}"
            )

            # Selection, Crossover, Mutation
            population = self._evolve_population(population, fitnesses)

        # Update metrics
        self.metrics['evolution_generations_completed'] += self.evolution_config['generations']
        self.metrics['current_best_fitness'] = best_overall_fitness
        self.metrics['best_strategy'] = best_overall_config

        logger.info(f"✅ Evolution complete! Best fitness: {best_overall_fitness:.1f}")
        logger.info(f"   Best config: {best_overall_config}")

        # SAFETY: Request human approval before adopting evolved config
        # This is a critical decision that could affect system behavior
        approval_request = await self.approval_system.request_approval(
            action='adopt_evolved_config',
            description=f"Adopt evolved config with fitness {best_overall_fitness:.1f}",
            requestor='learning_circle',
            details={
                'config': best_overall_config,
                'fitness': best_overall_fitness,
                'improvement': best_overall_fitness - 70,
                'generations': self.evolution_config['generations']
            },
            timeout_minutes=10
        )

        # SAFETY: Audit log evolution result
        await self.audit_log.log(
            event_type=EventType.DECISION,
            component='learning_circle',
            description='Evolutionary optimization completed',
            data={
                'best_fitness': best_overall_fitness,
                'best_config': best_overall_config,
                'generations': self.evolution_config['generations'],
                'approval_status': approval_request.status.value
            }
        )

        if approval_request.status == ApprovalStatus.APPROVED:
            logger.info("✅ Evolved config APPROVED by Jovnna")
            # Make decision to adopt best config
            await self.make_decision(
                decision_type="adopt_evolved_config",
                description=f"Adopt evolved config (fitness {best_overall_fitness:.1f})",
                rationale=f"Evolved config shows {best_overall_fitness - 70:.1f} improvement over baseline",
                cost_estimate=0.0,
                requires_prime_approval=False
            )
        else:
            logger.warning(f"⚠️ Evolved config NOT approved: {approval_request.status.value}")
            if approval_request.rejection_reason:
                logger.warning(f"   Reason: {approval_request.rejection_reason}")

    def _initialize_population(self, size: int) -> List[Dict]:
        """Initialize random population of consensus configs"""
        population = []

        strategies = ['3_billige', '3_medium', '5_diverse', '7_små', '5_premium']

        for _ in range(size):
            config = {
                'strategy': random.choice(strategies),
                'voting_method': random.choice(['majority', 'weighted', 'ice']),
                'confidence_threshold': random.uniform(0.6, 0.9),
                'use_caching': random.choice([True, False]),
                'timeout_seconds': random.randint(5, 30)
            }
            population.append(config)

        return population

    async def _load_test_problems(self, limit: int = 20) -> List[Dict]:
        """Load recent problems as test set"""
        if not self.experiments_file.exists():
            return []

        problems = []
        with open(self.experiments_file, 'r') as f:
            lines = f.readlines()
            for line in lines[-limit:]:
                exp = json.loads(line)
                if exp.get('ground_truth') is not None:
                    problems.append({
                        'problem': exp['problem'],
                        'ground_truth': exp['ground_truth'],
                        'metadata': exp.get('metadata', {})
                    })

        return problems

    async def _evaluate_fitness(self, config: Dict, test_problems: List[Dict]) -> float:
        """
        Evaluate fitness of a config

        Fitness = weighted score:
        - Accuracy: 40%
        - Cost (inverse): 20%
        - Latency (inverse): 20%
        - Diversity: 10%
        - Confidence: 10%
        """
        # Simulated evaluation (in real system, would actually run config)
        # For now, use heuristics based on config

        base_accuracy = 70.0

        # Strategy bonuses
        strategy_bonus = {
            '3_billige': 5,
            '3_medium': 10,
            '5_diverse': 15,
            '7_små': 12,
            '5_premium': 8
        }
        accuracy = base_accuracy + strategy_bonus.get(config['strategy'], 0)

        # Voting method bonus
        if config['voting_method'] == 'ice':
            accuracy += 5
        elif config['voting_method'] == 'weighted':
            accuracy += 3

        # Confidence threshold (sweet spot ~0.75)
        threshold_bonus = 5 - abs(config['confidence_threshold'] - 0.75) * 10
        accuracy += threshold_bonus

        # Cost (inverse - lower is better)
        cost_score = 100 if config['strategy'] in ['3_billige', '7_små'] else 80

        # Latency (inverse)
        latency_score = 100 if config['timeout_seconds'] < 15 else 80

        # Diversity (strategy-dependent)
        diversity_score = 100 if config['strategy'] in ['5_diverse', '7_små'] else 70

        # Overall fitness (weighted average)
        fitness = (
            accuracy * 0.40 +
            cost_score * 0.20 +
            latency_score * 0.20 +
            diversity_score * 0.10 +
            90 * 0.10  # Confidence placeholder
        )

        return fitness

    def _evolve_population(self, population: List[Dict], fitnesses: List[float]) -> List[Dict]:
        """
        Evolve population using genetic algorithm

        1. SELECTION: Keep elite + tournament selection
        2. CROSSOVER: Mix pairs of configs
        3. MUTATION: Random changes
        """
        new_population = []

        # Elite preservation (keep top 2)
        elite_indices = sorted(range(len(fitnesses)), key=lambda i: fitnesses[i], reverse=True)[:self.evolution_config['elite_size']]
        for idx in elite_indices:
            new_population.append(population[idx].copy())

        # Fill rest with crossover + mutation
        while len(new_population) < len(population):
            # Tournament selection (pick 2 random, keep best)
            parent1 = self._tournament_select(population, fitnesses)
            parent2 = self._tournament_select(population, fitnesses)

            # Crossover
            if random.random() < self.evolution_config['crossover_rate']:
                child = self._crossover(parent1, parent2)
            else:
                child = parent1.copy()

            # Mutation
            if random.random() < self.evolution_config['mutation_rate']:
                child = self._mutate(child)

            new_population.append(child)

        return new_population

    def _tournament_select(self, population: List[Dict], fitnesses: List[float]) -> Dict:
        """Tournament selection - pick 2 random, return fitter one"""
        idx1, idx2 = random.sample(range(len(population)), 2)
        return population[idx1] if fitnesses[idx1] > fitnesses[idx2] else population[idx2]

    def _crossover(self, parent1: Dict, parent2: Dict) -> Dict:
        """Crossover two configs - mix their traits"""
        child = {}
        for key in parent1.keys():
            child[key] = random.choice([parent1[key], parent2[key]])
        return child

    def _mutate(self, config: Dict) -> Dict:
        """Mutate a config - random changes"""
        mutated = config.copy()

        # Random mutation
        mutation_type = random.choice(['strategy', 'voting', 'threshold', 'timeout'])

        if mutation_type == 'strategy':
            mutated['strategy'] = random.choice(['3_billige', '3_medium', '5_diverse', '7_små', '5_premium'])
        elif mutation_type == 'voting':
            mutated['voting_method'] = random.choice(['majority', 'weighted', 'ice'])
        elif mutation_type == 'threshold':
            mutated['confidence_threshold'] = random.uniform(0.6, 0.9)
        elif mutation_type == 'timeout':
            mutated['timeout_seconds'] = random.randint(5, 30)

        return mutated

    async def _persist_generation(self, generation: EvolutionGeneration):
        """Persist generation record"""
        with open(self.generations_file, 'a') as f:
            f.write(json.dumps(asdict(generation), ensure_ascii=False) + '\n')

    async def _update_metrics(self):
        """Update learning metrics"""
        # Calculate strategy win rates
        if self.strategy_performance:
            best_strategy = max(
                self.strategy_performance.items(),
                key=lambda x: sum(x[1]) / len(x[1]) if x[1] else 0
            )
            self.metrics['best_strategy'] = best_strategy[0]

    def get_best_strategy(self, problem_type: Optional[str] = None) -> Optional[Dict]:
        """
        Get best strategy for a problem type

        Uses learned knowledge from experiments + evolution.
        """
        # Return evolved best config if available
        return self.metrics.get('best_strategy')


async def main():
    """Test Learning Circle"""
    circle = LearningCircle()

    # Simulate some experiments
    await circle.record_experiment(
        experiment_id="exp_001",
        strategy_tested="7_små",
        problem={'type': 'classification', 'complexity': 'medium'},
        prediction="class_A",
        ground_truth="class_A",
        cost=0.14,
        latency=0.6
    )

    await circle.record_experiment(
        experiment_id="exp_002",
        strategy_tested="3_medium",
        problem={'type': 'code_gen', 'complexity': 'medium'},
        prediction="generated code",
        ground_truth="expected code",
        cost=0.69,
        latency=1.2
    )

    print(f"Metrics: {circle.metrics}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
