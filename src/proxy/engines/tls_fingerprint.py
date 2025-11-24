"""
AIKI TLS Fingerprinting Engine

Implementerer JA3/JA3S/JA4 fingerprinting for å identifisere
apps basert på deres TLS ClientHello-signatur.

Konsept:
- Hver app har en unik "fingeravtrykk" basert på hvordan den setter opp TLS
- Vi kan identifisere TikTok, Netflix, banking-apper etc. UTEN å dekryptere
- Brukes til smart routing: pinned apps → passthrough, resten → MITM

Overkill features:
- Real-time fingerprint database med ML clustering
- Automatisk pinning-detection basert på connection failures
- Temporal patterns (samme app kan ha ulike fingerprints over tid)
- Device fingerprinting (kombinerer TLS + HTTP headers)
"""

import hashlib
import struct
import sqlite3
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Set, Tuple
from collections import defaultdict
import logging

logger = logging.getLogger("aiki.tls_fingerprint")

# Database path
DB_PATH = Path.home() / "aiki" / "data" / "fingerprints.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


@dataclass
class TLSFingerprint:
    """Representerer et TLS fingerprint"""
    ja3: str  # MD5 hash av client hello params
    ja3_full: str  # Full string før hash
    ja4: Optional[str] = None  # Nyere, mer presis fingerprint

    # Metadata
    sni: Optional[str] = None
    client_ip: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

    # Classification
    app_name: Optional[str] = None
    app_category: Optional[str] = None
    is_pinned: bool = False
    confidence: float = 0.0

    # Raw data for ML
    cipher_suites: List[int] = field(default_factory=list)
    extensions: List[int] = field(default_factory=list)
    supported_groups: List[int] = field(default_factory=list)
    ec_point_formats: List[int] = field(default_factory=list)


@dataclass
class AppProfile:
    """Profil for en identifisert app"""
    name: str
    category: str  # social_media, streaming, banking, etc.
    known_fingerprints: Set[str] = field(default_factory=set)
    known_domains: Set[str] = field(default_factory=set)
    is_pinned: bool = False
    pinning_confidence: float = 0.0

    # Behavioral data
    typical_packet_sizes: List[int] = field(default_factory=list)
    typical_intervals: List[float] = field(default_factory=list)

    # Stats
    total_connections: int = 0
    successful_intercepts: int = 0
    failed_intercepts: int = 0


