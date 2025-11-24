#!/usr/bin/env python3
"""
PHEROMONE PROTOCOL - Federation Communication Layer

Stigmergy-inspirert protokoll for synkronisering mellom
lokale AIKI-HOME instanser og sentral Prime.

DESIGNPRINSIPPER:
1. Privacy-first: Aldri send personlig data
2. Efficient: Kun delta-synkronisering
3. Resilient: Fungerer offline, sync nar mulig
4. Decentralized: Hvert hjem er autonomt

Inspirert av maur-kolonier: Ingen sentral kontroll,
men emergent oppførsel via pheromone-trails.
"""

import asyncio
import hashlib
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class SyncDirection(Enum):
    """Retning for synkronisering"""
    TO_PRIME = "to_prime"      # Lokal -> Sentral
    FROM_PRIME = "from_prime"  # Sentral -> Lokal
    BIDIRECTIONAL = "bidirectional"


class MessageType(Enum):
    """Typer meldinger i protokollen"""
    # Registrering
    REGISTER = "register"
    REGISTER_ACK = "register_ack"

    # Pheromone
    PHEROMONE_UPDATE = "pheromone_update"
    PHEROMONE_BROADCAST = "pheromone_broadcast"

    # Network
    NETWORK_DIAGNOSTIC = "network_diagnostic"
    NETWORK_SOLUTION = "network_solution"

    # Health
    HEARTBEAT = "heartbeat"
    HEARTBEAT_ACK = "heartbeat_ack"

    # Control
    SYNC_REQUEST = "sync_request"
    SYNC_RESPONSE = "sync_response"


class PrivacyLevel(Enum):
    """Nivå av personvern for data"""
    PUBLIC = "public"          # Kan deles fritt (aggregert stats)
    ANONYMIZED = "anonymized"  # Anonymisert men individspesifikk
    LOCAL_ONLY = "local_only"  # Aldri forlater enheten


@dataclass
class PheromoneMessage:
    """
    En melding i pheromone-protokollen.

    Alle meldinger er signert og validert for GDPR-compliance.
    """
    message_id: str
    message_type: MessageType
    source_home_id: str
    timestamp: datetime
    payload: Dict[str, Any]
    privacy_level: PrivacyLevel

    # Signatur for verifisering
    signature: Optional[str] = None

    # Metadata (aldri personlig!)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_wire_format(self) -> bytes:
        """Serialiser til bytes for sending"""
        data = {
            'message_id': self.message_id,
            'message_type': self.message_type.value,
            'source_home_id': self.source_home_id,
            'timestamp': self.timestamp.isoformat(),
            'payload': self.payload,
            'privacy_level': self.privacy_level.value,
            'signature': self.signature,
            'metadata': self.metadata
        }
        return json.dumps(data).encode('utf-8')

    @classmethod
    def from_wire_format(cls, data: bytes) -> 'PheromoneMessage':
        """Deserialiser fra bytes"""
        parsed = json.loads(data.decode('utf-8'))
        return cls(
            message_id=parsed['message_id'],
            message_type=MessageType(parsed['message_type']),
            source_home_id=parsed['source_home_id'],
            timestamp=datetime.fromisoformat(parsed['timestamp']),
            payload=parsed['payload'],
            privacy_level=PrivacyLevel(parsed['privacy_level']),
            signature=parsed.get('signature'),
            metadata=parsed.get('metadata', {})
        )


@dataclass
class SyncState:
    """Tilstand for synkronisering med Prime"""
    last_sync: Optional[datetime] = None
    pending_updates: List[PheromoneMessage] = field(default_factory=list)
    sync_failures: int = 0
    is_online: bool = False

    # Delta tracking
    last_pheromone_version: int = 0
    last_network_version: int = 0


