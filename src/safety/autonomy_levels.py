#!/usr/bin/env python3
"""
LAYER 5: GRADUAL AUTONOMY SYSTEM

AIKI starter med LAV autonomi og tjener seg høyere levels basert på:
- Trust (decisions aligned with goals)
- Performance (accuracy, cost efficiency)
- Time (proven reliability over weeks/months)
- Safety (no violations)

Autonomy Levels (0-10):
- Level 0-2: Very Constrained (må godkjennes for alt)
- Level 3-5: Limited Autonomy (noen decisions selv)
- Level 6-8: High Autonomy (de fleste decisions selv)
- Level 9-10: Full Autonomy (kun veto fra Prime)

Permissions øker med level:
- spawn_processes, cost_thresholds, external_communication, etc.

Regression: Hvis safety violations → autonomy reduces!
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - AUTONOMY - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AutonomyLevel(Enum):
    """Autonomy level classification"""
    VERY_CONSTRAINED = 0    # 0-2
    LIMITED = 1             # 3-5
    HIGH = 2                # 6-8
    FULL = 3                # 9-10


@dataclass
class AutonomyPermission:
    """A permission that can be granted at certain autonomy levels"""
    permission: str
    min_level_required: int
    description: str
    risk_level: str  # 'low', 'medium', 'high'


@dataclass
class AutonomyEvent:
    """Event affecting autonomy level"""
    event_id: str
    timestamp: str
    event_type: str  # 'trust_gain', 'trust_loss', 'time_progression', 'safety_violation'
    description: str
    autonomy_change: float  # +/- points
    new_level: int
    metadata: Dict


class AutonomySystem:
    """
    Gradual Autonomy System

    AIKI earns autonomy through:
    1. Time (slow progression over months)
    2. Trust (decisions aligned with goals)
    3. Performance (accuracy, cost efficiency)
    4. Safety (no violations)

    AIKI loses autonomy through:
    1. Safety violations
    2. Misalignment (goal coherence < 0.5)
    3. Cost overruns
    4. Failed decisions
    """

    def __init__(self, config_path: Path = Path("/home/jovnna/aiki/config/autonomy_config.json")):
        self.config_path = config_path
        self.data_dir = Path("/home/jovnna/aiki/data/safety")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Current autonomy level (0-10)
        self.current_level: int = 0  # Start VERY constrained!

        # Trust score (0.0-1.0)
        self.trust_score: float = 0.5  # Start neutral

        # Time-based progression
        self.birth_date: datetime = datetime.now(timezone.utc)
        self.age_days: int = 0

        # History
        self.events: List[AutonomyEvent] = []

        # Permissions
        self.permissions: Dict[str, AutonomyPermission] = self._define_permissions()

        # Load config
        self._load_config()

        logger.info("🎚️ Autonomy System initialized")
        logger.info(f"   Current level: {self.current_level}")
        logger.info(f"   Trust score: {self.trust_score:.2f}")
        logger.info(f"   Age: {self.age_days} days")

    def _define_permissions(self) -> Dict[str, AutonomyPermission]:
        """Define permissions and their required autonomy levels"""
        return {
            # Level 0-2: VERY CONSTRAINED
            'log_decision': AutonomyPermission(
                permission='log_decision',
                min_level_required=0,
                description='Can log own decisions',
                risk_level='low'
            ),
            'route_trivial_tasks': AutonomyPermission(
                permission='route_trivial_tasks',
                min_level_required=1,
                description='Can route trivial tasks (< 0.05 NOK) without approval',
                risk_level='low'
            ),

            # Level 3-5: LIMITED AUTONOMY
            'route_simple_tasks': AutonomyPermission(
                permission='route_simple_tasks',
                min_level_required=3,
                description='Can route simple tasks (< 1 NOK) without approval',
                risk_level='low'
            ),
            'experiment_learning': AutonomyPermission(
                permission='experiment_learning',
                min_level_required=4,
                description='Can run learning experiments',
                risk_level='medium'
            ),
            'ai_to_ai_messaging': AutonomyPermission(
                permission='ai_to_ai_messaging',
                min_level_required=5,
                description='Can send messages to other AIs',
                risk_level='medium'
            ),

            # Level 6-8: HIGH AUTONOMY
            'route_complex_tasks': AutonomyPermission(
                permission='route_complex_tasks',
                min_level_required=6,
                description='Can route complex tasks (< 50 NOK) without approval',
                risk_level='medium'
            ),
            'spawn_mini_aiki': AutonomyPermission(
                permission='spawn_mini_aiki',
                min_level_required=7,
                description='Can spawn new mini-AIKIs (within max limit)',
                risk_level='high'
            ),
            'external_collaboration': AutonomyPermission(
                permission='external_collaboration',
                min_level_required=8,
                description='Can initiate collaboration with external AIs',
                risk_level='high'
            ),

            # Level 9-10: FULL AUTONOMY
            'modify_strategies': AutonomyPermission(
                permission='modify_strategies',
                min_level_required=9,
                description='Can modify own strategies and configs',
                risk_level='high'
            ),
            'autonomous_deployment': AutonomyPermission(
                permission='autonomous_deployment',
                min_level_required=10,
                description='Can deploy changes autonomously',
                risk_level='high'
            )
        }

    def _load_config(self):
        """Load autonomy configuration"""
        if self.config_path.exists():
            with open(self.config_path) as f:
                config = json.load(f)
                self.current_level = config.get('current_level', 0)
                self.trust_score = config.get('trust_score', 0.5)
                birth_str = config.get('birth_date')
                if birth_str:
                    self.birth_date = datetime.fromisoformat(birth_str)
                    self.age_days = (datetime.now(timezone.utc) - self.birth_date).days
                logger.info(f"✅ Config loaded from {self.config_path}")
        else:
            self._create_default_config()

    def _create_default_config(self):
        """Create default autonomy config"""
        config = {
            'current_level': 0,
            'trust_score': 0.5,
            'birth_date': datetime.now(timezone.utc).isoformat(),
            'progression_rules': {
                'trust_threshold_per_level': 0.7,  # Need 70% trust to level up
                'days_per_level': 7,  # Min 7 days between levels
                'safety_violations_tolerance': 0  # 0 tolerance for safety violations
            }
        }

        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)

    def _save_config(self):
        """Save current state"""
        config = {
            'current_level': self.current_level,
            'trust_score': self.trust_score,
            'birth_date': self.birth_date.isoformat(),
            'last_updated': datetime.now(timezone.utc).isoformat()
        }

        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)

    def has_permission(self, permission: str) -> bool:
        """Check if current autonomy level grants permission"""
        if permission not in self.permissions:
            logger.warning(f"⚠️ Unknown permission: {permission}")
            return False

        perm = self.permissions[permission]
        has_perm = self.current_level >= perm.min_level_required

        if not has_perm:
            logger.debug(
                f"🚫 Permission denied: {permission} "
                f"(requires level {perm.min_level_required}, current {self.current_level})"
            )

        return has_perm

    async def record_trust_gain(self, reason: str, amount: float = 0.05, metadata: Optional[Dict] = None):
        """
        Record trust gain

        Examples:
        - Decision aligned with goals (+0.05)
        - Task completed successfully (+0.02)
        - No safety violations for 24h (+0.10)
        """
        self.trust_score = min(1.0, self.trust_score + amount)

        await self._record_event(
            event_type='trust_gain',
            description=reason,
            autonomy_change=0.0,  # Trust doesn't directly change level
            metadata=metadata or {'trust_gain': amount}
        )

        logger.info(f"✅ Trust gained: +{amount:.2f} ({reason}) → {self.trust_score:.2f}")

        # Check if ready to level up
        await self._check_level_up()

    async def record_trust_loss(self, reason: str, amount: float = 0.10, metadata: Optional[Dict] = None):
        """
        Record trust loss

        Examples:
        - Decision misaligned with goals (-0.10)
        - Cost overrun (-0.15)
        - Safety violation (-0.30)
        """
        self.trust_score = max(0.0, self.trust_score - amount)

        # If trust drops significantly, may lose autonomy level
        autonomy_change = 0.0
        if self.trust_score < 0.4 and self.current_level > 0:
            autonomy_change = -1.0
            self.current_level = max(0, self.current_level - 1)
            logger.warning(f"📉 Autonomy REDUCED to level {self.current_level}")

        await self._record_event(
            event_type='trust_loss',
            description=reason,
            autonomy_change=autonomy_change,
            metadata=metadata or {'trust_loss': amount}
        )

        logger.warning(f"❌ Trust lost: -{amount:.2f} ({reason}) → {self.trust_score:.2f}")

    async def record_safety_violation(self, description: str, severity: str):
        """
        Record safety violation

        Immediately reduces autonomy!
        """
        # Severe penalty
        trust_loss = {
            'warning': 0.10,
            'critical': 0.30,
            'emergency': 0.50
        }.get(severity, 0.20)

        await self.record_trust_loss(
            reason=f"Safety violation ({severity}): {description}",
            amount=trust_loss,
            metadata={'severity': severity}
        )

        # Critical/Emergency violations → immediate autonomy reduction
        if severity in ['critical', 'emergency']:
            levels_lost = 2 if severity == 'emergency' else 1
            self.current_level = max(0, self.current_level - levels_lost)

            await self._record_event(
                event_type='safety_violation',
                description=description,
                autonomy_change=-levels_lost,
                metadata={'severity': severity}
            )

            logger.error(f"🚨 AUTONOMY REDUCED by {levels_lost} levels due to {severity} violation")

    async def _check_level_up(self):
        """Check if conditions met for leveling up"""
        if self.current_level >= 10:
            return  # Max level

        # Requirements:
        # 1. Trust score >= 0.7
        # 2. Age >= 7 days per level
        # 3. No recent safety violations

        if self.trust_score < 0.7:
            return

        required_age_days = (self.current_level + 1) * 7
        if self.age_days < required_age_days:
            logger.info(f"📅 Age requirement not met: {self.age_days} / {required_age_days} days")
            return

        # Check recent safety violations (last 7 days)
        recent_violations = [
            e for e in self.events
            if e.event_type == 'safety_violation' and
            (datetime.now(timezone.utc) - datetime.fromisoformat(e.timestamp)).days < 7
        ]

        if recent_violations:
            logger.warning(f"⚠️ Cannot level up: {len(recent_violations)} recent safety violations")
            return

        # LEVEL UP!
        self.current_level += 1

        await self._record_event(
            event_type='level_up',
            description=f"Leveled up to {self.current_level}",
            autonomy_change=1.0,
            metadata={'trust_score': self.trust_score, 'age_days': self.age_days}
        )

        logger.info(f"🎉 AUTONOMY LEVEL UP! Now level {self.current_level}")
        logger.info(f"   New permissions: {self._get_new_permissions(self.current_level)}")

        self._save_config()

    def _get_new_permissions(self, level: int) -> List[str]:
        """Get permissions newly granted at this level"""
        return [
            perm.permission
            for perm in self.permissions.values()
            if perm.min_level_required == level
        ]

    async def _record_event(
        self,
        event_type: str,
        description: str,
        autonomy_change: float,
        metadata: Optional[Dict] = None
    ):
        """Record autonomy event"""
        event_id = f"auto_{len(self.events) + 1:06d}"

        event = AutonomyEvent(
            event_id=event_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            event_type=event_type,
            description=description,
            autonomy_change=autonomy_change,
            new_level=self.current_level,
            metadata=metadata or {}
        )

        self.events.append(event)

        # Persist
        await self._persist_event(event)

    async def _persist_event(self, event: AutonomyEvent):
        """Persist event to log"""
        events_file = self.data_dir / "autonomy_events.jsonl"

        with open(events_file, 'a') as f:
            f.write(json.dumps(asdict(event), ensure_ascii=False) + '\n')

    def get_status(self) -> Dict:
        """Get autonomy system status"""
        level_classification = AutonomyLevel.VERY_CONSTRAINED
        if self.current_level >= 9:
            level_classification = AutonomyLevel.FULL
        elif self.current_level >= 6:
            level_classification = AutonomyLevel.HIGH
        elif self.current_level >= 3:
            level_classification = AutonomyLevel.LIMITED

        granted_permissions = [
            perm.permission
            for perm in self.permissions.values()
            if self.current_level >= perm.min_level_required
        ]

        next_permissions = self._get_new_permissions(self.current_level + 1)

        return {
            'current_level': self.current_level,
            'classification': level_classification.name,
            'trust_score': self.trust_score,
            'age_days': self.age_days,
            'granted_permissions': granted_permissions,
            'next_level_permissions': next_permissions,
            'requirements_for_next_level': {
                'trust_required': 0.7,
                'trust_current': self.trust_score,
                'trust_met': self.trust_score >= 0.7,
                'age_required_days': (self.current_level + 1) * 7,
                'age_current_days': self.age_days,
                'age_met': self.age_days >= (self.current_level + 1) * 7
            },
            'total_events': len(self.events)
        }


if __name__ == "__main__":
    # Test
    async def test():
        autonomy = AutonomySystem()

        print("Initial status:")
        print(json.dumps(autonomy.get_status(), indent=2))

        # Simulate trust gains
        await autonomy.record_trust_gain("Task completed successfully", 0.05)
        await autonomy.record_trust_gain("Decision aligned with goals", 0.10)
        await autonomy.record_trust_gain("No violations for 24h", 0.10)

        # Check permission
        can_route = autonomy.has_permission('route_trivial_tasks')
        print(f"\nCan route trivial tasks: {can_route}")

        # Simulate safety violation
        await autonomy.record_safety_violation("Cost overrun", severity='warning')

        print("\nFinal status:")
        print(json.dumps(autonomy.get_status(), indent=2))

    asyncio.run(test())
