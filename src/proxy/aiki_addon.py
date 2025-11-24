"""
AIKI-HOME mitmproxy Addon

Intelligent proxy addon som:
1. Automatisk detekterer certificate pinning og bytter til passthrough
2. Logger all trafikk for analyse (HTTP metadata, ikke innhold for HTTPS)
3. Implementerer AIKI decision engine for innholdsfiltrering
4. Lærer over tid hvilke domener som trenger passthrough

Overkill-features:
- Per-device trafikk-tracking
- Real-time analytics dashboard feed
- Automatisk pinning-detection learning
- Integration med AIKI decision engine
"""

import json
import logging
import os
import re
import sqlite3
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Optional

from mitmproxy import http, ctx
from mitmproxy.net.http.http1.assemble import assemble_request_head

# Logging setup
LOG_DIR = Path.home() / "aiki" / "logs" / "proxy"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "addon.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("aiki_addon")

# Database for persistent learning
DB_PATH = Path.home() / "aiki" / "data" / "proxy_learning.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


class PinningDetector:
    """Lærer hvilke domener som bruker certificate pinning"""

    # Kjente pinnede domener (hardkodet baseline)
    KNOWN_PINNED = {
        # TikTok og ByteDance
        'tiktok.com', 'tiktokv.com', 'musical.ly', 'bytedance.com',
        'byteoversea.com', 'ibytedtos.com', 'bytedapm.com',
        # Banking/Finance (høy sannsynlighet)
        'bankid.no', 'vipps.no', 'dnb.no', 'nordea.no',
        # Apple
        'apple.com', 'icloud.com', 'mzstatic.com',
        # Google sensitive
        'google.com/accounts', 'accounts.google.com',
    }

    def __init__(self):
        self.failure_count = defaultdict(int)
        self.success_count = defaultdict(int)
        self.learned_pinned = set()
        self._load_learned()

    def _get_base_domain(self, host: str) -> str:
        """Hent base domain fra host"""
        parts = host.split('.')
        if len(parts) >= 2:
            return '.'.join(parts[-2:])
        return host

    def _load_learned(self):
        """Last inn lærte pinned domener fra DB"""
        if not DB_PATH.exists():
            self._init_db()

        try:
            conn = sqlite3.connect(str(DB_PATH))
            cursor = conn.execute(
                "SELECT domain FROM pinned_domains WHERE is_pinned = 1"
            )
            self.learned_pinned = {row[0] for row in cursor.fetchall()}
            conn.close()
            logger.info(f"Lastet {len(self.learned_pinned)} lærte pinnede domener")
        except Exception as e:
            logger.error(f"Feil ved lasting av pinnede domener: {e}")

    def _init_db(self):
        """Initialiser database"""
        conn = sqlite3.connect(str(DB_PATH))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS pinned_domains (
                domain TEXT PRIMARY KEY,
                is_pinned INTEGER DEFAULT 0,
                failure_count INTEGER DEFAULT 0,
                success_count INTEGER DEFAULT 0,
                last_updated TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS traffic_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                client_ip TEXT,
                host TEXT,
                path TEXT,
                method TEXT,
                status_code INTEGER,
                content_type TEXT,
                bytes_sent INTEGER,
                duration_ms REAL,
                blocked INTEGER DEFAULT 0,
                block_reason TEXT
            )
        """)
        conn.commit()
        conn.close()

    def is_pinned(self, host: str) -> bool:
        """Sjekk om domenet bruker pinning"""
        base = self._get_base_domain(host)

        # Sjekk kjente
        if any(known in host for known in self.KNOWN_PINNED):
            return True

        # Sjekk lærte
        if base in self.learned_pinned:
            return True

        return False

    def record_success(self, host: str):
        """Registrer vellykket HTTPS intercept"""
        base = self._get_base_domain(host)
        self.success_count[base] += 1

    def record_failure(self, host: str):
        """Registrer mislykket HTTPS intercept (mulig pinning)"""
        base = self._get_base_domain(host)
        self.failure_count[base] += 1

        # Hvis > 3 failures og < 20% success rate, marker som pinned
        total = self.failure_count[base] + self.success_count[base]
        if self.failure_count[base] >= 3 and total > 0:
            success_rate = self.success_count[base] / total
            if success_rate < 0.2:
                self._mark_as_pinned(base)

    def _mark_as_pinned(self, domain: str):
        """Marker domene som pinned i DB"""
        self.learned_pinned.add(domain)
        try:
            conn = sqlite3.connect(str(DB_PATH))
            conn.execute("""
                INSERT OR REPLACE INTO pinned_domains
                (domain, is_pinned, failure_count, success_count, last_updated)
                VALUES (?, 1, ?, ?, ?)
            """, (domain, self.failure_count[domain],
                  self.success_count[domain], datetime.now().isoformat()))
            conn.commit()
            conn.close()
            logger.info(f"LÆRT: {domain} bruker certificate pinning")
        except Exception as e:
            logger.error(f"Feil ved lagring av pinned domain: {e}")


class TrafficAnalyzer:
    """Real-time trafikk-analyse"""

    def __init__(self):
        self.stats = defaultdict(lambda: {
            'requests': 0,
            'bytes': 0,
            'blocked': 0,
            'domains': defaultdict(int)
        })
        self.start_time = time.time()

    def log_request(self, client_ip: str, host: str, path: str,
                    method: str, status: int, content_type: str,
                    bytes_sent: int, duration_ms: float,
                    blocked: bool = False, reason: str = None):
        """Logg en request"""

        # Update in-memory stats
        self.stats[client_ip]['requests'] += 1
        self.stats[client_ip]['bytes'] += bytes_sent
        self.stats[client_ip]['domains'][host] += 1
        if blocked:
            self.stats[client_ip]['blocked'] += 1

        # Log til DB
        try:
            conn = sqlite3.connect(str(DB_PATH))
            conn.execute("""
                INSERT INTO traffic_log
                (timestamp, client_ip, host, path, method, status_code,
                 content_type, bytes_sent, duration_ms, blocked, block_reason)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (datetime.now().isoformat(), client_ip, host, path[:500],
                  method, status, content_type, bytes_sent, duration_ms,
                  1 if blocked else 0, reason))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"DB log error: {e}")

    def get_stats(self) -> dict:
        """Hent real-time stats"""
        uptime = time.time() - self.start_time
        return {
            'uptime_seconds': uptime,
            'clients': dict(self.stats),
            'total_requests': sum(c['requests'] for c in self.stats.values()),
            'total_bytes': sum(c['bytes'] for c in self.stats.values()),
            'total_blocked': sum(c['blocked'] for c in self.stats.values())
        }


