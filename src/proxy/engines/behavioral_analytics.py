"""
AIKI Traffic Intelligence Platform
===================================
Layer 3: Behavioral Analytics Engine

Avansert brukeratferdsanalyse for ADHD accountability:
- Dopamine loop detection (infinite scroll patterns)
- Addiction scoring (personlig + per-app)
- Session tracking med focus/distraction metrics
- Circadian rhythm analysis
- Productivity correlation
- Intervention effectiveness tracking

Bruker:
- Time-series analysis
- Anomaly detection
- Reinforcement learning for adaptive thresholds
"""

import json
import math
import sqlite3
import statistics
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from pathlib import Path
from typing import Any, Callable

import numpy as np


class BehaviorState(Enum):
    """Brukerens nåværende atferdstilstand"""
    FOCUSED = auto()           # Produktiv, på oppgave
    DISTRACTED = auto()        # Avbrutt, multi-tasking
    DOPAMINE_SEEKING = auto()  # Aktivt søker stimuli
    BINGE = auto()             # Langvarig konsum av en kilde
    IDLE = auto()              # Ingen aktivitet
    PRODUCTIVE_BREAK = auto()  # Planlagt pause


class AlertLevel(Enum):
    """Varselsnivå for intervensjon"""
    NONE = 0
    INFO = 1
    GENTLE = 2
    MODERATE = 3
    URGENT = 4
    CRITICAL = 5


@dataclass
class SessionMetrics:
    """Metrics for en bruker-session"""
    session_id: str
    user_id: str
    start_time: float
    end_time: float | None = None

    # App usage
    app_switches: int = 0
    unique_apps: set = field(default_factory=set)
    dominant_app: str = ""
    dominant_app_time: float = 0.0

    # Attention metrics
    avg_time_per_app: float = 0.0
    focus_score: float = 0.0  # 0-100
    distraction_count: int = 0

    # Dopamine metrics
    scroll_events: int = 0
    video_starts: int = 0
    short_video_count: int = 0
    dopamine_score: float = 0.0  # 0-100 (høyere = mer dopamin-seeking)

    # Time of day
    is_work_hours: bool = False
    is_focus_time: bool = False

    # Addiction indicators
    addiction_score: float = 0.0


@dataclass
class UserProfile:
    """Brukerprofil med historiske data"""
    user_id: str
    created_at: float = field(default_factory=time.time)

    # Baseline metrics (learned over time)
    baseline_focus_score: float = 50.0
    baseline_session_length: float = 1800.0  # 30 min
    baseline_app_switches_per_hour: float = 10.0

    # Addiction scores per app category
    addiction_scores: dict[str, float] = field(default_factory=dict)

    # Time patterns
    most_productive_hours: list[int] = field(default_factory=list)
    most_distracted_hours: list[int] = field(default_factory=list)

    # Intervention effectiveness
    intervention_responses: dict[str, float] = field(default_factory=dict)

    # ADHD-specific
    hyperfocus_apps: list[str] = field(default_factory=list)
    adhd_trigger_apps: list[str] = field(default_factory=list)

    # Goals
    daily_limits: dict[str, int] = field(default_factory=dict)  # app -> minutes
    focus_goals: list[dict] = field(default_factory=list)


@dataclass
class DopamineEvent:
    """Ett dopamin-utløsende event"""
    timestamp: float
    app_name: str
    event_type: str  # scroll, video_start, notification, like, etc.
    intensity: float  # 0.0 - 1.0
    duration: float = 0.0


@dataclass
class BehaviorAlert:
    """Varsel om atferdsendring"""
    timestamp: float
    alert_level: AlertLevel
    alert_type: str
    message: str
    suggested_action: str
    data: dict = field(default_factory=dict)


class TimeSeriesBuffer:
    """Ringbuffer for time-series data"""

    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.data: list[tuple[float, float]] = []  # (timestamp, value)

    def add(self, value: float, timestamp: float | None = None):
        if timestamp is None:
            timestamp = time.time()
        self.data.append((timestamp, value))
        if len(self.data) > self.max_size:
            self.data.pop(0)

    def get_window(self, duration_seconds: float) -> list[tuple[float, float]]:
        """Hent data fra siste N sekunder"""
        cutoff = time.time() - duration_seconds
        return [(t, v) for t, v in self.data if t >= cutoff]

    def get_values(self, duration_seconds: float) -> list[float]:
        """Hent bare verdier fra siste N sekunder"""
        return [v for _, v in self.get_window(duration_seconds)]

    def mean(self, duration_seconds: float) -> float:
        values = self.get_values(duration_seconds)
        return statistics.mean(values) if values else 0.0

    def std(self, duration_seconds: float) -> float:
        values = self.get_values(duration_seconds)
        return statistics.stdev(values) if len(values) > 1 else 0.0


