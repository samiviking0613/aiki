"""
AIKI Traffic Intelligence Platform
===================================
ULTIMATE MITMPROXY ADDON

Verdens mest kompliserte MITM proxy!

Integrerer alle engines:
1. TLS Fingerprinting (JA3/JA4)
2. ML App Classification
3. Behavioral Analytics
4. Content Intelligence
5. Active Intervention
6. Federation Protocol

Bruk: mitmdump --mode transparent -s aiki_ultimate_addon.py
"""

import gzip
import json
import logging
import sqlite3
import threading
import time
from datetime import datetime
from pathlib import Path

from mitmproxy import ctx, http

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [AIKI] %(levelname)s: %(message)s'
)
logger = logging.getLogger('aiki')

# Data directory
DATA_DIR = Path("/home/jovnna/aiki/data/proxy")
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Import AIKI engines
try:
    from engines.tls_fingerprint import TLSFingerprintEngine
    from engines.app_classifier import AppClassifierEngine, create_classifier
    from engines.behavioral_analytics import BehavioralAnalyticsEngine, create_analytics_engine
    from engines.content_intelligence import ContentIntelligenceEngine, create_content_intelligence
    from engines.active_intervention import ActiveInterventionEngine, create_intervention_engine
    from engines.federation import FederationEngine, create_federation_engine
    from engines.app_throttler import AppThrottler, TikTokThrottler, ThrottleLevel, create_throttler
    ENGINES_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Could not import engines: {e}")
    ENGINES_AVAILABLE = False


class SessionManager:
    """Håndterer bruker-sessions"""

    def __init__(self):
        self.sessions: dict[str, dict] = {}
        self.default_user = "kids"  # Default user profile

    def get_or_create_session(self, client_ip: str) -> dict:
        """Hent eller opprett session for klient"""
        if client_ip not in self.sessions:
            self.sessions[client_ip] = {
                'user_id': self.default_user,
                'session_id': None,
                'start_time': time.time(),
                'app_times': {},
                'current_app': None,
                'is_dopamine_loop': False,
                'last_activity': time.time()
            }
        return self.sessions[client_ip]

    def update_activity(self, client_ip: str, app: str):
        """Oppdater aktivitet"""
        session = self.get_or_create_session(client_ip)
        session['last_activity'] = time.time()
        session['current_app'] = app

        if app not in session['app_times']:
            session['app_times'][app] = 0
        session['app_times'][app] += 1


