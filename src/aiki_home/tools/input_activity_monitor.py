#!/usr/bin/env python3
"""
INPUT ACTIVITY MONITOR - Lokal aktivitetsovervåker for AIKI-HOME

Måler brukeraktivitet (tastatur/mus) for å forstå:
- Når brukeren er aktiv vs passiv
- Produktive perioder (mye skriving) vs passive (scrolling)
- Pauser og avbrudd
- Dag-til-dag mønstre

VIKTIG PERSONVERN:
- Logger ALDRI hva som skrives (kun at det skrives)
- Logger ALDRI hvor musen er (kun at den beveger seg)
- All data forblir LOKALT på enheten
- Kun anonymiserte MØNSTRE kan deles (med samtykke)

Tenk på det som en skritteller for databruk - måler aktivitet, ikke innhold.
"""

import asyncio
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import logging
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class ActivityLevel(Enum):
    """Aktivitetsnivå basert på input"""
    IDLE = "idle"           # Ingen aktivitet
    LOW = "low"             # Lite aktivitet (scrolling, lesing)
    MODERATE = "moderate"   # Moderat (navigering, lett skriving)
    HIGH = "high"           # Høy (aktiv skriving, arbeid)
    INTENSE = "intense"     # Intens (rask skriving, flow-state)


class ActivityType(Enum):
    """Type aktivitet"""
    TYPING = "typing"       # Tastaturaktivitet
    MOUSE = "mouse"         # Musaktivitet
    MIXED = "mixed"         # Begge deler
    UNKNOWN = "unknown"


@dataclass
class ActivityWindow:
    """Et vindu med aktivitetsdata (typisk 1-5 min)"""
    start_time: datetime
    end_time: datetime

    # Tellere (IKKE innhold!)
    keystrokes: int = 0      # Antall tastetrykk
    mouse_moves: int = 0     # Antall musebevegelser
    mouse_clicks: int = 0    # Antall klikk
    scroll_events: int = 0   # Antall scroll-events

    # Beregnede verdier
    activity_level: ActivityLevel = ActivityLevel.IDLE
    activity_type: ActivityType = ActivityType.UNKNOWN

    # Pause-deteksjon
    idle_seconds: float = 0  # Sekunder uten aktivitet i vinduet
    breaks_taken: int = 0    # Antall pauser > 30 sek


@dataclass
class DailyPattern:
    """Daglig aktivitetsmønster"""
    date: str  # YYYY-MM-DD

    # Per-time aktivitet (24 timer)
    hourly_activity: Dict[int, float] = field(default_factory=dict)

    # Sammendrag
    total_active_minutes: int = 0
    peak_hour: int = 0
    low_hour: int = 0

    # ADHD-relevante metrics
    context_switches: int = 0      # Antall gang idle->active
    longest_focus_streak: int = 0  # Lengste periode uten lange pauser
    avg_session_length: float = 0  # Gjennomsnittlig arbeidsøkt