class DopamineLoopDetector:
    """
    Detekter dopamin-loops (infinite scroll, rapid content consumption)

    Patterns vi ser etter:
    - Rapid content switches (< 5 sek per innhold)
    - Increasing engagement over tid
    - Manglende naturlige stopp-punkter
    - Eskalerende stimuli-søking
    """

    # Thresholds
    SCROLL_INTERVAL_THRESHOLD = 3.0  # sekunder mellom scrolls
    MIN_LOOP_EVENTS = 5  # minimum events for loop detection
    LOOP_WINDOW = 60.0  # sekunder å analysere

    def __init__(self):
        self.recent_events: list[DopamineEvent] = []
        self.loop_active = False
        self.loop_start_time: float | None = None
        self.loop_intensity = 0.0

    def add_event(self, event: DopamineEvent):
        """Legg til nytt dopamin-event"""
        self.recent_events.append(event)

        # Fjern gamle events
        cutoff = time.time() - self.LOOP_WINDOW * 2
        self.recent_events = [e for e in self.recent_events if e.timestamp > cutoff]

    def detect_loop(self) -> tuple[bool, float, str]:
        """
        Detekter om bruker er i en dopamin-loop

        Returns: (is_looping, intensity, loop_type)
        """
        now = time.time()
        recent = [e for e in self.recent_events
                  if e.timestamp > now - self.LOOP_WINDOW]

        if len(recent) < self.MIN_LOOP_EVENTS:
            self.loop_active = False
            return False, 0.0, ""

        # Analyser intervaller
        intervals = []
        for i in range(1, len(recent)):
            intervals.append(recent[i].timestamp - recent[i-1].timestamp)

        if not intervals:
            return False, 0.0, ""

        avg_interval = statistics.mean(intervals)

        # Rapid scrolling detection
        if avg_interval < self.SCROLL_INTERVAL_THRESHOLD:
            self.loop_active = True
            if self.loop_start_time is None:
                self.loop_start_time = recent[0].timestamp

            # Beregn intensitet basert på:
            # - Hvor raskt scrollingen er
            # - Hvor lenge det har vart
            # - Antall events
            speed_factor = max(0, 1 - (avg_interval / self.SCROLL_INTERVAL_THRESHOLD))
            duration_factor = min(1, (now - self.loop_start_time) / 300)  # Max ved 5 min
            event_factor = min(1, len(recent) / 20)

            self.loop_intensity = (speed_factor * 0.4 +
                                   duration_factor * 0.4 +
                                   event_factor * 0.2)

            # Kategoriser loop-type
            event_types = [e.event_type for e in recent]
            if event_types.count('scroll') > len(event_types) * 0.7:
                loop_type = "infinite_scroll"
            elif event_types.count('video_start') > len(event_types) * 0.5:
                loop_type = "video_binge"
            else:
                loop_type = "rapid_consumption"

            return True, self.loop_intensity, loop_type

        self.loop_active = False
        self.loop_start_time = None
        return False, 0.0, ""


class FocusTracker:
    """
    Tracker brukerens fokus over tid

    Metrics:
    - App switching frequency
    - Time on task
    - Distraction sources
    - Focus streaks
    """

    def __init__(self):
        self.current_app: str | None = None
        self.app_start_time: float | None = None
        self.app_durations: dict[str, float] = defaultdict(float)
        self.switch_times: list[float] = []
        self.focus_streak = 0.0
        self.last_focus_check = time.time()

    def switch_app(self, new_app: str) -> dict:
        """Registrer app-bytte"""
        now = time.time()
        result = {
            'previous_app': self.current_app,
            'time_on_previous': 0.0,
            'was_distraction': False
        }

        if self.current_app and self.app_start_time:
            duration = now - self.app_start_time
            self.app_durations[self.current_app] += duration
            result['time_on_previous'] = duration

            # Kort tid på forrige app = distraction
            if duration < 30:  # Under 30 sek
                result['was_distraction'] = True

        self.switch_times.append(now)
        self.current_app = new_app
        self.app_start_time = now

        return result

    def calculate_focus_score(self, window_minutes: int = 30) -> float:
        """
        Beregn fokus-score basert på:
        - App-bytter (færre = bedre)
        - Tid på produktive apper
        - Avbrudd-mønster
        """
        now = time.time()
        window_start = now - (window_minutes * 60)

        # Tell bytter i vinduet
        recent_switches = [t for t in self.switch_times if t > window_start]
        switches_per_hour = len(recent_switches) / (window_minutes / 60)

        # Optimal: 5-10 switches per time
        # Dårlig: 30+ switches per time
        switch_score = max(0, 100 - (switches_per_hour - 5) * 3)

        # TODO: Legg til produktivitets-vekting basert på app-kategori
        return min(100, max(0, switch_score))