class CertPinningBypass:
    """
    SELVLÆRENDE Certificate Pinning Handler

    Strategi:
    1. Start med minimalt sett kjente pinned domener
    2. Lær automatisk fra TLS-feil
    3. Ekstraher rot-domene for bredere matching
    4. Persist til disk - overlever restart
    5. Aggressive first-fail passthrough for bedre UX
    """

    # Minimalt seed - resten læres automatisk
    SEED_DOMAINS = [
        # Banking er kritisk - må aldri MITM
        'dnb.no', 'nordea.no', 'sbanken.no', 'sparebank1.no',
        'vipps.no', 'mobilepay.no',
        # Messaging med E2E
        'whatsapp.net', 'signal.org',
    ]

    LEARNED_FILE = DATA_DIR / "learned_pinned_domains.json"

    def __init__(self):
        self.learned_domains: set[str] = set()  # Fulle domener
        self.learned_roots: set[str] = set()     # Rot-domener (f.eks. "hotmail")
        self.failure_counts: dict[str, int] = {}
        self.failure_timestamps: dict[str, float] = {}
        self._load_learned()
        logger.info(f"CertPinningBypass loaded {len(self.learned_domains)} domains, {len(self.learned_roots)} roots")

    def _extract_root(self, host: str) -> str:
        """Ekstraher rot-domene for bredere matching

        m.hotmail.com -> hotmail
        api16-normal-no1a.tiktokv.eu -> tiktokv
        v45.tiktokcdn-eu.com -> tiktokcdn
        """
        parts = host.lower().split('.')
        # Finn den mest signifikante delen (ikke tld, ikke subdomain-prefiks)
        for part in parts:
            # Skip korte deler, tall-prefiks, og TLDs
            if len(part) >= 4 and not part[0].isdigit():
                # Skip kjente prefiks
                if part not in ('www', 'api', 'cdn', 'static', 'assets', 'm'):
                    return part
        return parts[0] if parts else host

    def _load_learned(self):
        """Last lærte domener fra disk"""
        try:
            if self.LEARNED_FILE.exists():
                data = json.loads(self.LEARNED_FILE.read_text())
                self.learned_domains = set(data.get('domains', []))
                self.learned_roots = set(data.get('roots', []))
                logger.info(f"Loaded {len(self.learned_domains)} learned pinned domains")
        except Exception as e:
            logger.warning(f"Could not load learned domains: {e}")

    def _save_learned(self):
        """Lagre lærte domener til disk"""
        try:
            data = {
                'domains': list(self.learned_domains),
                'roots': list(self.learned_roots),
                'updated': datetime.now().isoformat()
            }
            self.LEARNED_FILE.write_text(json.dumps(data, indent=2))
        except Exception as e:
            logger.error(f"Could not save learned domains: {e}")

    def is_pinned(self, host: str) -> bool:
        """Sjekk om host er cert-pinned"""
        host_lower = host.lower()

        # 1. Eksakt match i lærte domener
        if host_lower in self.learned_domains:
            return True

        # 2. Rot-domene match (f.eks. "hotmail" matcher m.hotmail.com, outlook.hotmail.com, etc)
        root = self._extract_root(host_lower)
        if root in self.learned_roots:
            return True

        # 3. Seed domener (substring match)
        for domain in self.SEED_DOMAINS:
            if domain in host_lower:
                return True

        # 4. Sjekk om vi nylig har hatt feil på dette domenet (aggressiv first-fail)
        if host_lower in self.failure_counts and self.failure_counts[host_lower] >= 1:
            # Hvis vi har hatt minst 1 feil siste 5 min, passthrough
            last_fail = self.failure_timestamps.get(host_lower, 0)
            if time.time() - last_fail < 300:  # 5 minutter
                return True

        return False

    def record_failure(self, host: str):
        """Registrer TLS-feil og lær automatisk"""
        host_lower = host.lower()
        now = time.time()

        self.failure_counts[host_lower] = self.failure_counts.get(host_lower, 0) + 1
        self.failure_timestamps[host_lower] = now

        # Etter 1 feil - legg til domenet (aggressiv)
        if self.failure_counts[host_lower] >= 1:
            if host_lower not in self.learned_domains:
                self.learned_domains.add(host_lower)

                # Ekstraher og lagre rot-domene for bredere matching
                root = self._extract_root(host_lower)
                if root and len(root) >= 4:
                    self.learned_roots.add(root)
                    logger.info(f"🧠 AUTO-LEARNED: {host_lower} (root: {root})")
                else:
                    logger.info(f"🧠 AUTO-LEARNED: {host_lower}")

                # Persist til disk
                self._save_learned()

    def get_stats(self) -> dict:
        """Returner statistikk for debugging"""
        return {
            'learned_domains': len(self.learned_domains),
            'learned_roots': len(self.learned_roots),
            'recent_failures': len([t for t in self.failure_timestamps.values()
                                   if time.time() - t < 300])
        }


