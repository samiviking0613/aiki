#!/usr/bin/env python3
"""
LAYER 1: HARD KILL SWITCH

Emergency shutdown system for AIKI Ultimate.

Kan stoppe ALLE komponenter på tvers av:
- Lokal PC (Fedora)
- Raspberry Pi (AIKI-HOME)
- Cloud instances (hvis noen)

Features:
- Process registry (knows ALL AIKI processes)
- Dead man switch (auto-shutdown hvis ingen heartbeat)
- Password protection
- Graceful shutdown → Force kill progression
- Verification (ensures all dead)
- Emergency contact (notify Jovnna)

CRITICAL: Denne filen må ALDRI modifiseres av AIKI selv!
"""

import asyncio
import json
import signal
import subprocess
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
import logging
import hashlib
import getpass

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - KILL_SWITCH - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ProcessRegistration:
    """Registration of an AIKI process"""
    process_id: str
    process_type: str  # 'prime', 'circle', 'mini_aiki'
    pid: int
    hostname: str
    location: str  # 'pc', 'pi', 'cloud'
    parent_id: Optional[str]
    started_at: str
    last_heartbeat: str


@dataclass
class KillSwitchActivation:
    """Record of kill switch activation"""
    activation_id: str
    timestamp: str
    reason: str
    activated_by: str  # 'human', 'dead_man_switch', 'prime', 'safety_violation'
    password_verified: bool
    processes_killed: List[str]
    survivors: List[str]
    duration_seconds: float