class AddictionScorer:
    """
    Beregner avhengighets-score per bruker og per app

    Faktorer:
    - Frekvens av bruk
    - Tid brukt
    - Time-of-day patterns
    - Dopamine loop frequency
    - Response to intervention
    """

    # Vekter for ulike faktorer
    WEIGHTS = {
        'frequency': 0.2,
        'duration': 0.3,
        'time_of_day': 0.15,
        'dopamine_loops': 0.25,
        'intervention_resistance': 0.1
    }

    def __init__(self):
        self.usage_history: dict[str, list[tuple[float, float]]] = defaultdict(list)
        self.intervention_history: list[tuple[float, str, bool]] = []  # (time, type, accepted)

    def record_usage(self, app: str, start_time: float, duration: float):
        """Registrer app-bruk"""
        self.usage_history[app].append((start_time, duration))

        # Trim gammel historie
        cutoff = time.time() - 86400 * 30  # 30 dager
        for app_name in self.usage_history:
            self.usage_history[app_name] = [
                (t, d) for t, d in self.usage_history[app_name] if t > cutoff
            ]

    def record_intervention(self, intervention_type: str, accepted: bool):
        """Registrer respons på intervensjon"""
        self.intervention_history.append((time.time(), intervention_type, accepted))

    def calculate_score(self, app: str | None = None, days: int = 7) -> float:
        """
        Beregn addiction score (0-100)

        Høyere = mer avhengig/problematisk bruk
        """
        cutoff = time.time() - (days * 86400)

        if app:
            history = [(t, d) for t, d in self.usage_history.get(app, []) if t > cutoff]
        else:
            history = []
            for app_history in self.usage_history.values():
                history.extend([(t, d) for t, d in app_history if t > cutoff])

        if not history:
            return 0.0

        # Frekvens-score
        daily_sessions = len(history) / days
        freq_score = min(100, daily_sessions * 5)  # 20 sessions/dag = 100

        # Varighet-score
        total_duration = sum(d for _, d in history)
        daily_duration = total_duration / days
        duration_score = min(100, (daily_duration / 3600) * 25)  # 4 timer/dag = 100

        # Tid-på-dagen score (natt-bruk er mer problematisk)
        night_sessions = sum(1 for t, _ in history
                           if 0 <= datetime.fromtimestamp(t).hour < 6)
        time_score = min(100, (night_sessions / max(1, len(history))) * 200)

        # Intervention resistance
        recent_interventions = [
            accepted for t, _, accepted in self.intervention_history
            if t > cutoff
        ]
        if recent_interventions:
            resistance_score = (1 - sum(recent_interventions) / len(recent_interventions)) * 100
        else:
            resistance_score = 50  # Nøytral uten data

        # Kombinert score
        total = (
            freq_score * self.WEIGHTS['frequency'] +
            duration_score * self.WEIGHTS['duration'] +
            time_score * self.WEIGHTS['time_of_day'] +
            resistance_score * self.WEIGHTS['intervention_resistance']
        )

        return min(100, max(0, total))


