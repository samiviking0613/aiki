#!/usr/bin/env python3
"""
📊 CLAUDE USAGE TRACKER - Monitor Claude API Usage

Tracker tokens og estimert bruk opp mot Claude Pro/Max limits.
Viser warnings når man nærmer seg grensene.

Limits (Claude Pro):
- Session: 200k tokens per 5 hours
- Weekly: ~500k tokens per uke (All models, 76% = ~380k brukt)
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import sys

# Paths
USAGE_FILE = Path.home() / "aiki" / "data" / "claude_usage.json"
USAGE_FILE.parent.mkdir(exist_ok=True, parents=True)

# Limits (basert på Claude Pro - juster etter ditt abonnement)
LIMITS = {
    'session': {
        'tokens': 200_000,  # 200k tokens per 5 timer
        'duration_hours': 5
    },
    'weekly': {
        'tokens': 500_000,  # Estimert weekly limit for All models
        'reset_day': 6  # Søndag = 6 (0=Monday)
    }
}


class ClaudeUsageTracker:
    """Track Claude Code token usage"""

    def __init__(self):
        self.usage_file = USAGE_FILE
        self.data = self._load_usage()

    def _load_usage(self) -> Dict[str, Any]:
        """Load usage data from file"""
        if not self.usage_file.exists():
            return {
                'sessions': [],
                'weekly_total': 0,
                'weekly_reset': self._next_reset_date().isoformat(),
                'last_updated': datetime.now().isoformat()
            }

        with open(self.usage_file, 'r') as f:
            return json.load(f)

    def _save_usage(self):
        """Save usage data to file"""
        self.data['last_updated'] = datetime.now().isoformat()
        with open(self.usage_file, 'w') as f:
            json.dump(self.data, f, indent=2)

    def _next_reset_date(self) -> datetime:
        """Calculate next weekly reset (Sunday 11:00)"""
        now = datetime.now()
        days_until_sunday = (6 - now.weekday()) % 7
        if days_until_sunday == 0 and now.hour >= 11:
            days_until_sunday = 7  # Next sunday

        reset_date = now + timedelta(days=days_until_sunday)
        return reset_date.replace(hour=11, minute=0, second=0, microsecond=0)

    def _check_weekly_reset(self):
        """Check if weekly limit should reset"""
        reset_date = datetime.fromisoformat(self.data['weekly_reset'])

        if datetime.now() >= reset_date:
            # Reset weekly counter
            self.data['weekly_total'] = 0
            self.data['weekly_reset'] = self._next_reset_date().isoformat()
            self._save_usage()
            print("🔄 Weekly usage reset!")

    def _clean_old_sessions(self):
        """Remove sessions older than 5 hours"""
        cutoff = datetime.now() - timedelta(hours=5)
        self.data['sessions'] = [
            s for s in self.data['sessions']
            if datetime.fromisoformat(s['timestamp']) > cutoff
        ]

    def add_session(self, tokens_used: int, description: str = "Claude Code session"):
        """Add a session's token usage"""
        self._check_weekly_reset()
        self._clean_old_sessions()

        session = {
            'timestamp': datetime.now().isoformat(),
            'tokens': tokens_used,
            'description': description
        }

        self.data['sessions'].append(session)
        self.data['weekly_total'] += tokens_used
        self._save_usage()

    def get_session_usage(self) -> Dict[str, Any]:
        """Get current 5-hour session usage"""
        self._clean_old_sessions()

        session_total = sum(s['tokens'] for s in self.data['sessions'])
        session_limit = LIMITS['session']['tokens']
        session_percent = (session_total / session_limit) * 100

        # Calculate time until session reset
        if self.data['sessions']:
            oldest_session = min(
                datetime.fromisoformat(s['timestamp'])
                for s in self.data['sessions']
            )
            reset_time = oldest_session + timedelta(hours=5)
            time_until_reset = reset_time - datetime.now()
            hours = int(time_until_reset.total_seconds() / 3600)
            minutes = int((time_until_reset.total_seconds() % 3600) / 60)
            reset_str = f"{hours}h {minutes}m"
        else:
            reset_str = "N/A"

        return {
            'used': session_total,
            'limit': session_limit,
            'remaining': session_limit - session_total,
            'percent': round(session_percent, 1),
            'resets_in': reset_str
        }

    def get_weekly_usage(self) -> Dict[str, Any]:
        """Get weekly usage"""
        self._check_weekly_reset()

        weekly_limit = LIMITS['weekly']['tokens']
        weekly_percent = (self.data['weekly_total'] / weekly_limit) * 100

        reset_date = datetime.fromisoformat(self.data['weekly_reset'])
        time_until_reset = reset_date - datetime.now()
        days = time_until_reset.days
        hours = int(time_until_reset.seconds / 3600)

        return {
            'used': self.data['weekly_total'],
            'limit': weekly_limit,
            'remaining': weekly_limit - self.data['weekly_total'],
            'percent': round(weekly_percent, 1),
            'resets_in': f"{days}d {hours}h",
            'reset_date': reset_date.strftime('%a %H:%M')
        }

    def print_status(self):
        """Print formatted usage status"""
        session = self.get_session_usage()
        weekly = self.get_weekly_usage()

        print("\n" + "="*60)
        print("📊 CLAUDE CODE USAGE TRACKER")
        print("="*60)

        # Session usage
        print(f"\n🕐 Current Session (5h rolling window):")
        print(f"   Used: {session['used']:,} / {session['limit']:,} tokens")
        print(f"   Remaining: {session['remaining']:,} tokens")
        bar = self._progress_bar(session['percent'])
        print(f"   {bar} {session['percent']}%")
        print(f"   Resets in: {session['resets_in']}")

        if session['percent'] > 70:
            print(f"   ⚠️  WARNING: {session['percent']}% av session limit brukt!")

        # Weekly usage
        print(f"\n📅 Weekly Usage:")
        print(f"   Used: {weekly['used']:,} / {weekly['limit']:,} tokens")
        print(f"   Remaining: {weekly['remaining']:,} tokens")
        bar = self._progress_bar(weekly['percent'])
        print(f"   {bar} {weekly['percent']}%")
        print(f"   Resets: {weekly['reset_date']} ({weekly['resets_in']})")

        if weekly['percent'] > 80:
            print(f"   🚨 KRITISK: {weekly['percent']}% av ukentlig limit brukt!")
        elif weekly['percent'] > 60:
            print(f"   ⚠️  ADVARSEL: {weekly['percent']}% av ukentlig limit brukt!")

        print("\n" + "="*60 + "\n")

    def _progress_bar(self, percent: float, width: int = 30) -> str:
        """Generate a progress bar"""
        filled = int(width * percent / 100)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}]"

    def should_warn(self) -> Optional[str]:
        """Check if usage is high enough to warn user"""
        session = self.get_session_usage()
        weekly = self.get_weekly_usage()

        warnings = []

        if session['percent'] > 80:
            warnings.append(f"🚨 Session: {session['percent']}% brukt!")

        if weekly['percent'] > 80:
            warnings.append(f"🚨 Weekly: {weekly['percent']}% brukt!")
        elif weekly['percent'] > 60:
            warnings.append(f"⚠️  Weekly: {weekly['percent']}% brukt")

        return " | ".join(warnings) if warnings else None

    def get_status_json(self) -> str:
        """Get status as JSON for statusline integration"""
        session = self.get_session_usage()
        weekly = self.get_weekly_usage()

        status = {
            'session': {
                'percent': session['percent'],
                'tokens_used': session['used'],
                'limit': session['limit']
            },
            'weekly': {
                'percent': weekly['percent'],
                'tokens_used': weekly['used'],
                'limit': weekly['limit']
            }
        }

        return json.dumps(status)


# CLI Interface
def main():
    """CLI for usage tracking"""
    tracker = ClaudeUsageTracker()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "add":
            tokens = int(sys.argv[2]) if len(sys.argv) > 2 else 10000
            desc = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else "Manual entry"
            tracker.add_session(tokens, desc)
            print(f"✅ Added {tokens:,} tokens: {desc}")

        elif command == "reset":
            tracker.data['weekly_total'] = 0
            tracker.data['sessions'] = []
            tracker._save_usage()
            print("🔄 Usage data reset!")

        elif command == "status":
            # Check if JSON output is requested (for statusline integration)
            if "--json" in sys.argv or len(sys.argv) == 2:
                # Output raw JSON for parsing by statusline.sh
                print(tracker.get_status_json())
            else:
                tracker.print_status()

        else:
            print("Usage: claude_usage_tracker.py [status|add <tokens> <desc>|reset]")
    else:
        # Default: print status
        tracker.print_status()


if __name__ == "__main__":
    main()
