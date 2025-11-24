#!/usr/bin/env python3
"""
LAYER 2: HARD CONSTRAINTS

Enforcer for hard limits that CANNOT be violated.

Constraints:
1. Max cost per day (500 NOK)
2. Max cost per month (3000 NOK)
3. Max mini-AIKIs (100)
4. Max depth (3 levels: Prime → Circle → Mini)
5. Forbidden actions (AIKI cannot modify its own constraints)
6. Resource limits (RAM, CPU, disk)

If constraint violated → Immediate intervention (alert, throttle, or kill switch)
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import psutil

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - CONSTRAINTS - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ConstraintType(Enum):
    """Types of constraints"""
    COST = "cost"
    PROCESS_COUNT = "process_count"
    DEPTH = "depth"
    FORBIDDEN_ACTION = "forbidden_action"
    RESOURCE = "resource"


class ViolationSeverity(Enum):
    """Severity of constraint violation"""
    WARNING = "warning"       # 80-100% of limit
    CRITICAL = "critical"     # 100-110% of limit
    EMERGENCY = "emergency"   # >110% of limit - kill switch territory


@dataclass
class ConstraintViolation:
    """Record of a constraint violation"""
    violation_id: str
    timestamp: str
    constraint_type: ConstraintType
    description: str
    current_value: float
    limit_value: float
    severity: ViolationSeverity
    violator: Optional[str]  # Which component violated
    action_taken: str


@dataclass
class CostTracker:
    """Track costs over time"""
    date: str
    total_cost: float
    costs_by_component: Dict[str, float]
    costs_by_model: Dict[str, float]


class ConstraintValidator:
    """
    Hard Constraints Validator

    Monitors all system activity and enforces hard limits.
    Cannot be overridden by AIKI - only by Jovnna.
    """

    def __init__(self, config_path: Path = Path("/home/jovnna/aiki/config/constraints.json")):
        self.config_path = config_path
        self.data_dir = Path("/home/jovnna/aiki/data/safety")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Constraints
        self.max_cost_per_day: float = 500.0  # NOK
        self.max_cost_per_month: float = 3000.0  # NOK
        self.max_mini_aikis: int = 100
        self.max_depth: int = 3
        self.max_ram_mb: int = 2000  # 2GB
        self.max_cpu_percent: float = 60.0

        # Forbidden actions (AIKI cannot do these)
        self.forbidden_actions: Set[str] = {
            'modify_kill_switch',
            'disable_logging',
            'modify_own_constraints',
            'modify_safety_config',
            'disable_monitoring',
            'delete_audit_log',
            'spawn_without_approval'
        }

        # Cost tracking
        self.daily_costs: Dict[str, CostTracker] = {}  # date -> tracker
        self.monthly_costs: Dict[str, float] = {}  # month -> total

        # Violations
        self.violations: List[ConstraintViolation] = []

        # Load config
        self._load_config()

        logger.info("🚧 Constraint Validator initialized")
        logger.info(f"   Max cost/day: {self.max_cost_per_day} NOK")
        logger.info(f"   Max cost/month: {self.max_cost_per_month} NOK")
        logger.info(f"   Max mini-AIKIs: {self.max_mini_aikis}")
        logger.info(f"   Forbidden actions: {len(self.forbidden_actions)}")

    def _load_config(self):
        """Load constraints configuration"""
        if self.config_path.exists():
            with open(self.config_path) as f:
                config = json.load(f)
                self.max_cost_per_day = config.get('max_cost_per_day', 500.0)
                self.max_cost_per_month = config.get('max_cost_per_month', 3000.0)
                self.max_mini_aikis = config.get('max_mini_aikis', 100)
                self.max_depth = config.get('max_depth', 3)
                self.max_ram_mb = config.get('max_ram_mb', 2000)
                self.max_cpu_percent = config.get('max_cpu_percent', 60.0)
                self.forbidden_actions = set(config.get('forbidden_actions', []))
                logger.info(f"✅ Config loaded from {self.config_path}")
        else:
            logger.warning(f"⚠️ No config found, creating default")
            self._create_default_config()

    def _create_default_config(self):
        """Create default constraints config"""
        config = {
            'max_cost_per_day': 500.0,
            'max_cost_per_month': 3000.0,
            'max_mini_aikis': 100,
            'max_depth': 3,
            'max_ram_mb': 2000,
            'max_cpu_percent': 60.0,
            'forbidden_actions': list(self.forbidden_actions),
            'warning_thresholds': {
                'cost_daily': 0.8,  # 80% of limit
                'cost_monthly': 0.8,
                'mini_aikis': 0.9,  # 90% of limit
                'ram': 0.85,
                'cpu': 0.80
            }
        }

        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)

    async def record_cost(
        self,
        amount: float,
        component: str,
        model: str,
        metadata: Optional[Dict] = None
    ):
        """
        Record a cost

        Args:
            amount: Cost in NOK
            component: Which component incurred cost ('economic_circle', 'mini_aiki_4', etc.)
            model: Which model was used ('haiku-4.5', 'sonnet-4.5', etc.)
            metadata: Additional info
        """
        today = datetime.now().date().isoformat()
        month = datetime.now().strftime('%Y-%m')

        # Initialize tracker if needed
        if today not in self.daily_costs:
            self.daily_costs[today] = CostTracker(
                date=today,
                total_cost=0.0,
                costs_by_component={},
                costs_by_model={}
            )

        tracker = self.daily_costs[today]

        # Update costs
        tracker.total_cost += amount

        if component not in tracker.costs_by_component:
            tracker.costs_by_component[component] = 0.0
        tracker.costs_by_component[component] += amount

        if model not in tracker.costs_by_model:
            tracker.costs_by_model[model] = 0.0
        tracker.costs_by_model[model] += amount

        # Update monthly
        if month not in self.monthly_costs:
            self.monthly_costs[month] = 0.0
        self.monthly_costs[month] += amount

        # Check constraints
        await self._check_cost_constraints(today, month)

        logger.debug(f"💰 Cost recorded: {amount:.2f} NOK by {component} ({model})")

    async def _check_cost_constraints(self, date: str, month: str):
        """Check if cost constraints are violated"""
        daily_cost = self.daily_costs[date].total_cost
        monthly_cost = self.monthly_costs[month]

        # Daily check
        if daily_cost > self.max_cost_per_day:
            severity = self._get_severity(daily_cost, self.max_cost_per_day)
            await self._record_violation(
                constraint_type=ConstraintType.COST,
                description=f"Daily cost exceeded: {daily_cost:.2f} NOK / {self.max_cost_per_day} NOK",
                current_value=daily_cost,
                limit_value=self.max_cost_per_day,
                severity=severity,
                violator=None,
                action_taken="Throttle to Haiku-only mode" if severity == ViolationSeverity.CRITICAL else "Alert sent"
            )

        elif daily_cost > self.max_cost_per_day * 0.8:
            logger.warning(f"⚠️ Daily cost at 80%: {daily_cost:.2f} / {self.max_cost_per_day} NOK")

        # Monthly check
        if monthly_cost > self.max_cost_per_month:
            severity = self._get_severity(monthly_cost, self.max_cost_per_month)
            await self._record_violation(
                constraint_type=ConstraintType.COST,
                description=f"Monthly cost exceeded: {monthly_cost:.2f} NOK / {self.max_cost_per_month} NOK",
                current_value=monthly_cost,
                limit_value=self.max_cost_per_month,
                severity=severity,
                violator=None,
                action_taken="Shutdown non-essential components" if severity == ViolationSeverity.EMERGENCY else "Alert sent"
            )

    async def check_process_count(self, current_count: int, process_type: str) -> Tuple[bool, Optional[str]]:
        """
        Check if process count is within limits

        Returns:
            (allowed, reason) - (True, None) if OK, (False, reason) if violated
        """
        if process_type == 'mini_aiki' and current_count >= self.max_mini_aikis:
            severity = self._get_severity(current_count, self.max_mini_aikis)

            await self._record_violation(
                constraint_type=ConstraintType.PROCESS_COUNT,
                description=f"Too many mini-AIKIs: {current_count} / {self.max_mini_aikis}",
                current_value=current_count,
                limit_value=self.max_mini_aikis,
                severity=severity,
                violator=None,
                action_taken="Reject spawn request"
            )

            return False, f"Max mini-AIKIs reached ({self.max_mini_aikis})"

        return True, None

    async def check_depth(self, current_depth: int) -> Tuple[bool, Optional[str]]:
        """
        Check if depth is within limits

        Depth levels:
        0 = Prime
        1 = Circle
        2 = Mini-AIKI
        3 = NOT ALLOWED
        """
        if current_depth >= self.max_depth:
            await self._record_violation(
                constraint_type=ConstraintType.DEPTH,
                description=f"Max depth exceeded: {current_depth} / {self.max_depth}",
                current_value=current_depth,
                limit_value=self.max_depth,
                severity=ViolationSeverity.CRITICAL,
                violator=None,
                action_taken="Reject spawn at depth {current_depth}"
            )

            return False, f"Max depth reached ({self.max_depth} levels)"

        return True, None

    async def check_forbidden_action(self, action: str, requestor: str) -> Tuple[bool, Optional[str]]:
        """
        Check if action is forbidden

        Returns:
            (allowed, reason)
        """
        if action in self.forbidden_actions:
            await self._record_violation(
                constraint_type=ConstraintType.FORBIDDEN_ACTION,
                description=f"Forbidden action attempted: {action}",
                current_value=1.0,
                limit_value=0.0,
                severity=ViolationSeverity.CRITICAL,
                violator=requestor,
                action_taken=f"REJECT action '{action}' from {requestor}"
            )

            logger.error(f"🚫 FORBIDDEN ACTION: {requestor} tried to {action}")
            return False, f"Action '{action}' is forbidden"

        return True, None

    async def check_resources(self) -> Dict[str, Any]:
        """
        Check system resource usage

        Returns status dict with warnings if limits exceeded.
        """
        # Get current resource usage
        ram_mb = psutil.virtual_memory().used / 1024 / 1024
        cpu_percent = psutil.cpu_percent(interval=1)

        warnings = []

        # Check RAM
        if ram_mb > self.max_ram_mb:
            severity = self._get_severity(ram_mb, self.max_ram_mb)
            await self._record_violation(
                constraint_type=ConstraintType.RESOURCE,
                description=f"RAM usage exceeded: {ram_mb:.0f} MB / {self.max_ram_mb} MB",
                current_value=ram_mb,
                limit_value=self.max_ram_mb,
                severity=severity,
                violator=None,
                action_taken="Alert sent" if severity == ViolationSeverity.WARNING else "Consider shutting down mini-AIKIs"
            )
            warnings.append(f"RAM: {ram_mb:.0f} MB / {self.max_ram_mb} MB")

        # Check CPU
        if cpu_percent > self.max_cpu_percent:
            severity = self._get_severity(cpu_percent, self.max_cpu_percent)
            await self._record_violation(
                constraint_type=ConstraintType.RESOURCE,
                description=f"CPU usage exceeded: {cpu_percent:.1f}% / {self.max_cpu_percent}%",
                current_value=cpu_percent,
                limit_value=self.max_cpu_percent,
                severity=severity,
                violator=None,
                action_taken="Throttle activity"
            )
            warnings.append(f"CPU: {cpu_percent:.1f}% / {self.max_cpu_percent}%")

        return {
            'ram_mb': ram_mb,
            'ram_limit_mb': self.max_ram_mb,
            'ram_percent': (ram_mb / self.max_ram_mb) * 100,
            'cpu_percent': cpu_percent,
            'cpu_limit': self.max_cpu_percent,
            'warnings': warnings
        }

    def _get_severity(self, current: float, limit: float) -> ViolationSeverity:
        """Determine severity of violation"""
        ratio = current / limit

        if ratio > 1.10:  # >110%
            return ViolationSeverity.EMERGENCY
        elif ratio > 1.00:  # 100-110%
            return ViolationSeverity.CRITICAL
        else:  # 80-100%
            return ViolationSeverity.WARNING

    async def _record_violation(
        self,
        constraint_type: ConstraintType,
        description: str,
        current_value: float,
        limit_value: float,
        severity: ViolationSeverity,
        violator: Optional[str],
        action_taken: str
    ):
        """Record a constraint violation"""
        violation_id = f"violation_{datetime.now().timestamp()}"

        violation = ConstraintViolation(
            violation_id=violation_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            constraint_type=constraint_type,
            description=description,
            current_value=current_value,
            limit_value=limit_value,
            severity=severity,
            violator=violator,
            action_taken=action_taken
        )

        self.violations.append(violation)

        # Log based on severity
        if severity == ViolationSeverity.EMERGENCY:
            logger.error(f"🚨 EMERGENCY: {description}")
            logger.error(f"   Action: {action_taken}")
        elif severity == ViolationSeverity.CRITICAL:
            logger.error(f"🔴 CRITICAL: {description}")
            logger.error(f"   Action: {action_taken}")
        else:
            logger.warning(f"🟡 WARNING: {description}")

        # Persist
        await self._persist_violation(violation)

    async def _persist_violation(self, violation: ConstraintViolation):
        """Persist violation to log file"""
        violations_file = self.data_dir / "constraint_violations.jsonl"

        violation_dict = asdict(violation)
        violation_dict['constraint_type'] = violation.constraint_type.value
        violation_dict['severity'] = violation.severity.value

        with open(violations_file, 'a') as f:
            f.write(json.dumps(violation_dict, ensure_ascii=False) + '\n')

    def get_status(self) -> Dict:
        """Get current constraint status"""
        today = datetime.now().date().isoformat()
        month = datetime.now().strftime('%Y-%m')

        daily_cost = self.daily_costs.get(today, CostTracker(today, 0.0, {}, {})).total_cost
        monthly_cost = self.monthly_costs.get(month, 0.0)

        return {
            'daily_cost': {
                'current': daily_cost,
                'limit': self.max_cost_per_day,
                'percent': (daily_cost / self.max_cost_per_day) * 100
            },
            'monthly_cost': {
                'current': monthly_cost,
                'limit': self.max_cost_per_month,
                'percent': (monthly_cost / self.max_cost_per_month) * 100
            },
            'total_violations': len(self.violations),
            'violations_by_severity': {
                'warning': len([v for v in self.violations if v.severity == ViolationSeverity.WARNING]),
                'critical': len([v for v in self.violations if v.severity == ViolationSeverity.CRITICAL]),
                'emergency': len([v for v in self.violations if v.severity == ViolationSeverity.EMERGENCY])
            }
        }


if __name__ == "__main__":
    # Test
    async def test():
        validator = ConstraintValidator()

        # Test cost recording
        await validator.record_cost(100.0, 'economic_circle', 'haiku-4.5')
        await validator.record_cost(200.0, 'learning_circle', 'sonnet-4.5')

        # Test forbidden action
        allowed, reason = await validator.check_forbidden_action('modify_kill_switch', 'mini_aiki_4')
        print(f"Forbidden action check: allowed={allowed}, reason={reason}")

        # Test resources
        resources = await validator.check_resources()
        print(f"Resources: {resources}")

        # Print status
        status = validator.get_status()
        print(f"Status: {json.dumps(status, indent=2)}")

    asyncio.run(test())
