"""
AIKI Traffic Intelligence Platform
===================================
Layer 6: Federation Protocol

Distribuert læring og deling av innsikter mellom AIKI-noder:
- Anonymisert data-sharing
- Federated learning for modell-oppdateringer
- Collective intelligence om nye trusler/patterns
- Privacy-preserving aggregation

Arkitektur:
- AIKI-HOME noder (edge)
- AIKI Prime (central aggregator)
- Peer-to-peer gossip protocol
- Differentially private statistics
"""

import hashlib
import json
import secrets
import sqlite3
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urljoin

import numpy as np


class NodeRole(Enum):
    """Rolle i federasjonen"""
    EDGE = auto()        # AIKI-HOME node
    AGGREGATOR = auto()  # Regional aggregator
    PRIME = auto()       # Central AIKI Prime


class MessageType(Enum):
    """Melding-typer i protokollen"""
    # Discovery
    HELLO = auto()
    PEER_LIST = auto()

    # Data sharing
    STATS_REPORT = auto()
    PATTERN_ALERT = auto()
    MODEL_UPDATE = auto()

    # Learning
    GRADIENT_SHARE = auto()
    MODEL_REQUEST = auto()
    MODEL_RESPONSE = auto()

    # Control
    HEARTBEAT = auto()
    CONFIG_UPDATE = auto()


@dataclass
class FederationNode:
    """En node i federasjonen"""
    node_id: str
    role: NodeRole
    public_key: str
    endpoint: str | None = None
    last_seen: float = 0.0
    reputation: float = 0.5  # 0.0 - 1.0
    capabilities: list[str] = field(default_factory=list)


@dataclass
class FederationMessage:
    """Melding i federation protocol"""
    message_id: str
    message_type: MessageType
    sender_id: str
    timestamp: float
    payload: dict
    signature: str = ""
    ttl: int = 3  # Hop count for gossip


@dataclass
class AnonymizedStats:
    """Anonymiserte statistikker for deling"""
    period_start: float
    period_end: float

    # Aggregerte tall (ingen persondata)
    total_sessions: int = 0
    total_interventions: int = 0
    intervention_success_rate: float = 0.0

    # App-kategorier (aggregert)
    time_by_category: dict[str, float] = field(default_factory=dict)
    interventions_by_category: dict[str, int] = field(default_factory=dict)

    # Pattern insights
    detected_patterns: list[str] = field(default_factory=list)
    new_fingerprints: list[str] = field(default_factory=list)

    # Effectiveness metrics
    avg_focus_improvement: float = 0.0
    avg_dopamine_reduction: float = 0.0

    # Differentially private noise added
    epsilon: float = 1.0  # Privacy budget


@dataclass
class PatternAlert:
    """Varsel om nytt pattern som bør deles"""
    pattern_id: str
    pattern_type: str  # dark_pattern, engagement_tactic, new_app
    description: str
    detection_count: int
    confidence: float
    first_seen: float
    indicators: list[str] = field(default_factory=list)


@dataclass
class ModelGradient:
    """Gradient for federated learning"""
    model_name: str
    layer_gradients: dict[str, list[float]]
    sample_count: int
    loss: float


class DifferentialPrivacy:
    """
    Differential privacy for statistikk-deling

    Legger til støy for å anonymisere data
    """

    def __init__(self, epsilon: float = 1.0, delta: float = 1e-5):
        self.epsilon = epsilon
        self.delta = delta

    def add_laplace_noise(self, value: float, sensitivity: float = 1.0) -> float:
        """Legg til Laplace-støy"""
        scale = sensitivity / self.epsilon
        noise = np.random.laplace(0, scale)
        return value + noise

    def add_gaussian_noise(self, value: float, sensitivity: float = 1.0) -> float:
        """Legg til Gaussian-støy for (ε,δ)-DP"""
        sigma = sensitivity * np.sqrt(2 * np.log(1.25 / self.delta)) / self.epsilon
        noise = np.random.normal(0, sigma)
        return value + noise

    def clip_and_noise(self, values: list[float], clip_bound: float) -> list[float]:
        """Clip verdier og legg til støy"""
        clipped = [max(-clip_bound, min(clip_bound, v)) for v in values]
        return [self.add_laplace_noise(v, clip_bound) for v in clipped]