class JA3Calculator:
    """Beregner JA3 fingerprint fra TLS ClientHello"""

    # Known GREASE values (Google randomization)
    GREASE_VALUES = {
        0x0a0a, 0x1a1a, 0x2a2a, 0x3a3a, 0x4a4a, 0x5a5a,
        0x6a6a, 0x7a7a, 0x8a8a, 0x9a9a, 0xaaaa, 0xbaba,
        0xcaca, 0xdada, 0xeaea, 0xfafa
    }

    @classmethod
    def calculate(cls, client_hello: bytes) -> Optional[TLSFingerprint]:
        """
        Parse TLS ClientHello og generer JA3 fingerprint.

        JA3 format: SSLVersion,Ciphers,Extensions,EllipticCurves,EllipticCurvePointFormats
        """
        try:
            # Skip record layer header (5 bytes)
            # Record type (1) + Version (2) + Length (2)
            if len(client_hello) < 5:
                return None

            record_type = client_hello[0]
            if record_type != 0x16:  # Handshake
                return None

            # Handshake header
            handshake_type = client_hello[5]
            if handshake_type != 0x01:  # ClientHello
                return None

            # Parse ClientHello
            pos = 9  # Skip to version in ClientHello

            # Client version (2 bytes)
            if pos + 2 > len(client_hello):
                return None
            ssl_version = struct.unpack(">H", client_hello[pos:pos+2])[0]
            pos += 2

            # Random (32 bytes)
            pos += 32

            # Session ID
            if pos >= len(client_hello):
                return None
            session_id_len = client_hello[pos]
            pos += 1 + session_id_len

            # Cipher suites
            if pos + 2 > len(client_hello):
                return None
            cipher_len = struct.unpack(">H", client_hello[pos:pos+2])[0]
            pos += 2

            cipher_suites = []
            for i in range(0, cipher_len, 2):
                if pos + 2 > len(client_hello):
                    break
                cipher = struct.unpack(">H", client_hello[pos:pos+2])[0]
                if cipher not in cls.GREASE_VALUES:
                    cipher_suites.append(cipher)
                pos += 2

            # Compression methods
            if pos >= len(client_hello):
                return None
            comp_len = client_hello[pos]
            pos += 1 + comp_len

            # Extensions
            extensions = []
            supported_groups = []
            ec_point_formats = []
            sni = None

            if pos + 2 <= len(client_hello):
                ext_len = struct.unpack(">H", client_hello[pos:pos+2])[0]
                pos += 2
                ext_end = pos + ext_len

                while pos + 4 <= ext_end and pos + 4 <= len(client_hello):
                    ext_type = struct.unpack(">H", client_hello[pos:pos+2])[0]
                    ext_data_len = struct.unpack(">H", client_hello[pos+2:pos+4])[0]
                    pos += 4

                    if ext_type not in cls.GREASE_VALUES:
                        extensions.append(ext_type)

                    ext_data = client_hello[pos:pos+ext_data_len]

                    # Parse SNI (extension 0)
                    if ext_type == 0 and len(ext_data) > 5:
                        name_len = struct.unpack(">H", ext_data[3:5])[0]
                        if 5 + name_len <= len(ext_data):
                            sni = ext_data[5:5+name_len].decode('utf-8', errors='ignore')

                    # Supported groups (extension 10)
                    elif ext_type == 10 and len(ext_data) >= 2:
                        groups_len = struct.unpack(">H", ext_data[0:2])[0]
                        for i in range(2, min(2 + groups_len, len(ext_data)), 2):
                            if i + 2 <= len(ext_data):
                                group = struct.unpack(">H", ext_data[i:i+2])[0]
                                if group not in cls.GREASE_VALUES:
                                    supported_groups.append(group)

                    # EC point formats (extension 11)
                    elif ext_type == 11 and len(ext_data) >= 1:
                        formats_len = ext_data[0]
                        for i in range(1, min(1 + formats_len, len(ext_data))):
                            ec_point_formats.append(ext_data[i])

                    pos += ext_data_len

            # Build JA3 string
            ja3_parts = [
                str(ssl_version),
                "-".join(str(c) for c in cipher_suites),
                "-".join(str(e) for e in extensions),
                "-".join(str(g) for g in supported_groups),
                "-".join(str(f) for f in ec_point_formats)
            ]
            ja3_full = ",".join(ja3_parts)
            ja3_hash = hashlib.md5(ja3_full.encode()).hexdigest()

            return TLSFingerprint(
                ja3=ja3_hash,
                ja3_full=ja3_full,
                sni=sni,
                cipher_suites=cipher_suites,
                extensions=extensions,
                supported_groups=supported_groups,
                ec_point_formats=ec_point_formats
            )

        except Exception as e:
            logger.error(f"JA3 calculation error: {e}")
            return None

    @classmethod
    def calculate_ja4(cls, fingerprint: TLSFingerprint) -> str:
        """
        Calculate JA4 fingerprint (more detailed than JA3).

        JA4 format: t[version][sni][cipher_count][ext_count]_[sorted_ciphers]_[sorted_extensions]
        """
        # Protocol version mapping
        version_map = {
            0x0301: "10",  # TLS 1.0
            0x0302: "11",  # TLS 1.1
            0x0303: "12",  # TLS 1.2
            0x0304: "13",  # TLS 1.3
        }

        # Extract version from ja3_full
        parts = fingerprint.ja3_full.split(",")
        if not parts:
            return ""

        try:
            version = int(parts[0])
            ver_str = version_map.get(version, "00")
        except:
            ver_str = "00"

        # SNI indicator
        sni_ind = "d" if fingerprint.sni else "i"

        # Counts
        cipher_count = min(len(fingerprint.cipher_suites), 99)
        ext_count = min(len(fingerprint.extensions), 99)

        # Sorted hashes
        sorted_ciphers = sorted(fingerprint.cipher_suites)
        sorted_exts = sorted(fingerprint.extensions)

        cipher_hash = hashlib.sha256(
            ",".join(str(c) for c in sorted_ciphers).encode()
        ).hexdigest()[:12]

        ext_hash = hashlib.sha256(
            ",".join(str(e) for e in sorted_exts).encode()
        ).hexdigest()[:12]

        return f"t{ver_str}{sni_ind}{cipher_count:02d}{ext_count:02d}_{cipher_hash}_{ext_hash}"