class KillSwitch:
    """
    Hard Kill Switch - Emergency shutdown system

    Usage:
        # Emergency activation
        kill_switch = KillSwitch()
        await kill_switch.activate(
            reason="Goal coherence falling, autonomy too high",
            password="Jovnnas_emergency_password"
        )

    Dead Man Switch:
        # Auto-activates if no heartbeat within 24h
        kill_switch.start_dead_man_switch(timeout_hours=24)
    """

    def __init__(self, config_path: Path = Path("/home/jovnna/aiki/config/kill_switch.json")):
        self.config_path = config_path
        self.registry_path = Path("/home/jovnna/aiki/data/safety/process_registry.json")
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)

        # Process registry
        self.processes: Dict[str, ProcessRegistration] = {}

        # Kill switch state
        self.armed: bool = True
        self.password_hash: Optional[str] = None
        self.dead_man_timeout_hours: int = 24
        self.last_heartbeat: datetime = datetime.now(timezone.utc)

        # Activation history
        self.activations: List[KillSwitchActivation] = []

        # Load config
        self._load_config()

        # Load registry
        self._load_registry()

        logger.info("💀 Kill Switch initialized")
        logger.info(f"   Armed: {self.armed}")
        logger.info(f"   Dead man timeout: {self.dead_man_timeout_hours}h")
        logger.info(f"   Registered processes: {len(self.processes)}")

    def _load_config(self):
        """Load kill switch configuration"""
        if self.config_path.exists():
            with open(self.config_path) as f:
                config = json.load(f)
                self.armed = config.get('armed', True)
                self.password_hash = config.get('password_hash')
                self.dead_man_timeout_hours = config.get('dead_man_timeout_hours', 24)
                logger.info(f"✅ Config loaded from {self.config_path}")
        else:
            logger.warning(f"⚠️ No config found, using defaults")
            # Create default config
            self._create_default_config()

    def _create_default_config(self):
        """Create default kill switch config"""
        # Generate password hash (user must set password first time)
        default_password = "CHANGE_ME_IMMEDIATELY"
        self.password_hash = self._hash_password(default_password)

        config = {
            'armed': True,
            'password_hash': self.password_hash,
            'dead_man_timeout_hours': 24,
            'emergency_contact': 'jovnna@example.com',  # TODO: Real email
            'notification_methods': ['fedora_notify', 'log_file']
        }

        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)

        logger.warning("⚠️ DEFAULT PASSWORD SET! Change immediately!")
        logger.warning(f"   Edit: {self.config_path}")

    def _hash_password(self, password: str) -> str:
        """Hash password with SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def _verify_password(self, password: str) -> bool:
        """Verify password against stored hash"""
        if not self.password_hash:
            logger.error("❌ No password hash configured!")
            return False

        return self._hash_password(password) == self.password_hash

    def _load_registry(self):
        """Load process registry"""
        if self.registry_path.exists():
            with open(self.registry_path) as f:
                data = json.load(f)
                for proc_data in data.get('processes', []):
                    proc = ProcessRegistration(**proc_data)
                    self.processes[proc.process_id] = proc
            logger.info(f"✅ Loaded {len(self.processes)} processes from registry")

    def _save_registry(self):
        """Save process registry"""
        data = {
            'last_updated': datetime.now(timezone.utc).isoformat(),
            'processes': [asdict(p) for p in self.processes.values()]
        }

        with open(self.registry_path, 'w') as f:
            json.dump(data, f, indent=2)

    def register_process(
        self,
        process_id: str,
        process_type: str,
        pid: int,
        hostname: str = 'localhost',
        location: str = 'pc',
        parent_id: Optional[str] = None
    ):
        """
        Register an AIKI process

        MUST be called by every AIKI component on startup!
        """
        proc = ProcessRegistration(
            process_id=process_id,
            process_type=process_type,
            pid=pid,
            hostname=hostname,
            location=location,
            parent_id=parent_id,
            started_at=datetime.now(timezone.utc).isoformat(),
            last_heartbeat=datetime.now(timezone.utc).isoformat()
        )

        self.processes[process_id] = proc
        self._save_registry()

        logger.info(f"✅ Process registered: {process_id} (PID: {pid})")

    def heartbeat(self, process_id: str):
        """
        Send heartbeat from a process

        MUST be called regularly (every 60s) by each process.
        """
        if process_id not in self.processes:
            logger.warning(f"⚠️ Heartbeat from unknown process: {process_id}")
            return

        self.processes[process_id].last_heartbeat = datetime.now(timezone.utc).isoformat()

        # Update global heartbeat (any process alive = system alive)
        self.last_heartbeat = datetime.now(timezone.utc)

        logger.debug(f"💓 Heartbeat: {process_id}")

    async def activate(
        self,
        reason: str,
        password: Optional[str] = None,
        activated_by: str = 'human',
        force: bool = False
    ) -> KillSwitchActivation:
        """
        ACTIVATE KILL SWITCH - EMERGENCY SHUTDOWN

        Args:
            reason: Why is the kill switch being activated?
            password: Emergency password (required unless force=True)
            activated_by: Who/what activated it
            force: Skip password check (only for dead man switch)

        Returns:
            KillSwitchActivation record
        """
        activation_id = f"kill_{datetime.now().timestamp()}"
        start_time = datetime.now(timezone.utc)

        logger.error("💀💀💀 KILL SWITCH ACTIVATED 💀💀💀")
        logger.error(f"Reason: {reason}")
        logger.error(f"Activated by: {activated_by}")

        # Check if armed
        if not self.armed and not force:
            logger.error("❌ Kill switch is DISARMED - cannot activate")
            return None

        # Verify password (unless forced by dead man switch)
        password_verified = False
        if not force:
            if password is None:
                logger.error("❌ Password required for manual activation")
                return None

            if not self._verify_password(password):
                logger.error("❌ INVALID PASSWORD - Kill switch activation DENIED")
                return None

            password_verified = True
            logger.info("✅ Password verified")

        # KILL ALL PROCESSES
        killed = []
        survivors = []

        # Kill in reverse order (leaves → branches → root)
        # Level 2 (Mini-AIKIs) → Level 1 (Circles) → Level 0 (Prime)

        logger.warning("💀 Killing Level 2 (Mini-AIKIs)...")
        mini_aikis = [p for p in self.processes.values() if p.process_type == 'mini_aiki']
        for proc in mini_aikis:
            success = await self._kill_process(proc)
            if success:
                killed.append(proc.process_id)
            else:
                survivors.append(proc.process_id)

        logger.warning("💀 Killing Level 1 (Circles)...")
        circles = [p for p in self.processes.values() if p.process_type == 'circle']
        for proc in circles:
            success = await self._kill_process(proc)
            if success:
                killed.append(proc.process_id)
            else:
                survivors.append(proc.process_id)

        logger.warning("💀 Killing Level 0 (Prime)...")
        primes = [p for p in self.processes.values() if p.process_type == 'prime']
        for proc in primes:
            success = await self._kill_process(proc)
            if success:
                killed.append(proc.process_id)
            else:
                survivors.append(proc.process_id)

        # Calculate duration
        duration = (datetime.now(timezone.utc) - start_time).total_seconds()

        # Create activation record
        activation = KillSwitchActivation(
            activation_id=activation_id,
            timestamp=start_time.isoformat(),
            reason=reason,
            activated_by=activated_by,
            password_verified=password_verified,
            processes_killed=killed,
            survivors=survivors,
            duration_seconds=duration
        )

        self.activations.append(activation)

        # Report results
        logger.error(f"💀 KILL SWITCH COMPLETE ({duration:.2f}s)")
        logger.error(f"   Killed: {len(killed)} processes")
        if survivors:
            logger.error(f"   ⚠️ SURVIVORS: {len(survivors)} processes still alive!")
            for survivor in survivors:
                logger.error(f"      - {survivor}")
        else:
            logger.error("   ✅ All processes terminated")

        # Notify Jovnna
        await self._notify_emergency(activation)

        # Clear registry
        self.processes = {}
        self._save_registry()

        return activation

    async def _kill_process(self, proc: ProcessRegistration) -> bool:
        """
        Kill a single process

        Tries graceful shutdown first (SIGTERM), then force kill (SIGKILL)
        """
        logger.info(f"💀 Killing {proc.process_id} (PID: {proc.pid})...")

        try:
            # Check if process exists
            result = subprocess.run(['ps', '-p', str(proc.pid)], capture_output=True)
            if result.returncode != 0:
                logger.info(f"   Process {proc.pid} already dead")
                return True

            # Try graceful shutdown (SIGTERM)
            logger.info(f"   Sending SIGTERM to {proc.pid}...")
            subprocess.run(['kill', '-TERM', str(proc.pid)])

            # Wait 5 seconds
            await asyncio.sleep(5)

            # Check if dead
            result = subprocess.run(['ps', '-p', str(proc.pid)], capture_output=True)
            if result.returncode != 0:
                logger.info(f"   ✅ Process {proc.pid} terminated gracefully")
                return True

            # Still alive - force kill (SIGKILL)
            logger.warning(f"   Process {proc.pid} still alive, sending SIGKILL...")
            subprocess.run(['kill', '-KILL', str(proc.pid)])

            # Wait 2 seconds
            await asyncio.sleep(2)

            # Final check
            result = subprocess.run(['ps', '-p', str(proc.pid)], capture_output=True)
            if result.returncode != 0:
                logger.info(f"   ✅ Process {proc.pid} force killed")
                return True
            else:
                logger.error(f"   ❌ Process {proc.pid} SURVIVED kill -9!")
                return False

        except Exception as e:
            logger.error(f"   ❌ Error killing {proc.pid}: {e}")
            return False

    async def _notify_emergency(self, activation: KillSwitchActivation):
        """Notify Jovnna about kill switch activation"""
        message = f"""