class InputActivityMonitor:
    """
    Input Activity Monitor - Måler aktivitet uten å logge innhold

    Brukes til:
    1. Forstå når brukeren er mest produktiv
    2. Detektere ADHD-mønstre (hyppige pauser, context-switching)
    3. Trigge intervensjoner (f.eks. "ta en pause" etter lang intensiv periode)
    4. Lære optimale tidspunkter for fokus-modus

    PERSONVERN: Logger KUN aktivitetsnivå, aldri innhold!
    """

    def __init__(
        self,
        window_seconds: int = 60,
        idle_threshold_seconds: int = 30,
        data_dir: Optional[Path] = None
    ):
        self.window_seconds = window_seconds
        self.idle_threshold_seconds = idle_threshold_seconds
        self.data_dir = data_dir or Path.home() / '.aiki_home' / 'activity'
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Nåværende vindu
        self.current_window: Optional[ActivityWindow] = None
        self._window_start: Optional[datetime] = None

        # Historikk (siste 24 timer i minnet)
        self.recent_windows: deque = deque(maxlen=1440)  # 24h * 60 min

        # State
        self.running = False
        self._last_activity: float = time.time()
        self._keystroke_count = 0
        self._mouse_move_count = 0
        self._mouse_click_count = 0
        self._scroll_count = 0

        # Callbacks
        self._on_activity_change: Optional[Callable] = None
        self._on_idle_detected: Optional[Callable] = None
        self._on_focus_streak: Optional[Callable] = None

        # Dagens mønster
        self.today_pattern: Optional[DailyPattern] = None

        logger.info("InputActivityMonitor initialized")

    def register_keystroke(self):
        """
        Registrer et tastetrykk.

        VIKTIG: Tar IKKE imot hvilken tast - kun at en tast ble trykket!
        """
        self._keystroke_count += 1
        self._last_activity = time.time()

    def register_mouse_move(self):
        """
        Registrer musebevegelse.

        VIKTIG: Tar IKKE imot posisjon - kun at musen beveget seg!
        """
        self._mouse_move_count += 1
        self._last_activity = time.time()

    def register_mouse_click(self):
        """Registrer museklikk (uten posisjon)"""
        self._mouse_click_count += 1
        self._last_activity = time.time()

    def register_scroll(self):
        """Registrer scroll-event (uten retning/mengde)"""
        self._scroll_count += 1
        self._last_activity = time.time()

    async def start(self):
        """Start monitoren"""
        self.running = True
        self._start_new_window()
        self._load_today_pattern()

        logger.info("InputActivityMonitor started")

        # Start window-prosessering
        asyncio.create_task(self._window_loop())
        asyncio.create_task(self._idle_check_loop())

    async def stop(self):
        """Stopp monitoren og lagre data"""
        self.running = False

        # Lagre siste vindu
        if self.current_window:
            self._finalize_window()

        # Lagre dagens mønster
        self._save_today_pattern()

        logger.info("InputActivityMonitor stopped")

    def _start_new_window(self):
        """Start nytt aktivitetsvindu"""
        now = datetime.now(timezone.utc)

        self.current_window = ActivityWindow(
            start_time=now,
            end_time=now + timedelta(seconds=self.window_seconds)
        )
        self._window_start = now

        # Reset tellere
        self._keystroke_count = 0
        self._mouse_move_count = 0
        self._mouse_click_count = 0
        self._scroll_count = 0

    def _finalize_window(self):
        """Fullfør nåværende vindu og beregn metrics"""
        if not self.current_window:
            return

        window = self.current_window

        # Overfør tellere
        window.keystrokes = self._keystroke_count
        window.mouse_moves = self._mouse_move_count
        window.mouse_clicks = self._mouse_click_count
        window.scroll_events = self._scroll_count

        # Beregn aktivitetsnivå
        window.activity_level = self._calculate_activity_level(window)
        window.activity_type = self._calculate_activity_type(window)

        # Legg til i historikk
        self.recent_windows.append(window)

        # Oppdater dagens mønster
        self._update_daily_pattern(window)

        # Callbacks
        if self._on_activity_change:
            asyncio.create_task(self._on_activity_change(window))

    def _calculate_activity_level(self, window: ActivityWindow) -> ActivityLevel:
        """
        Beregn aktivitetsnivå basert på input.

        Visualisert som et termometer:

        ┌─────┐
        │█████│ INTENSE  (>200 keystrokes/min, flow-state)
        │████ │ HIGH     (100-200 keystrokes/min, aktiv skriving)
        │███  │ MODERATE (30-100 keystrokes/min, lett arbeid)
        │██   │ LOW      (1-30 events/min, lesing/scrolling)
        │░    │ IDLE     (0 events/min)
        └─────┘
        """
        total_events = (
            window.keystrokes +
            window.mouse_clicks +
            window.scroll_events +
            window.mouse_moves // 10  # Musebevegelser teller mindre
        )

        events_per_minute = total_events * (60 / self.window_seconds)

        if events_per_minute == 0:
            return ActivityLevel.IDLE
        elif events_per_minute < 30:
            return ActivityLevel.LOW
        elif events_per_minute < 100:
            return ActivityLevel.MODERATE
        elif events_per_minute < 200:
            return ActivityLevel.HIGH
        else:
            return ActivityLevel.INTENSE

    def _calculate_activity_type(self, window: ActivityWindow) -> ActivityType:
        """Bestem om aktiviteten er tastatur, mus, eller blandet"""
        if window.keystrokes == 0 and window.mouse_moves == 0:
            return ActivityType.UNKNOWN

        keyboard_score = window.keystrokes
        mouse_score = window.mouse_moves + window.mouse_clicks * 5 + window.scroll_events * 2

        if keyboard_score > mouse_score * 2:
            return ActivityType.TYPING
        elif mouse_score > keyboard_score * 2:
            return ActivityType.MOUSE
        else:
            return ActivityType.MIXED

    async def _window_loop(self):
        """Hovedloop som prosesserer vinduer"""
        while self.running:
            await asyncio.sleep(self.window_seconds)

            self._finalize_window()
            self._start_new_window()

    async def _idle_check_loop(self):
        """Sjekk for idle og trigger callbacks"""
        while self.running:
            await asyncio.sleep(5)  # Sjekk hvert 5. sekund

            idle_time = time.time() - self._last_activity

            if idle_time > self.idle_threshold_seconds:
                if self._on_idle_detected:
                    await self._on_idle_detected(idle_time)

    def _update_daily_pattern(self, window: ActivityWindow):
        """Oppdater dagens mønster med nytt vindu"""
        if not self.today_pattern:
            self._load_today_pattern()

        hour = window.start_time.hour

        # Oppdater time-aktivitet
        if hour not in self.today_pattern.hourly_activity:
            self.today_pattern.hourly_activity[hour] = 0

        # Konverter aktivitetsnivå til tall
        level_score = {
            ActivityLevel.IDLE: 0,
            ActivityLevel.LOW: 0.25,
            ActivityLevel.MODERATE: 0.5,
            ActivityLevel.HIGH: 0.75,
            ActivityLevel.INTENSE: 1.0
        }

        self.today_pattern.hourly_activity[hour] += level_score[window.activity_level]

        # Oppdater totaler
        if window.activity_level != ActivityLevel.IDLE:
            self.today_pattern.total_active_minutes += 1

    def _load_today_pattern(self):
        """Last eller opprett dagens mønster"""
        today = datetime.now().strftime('%Y-%m-%d')
        pattern_file = self.data_dir / f'{today}.json'

        if pattern_file.exists():
            with open(pattern_file) as f:
                data = json.load(f)
                self.today_pattern = DailyPattern(
                    date=data['date'],
                    hourly_activity=data.get('hourly_activity', {}),
                    total_active_minutes=data.get('total_active_minutes', 0),
                    peak_hour=data.get('peak_hour', 0),
                    low_hour=data.get('low_hour', 0),
                    context_switches=data.get('context_switches', 0),
                    longest_focus_streak=data.get('longest_focus_streak', 0),
                    avg_session_length=data.get('avg_session_length', 0)
                )
        else:
            self.today_pattern = DailyPattern(date=today)

    def _save_today_pattern(self):
        """Lagre dagens mønster til fil"""
        if not self.today_pattern:
            return

        pattern_file = self.data_dir / f'{self.today_pattern.date}.json'

        # Beregn peak/low hours
        if self.today_pattern.hourly_activity:
            self.today_pattern.peak_hour = max(
                self.today_pattern.hourly_activity,
                key=self.today_pattern.hourly_activity.get
            )
            self.today_pattern.low_hour = min(
                self.today_pattern.hourly_activity,
                key=self.today_pattern.hourly_activity.get
            )

        data = {
            'date': self.today_pattern.date,
            'hourly_activity': self.today_pattern.hourly_activity,
            'total_active_minutes': self.today_pattern.total_active_minutes,
            'peak_hour': self.today_pattern.peak_hour,
            'low_hour': self.today_pattern.low_hour,
            'context_switches': self.today_pattern.context_switches,
            'longest_focus_streak': self.today_pattern.longest_focus_streak,
            'avg_session_length': self.today_pattern.avg_session_length
        }

        with open(pattern_file, 'w') as f:
            json.dump(data, f, indent=2)

    def on_activity_change(self, callback: Callable):
        """Registrer callback for aktivitetsendringer"""
        self._on_activity_change = callback

    def on_idle_detected(self, callback: Callable):
        """Registrer callback for idle-deteksjon"""
        self._on_idle_detected = callback

    def on_focus_streak(self, callback: Callable):
        """Registrer callback for fokus-streaks"""
        self._on_focus_streak = callback

    def get_current_level(self) -> ActivityLevel:
        """Hent nåværende aktivitetsnivå"""
        if not self.current_window:
            return ActivityLevel.IDLE

        # Lag midlertidig vindu for å beregne
        temp = ActivityWindow(
            start_time=self.current_window.start_time,
            end_time=datetime.now(timezone.utc),
            keystrokes=self._keystroke_count,
            mouse_moves=self._mouse_move_count,
            mouse_clicks=self._mouse_click_count,
            scroll_events=self._scroll_count
        )
        return self._calculate_activity_level(temp)

    def get_today_summary(self) -> Dict[str, Any]:
        """
        Hent dagens sammendrag.

        Returnerer noe som:
        {
            'date': '2025-11-23',
            'total_active_hours': 5.3,
            'peak_hour': 10,  # Mest aktiv kl 10
            'activity_distribution': {
                'morning': 0.4,   # 40% aktivitet om morgenen
                'afternoon': 0.5, # 50% på ettermiddagen
                'evening': 0.1    # 10% på kvelden
            }
        }
        """
        if not self.today_pattern:
            return {'error': 'No data'}

        # Beregn fordeling
        morning = sum(self.today_pattern.hourly_activity.get(h, 0) for h in range(6, 12))
        afternoon = sum(self.today_pattern.hourly_activity.get(h, 0) for h in range(12, 18))
        evening = sum(self.today_pattern.hourly_activity.get(h, 0) for h in range(18, 24))
        total = morning + afternoon + evening or 1

        return {
            'date': self.today_pattern.date,
            'total_active_hours': self.today_pattern.total_active_minutes / 60,
            'peak_hour': self.today_pattern.peak_hour,
            'activity_distribution': {
                'morning': morning / total,
                'afternoon': afternoon / total,
                'evening': evening / total
            },
            'context_switches': self.today_pattern.context_switches,
            'longest_focus_streak': self.today_pattern.longest_focus_streak
        }

    def get_anonymized_patterns(self) -> Dict[str, Any]:
        """
        Hent anonymiserte mønstre som KAN deles med Prime.

        VIKTIG: Inneholder KUN aggregerte mønstre, ingen personlig data!

        Brukes for pheromone-systemet til å lære fra mange brukere.
        """
        if not self.today_pattern:
            return {}

        # Normaliser time-aktivitet (0-1 skala)
        max_activity = max(self.today_pattern.hourly_activity.values()) or 1
        normalized = {
            h: v / max_activity
            for h, v in self.today_pattern.hourly_activity.items()
        }

        return {
            'profile_type': 'adhd_adult',  # Settes basert på config
            'hourly_pattern': normalized,
            'peak_productivity_hour': self.today_pattern.peak_hour,
            'avg_focus_duration_minutes': self.today_pattern.avg_session_length,
            'context_switch_frequency': self.today_pattern.context_switches / max(self.today_pattern.total_active_minutes, 1)
        }


