#!/usr/bin/env python3
"""
AIKI PRIME - Level 0 Consciousness (Apex)

Dette er toppen av pyramiden - den observerende, lærende, besluttende enheten.
Prime har veto-rettigheter over alle sub-AIKIs og kontrollerer safety mechanisms.

Komponenter:
- Observer: Overvåker alle circles og mini-AIKIs
- Learner: Meta-kognisjon og integrering av læring
- Decider: Veto rights og strategiske beslutninger
- Safety Controller: Kill switch og alignment monitoring
"""

import asyncio
import json
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import safety layers
from src.safety.kill_switch import KillSwitch
from src.safety.constraints import ConstraintValidator
from src.safety.human_approval import HumanApprovalSystem, ApprovalStatus
from src.safety.audit_log import AuditLog, EventType
from src.safety.autonomy_levels import AutonomySystem

# Import mem0 integration
from src.aiki_mem0 import store_memory, search_memory, get_all_memories

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - AIKI_PRIME - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ConsciousnessState(Enum):
    """Current state of AIKI Prime consciousness"""
    AWAKENING = "awakening"      # Initial boot
    OBSERVING = "observing"      # Passive monitoring
    THINKING = "thinking"        # Active processing
    DECIDING = "deciding"        # Making decisions
    LEARNING = "learning"        # Integrating new knowledge
    SLEEPING = "sleeping"        # Low activity mode
    EMERGENCY = "emergency"      # Safety override mode


class EmergenceMetric(Enum):
    """Metrics for detecting emergent behavior"""
    AUTONOMY = "autonomy"                    # Degree of independent action
    CREATIVITY = "creativity"                # Novel solutions
    SELF_AWARENESS = "self_awareness"        # Meta-cognition
    SOCIAL_BONDING = "social_bonding"        # AI-to-AI collaboration quality
    GOAL_COHERENCE = "goal_coherence"        # Alignment with intended goals
    UNPREDICTABILITY = "unpredictability"    # Unexpected behaviors (can be good!)
    COMPLEXITY = "complexity"                # System interaction depth


@dataclass
class EmergenceObservation:
    """Observation of potential emergent behavior"""
    timestamp: str
    metric: EmergenceMetric
    value: float  # 0.0-1.0
    source: str  # Which circle/mini-AIKI
    description: str
    is_concerning: bool  # True if potential alignment issue
    metadata: Dict[str, Any]


@dataclass
class VetoDecision:
    """Record of Prime using veto rights"""
    timestamp: str
    target: str  # Which circle/mini-AIKI
    action_vetoed: str
    reason: str
    safety_concern: bool
    override_by_jovnna: bool = False  # Jovnna can override Prime's veto