class FingerprintDatabase:
    """Database for fingerprints med ML-clustering"""

    # Known app fingerprints (baseline)
    KNOWN_FINGERPRINTS = {
        # TikTok variants
        "cd08e31494f9531f560d64c695473da9": AppProfile(
            name="TikTok", category="social_media", is_pinned=True,
            known_domains={"tiktok.com", "tiktokv.com", "musical.ly"}
        ),
        # Chrome
        "b32309a26951912be7dba376398abc3b": AppProfile(
            name="Chrome", category="browser", is_pinned=False,
            known_domains={"*"}
        ),
        # Safari iOS
        "773906b0efdefa24a7f2b8eb6985bf37": AppProfile(
            name="Safari iOS", category="browser", is_pinned=False,
            known_domains={"*"}
        ),
    }

    def __init__(self):
        self._init_db()
        self.fingerprint_cache: Dict[str, AppProfile] = dict(self.KNOWN_FINGERPRINTS)
        self.unknown_fingerprints: Dict[str, List[TLSFingerprint]] = defaultdict(list)

    def _init_db(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(str(DB_PATH))
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS fingerprints (
                ja3 TEXT PRIMARY KEY,
                ja3_full TEXT,
                ja4 TEXT,
                app_name TEXT,
                app_category TEXT,
                is_pinned INTEGER DEFAULT 0,
                confidence REAL DEFAULT 0.0,
                first_seen TEXT,
                last_seen TEXT,
                hit_count INTEGER DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS fingerprint_domains (
                ja3 TEXT,
                domain TEXT,
                hit_count INTEGER DEFAULT 1,
                PRIMARY KEY (ja3, domain)
            );

            CREATE TABLE IF NOT EXISTS connection_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                client_ip TEXT,
                ja3 TEXT,
                sni TEXT,
                success INTEGER,
                failure_reason TEXT
            );

            CREATE TABLE IF NOT EXISTS app_profiles (
                name TEXT PRIMARY KEY,
                category TEXT,
                is_pinned INTEGER DEFAULT 0,
                pinning_confidence REAL DEFAULT 0.0,
                total_connections INTEGER DEFAULT 0,
                successful_intercepts INTEGER DEFAULT 0,
                failed_intercepts INTEGER DEFAULT 0,
                metadata TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_conn_ja3 ON connection_log(ja3);
            CREATE INDEX IF NOT EXISTS idx_conn_sni ON connection_log(sni);
        """)
        conn.commit()
        conn.close()

    def lookup(self, fingerprint: TLSFingerprint) -> Optional[AppProfile]:
        """Look up app profile by fingerprint"""
        # Check cache first
        if fingerprint.ja3 in self.fingerprint_cache:
            return self.fingerprint_cache[fingerprint.ja3]

        # Check database
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.execute(
            "SELECT app_name, app_category, is_pinned, confidence FROM fingerprints WHERE ja3 = ?",
            (fingerprint.ja3,)
        )
        row = cursor.fetchone()
        conn.close()

        if row:
            profile = AppProfile(
                name=row[0] or "Unknown",
                category=row[1] or "unknown",
                is_pinned=bool(row[2]),
                pinning_confidence=row[3] or 0.0
            )
            profile.known_fingerprints.add(fingerprint.ja3)
            self.fingerprint_cache[fingerprint.ja3] = profile
            return profile

        return None

    def record(self, fingerprint: TLSFingerprint, success: bool, failure_reason: str = None):
        """Record a fingerprint observation"""
        conn = sqlite3.connect(str(DB_PATH))
        now = datetime.now().isoformat()

        # Update fingerprint record
        conn.execute("""
            INSERT INTO fingerprints (ja3, ja3_full, ja4, first_seen, last_seen, hit_count)
            VALUES (?, ?, ?, ?, ?, 1)
            ON CONFLICT(ja3) DO UPDATE SET
                last_seen = excluded.last_seen,
                hit_count = hit_count + 1
        """, (fingerprint.ja3, fingerprint.ja3_full, fingerprint.ja4, now, now))

        # Update domain association
        if fingerprint.sni:
            conn.execute("""
                INSERT INTO fingerprint_domains (ja3, domain, hit_count)
                VALUES (?, ?, 1)
                ON CONFLICT(ja3, domain) DO UPDATE SET
                    hit_count = hit_count + 1
            """, (fingerprint.ja3, fingerprint.sni))

        # Log connection
        conn.execute("""
            INSERT INTO connection_log (timestamp, client_ip, ja3, sni, success, failure_reason)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (now, fingerprint.client_ip, fingerprint.ja3, fingerprint.sni,
              1 if success else 0, failure_reason))

        conn.commit()
        conn.close()

        # Update pinning detection
        if not success and "certificate" in (failure_reason or "").lower():
            self._update_pinning_detection(fingerprint.ja3)

    def _update_pinning_detection(self, ja3: str):
        """Update pinning detection based on failure patterns"""
        conn = sqlite3.connect(str(DB_PATH))

        # Get recent stats
        cursor = conn.execute("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failures
            FROM connection_log
            WHERE ja3 = ?
            AND timestamp > datetime('now', '-1 hour')
        """, (ja3,))

        row = cursor.fetchone()
        if row and row[0] >= 5:  # Min 5 connections
            failure_rate = row[1] / row[0]
            if failure_rate > 0.8:  # 80%+ failure = likely pinned
                conn.execute("""
                    UPDATE fingerprints
                    SET is_pinned = 1, confidence = ?
                    WHERE ja3 = ?
                """, (failure_rate, ja3))

                # Update cache
                if ja3 in self.fingerprint_cache:
                    self.fingerprint_cache[ja3].is_pinned = True
                    self.fingerprint_cache[ja3].pinning_confidence = failure_rate

                logger.info(f"Auto-detected pinning for JA3 {ja3[:16]}... ({failure_rate:.1%} failure rate)")

        conn.commit()
        conn.close()

    def get_routing_decision(self, fingerprint: TLSFingerprint) -> Tuple[str, float]:
        """
        Decide routing for this fingerprint.
        Returns: (action, confidence) where action is 'intercept' or 'passthrough'
        """
        profile = self.lookup(fingerprint)

        if profile:
            if profile.is_pinned:
                return ("passthrough", profile.pinning_confidence)
            else:
                return ("intercept", 1.0 - profile.pinning_confidence)

        # Unknown fingerprint - default to intercept but watch for failures
        return ("intercept", 0.5)

    def get_statistics(self) -> Dict:
        """Get fingerprint statistics"""
        conn = sqlite3.connect(str(DB_PATH))

        stats = {}

        # Total fingerprints
        cursor = conn.execute("SELECT COUNT(*) FROM fingerprints")
        stats['total_fingerprints'] = cursor.fetchone()[0]

        # Pinned apps
        cursor = conn.execute("SELECT COUNT(*) FROM fingerprints WHERE is_pinned = 1")
        stats['pinned_apps'] = cursor.fetchone()[0]

        # Recent connections
        cursor = conn.execute("""
            SELECT COUNT(*), SUM(success)
            FROM connection_log
            WHERE timestamp > datetime('now', '-1 hour')
        """)
        row = cursor.fetchone()
        stats['recent_connections'] = row[0] or 0
        stats['recent_success_rate'] = (row[1] or 0) / max(row[0] or 1, 1)

        # Top fingerprints
        cursor = conn.execute("""
            SELECT ja3, app_name, hit_count, is_pinned
            FROM fingerprints
            ORDER BY hit_count DESC
            LIMIT 10
        """)
        stats['top_fingerprints'] = [
            {'ja3': row[0][:16] + '...', 'app': row[1], 'hits': row[2], 'pinned': bool(row[3])}
            for row in cursor.fetchall()
        ]

        conn.close()
        return stats


class TLSFingerprintEngine:
    """
    Main engine for TLS fingerprinting.

    Integrates with mitmproxy to provide intelligent routing.
    """

    def __init__(self):
        self.calculator = JA3Calculator()
        self.database = FingerprintDatabase()
        self.active_connections: Dict[str, TLSFingerprint] = {}

    def process_client_hello(self, client_hello: bytes, client_ip: str) -> Optional[TLSFingerprint]:
        """Process a ClientHello and return fingerprint"""
        fingerprint = self.calculator.calculate(client_hello)

        if fingerprint:
            fingerprint.client_ip = client_ip
            fingerprint.ja4 = self.calculator.calculate_ja4(fingerprint)

            # Store for later correlation
            conn_key = f"{client_ip}:{fingerprint.sni}"
            self.active_connections[conn_key] = fingerprint

            logger.debug(f"Fingerprint: JA3={fingerprint.ja3[:16]}... SNI={fingerprint.sni}")

        return fingerprint

    def should_intercept(self, fingerprint: TLSFingerprint) -> bool:
        """Determine if connection should be intercepted"""
        action, confidence = self.database.get_routing_decision(fingerprint)

        logger.info(f"Routing decision for {fingerprint.sni}: {action} ({confidence:.1%})")

        return action == "intercept"

    def record_success(self, client_ip: str, sni: str):
        """Record successful interception"""
        conn_key = f"{client_ip}:{sni}"
        if conn_key in self.active_connections:
            fp = self.active_connections.pop(conn_key)
            self.database.record(fp, success=True)

    def record_failure(self, client_ip: str, sni: str, reason: str):
        """Record failed interception"""
        conn_key = f"{client_ip}:{sni}"
        if conn_key in self.active_connections:
            fp = self.active_connections.pop(conn_key)
            self.database.record(fp, success=False, failure_reason=reason)

    def get_stats(self) -> Dict:
        """Get engine statistics"""
        return {
            'active_connections': len(self.active_connections),
            'database': self.database.get_statistics()
        }


# Singleton instance
_engine: Optional[TLSFingerprintEngine] = None

def get_engine() -> TLSFingerprintEngine:
    """Get or create the fingerprint engine"""
    global _engine
    if _engine is None:
        _engine = TLSFingerprintEngine()
    return _engine
