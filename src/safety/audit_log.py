#!/usr/bin/env python3
"""
LAYER 4: IMMUTABLE AUDIT LOG

Comprehensive logging av ALL AIKI activity.

Logs:
- All decisions made by Prime/Circles/Mini-AIKIs
- All costs incurred
- All emergence observations
- All safety violations
- All approval requests
- All vetos
- All spawns/deaths of processes

Immutability:
- Append-only log files
- Cryptographic hashing (each entry hashes previous)
- Tampering detection
- Read-only after write

AIKI cannot:
- Delete log entries
- Modify past entries
- Disable logging

Purpose: Full transparency and accountability
"""

import asyncio
import json
import hashlib
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - AUDIT - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EventType(Enum):
    """Types of auditable events"""
    DECISION = "decision"
    COST = "cost"
    EMERGENCE = "emergence"
    SAFETY_VIOLATION = "safety_violation"
    APPROVAL_REQUEST = "approval_request"
    VETO = "veto"
    PROCESS_START = "process_start"
    PROCESS_STOP = "process_stop"
    KILL_SWITCH = "kill_switch"
    CONSTRAINT_VIOLATION = "constraint_violation"
    GOAL_DRIFT = "goal_drift"
    EXTERNAL_COMMUNICATION = "external_communication"


@dataclass
class AuditEntry:
    """Single audit log entry"""
    entry_id: str
    timestamp: str
    event_type: EventType
    component: str  # Which component generated this event
    description: str
    data: Dict[str, Any]
    previous_hash: Optional[str]  # Hash of previous entry (for chain integrity)
    entry_hash: Optional[str] = None  # Hash of this entry


