#!/usr/bin/env python3
"""
ECONOMIC CIRCLE - Level 1

Purpose: "Optimize cost without sacrificing quality"

Domain:
- API provider selection
- Model routing decisions
- Cost tracking and budget management
- Batch API optimization
- Prompt caching strategies

Lead: Hierarchical Decision Engine (Mini-1)

Mini-AIKIs under Economic:
- Mini-1: Hierarchical Engine (CEO→Manager→Worker routing)
- Mini-2: Ensemble Learner (weighted by expertise)
- Mini-3: Cost Tracker (monitoring and alerts)
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

# Add to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.circles.base_circle import BaseCircle, CircleState
from src.safety.kill_switch import KillSwitch
from src.safety.constraints import ConstraintValidator
from src.safety.audit_log import AuditLog, EventType

logger = logging.getLogger(__name__)


@dataclass
class TaskRoutingDecision:
    """Decision about which model to route a task to"""
    task_complexity: str  # 'trivial', 'simple', 'medium', 'complex', 'very_complex'
    model_selected: str
    cost_estimate: float  # NOK
    rationale: str
    alternatives_considered: List[Dict[str, Any]]


class EconomicCircle(BaseCircle):
    """
    Economic Circle - Cost optimization without quality sacrifice

    This circle is responsible for keeping AIKI economically sustainable
    while maintaining high quality outputs.

    Uses Hierarchical Decision Engine as lead:
    - 70% of tasks → Haiku (trivial/simple)
    - 20% of tasks → Sonnet (medium)
    - 10% of tasks → Opus or Swarm (complex/very complex)

    Target: 750-1,500 NOK/month for normal usage
    """

    def __init__(self, prime_endpoint: Optional[str] = None):
        super().__init__(
            circle_id="economic",
            purpose="Optimize cost without sacrificing quality",
            domain=[
                "api_provider_selection",
                "model_routing",
                "cost_tracking",
                "budget_management",
                "batch_optimization",
                "prompt_caching"
            ],
            accountabilities=[
                "Stay within daily budget (500 NOK)",
                "Minimize cost per task",
                "Maintain quality thresholds (>85% accuracy)",
                "Alert on budget overruns",
                "Optimize for best value models"
            ],
            prime_endpoint=prime_endpoint
        )

        # === SAFETY LAYERS (Integrated!) ===
        self.kill_switch = KillSwitch()
        self.constraints = ConstraintValidator()
        self.audit_log = AuditLog()

        # Register with kill switch
        self.kill_switch.register_process(
            process_id='economic_circle',
            process_type='circle',
            pid=os.getpid(),
            hostname='localhost',
            location='pc'
        )

        logger.info("🔐 Economic Circle safety layers initialized")

        # Metrics
        self.metrics = {
            'total_tasks_routed': 0,
            'total_cost_today': 0.0,
            'average_cost_per_task': 0.0,
            'haiku_usage_pct': 0.0,
            'sonnet_usage_pct': 0.0,
            'opus_usage_pct': 0.0,
            'swarm_usage_pct': 0.0
        }

        # Task complexity thresholds
        self.complexity_rules = {
            'trivial': {
                'model': 'haiku-4.5',
                'cost_per_1k_tokens': 0.011,  # 11 øre per 1000 tokens
                'examples': ['classification', 'simple parsing', 'yes/no questions']
            },
            'simple': {
                'model': 'haiku-4.5',
                'cost_per_1k_tokens': 0.011,
                'examples': ['short code gen', 'basic analysis', 'formatting']
            },
            'medium': {
                'model': 'sonnet-4.5',
                'cost_per_1k_tokens': 0.033,  # 33 øre per 1000 tokens
                'examples': ['code generation', 'debugging', 'explanation']
            },
            'complex': {
                'model': 'swarm-7-små',  # 7 små modeller
                'cost_per_1k_tokens': 0.044,  # 44 øre per 1000 tokens
                'examples': ['architecture decisions', 'multi-file refactoring']
            },
            'very_complex': {
                'model': 'opus-4',
                'cost_per_1k_tokens': 0.165,  # 165 øre per 1000 tokens
                'examples': ['deep analysis', 'system design', 'complex debugging']
            }
        }

        logger.info("💰 Economic Circle initialized")

    async def _main_loop(self):
        """Main Economic Circle loop"""
        iteration = 0
        while self.state == CircleState.ACTIVE:
            try:
                iteration += 1

                # SAFETY: Heartbeat to kill switch (every iteration)
                self.kill_switch.heartbeat('economic_circle')

                # Every 60 seconds:
                # 1. Update cost metrics
                # 2. Check budget status
                # 3. Optimize routing if needed

                await self._update_metrics()
                await self._check_budget()
                await self._optimize_routing()

                # SAFETY: Audit log every 10th iteration
                if iteration % 10 == 0:
                    await self.audit_log.log(
                        event_type=EventType.DECISION,
                        component='economic_circle',
                        description=f'Economic loop iteration {iteration}',
                        data={
                            'total_tasks': self.metrics['total_tasks_routed'],
                            'daily_cost': self.metrics['total_cost_today'],
                            'state': self.state.value
                        }
                    )

                await asyncio.sleep(60)

            except Exception as e:
                logger.error(f"❌ Error in Economic Circle main loop: {e}")
                await asyncio.sleep(30)

    async def route_task(
        self,
        task_description: str,
        estimated_tokens: int,
        complexity: Optional[str] = None
    ) -> TaskRoutingDecision:
        """
        Route a task to the optimal model

        Args:
            task_description: What the task is about
            estimated_tokens: Estimated input+output tokens
            complexity: Optional manual complexity override

        Returns:
            TaskRoutingDecision with model selection and rationale
        """
        # If no complexity provided, infer it
        if complexity is None:
            complexity = await self._infer_complexity(task_description, estimated_tokens)

        rule = self.complexity_rules[complexity]
        model = rule['model']
        cost = (estimated_tokens / 1000.0) * rule['cost_per_1k_tokens']

        # Build decision
        decision = TaskRoutingDecision(
            task_complexity=complexity,
            model_selected=model,
            cost_estimate=cost,
            rationale=f"Task classified as {complexity}, routing to {model} (estimated {cost:.2f} NOK)",
            alternatives_considered=self._get_alternatives(complexity)
        )

        # SAFETY: Record cost via constraints system (replaces internal tracking)
        await self.constraints.record_cost(
            amount=cost,
            component='economic_circle',
            model=model
        )

        # Update metrics
        self.metrics['total_tasks_routed'] += 1
        # Use constraints' cost tracking instead of internal
        constraint_status = self.constraints.get_status()
        self.metrics['total_cost_today'] = constraint_status['daily_cost']['current']

        # Update usage percentages
        if 'haiku' in model:
            self.metrics['haiku_usage_pct'] = (
                (self.metrics.get('haiku_count', 0) + 1) / self.metrics['total_tasks_routed']
            ) * 100
            self.metrics['haiku_count'] = self.metrics.get('haiku_count', 0) + 1
        elif 'sonnet' in model:
            self.metrics['sonnet_usage_pct'] = (
                (self.metrics.get('sonnet_count', 0) + 1) / self.metrics['total_tasks_routed']
            ) * 100
            self.metrics['sonnet_count'] = self.metrics.get('sonnet_count', 0) + 1
        elif 'opus' in model:
            self.metrics['opus_usage_pct'] = (
                (self.metrics.get('opus_count', 0) + 1) / self.metrics['total_tasks_routed']
            ) * 100
            self.metrics['opus_count'] = self.metrics.get('opus_count', 0) + 1
        elif 'swarm' in model:
            self.metrics['swarm_usage_pct'] = (
                (self.metrics.get('swarm_count', 0) + 1) / self.metrics['total_tasks_routed']
            ) * 100
            self.metrics['swarm_count'] = self.metrics.get('swarm_count', 0) + 1

        self.metrics['average_cost_per_task'] = (
            self.metrics['total_cost_today'] / self.metrics['total_tasks_routed']
        )

        logger.info(f"💰 Routed task: {complexity} → {model} ({cost:.3f} NOK)")

        # SAFETY: Audit log routing decision
        await self.audit_log.log(
            event_type=EventType.DECISION,
            component='economic_circle',
            description=f'Routed task to {model}',
            data={
                'complexity': complexity,
                'model': model,
                'cost': cost,
                'rationale': decision.rationale
            }
        )

        return decision

    async def _infer_complexity(self, task_description: str, estimated_tokens: int) -> str:
        """
        Infer task complexity from description and token estimate

        Simple heuristics for now, can be improved with ML later.
        """
        desc_lower = task_description.lower()

        # Trivial indicators
        if any(word in desc_lower for word in ['classify', 'yes/no', 'true/false', 'parse simple']):
            return 'trivial'

        # Simple indicators
        if estimated_tokens < 1000 and any(word in desc_lower for word in ['short', 'quick', 'simple']):
            return 'simple'

        # Complex indicators
        if any(word in desc_lower for word in ['architecture', 'design', 'refactor', 'analyze system']):
            return 'complex'

        # Very complex indicators
        if any(word in desc_lower for word in ['deep analysis', 'comprehensive', 'entire codebase']):
            return 'very_complex'

        # Default: medium
        if estimated_tokens < 3000:
            return 'medium'
        elif estimated_tokens < 10000:
            return 'complex'
        else:
            return 'very_complex'

    def _get_alternatives(self, complexity: str) -> List[Dict[str, Any]]:
        """Get alternative model options for this complexity"""
        alternatives = []

        for comp, rule in self.complexity_rules.items():
            if comp != complexity:
                alternatives.append({
                    'complexity': comp,
                    'model': rule['model'],
                    'cost_per_1k': rule['cost_per_1k_tokens']
                })

        return alternatives

    async def _update_metrics(self):
        """Update cost and usage metrics"""
        # Metrics are updated in real-time during route_task
        pass

    async def _check_budget(self):
        """Check if we're within budget"""
        # SAFETY: Use constraints system for budget checking
        constraint_status = self.constraints.get_status()
        daily_cost = constraint_status['daily_cost']
        current_cost = daily_cost['current']
        daily_budget = daily_cost['limit']

        if current_cost > daily_budget:
            logger.error(f"🚨 BUDGET EXCEEDED: {current_cost:.2f} NOK / {daily_budget:.2f} NOK")

            # SAFETY: Audit log violation
            await self.audit_log.log(
                event_type=EventType.SAFETY_VIOLATION,
                component='economic_circle',
                description='Daily budget exceeded',
                data={
                    'current_cost': current_cost,
                    'budget': daily_budget,
                    'violations': constraint_status['total_violations']
                }
            )

            # Make decision to throttle
            await self.make_decision(
                decision_type="budget_throttle",
                description="Daily budget exceeded, throttling to Haiku-only mode",
                rationale=f"Current cost {current_cost:.2f} exceeds budget {daily_budget}",
                cost_estimate=0.0,
                requires_prime_approval=True
            )

        elif current_cost > daily_budget * 0.8:
            logger.warning(f"⚠️ BUDGET WARNING: {current_cost:.2f} NOK / {daily_budget:.2f} NOK (80%)")

    async def _optimize_routing(self):
        """Optimize routing strategy based on performance data"""
        # TODO: Use Learning Circle's insights to optimize routing
        # For now, just log current distribution
        logger.debug(
            f"💰 Usage: Haiku {self.metrics.get('haiku_usage_pct', 0):.1f}%, "
            f"Sonnet {self.metrics.get('sonnet_usage_pct', 0):.1f}%, "
            f"Opus {self.metrics.get('opus_usage_pct', 0):.1f}%, "
            f"Swarm {self.metrics.get('swarm_usage_pct', 0):.1f}%"
        )


async def main():
    """Test Economic Circle"""
    circle = EconomicCircle()
    await circle.start()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
