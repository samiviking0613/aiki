"""
AIKI Traffic Intelligence Platform
===================================
Layer 2: ML-basert App Classifier

Bruker maskinlæring for å klassifisere applikasjoner basert på:
- TLS fingerprints (JA3/JA4)
- Traffic patterns (timing, burst, packet sizes)
- DNS queries
- SNI hostnames
- Certificate chains

Modeller:
- RandomForest for initial classification
- DBSCAN for clustering ukjente apper
- Neural network for content category prediction
- Ensemble voting for høy confidence
"""

import hashlib
import json
import pickle
import sqlite3
import statistics
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Any

import numpy as np


class AppCategory(Enum):
    """Detaljert app-kategorisering"""
    # Social Media
    SOCIAL_SHORT_VIDEO = auto()      # TikTok, Reels, Shorts
    SOCIAL_PHOTO = auto()            # Instagram, Snapchat
    SOCIAL_MESSAGING = auto()        # WhatsApp, Messenger, Signal
    SOCIAL_MICROBLOG = auto()        # Twitter/X
    SOCIAL_LONG_VIDEO = auto()       # YouTube
    SOCIAL_STREAMING = auto()        # Twitch

    # Entertainment
    STREAMING_VIDEO = auto()         # Netflix, Disney+, HBO
    STREAMING_MUSIC = auto()         # Spotify, Apple Music
    GAMING_CASUAL = auto()           # Candy Crush etc
    GAMING_HARDCORE = auto()         # PUBG, Fortnite

    # Productivity
    WORK_EMAIL = auto()              # Gmail, Outlook
    WORK_CALENDAR = auto()           # Calendar apps
    WORK_DOCS = auto()               # Google Docs, Office
    WORK_COMMUNICATION = auto()      # Slack, Teams, Zoom

    # Utilities
    UTIL_BROWSER = auto()            # Chrome, Safari, Firefox
    UTIL_MAPS = auto()               # Google Maps, Apple Maps
    UTIL_WEATHER = auto()
    UTIL_FINANCE = auto()            # Banking, trading

    # System
    SYSTEM_UPDATE = auto()           # OS updates, app updates
    SYSTEM_CLOUD_SYNC = auto()       # iCloud, Google Drive
    SYSTEM_ANALYTICS = auto()        # Crashlytics, analytics
    SYSTEM_PUSH = auto()             # Push notification services

    # ADHD-relevant
    ADHD_DOPAMINE_TRAP = auto()      # Identified dopamine hooks
    ADHD_FOCUS_TOOL = auto()         # Focus apps, timers

    # Unknown
    UNKNOWN = auto()
    ENCRYPTED_PINNED = auto()        # Can't classify - cert pinned


class AddictionRisk(Enum):
    """Avhengighetsrisiko-klassifisering"""
    CRITICAL = 5      # TikTok, gambling
    HIGH = 4          # Instagram, YouTube shorts
    MODERATE = 3      # YouTube long-form, Netflix
    LOW = 2           # Email, productivity
    BENEFICIAL = 1    # Focus tools, exercise apps


@dataclass
class TrafficSample:
    """En enkelt trafikkprøve for analyse"""
    timestamp: float
    src_ip: str
    dst_ip: str
    dst_port: int
    sni: str
    ja3_hash: str
    ja4_hash: str
    packet_sizes: list[int] = field(default_factory=list)
    inter_arrival_times: list[float] = field(default_factory=list)
    dns_queries: list[str] = field(default_factory=list)
    http_methods: list[str] = field(default_factory=list)
    content_types: list[str] = field(default_factory=list)
    total_bytes_in: int = 0
    total_bytes_out: int = 0
    connection_duration: float = 0.0


@dataclass
class AppClassification:
    """Resultat av app-klassifisering"""
    app_name: str
    app_category: AppCategory
    addiction_risk: AddictionRisk
    confidence: float  # 0.0 - 1.0
    features_used: list[str]
    classification_method: str
    metadata: dict = field(default_factory=dict)