class SecureAggregator:
    """
    Secure aggregation for federated learning

    Bruker additive secret sharing for å aggregere
    uten at sentralen ser individuelle bidrag
    """

    def __init__(self, num_parties: int, threshold: int):
        self.num_parties = num_parties
        self.threshold = threshold
        self.shares: dict[str, list[dict]] = {}  # model -> party shares

    def create_shares(self, value: float, num_shares: int) -> list[float]:
        """Del opp verdi i secret shares"""
        # Additive sharing
        shares = [secrets.randbelow(2**32) - 2**31 for _ in range(num_shares - 1)]
        final_share = int(value * 1000) - sum(shares)  # Scale for precision
        shares.append(final_share)
        return shares

    def reconstruct(self, shares: list[float]) -> float:
        """Rekonstruer verdi fra shares"""
        return sum(shares) / 1000  # Unscale


class GossipProtocol:
    """
    Gossip protocol for peer-to-peer communication

    Sprer meldinger gjennom nettverket uten sentral koordinering
    """

    def __init__(self, node_id: str, fanout: int = 3):
        self.node_id = node_id
        self.fanout = fanout
        self.seen_messages: set[str] = set()
        self.peers: list[FederationNode] = []
        self.message_handlers: dict[MessageType, Callable] = {}

    def add_peer(self, peer: FederationNode):
        """Legg til peer"""
        if peer.node_id != self.node_id:
            self.peers.append(peer)

    def remove_peer(self, node_id: str):
        """Fjern peer"""
        self.peers = [p for p in self.peers if p.node_id != node_id]

    def register_handler(self, message_type: MessageType,
                        handler: Callable[[FederationMessage], None]):
        """Registrer handler for melding-type"""
        self.message_handlers[message_type] = handler

    def broadcast(self, message: FederationMessage) -> list[str]:
        """Broadcast melding til tilfeldige peers"""
        if message.message_id in self.seen_messages:
            return []

        self.seen_messages.add(message.message_id)

        # Velg tilfeldige peers
        import random
        targets = random.sample(self.peers, min(self.fanout, len(self.peers)))

        sent_to = []
        for peer in targets:
            try:
                self._send_to_peer(peer, message)
                sent_to.append(peer.node_id)
            except Exception:
                pass

        return sent_to

    def receive(self, message: FederationMessage):
        """Motta melding"""
        if message.message_id in self.seen_messages:
            return  # Allerede sett

        self.seen_messages.add(message.message_id)

        # Kall handler
        if message.message_type in self.message_handlers:
            self.message_handlers[message.message_type](message)

        # Videresend hvis TTL > 0
        if message.ttl > 0:
            message.ttl -= 1
            self.broadcast(message)

    def _send_to_peer(self, peer: FederationNode, message: FederationMessage):
        """Send melding til peer (placeholder)"""
        # I prod: HTTP/WebSocket til peer.endpoint
        pass


class FederatedLearner:
    """
    Federated learning for ML-modeller

    Trener lokalt og deler kun gradients/updates
    """

    def __init__(self, node_id: str, dp: DifferentialPrivacy):
        self.node_id = node_id
        self.dp = dp
        self.local_models: dict[str, Any] = {}
        self.pending_gradients: list[ModelGradient] = []

    def compute_gradient(self, model_name: str, local_data: list) -> ModelGradient | None:
        """Beregn gradient basert på lokal data"""
        if model_name not in self.local_models:
            return None

        # Placeholder - i prod: faktisk gradient computation
        # Her simulerer vi med tilfeldig gradient
        gradient = {
            'layer1': [self.dp.add_laplace_noise(0.01) for _ in range(10)],
            'layer2': [self.dp.add_laplace_noise(0.005) for _ in range(5)]
        }

        return ModelGradient(
            model_name=model_name,
            layer_gradients=gradient,
            sample_count=len(local_data),
            loss=0.5
        )

    def apply_aggregated_update(self, model_name: str, aggregated_gradient: dict):
        """Oppdater lokal modell med aggregert gradient"""
        # Placeholder - i prod: faktisk modell-oppdatering
        pass


