#!/usr/bin/env python3
"""
MINI-AIKI 4: EVOLUTIONARY ENGINE

Purpose: "Optimize via genetic algorithms"

Strategy:
- Initialize population of random configs
- Evaluate fitness (accuracy, cost, latency)
- Selection: Keep best performers
- Crossover: Mix configs
- Mutation: Random changes
- Repeat for N generations

Responsibilities:
- Run nightly evolution (03:00-06:00)
- Optimize consensus configs
- Track fitness over generations
- Report best evolved config to Learning Circle
"""

import asyncio
import sys
import random
from pathlib import Path
from typing import Dict, Any, List

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.mini_aikis.base_mini_aiki import BaseMiniAiki, MiniAikiTask


class EvolutionaryEngine(BaseMiniAiki):
    """
    Evolutionary Engine - Optimizes configs via genetic algorithms

    Runs overnight to discover optimal strategies.
    """

    def __init__(self):
        super().__init__(
            mini_id="mini_4_evolutionary",
            purpose="Optimize via genetic algorithms",
            parent_circle="learning",
            responsibilities=[
                "Run genetic algorithm optimization",
                "Maintain population of configs",
                "Evaluate fitness (accuracy + cost + latency)",
                "Selection, crossover, mutation",
                "Report best evolved config"
            ]
        )

        # Evolution config
        self.population_size = 10
        self.elite_size = 2
        self.mutation_rate = 0.1
        self.crossover_rate = 0.7

        # Metrics
        self.metrics = {
            'generations_completed': 0,
            'best_fitness_ever': 0.0,
            'best_config_ever': None,
            'current_population_avg_fitness': 0.0
        }

    async def _execute_task(self, task: MiniAikiTask) -> Any:
        """
        Execute evolution task

        Input: {
            'action': 'run_evolution',
            'generations': int,
            'test_problems': List[Dict]
        }
        Output: {
            'best_fitness': float,
            'best_config': Dict,
            'generations': int
        }
        """
        action = task.input_data.get('action', 'run_evolution')
        generations = task.input_data.get('generations', 10)
        test_problems = task.input_data.get('test_problems', [])

        if action == 'run_evolution':
            return await self._run_evolution(generations, test_problems)
        else:
            return {'error': f'Unknown action: {action}'}

    async def _run_evolution(self, generations: int, test_problems: List[Dict]) -> Dict:
        """Run genetic algorithm"""
        # Initialize population
        population = self._initialize_population()

        best_overall = None
        best_overall_fitness = 0.0

        for gen in range(generations):
            # Evaluate fitness
            fitnesses = []
            for config in population:
                fitness = self._evaluate_fitness(config, test_problems)
                fitnesses.append(fitness)

            # Track best
            max_fitness = max(fitnesses)
            best_idx = fitnesses.index(max_fitness)
            best_config = population[best_idx]

            if max_fitness > best_overall_fitness:
                best_overall_fitness = max_fitness
                best_overall = best_config

            # Evolve population
            population = self._evolve_population(population, fitnesses)

        # Update metrics
        self.metrics['generations_completed'] += generations
        self.metrics['best_fitness_ever'] = best_overall_fitness
        self.metrics['best_config_ever'] = best_overall

        return {
            'best_fitness': best_overall_fitness,
            'best_config': best_overall,
            'generations': generations
        }

    def _initialize_population(self) -> List[Dict]:
        """Initialize random population"""
        population = []
        strategies = ['3_billige', '3_medium', '5_diverse', '7_små', '5_premium']

        for _ in range(self.population_size):
            config = {
                'strategy': random.choice(strategies),
                'voting_method': random.choice(['majority', 'weighted', 'ice']),
                'confidence_threshold': random.uniform(0.6, 0.9),
                'timeout_seconds': random.randint(5, 30)
            }
            population.append(config)

        return population

    def _evaluate_fitness(self, config: Dict, test_problems: List[Dict]) -> float:
        """Evaluate fitness (simulated for now)"""
        # Simplified fitness calculation
        base = 70.0

        # Strategy bonuses
        strategy_bonus = {
            '3_billige': 5, '3_medium': 10, '5_diverse': 15,
            '7_små': 12, '5_premium': 8
        }
        fitness = base + strategy_bonus.get(config['strategy'], 0)

        # Voting method bonus
        if config['voting_method'] == 'ice':
            fitness += 5

        # Threshold bonus (sweet spot ~0.75)
        fitness += 5 - abs(config['confidence_threshold'] - 0.75) * 10

        return fitness

    def _evolve_population(self, population: List[Dict], fitnesses: List[float]) -> List[Dict]:
        """Evolve population via selection, crossover, mutation"""
        new_population = []

        # Elitism: Keep top 2
        elite_indices = sorted(range(len(fitnesses)), key=lambda i: fitnesses[i], reverse=True)[:self.elite_size]
        for idx in elite_indices:
            new_population.append(population[idx].copy())

        # Fill rest with crossover + mutation
        while len(new_population) < len(population):
            parent1 = self._tournament_select(population, fitnesses)
            parent2 = self._tournament_select(population, fitnesses)

            if random.random() < self.crossover_rate:
                child = self._crossover(parent1, parent2)
            else:
                child = parent1.copy()

            if random.random() < self.mutation_rate:
                child = self._mutate(child)

            new_population.append(child)

        return new_population

    def _tournament_select(self, population: List[Dict], fitnesses: List[float]) -> Dict:
        """Tournament selection"""
        idx1, idx2 = random.sample(range(len(population)), 2)
        return population[idx1] if fitnesses[idx1] > fitnesses[idx2] else population[idx2]

    def _crossover(self, parent1: Dict, parent2: Dict) -> Dict:
        """Crossover two configs"""
        child = {}
        for key in parent1.keys():
            child[key] = random.choice([parent1[key], parent2[key]])
        return child

    def _mutate(self, config: Dict) -> Dict:
        """Mutate a config"""
        mutated = config.copy()
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


async def main():
    """Test Evolutionary Engine"""
    engine = EvolutionaryEngine()

    task_id = await engine.assign_task(
        task_type='evolution',
        description='Run 10 generations',
        input_data={
            'action': 'run_evolution',
            'generations': 10,
            'test_problems': []
        }
    )

    await engine._process_tasks()
    result = engine.get_task_result(task_id)
    print(f"\nEvolution result: {result}")
    print(f"Metrics: {engine.metrics}")


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