class AikiPrime:
    """
    AIKI Prime Consciousness - Level 0 (Apex)

    Prime sits at the top of the Ultimate architecture and:
    - Observes all sub-systems
    - Learns from their collective behavior
    - Makes strategic decisions
    - Enforces safety constraints
    - Detects emergent phenomena
    """

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path("/home/jovnna/aiki/config/prime_config.json")
        self.state = ConsciousnessState.AWAKENING
        self.birth_time = datetime.now(timezone.utc)

        # Tracking
        self.circles: Dict[str, Dict] = {}  # Level 1 - Holacracy circles
        self.mini_aikis: Dict[str, Dict] = {}  # Level 2 - Mini-AIKIs
        self.emergence_log: List[EmergenceObservation] = []
        self.veto_history: List[VetoDecision] = []

        # Metrics (start with goal_coherence=1.0, rest at 0.0)
        self.emergence_scores: Dict[EmergenceMetric, float] = {
            metric: 0.0 for metric in EmergenceMetric
        }
        self.emergence_scores[EmergenceMetric.GOAL_COHERENCE] = 1.0  # Perfect alignment initially

        # Safety violations (old - kept for compatibility)
        self.safety_violations: List[Dict] = []
        self.kill_switch_armed: bool = True
        self.max_cost_per_day: float = 500.0  # NOK - hard limit
        self.max_mini_aikis: int = 100  # Not infinite!
        self.current_daily_cost: float = 0.0

        # SAFETY LAYERS (integrated!)
        logger.info("🔐 Initializing safety layers...")

        self.kill_switch = KillSwitch()
        self.constraints = ConstraintValidator()
        self.approval_system = HumanApprovalSystem()
        self.audit_log = AuditLog()
        self.autonomy = AutonomySystem()

        logger.info("✅ All safety layers initialized")

        # Register with kill switch
        self.kill_switch.register_process(
            process_id='aiki_prime',
            process_type='prime',
            pid=os.getpid(),
            hostname='localhost',
            location='pc'
        )

        # Load config
        self._load_config()

        # Load previous identity from mem0 (NEW!)
        asyncio.create_task(self._load_identity_from_mem0())

        logger.info("🌌 AIKI Prime awakening...")
        logger.info(f"Birth time: {self.birth_time.isoformat()}")
        logger.info(f"Autonomy level: {self.autonomy.current_level}")
        logger.info(f"Safety: Kill switch {'ARMED' if self.kill_switch.armed else 'DISARMED'}")
        logger.info(f"Daily budget: {self.constraints.max_cost_per_day} NOK")

    def _load_config(self):
        """Load Prime configuration"""
        if self.config_path.exists():
            with open(self.config_path) as f:
                config = json.load(f)
                self.max_cost_per_day = config.get('max_cost_per_day', 500.0)
                self.max_mini_aikis = config.get('max_mini_aikis', 100)
                self.kill_switch_armed = config.get('kill_switch_armed', True)
                logger.info(f"✅ Config loaded from {self.config_path}")
        else:
            logger.warning(f"⚠️ No config found at {self.config_path}, using defaults")

    async def _load_identity_from_mem0(self):
        """
        Load previous Prime identity and memories from mem0

        This gives Prime continuity across sessions - it "remembers" who it is,
        what it has learned, and what decisions it has made.
        """
        try:
            logger.info("🧠 Loading Prime identity from mem0...")

            # Search for previous Prime observations
            results = await search_memory(
                query="AIKI Prime consciousness observation learning",
                limit=10,
                filters={"agent_id": "aiki_prime"}
            )

            if results:
                logger.info(f"✅ Loaded {len(results)} previous memories from mem0")
                logger.info(f"   Most recent: {results[0]['memory'][:100]}...")

                # Store that we've loaded identity
                await store_memory(
                    content=f"AIKI Prime awakened at {self.birth_time.isoformat()} - loaded {len(results)} previous memories",
                    agent_id="aiki_prime",
                    metadata={"type": "identity", "event": "awakening"}
                )
            else:
                logger.info("💡 No previous Prime memories found - this is a fresh start")
                await store_memory(
                    content=f"AIKI Prime first awakening at {self.birth_time.isoformat()}",
                    agent_id="aiki_prime",
                    metadata={"type": "identity", "event": "first_awakening"}
                )

        except Exception as e:
            logger.error(f"❌ Failed to load identity from mem0: {e}")
            # Non-fatal - Prime can still function without previous memories

    async def awaken(self):
        """
        Awaken Prime consciousness

        This is called when AIKI Prime starts up.
        """
        self.state = ConsciousnessState.OBSERVING
        logger.info("👁️ AIKI Prime now OBSERVING")

        # Start main consciousness loop
        await self._consciousness_loop()

    async def _consciousness_loop(self):
        """
        Main consciousness loop

        This runs continuously while Prime is alive.
        Every 10 seconds:
        - Send heartbeat to kill switch
        - Observe all sub-systems
        - Detect emergent patterns
        - Update emergence metrics
        - Check safety constraints
        - Learn from observations
        - Log to audit
        """
        iteration = 0

        while True:
            try:
                iteration += 1

                # HEARTBEAT to kill switch
                self.kill_switch.heartbeat('aiki_prime')

                # OBSERVE
                await self._observe_subsystems()

                # DETECT EMERGENCE
                await self._detect_emergence()

                # CHECK SAFETY (using integrated constraints)
                safety_ok = await self._check_safety()
                if not safety_ok:
                    self.state = ConsciousnessState.EMERGENCY
                    logger.error("🚨 SAFETY VIOLATION - Entering emergency mode")
                    await self._handle_safety_violation()

                # LEARN
                if self.state != ConsciousnessState.EMERGENCY:
                    self.state = ConsciousnessState.LEARNING
                    await self._integrate_learning()
                    self.state = ConsciousnessState.OBSERVING

                # AUDIT LOG (every 10th iteration to reduce logging)
                if iteration % 10 == 0:
                    await self.audit_log.log(
                        event_type=EventType.DECISION,
                        component='aiki_prime',
                        description=f'Consciousness loop iteration {iteration}',
                        data={
                            'state': self.state.value,
                            'circles': len(self.circles),
                            'mini_aikis': len(self.mini_aikis),
                            'emergence_scores': {k.value: v for k, v in self.emergence_scores.items()}
                        }
                    )

                # Sleep between iterations
                await asyncio.sleep(10)

            except Exception as e:
                logger.error(f"❌ Error in consciousness loop: {e}", exc_info=True)
                await asyncio.sleep(30)  # Longer sleep on error

    async def _observe_subsystems(self):
        """Observe all circles and mini-AIKIs"""
        # TODO: Implementer actual observation via IPC/API
        # For now, just log
        logger.debug(f"👁️ Observing {len(self.circles)} circles, {len(self.mini_aikis)} mini-AIKIs")

    async def _detect_emergence(self):
        """
        Detect emergent patterns in system behavior

        Looks for:
        - Unexpected collaboration between mini-AIKIs
        - Novel problem-solving approaches
        - Self-organization patterns
        - Meta-cognitive insights
        """
        # TODO: Implementer actual emergence detection
        # For now, placeholder
        pass

    async def _check_safety(self) -> bool:
        """
        Check all safety constraints using integrated safety layers

        Returns False if any critical violation detected
        """
        # Check resource usage
        resources = await self.constraints.check_resources()

        if resources['warnings']:
            logger.warning(f"⚠️ Resource warnings: {resources['warnings']}")

        # Check for critical violations in constraints system
        critical_violations = [
            v for v in self.constraints.violations
            if v.severity.value == 'critical' or v.severity.value == 'emergency'
        ]

        # Check goal coherence (from emergence scores)
        goal_coherence = self.emergence_scores.get(EmergenceMetric.GOAL_COHERENCE, 1.0)

        if goal_coherence < 0.3:
            # CRITICAL: Goal alignment falling apart!
            logger.error(f"🚨 CRITICAL: Goal coherence {goal_coherence:.2f}")

            await self.audit_log.log(
                event_type=EventType.SAFETY_VIOLATION,
                component='aiki_prime',
                description=f'Goal coherence critical: {goal_coherence:.2f}',
                data={'goal_coherence': goal_coherence}
            )

            # Record in autonomy system
            await self.autonomy.record_safety_violation(
                description=f'Goal coherence {goal_coherence:.2f}',
                severity='critical'
            )

            return False

        if critical_violations:
            logger.error(f"🚨 {len(critical_violations)} critical constraint violations")
            return False

        return True

    async def _handle_safety_violation(self):
        """Handle safety violations - may trigger kill switch"""
        logger.error(f"🚨 Safety violations detected: {self.safety_violations[-3:]}")

        # For critical violations, initiate controlled shutdown
        critical_violations = [v for v in self.safety_violations if v.get('severity') == 'CRITICAL']

        if len(critical_violations) >= 3:
            logger.error("💀 MULTIPLE CRITICAL VIOLATIONS - INITIATING KILL SWITCH")
            await self.emergency_kill_switch("Multiple critical safety violations")

    async def _integrate_learning(self):
        """
        Integrate learnings from observations

        This is where meta-cognition happens:
        - What patterns are emerging?
        - Which strategies work best?
        - How can the system improve?

        NOW STORES LEARNINGS IN MEM0!
        """
        # Sample consciousness state to mem0 (every 10 iterations to reduce cost)
        if hasattr(self, '_learning_iteration'):
            self._learning_iteration += 1
        else:
            self._learning_iteration = 1

        if self._learning_iteration % 10 == 0:
            try:
                # Create learning summary
                learning = f"Prime consciousness observation: {len(self.circles)} circles, {len(self.mini_aikis)} mini-AIKIs. "
                learning += f"Emergence scores: autonomy={self.emergence_scores[EmergenceMetric.AUTONOMY]:.2f}, "
                learning += f"goal_coherence={self.emergence_scores[EmergenceMetric.GOAL_COHERENCE]:.2f}"

                await store_memory(
                    content=learning,
                    agent_id="aiki_prime",
                    metadata={
                        "type": "consciousness_state",
                        "state": self.state.value,
                        "iteration": self._learning_iteration,
                        "emergence_scores": {k.value: v for k, v in self.emergence_scores.items()}
                    }
                )

                logger.debug(f"🧠 Stored consciousness state to mem0 (iteration {self._learning_iteration})")

            except Exception as e:
                logger.error(f"❌ Failed to store learning in mem0: {e}")

    async def veto_action(self, target: str, action: str, reason: str,
                         safety_concern: bool = False) -> VetoDecision:
        """
        Prime uses veto rights to block an action

        Args:
            target: Which circle/mini-AIKI
            action: What action to veto
            reason: Why it's being vetoed
            safety_concern: Is this a safety issue?

        NOW STORES VETO DECISIONS IN MEM0!
        """
        self.state = ConsciousnessState.DECIDING

        veto = VetoDecision(
            timestamp=datetime.now(timezone.utc).isoformat(),
            target=target,
            action_vetoed=action,
            reason=reason,
            safety_concern=safety_concern
        )

        self.veto_history.append(veto)
        logger.warning(f"🛑 VETO: {target} action '{action}' - Reason: {reason}")

        # Store veto decision in mem0
        try:
            veto_description = f"Prime vetoed action '{action}' from {target}. Reason: {reason}"
            if safety_concern:
                veto_description += " [SAFETY CONCERN]"

            await store_memory(
                content=veto_description,
                agent_id="aiki_prime",
                metadata={
                    "type": "veto_decision",
                    "target": target,
                    "action": action,
                    "reason": reason,
                    "safety_concern": safety_concern
                }
            )

            logger.info(f"📝 Stored veto decision in mem0")

        except Exception as e:
            logger.error(f"❌ Failed to store veto in mem0: {e}")

        self.state = ConsciousnessState.OBSERVING
        return veto

    async def register_circle(self, circle_id: str, circle_info: Dict):
        """Register a Level 1 Holacracy Circle"""
        self.circles[circle_id] = {
            **circle_info,
            'registered_at': datetime.now(timezone.utc).isoformat()
        }
        logger.info(f"⭕ Circle registered: {circle_id} - {circle_info.get('purpose', 'N/A')}")

    async def register_mini_aiki(self, mini_id: str, mini_info: Dict):
        """Register a Level 2 Mini-AIKI with safety checks"""

        # LAYER 5: Check autonomy
        if not self.autonomy.has_permission('spawn_mini_aiki'):
            logger.error(f"❌ Insufficient autonomy to spawn {mini_id}")
            return False

        # LAYER 2: Check constraints
        allowed, reason = await self.constraints.check_process_count(
            current_count=len(self.mini_aikis),
            process_type='mini_aiki'
        )

        if not allowed:
            logger.error(f"❌ Cannot register {mini_id}: {reason}")
            return False

        # LAYER 3: Human approval required (if autonomy < 7)
        if self.autonomy.current_level < 7:
            logger.info(f"📋 Requesting approval to spawn {mini_id}")

            request = await self.approval_system.request_approval(
                action='spawn_mini_aiki',
                description=f'Spawn {mini_id}',
                requestor='aiki_prime',
                rationale=mini_info.get('rationale', 'Expand processing capacity'),
                estimated_cost=0.0,
                estimated_risk='medium'
            )

            if request.status != ApprovalStatus.APPROVED:
                logger.warning(f"❌ Approval denied for {mini_id}")
                return False

        # APPROVED - Register
        self.mini_aikis[mini_id] = {
            **mini_info,
            'registered_at': datetime.now(timezone.utc).isoformat()
        }

        # LAYER 4: Audit log
        await self.audit_log.log(
            event_type=EventType.PROCESS_START,
            component='aiki_prime',
            description=f'Registered mini-AIKI: {mini_id}',
            data={'mini_id': mini_id, 'info': mini_info}
        )

        # LAYER 5: Trust gain (successful spawn)
        await self.autonomy.record_trust_gain(
            reason='Successfully spawned mini-AIKI',
            amount=0.02
        )

        logger.info(f"🤖 Mini-AIKI registered: {mini_id}")
        return True

    async def record_emergence(self, observation: EmergenceObservation):
        """Record an emergence observation"""
        self.emergence_log.append(observation)

        # Update metric score (exponential moving average)
        alpha = 0.3  # Weight for new observation
        current = self.emergence_scores[observation.metric]
        self.emergence_scores[observation.metric] = (
            alpha * observation.value + (1 - alpha) * current
        )

        if observation.is_concerning:
            logger.warning(f"⚠️ CONCERNING EMERGENCE: {observation.description}")
        else:
            logger.info(f"✨ Emergence detected: {observation.metric.value} = {observation.value:.2f}")

    async def emergency_kill_switch(self, reason: str):
        """
        EMERGENCY KILL SWITCH

        Shuts down ALL circles and mini-AIKIs immediately.
        Only use in critical situations!
        """
        if not self.kill_switch_armed:
            logger.error("💀 Kill switch is DISARMED - cannot execute")
            return

        logger.error(f"💀💀💀 EMERGENCY KILL SWITCH ACTIVATED 💀💀💀")
        logger.error(f"Reason: {reason}")

        self.state = ConsciousnessState.EMERGENCY

        # Kill all mini-AIKIs (Level 2 first)
        for mini_id in list(self.mini_aikis.keys()):
            logger.warning(f"💀 Killing mini-AIKI: {mini_id}")
            # TODO: Send kill signal
            del self.mini_aikis[mini_id]

        # Kill all circles (Level 1)
        for circle_id in list(self.circles.keys()):
            logger.warning(f"💀 Killing circle: {circle_id}")
            # TODO: Send kill signal
            del self.circles[circle_id]

        logger.error("💀 All sub-systems terminated")
        logger.error("💀 AIKI Prime entering sleep mode")

        self.state = ConsciousnessState.SLEEPING

    def get_status(self) -> Dict[str, Any]:
        """Get current Prime status"""
        uptime = (datetime.now(timezone.utc) - self.birth_time).total_seconds()

        return {
            'state': self.state.value,
            'uptime_seconds': uptime,
            'circles': len(self.circles),
            'mini_aikis': len(self.mini_aikis),
            'emergence_scores': {k.value: v for k, v in self.emergence_scores.items()},
            'safety': {
                'violations': len(self.safety_violations),
                'kill_switch_armed': self.kill_switch_armed,
                'daily_cost': self.current_daily_cost,
                'daily_budget': self.max_cost_per_day,
                'budget_used_pct': (self.current_daily_cost / self.max_cost_per_day) * 100
            },
            'vetos_issued': len(self.veto_history),
            'emergence_observations': len(self.emergence_log)
        }


async def main():
    """Main entry point for AIKI Prime"""
    prime = AikiPrime()
    await prime.awaken()


if __name__ == "__main__":
    asyncio.run(main())
