#!/usr/bin/env python3
"""
BASE MINI-AIKI - Level 2

Mini-AIKIs er små, spesialiserte AI-agenter som rapporterer til Circles.
Hver mini-AIKI har:
- Spesifikt ansvar (f.eks. cost tracking, evolutionary optimization)
- Parent Circle (Economic, Learning, eller Social)
- Safety layers (kill switch, audit log)
- Kommunikasjon med andre mini-AIKIs

Mini-AIKIs er IKKE autonome som Prime eller Circles.
De utfører spesifikke oppgaver og rapporterer resultater.

Fractal structure:
- Prime (Level 0) → Circles (Level 1) → Mini-AIKIs (Level 2)
- Hver mini-AIKI har samme safety guarantees som Prime
"""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging

# Add to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.safety.kill_switch import KillSwitch
from src.safety.audit_log import AuditLog, EventType

logger = logging.getLogger(__name__)


class MiniAikiState(Enum):
    """Current state of a mini-AIKI"""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    PROCESSING = "processing"
    WAITING = "waiting"
    ERROR = "error"
    SHUTDOWN = "shutdown"


@dataclass
class MiniAikiTask:
    """A task assigned to this mini-AIKI"""
    task_id: str
    task_type: str
    description: str
    input_data: Dict[str, Any]
    assigned_at: str
    completed_at: Optional[str] = None
    result: Optional[Any] = None
    status: str = "pending"  # pending, processing, completed, failed