class DecisionEngine:
    """AIKI beslutningsmotor for innholdsfiltrering"""

    # Content categories (kan utvides)
    CATEGORIES = {
        'social_media': [
            'tiktok.com', 'instagram.com', 'facebook.com', 'snapchat.com',
            'twitter.com', 'x.com', 'threads.net'
        ],
        'streaming': [
            'netflix.com', 'youtube.com', 'twitch.tv', 'disney.com',
            'hbo.com', 'viaplay.', 'tv2.no', 'nrk.no'
        ],
        'gaming': [
            'steampowered.com', 'epicgames.com', 'roblox.com',
            'minecraft.net', 'twitch.tv'
        ],
        'work': [
            'slack.com', 'teams.microsoft.com', 'notion.so',
            'linear.app', 'github.com', 'gitlab.com'
        ],
        'educational': [
            'khanacademy.org', 'coursera.org', 'duolingo.com',
            'quizlet.com', 'wikipedia.org'
        ]
    }

    def __init__(self):
        self.rules_path = Path.home() / "aiki" / "config" / "proxy_rules.json"
        self.rules = self._load_rules()
        self.active_restrictions = {}

    def _load_rules(self) -> dict:
        """Last inn regler fra config"""
        if self.rules_path.exists():
            try:
                return json.loads(self.rules_path.read_text())
            except:
                pass

        # Default regler
        return {
            'default_action': 'allow',
            'time_based': {
                'homework_hours': {
                    'start': '15:00',
                    'end': '18:00',
                    'days': [0, 1, 2, 3, 4],  # Mon-Fri
                    'block': ['social_media', 'gaming'],
                    'allow': ['educational', 'work']
                },
                'morning_routine': {
                    'start': '06:00',
                    'end': '10:00',
                    'days': [0, 1, 2, 3, 4, 5, 6],
                    'require_activity': True,
                    'block_until_activity': ['streaming', 'social_media']
                }
            },
            'device_profiles': {
                '10.8.0.2': {
                    'name': 'Jovnna iPhone',
                    'profile': 'adult'
                }
            }
        }

    def _get_category(self, host: str) -> Optional[str]:
        """Finn kategori for et domene"""
        for category, domains in self.CATEGORIES.items():
            if any(d in host for d in domains):
                return category
        return None

    def should_block(self, client_ip: str, host: str, path: str) -> tuple[bool, str]:
        """
        Beslutt om request skal blokkeres.
        Returns: (should_block, reason)
        """
        category = self._get_category(host)
        now = datetime.now()
        current_time = now.strftime('%H:%M')
        current_day = now.weekday()

        # Sjekk time-based rules
        for rule_name, rule in self.rules.get('time_based', {}).items():
            if current_day not in rule.get('days', []):
                continue

            start = rule.get('start', '00:00')
            end = rule.get('end', '23:59')

            if start <= current_time <= end:
                # I aktivt tidsvindu
                blocked_categories = rule.get('block', [])
                if category in blocked_categories:
                    return True, f"Blokkert av regel: {rule_name} ({category})"

        return False, None

    def inject_educational(self, response: http.Response) -> Optional[bytes]:
        """
        Inject educational content i response.
        Returnerer modifisert body hvis relevant, ellers None.
        """
        # TODO: Implementer innholds-injeksjon
        # Dette er der den virkelige magien skjer for AIKI-HOME
        return None