class CircadianAnalyzer:
    """
    Analyserer døgnrytme og korrelerer med produktivitet

    Features:
    - Identifiser produktive timer
    - Detekter unormale mønstre
    - Suggest optimal focus times
    """

    def __init__(self):
        # Hourly buckets for 24 timer
        self.hourly_productivity: list[TimeSeriesBuffer] = [
            TimeSeriesBuffer(max_size=100) for _ in range(24)
        ]
        self.hourly_distraction: list[TimeSeriesBuffer] = [
            TimeSeriesBuffer(max_size=100) for _ in range(24)
        ]

    def record_hour(self, hour: int, productivity_score: float, distraction_score: float):
        """Registrer data for en time"""
        self.hourly_productivity[hour].add(productivity_score)
        self.hourly_distraction[hour].add(distraction_score)

    def get_best_focus_hours(self, count: int = 3) -> list[int]:
        """Finn de beste timene for fokus"""
        scores = []
        for hour in range(24):
            prod_mean = self.hourly_productivity[hour].mean(86400 * 30)  # 30 dager
            dist_mean = self.hourly_distraction[hour].mean(86400 * 30)
            score = prod_mean - dist_mean
            scores.append((hour, score))

        scores.sort(key=lambda x: x[1], reverse=True)
        return [h for h, _ in scores[:count]]

    def get_risky_hours(self, count: int = 3) -> list[int]:
        """Finn timer med høy distraksjonsrisiko"""
        scores = []
        for hour in range(24):
            dist_mean = self.hourly_distraction[hour].mean(86400 * 30)
            scores.append((hour, dist_mean))

        scores.sort(key=lambda x: x[1], reverse=True)
        return [h for h, _ in scores[:count]]

    def is_abnormal_pattern(self) -> tuple[bool, str]:
        """Sjekk for unormale døgnrytme-mønstre"""
        now = datetime.now()
        current_hour = now.hour

        # Sjekk for aktivitet på unormale tider
        if 2 <= current_hour < 5:
            recent_activity = self.hourly_distraction[current_hour].get_values(3600)
            if len(recent_activity) > 3:
                return True, "late_night_activity"

        return False, ""