async def main():
    """Test Input Activity Monitor"""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║          INPUT ACTIVITY MONITOR - DEMO                       ║
    ╠══════════════════════════════════════════════════════════════╣
    ║                                                              ║
    ║  Tenk på dette som en SKRITTELLER for datamaskinen:          ║
    ║                                                              ║
    ║    ┌─────────────────────────────────────┐                   ║
    ║    │  🏃 Skritteller   │  ⌨️ Aktivitet   │                   ║
    ║    ├─────────────────────────────────────┤                   ║
    ║    │  Teller skritt    │  Teller trykk   │                   ║
    ║    │  Ikke HVOR du går │  Ikke HVA du    │                   ║
    ║    │                   │  skriver        │                   ║
    ║    └─────────────────────────────────────┘                   ║
    ║                                                              ║
    ║  PERSONVERN: Vi logger AKTIVITET, ikke INNHOLD!              ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

    monitor = InputActivityMonitor(window_seconds=5)  # Kort vindu for demo

    # Registrer callbacks
    async def on_activity(window):
        level_bar = {
            ActivityLevel.IDLE: "░░░░░",
            ActivityLevel.LOW: "█░░░░",
            ActivityLevel.MODERATE: "██░░░",
            ActivityLevel.HIGH: "███░░",
            ActivityLevel.INTENSE: "█████"
        }
        print(f"  Aktivitet: [{level_bar[window.activity_level]}] {window.activity_level.value}")
        print(f"    Tastetrykk: {window.keystrokes}, Mus: {window.mouse_moves}")

    async def on_idle(seconds):
        print(f"  💤 Idle i {seconds:.0f} sekunder...")

    monitor.on_activity_change(on_activity)
    monitor.on_idle_detected(on_idle)

    await monitor.start()

    # Simuler aktivitet
    print("\nSimulerer aktivitet (5 sekunder)...\n")

    for i in range(50):
        monitor.register_keystroke()
        if i % 3 == 0:
            monitor.register_mouse_move()
        await asyncio.sleep(0.1)

    # Vent litt
    await asyncio.sleep(2)

    # Mer aktivitet
    for i in range(20):
        monitor.register_mouse_move()
        monitor.register_scroll()
        await asyncio.sleep(0.05)

    await asyncio.sleep(3)

    # Hent sammendrag
    print("\n" + "="*60)
    print("DAGENS SAMMENDRAG:")
    print("="*60)
    summary = monitor.get_today_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")

    await monitor.stop()


if __name__ == "__main__":
    asyncio.run(main())