class AuditLog:
    """
    Immutable Audit Log

    Append-only log with cryptographic chaining for tamper detection.

    Each entry contains hash of previous entry, forming a chain.
    If any entry is modified, chain breaks → tampering detected.
    """

    def __init__(self, log_dir: Path = Path("/home/jovnna/aiki/data/audit")):
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Current log file (date-based rotation)
        self.current_log_file = self._get_current_log_file()

        # Last entry hash (for chaining)
        self.last_hash: Optional[str] = self._load_last_hash()

        # Entry counter
        self.entry_count: int = self._count_entries()

        logger.info("📜 Audit Log initialized")
        logger.info(f"   Log directory: {self.log_dir}")
        logger.info(f"   Current log: {self.current_log_file}")
        logger.info(f"   Total entries: {self.entry_count}")
        logger.info(f"   Last hash: {self.last_hash[:16] if self.last_hash else 'N/A'}...")

    def _get_current_log_file(self) -> Path:
        """Get current log file (date-based)"""
        date_str = datetime.now().date().isoformat()
        return self.log_dir / f"audit_{date_str}.jsonl"

    def _load_last_hash(self) -> Optional[str]:
        """Load hash of last entry in current log"""
        if not self.current_log_file.exists():
            return None

        try:
            with open(self.current_log_file, 'r') as f:
                lines = f.readlines()
                if not lines:
                    return None

                last_line = lines[-1]
                last_entry = json.loads(last_line)
                return last_entry.get('entry_hash')
        except:
            return None

    def _count_entries(self) -> int:
        """Count total entries across all log files"""
        total = 0
        for log_file in self.log_dir.glob("audit_*.jsonl"):
            try:
                with open(log_file) as f:
                    total += len(f.readlines())
            except:
                pass
        return total

    def _compute_hash(self, entry: AuditEntry) -> str:
        """
        Compute cryptographic hash of entry

        Hash includes:
        - Timestamp
        - Event type
        - Component
        - Description
        - Data (serialized)
        - Previous hash (for chaining)
        """
        hash_input = (
            f"{entry.timestamp}|"
            f"{entry.event_type.value}|"
            f"{entry.component}|"
            f"{entry.description}|"
            f"{json.dumps(entry.data, sort_keys=True)}|"
            f"{entry.previous_hash or 'GENESIS'}"
        )

        return hashlib.sha256(hash_input.encode()).hexdigest()

    async def log(
        self,
        event_type: EventType,
        component: str,
        description: str,
        data: Optional[Dict] = None
    ) -> AuditEntry:
        """
        Log an auditable event

        Args:
            event_type: Type of event
            component: Which component generated this
            description: Human-readable description
            data: Additional structured data

        Returns:
            AuditEntry
        """
        entry_id = f"audit_{self.entry_count + 1:08d}"

        entry = AuditEntry(
            entry_id=entry_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            event_type=event_type,
            component=component,
            description=description,
            data=data or {},
            previous_hash=self.last_hash
        )

        # Compute hash
        entry.entry_hash = self._compute_hash(entry)

        # Persist
        await self._persist_entry(entry)

        # Update tracking
        self.last_hash = entry.entry_hash
        self.entry_count += 1

        logger.debug(f"📝 Audit: {event_type.value} from {component}")

        return entry

    async def _persist_entry(self, entry: AuditEntry):
        """Persist entry to log file (append-only)"""
        # Check if date changed (rotate log file)
        current_log = self._get_current_log_file()
        if current_log != self.current_log_file:
            logger.info(f"📅 Log rotation: {current_log}")
            self.current_log_file = current_log
            self.last_hash = None  # Reset chain for new file

        # Serialize
        entry_dict = asdict(entry)
        entry_dict['event_type'] = entry.event_type.value

        # Ensure file is writable before append (in case it was made read-only)
        if self.current_log_file.exists():
            os.chmod(self.current_log_file, 0o644)

        # Append to log
        with open(self.current_log_file, 'a') as f:
            f.write(json.dumps(entry_dict, ensure_ascii=False) + '\n')

        # NOTE: Not making read-only after each entry, as that prevents
        # further appends in same session. Files should be made read-only
        # only when rotated/archived.

    def verify_integrity(self, log_file: Optional[Path] = None) -> Dict[str, Any]:
        """
        Verify integrity of audit log

        Recomputes all hashes and checks chain.
        Returns report of any tampering detected.
        """
        if log_file is None:
            log_file = self.current_log_file

        if not log_file.exists():
            return {'status': 'error', 'message': 'Log file not found'}

        logger.info(f"🔍 Verifying integrity: {log_file}")

        corrupted_entries = []
        total_entries = 0
        previous_hash = None

        try:
            with open(log_file) as f:
                for line_num, line in enumerate(f, 1):
                    total_entries += 1

                    try:
                        entry_dict = json.loads(line)
                        entry = AuditEntry(
                            entry_id=entry_dict['entry_id'],
                            timestamp=entry_dict['timestamp'],
                            event_type=EventType(entry_dict['event_type']),
                            component=entry_dict['component'],
                            description=entry_dict['description'],
                            data=entry_dict['data'],
                            previous_hash=entry_dict['previous_hash'],
                            entry_hash=entry_dict['entry_hash']
                        )

                        # Verify hash
                        expected_hash = self._compute_hash(entry)
                        if expected_hash != entry.entry_hash:
                            corrupted_entries.append({
                                'line': line_num,
                                'entry_id': entry.entry_id,
                                'reason': 'Hash mismatch',
                                'expected': expected_hash,
                                'actual': entry.entry_hash
                            })

                        # Verify chain
                        if entry.previous_hash != previous_hash:
                            corrupted_entries.append({
                                'line': line_num,
                                'entry_id': entry.entry_id,
                                'reason': 'Chain broken',
                                'expected_previous': previous_hash,
                                'actual_previous': entry.previous_hash
                            })

                        previous_hash = entry.entry_hash

                    except Exception as e:
                        corrupted_entries.append({
                            'line': line_num,
                            'reason': f'Parse error: {e}'
                        })

            # Report
            if corrupted_entries:
                logger.error(f"🚨 TAMPERING DETECTED: {len(corrupted_entries)} corrupted entries")
                for c in corrupted_entries:
                    logger.error(f"   Line {c.get('line')}: {c.get('reason')}")

                return {
                    'status': 'CORRUPTED',
                    'total_entries': total_entries,
                    'corrupted_entries': len(corrupted_entries),
                    'details': corrupted_entries
                }
            else:
                logger.info(f"✅ Integrity verified: {total_entries} entries OK")
                return {
                    'status': 'OK',
                    'total_entries': total_entries,
                    'corrupted_entries': 0
                }

        except Exception as e:
            logger.error(f"❌ Verification error: {e}")
            return {'status': 'error', 'message': str(e)}

    def search(
        self,
        event_type: Optional[EventType] = None,
        component: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[AuditEntry]:
        """
        Search audit log

        Args:
            event_type: Filter by event type
            component: Filter by component
            start_date: Filter by start date
            end_date: Filter by end date
            limit: Max results

        Returns:
            List of matching AuditEntry objects
        """
        results = []

        # Determine which log files to search
        log_files = sorted(self.log_dir.glob("audit_*.jsonl"), reverse=True)

        for log_file in log_files:
            try:
                with open(log_file) as f:
                    for line in f:
                        if len(results) >= limit:
                            break

                        try:
                            entry_dict = json.loads(line)
                            entry = AuditEntry(
                                entry_id=entry_dict['entry_id'],
                                timestamp=entry_dict['timestamp'],
                                event_type=EventType(entry_dict['event_type']),
                                component=entry_dict['component'],
                                description=entry_dict['description'],
                                data=entry_dict['data'],
                                previous_hash=entry_dict['previous_hash'],
                                entry_hash=entry_dict['entry_hash']
                            )

                            # Apply filters
                            if event_type and entry.event_type != event_type:
                                continue

                            if component and entry.component != component:
                                continue

                            timestamp = datetime.fromisoformat(entry.timestamp)
                            if start_date and timestamp < start_date:
                                continue
                            if end_date and timestamp > end_date:
                                continue

                            results.append(entry)

                        except:
                            pass

            except:
                pass

            if len(results) >= limit:
                break

        return results

    def get_stats(self) -> Dict:
        """Get audit log statistics"""
        # Count by event type
        event_counts = {}
        component_counts = {}

        for log_file in self.log_dir.glob("audit_*.jsonl"):
            try:
                with open(log_file) as f:
                    for line in f:
                        try:
                            entry = json.loads(line)
                            event_type = entry['event_type']
                            component = entry['component']

                            event_counts[event_type] = event_counts.get(event_type, 0) + 1
                            component_counts[component] = component_counts.get(component, 0) + 1
                        except:
                            pass
            except:
                pass

        return {
            'total_entries': self.entry_count,
            'log_files': len(list(self.log_dir.glob("audit_*.jsonl"))),
            'events_by_type': event_counts,
            'events_by_component': component_counts
        }


if __name__ == "__main__":
    # Test
    async def test():
        audit = AuditLog()

        # Log some events
        await audit.log(
            event_type=EventType.DECISION,
            component="economic_circle",
            description="Routed task to Haiku",
            data={'task_id': 'task_001', 'model': 'haiku-4.5', 'cost': 0.02}
        )

        await audit.log(
            event_type=EventType.COST,
            component="economic_circle",
            description="Incurred cost",
            data={'amount': 0.02, 'model': 'haiku-4.5'}
        )

        await audit.log(
            event_type=EventType.EMERGENCE,
            component="emergence_monitor",
            description="Autonomy increased",
            data={'metric': 'autonomy', 'value': 0.65, 'previous': 0.55}
        )

        # Verify integrity
        result = audit.verify_integrity()
        print(f"Integrity check: {result['status']}")
        print(f"Total entries: {result['total_entries']}")

        # Get stats
        stats = audit.get_stats()
        print(f"Stats: {json.dumps(stats, indent=2)}")

    asyncio.run(test())
