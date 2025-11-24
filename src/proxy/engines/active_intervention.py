"""
AIKI Traffic Intelligence Platform
===================================
Layer 4: Active Intervention System

DIN DRØM: Injiser educational content i TikTok-feed!

Intervensjonsmåter:
1. CONTENT INJECTION - Bytt ut video-feeds med educational content
2. DELAY INJECTION - Legg til kunstig forsinkelse for å redusere dopamin
3. BLOCK/REDIRECT - Blokker helt eller redirect til alternativ
4. OVERLAY INJECTION - Legg til overlay-meldinger i webinnhold
5. QUOTA ENFORCEMENT - Tidsbaserte grenser med progressiv degradering
6. GAMIFICATION - Belønn positiv atferd, "boss battles" for å låse opp

TikTok-injeksjon fungerer via:
- Intercept API-responser for video-feed
- Parse JSON og modifiser video-URLer
- Erstatt med pre-approved educational TikToks
- Eller host egne videoer som serveres via proxyen
"""

import gzip
import hashlib
import io
import json
import random
import re
import sqlite3
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from pathlib import Path
from typing import Any, Callable
from urllib.parse import parse_qs, urlparse


class InterventionType(Enum):
    """Type intervensjon"""
    CONTENT_INJECTION = auto()    # Bytt innhold
    DELAY_INJECTION = auto()      # Kunstig forsinkelse
    FULL_BLOCK = auto()           # Blokker helt
    REDIRECT = auto()             # Redirect til alternativ
    OVERLAY = auto()              # Vis melding over innhold
    QUOTA_WARNING = auto()        # Vis at kvote er i ferd med å brukes opp
    QUOTA_EXCEEDED = auto()       # Kvote brukt opp
    GAMIFICATION = auto()         # Boss battle / achievement


class InterventionTrigger(Enum):
    """Hva trigget intervensjonen"""
    DOPAMINE_LOOP = auto()
    TIME_LIMIT = auto()
    FOCUS_TIME = auto()
    BEDTIME = auto()
    WORK_HOURS = auto()
    MANUAL = auto()
    SCHEDULED = auto()
    BOSS_BATTLE = auto()


@dataclass
class EducationalContent:
    """Pre-approved educational content"""
    content_id: str
    title: str
    source: str  # tiktok, youtube, custom
    url: str
    duration: int  # sekunder
    category: str  # math, science, language, history, coding
    age_group: str  # kids, teens, adults
    tags: list[str] = field(default_factory=list)
    effectiveness_score: float = 0.5  # Learned over time


@dataclass
class InterventionResult:
    """Resultat av intervensjon"""
    intervention_type: InterventionType
    trigger: InterventionTrigger
    timestamp: float
    success: bool
    original_url: str
    modified_url: str | None = None
    injected_content: str | None = None
    delay_ms: int = 0
    user_response: str | None = None  # accepted, bypassed, ignored


@dataclass
class UserQuota:
    """Daglige kvoter per bruker"""
    user_id: str
    date: str  # YYYY-MM-DD

    # Tid brukt (sekunder)
    tiktok_used: int = 0
    tiktok_limit: int = 1800  # 30 min default

    instagram_used: int = 0
    instagram_limit: int = 1800

    youtube_shorts_used: int = 0
    youtube_shorts_limit: int = 1800

    gaming_used: int = 0
    gaming_limit: int = 3600  # 1 time

    # Earned bonus tid via achievements
    bonus_time: int = 0

    # Antall interventions i dag
    intervention_count: int = 0
    bypass_count: int = 0


@dataclass
class BossBattle:
    """Gamification: Boss battle for å låse opp tid"""
    battle_id: str
    user_id: str
    challenge_type: str  # math, trivia, physical, focus
    difficulty: int  # 1-5
    reward_minutes: int
    time_limit: int  # sekunder
    question: str
    correct_answer: str
    started_at: float | None = None
    completed: bool = False
    won: bool = False


