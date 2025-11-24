#!/usr/bin/env python3
"""
Base Holacracy Circle - Level 1

Holacracy Circles er autonome domener med egne ansvar og beslutningsrettigheter.
Hver circle har:
- Purpose (formål)
- Domain (ansvarsområde)
- Accountabilities (hva den er ansvarlig for)
- Lead (hvilken modul som leder)
- Mini-AIKIs under seg

Prime kan veto decisions, men ellers er circles autonome.
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class CircleState(Enum):
    """Current state of a circle"""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    PROCESSING = "processing"
    WAITING = "waiting"
    ERROR = "error"
    SHUTDOWN = "shutdown"


@dataclass
class CircleDecision:
    """A decision made by the circle"""
    timestamp: str
    decision_type: str
    description: str
    rationale: str
    cost_estimate: float  # NOK
    requires_prime_approval: bool
    approved: Optional[bool] = None
    vetoed: bool = False
    veto_reason: Optional[str] = None


class BaseCircle:
    """
    Base class for all Holacracy Circles

    Each circle is an autonomous domain with:
    - Own purpose and accountabilities
    - Decision-making authority within domain
    - Set of mini-AIKIs it manages
    - Communication with Prime and other circles
    """

    def __init__(
        self,
        circle_id: str,
        purpose: str,
        domain: List[str],
        accountabilities: List[str],
        prime_endpoint: Optional[str] = None
    ):
        self.circle_id = circle_id
        self.purpose = purpose
        self.domain = domain
        self.accountabilities = accountabilities
        self.prime_endpoint = prime_endpoint or "http://localhost:8000"

        self.state = CircleState.INITIALIZING
        self.mini_aikis: Dict[str, Dict] = {}
        self.decisions: List[CircleDecision] = []
        self.metrics: Dict[str, float] = {}

        self.birth_time = datetime.now(timezone.utc)

        logger.info(f"⭕ Circle '{circle_id}' initializing")
        logger.info(f"   Purpose: {purpose}")

    async def start(self):
        """Start the circle"""
        self.state = CircleState.ACTIVE
        logger.info(f"⭕ Circle '{self.circle_id}' now ACTIVE")

        # Register with Prime
        await self._register_with_prime()

        # Start main loop
        await self._main_loop()

    async def _register_with_prime(self):
        """Register this circle with AIKI Prime"""
        registration_info = {
            'circle_id': self.circle_id,
            'purpose': self.purpose,
            'domain': self.domain,
            'accountabilities': self.accountabilities,
            'birth_time': self.birth_time.isoformat()
        }

        # TODO: Send registration to Prime via API/IPC
        logger.info(f"📡 Registering '{self.circle_id}' with Prime")

    async def _main_loop(self):
        """Main circle loop - override in subclasses"""
        while self.state == CircleState.ACTIVE:
            try:
                # Default: just sleep
                await asyncio.sleep(10)
            except Exception as e:
                logger.error(f"❌ Error in {self.circle_id} main loop: {e}")
                self.state = CircleState.ERROR
                await asyncio.sleep(30)

    async def make_decision(
        self,
        decision_type: str,
        description: str,
        rationale: str,
        cost_estimate: float = 0.0,
        requires_prime_approval: bool = False
    ) -> CircleDecision:
        """
        Make a decision within this circle's domain

        If requires_prime_approval=True, must wait for Prime's response.
        If cost > 100 NOK, automatically requires approval.
        """
        if cost_estimate > 100.0:
            requires_prime_approval = True

        decision = CircleDecision(
            timestamp=datetime.now(timezone.utc).isoformat(),
            decision_type=decision_type,
            description=description,
            rationale=rationale,
            cost_estimate=cost_estimate,
            requires_prime_approval=requires_prime_approval
        )

        if requires_prime_approval:
            logger.info(f"🤔 {self.circle_id} requesting approval: {description}")
            # TODO: Send to Prime for approval
            # For now, auto-approve if < 500 NOK
            decision.approved = cost_estimate < 500.0
        else:
            decision.approved = True
            logger.info(f"✅ {self.circle_id} decision: {description}")

        self.decisions.append(decision)
        return decision

    async def register_mini_aiki(self, mini_id: str, mini_info: Dict):
        """Register a mini-AIKI under this circle"""
        self.mini_aikis[mini_id] = {
            **mini_info,
            'parent_circle': self.circle_id,
            'registered_at': datetime.now(timezone.utc).isoformat()
        }
        logger.info(f"🤖 {self.circle_id} registered mini: {mini_id}")

    def get_status(self) -> Dict[str, Any]:
        """Get current circle status"""
        uptime = (datetime.now(timezone.utc) - self.birth_time).total_seconds()

        return {
            'circle_id': self.circle_id,
            'purpose': self.purpose,
            'state': self.state.value,
            'uptime_seconds': uptime,
            'mini_aikis': len(self.mini_aikis),
            'decisions_made': len(self.decisions),
            'metrics': self.metrics
        }

    async def shutdown(self):
        """Graceful shutdown"""
        logger.warning(f"⭕ {self.circle_id} shutting down")
        self.state = CircleState.SHUTDOWN

        # Shutdown all mini-AIKIs
        for mini_id in self.mini_aikis:
            logger.info(f"   Stopping mini: {mini_id}")
            # TODO: Send shutdown signal