class AIKIUltimateAddon:
    """
    HOVEDKLASSE: AIKI Ultimate Proxy Addon

    Verdens mest kompliserte MITM proxy - spesialdesignet for
    ADHD accountability og innholds-manipulasjon.
    """

    def __init__(self):
        logger.info("=" * 60)
        logger.info("AIKI TRAFFIC INTELLIGENCE PLATFORM")
        logger.info("=" * 60)

        # Core managers
        self.session_manager = SessionManager()
        self.pinning_bypass = CertPinningBypass()

        # Statistics
        self.stats = {
            'requests_total': 0,
            'requests_intercepted': 0,
            'requests_passthrough': 0,
            'interventions_triggered': 0,
            'content_injections': 0,
            'content_blocked': 0,
            'delays_added': 0,
            'start_time': time.time()
        }

        # Initialize engines
        self._init_engines()

        # Background thread for periodic tasks
        self._running = True
        self.bg_thread = threading.Thread(target=self._background_tasks, daemon=True)
        self.bg_thread.start()

        logger.info("AIKI Ultimate Addon initialized")

    def _init_engines(self):
        """Initialize all AIKI engines"""
        if not ENGINES_AVAILABLE:
            logger.warning("Engines not available - running in basic mode")
            self.classifier = None
            self.analytics = None
            self.content_intel = None
            self.intervention = None
            self.federation = None
            return

        try:
            logger.info("Initializing TLS Fingerprint Engine...")
            self.fingerprint = TLSFingerprintEngine()  # Bruker intern DB_PATH

            logger.info("Initializing App Classifier...")
            self.classifier = create_classifier(str(DATA_DIR))

            logger.info("Initializing Behavioral Analytics...")
            self.analytics = create_analytics_engine(str(DATA_DIR))

            logger.info("Initializing Content Intelligence...")
            self.content_intel = create_content_intelligence(str(DATA_DIR))

            logger.info("Initializing Active Intervention...")
            self.intervention = create_intervention_engine(str(DATA_DIR))

            logger.info("Initializing Federation Protocol...")
            self.federation = create_federation_engine(str(DATA_DIR))

            logger.info("Initializing App Throttler...")
            self.throttler = create_throttler(str(DATA_DIR))
            self.tiktok_throttler = TikTokThrottler(self.throttler)

            logger.info("All engines initialized successfully!")

        except Exception as e:
            logger.error(f"Error initializing engines: {e}")
            self.classifier = None
            self.analytics = None
            self.content_intel = None
            self.intervention = None
            self.federation = None
            self.throttler = None
            self.tiktok_throttler = None

    def _background_tasks(self):
        """Background tasks thread"""
        while self._running:
            try:
                # Log stats hver 60 sek
                time.sleep(60)
                self._log_stats()

                # Share stats til federation hver time
                if self.federation and (time.time() % 3600) < 60:
                    self.federation.share_stats()

            except Exception as e:
                logger.error(f"Background task error: {e}")

    def _log_stats(self):
        """Log statistics"""
        uptime = time.time() - self.stats['start_time']
        pinning_stats = self.pinning_bypass.get_stats()
        logger.info(f"Stats - Uptime: {uptime/60:.1f}min, "
                   f"Total: {self.stats['requests_total']}, "
                   f"Intercepted: {self.stats['requests_intercepted']}, "
                   f"Passthrough: {self.stats['requests_passthrough']}, "
                   f"Learned domains: {pinning_stats['learned_domains']}, "
                   f"Learned roots: {pinning_stats['learned_roots']}")

    def _identify_app(self, host: str) -> str:
        """Identifiser app fra host"""
        host_lower = host.lower()

        app_patterns = {
            'tiktok': ['tiktok', 'bytedance', 'musical.ly'],
            'instagram': ['instagram', 'cdninstagram', 'fbcdn'],
            'youtube': ['youtube', 'googlevideo', 'ytimg'],
            'snapchat': ['snapchat', 'sc-cdn'],
            'twitter': ['twitter', 'x.com', 'twimg'],
            'netflix': ['netflix', 'nflxvideo'],
            'spotify': ['spotify', 'scdn'],
        }

        for app, patterns in app_patterns.items():
            if any(p in host_lower for p in patterns):
                return app

        return 'unknown'

    def _get_session_duration(self, client_ip: str) -> float:
        """Hent session varighet"""
        session = self.session_manager.get_or_create_session(client_ip)
        return time.time() - session['start_time']

    # === MITMPROXY HOOKS ===

    def load(self, loader):
        """Called when addon is loaded"""
        logger.info("AIKI addon loaded")

    def configure(self, updated):
        """Called when config is updated"""
        pass

    def proxy_running(self):
        """Called when proxy starts running"""
        logger.info("AIKI proxy is now running!")

    def tls_clienthello(self, data):
        """
        Intercept TLS ClientHello for fingerprinting

        Dette er hvor vi får JA3/JA4 fingerprints og SNI!
        """
        try:
            # Hent SNI (Server Name Indication) - dette er hostname!
            sni = data.client_hello.sni
            if not sni:
                # Fallback til IP hvis ingen SNI
                sni = data.context.server.address[0] if data.context.server.address else "unknown"

            # Lagre SNI for senere bruk i tls_failed_client
            # Vi må lagre det på context siden det ikke er tilgjengelig der
            if hasattr(data, 'context'):
                data.context._aiki_sni = sni

            # Sjekk for cert pinning
            if self.pinning_bypass.is_pinned(sni):
                logger.debug(f"Passthrough pinned: {sni}")
                data.ignore_connection = True
                self.stats['requests_passthrough'] += 1
                return

            # TODO: Parse ClientHello for JA3/JA4
            # Dette krever lavnivå TLS parsing

        except Exception as e:
            logger.debug(f"TLS clienthello error: {e}")

    def tls_failed_client(self, data):
        """Called when TLS fails - might indicate pinning"""
        try:
            # Prøv å hente SNI fra context (lagret i tls_clienthello)
            host = getattr(data.context, '_aiki_sni', None)

            # Fallback: Prøv å hente fra error message eller server address
            if not host:
                # Mitmproxy logger ofte hostname i error message
                if hasattr(data, 'error') and data.error:
                    error_str = str(data.error)
                    # Parse "for hostname" fra error message
                    if ' for ' in error_str:
                        parts = error_str.split(' for ')
                        if len(parts) > 1:
                            host = parts[1].split(' ')[0].strip('()')

            if not host:
                host = data.context.server.address[0] if data.context.server.address else "unknown"

            # Ikke lær IP-adresser direkte
            if host and not self._is_ip_address(host):
                self.pinning_bypass.record_failure(host)
            else:
                logger.debug(f"Skipping IP-based learning for: {host}")

        except Exception as e:
            logger.debug(f"TLS failed handler error: {e}")

    def _is_ip_address(self, host: str) -> bool:
        """Sjekk om host er en IP-adresse"""
        import re
        # IPv4 pattern
        ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        # IPv6 pattern (simplified)
        ipv6_pattern = r'^[0-9a-fA-F:]+$'
        return bool(re.match(ipv4_pattern, host) or re.match(ipv6_pattern, host))

    def request(self, flow: http.HTTPFlow):
        """
        Intercept HTTP request

        Her kan vi:
        - Blokkere requests
        - Legge til delay
        - Modifisere headers
        """
        self.stats['requests_total'] += 1

        try:
            host = flow.request.host
            client_ip = flow.client_conn.peername[0]
            url = flow.request.pretty_url

            # Identifiser app
            app = self._identify_app(host)

            # Oppdater session
            self.session_manager.update_activity(client_ip, app)
            session = self.session_manager.get_or_create_session(client_ip)

            # === APP THROTTLING (NYT!) ===
            if self.throttler:
                # Bruk TikTok-spesifikk throttler for TikTok
                if app == 'tiktok' and self.tiktok_throttler:
                    throttle_result = self.tiktok_throttler.process_tiktok_request(
                        url, session['user_id'], client_ip
                    )
                else:
                    throttle_result = self.throttler.process_request(
                        host, session['user_id'], client_ip
                    )

                # Apply throttling
                if throttle_result['block']:
                    self.stats['content_blocked'] += 1
                    flow.response = http.Response.make(
                        403,
                        throttle_result['message'].encode() or b"Blocked by AIKI - Take a break!",
                        {"Content-Type": "text/plain"}
                    )
                    logger.info(f"BLOCKED: {app} ({throttle_result['reason'].name})")
                    return

                if throttle_result['delay_ms'] > 0:
                    time.sleep(throttle_result['delay_ms'] / 1000)
                    self.stats['delays_added'] += 1
                    logger.debug(f"Throttled {app}: {throttle_result['delay_ms']}ms ({throttle_result['level'].name})")

                # Store throttle info for logging
                flow.metadata['aiki_throttle'] = throttle_result

            # === ENGINE INTEGRATION ===

            if self.intervention:
                # Sjekk om vi skal intervenere
                session_duration = self._get_session_duration(client_ip)

                decision = self.intervention.process_request(
                    user_id=session['user_id'],
                    app=app,
                    url=url,
                    session_duration=session_duration,
                    is_dopamine_loop=session['is_dopamine_loop']
                )

                # Delay injection
                if decision['delay_ms'] > 0:
                    time.sleep(decision['delay_ms'] / 1000)
                    self.stats['delays_added'] += 1

                # Block
                if decision['action'] == 'block':
                    self.stats['content_blocked'] += 1
                    flow.response = http.Response.make(
                        403,
                        b"Blocked by AIKI - Take a break!",
                        {"Content-Type": "text/plain"}
                    )
                    return

                # Store decision for response processing
                flow.metadata['aiki_decision'] = decision
                flow.metadata['aiki_app'] = app
                flow.metadata['aiki_user'] = session['user_id']

            self.stats['requests_intercepted'] += 1
            logger.debug(f"Request: {app} - {host}")

        except Exception as e:
            logger.error(f"Request processing error: {e}")

    def response(self, flow: http.HTTPFlow):
        """
        Intercept HTTP response

        Her kan vi:
        - Modifisere innhold (CONTENT INJECTION!)
        - Analysere innhold
        - Logge data
        """
        try:
            host = flow.request.host
            app = flow.metadata.get('aiki_app', 'unknown')
            decision = flow.metadata.get('aiki_decision', {})
            user_id = flow.metadata.get('aiki_user', 'default')

            # === TIKTOK CONTENT INJECTION ===
            if decision.get('inject_content') and app == 'tiktok':
                if self._is_tiktok_feed_response(flow):
                    self._inject_tiktok_content(flow, user_id)

            # === CONTENT INTELLIGENCE ===
            if self.content_intel and self._is_json_response(flow):
                self._analyze_content(flow, app)

            # === BEHAVIORAL ANALYTICS ===
            if self.analytics:
                self._record_analytics(flow, app)

        except Exception as e:
            logger.error(f"Response processing error: {e}")

    def _is_tiktok_feed_response(self, flow: http.HTTPFlow) -> bool:
        """Sjekk om dette er TikTok feed response"""
        url = flow.request.pretty_url
        patterns = [
            '/api/recommend/item_list',
            '/api/feed/',
            '/aweme/v1/feed',
        ]
        return any(p in url for p in patterns)

    def _is_json_response(self, flow: http.HTTPFlow) -> bool:
        """Sjekk om response er JSON"""
        content_type = flow.response.headers.get('content-type', '')
        return 'json' in content_type.lower()

    def _inject_tiktok_content(self, flow: http.HTTPFlow, user_id: str):
        """
        INJISER EDUCATIONAL CONTENT I TIKTOK FEED!

        Dette er DRØMMEN!
        """
        try:
            if not self.intervention:
                return

            body = flow.response.get_content()
            if not body:
                return

            # Process with intervention engine
            modified_body, stats = self.intervention.process_response(
                body,
                app='tiktok',
                inject_content=True,
                age_group='kids'  # TODO: Hent fra user profile
            )

            if stats['modified']:
                flow.response.set_content(modified_body)
                self.stats['content_injections'] += stats['injected']
                logger.info(f"Injected {stats['injected']} educational videos into TikTok feed!")

        except Exception as e:
            logger.error(f"TikTok injection error: {e}")

    def _analyze_content(self, flow: http.HTTPFlow, app: str):
        """Analyser innhold med Content Intelligence"""
        try:
            body = flow.response.get_content()
            if not body:
                return

            # Decompress if needed
            try:
                body_text = gzip.decompress(body).decode('utf-8')
            except:
                body_text = body.decode('utf-8')

            # Parse JSON
            try:
                data = json.loads(body_text)
            except:
                return

            # Analyze (background - don't block)
            # TODO: Send to async queue
            pass

        except Exception as e:
            logger.debug(f"Content analysis error: {e}")

    def _record_analytics(self, flow: http.HTTPFlow, app: str):
        """Record to behavioral analytics"""
        try:
            # Record event
            if 'video' in flow.request.pretty_url.lower():
                # Video event
                pass

            if 'scroll' in flow.request.pretty_url.lower():
                # Scroll event
                pass

        except Exception as e:
            logger.debug(f"Analytics error: {e}")

    def done(self):
        """Called when proxy shuts down"""
        self._running = False
        logger.info("AIKI addon shutting down")
        self._log_stats()


# Addon instance for mitmproxy
addons = [AIKIUltimateAddon()]