class BaseMiniAiki:
    """
    Base class for all Mini-AIKIs (Level 2)

    Each mini-AIKI:
    - Has a specific responsibility
    - Reports to a parent Circle
    - Has safety layers (kill switch, audit log)
    - Can communicate with other mini-AIKIs via parent
    """

    def __init__(
        self,
        mini_id: str,
        purpose: str,
        parent_circle: str,  # 'economic', 'learning', or 'social'
        responsibilities: List[str]
    ):
        self.mini_id = mini_id
        self.purpose = purpose
        self.parent_circle = parent_circle
        self.responsibilities = responsibilities

        self.state = MiniAikiState.INITIALIZING
        self.tasks: Dict[str, MiniAikiTask] = {}
        self.metrics: Dict[str, float] = {}

        self.birth_time = datetime.now(timezone.utc)

        # === SAFETY LAYERS (Mini-AIKIs inherit safety!) ===
        self.kill_switch = KillSwitch()
        self.audit_log = AuditLog()

        # Register with kill switch
        self.kill_switch.register_process(
            process_id=mini_id,
            process_type='mini_aiki',
            pid=os.getpid(),
            hostname='localhost',
            location='pc',
            parent_id=parent_circle
        )

        logger.info(f"🤖 Mini-AIKI '{mini_id}' initializing")
        logger.info(f"   Purpose: {purpose}")
        logger.info(f"   Parent: {parent_circle}")
        logger.info(f"   🔐 Safety layers initialized")

    async def start(self):
        """Start the mini-AIKI"""
        self.state = MiniAikiState.ACTIVE
        logger.info(f"🤖 Mini-AIKI '{self.mini_id}' now ACTIVE")

        # Log startup to audit
        await self.audit_log.log(
            event_type=EventType.PROCESS_START,
            component=self.mini_id,
            description=f'Mini-AIKI started (parent: {self.parent_circle})',
            data={
                'purpose': self.purpose,
                'responsibilities': self.responsibilities,
                'parent_circle': self.parent_circle
            }
        )

        # Start main loop
        await self._main_loop()

    async def _main_loop(self):
        """Main mini-AIKI loop - override in subclasses"""
        iteration = 0
        while self.state == MiniAikiState.ACTIVE:
            try:
                iteration += 1

                # SAFETY: Heartbeat to kill switch (every iteration)
                self.kill_switch.heartbeat(self.mini_id)

                # Process tasks
                await self._process_tasks()

                # SAFETY: Audit log every 10th iteration
                if iteration % 10 == 0:
                    await self.audit_log.log(
                        event_type=EventType.DECISION,
                        component=self.mini_id,
                        description=f'Mini-AIKI loop iteration {iteration}',
                        data={
                            'state': self.state.value,
                            'pending_tasks': len([t for t in self.tasks.values() if t.status == 'pending']),
                            'completed_tasks': len([t for t in self.tasks.values() if t.status == 'completed'])
                        }
                    )

                await asyncio.sleep(10)  # Mini-AIKIs check every 10s

            except Exception as e:
                logger.error(f"❌ Error in {self.mini_id} main loop: {e}")
                self.state = MiniAikiState.ERROR
                await asyncio.sleep(30)

    async def _process_tasks(self):
        """Process pending tasks"""
        pending_tasks = [t for t in self.tasks.values() if t.status == 'pending']

        for task in pending_tasks:
            try:
                task.status = 'processing'
                self.state = MiniAikiState.PROCESSING

                # Execute task (subclass implements this)
                result = await self._execute_task(task)

                # Mark completed
                task.status = 'completed'
                task.completed_at = datetime.now(timezone.utc).isoformat()
                task.result = result

                self.state = MiniAikiState.ACTIVE

                logger.info(f"✅ {self.mini_id} completed task: {task.task_id}")

                # Audit log
                await self.audit_log.log(
                    event_type=EventType.DECISION,
                    component=self.mini_id,
                    description=f'Task completed: {task.task_type}',
                    data={
                        'task_id': task.task_id,
                        'task_type': task.task_type,
                        'result': str(result)[:200]  # First 200 chars
                    }
                )

            except Exception as e:
                task.status = 'failed'
                logger.error(f"❌ {self.mini_id} failed task {task.task_id}: {e}")

    async def _execute_task(self, task: MiniAikiTask) -> Any:
        """
        Execute a task - OVERRIDE in subclasses

        Each mini-AIKI implements its own task execution logic.
        """
        raise NotImplementedError("Subclass must implement _execute_task()")

    async def assign_task(
        self,
        task_type: str,
        description: str,
        input_data: Dict[str, Any]
    ) -> str:
        """
        Assign a task to this mini-AIKI

        Called by parent Circle to give work to mini-AIKI.
        """
        task_id = f"{self.mini_id}_task_{datetime.now().timestamp()}"

        task = MiniAikiTask(
            task_id=task_id,
            task_type=task_type,
            description=description,
            input_data=input_data,
            assigned_at=datetime.now(timezone.utc).isoformat()
        )

        self.tasks[task_id] = task

        logger.info(f"📋 {self.mini_id} assigned task: {task_type}")

        return task_id

    def get_task_result(self, task_id: str) -> Optional[Any]:
        """Get result of a completed task"""
        task = self.tasks.get(task_id)
        if task and task.status == 'completed':
            return task.result
        return None

    def get_status(self) -> Dict[str, Any]:
        """Get current mini-AIKI status"""
        uptime = (datetime.now(timezone.utc) - self.birth_time).total_seconds()

        return {
            'mini_id': self.mini_id,
            'purpose': self.purpose,
            'parent_circle': self.parent_circle,
            'state': self.state.value,
            'uptime_seconds': uptime,
            'total_tasks': len(self.tasks),
            'pending_tasks': len([t for t in self.tasks.values() if t.status == 'pending']),
            'completed_tasks': len([t for t in self.tasks.values() if t.status == 'completed']),
            'failed_tasks': len([t for t in self.tasks.values() if t.status == 'failed']),
            'metrics': self.metrics
        }

    async def shutdown(self):
        """Graceful shutdown"""
        logger.warning(f"🤖 {self.mini_id} shutting down")
        self.state = MiniAikiState.SHUTDOWN

        # Log shutdown
        await self.audit_log.log(
            event_type=EventType.PROCESS_END,
            component=self.mini_id,
            description='Mini-AIKI shutdown',
            data=self.get_status()
        )