@dataclass
class FeatureVector:
    """Normalisert feature-vektor for ML"""
    # TLS features
    ja3_cluster_id: int = 0
    ja4_cluster_id: int = 0
    tls_version: float = 0.0
    cipher_strength: float = 0.0

    # Traffic pattern features
    avg_packet_size: float = 0.0
    packet_size_variance: float = 0.0
    avg_inter_arrival: float = 0.0
    burst_ratio: float = 0.0

    # Volume features
    bytes_ratio_in_out: float = 0.0
    avg_bandwidth: float = 0.0

    # Domain features
    domain_entropy: float = 0.0
    subdomain_depth: float = 0.0
    is_cdn: float = 0.0

    # Behavioral features
    connection_frequency: float = 0.0
    session_regularity: float = 0.0

    def to_numpy(self) -> np.ndarray:
        """Konverter til numpy array"""
        return np.array([
            self.ja3_cluster_id,
            self.ja4_cluster_id,
            self.tls_version,
            self.cipher_strength,
            self.avg_packet_size,
            self.packet_size_variance,
            self.avg_inter_arrival,
            self.burst_ratio,
            self.bytes_ratio_in_out,
            self.avg_bandwidth,
            self.domain_entropy,
            self.subdomain_depth,
            self.is_cdn,
            self.connection_frequency,
            self.session_regularity
        ], dtype=np.float32)


class FeatureExtractor:
    """Ekstraherer features fra rå trafikk-data"""

    # Kjente CDN-domener
    CDN_PATTERNS = [
        'cloudfront.net', 'akamai', 'fastly', 'cloudflare',
        'cdn.', 'static.', 'assets.', 'media.', 'images.'
    ]

    @staticmethod
    def calculate_entropy(s: str) -> float:
        """Beregn Shannon entropy for en streng"""
        if not s:
            return 0.0
        prob = [s.count(c) / len(s) for c in set(s)]
        return -sum(p * np.log2(p) for p in prob if p > 0)

    @staticmethod
    def is_cdn_domain(domain: str) -> bool:
        """Sjekk om domene er CDN"""
        domain_lower = domain.lower()
        return any(cdn in domain_lower for cdn in FeatureExtractor.CDN_PATTERNS)

    @classmethod
    def extract(cls, sample: TrafficSample) -> FeatureVector:
        """Ekstraher alle features fra en trafikkprøve"""
        fv = FeatureVector()

        # Packet statistics
        if sample.packet_sizes:
            fv.avg_packet_size = statistics.mean(sample.packet_sizes) / 1500  # Normalize to MTU
            fv.packet_size_variance = statistics.variance(sample.packet_sizes) if len(sample.packet_sizes) > 1 else 0
            fv.packet_size_variance /= 1500**2  # Normalize

        # Timing statistics
        if sample.inter_arrival_times:
            fv.avg_inter_arrival = statistics.mean(sample.inter_arrival_times)
            # Burst = mange pakker med kort mellomrom
            burst_threshold = 0.01  # 10ms
            bursts = sum(1 for t in sample.inter_arrival_times if t < burst_threshold)
            fv.burst_ratio = bursts / len(sample.inter_arrival_times)

        # Volume
        total_bytes = sample.total_bytes_in + sample.total_bytes_out
        if total_bytes > 0:
            fv.bytes_ratio_in_out = sample.total_bytes_in / total_bytes
        if sample.connection_duration > 0:
            fv.avg_bandwidth = total_bytes / sample.connection_duration / 1_000_000  # MB/s

        # Domain analysis
        fv.domain_entropy = cls.calculate_entropy(sample.sni)
        fv.subdomain_depth = sample.sni.count('.') / 5.0  # Normalize
        fv.is_cdn = 1.0 if cls.is_cdn_domain(sample.sni) else 0.0

        return fv