class ContentLibrary:
    """
    Bibliotek over educational content som kan injiseres

    For TikTok-injeksjon trenger vi:
    - TikTok video IDs som er godkjent
    - Mapping til kategorier
    - Effektivitets-tracking
    """

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_db()
        self._load_default_content()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS educational_content (
                    content_id TEXT PRIMARY KEY,
                    title TEXT,
                    source TEXT,
                    url TEXT,
                    duration INTEGER,
                    category TEXT,
                    age_group TEXT,
                    tags TEXT,
                    effectiveness_score REAL DEFAULT 0.5,
                    times_shown INTEGER DEFAULT 0,
                    times_completed INTEGER DEFAULT 0,
                    created_at TEXT
                );

                CREATE TABLE IF NOT EXISTS content_responses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content_id TEXT,
                    user_id TEXT,
                    shown_at REAL,
                    watch_duration INTEGER,
                    skipped BOOLEAN,
                    liked BOOLEAN,
                    FOREIGN KEY (content_id) REFERENCES educational_content(content_id)
                );

                CREATE INDEX IF NOT EXISTS idx_content_category
                ON educational_content(category, age_group);
            """)

    def _load_default_content(self):
        """Populer med default educational TikToks"""
        default_content = [
            # Science
            EducationalContent(
                content_id="edu_sci_001",
                title="Why is the sky blue?",
                source="tiktok",
                url="https://www.tiktok.com/@scienceinseconds/video/example1",
                duration=45,
                category="science",
                age_group="kids",
                tags=["physics", "light", "sky"]
            ),
            EducationalContent(
                content_id="edu_sci_002",
                title="How do volcanoes work?",
                source="tiktok",
                url="https://www.tiktok.com/@natgeo/video/example2",
                duration=60,
                category="science",
                age_group="kids",
                tags=["geology", "volcanoes", "earth"]
            ),
            # Math
            EducationalContent(
                content_id="edu_math_001",
                title="Cool math trick: multiply by 11",
                source="tiktok",
                url="https://www.tiktok.com/@mathtricks/video/example3",
                duration=30,
                category="math",
                age_group="kids",
                tags=["multiplication", "tricks"]
            ),
            # History
            EducationalContent(
                content_id="edu_hist_001",
                title="Vikings in 60 seconds",
                source="tiktok",
                url="https://www.tiktok.com/@history/video/example4",
                duration=60,
                category="history",
                age_group="kids",
                tags=["vikings", "norway", "history"]
            ),
            # Coding
            EducationalContent(
                content_id="edu_code_001",
                title="What is an algorithm?",
                source="tiktok",
                url="https://www.tiktok.com/@codecademy/video/example5",
                duration=45,
                category="coding",
                age_group="kids",
                tags=["programming", "algorithms", "basics"]
            ),
            # Norwegian/Sami
            EducationalContent(
                content_id="edu_lang_001",
                title="Samisk: 5 ord du bør kunne",
                source="tiktok",
                url="https://www.tiktok.com/@samilearn/video/example6",
                duration=40,
                category="language",
                age_group="kids",
                tags=["sami", "language", "norwegian"]
            ),
        ]

        with sqlite3.connect(self.db_path) as conn:
            for content in default_content:
                conn.execute("""
                    INSERT OR IGNORE INTO educational_content
                    (content_id, title, source, url, duration, category, age_group, tags, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    content.content_id,
                    content.title,
                    content.source,
                    content.url,
                    content.duration,
                    content.category,
                    content.age_group,
                    json.dumps(content.tags),
                    datetime.now().isoformat()
                ))

    def get_content_for_injection(self, category: str | None = None,
                                   age_group: str = "kids",
                                   count: int = 1) -> list[EducationalContent]:
        """Hent content for injeksjon"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            if category:
                cursor = conn.execute("""
                    SELECT * FROM educational_content
                    WHERE category = ? AND age_group = ?
                    ORDER BY effectiveness_score DESC, RANDOM()
                    LIMIT ?
                """, (category, age_group, count))
            else:
                cursor = conn.execute("""
                    SELECT * FROM educational_content
                    WHERE age_group = ?
                    ORDER BY effectiveness_score DESC, RANDOM()
                    LIMIT ?
                """, (age_group, count))

            results = []
            for row in cursor.fetchall():
                results.append(EducationalContent(
                    content_id=row['content_id'],
                    title=row['title'],
                    source=row['source'],
                    url=row['url'],
                    duration=row['duration'],
                    category=row['category'],
                    age_group=row['age_group'],
                    tags=json.loads(row['tags']),
                    effectiveness_score=row['effectiveness_score']
                ))

            return results

    def record_response(self, content_id: str, user_id: str,
                       watch_duration: int, skipped: bool, liked: bool):
        """Registrer brukerrespons for å lære effektivitet"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO content_responses
                (content_id, user_id, shown_at, watch_duration, skipped, liked)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (content_id, user_id, time.time(), watch_duration, skipped, liked))

            # Oppdater effectiveness score
            if not skipped and liked:
                conn.execute("""
                    UPDATE educational_content
                    SET effectiveness_score = MIN(1.0, effectiveness_score + 0.05),
                        times_completed = times_completed + 1,
                        times_shown = times_shown + 1
                    WHERE content_id = ?
                """, (content_id,))
            elif skipped:
                conn.execute("""
                    UPDATE educational_content
                    SET effectiveness_score = MAX(0.0, effectiveness_score - 0.02),
                        times_shown = times_shown + 1
                    WHERE content_id = ?
                """, (content_id,))


