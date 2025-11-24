"""
AIKI App Throttler Engine
=========================

Generisk throttling-system for alle apper med konfigurerbare nivåer.
TikTok er primær target, men fungerer for alle apper.

Throttling-teknikker:
1. Response delay (proxy-level)
2. Bandwidth limiting (tc/iptables)
3. Random packet loss simulation
4. Progressive degradation basert på bruk

Nivåer:
- OFF: Ingen throttling
- GENTLE: Knapt merkbar (200-500ms delay)
- ANNOYING: Merkbar frustrerende (1-3s delay, buffer)
- UNBEARABLE: Nesten ubrukelig (5-10s delay, konstant buffer)
- BLOCKED: Full blokkering

Forfatter: AIKI / Jovnna
Dato: 24. november 2025
"""

import json
import logging
import random
import sqlite3
import subprocess
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from pathlib import Path
from typing import Optional

logger = logging.getLogger('aiki.throttler')


class ThrottleLevel(Enum):
    """Throttling-nivåer"""
    OFF = 0
    GENTLE = 1       # Knapt merkbar
    ANNOYING = 2     # Merkbart irriterende
    UNBEARABLE = 3   # Nesten ubrukelig
    BLOCKED = 4      # Full blokkering


class ThrottleReason(Enum):
    """Hvorfor throttles appen"""
    MANUAL = auto()          # Forelder satt det manuelt
    QUOTA_EXCEEDED = auto()  # Over daglig kvote
    HOMEWORK_TIME = auto()   # Leksetid
    BEDTIME = auto()         # Leggetid
    FOCUS_MODE = auto()      # Fokus-modus aktiv
    ADAPTIVE = auto()        # ML-basert beslutning


@dataclass
class ThrottleConfig:
    """Konfigurasjon for én app"""
    app_name: str
    domains: list[str]

    # Nivå-innstillinger
    default_level: ThrottleLevel = ThrottleLevel.OFF
    current_level: ThrottleLevel = ThrottleLevel.OFF
    reason: ThrottleReason = ThrottleReason.MANUAL

    # Tidsbegrensninger
    daily_quota_minutes: int = 60  # 0 = ingen kvote
    used_today_minutes: float = 0

    # Tidsbasert throttling
    homework_hours: tuple[int, int] = (15, 18)  # 15:00-18:00
    bedtime_hour: int = 21

    # Progressive settings
    progressive_enabled: bool = True
    progressive_start_percent: int = 80  # Start throttling ved 80% av kvote

    # Delay settings per nivå (ms)
    delay_gentle: tuple[int, int] = (200, 500)
    delay_annoying: tuple[int, int] = (1000, 3000)
    delay_unbearable: tuple[int, int] = (5000, 10000)


@dataclass
class ThrottleStats:
    """Statistikk for throttling"""
    app: str
    requests_total: int = 0
    requests_throttled: int = 0
    requests_blocked: int = 0
    total_delay_added_ms: int = 0
    sessions_abandoned: int = 0  # Bruker ga opp
    last_request: Optional[datetime] = None


@dataclass
class DeviceProfile:
    """Profil for én enhet/bruker - hver kid har sin egen"""
    profile_id: str           # f.eks. "emma_iphone"
    display_name: str         # f.eks. "Emma"
    device_ips: list[str]     # WireGuard IPs: ["10.8.0.2"]

    # Type bruker
    is_child: bool = True     # False = voksen (ingen throttling)
    age: int = 10             # Alder påvirker regler

    # Globale innstillinger for denne profilen
    enabled: bool = True      # Throttling aktiv?

    # Per-app overrides (app_name -> custom config)
    app_overrides: dict = field(default_factory=dict)

    # Tidsregler for denne profilen
    homework_hours: tuple[int, int] = (15, 18)
    bedtime_hour: int = 21
    weekend_bedtime_hour: int = 22

    # Kvoter (minutter per dag)
    daily_quota_social: int = 60      # TikTok, Instagram, Snapchat
    daily_quota_streaming: int = 120  # YouTube, Netflix
    daily_quota_gaming: int = 60      # Spill

    # Stats
    created_at: datetime = field(default_factory=datetime.now)