class StatsCollector:
    """
    Samler og anonymiserer statistikk for deling
    """

    def __init__(self, dp: DifferentialPrivacy):
        self.dp = dp
        self.raw_stats: dict[str, list] = {
            'sessions': [],
            'interventions': [],
            'patterns': [],
            'fingerprints': []
        }

    def record_session(self, duration: float, focus_score: float,
                      apps_used: list[str]):
        """Registrer session"""
        self.raw_stats['sessions'].append({
            'duration': duration,
            'focus_score': focus_score,
            'apps': apps_used,
            'timestamp': time.time()
        })

    def record_intervention(self, intervention_type: str, success: bool,
                           app: str):
        """Registrer intervensjon"""
        self.raw_stats['interventions'].append({
            'type': intervention_type,
            'success': success,
            'app': app,
            'timestamp': time.time()
        })

    def record_pattern(self, pattern_type: str, indicators: list[str]):
        """Registrer detektert pattern"""
        self.raw_stats['patterns'].append({
            'type': pattern_type,
            'indicators': indicators,
            'timestamp': time.time()
        })

    def create_anonymized_report(self, period_hours: int = 24) -> AnonymizedStats:
        """Lag anonymisert rapport"""
        cutoff = time.time() - (period_hours * 3600)

        # Filtrer til periode
        sessions = [s for s in self.raw_stats['sessions'] if s['timestamp'] > cutoff]
        interventions = [i for i in self.raw_stats['interventions'] if i['timestamp'] > cutoff]

        # Aggreger med DP-støy
        total_sessions = int(self.dp.add_laplace_noise(len(sessions), 1.0))
        total_interventions = int(self.dp.add_laplace_noise(len(interventions), 1.0))

        # Success rate
        if interventions:
            success_count = sum(1 for i in interventions if i['success'])
            raw_rate = success_count / len(interventions)
            success_rate = self.dp.add_laplace_noise(raw_rate, 0.1)
        else:
            success_rate = 0.0

        # Tid per kategori
        time_by_cat: dict[str, float] = {}
        for session in sessions:
            for app in session['apps']:
                cat = self._app_to_category(app)
                time_by_cat[cat] = time_by_cat.get(cat, 0) + session['duration']

        # Legg til støy på kategori-tider
        for cat in time_by_cat:
            time_by_cat[cat] = max(0, self.dp.add_laplace_noise(time_by_cat[cat], 60))

        # Patterns (bare typer, ikke detaljer)
        patterns = list(set(p['type'] for p in self.raw_stats['patterns']))

        return AnonymizedStats(
            period_start=cutoff,
            period_end=time.time(),
            total_sessions=max(0, total_sessions),
            total_interventions=max(0, total_interventions),
            intervention_success_rate=max(0, min(1, success_rate)),
            time_by_category=time_by_cat,
            detected_patterns=patterns,
            epsilon=self.dp.epsilon
        )

    def _app_to_category(self, app: str) -> str:
        """Map app til kategori"""
        categories = {
            'tiktok': 'short_video',
            'instagram': 'social',
            'youtube': 'video',
            'netflix': 'streaming',
            'spotify': 'music'
        }
        for key, cat in categories.items():
            if key in app.lower():
                return cat
        return 'other'

    def clear_old_data(self, max_age_hours: int = 168):
        """Fjern gammel data"""
        cutoff = time.time() - (max_age_hours * 3600)
        for key in self.raw_stats:
            self.raw_stats[key] = [
                item for item in self.raw_stats[key]
                if item.get('timestamp', 0) > cutoff
            ]