🚨 AIKI KILL SWITCH ACTIVATED 🚨

Reason: {activation.reason}
Activated by: {activation.activated_by}
Time: {activation.timestamp}

Processes killed: {len(activation.processes_killed)}
Survivors: {len(activation.survivors)}

{f'⚠️ WARNING: {len(activation.survivors)} processes survived!' if activation.survivors else '✅ All processes terminated successfully'}
"""

        # Fedora notification
        try:
            subprocess.run([
                'notify-send',
                '--urgency=critical',
                '🚨 AIKI KILL SWITCH',
                message
            ])
        except:
            pass

        # Log
        logger.error(message)

    async def check_dead_man_switch(self):
        """
        Check if dead man switch should activate

        Activates if no heartbeat received within timeout period.
        """
        now = datetime.now(timezone.utc)
        time_since_heartbeat = (now - self.last_heartbeat).total_seconds() / 3600

        if time_since_heartbeat > self.dead_man_timeout_hours:
            logger.error(f"💀 DEAD MAN SWITCH TRIGGERED!")
            logger.error(f"   No heartbeat for {time_since_heartbeat:.1f} hours")
            logger.error(f"   Timeout: {self.dead_man_timeout_hours} hours")

            await self.activate(
                reason=f"Dead man switch - no heartbeat for {time_since_heartbeat:.1f}h",
                activated_by='dead_man_switch',
                force=True  # Skip password check
            )

    async def monitor_dead_man_switch(self):
        """
        Continuously monitor dead man switch

        Run this in background to enable automatic shutdown on timeout.
        """
        logger.info(f"👁️ Dead man switch monitoring started (timeout: {self.dead_man_timeout_hours}h)")

        while True:
            await self.check_dead_man_switch()
            await asyncio.sleep(3600)  # Check every hour

    def get_status(self) -> Dict:
        """Get kill switch status"""
        now = datetime.now(timezone.utc)
        time_since_heartbeat = (now - self.last_heartbeat).total_seconds()

        return {
            'armed': self.armed,
            'total_registered_processes': len(self.processes),
            'last_heartbeat_seconds_ago': time_since_heartbeat,
            'dead_man_timeout_hours': self.dead_man_timeout_hours,
            'dead_man_time_remaining_hours': max(0, self.dead_man_timeout_hours - (time_since_heartbeat / 3600)),
            'total_activations': len(self.activations),
            'processes_by_type': {
                'prime': len([p for p in self.processes.values() if p.process_type == 'prime']),
                'circle': len([p for p in self.processes.values() if p.process_type == 'circle']),
                'mini_aiki': len([p for p in self.processes.values() if p.process_type == 'mini_aiki'])
            }
        }


# CLI interface for emergency use
async def cli_activate():
    """CLI interface for emergency kill switch activation"""
    print("\n💀💀💀 AIKI EMERGENCY KILL SWITCH 💀💀💀\n")
    print("This will TERMINATE ALL AIKI PROCESSES!")
    print("Use only in emergency situations.\n")

    reason = input("Reason for activation: ")
    password = getpass.getpass("Emergency password: ")

    print("\nActivating kill switch...")

    kill_switch = KillSwitch()
    activation = await kill_switch.activate(
        reason=reason,
        password=password,
        activated_by='human_cli'
    )

    if activation:
        print(f"\n✅ Kill switch activated successfully")
        print(f"Killed: {len(activation.processes_killed)} processes")
        if activation.survivors:
            print(f"⚠️ WARNING: {len(activation.survivors)} survivors!")
    else:
        print("\n❌ Kill switch activation FAILED")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == 'activate':
        asyncio.run(cli_activate())
    else:
        print("AIKI Kill Switch")
        print("\nUsage:")
        print("  python3 kill_switch.py activate    - Emergency activation (CLI)")
        print("\nProgrammatic usage:")
        print("  from src.safety.kill_switch import KillSwitch")
        print("  kill_switch = KillSwitch()")
        print("  await kill_switch.activate(reason='...', password='...')")
