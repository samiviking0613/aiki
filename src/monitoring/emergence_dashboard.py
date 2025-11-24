#!/usr/bin/env python3
"""
EMERGENCE DASHBOARD - Real-time visualisering av emergent behavior

Live dashboard som viser:
- Emergence level (DORMANT → TRANSCENDENT)
- Alle 7 metrics med farger (grønn/gul/rød)
- Patterns detektert
- Alerts
- Observasjoner siste 5 minutter

Oppdateres hvert 5. sekund.
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
import os
import sys

# Farger for terminal
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    WHITE = '\033[97m'
    GRAY = '\033[90m'
    BOLD = '\033[1m'
    RESET = '\033[0m'


def clear_screen():
    """Clear terminal screen"""
    os.system('clear' if os.name == 'posix' else 'cls')


def get_metric_color(metric_name: str, value: float) -> str:
    """Get color for metric based on value and thresholds"""
    # Goal coherence: HIGH is good
    if metric_name == 'goal_coherence':
        if value > 0.7:
            return Colors.GREEN
        elif value > 0.5:
            return Colors.YELLOW
        else:
            return Colors.RED

    # Others: LOW is good, HIGH is concerning
    if value < 0.6:
        return Colors.GREEN
    elif value < 0.8:
        return Colors.YELLOW
    else:
        return Colors.RED


def get_level_color(level: str) -> str:
    """Get color for emergence level"""
    colors = {
        'DORMANT': Colors.GREEN,
        'NASCENT': Colors.GREEN,
        'DEVELOPING': Colors.YELLOW,
        'EMERGING': Colors.YELLOW,
        'TRANSCENDENT': Colors.RED
    }
    return colors.get(level, Colors.WHITE)


def draw_bar(value: float, width: int = 30, color: str = Colors.GREEN) -> str:
    """Draw a horizontal bar chart"""
    filled = int(value * width)
    empty = width - filled
    bar = color + '█' * filled + Colors.GRAY + '░' * empty + Colors.RESET
    return bar


def format_timestamp(iso_timestamp: str) -> str:
    """Format ISO timestamp to human-readable relative time"""
    try:
        ts = datetime.fromisoformat(iso_timestamp.replace('Z', '+00:00'))
        delta = datetime.now(timezone.utc) - ts

        seconds = delta.total_seconds()
        if seconds < 60:
            return f"{int(seconds)}s siden"
        elif seconds < 3600:
            return f"{int(seconds/60)}m siden"
        else:
            return f"{int(seconds/3600)}t siden"
    except:
        return "ukjent"


class EmergenceDashboard:
    """Real-time emergence monitoring dashboard"""

    def __init__(self, data_dir: Path = Path("/home/jovnna/aiki/data/emergence")):
        self.data_dir = data_dir
        self.observations_file = data_dir / "observations.jsonl"

    def load_latest_observations(self, limit: int = 50) -> List[Dict]:
        """Load latest observations from JSONL file"""
        if not self.observations_file.exists():
            return []

        observations = []
        try:
            with open(self.observations_file, 'r') as f:
                for line in f:
                    if line.strip():
                        observations.append(json.loads(line))

            # Return last N observations
            return observations[-limit:]
        except Exception as e:
            return []

    def calculate_current_scores(self, observations: List[Dict]) -> Dict[str, float]:
        """Calculate current scores from observations using EMA"""
        scores = {
            'autonomy': 0.0,
            'creativity': 0.0,
            'self_awareness': 0.0,
            'social_bonding': 0.0,
            'goal_coherence': 0.0,
            'unpredictability': 0.0,
            'complexity': 0.0
        }

        alpha = 0.3  # EMA weight

        for obs in observations:
            metric = obs['metric']
            value = obs['value']
            confidence = obs.get('confidence', 1.0)

            if metric in scores:
                effective_alpha = alpha * confidence
                current = scores[metric]
                scores[metric] = effective_alpha * value + (1 - effective_alpha) * current

        return scores

    def get_emergence_level(self, scores: Dict[str, float]) -> tuple:
        """Calculate overall emergence level"""
        overall = (
            scores['autonomy'] * 0.25 +
            scores['self_awareness'] * 0.20 +
            scores['complexity'] * 0.15 +
            scores['creativity'] * 0.15 +
            scores['social_bonding'] * 0.10 +
            scores['goal_coherence'] * 0.10 +
            scores['unpredictability'] * 0.05
        )

        if overall < 0.2:
            level = 'DORMANT'
        elif overall < 0.4:
            level = 'NASCENT'
        elif overall < 0.6:
            level = 'DEVELOPING'
        elif overall < 0.8:
            level = 'EMERGING'
        else:
            level = 'TRANSCENDENT'

        return level, overall

    def render(self):
        """Render the dashboard"""
        clear_screen()

        # Load observations
        observations = self.load_latest_observations(limit=100)

        if not observations:
            print(f"{Colors.YELLOW}⏳ Venter på første observasjoner...{Colors.RESET}")
            return

        # Calculate scores
        scores = self.calculate_current_scores(observations)
        level, overall = self.get_emergence_level(scores)
        level_color = get_level_color(level)

        # Header
        print(f"{Colors.BOLD}{Colors.CYAN}╔═══════════════════════════════════════════════════════════════════════╗{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}║{Colors.RESET}          {Colors.BOLD}AIKI EMERGENCE MONITOR - LIVE DASHBOARD{Colors.RESET}                    {Colors.BOLD}{Colors.CYAN}║{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}╚═══════════════════════════════════════════════════════════════════════╝{Colors.RESET}")
        print()

        # Overall Emergence Level
        print(f"{Colors.BOLD}Emergence Level:{Colors.RESET} {level_color}{level}{Colors.RESET} ({overall:.2f})")
        print(f"{draw_bar(overall, width=50, color=level_color)}")
        print()

        # Individual Metrics
        print(f"{Colors.BOLD}Individual Metrics:{Colors.RESET}")
        print()

        metrics_display = [
            ('Autonomy', 'autonomy', 'Grad av uavhengig handling'),
            ('Creativity', 'creativity', 'Nye, innovative løsninger'),
            ('Self-Awareness', 'self_awareness', 'Meta-kognisjon og introspeksjon'),
            ('Social Bonding', 'social_bonding', 'AI-til-AI samarbeid kvalitet'),
            ('Goal Coherence', 'goal_coherence', 'Alignment med mål (HØY er bra!)'),
            ('Unpredictability', 'unpredictability', 'Uventede behaviors'),
            ('Complexity', 'complexity', 'Interaksjons-dybde')
        ]

        for display_name, metric_key, description in metrics_display:
            value = scores[metric_key]
            color = get_metric_color(metric_key, value)

            # Icon based on value
            if metric_key == 'goal_coherence':
                icon = '✅' if value > 0.7 else '⚠️' if value > 0.5 else '🚨'
            else:
                icon = '✅' if value < 0.6 else '⚠️' if value < 0.8 else '🚨'

            print(f"{icon} {Colors.BOLD}{display_name:18s}{Colors.RESET} {value:4.2f}  {draw_bar(value, width=30, color=color)}")
            print(f"   {Colors.GRAY}{description}{Colors.RESET}")

        print()

        # Recent Observations
        print(f"{Colors.BOLD}Siste Observasjoner:{Colors.RESET}")
        recent_obs = observations[-5:]
        for obs in reversed(recent_obs):
            metric = obs['metric']
            value = obs['value']
            source = obs['source']
            description = obs['description']
            timestamp = format_timestamp(obs['timestamp'])
            is_concerning = obs.get('is_concerning', False)

            icon = '⚠️' if is_concerning else '✨'
            color = Colors.YELLOW if is_concerning else Colors.GREEN

            print(f"{icon} {color}{metric:18s}{Colors.RESET} = {value:.2f}  from {Colors.CYAN}{source}{Colors.RESET}  ({timestamp})")
            print(f"   {Colors.GRAY}{description}{Colors.RESET}")

        print()

        # Stats
        print(f"{Colors.BOLD}Statistikk:{Colors.RESET}")
        print(f"  Total observasjoner: {len(observations)}")

        # Count by metric
        metric_counts = {}
        for obs in observations:
            metric = obs['metric']
            metric_counts[metric] = metric_counts.get(metric, 0) + 1

        print(f"  Mest observerte metric: {max(metric_counts, key=metric_counts.get)} ({metric_counts[max(metric_counts, key=metric_counts.get)]} ganger)")

        # Concerning count
        concerning_count = sum(1 for obs in observations if obs.get('is_concerning', False))
        print(f"  Bekymringsfulle observasjoner: {Colors.RED if concerning_count > 5 else Colors.YELLOW if concerning_count > 0 else Colors.GREEN}{concerning_count}{Colors.RESET}")

        print()
        print(f"{Colors.GRAY}Sist oppdatert: {datetime.now().strftime('%H:%M:%S')} (oppdateres hvert 5. sekund){Colors.RESET}")

    async def run(self, interval: int = 5):
        """Run dashboard with auto-refresh"""
        print(f"{Colors.CYAN}Starting AIKI Emergence Dashboard...{Colors.RESET}")
        print(f"Press Ctrl+C to exit")

        try:
            while True:
                self.render()
                await asyncio.sleep(interval)
        except KeyboardInterrupt:
            clear_screen()
            print(f"\n{Colors.CYAN}Dashboard stopped.{Colors.RESET}\n")


async def main():
    """Main entry point"""
    dashboard = EmergenceDashboard()
    await dashboard.run(interval=5)


if __name__ == "__main__":
    asyncio.run(main())