# Default profiler - rediger i config-fil
DEFAULT_PROFILES: dict[str, DeviceProfile] = {
    # Eksempel: Jovnnas iPhone - voksen, ingen throttling
    "10.8.0.2": DeviceProfile(
        profile_id="jovnna_iphone",
        display_name="Jovnna",
        device_ips=["10.8.0.2"],
        is_child=False,
        enabled=False  # Voksne throttles ikke som default
    ),
}


# Pre-konfigurerte apper
DEFAULT_APP_CONFIGS = {
    'tiktok': ThrottleConfig(
        app_name='TikTok',
        domains=[
            'tiktok.com', 'tiktokv.com', 'bytedance.com',
            'byteoversea.com', 'byteimg.com', 'musical.ly',
            'tiktokcdn.com', 'tiktokcdn-eu.com', 'ibytedtos.com',
            'ibyteimg.com', 'ipstatp.com', 'sgsnssdk.com'
        ],
        daily_quota_minutes=30,
        homework_hours=(15, 18),
        progressive_enabled=True
    ),
    'instagram': ThrottleConfig(
        app_name='Instagram',
        domains=[
            'instagram.com', 'cdninstagram.com', 'fbcdn.net',
            'instagram.c10r.facebook.com'
        ],
        daily_quota_minutes=45,
        progressive_enabled=True
    ),
    'snapchat': ThrottleConfig(
        app_name='Snapchat',
        domains=[
            'snapchat.com', 'sc-cdn.net', 'snap-dev.net',
            'snapkit.co', 'bitmoji.com'
        ],
        daily_quota_minutes=45,
        progressive_enabled=True
    ),
    'youtube': ThrottleConfig(
        app_name='YouTube',
        domains=[
            'youtube.com', 'googlevideo.com', 'ytimg.com',
            'youtube-nocookie.com', 'youtu.be'
        ],
        daily_quota_minutes=60,
        progressive_enabled=True
    ),
    'netflix': ThrottleConfig(
        app_name='Netflix',
        domains=[
            'netflix.com', 'nflxvideo.net', 'nflximg.net',
            'nflxext.com', 'nflxso.net'
        ],
        daily_quota_minutes=90,
        progressive_enabled=True
    ),
    'twitch': ThrottleConfig(
        app_name='Twitch',
        domains=[
            'twitch.tv', 'jtvnw.net', 'twitchcdn.net',
            'ttvnw.net'
        ],
        daily_quota_minutes=60,
        progressive_enabled=True
    ),
    'twitter': ThrottleConfig(
        app_name='Twitter/X',
        domains=[
            'twitter.com', 'x.com', 'twimg.com',
            't.co', 'abs.twimg.com'
        ],
        daily_quota_minutes=30,
        progressive_enabled=True
    ),
    'reddit': ThrottleConfig(
        app_name='Reddit',
        domains=[
            'reddit.com', 'redd.it', 'redditstatic.com',
            'redditmedia.com'
        ],
        daily_quota_minutes=30,
        progressive_enabled=True
    ),
}


