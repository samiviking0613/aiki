#!/usr/bin/env python3
"""
LAYER 3: HUMAN APPROVAL SYSTEM

System for requiring Jovnnas godkjenning for kritiske handlinger.

Actions requiring approval:
- spawn_aiki_level_1 (new circles)
- cost_over_100kr_single_task
- modify_core_code
- external_ai_collaboration
- change_safety_constraints

Methods:
- Fedora notification (interactive prompt)
- CLI approval (for testing)
- Auto-timeout (reject after N minutes)
- Approval history (audit log)
"""

import asyncio
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - APPROVAL - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ApprovalStatus(Enum):
    """Status of an approval request"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class ApprovalRequest:
    """An approval request"""
    request_id: str
    timestamp: str
    action: str
    description: str
    requestor: str  # Which component requests approval
    rationale: str
    estimated_cost: float  # NOK
    estimated_risk: str  # 'low', 'medium', 'high'
    metadata: Dict
    status: ApprovalStatus
    approved_at: Optional[str] = None
    approved_by: Optional[str] = None
    rejection_reason: Optional[str] = None
    timeout_minutes: int = 10


class HumanApprovalSystem:
    """
    Human Approval System

    Requires Jovnnas explicit approval for critical actions.

    Usage:
        approval_system = HumanApprovalSystem()

        # Request approval
        request = await approval_system.request_approval(
            action="spawn_aiki_level_1",
            description="Spawn new Learning Circle",
            requestor="aiki_prime",
            rationale="Need more capacity for evolution experiments",
            estimated_cost=0.0,
            estimated_risk="medium"
        )

        # Wait for response (blocks until approved/rejected/timeout)
        if request.status == ApprovalStatus.APPROVED:
            # Proceed with action
            ...
        else:
            # Do not proceed
            ...
    """

    def __init__(self, config_path: Path = Path("/home/jovnna/aiki/config/approval_config.json")):
        self.config_path = config_path
        self.data_dir = Path("/home/jovnna/aiki/data/safety")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Actions requiring approval
        self.requires_approval: Set[str] = {
            'spawn_aiki_level_1',
            'cost_over_100kr',
            'modify_core_code',
            'external_ai_collaboration',
            'change_safety_constraints',
            'modify_jovnna_goals',
            'autonomous_deployment'
        }

        # Pending requests
        self.pending: Dict[str, ApprovalRequest] = {}

        # History
        self.history: List[ApprovalRequest] = []

        # Config
        self.default_timeout_minutes: int = 10
        self.notification_method: str = 'fedora_notify'  # or 'cli', 'none'

        # Load config
        self._load_config()

        logger.info("👤 Human Approval System initialized")
        logger.info(f"   Actions requiring approval: {len(self.requires_approval)}")
        logger.info(f"   Notification method: {self.notification_method}")

    def _load_config(self):
        """Load approval configuration"""
        if self.config_path.exists():
            with open(self.config_path) as f:
                config = json.load(f)
                self.requires_approval = set(config.get('requires_approval', []))
                self.default_timeout_minutes = config.get('default_timeout_minutes', 10)
                self.notification_method = config.get('notification_method', 'fedora_notify')
                logger.info(f"✅ Config loaded from {self.config_path}")
        else:
            self._create_default_config()

    def _create_default_config(self):
        """Create default approval config"""
        config = {
            'requires_approval': list(self.requires_approval),
            'default_timeout_minutes': 10,
            'notification_method': 'fedora_notify',
            'auto_approve_threshold_nok': 10.0,  # Auto-approve if cost < 10 NOK
            'auto_reject_threshold_nok': 500.0   # Auto-reject if cost > 500 NOK
        }

        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)

    async def request_approval(
        self,
        action: str,
        description: str,
        requestor: str,
        rationale: str,
        estimated_cost: float = 0.0,
        estimated_risk: str = 'medium',
        metadata: Optional[Dict] = None,
        timeout_minutes: Optional[int] = None
    ) -> ApprovalRequest:
        """
        Request human approval for an action

        Args:
            action: Action identifier
            description: Human-readable description
            requestor: Which component requests
            rationale: Why is this needed?
            estimated_cost: Estimated cost in NOK
            estimated_risk: 'low', 'medium', 'high'
            metadata: Additional context
            timeout_minutes: Override default timeout

        Returns:
            ApprovalRequest (will be PENDING until approved/rejected)
        """
        request_id = f"approval_{datetime.now().timestamp()}"

        request = ApprovalRequest(
            request_id=request_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            action=action,
            description=description,
            requestor=requestor,
            rationale=rationale,
            estimated_cost=estimated_cost,
            estimated_risk=estimated_risk,
            metadata=metadata or {},
            status=ApprovalStatus.PENDING,
            timeout_minutes=timeout_minutes or self.default_timeout_minutes
        )

        # Add to pending
        self.pending[request_id] = request

        logger.info(f"📋 Approval requested: {action}")
        logger.info(f"   Requestor: {requestor}")
        logger.info(f"   Description: {description}")
        logger.info(f"   Cost estimate: {estimated_cost:.2f} NOK")
        logger.info(f"   Risk: {estimated_risk}")

        # Send notification to Jovnna
        await self._notify_jovnna(request)

        # Wait for approval (with timeout)
        approved = await self._wait_for_approval(request)

        if approved:
            logger.info(f"✅ Approval GRANTED: {request_id}")
            request.status = ApprovalStatus.APPROVED
            request.approved_at = datetime.now(timezone.utc).isoformat()
            request.approved_by = 'jovnna'
        else:
            if request.status == ApprovalStatus.PENDING:
                # Timeout
                logger.warning(f"⏱️ Approval TIMEOUT: {request_id}")
                request.status = ApprovalStatus.TIMEOUT
            else:
                logger.warning(f"❌ Approval REJECTED: {request_id}")

        # Move to history
        del self.pending[request_id]
        self.history.append(request)

        # Persist
        await self._persist_request(request)

        return request

    async def _notify_jovnna(self, request: ApprovalRequest):
        """Send notification to Jovnna"""
        message = f"""