class TikTokInjector:
    """
    HOVEDKLASSE: Injiser educational content i TikTok feeds

    TikTok API struktur (basert på reverse engineering):
    - Feed endpoint: /api/recommend/item_list/
    - Video data i JSON response med video URLs
    - Vi kan modifisere JSON før det sendes til appen

    Strategi:
    1. Intercept API response
    2. Parse JSON
    3. Erstatt N videoer med educational content
    4. Re-encode og send til klient
    """

    # TikTok API patterns
    FEED_PATTERNS = [
        r'/api/recommend/item_list',
        r'/api/feed/',
        r'/aweme/v1/feed',
        r'/api/post/item_list',
    ]

    def __init__(self, content_library: ContentLibrary):
        self.content_library = content_library
        self.injection_ratio = 0.3  # 30% av videoer byttes ut
        self.stats = {
            'requests_intercepted': 0,
            'videos_injected': 0,
            'injection_failures': 0
        }

    def should_intercept(self, url: str) -> bool:
        """Sjekk om denne URLen skal interceptes"""
        for pattern in self.FEED_PATTERNS:
            if re.search(pattern, url):
                return True
        return False

    def inject_into_feed(self, response_body: bytes,
                         age_group: str = "kids") -> tuple[bytes, int]:
        """
        Injiser educational content i TikTok feed response

        Args:
            response_body: Original response body (may be gzipped)
            age_group: Målgruppe for content

        Returns:
            (modified_body, num_injected)
        """
        self.stats['requests_intercepted'] += 1

        try:
            # Decompress if gzipped
            try:
                body_text = gzip.decompress(response_body).decode('utf-8')
                was_gzipped = True
            except:
                body_text = response_body.decode('utf-8')
                was_gzipped = False

            # Parse JSON
            data = json.loads(body_text)

            # Finn video-listen
            video_list = self._find_video_list(data)
            if not video_list:
                return response_body, 0

            # Beregn hvor mange å injisere
            num_to_inject = max(1, int(len(video_list) * self.injection_ratio))

            # Hent educational content
            edu_content = self.content_library.get_content_for_injection(
                age_group=age_group,
                count=num_to_inject
            )

            if not edu_content:
                return response_body, 0

            # Velg tilfeldige posisjoner for injeksjon
            positions = random.sample(range(len(video_list)), min(num_to_inject, len(video_list)))

            injected = 0
            for pos, content in zip(positions, edu_content):
                try:
                    video_list[pos] = self._create_edu_video_entry(content, video_list[pos])
                    injected += 1
                except Exception:
                    pass

            self.stats['videos_injected'] += injected

            # Re-encode
            modified_json = json.dumps(data, ensure_ascii=False)

            if was_gzipped:
                buf = io.BytesIO()
                with gzip.GzipFile(fileobj=buf, mode='wb') as f:
                    f.write(modified_json.encode('utf-8'))
                return buf.getvalue(), injected
            else:
                return modified_json.encode('utf-8'), injected

        except Exception as e:
            self.stats['injection_failures'] += 1
            return response_body, 0

    def _find_video_list(self, data: dict) -> list | None:
        """Finn video-listen i TikTok response"""
        # Mulige stier til video-data
        paths = [
            ['itemList'],
            ['aweme_list'],
            ['items'],
            ['data', 'itemList'],
            ['data', 'items'],
        ]

        for path in paths:
            current = data
            try:
                for key in path:
                    current = current[key]
                if isinstance(current, list):
                    return current
            except (KeyError, TypeError):
                continue

        return None

    def _create_edu_video_entry(self, content: EducationalContent,
                                 template: dict) -> dict:
        """
        Lag video entry som matcher TikTok-format

        Vi bruker template fra original video og bytter ut video-URL
        """
        # Deep copy template
        entry = json.loads(json.dumps(template))

        # Oppdater video info
        if 'video' in entry:
            # Marker som educational
            entry['video']['__aiki_educational'] = True
            entry['video']['__aiki_content_id'] = content.content_id

            # Prøv å sette video URL
            if 'playAddr' in entry['video']:
                entry['video']['playAddr'] = content.url
            if 'downloadAddr' in entry['video']:
                entry['video']['downloadAddr'] = content.url

        # Oppdater beskrivelse
        if 'desc' in entry:
            entry['desc'] = f"📚 {content.title}"
        if 'title' in entry:
            entry['title'] = f"📚 {content.title}"

        # Marker hele entry
        entry['__aiki_injected'] = True
        entry['__aiki_category'] = content.category

        return entry