class PheromoneProtocol:
    """
    Pheromone Protocol - Federation Communication Layer

    Håndterer all kommunikasjon mellom lokale AIKI-HOME
    og sentral Prime. Designet for:

    1. Offline-first: Kø meldinger når offline
    2. Privacy-first: Valider alt for GDPR
    3. Efficient: Delta-sync, komprimering
    4. Resilient: Retry med backoff
    """

    def __init__(
        self,
        home_id: str,
        is_prime: bool = False,
        prime_url: Optional[str] = None
    ):
        self.home_id = home_id
        self.is_prime = is_prime
        self.prime_url = prime_url or "https://aiki-prime.local:8443"

        # State
        self.sync_state = SyncState()
        self.message_queue: asyncio.Queue = asyncio.Queue()

        # GDPR validation
        self.forbidden_fields: Set[str] = {
            'name', 'email', 'phone', 'address', 'ip_address',
            'browsing_history', 'search_queries', 'messages',
            'location', 'device_id', 'mac_address', 'ssn',
            'bank_account', 'credit_card', 'health_records',
            'password', 'social_security', 'birth_date'
        }

        # Callbacks
        self._message_handlers: Dict[MessageType, callable] = {}

        # Metrics
        self.metrics = {
            'messages_sent': 0,
            'messages_received': 0,
            'gdpr_blocks': 0,
            'sync_successes': 0,
            'sync_failures': 0
        }

        logger.info(f"PheromoneProtocol initialized for home {home_id}")

    def register_handler(self, message_type: MessageType, handler: callable):
        """Registrer handler for en meldingstype"""
        self._message_handlers[message_type] = handler

    async def send_pheromone_update(
        self,
        rule_effectiveness: Dict[str, float],
        profile_type: str,
        patterns: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Send pheromone-oppdatering til Prime.

        GDPR: Kun regel-effektivitet og anonymiserte patterns!
        """
        # Valider payload
        payload = {
            'rule_effectiveness': rule_effectiveness,
            'profile_type': profile_type,
            'patterns': patterns or {}
        }

        if not self._validate_gdpr(payload):
            logger.warning("GDPR violation blocked in pheromone update")
            self.metrics['gdpr_blocks'] += 1
            return False

        message = PheromoneMessage(
            message_id=self._generate_message_id(),
            message_type=MessageType.PHEROMONE_UPDATE,
            source_home_id=self.home_id,
            timestamp=datetime.now(timezone.utc),
            payload=payload,
            privacy_level=PrivacyLevel.ANONYMIZED
        )

        return await self._queue_message(message)

    async def send_network_diagnostic(
        self,
        problem_type: str,
        diagnostic_data: Dict[str, Any],
        isp: Optional[str] = None
    ) -> bool:
        """
        Send nettverksdiagnostikk til Network Circle.

        GDPR: Fjern IP-adresser og MAC-adresser!
        """
        # Sanitize diagnostic data
        sanitized = self._sanitize_network_data(diagnostic_data)

        payload = {
            'problem_type': problem_type,
            'diagnostic': sanitized,
            'isp': isp,
            'country': 'NO'  # Kun land, ikke mer spesifikt
        }

        if not self._validate_gdpr(payload):
            logger.warning("GDPR violation in network diagnostic")
            self.metrics['gdpr_blocks'] += 1
            return False

        message = PheromoneMessage(
            message_id=self._generate_message_id(),
            message_type=MessageType.NETWORK_DIAGNOSTIC,
            source_home_id=self.home_id,
            timestamp=datetime.now(timezone.utc),
            payload=payload,
            privacy_level=PrivacyLevel.ANONYMIZED
        )

        return await self._queue_message(message)

    async def request_recommendations(
        self,
        profile_type: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Be om anbefalinger fra Prime basert på fleet pheromones.
        """
        message = PheromoneMessage(
            message_id=self._generate_message_id(),
            message_type=MessageType.SYNC_REQUEST,
            source_home_id=self.home_id,
            timestamp=datetime.now(timezone.utc),
            payload={
                'request_type': 'recommendations',
                'profile_type': profile_type,
                'context': context or {},
                'last_pheromone_version': self.sync_state.last_pheromone_version
            },
            privacy_level=PrivacyLevel.ANONYMIZED
        )

        # For nå, simuler svar (i produksjon: faktisk HTTP/WebSocket)
        return await self._simulate_prime_response(message)

    async def heartbeat(self) -> bool:
        """Send heartbeat til Prime for online-status"""
        message = PheromoneMessage(
            message_id=self._generate_message_id(),
            message_type=MessageType.HEARTBEAT,
            source_home_id=self.home_id,
            timestamp=datetime.now(timezone.utc),
            payload={
                'status': 'online',
                'version': '1.0.0',
                'uptime_hours': 24  # Placeholder
            },
            privacy_level=PrivacyLevel.PUBLIC
        )

        success = await self._queue_message(message)
        if success:
            self.sync_state.is_online = True
            self.sync_state.last_sync = datetime.now(timezone.utc)

        return success

    async def process_incoming(self, data: bytes) -> Optional[Dict[str, Any]]:
        """Prosesser innkommende melding"""
        try:
            message = PheromoneMessage.from_wire_format(data)

            # Valider GDPR
            if not self._validate_gdpr(message.payload):
                logger.warning(f"GDPR violation in incoming message {message.message_id}")
                self.metrics['gdpr_blocks'] += 1
                return {'error': 'GDPR violation', 'accepted': False}

            # Finn handler
            handler = self._message_handlers.get(message.message_type)
            if handler:
                result = await handler(message)
                self.metrics['messages_received'] += 1
                return result

            logger.warning(f"No handler for message type {message.message_type}")
            return None

        except Exception as e:
            logger.error(f"Error processing incoming message: {e}")
            return {'error': str(e), 'accepted': False}

    async def sync_with_prime(self) -> Dict[str, Any]:
        """
        Full synkronisering med Prime.

        1. Send køede meldinger
        2. Motta nye pheromones
        3. Oppdater local state
        """
        if self.is_prime:
            return {'status': 'skipped', 'reason': 'This is Prime'}

        results = {
            'sent': 0,
            'received': 0,
            'errors': []
        }

        # Send pending messages
        while not self.message_queue.empty():
            try:
                message = await asyncio.wait_for(
                    self.message_queue.get(),
                    timeout=1.0
                )

                success = await self._send_to_prime(message)
                if success:
                    results['sent'] += 1
                else:
                    # Re-queue for retry
                    await self.message_queue.put(message)
                    results['errors'].append(f"Failed to send {message.message_id}")
                    break  # Stop on first failure

            except asyncio.TimeoutError:
                break

        # Request updates from Prime
        response = await self.request_recommendations(
            profile_type='generic',
            context={'sync': True}
        )

        if 'recommendations' in response:
            results['received'] = len(response.get('recommendations', []))
            self.sync_state.last_pheromone_version = response.get('version', 0)

        # Update state
        if results['sent'] > 0 or results['received'] > 0:
            self.sync_state.last_sync = datetime.now(timezone.utc)
            self.sync_state.sync_failures = 0
            self.metrics['sync_successes'] += 1
        elif results['errors']:
            self.sync_state.sync_failures += 1
            self.metrics['sync_failures'] += 1

        return results

    def _validate_gdpr(self, data: Dict[str, Any]) -> bool:
        """
        Valider at data ikke inneholder GDPR-sensitive felt.

        Returnerer False hvis personlig data er funnet.
        """
        def check_recursive(d: Dict, path: str = "") -> List[str]:
            violations = []
            for key, value in d.items():
                full_path = f"{path}.{key}" if path else key

                # Sjekk nøkkelnavn
                if key.lower() in self.forbidden_fields:
                    violations.append(full_path)

                # Sjekk nested
                if isinstance(value, dict):
                    violations.extend(check_recursive(value, full_path))
                elif isinstance(value, list):
                    for i, item in enumerate(value):
                        if isinstance(item, dict):
                            violations.extend(check_recursive(item, f"{full_path}[{i}]"))

            return violations

        violations = check_recursive(data)
        if violations:
            logger.warning(f"GDPR violations found: {violations}")
            return False

        return True

    def _sanitize_network_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fjern sensitiv nettverksdata.

        - IP-adresser -> erstattes med subnet-info
        - MAC-adresser -> fjernes helt
        - Hostname -> fjernes
        """
        sanitized = {}

        for key, value in data.items():
            lower_key = key.lower()

            # Skip sensitive fields
            if any(x in lower_key for x in ['ip', 'mac', 'hostname', 'address']):
                continue

            # Sanitize nested
            if isinstance(value, dict):
                sanitized[key] = self._sanitize_network_data(value)
            elif isinstance(value, str):
                # Fjern eventuelle IP-adresser i tekst
                import re
                cleaned = re.sub(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', '[IP]', value)
                sanitized[key] = cleaned
            else:
                sanitized[key] = value

        return sanitized

    def _generate_message_id(self) -> str:
        """Generer unik meldings-ID"""
        data = f"{self.home_id}:{datetime.now().isoformat()}:{id(self)}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    async def _queue_message(self, message: PheromoneMessage) -> bool:
        """Legg melding i kø for sending"""
        try:
            await self.message_queue.put(message)
            self.sync_state.pending_updates.append(message)
            self.metrics['messages_sent'] += 1
            return True
        except Exception as e:
            logger.error(f"Failed to queue message: {e}")
            return False

    async def _send_to_prime(self, message: PheromoneMessage) -> bool:
        """
        Send melding til Prime.

        I produksjon: Bruk aiohttp/websockets til prime_url
        For nå: Simuler suksess
        """
        # TODO: Implementer faktisk HTTP/WebSocket sending
        # For nå, simuler suksess for testing
        logger.info(f"[SIM] Sending message {message.message_id} to Prime")
        await asyncio.sleep(0.01)  # Simuler nettverkslatency
        return True

    async def _simulate_prime_response(
        self,
        request: PheromoneMessage
    ) -> Dict[str, Any]:
        """Simuler svar fra Prime for testing"""
        # I produksjon: Faktisk HTTP request til Prime
        return {
            'status': 'ok',
            'version': self.sync_state.last_pheromone_version + 1,
            'recommendations': [
                {
                    'rule_id': 'block_social_morning',
                    'strength': 0.78,
                    'confidence': 0.85,
                    'sample_size': 42
                },
                {
                    'rule_id': 'focus_mode_pomodoro',
                    'strength': 0.72,
                    'confidence': 0.80,
                    'sample_size': 38
                }
            ],
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

    def get_status(self) -> Dict[str, Any]:
        """Hent protokoll-status"""
        return {
            'home_id': self.home_id,
            'is_prime': self.is_prime,
            'is_online': self.sync_state.is_online,
            'last_sync': self.sync_state.last_sync.isoformat() if self.sync_state.last_sync else None,
            'pending_messages': self.message_queue.qsize(),
            'sync_failures': self.sync_state.sync_failures,
            'metrics': self.metrics
        }


async def main():
    """Test Pheromone Protocol"""
    import logging
    logging.basicConfig(level=logging.INFO)

    print("\n=== Pheromone Protocol Test ===\n")

    # Opprett lokal protokoll
    protocol = PheromoneProtocol(
        home_id='home-test-001',
        is_prime=False,
        prime_url='https://aiki-prime.local:8443'
    )

    # Test 1: Send pheromone update
    print("1. Testing pheromone update...")
    success = await protocol.send_pheromone_update(
        rule_effectiveness={
            'block_social_morning': 0.73,
            'medication_reminder': 0.95
        },
        profile_type='adhd_adult_work_from_home'
    )
    print(f"   Success: {success}")

    # Test 2: GDPR validation
    print("\n2. Testing GDPR validation...")
    bad_success = await protocol.send_pheromone_update(
        rule_effectiveness={'rule1': 0.5},
        profile_type='generic',
        patterns={'email': 'test@example.com'}  # FORBUDT!
    )
    print(f"   Blocked (correct): {not bad_success}")

    # Test 3: Network diagnostic
    print("\n3. Testing network diagnostic...")
    success = await protocol.send_network_diagnostic(
        problem_type='double_nat',
        diagnostic_data={
            'nat_type': 'symmetric',
            'upnp_available': False,
            'gateway_ip': '192.168.1.1'  # Vil bli sanitert
        },
        isp='Telenor'
    )
    print(f"   Success: {success}")

    # Test 4: Heartbeat
    print("\n4. Testing heartbeat...")
    await protocol.heartbeat()
    print(f"   Online: {protocol.sync_state.is_online}")

    # Test 5: Full sync
    print("\n5. Testing full sync...")
    results = await protocol.sync_with_prime()
    print(f"   Sent: {results['sent']}, Received: {results['received']}")

    # Status
    print("\n=== Protocol Status ===")
    status = protocol.get_status()
    print(f"Home ID: {status['home_id']}")
    print(f"Online: {status['is_online']}")
    print(f"Pending: {status['pending_messages']}")
    print(f"GDPR blocks: {status['metrics']['gdpr_blocks']}")


if __name__ == "__main__":
    asyncio.run(main())