class AikiAddon:
    """Hovedaddon for AIKI-HOME transparent proxy"""

    def __init__(self):
        self.pinning = PinningDetector()
        self.analyzer = TrafficAnalyzer()
        self.decision = DecisionEngine()
        logger.info("AIKI-HOME addon initialized")

    def load(self, loader):
        """Called when addon loads"""
        loader.add_option(
            name="aiki_passthrough_all",
            typespec=bool,
            default=False,
            help="Passthrough all HTTPS (no inspection)"
        )

    def configure(self, updates):
        """Called when config changes"""
        if "aiki_passthrough_all" in updates:
            logger.info(f"Passthrough mode: {ctx.options.aiki_passthrough_all}")

    def tls_clienthello(self, data):
        """
        Kalles før TLS handshake.
        Bestem om vi skal intercept eller passthrough basert på SNI.
        """
        sni = data.context.client.sni
        if sni and self.pinning.is_pinned(sni):
            logger.debug(f"Passthrough for pinned: {sni}")
            data.ignore_connection = True

    def request(self, flow: http.HTTPFlow):
        """Håndter incoming request"""
        host = flow.request.host
        path = flow.request.path
        client_ip = flow.client_conn.peername[0]

        start_time = time.time()
        flow.metadata['start_time'] = start_time

        # Sjekk om request skal blokkeres
        should_block, reason = self.decision.should_block(client_ip, host, path)

        if should_block:
            logger.info(f"BLOCKED: {client_ip} -> {host}{path} ({reason})")
            flow.response = http.Response.make(
                403,
                b"<html><body><h1>AIKI-HOME</h1><p>Denne siden er midlertidig blokkert.</p></body></html>",
                {"Content-Type": "text/html"}
            )
            self.analyzer.log_request(
                client_ip, host, path, flow.request.method,
                403, "text/html", 0, 0, blocked=True, reason=reason
            )
            return

        logger.debug(f"REQUEST: {client_ip} -> {host}{path}")

    def response(self, flow: http.HTTPFlow):
        """Håndter response"""
        if flow.response is None:
            return

        host = flow.request.host
        path = flow.request.path
        client_ip = flow.client_conn.peername[0]

        start_time = flow.metadata.get('start_time', time.time())
        duration_ms = (time.time() - start_time) * 1000

        content_type = flow.response.headers.get('content-type', '')
        bytes_sent = len(flow.response.content or b'')

        # Log request
        self.analyzer.log_request(
            client_ip, host, path, flow.request.method,
            flow.response.status_code, content_type,
            bytes_sent, duration_ms
        )

        # Record success for pinning detection
        if flow.request.scheme == 'https':
            self.pinning.record_success(host)

        # Educational injection (future feature)
        if 'text/html' in content_type:
            modified = self.decision.inject_educational(flow.response)
            if modified:
                flow.response.content = modified

    def error(self, flow: http.HTTPFlow):
        """Håndter errors (inkl. TLS failures)"""
        if flow.error:
            host = flow.request.host if flow.request else "unknown"

            # Mulig pinning failure
            if "certificate" in str(flow.error).lower() or "ssl" in str(flow.error).lower():
                self.pinning.record_failure(host)
                logger.warning(f"TLS failure (mulig pinning): {host}")


# Registrer addon
addons = [AikiAddon()]