class AppThrottler:
    """
    Hovedklasse for app throttling

    Håndterer:
    - Per-app konfigurasjon
    - Tidsbasert throttling (leksetid, leggetid)
    - Kvote-basert progressiv degradering
    - Statistikk og logging
    """

    def __init__(self, data_dir: str | Path):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # App configs
        self.configs: dict[str, ThrottleConfig] = {}
        self.stats: dict[str, ThrottleStats] = {}

        # User-specific overrides
        self.user_configs: dict[str, dict[str, ThrottleConfig]] = {}

        # Device profiles: IP -> profil
        self.profiles: dict[str, DeviceProfile] = {}
        self._load_profiles()

        # Session tracking
        self.active_sessions: dict[str, dict] = {}  # client_ip -> session data

        # Database
        self.db_path = self.data_dir / "throttle_data.db"
        self._init_database()

        # Load configs
        self._load_default_configs()
        self._load_saved_configs()

        logger.info(f"AppThrottler initialized with {len(self.configs)} apps, {len(self.profiles)} device profiles")

    def _load_profiles(self):
        """Last device profiles fra config-fil eller defaults"""
        config_file = self.data_dir / "device_profiles.json"

        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    data = json.load(f)
                for ip, profile_data in data.items():
                    self.profiles[ip] = DeviceProfile(**profile_data)
                logger.info(f"Loaded {len(self.profiles)} profiles from {config_file}")
            except Exception as e:
                logger.error(f"Error loading profiles: {e}")
                self.profiles = dict(DEFAULT_PROFILES)
        else:
            # Bruk defaults og lagre
            self.profiles = dict(DEFAULT_PROFILES)
            self._save_profiles()

    def _save_profiles(self):
        """Lagre profiles til JSON"""
        config_file = self.data_dir / "device_profiles.json"
        data = {}
        for ip, profile in self.profiles.items():
            data[ip] = {
                'profile_id': profile.profile_id,
                'display_name': profile.display_name,
                'device_ips': profile.device_ips,
                'is_child': profile.is_child,
                'age': profile.age,
                'enabled': profile.enabled,
                'app_overrides': profile.app_overrides,
                'homework_hours': list(profile.homework_hours),
                'bedtime_hour': profile.bedtime_hour,
                'weekend_bedtime_hour': profile.weekend_bedtime_hour,
                'daily_quota_social': profile.daily_quota_social,
                'daily_quota_streaming': profile.daily_quota_streaming,
                'daily_quota_gaming': profile.daily_quota_gaming,
            }
        with open(config_file, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Saved {len(data)} profiles to {config_file}")

    def get_profile(self, client_ip: str) -> Optional[DeviceProfile]:
        """Hent profil for en IP-adresse"""
        return self.profiles.get(client_ip)

    def add_profile(self, profile: DeviceProfile) -> None:
        """Legg til eller oppdater en profil"""
        for ip in profile.device_ips:
            self.profiles[ip] = profile
        self._save_profiles()
        logger.info(f"Added profile '{profile.profile_id}' for IPs: {profile.device_ips}")

    def should_throttle(self, client_ip: str) -> bool:
        """Sjekk om trafikk fra denne IP skal throttles"""
        profile = self.get_profile(client_ip)
        if profile is None:
            # Ukjent enhet - throttle som default (sikkerhet)
            return True
        return profile.enabled and profile.is_child

    def _init_database(self):
        """Opprett database-tabeller"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # App usage tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS app_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                app_name TEXT NOT NULL,
                date TEXT NOT NULL,
                minutes_used REAL DEFAULT 0,
                requests_total INTEGER DEFAULT 0,
                requests_throttled INTEGER DEFAULT 0,
                sessions_abandoned INTEGER DEFAULT 0,
                UNIQUE(user_id, app_name, date)
            )
        ''')

        # Throttle events
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS throttle_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                user_id TEXT NOT NULL,
                app_name TEXT NOT NULL,
                level TEXT NOT NULL,
                reason TEXT NOT NULL,
                delay_ms INTEGER DEFAULT 0
            )
        ''')

        # User preferences
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                user_id TEXT PRIMARY KEY,
                config_json TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')

        conn.commit()
        conn.close()

    def _load_default_configs(self):
        """Last standard app-konfigurasjoner"""
        for app_key, config in DEFAULT_APP_CONFIGS.items():
            self.configs[app_key] = config
            self.stats[app_key] = ThrottleStats(app=app_key)

    def _load_saved_configs(self):
        """Last lagrede konfigurasjoner fra database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            cursor.execute('SELECT user_id, config_json FROM user_preferences')
            rows = cursor.fetchall()

            for user_id, config_json in rows:
                try:
                    self.user_configs[user_id] = json.loads(config_json)
                except json.JSONDecodeError:
                    pass

            conn.close()
        except Exception as e:
            logger.error(f"Error loading configs: {e}")

    def identify_app(self, host: str) -> Optional[str]:
        """Identifiser app fra hostname"""
        host_lower = host.lower()

        for app_key, config in self.configs.items():
            for domain in config.domains:
                if domain in host_lower:
                    return app_key

        return None

    def get_config(self, app: str, user_id: str = 'default') -> Optional[ThrottleConfig]:
        """Hent config for app, med user overrides"""
        if app not in self.configs:
            return None

        base_config = self.configs[app]

        # Check user-specific config
        if user_id in self.user_configs and app in self.user_configs[user_id]:
            # Merge user config over base
            user_conf = self.user_configs[user_id][app]
            # For now, just return base (TODO: proper merge)
            pass

        return base_config

    def calculate_throttle_level(
        self,
        app: str,
        user_id: str = 'default',
        current_time: Optional[datetime] = None
    ) -> tuple[ThrottleLevel, ThrottleReason]:
        """
        Beregn throttle-nivå basert på:
        1. Manuell setting
        2. Tidsbasert (leksetid, leggetid)
        3. Kvote-basert progressiv
        """
        config = self.get_config(app, user_id)
        if not config:
            return ThrottleLevel.OFF, ThrottleReason.MANUAL

        now = current_time or datetime.now()
        hour = now.hour

        # 1. Sjekk manuell override
        if config.current_level != ThrottleLevel.OFF:
            return config.current_level, config.reason

        # 2. Sjekk leggetid
        if hour >= config.bedtime_hour:
            return ThrottleLevel.UNBEARABLE, ThrottleReason.BEDTIME

        # 3. Sjekk leksetid
        if config.homework_hours[0] <= hour < config.homework_hours[1]:
            return ThrottleLevel.ANNOYING, ThrottleReason.HOMEWORK_TIME

        # 4. Sjekk kvote
        if config.daily_quota_minutes > 0 and config.progressive_enabled:
            usage = self._get_today_usage(app, user_id)
            percent = (usage / config.daily_quota_minutes) * 100

            if percent >= 110:
                return ThrottleLevel.BLOCKED, ThrottleReason.QUOTA_EXCEEDED
            elif percent >= 100:
                return ThrottleLevel.UNBEARABLE, ThrottleReason.QUOTA_EXCEEDED
            elif percent >= 90:
                return ThrottleLevel.ANNOYING, ThrottleReason.QUOTA_EXCEEDED
            elif percent >= config.progressive_start_percent:
                return ThrottleLevel.GENTLE, ThrottleReason.QUOTA_EXCEEDED

        return ThrottleLevel.OFF, ThrottleReason.MANUAL

    def _get_today_usage(self, app: str, user_id: str) -> float:
        """Hent dagens bruk i minutter"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute(
                'SELECT minutes_used FROM app_usage WHERE user_id = ? AND app_name = ? AND date = ?',
                (user_id, app, today)
            )
            row = cursor.fetchone()
            conn.close()

            return row[0] if row else 0.0
        except Exception as e:
            logger.error(f"Error getting usage: {e}")
            return 0.0

    def process_request(
        self,
        host: str,
        user_id: str = 'default',
        client_ip: str = ''
    ) -> dict:
        """
        Prosesser en request og returner throttle-beslutning

        Returns:
            {
                'app': str,
                'level': ThrottleLevel,
                'reason': ThrottleReason,
                'delay_ms': int,
                'block': bool,
                'message': str
            }
        """
        app = self.identify_app(host)

        result = {
            'app': app,
            'level': ThrottleLevel.OFF,
            'reason': ThrottleReason.MANUAL,
            'delay_ms': 0,
            'block': False,
            'message': ''
        }

        if not app:
            return result

        # Oppdater session tracking
        self._track_session(app, user_id, client_ip)

        # Beregn throttle-nivå
        level, reason = self.calculate_throttle_level(app, user_id)
        result['level'] = level
        result['reason'] = reason

        # Bestem delay basert på nivå
        config = self.get_config(app, user_id)
        if config:
            if level == ThrottleLevel.GENTLE:
                result['delay_ms'] = random.randint(*config.delay_gentle)
            elif level == ThrottleLevel.ANNOYING:
                result['delay_ms'] = random.randint(*config.delay_annoying)
            elif level == ThrottleLevel.UNBEARABLE:
                result['delay_ms'] = random.randint(*config.delay_unbearable)
            elif level == ThrottleLevel.BLOCKED:
                result['block'] = True
                result['message'] = f'{config.app_name} er blokkert. Ta en pause!'

        # Oppdater statistikk
        if app in self.stats:
            self.stats[app].requests_total += 1
            if level != ThrottleLevel.OFF:
                self.stats[app].requests_throttled += 1
            if result['block']:
                self.stats[app].requests_blocked += 1
            self.stats[app].total_delay_added_ms += result['delay_ms']
            self.stats[app].last_request = datetime.now()

        # Logg event
        if level != ThrottleLevel.OFF:
            self._log_throttle_event(user_id, app, level, reason, result['delay_ms'])

        return result

    def _track_session(self, app: str, user_id: str, client_ip: str):
        """Track aktiv session for brukstid-beregning"""
        key = f"{client_ip}:{app}"
        now = time.time()

        if key not in self.active_sessions:
            self.active_sessions[key] = {
                'start': now,
                'last_seen': now,
                'user_id': user_id,
                'app': app
            }
        else:
            session = self.active_sessions[key]
            gap = now - session['last_seen']

            # Hvis mer enn 5 min siden sist, ny session
            if gap > 300:
                # Logg forrige session
                duration = (session['last_seen'] - session['start']) / 60
                self._record_usage(user_id, app, duration)

                # Start ny
                session['start'] = now

            session['last_seen'] = now

    def _record_usage(self, user_id: str, app: str, minutes: float):
        """Lagre brukstid til database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute('''
                INSERT INTO app_usage (user_id, app_name, date, minutes_used)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id, app_name, date)
                DO UPDATE SET minutes_used = minutes_used + ?
            ''', (user_id, app, today, minutes, minutes))

            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error recording usage: {e}")

    def _log_throttle_event(
        self,
        user_id: str,
        app: str,
        level: ThrottleLevel,
        reason: ThrottleReason,
        delay_ms: int
    ):
        """Logg throttle-event til database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO throttle_events (timestamp, user_id, app_name, level, reason, delay_ms)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                user_id,
                app,
                level.name,
                reason.name,
                delay_ms
            ))

            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error logging event: {e}")

    # === ADMIN METHODS ===

    def set_app_level(
        self,
        app: str,
        level: ThrottleLevel,
        reason: ThrottleReason = ThrottleReason.MANUAL,
        user_id: str = 'default'
    ):
        """Sett throttle-nivå for en app"""
        if app in self.configs:
            self.configs[app].current_level = level
            self.configs[app].reason = reason
            logger.info(f"Set {app} throttle level to {level.name} ({reason.name})")

    def set_quota(self, app: str, minutes: int, user_id: str = 'default'):
        """Sett daglig kvote for en app"""
        if app in self.configs:
            self.configs[app].daily_quota_minutes = minutes
            logger.info(f"Set {app} daily quota to {minutes} minutes")

    def set_homework_hours(
        self,
        start_hour: int,
        end_hour: int,
        apps: Optional[list[str]] = None
    ):
        """Sett leksetimer for apper"""
        target_apps = apps or list(self.configs.keys())
        for app in target_apps:
            if app in self.configs:
                self.configs[app].homework_hours = (start_hour, end_hour)
        logger.info(f"Set homework hours {start_hour}:00-{end_hour}:00 for {len(target_apps)} apps")

    def set_bedtime(self, hour: int, apps: Optional[list[str]] = None):
        """Sett leggetid for apper"""
        target_apps = apps or list(self.configs.keys())
        for app in target_apps:
            if app in self.configs:
                self.configs[app].bedtime_hour = hour
        logger.info(f"Set bedtime to {hour}:00 for {len(target_apps)} apps")

    def get_stats(self, app: Optional[str] = None) -> dict:
        """Hent statistikk"""
        if app:
            if app in self.stats:
                s = self.stats[app]
                return {
                    'app': app,
                    'requests_total': s.requests_total,
                    'requests_throttled': s.requests_throttled,
                    'requests_blocked': s.requests_blocked,
                    'total_delay_sec': s.total_delay_added_ms / 1000,
                    'throttle_rate': (s.requests_throttled / s.requests_total * 100) if s.requests_total else 0
                }
            return {}

        return {
            app: self.get_stats(app) for app in self.stats
        }

    def get_usage_report(self, user_id: str = 'default', days: int = 7) -> list[dict]:
        """Hent bruksrapport for bruker"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            cursor.execute('''
                SELECT date, app_name, minutes_used, requests_throttled, sessions_abandoned
                FROM app_usage
                WHERE user_id = ? AND date >= date('now', ?)
                ORDER BY date DESC, minutes_used DESC
            ''', (user_id, f'-{days} days'))

            rows = cursor.fetchall()
            conn.close()

            return [
                {
                    'date': row[0],
                    'app': row[1],
                    'minutes': row[2],
                    'throttled': row[3],
                    'abandoned': row[4]
                }
                for row in rows
            ]
        except Exception as e:
            logger.error(f"Error getting report: {e}")
            return []


# === FACTORY FUNCTION ===

def create_throttler(data_dir: str | Path = '/home/jovnna/aiki/data/proxy') -> AppThrottler:
    """Opprett AppThrottler instans"""
    return AppThrottler(data_dir)


# === TIKTOK SPECIFIC HELPERS ===

class TikTokThrottler:
    """
    Spesialisert TikTok-throttler med ekstra teknikker

    TikTok-spesifikke funksjoner:
    - Video buffer simulation
    - Feed refresh throttling
    - Like/comment delay
    """

    def __init__(self, base_throttler: AppThrottler):
        self.throttler = base_throttler

        # TikTok-spesifikke innstillinger
        self.video_endpoints = [
            '/api/recommend/item_list',
            '/api/feed/',
            '/aweme/v1/feed',
            '/video/play'
        ]
        self.interaction_endpoints = [
            '/like/', '/comment/', '/share/', '/follow/'
        ]

    def is_video_request(self, url: str) -> bool:
        """Sjekk om dette er video-request"""
        return any(ep in url for ep in self.video_endpoints)

    def is_interaction_request(self, url: str) -> bool:
        """Sjekk om dette er interaksjons-request"""
        return any(ep in url for ep in self.interaction_endpoints)

    def get_video_delay(self, level: ThrottleLevel) -> int:
        """Ekstra delay for video-requests (simulerer buffering)"""
        if level == ThrottleLevel.GENTLE:
            return random.randint(500, 1000)
        elif level == ThrottleLevel.ANNOYING:
            return random.randint(2000, 5000)
        elif level == ThrottleLevel.UNBEARABLE:
            return random.randint(8000, 15000)  # 8-15 sek buffer!
        return 0

    def process_tiktok_request(
        self,
        url: str,
        user_id: str = 'default',
        client_ip: str = ''
    ) -> dict:
        """Prosesser TikTok-request med ekstra logikk"""
        result = self.throttler.process_request('tiktok.com', user_id, client_ip)

        if result['app'] != 'tiktok':
            return result

        # Legg til ekstra delay for video
        if self.is_video_request(url):
            extra_delay = self.get_video_delay(result['level'])
            result['delay_ms'] += extra_delay
            result['video_buffer'] = True

        # Legg til delay for interaksjoner (frustrerende!)
        if self.is_interaction_request(url):
            if result['level'] != ThrottleLevel.OFF:
                result['delay_ms'] += random.randint(500, 2000)
                result['interaction_throttled'] = True

        return result


# Test
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    throttler = create_throttler('/tmp/throttle_test')

    # Test TikTok
    result = throttler.process_request('v16-webapp-prime.tiktok.com')
    print(f"TikTok: {result}")

    # Test Instagram
    result = throttler.process_request('www.instagram.com')
    print(f"Instagram: {result}")

    # Sett throttle-nivå
    throttler.set_app_level('tiktok', ThrottleLevel.ANNOYING)
    result = throttler.process_request('tiktok.com')
    print(f"TikTok (throttled): {result}")