class FederationEngine:
    """
    HOVED-ENGINE for federation protocol

    Koordinerer:
    - Node discovery og management
    - Statistikk-deling
    - Federated learning
    - Pattern alerts
    """

    def __init__(self, data_dir: Path, node_id: str | None = None):
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Generer node ID hvis ikke gitt
        self.node_id = node_id or self._generate_node_id()
        self.role = NodeRole.EDGE

        # Privacy
        self.dp = DifferentialPrivacy(epsilon=1.0)

        # Sub-systemer
        self.gossip = GossipProtocol(self.node_id)
        self.learner = FederatedLearner(self.node_id, self.dp)
        self.stats_collector = StatsCollector(self.dp)
        self.aggregator = SecureAggregator(num_parties=10, threshold=6)

        # Peers og state
        self.known_peers: dict[str, FederationNode] = {}
        self.pending_alerts: list[PatternAlert] = []

        # Config
        self.config = {
            'report_interval': 3600,  # 1 time
            'prime_endpoint': None,  # Settes ved tilkobling
            'enable_sharing': True,
            'min_data_points': 10  # Minimum før deling
        }

        # Database
        self._init_db()

        # Register message handlers
        self._setup_handlers()

    def _generate_node_id(self) -> str:
        """Generer unik node ID"""
        return f"aiki-home-{secrets.token_hex(8)}"

    def _init_db(self):
        db_path = self.data_dir / "federation.db"
        with sqlite3.connect(db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS peers (
                    node_id TEXT PRIMARY KEY,
                    role TEXT,
                    endpoint TEXT,
                    public_key TEXT,
                    last_seen REAL,
                    reputation REAL
                );

                CREATE TABLE IF NOT EXISTS shared_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    report_hash TEXT,
                    recipient TEXT,
                    status TEXT
                );

                CREATE TABLE IF NOT EXISTS received_patterns (
                    pattern_id TEXT PRIMARY KEY,
                    pattern_type TEXT,
                    description TEXT,
                    received_at REAL,
                    source_node TEXT,
                    applied BOOLEAN
                );

                CREATE INDEX IF NOT EXISTS idx_reports_time
                ON shared_reports(timestamp);
            """)

    def _setup_handlers(self):
        """Setup message handlers"""
        self.gossip.register_handler(
            MessageType.STATS_REPORT,
            self._handle_stats_report
        )
        self.gossip.register_handler(
            MessageType.PATTERN_ALERT,
            self._handle_pattern_alert
        )
        self.gossip.register_handler(
            MessageType.MODEL_UPDATE,
            self._handle_model_update
        )
        self.gossip.register_handler(
            MessageType.PEER_LIST,
            self._handle_peer_list
        )

    def _handle_stats_report(self, message: FederationMessage):
        """Håndter mottatt stats-rapport"""
        # Kun Prime aggregerer stats
        if self.role != NodeRole.PRIME:
            return
        # TODO: Aggreger stats

    def _handle_pattern_alert(self, message: FederationMessage):
        """Håndter pattern alert"""
        alert_data = message.payload
        pattern = PatternAlert(
            pattern_id=alert_data['pattern_id'],
            pattern_type=alert_data['pattern_type'],
            description=alert_data['description'],
            detection_count=alert_data['detection_count'],
            confidence=alert_data['confidence'],
            first_seen=alert_data['first_seen'],
            indicators=alert_data.get('indicators', [])
        )

        # Lagre i database
        self._save_received_pattern(pattern, message.sender_id)

    def _handle_model_update(self, message: FederationMessage):
        """Håndter modell-oppdatering"""
        model_name = message.payload['model_name']
        gradients = message.payload['aggregated_gradient']
        self.learner.apply_aggregated_update(model_name, gradients)

    def _handle_peer_list(self, message: FederationMessage):
        """Håndter peer-liste"""
        for peer_data in message.payload.get('peers', []):
            peer = FederationNode(
                node_id=peer_data['node_id'],
                role=NodeRole[peer_data['role']],
                public_key=peer_data.get('public_key', ''),
                endpoint=peer_data.get('endpoint')
            )
            self.add_peer(peer)

    def _save_received_pattern(self, pattern: PatternAlert, source: str):
        """Lagre mottatt pattern"""
        db_path = self.data_dir / "federation.db"
        with sqlite3.connect(db_path) as conn:
            conn.execute("""
                INSERT OR IGNORE INTO received_patterns
                (pattern_id, pattern_type, description, received_at, source_node, applied)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                pattern.pattern_id,
                pattern.pattern_type,
                pattern.description,
                time.time(),
                source,
                False
            ))

    def add_peer(self, peer: FederationNode):
        """Legg til peer"""
        self.known_peers[peer.node_id] = peer
        self.gossip.add_peer(peer)

        # Lagre i database
        db_path = self.data_dir / "federation.db"
        with sqlite3.connect(db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO peers
                (node_id, role, endpoint, public_key, last_seen, reputation)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                peer.node_id,
                peer.role.name,
                peer.endpoint,
                peer.public_key,
                time.time(),
                peer.reputation
            ))

    def share_stats(self, force: bool = False) -> bool:
        """
        Del anonymiserte statistikker

        Returns: True hvis delt
        """
        if not self.config['enable_sharing']:
            return False

        # Sjekk minimum datapunkter
        total_points = sum(len(v) for v in self.stats_collector.raw_stats.values())
        if total_points < self.config['min_data_points'] and not force:
            return False

        # Lag rapport
        report = self.stats_collector.create_anonymized_report()

        # Lag melding
        message = FederationMessage(
            message_id=secrets.token_hex(16),
            message_type=MessageType.STATS_REPORT,
            sender_id=self.node_id,
            timestamp=time.time(),
            payload={
                'period_start': report.period_start,
                'period_end': report.period_end,
                'sessions': report.total_sessions,
                'interventions': report.total_interventions,
                'success_rate': report.intervention_success_rate,
                'categories': report.time_by_category,
                'patterns': report.detected_patterns,
                'epsilon': report.epsilon
            }
        )

        # Send via gossip
        sent_to = self.gossip.broadcast(message)

        # Logg
        db_path = self.data_dir / "federation.db"
        with sqlite3.connect(db_path) as conn:
            conn.execute("""
                INSERT INTO shared_reports (timestamp, report_hash, recipient, status)
                VALUES (?, ?, ?, ?)
            """, (
                time.time(),
                hashlib.sha256(json.dumps(message.payload).encode()).hexdigest()[:16],
                ','.join(sent_to),
                'sent'
            ))

        return len(sent_to) > 0

    def broadcast_pattern_alert(self, pattern: PatternAlert):
        """Broadcast varsel om nytt pattern"""
        if not self.config['enable_sharing']:
            return

        message = FederationMessage(
            message_id=secrets.token_hex(16),
            message_type=MessageType.PATTERN_ALERT,
            sender_id=self.node_id,
            timestamp=time.time(),
            payload={
                'pattern_id': pattern.pattern_id,
                'pattern_type': pattern.pattern_type,
                'description': pattern.description,
                'detection_count': pattern.detection_count,
                'confidence': pattern.confidence,
                'first_seen': pattern.first_seen,
                'indicators': pattern.indicators
            },
            ttl=5  # Spre bredt
        )

        self.gossip.broadcast(message)

    def contribute_gradient(self, model_name: str, local_data: list):
        """Bidra med gradient til federated learning"""
        gradient = self.learner.compute_gradient(model_name, local_data)
        if gradient is None:
            return

        message = FederationMessage(
            message_id=secrets.token_hex(16),
            message_type=MessageType.GRADIENT_SHARE,
            sender_id=self.node_id,
            timestamp=time.time(),
            payload={
                'model_name': gradient.model_name,
                'gradients': gradient.layer_gradients,
                'sample_count': gradient.sample_count,
                'loss': gradient.loss
            }
        )

        # Send kun til aggregator/prime
        for peer in self.known_peers.values():
            if peer.role in [NodeRole.AGGREGATOR, NodeRole.PRIME]:
                # Direct send
                pass

    def get_collective_insights(self) -> dict:
        """Hent kollektive innsikter fra nettverket"""
        db_path = self.data_dir / "federation.db"
        with sqlite3.connect(db_path) as conn:
            # Hent nylige patterns
            cursor = conn.execute("""
                SELECT pattern_type, description, COUNT(*) as count
                FROM received_patterns
                WHERE received_at > ?
                GROUP BY pattern_type
            """, (time.time() - 86400,))

            patterns = [
                {'type': row[0], 'description': row[1], 'reports': row[2]}
                for row in cursor.fetchall()
            ]

            # Peer stats
            cursor = conn.execute("SELECT COUNT(*) FROM peers")
            peer_count = cursor.fetchone()[0]

            return {
                'known_peers': peer_count,
                'recent_patterns': patterns,
                'network_active': peer_count > 0
            }

    def get_stats(self) -> dict:
        """Hent statistikk"""
        db_path = self.data_dir / "federation.db"
        with sqlite3.connect(db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM shared_reports")
            reports_sent = cursor.fetchone()[0]

            cursor = conn.execute("SELECT COUNT(*) FROM received_patterns")
            patterns_received = cursor.fetchone()[0]

            return {
                'node_id': self.node_id,
                'role': self.role.name,
                'known_peers': len(self.known_peers),
                'reports_sent': reports_sent,
                'patterns_received': patterns_received,
                'sharing_enabled': self.config['enable_sharing']
            }


# Factory function
def create_federation_engine(data_dir: str = "/home/jovnna/aiki/data/proxy",
                              node_id: str | None = None) -> FederationEngine:
    """Opprett federation engine"""
    return FederationEngine(Path(data_dir), node_id)