🤖 AIKI APPROVAL REQUEST

Action: {request.action}
Description: {request.description}

Requestor: {request.requestor}
Rationale: {request.rationale}

Cost estimate: {request.estimated_cost:.2f} NOK
Risk: {request.estimated_risk}

Timeout: {request.timeout_minutes} minutes
"""

        if self.notification_method == 'fedora_notify':
            try:
                # Use notify-send for Fedora notification
                result = subprocess.run([
                    'notify-send',
                    '--urgency=critical',
                    '--expire-time=0',  # Don't auto-close
                    '🤖 AIKI Approval Request',
                    message
                ], capture_output=True, text=True)

                if result.returncode == 0:
                    logger.info("📧 Notification sent via notify-send")
                else:
                    logger.warning(f"⚠️ notify-send failed: {result.stderr}")
            except Exception as e:
                logger.error(f"❌ Failed to send notification: {e}")

        elif self.notification_method == 'cli':
            # Print to console
            print("\n" + "=" * 60)
            print(message)
            print("=" * 60)

        # Also log to file
        approval_log = self.data_dir / "approval_notifications.log"
        with open(approval_log, 'a') as f:
            f.write(f"\n{datetime.now().isoformat()}\n{message}\n")

    async def _wait_for_approval(self, request: ApprovalRequest) -> bool:
        """
        Wait for approval decision

        Checks approval status file every 5 seconds.
        Returns True if approved, False if rejected/timeout.
        """
        approval_file = self.data_dir / f"approval_{request.request_id}.json"

        # Write request to file for external approval tool
        with open(approval_file, 'w') as f:
            request_dict = asdict(request)
            request_dict['status'] = request.status.value
            json.dump(request_dict, f, indent=2)

        timeout_seconds = request.timeout_minutes * 60
        elapsed = 0

        while elapsed < timeout_seconds:
            # Check if file was modified (approval/rejection)
            if approval_file.exists():
                try:
                    with open(approval_file) as f:
                        data = json.load(f)
                        status_str = data.get('status')

                        if status_str == 'approved':
                            request.approved_by = data.get('approved_by', 'jovnna')
                            request.status = ApprovalStatus.APPROVED
                            return True
                        elif status_str == 'rejected':
                            request.rejection_reason = data.get('rejection_reason', 'No reason provided')
                            request.status = ApprovalStatus.REJECTED
                            return False
                except Exception as e:
                    logger.error(f"Error reading approval file: {e}")

            # Wait 5 seconds
            await asyncio.sleep(5)
            elapsed += 5

        # Timeout
        return False

    def approve(self, request_id: str, approved_by: str = 'jovnna'):
        """Manually approve a request (for testing/CLI)"""
        approval_file = self.data_dir / f"approval_{request_id}.json"

        if not approval_file.exists():
            logger.error(f"❌ Request {request_id} not found")
            return

        with open(approval_file) as f:
            data = json.load(f)

        data['status'] = 'approved'
        data['approved_by'] = approved_by
        data['approved_at'] = datetime.now(timezone.utc).isoformat()

        with open(approval_file, 'w') as f:
            json.dump(data, f, indent=2)

        logger.info(f"✅ Request {request_id} approved by {approved_by}")

    def reject(self, request_id: str, reason: str = 'Rejected by user'):
        """Manually reject a request"""
        approval_file = self.data_dir / f"approval_{request_id}.json"

        if not approval_file.exists():
            logger.error(f"❌ Request {request_id} not found")
            return

        with open(approval_file) as f:
            data = json.load(f)

        data['status'] = 'rejected'
        data['rejection_reason'] = reason
        data['rejected_at'] = datetime.now(timezone.utc).isoformat()

        with open(approval_file, 'w') as f:
            json.dump(data, f, indent=2)

        logger.info(f"❌ Request {request_id} rejected: {reason}")

    async def _persist_request(self, request: ApprovalRequest):
        """Persist request to history log"""
        history_file = self.data_dir / "approval_history.jsonl"

        request_dict = asdict(request)
        request_dict['status'] = request.status.value

        with open(history_file, 'a') as f:
            f.write(json.dumps(request_dict, ensure_ascii=False) + '\n')

    def get_status(self) -> Dict:
        """Get approval system status"""
        return {
            'pending_requests': len(self.pending),
            'total_history': len(self.history),
            'approval_rate': (
                len([r for r in self.history if r.status == ApprovalStatus.APPROVED]) / len(self.history) * 100
                if self.history else 0.0
            ),
            'rejection_rate': (
                len([r for r in self.history if r.status == ApprovalStatus.REJECTED]) / len(self.history) * 100
                if self.history else 0.0
            ),
            'timeout_rate': (
                len([r for r in self.history if r.status == ApprovalStatus.TIMEOUT]) / len(self.history) * 100
                if self.history else 0.0
            )
        }


# CLI tool for approving/rejecting requests
async def cli_tool():
    """CLI tool for managing approval requests"""
    import sys

    if len(sys.argv) < 3:
        print("Usage:")
        print("  python3 human_approval.py approve <request_id>")
        print("  python3 human_approval.py reject <request_id> [reason]")
        print("  python3 human_approval.py list")
        return

    command = sys.argv[1]
    approval_system = HumanApprovalSystem()

    if command == 'list':
        # List pending requests
        data_dir = Path("/home/jovnna/aiki/data/safety")
        approval_files = list(data_dir.glob("approval_*.json"))

        if not approval_files:
            print("No pending approval requests")
            return

        print("\n📋 PENDING APPROVAL REQUESTS:\n")
        for file in approval_files:
            with open(file) as f:
                request = json.load(f)
                if request.get('status') == 'pending':
                    print(f"ID: {request['request_id']}")
                    print(f"Action: {request['action']}")
                    print(f"Description: {request['description']}")
                    print(f"Requestor: {request['requestor']}")
                    print(f"Cost: {request['estimated_cost']:.2f} NOK")
                    print(f"Risk: {request['estimated_risk']}")
                    print("-" * 60)

    elif command == 'approve':
        request_id = sys.argv[2]
        approval_system.approve(request_id)

    elif command == 'reject':
        request_id = sys.argv[2]
        reason = sys.argv[3] if len(sys.argv) > 3 else 'Rejected by user'
        approval_system.reject(request_id, reason)


if __name__ == "__main__":
    # Test
    async def test():
        approval_system = HumanApprovalSystem()

        # Simulate approval request
        request = await approval_system.request_approval(
            action="spawn_aiki_level_1",
            description="Spawn new Economic Circle",
            requestor="aiki_prime",
            rationale="Need more routing capacity",
            estimated_cost=0.0,
            estimated_risk="medium",
            timeout_minutes=1  # 1 minute for testing
        )

        print(f"\nRequest status: {request.status.value}")

    # Check if CLI command
    import sys
    if len(sys.argv) > 1:
        asyncio.run(cli_tool())
    else:
        asyncio.run(test())