class SignatureDatabase:
    """Database over kjente app-signaturer"""

    # Predefinerte signaturer for kjente apper
    KNOWN_SIGNATURES = {
        # TikTok
        'tiktok': {
            'domains': ['tiktok.com', 'tiktokv.com', 'bytedance', 'musical.ly',
                       'byteoversea.com', 'byteimg.com', 'bytegecko.com'],
            'category': AppCategory.SOCIAL_SHORT_VIDEO,
            'addiction_risk': AddictionRisk.CRITICAL,
            'ja3_patterns': [],  # Populated dynamically
        },
        # Instagram
        'instagram': {
            'domains': ['instagram.com', 'cdninstagram.com', 'fbcdn.net'],
            'category': AppCategory.SOCIAL_PHOTO,
            'addiction_risk': AddictionRisk.HIGH,
            'ja3_patterns': [],
        },
        # YouTube
        'youtube': {
            'domains': ['youtube.com', 'googlevideo.com', 'ytimg.com', 'yt3.ggpht.com'],
            'category': AppCategory.SOCIAL_LONG_VIDEO,
            'addiction_risk': AddictionRisk.MODERATE,
            'ja3_patterns': [],
        },
        # YouTube Shorts detection (same domain, different behavior)
        'youtube_shorts': {
            'domains': ['youtube.com'],
            'category': AppCategory.SOCIAL_SHORT_VIDEO,
            'addiction_risk': AddictionRisk.HIGH,
            'traffic_pattern': 'short_burst',  # Kort videoer = korte bursts
        },
        # Netflix
        'netflix': {
            'domains': ['netflix.com', 'nflxvideo.net', 'nflxso.net', 'nflximg.net'],
            'category': AppCategory.STREAMING_VIDEO,
            'addiction_risk': AddictionRisk.MODERATE,
            'ja3_patterns': [],
        },
        # Spotify
        'spotify': {
            'domains': ['spotify.com', 'scdn.co', 'spotifycdn.com'],
            'category': AppCategory.STREAMING_MUSIC,
            'addiction_risk': AddictionRisk.LOW,
            'ja3_patterns': [],
        },
        # WhatsApp
        'whatsapp': {
            'domains': ['whatsapp.com', 'whatsapp.net', 'wa.me'],
            'category': AppCategory.SOCIAL_MESSAGING,
            'addiction_risk': AddictionRisk.MODERATE,
            'ja3_patterns': [],
        },
        # Snapchat
        'snapchat': {
            'domains': ['snapchat.com', 'sc-cdn.net', 'snap-dev.net'],
            'category': AppCategory.SOCIAL_PHOTO,
            'addiction_risk': AddictionRisk.HIGH,
            'ja3_patterns': [],
        },
        # Twitter/X
        'twitter': {
            'domains': ['twitter.com', 'x.com', 'twimg.com', 't.co'],
            'category': AppCategory.SOCIAL_MICROBLOG,
            'addiction_risk': AddictionRisk.HIGH,
            'ja3_patterns': [],
        },
        # Twitch
        'twitch': {
            'domains': ['twitch.tv', 'ttvnw.net', 'jtvnw.net'],
            'category': AppCategory.SOCIAL_STREAMING,
            'addiction_risk': AddictionRisk.HIGH,
            'ja3_patterns': [],
        },
        # Slack
        'slack': {
            'domains': ['slack.com', 'slack-edge.com', 'slack-imgs.com'],
            'category': AppCategory.WORK_COMMUNICATION,
            'addiction_risk': AddictionRisk.LOW,
            'ja3_patterns': [],
        },
        # Gmail
        'gmail': {
            'domains': ['mail.google.com', 'gmail.com'],
            'category': AppCategory.WORK_EMAIL,
            'addiction_risk': AddictionRisk.LOW,
            'ja3_patterns': [],
        },
        # Apple services
        'apple_icloud': {
            'domains': ['icloud.com', 'apple.com', 'mzstatic.com'],
            'category': AppCategory.SYSTEM_CLOUD_SYNC,
            'addiction_risk': AddictionRisk.BENEFICIAL,
            'ja3_patterns': [],
        },
        # Banking (generic)
        'banking': {
            'domains': ['dnb.no', 'nordea.no', 'sbanken.no', 'sparebank1.no'],
            'category': AppCategory.UTIL_FINANCE,
            'addiction_risk': AddictionRisk.BENEFICIAL,
            'ja3_patterns': [],
        },
    }

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_db()
        self._domain_cache: dict[str, str] = {}
        self._build_domain_cache()

    def _init_db(self):
        """Initialiser SQLite database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS learned_signatures (
                    id INTEGER PRIMARY KEY,
                    app_name TEXT NOT NULL,
                    domain_pattern TEXT,
                    ja3_hash TEXT,
                    ja4_hash TEXT,
                    category TEXT,
                    addiction_risk INTEGER,
                    confidence REAL,
                    sample_count INTEGER DEFAULT 1,
                    first_seen TEXT,
                    last_seen TEXT,
                    UNIQUE(app_name, domain_pattern, ja3_hash)
                );

                CREATE TABLE IF NOT EXISTS traffic_clusters (
                    id INTEGER PRIMARY KEY,
                    cluster_id INTEGER,
                    centroid BLOB,
                    app_name TEXT,
                    sample_count INTEGER,
                    created_at TEXT
                );

                CREATE INDEX IF NOT EXISTS idx_learned_domain
                ON learned_signatures(domain_pattern);

                CREATE INDEX IF NOT EXISTS idx_learned_ja3
                ON learned_signatures(ja3_hash);
            """)

    def _build_domain_cache(self):
        """Bygg cache for rask domene-oppslag"""
        for app_name, sig in self.KNOWN_SIGNATURES.items():
            for domain in sig['domains']:
                self._domain_cache[domain] = app_name

    def lookup_domain(self, sni: str) -> str | None:
        """Finn app basert på SNI"""
        # Direkt match
        if sni in self._domain_cache:
            return self._domain_cache[sni]

        # Substring match
        for domain, app_name in self._domain_cache.items():
            if domain in sni or sni.endswith('.' + domain):
                return app_name

        return None

    def get_signature(self, app_name: str) -> dict | None:
        """Hent signatur for app"""
        return self.KNOWN_SIGNATURES.get(app_name)

    def learn_signature(self, app_name: str, domain: str, ja3: str,
                       ja4: str, category: AppCategory, risk: AddictionRisk):
        """Lær ny signatur"""
        now = datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO learned_signatures
                (app_name, domain_pattern, ja3_hash, ja4_hash, category,
                 addiction_risk, confidence, first_seen, last_seen)
                VALUES (?, ?, ?, ?, ?, ?, 0.5, ?, ?)
                ON CONFLICT(app_name, domain_pattern, ja3_hash) DO UPDATE SET
                    sample_count = sample_count + 1,
                    last_seen = ?,
                    confidence = MIN(confidence + 0.05, 1.0)
            """, (app_name, domain, ja3, ja4, category.name, risk.value,
                  now, now, now))


class TrafficPatternAnalyzer:
    """Analyserer trafikkpatterns for å identifisere app-type"""

    @staticmethod
    def detect_video_streaming(sample: TrafficSample) -> tuple[bool, str]:
        """Detekter video streaming basert på trafikkmønstre"""
        if not sample.packet_sizes:
            return False, ""

        avg_size = statistics.mean(sample.packet_sizes)

        # Video = store pakker, høy bandwidth
        if avg_size > 1000 and sample.total_bytes_in > 100_000:
            # Kort video vs lang video
            if sample.connection_duration < 60:
                return True, "short_video"
            else:
                return True, "long_video"

        return False, ""

    @staticmethod
    def detect_messaging(sample: TrafficSample) -> bool:
        """Detekter meldingsapper"""
        if not sample.packet_sizes:
            return False

        avg_size = statistics.mean(sample.packet_sizes)
        # Meldinger = små pakker, uregelmessig timing
        return avg_size < 500 and sample.total_bytes_in < 50_000

    @staticmethod
    def detect_infinite_scroll(samples: list[TrafficSample]) -> bool:
        """Detekter infinite scroll pattern (TikTok, Instagram feed)"""
        if len(samples) < 5:
            return False

        # Infinite scroll = regelmessige requests med lignende størrelse
        intervals = []
        for i in range(1, len(samples)):
            intervals.append(samples[i].timestamp - samples[i-1].timestamp)

        if not intervals:
            return False

        # Regelmessige intervaller mellom 2-15 sekunder = scrolling
        avg_interval = statistics.mean(intervals)
        return 2 < avg_interval < 15


class MLClassifier:
    """Maskinlæringsbasert klassifiserer"""

    def __init__(self, model_path: Path):
        self.model_path = model_path
        self.model = None
        self.label_encoder = None
        self.scaler = None
        self._load_or_init_model()

    def _load_or_init_model(self):
        """Last eksisterende modell eller initialiser ny"""
        if self.model_path.exists():
            try:
                with open(self.model_path, 'rb') as f:
                    data = pickle.load(f)
                    self.model = data['model']
                    self.label_encoder = data['label_encoder']
                    self.scaler = data['scaler']
                return
            except Exception:
                pass

        # Initialiser tom modell
        self.model = None
        self.label_encoder = {}
        self.scaler = None

    def save_model(self):
        """Lagre modell til disk"""
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.model_path, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'label_encoder': self.label_encoder,
                'scaler': self.scaler
            }, f)

    def train(self, features: list[FeatureVector], labels: list[str]):
        """Tren modell på merkede data"""
        try:
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.preprocessing import LabelEncoder, StandardScaler
        except ImportError:
            print("sklearn ikke installert - ML klassifisering deaktivert")
            return

        if len(features) < 10:
            return  # For lite data

        # Konverter til numpy
        X = np.array([f.to_numpy() for f in features])

        # Encode labels
        le = LabelEncoder()
        y = le.fit_transform(labels)

        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # Train RandomForest
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            random_state=42
        )
        model.fit(X_scaled, y)

        self.model = model
        self.label_encoder = dict(zip(le.classes_, range(len(le.classes_))))
        self.scaler = scaler
        self.save_model()

    def predict(self, feature: FeatureVector) -> tuple[str, float]:
        """Prediker app-kategori"""
        if self.model is None or self.scaler is None:
            return "unknown", 0.0

        X = feature.to_numpy().reshape(1, -1)
        X_scaled = self.scaler.transform(X)

        proba = self.model.predict_proba(X_scaled)[0]
        pred_idx = np.argmax(proba)
        confidence = proba[pred_idx]

        # Reverse label encoding
        label = None
        for name, idx in self.label_encoder.items():
            if idx == pred_idx:
                label = name
                break

        return label or "unknown", float(confidence)


class ClusteringEngine:
    """DBSCAN clustering for ukjente apper"""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.samples: list[tuple[FeatureVector, str]] = []  # (feature, sni)

    def add_sample(self, feature: FeatureVector, sni: str):
        """Legg til sample for clustering"""
        self.samples.append((feature, sni))

    def cluster(self) -> dict[int, list[str]]:
        """Utfør clustering og returner cluster -> SNI mapping"""
        if len(self.samples) < 10:
            return {}

        try:
            from sklearn.cluster import DBSCAN
            from sklearn.preprocessing import StandardScaler
        except ImportError:
            return {}

        X = np.array([s[0].to_numpy() for s in self.samples])
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        clustering = DBSCAN(eps=0.5, min_samples=3).fit(X_scaled)

        clusters: dict[int, list[str]] = defaultdict(list)
        for i, label in enumerate(clustering.labels_):
            if label >= 0:  # -1 = noise
                clusters[label].append(self.samples[i][1])

        return dict(clusters)


class AppClassifierEngine:
    """
    Hoved-engine for app-klassifisering

    Kombinerer:
    - Domain-basert lookup
    - JA3/JA4 fingerprinting
    - Traffic pattern analyse
    - ML-basert klassifisering
    - Clustering for ukjente apper
    """

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.signature_db = SignatureDatabase(data_dir / "signatures.db")
        self.ml_classifier = MLClassifier(data_dir / "ml_model.pkl")
        self.clustering = ClusteringEngine(data_dir / "clusters.db")
        self.pattern_analyzer = TrafficPatternAnalyzer()

        # Cache for nylige klassifiseringer
        self._classification_cache: dict[str, AppClassification] = {}
        self._cache_ttl = 300  # 5 minutter

        # Statistikk
        self.stats = {
            'total_classifications': 0,
            'cache_hits': 0,
            'domain_matches': 0,
            'ml_predictions': 0,
            'unknown': 0
        }

    def classify(self, sample: TrafficSample) -> AppClassification:
        """
        Klassifiser en trafikkprøve

        Prioritet:
        1. Cache hit
        2. Domain match
        3. JA3/JA4 match
        4. Traffic pattern
        5. ML prediction
        6. Clustering / Unknown
        """
        self.stats['total_classifications'] += 1

        # 1. Sjekk cache
        cache_key = f"{sample.sni}:{sample.ja3_hash}"
        if cache_key in self._classification_cache:
            self.stats['cache_hits'] += 1
            return self._classification_cache[cache_key]

        classification = self._do_classify(sample)

        # Cache resultatet
        self._classification_cache[cache_key] = classification

        # Legg til i clustering hvis ukjent
        if classification.app_category == AppCategory.UNKNOWN:
            feature = FeatureExtractor.extract(sample)
            self.clustering.add_sample(feature, sample.sni)

        return classification

    def _do_classify(self, sample: TrafficSample) -> AppClassification:
        """Intern klassifiseringslogikk"""
        features_used = []

        # 1. Domain lookup
        app_name = self.signature_db.lookup_domain(sample.sni)
        if app_name:
            self.stats['domain_matches'] += 1
            sig = self.signature_db.get_signature(app_name)
            features_used.append('domain_match')

            # Sjekk for spesielle patterns (f.eks. YouTube Shorts)
            if app_name == 'youtube':
                is_video, video_type = self.pattern_analyzer.detect_video_streaming(sample)
                if is_video and video_type == 'short_video':
                    return AppClassification(
                        app_name='youtube_shorts',
                        app_category=AppCategory.SOCIAL_SHORT_VIDEO,
                        addiction_risk=AddictionRisk.HIGH,
                        confidence=0.85,
                        features_used=['domain_match', 'traffic_pattern'],
                        classification_method='pattern_enhanced'
                    )

            return AppClassification(
                app_name=app_name,
                app_category=sig['category'],
                addiction_risk=sig['addiction_risk'],
                confidence=0.95,
                features_used=features_used,
                classification_method='domain_lookup'
            )

        # 2. Traffic pattern analyse
        is_video, video_type = self.pattern_analyzer.detect_video_streaming(sample)
        is_messaging = self.pattern_analyzer.detect_messaging(sample)

        if is_video:
            features_used.append('traffic_pattern')
            category = AppCategory.SOCIAL_SHORT_VIDEO if video_type == 'short_video' else AppCategory.STREAMING_VIDEO
            risk = AddictionRisk.HIGH if video_type == 'short_video' else AddictionRisk.MODERATE

            return AppClassification(
                app_name=f'unknown_video_{video_type}',
                app_category=category,
                addiction_risk=risk,
                confidence=0.7,
                features_used=features_used,
                classification_method='traffic_pattern'
            )

        if is_messaging:
            features_used.append('traffic_pattern')
            return AppClassification(
                app_name='unknown_messaging',
                app_category=AppCategory.SOCIAL_MESSAGING,
                addiction_risk=AddictionRisk.MODERATE,
                confidence=0.6,
                features_used=features_used,
                classification_method='traffic_pattern'
            )

        # 3. ML prediction
        feature = FeatureExtractor.extract(sample)
        ml_label, ml_confidence = self.ml_classifier.predict(feature)

        if ml_confidence > 0.7:
            self.stats['ml_predictions'] += 1
            features_used.append('ml_model')

            # Map label til category
            category = self._label_to_category(ml_label)

            return AppClassification(
                app_name=ml_label,
                app_category=category,
                addiction_risk=self._category_to_risk(category),
                confidence=ml_confidence,
                features_used=features_used,
                classification_method='ml_prediction'
            )

        # 4. Unknown
        self.stats['unknown'] += 1
        return AppClassification(
            app_name='unknown',
            app_category=AppCategory.UNKNOWN,
            addiction_risk=AddictionRisk.MODERATE,  # Conservative default
            confidence=0.0,
            features_used=[],
            classification_method='none'
        )

    def _label_to_category(self, label: str) -> AppCategory:
        """Map ML label til AppCategory"""
        label_lower = label.lower()

        if 'tiktok' in label_lower or 'shorts' in label_lower:
            return AppCategory.SOCIAL_SHORT_VIDEO
        elif 'instagram' in label_lower or 'snapchat' in label_lower:
            return AppCategory.SOCIAL_PHOTO
        elif 'youtube' in label_lower:
            return AppCategory.SOCIAL_LONG_VIDEO
        elif 'netflix' in label_lower or 'streaming' in label_lower:
            return AppCategory.STREAMING_VIDEO
        elif 'spotify' in label_lower or 'music' in label_lower:
            return AppCategory.STREAMING_MUSIC
        elif 'whatsapp' in label_lower or 'message' in label_lower:
            return AppCategory.SOCIAL_MESSAGING
        elif 'slack' in label_lower or 'teams' in label_lower:
            return AppCategory.WORK_COMMUNICATION
        elif 'mail' in label_lower or 'email' in label_lower:
            return AppCategory.WORK_EMAIL
        else:
            return AppCategory.UNKNOWN

    def _category_to_risk(self, category: AppCategory) -> AddictionRisk:
        """Map category til default addiction risk"""
        risk_map = {
            AppCategory.SOCIAL_SHORT_VIDEO: AddictionRisk.CRITICAL,
            AppCategory.SOCIAL_PHOTO: AddictionRisk.HIGH,
            AppCategory.SOCIAL_MESSAGING: AddictionRisk.MODERATE,
            AppCategory.SOCIAL_MICROBLOG: AddictionRisk.HIGH,
            AppCategory.SOCIAL_LONG_VIDEO: AddictionRisk.MODERATE,
            AppCategory.SOCIAL_STREAMING: AddictionRisk.HIGH,
            AppCategory.STREAMING_VIDEO: AddictionRisk.MODERATE,
            AppCategory.STREAMING_MUSIC: AddictionRisk.LOW,
            AppCategory.GAMING_CASUAL: AddictionRisk.HIGH,
            AppCategory.GAMING_HARDCORE: AddictionRisk.CRITICAL,
            AppCategory.WORK_EMAIL: AddictionRisk.LOW,
            AppCategory.WORK_CALENDAR: AddictionRisk.BENEFICIAL,
            AppCategory.WORK_DOCS: AddictionRisk.BENEFICIAL,
            AppCategory.WORK_COMMUNICATION: AddictionRisk.LOW,
            AppCategory.UTIL_BROWSER: AddictionRisk.MODERATE,
            AppCategory.UTIL_MAPS: AddictionRisk.BENEFICIAL,
            AppCategory.UTIL_WEATHER: AddictionRisk.BENEFICIAL,
            AppCategory.UTIL_FINANCE: AddictionRisk.BENEFICIAL,
            AppCategory.SYSTEM_UPDATE: AddictionRisk.BENEFICIAL,
            AppCategory.SYSTEM_CLOUD_SYNC: AddictionRisk.BENEFICIAL,
            AppCategory.SYSTEM_ANALYTICS: AddictionRisk.BENEFICIAL,
            AppCategory.SYSTEM_PUSH: AddictionRisk.BENEFICIAL,
            AppCategory.ADHD_DOPAMINE_TRAP: AddictionRisk.CRITICAL,
            AppCategory.ADHD_FOCUS_TOOL: AddictionRisk.BENEFICIAL,
            AppCategory.UNKNOWN: AddictionRisk.MODERATE,
            AppCategory.ENCRYPTED_PINNED: AddictionRisk.MODERATE,
        }
        return risk_map.get(category, AddictionRisk.MODERATE)

    def get_stats(self) -> dict:
        """Returner klassifiseringsstatistikk"""
        return {
            **self.stats,
            'cache_size': len(self._classification_cache),
            'pending_clusters': len(self.clustering.samples)
        }

    def train_from_history(self, samples: list[tuple[TrafficSample, str]]):
        """Tren ML-modell fra historiske merkede data"""
        features = []
        labels = []

        for sample, label in samples:
            features.append(FeatureExtractor.extract(sample))
            labels.append(label)

        self.ml_classifier.train(features, labels)

    def export_unknown_for_labeling(self) -> list[dict]:
        """Eksporter ukjente samples for manuell merking"""
        clusters = self.clustering.cluster()
        export = []

        for cluster_id, snis in clusters.items():
            export.append({
                'cluster_id': cluster_id,
                'sample_snis': snis[:10],  # Max 10 eksempler
                'count': len(snis),
                'suggested_label': None
            })

        return export


# Convenience functions for integration
def create_classifier(data_dir: str = "/home/jovnna/aiki/data/proxy") -> AppClassifierEngine:
    """Opprett app classifier engine"""
    return AppClassifierEngine(Path(data_dir))


def classify_connection(classifier: AppClassifierEngine, sni: str,
                       ja3: str, ja4: str) -> dict:
    """Quick classification for mitmproxy integration"""
    sample = TrafficSample(
        timestamp=time.time(),
        src_ip="",
        dst_ip="",
        dst_port=443,
        sni=sni,
        ja3_hash=ja3,
        ja4_hash=ja4
    )

    result = classifier.classify(sample)

    return {
        'app_name': result.app_name,
        'category': result.app_category.name,
        'addiction_risk': result.addiction_risk.name,
        'addiction_risk_level': result.addiction_risk.value,
        'confidence': result.confidence,
        'method': result.classification_method,
        'should_block': result.addiction_risk.value >= AddictionRisk.HIGH.value
    }