class BehavioralAnalyticsEngine:
    """
    Hoved-engine for atferdsanalyse

    Koordinerer alle sub-systemer og gir helhetlig innsikt
    """

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Sub-systemer
        self.dopamine_detector = DopamineLoopDetector()
        self.focus_tracker = FocusTracker()
        self.addiction_scorer = AddictionScorer()
        self.circadian_analyzer = CircadianAnalyzer()

        # User profiles
        self.profiles: dict[str, UserProfile] = {}

        # Current sessions
        self.active_sessions: dict[str, SessionMetrics] = {}

        # Alert callbacks
        self.alert_callbacks: list[Callable[[BehaviorAlert], None]] = []

        # Time-series buffers
        self.focus_buffer = TimeSeriesBuffer(max_size=1000)
        self.dopamine_buffer = TimeSeriesBuffer(max_size=1000)

        # Database
        self._init_db()

    def _init_db(self):
        """Initialiser SQLite for persistent lagring"""
        db_path = self.data_dir / "behavioral.db"
        with sqlite3.connect(db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    start_time REAL,
                    end_time REAL,
                    focus_score REAL,
                    dopamine_score REAL,
                    addiction_score REAL,
                    app_switches INTEGER,
                    dominant_app TEXT,
                    data JSON
                );

                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    user_id TEXT,
                    alert_level INTEGER,
                    alert_type TEXT,
                    message TEXT,
                    data JSON
                );

                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id TEXT PRIMARY KEY,
                    profile_data JSON,
                    updated_at REAL
                );

                CREATE INDEX IF NOT EXISTS idx_sessions_user
                ON sessions(user_id);

                CREATE INDEX IF NOT EXISTS idx_alerts_user_time
                ON alerts(user_id, timestamp);
            """)

    def get_or_create_profile(self, user_id: str) -> UserProfile:
        """Hent eller opprett brukerprofil"""
        if user_id not in self.profiles:
            self.profiles[user_id] = UserProfile(user_id=user_id)
        return self.profiles[user_id]

    def start_session(self, user_id: str) -> str:
        """Start ny session for bruker"""
        import uuid
        session_id = str(uuid.uuid4())

        now = time.time()
        current_hour = datetime.now().hour

        session = SessionMetrics(
            session_id=session_id,
            user_id=user_id,
            start_time=now,
            is_work_hours=9 <= current_hour <= 17,
            is_focus_time=current_hour in self.circadian_analyzer.get_best_focus_hours()
        )

        self.active_sessions[session_id] = session
        return session_id

    def end_session(self, session_id: str) -> SessionMetrics | None:
        """Avslutt session og beregn endelige metrics"""
        if session_id not in self.active_sessions:
            return None

        session = self.active_sessions.pop(session_id)
        session.end_time = time.time()

        # Beregn endelige scores
        session.focus_score = self.focus_tracker.calculate_focus_score()
        session.addiction_score = self.addiction_scorer.calculate_score()

        # Lagre til database
        self._save_session(session)

        return session

    def _save_session(self, session: SessionMetrics):
        """Lagre session til database"""
        db_path = self.data_dir / "behavioral.db"
        with sqlite3.connect(db_path) as conn:
            conn.execute("""
                INSERT INTO sessions
                (id, user_id, start_time, end_time, focus_score, dopamine_score,
                 addiction_score, app_switches, dominant_app, data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session.session_id,
                session.user_id,
                session.start_time,
                session.end_time,
                session.focus_score,
                session.dopamine_score,
                session.addiction_score,
                session.app_switches,
                session.dominant_app,
                json.dumps({
                    'unique_apps': list(session.unique_apps),
                    'scroll_events': session.scroll_events,
                    'video_starts': session.video_starts,
                })
            ))

    def process_event(self, session_id: str, event_type: str,
                      app_name: str, metadata: dict | None = None) -> list[BehaviorAlert]:
        """
        Prosesser ett event og returner eventuelle alerts

        Event types:
        - app_switch: Byttet til annen app
        - scroll: Scroll event
        - video_start: Video begynt å spille
        - notification: Mottatt notifikasjon
        - interaction: Generell interaksjon
        """
        alerts: list[BehaviorAlert] = []
        now = time.time()
        metadata = metadata or {}

        session = self.active_sessions.get(session_id)
        if not session:
            return alerts

        # Oppdater session metrics
        if event_type == 'app_switch':
            session.app_switches += 1
            session.unique_apps.add(app_name)
            switch_result = self.focus_tracker.switch_app(app_name)

            if switch_result['was_distraction']:
                session.distraction_count += 1

        elif event_type == 'scroll':
            session.scroll_events += 1
            self.dopamine_detector.add_event(DopamineEvent(
                timestamp=now,
                app_name=app_name,
                event_type='scroll',
                intensity=0.5
            ))

        elif event_type == 'video_start':
            session.video_starts += 1
            duration = metadata.get('duration', 0)
            if duration < 60:  # Kort video
                session.short_video_count += 1
                intensity = 0.8
            else:
                intensity = 0.4

            self.dopamine_detector.add_event(DopamineEvent(
                timestamp=now,
                app_name=app_name,
                event_type='video_start',
                intensity=intensity,
                duration=duration
            ))

        # Sjekk for dopamin-loop
        is_looping, loop_intensity, loop_type = self.dopamine_detector.detect_loop()

        if is_looping:
            session.dopamine_score = loop_intensity * 100

            if loop_intensity > 0.7:
                alert = BehaviorAlert(
                    timestamp=now,
                    alert_level=AlertLevel.URGENT,
                    alert_type='dopamine_loop',
                    message=f"Du har vært i en {loop_type} i over 5 minutter",
                    suggested_action="Ta en 5-minutters pause",
                    data={'intensity': loop_intensity, 'loop_type': loop_type}
                )
                alerts.append(alert)
                self._trigger_alert(alert)

            elif loop_intensity > 0.4:
                alert = BehaviorAlert(
                    timestamp=now,
                    alert_level=AlertLevel.GENTLE,
                    alert_type='dopamine_loop',
                    message="Ser ut som du scroller mye",
                    suggested_action="Bevisst valg?",
                    data={'intensity': loop_intensity}
                )
                alerts.append(alert)
                self._trigger_alert(alert)

        # Oppdater time-series
        focus_score = self.focus_tracker.calculate_focus_score()
        self.focus_buffer.add(focus_score)
        self.dopamine_buffer.add(session.dopamine_score)

        # Circadian logging
        current_hour = datetime.now().hour
        self.circadian_analyzer.record_hour(
            current_hour,
            focus_score,
            session.dopamine_score
        )

        return alerts

    def _trigger_alert(self, alert: BehaviorAlert):
        """Trigger callbacks for alert"""
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception:
                pass

        # Lagre til database
        db_path = self.data_dir / "behavioral.db"
        with sqlite3.connect(db_path) as conn:
            conn.execute("""
                INSERT INTO alerts (timestamp, user_id, alert_level, alert_type, message, data)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                alert.timestamp,
                "",  # TODO: Add user_id
                alert.alert_level.value,
                alert.alert_type,
                alert.message,
                json.dumps(alert.data)
            ))

    def register_alert_callback(self, callback: Callable[[BehaviorAlert], None]):
        """Registrer callback for alerts"""
        self.alert_callbacks.append(callback)

    def get_current_state(self, session_id: str) -> dict:
        """Hent nåværende tilstand for session"""
        session = self.active_sessions.get(session_id)
        if not session:
            return {}

        is_looping, loop_intensity, loop_type = self.dopamine_detector.detect_loop()

        # Bestem behavior state
        if is_looping and loop_intensity > 0.5:
            state = BehaviorState.DOPAMINE_SEEKING
        elif session.focus_score > 70:
            state = BehaviorState.FOCUSED
        elif session.distraction_count > 5:
            state = BehaviorState.DISTRACTED
        else:
            state = BehaviorState.IDLE

        return {
            'state': state.name,
            'focus_score': session.focus_score,
            'dopamine_score': session.dopamine_score,
            'addiction_score': session.addiction_score,
            'is_looping': is_looping,
            'loop_type': loop_type,
            'loop_intensity': loop_intensity,
            'app_switches': session.app_switches,
            'distraction_count': session.distraction_count,
            'session_duration': time.time() - session.start_time,
            'is_work_hours': session.is_work_hours,
            'is_focus_time': session.is_focus_time
        }

    def get_daily_summary(self, user_id: str, date: datetime | None = None) -> dict:
        """Hent daglig sammendrag for bruker"""
        if date is None:
            date = datetime.now()

        day_start = datetime(date.year, date.month, date.day).timestamp()
        day_end = day_start + 86400

        db_path = self.data_dir / "behavioral.db"
        with sqlite3.connect(db_path) as conn:
            # Hent sessions for dagen
            cursor = conn.execute("""
                SELECT focus_score, dopamine_score, addiction_score,
                       app_switches, dominant_app,
                       end_time - start_time as duration
                FROM sessions
                WHERE user_id = ? AND start_time >= ? AND start_time < ?
            """, (user_id, day_start, day_end))

            sessions = cursor.fetchall()

            if not sessions:
                return {'has_data': False}

            # Aggreger
            total_duration = sum(s[5] or 0 for s in sessions)
            avg_focus = statistics.mean(s[0] for s in sessions if s[0])
            avg_dopamine = statistics.mean(s[1] for s in sessions if s[1])
            total_switches = sum(s[3] for s in sessions)

            # Finn mest brukte app
            app_counts = defaultdict(int)
            for s in sessions:
                if s[4]:
                    app_counts[s[4]] += 1
            dominant_app = max(app_counts.keys(), key=lambda x: app_counts[x]) if app_counts else None

            return {
                'has_data': True,
                'date': date.strftime('%Y-%m-%d'),
                'total_sessions': len(sessions),
                'total_duration_hours': total_duration / 3600,
                'avg_focus_score': avg_focus,
                'avg_dopamine_score': avg_dopamine,
                'total_app_switches': total_switches,
                'dominant_app': dominant_app,
                'best_focus_hours': self.circadian_analyzer.get_best_focus_hours(),
                'risky_hours': self.circadian_analyzer.get_risky_hours()
            }

    def get_intervention_recommendation(self, session_id: str) -> dict | None:
        """
        Få anbefaling om intervensjon basert på nåværende tilstand
        """
        state = self.get_current_state(session_id)
        if not state:
            return None

        # Ingen intervensjon ved fokus
        if state['state'] == 'FOCUSED':
            return None

        # Dopamin-loop = prioritet 1
        if state['is_looping'] and state['loop_intensity'] > 0.5:
            return {
                'type': 'dopamine_intervention',
                'urgency': min(5, int(state['loop_intensity'] * 6)),
                'action': 'pause_suggestion',
                'message': "Din hjerne trenger en pause fra denne stimuleringen",
                'duration': 300,  # 5 min pause
                'alternatives': ['walk', 'stretch', 'water']
            }

        # Mye distraction
        if state['distraction_count'] > 10:
            return {
                'type': 'focus_intervention',
                'urgency': 3,
                'action': 'focus_mode',
                'message': "Mange avbrytelser - vil du aktivere fokus-modus?",
                'duration': 1800,  # 30 min fokus
                'block_apps': ['social', 'entertainment']
            }

        # Lang sesjon uten pause
        if state['session_duration'] > 7200:  # 2 timer
            return {
                'type': 'break_reminder',
                'urgency': 2,
                'action': 'take_break',
                'message': "Du har vært aktiv i over 2 timer",
                'duration': 600,  # 10 min pause
                'alternatives': ['walk', 'snack', 'eyes_rest']
            }

        return None


# Factory function
def create_analytics_engine(data_dir: str = "/home/jovnna/aiki/data/proxy") -> BehavioralAnalyticsEngine:
    """Opprett behavioral analytics engine"""
    return BehavioralAnalyticsEngine(Path(data_dir))