class DelayInjector:
    """
    Kunstig forsinkelse for å redusere dopamin-rush

    Strategier:
    - Progressive delay: Øk forsinkelsen jo lengre bruker er i app
    - Random delay: Uforutsigbar for å bryte loop
    - Penalty delay: Ekstra forsinkelse for overtredelser
    """

    def __init__(self):
        self.base_delay_ms = 500  # Minimum delay
        self.max_delay_ms = 5000  # Maksimum delay
        self.session_start: float | None = None
        self.requests_in_session = 0

    def calculate_delay(self, app: str, session_duration: float,
                        is_dopamine_loop: bool) -> int:
        """
        Beregn forsinkelse basert på kontekst

        Returns: Forsinkelse i millisekunder
        """
        delay = self.base_delay_ms

        # Progressive delay basert på tid i sesjon
        if session_duration > 300:  # Over 5 min
            progress_factor = min(4, session_duration / 300)
            delay += int(self.base_delay_ms * progress_factor)

        # Ekstra delay for dopamin-loop
        if is_dopamine_loop:
            delay += 1500  # +1.5 sek

        # Random komponent (±20%)
        delay = int(delay * random.uniform(0.8, 1.2))

        return min(delay, self.max_delay_ms)


class QuotaManager:
    """
    Håndter daglige kvoter og progressiv degradering

    Progressiv degradering:
    1. 80% quota: Vis advarsel
    2. 90% quota: Legg til forsinkelser
    3. 100% quota: Injiser kun educational
    4. 110% quota: Økende blokkering
    """

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_quotas (
                    user_id TEXT,
                    date TEXT,
                    app TEXT,
                    seconds_used INTEGER DEFAULT 0,
                    seconds_limit INTEGER,
                    bonus_time INTEGER DEFAULT 0,
                    PRIMARY KEY (user_id, date, app)
                )
            """)

    def get_quota(self, user_id: str, app: str, date: str | None = None) -> dict:
        """Hent quota status for bruker/app"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT seconds_used, seconds_limit, bonus_time
                FROM user_quotas
                WHERE user_id = ? AND date = ? AND app = ?
            """, (user_id, date, app))

            row = cursor.fetchone()
            if row:
                used, limit, bonus = row
            else:
                # Default limits
                defaults = {
                    'tiktok': 1800,
                    'instagram': 1800,
                    'youtube_shorts': 1800,
                    'gaming': 3600
                }
                used = 0
                limit = defaults.get(app, 3600)
                bonus = 0

                # Opprett entry
                conn.execute("""
                    INSERT INTO user_quotas (user_id, date, app, seconds_used, seconds_limit, bonus_time)
                    VALUES (?, ?, ?, 0, ?, 0)
                """, (user_id, date, app, limit))

            total_limit = limit + bonus
            remaining = max(0, total_limit - used)
            percentage = (used / total_limit * 100) if total_limit > 0 else 100

            return {
                'used': used,
                'limit': limit,
                'bonus': bonus,
                'total_limit': total_limit,
                'remaining': remaining,
                'percentage': percentage,
                'status': self._get_quota_status(percentage)
            }

    def _get_quota_status(self, percentage: float) -> str:
        if percentage < 80:
            return 'ok'
        elif percentage < 90:
            return 'warning'
        elif percentage < 100:
            return 'degraded'
        elif percentage < 110:
            return 'exceeded'
        else:
            return 'blocked'

    def add_usage(self, user_id: str, app: str, seconds: int):
        """Legg til brukstid"""
        date = datetime.now().strftime('%Y-%m-%d')

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE user_quotas
                SET seconds_used = seconds_used + ?
                WHERE user_id = ? AND date = ? AND app = ?
            """, (seconds, user_id, date, app))

    def add_bonus_time(self, user_id: str, app: str, bonus_seconds: int):
        """Legg til bonus-tid (fra boss battles etc)"""
        date = datetime.now().strftime('%Y-%m-%d')

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE user_quotas
                SET bonus_time = bonus_time + ?
                WHERE user_id = ? AND date = ? AND app = ?
            """, (bonus_seconds, user_id, date, app))


class BossBattleGenerator:
    """
    Generer "boss battles" - utfordringer for å låse opp mer tid

    Utfordringstyper:
    - Math: Regneoppgaver
    - Trivia: Kunnskapsspørsmål
    - Physical: Bevegelsesutfordringer
    - Focus: Konsentrasjonsoppgaver
    """

    MATH_TEMPLATES = [
        ("Hva er {a} + {b}?", lambda a, b: str(a + b)),
        ("Hva er {a} × {b}?", lambda a, b: str(a * b)),
        ("Hva er {a} - {b}?", lambda a, b: str(a - b)),
        ("Hvis du har {a} epler og gir bort {b}, hvor mange har du igjen?",
         lambda a, b: str(max(0, a - b))),
    ]

    TRIVIA_QUESTIONS = [
        ("Hva er hovedstaden i Norge?", "Oslo"),
        ("Hvor mange planeter er det i solsystemet?", "8"),
        ("Hvilket element har symbol H?", "Hydrogen"),
        ("Hvem skrev 'Sofies verden'?", "Jostein Gaarder"),
        ("Hva kalles tradisjonelle samiske boliger?", "Lavvo"),
    ]

    PHYSICAL_CHALLENGES = [
        ("Gjør 10 knebøy og trykk 'Ferdig' når du er klar", "done"),
        ("Gå til vinduet og se ut i 30 sekunder", "done"),
        ("Drikk et glass vann", "done"),
        ("Strekk deg i 20 sekunder", "done"),
    ]

    def generate_battle(self, user_id: str, difficulty: int = 1,
                        preferred_type: str | None = None) -> BossBattle:
        """Generer ny boss battle"""
        import uuid

        battle_type = preferred_type or random.choice(['math', 'trivia', 'physical'])
        reward = difficulty * 5  # 5 min per difficulty level

        if battle_type == 'math':
            template, answer_fn = random.choice(self.MATH_TEMPLATES)
            # Generer tall basert på vanskelighetsgrad
            max_val = 10 * difficulty
            a = random.randint(1, max_val)
            b = random.randint(1, max_val)
            question = template.format(a=a, b=b)
            answer = answer_fn(a, b)

        elif battle_type == 'trivia':
            question, answer = random.choice(self.TRIVIA_QUESTIONS)

        else:  # physical
            question, answer = random.choice(self.PHYSICAL_CHALLENGES)

        return BossBattle(
            battle_id=str(uuid.uuid4()),
            user_id=user_id,
            challenge_type=battle_type,
            difficulty=difficulty,
            reward_minutes=reward,
            time_limit=60 * difficulty,  # 1 min per difficulty
            question=question,
            correct_answer=answer
        )

    def check_answer(self, battle: BossBattle, user_answer: str) -> bool:
        """Sjekk svar"""
        if battle.challenge_type == 'physical':
            return user_answer.lower() in ['done', 'ferdig', 'ja', 'yes']

        # Fuzzy matching for tekst-svar
        correct = battle.correct_answer.lower().strip()
        given = user_answer.lower().strip()

        return correct == given or correct in given


class ActiveInterventionEngine:
    """
    HOVED-ENGINE for aktiv intervensjon

    Koordinerer:
    - TikTok content injection
    - Delay injection
    - Quota management
    - Boss battles
    - Response logging
    """

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Sub-systemer
        self.content_library = ContentLibrary(data_dir / "content.db")
        self.tiktok_injector = TikTokInjector(self.content_library)
        self.delay_injector = DelayInjector()
        self.quota_manager = QuotaManager(data_dir / "quotas.db")
        self.boss_generator = BossBattleGenerator()

        # Active battles
        self.active_battles: dict[str, BossBattle] = {}

        # Intervention log
        self._init_log_db()

    def _init_log_db(self):
        db_path = self.data_dir / "interventions.db"
        with sqlite3.connect(db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS interventions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    user_id TEXT,
                    intervention_type TEXT,
                    trigger TEXT,
                    app TEXT,
                    success BOOLEAN,
                    user_response TEXT,
                    data JSON
                );

                CREATE INDEX IF NOT EXISTS idx_interventions_user_time
                ON interventions(user_id, timestamp);
            """)

    def process_request(self, user_id: str, app: str, url: str,
                        session_duration: float,
                        is_dopamine_loop: bool) -> dict:
        """
        Prosesser request og bestem intervensjon

        Returns dict med:
        - action: 'allow', 'delay', 'inject', 'block', 'boss_battle'
        - delay_ms: Eventuell forsinkelse
        - inject_content: Content for injeksjon
        - message: Eventuell melding til bruker
        """
        result = {
            'action': 'allow',
            'delay_ms': 0,
            'inject_content': False,
            'message': None,
            'boss_battle': None
        }

        # Sjekk quota
        quota = self.quota_manager.get_quota(user_id, app)

        if quota['status'] == 'blocked':
            result['action'] = 'block'
            result['message'] = f"Du har brukt opp tiden din på {app} i dag. Prøv en boss battle for å låse opp mer tid!"
            result['boss_battle'] = self.boss_generator.generate_battle(user_id, difficulty=2)
            return result

        if quota['status'] == 'exceeded':
            # 100-110%: Kun educational content
            result['action'] = 'inject'
            result['inject_content'] = True
            result['message'] = f"Kvoten er overskredet. Nå vises kun lærerikt innhold."
            return result

        if quota['status'] == 'degraded':
            # 90-100%: Forsinkelser + noe injeksjon
            result['delay_ms'] = self.delay_injector.calculate_delay(
                app, session_duration, is_dopamine_loop
            )
            if random.random() < 0.5:  # 50% sjanse for injeksjon
                result['inject_content'] = True
            result['message'] = f"Du har {quota['remaining'] // 60} minutter igjen på {app}"

        if quota['status'] == 'warning':
            # 80-90%: Advarsel
            result['message'] = f"Husk: Du har {quota['remaining'] // 60} minutter igjen"

        # Dopamin-loop = alltid forsinkelse
        if is_dopamine_loop:
            result['delay_ms'] = max(
                result['delay_ms'],
                self.delay_injector.calculate_delay(app, session_duration, True)
            )
            if session_duration > 600:  # Over 10 min i loop
                result['inject_content'] = True
                result['message'] = "La oss ta en pause fra dopamin-loopen!"

        return result

    def process_response(self, response_body: bytes, app: str,
                         inject_content: bool, age_group: str = "kids") -> tuple[bytes, dict]:
        """
        Prosesser response og injiser content hvis nødvendig

        Returns: (modified_body, stats)
        """
        stats = {
            'injected': 0,
            'modified': False
        }

        if not inject_content:
            return response_body, stats

        if app == 'tiktok':
            modified_body, num_injected = self.tiktok_injector.inject_into_feed(
                response_body, age_group
            )
            stats['injected'] = num_injected
            stats['modified'] = num_injected > 0
            return modified_body, stats

        return response_body, stats

    def start_boss_battle(self, user_id: str, difficulty: int = 1) -> BossBattle:
        """Start boss battle for bruker"""
        battle = self.boss_generator.generate_battle(user_id, difficulty)
        battle.started_at = time.time()
        self.active_battles[battle.battle_id] = battle
        return battle

    def submit_boss_battle(self, battle_id: str, answer: str) -> dict:
        """Submit svar på boss battle"""
        battle = self.active_battles.get(battle_id)
        if not battle:
            return {'success': False, 'error': 'Battle not found'}

        if battle.completed:
            return {'success': False, 'error': 'Battle already completed'}

        # Sjekk tidsfrist
        elapsed = time.time() - (battle.started_at or 0)
        if elapsed > battle.time_limit:
            battle.completed = True
            battle.won = False
            return {
                'success': False,
                'error': 'Time expired',
                'won': False
            }

        # Sjekk svar
        correct = self.boss_generator.check_answer(battle, answer)
        battle.completed = True
        battle.won = correct

        if correct:
            # Legg til bonus-tid
            bonus_seconds = battle.reward_minutes * 60
            self.quota_manager.add_bonus_time(battle.user_id, 'tiktok', bonus_seconds)
            self.quota_manager.add_bonus_time(battle.user_id, 'instagram', bonus_seconds)

            return {
                'success': True,
                'won': True,
                'reward_minutes': battle.reward_minutes,
                'message': f"🎉 Du vant {battle.reward_minutes} ekstra minutter!"
            }
        else:
            return {
                'success': True,
                'won': False,
                'correct_answer': battle.correct_answer,
                'message': "Beklager, feil svar. Prøv igjen senere!"
            }

    def log_intervention(self, user_id: str, intervention_type: InterventionType,
                         trigger: InterventionTrigger, app: str, success: bool,
                         user_response: str | None = None, data: dict | None = None):
        """Logg intervensjon"""
        db_path = self.data_dir / "interventions.db"
        with sqlite3.connect(db_path) as conn:
            conn.execute("""
                INSERT INTO interventions
                (timestamp, user_id, intervention_type, trigger, app, success, user_response, data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                time.time(),
                user_id,
                intervention_type.name,
                trigger.name,
                app,
                success,
                user_response,
                json.dumps(data or {})
            ))

    def get_stats(self) -> dict:
        """Hent statistikk"""
        return {
            'tiktok_injector': self.tiktok_injector.stats,
            'active_battles': len(self.active_battles)
        }


# Factory function
def create_intervention_engine(data_dir: str = "/home/jovnna/aiki/data/proxy") -> ActiveInterventionEngine:
    """Opprett active intervention engine"""
    return ActiveInterventionEngine(Path(data_dir))


# mitmproxy integration helper
def get_intervention_for_flow(engine: ActiveInterventionEngine,
                               flow: Any,  # mitmproxy flow
                               user_id: str = "default",
                               session_duration: float = 0,
                               is_dopamine_loop: bool = False) -> dict:
    """
    Helper for mitmproxy integration

    Brukes i aiki_addon.py for å bestemme hva som skal gjøres med en request
    """
    url = flow.request.pretty_url
    host = flow.request.host

    # Identifiser app
    app = 'unknown'
    if 'tiktok' in host:
        app = 'tiktok'
    elif 'instagram' in host:
        app = 'instagram'
    elif 'youtube' in host:
        app = 'youtube_shorts'

    return engine.process_request(
        user_id=user_id,
        app=app,
        url=url,
        session_duration=session_duration,
        is_dopamine_loop=is_dopamine_loop
    )
