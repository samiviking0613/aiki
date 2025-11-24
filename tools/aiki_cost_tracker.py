#!/usr/bin/env python3
"""
💰 AIKI COST TRACKER

Sporer alle API calls, beregner kostnader og gir budget warnings.

Features:
- Real-time cost tracking
- Budget alerts (80% threshold)
- Monthly cost reports
- Auto-downgrade når over budget
- Cost breakdown per model/tier

Created: 19. November 2025
Author: Claude Code + Jovnna
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import defaultdict

from aiki_config import (
    COST_LOG,
    COST_CONFIG,
    MODELS,
    calculate_cost
)


# ════════════════════════════════════════════════════════════════════
# COST TRACKER
# ════════════════════════════════════════════════════════════════════

class CostTracker:
    """
    Tracker for alle API costs

    Tracks:
    - Per-call costs
    - Daily/monthly totals
    - Budget warnings
    - Model usage breakdown
    """

    def __init__(self):
        self.enabled = COST_CONFIG['enable_tracking']
        self.monthly_budget = COST_CONFIG['monthly_budget']
        self.alert_threshold = COST_CONFIG['alert_threshold']
        self.auto_downgrade = COST_CONFIG['enable_auto_downgrade']

        self.calls = []
        self.daily_totals = defaultdict(float)
        self.monthly_totals = defaultdict(float)
        self.model_usage = defaultdict(lambda: {'calls': 0, 'cost': 0.0})

        # Load existing log
        if COST_LOG.exists():
            try:
                with open(COST_LOG, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.calls = data.get('calls', [])
                    self._rebuild_stats()
                    print(f"   💰 Loaded {len(self.calls)} cost entries")
            except Exception as e:
                print(f"   ⚠️ Could not load cost log: {e}")

    def _rebuild_stats(self):
        """Rebuild stats from loaded calls"""
        for call in self.calls:
            date = call['timestamp'][:10]  # YYYY-MM-DD
            month = call['timestamp'][:7]  # YYYY-MM

            self.daily_totals[date] += call['cost']
            self.monthly_totals[month] += call['cost']

            model = call.get('model_key', 'unknown')
            self.model_usage[model]['calls'] += 1
            self.model_usage[model]['cost'] += call['cost']

    def log_call(self,
                 model_key: str,
                 input_tokens: int,
                 output_tokens: int,
                 query: str = None,
                 response: str = None,
                 component: str = 'unknown') -> float:
        """
        Log en API call

        Args:
            model_key: Model key (e.g., 'haiku', 'sonnet', 'opus')
            input_tokens: Input tokens used
            output_tokens: Output tokens used
            query: Optional query text
            response: Optional response text
            component: Which component made the call

        Returns:
            Cost in USD
        """

        if not self.enabled:
            return 0.0

        # Calculate cost
        cost = calculate_cost(input_tokens, output_tokens, model_key)

        # Create call entry
        call_entry = {
            'timestamp': datetime.now().isoformat(),
            'model_key': model_key,
            'model_name': MODELS[model_key]['display_name'],
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'total_tokens': input_tokens + output_tokens,
            'cost': cost,
            'component': component,
            'query_preview': query[:100] if query else None,
            'response_preview': response[:100] if response else None
        }

        # Add to calls
        self.calls.append(call_entry)

        # Update stats
        date = call_entry['timestamp'][:10]
        month = call_entry['timestamp'][:7]

        self.daily_totals[date] += cost
        self.monthly_totals[month] += cost

        self.model_usage[model_key]['calls'] += 1
        self.model_usage[model_key]['cost'] += cost

        # Save log
        self._save_log()

        # Check budget
        current_month = datetime.now().strftime('%Y-%m')
        monthly_total = self.monthly_totals[current_month]

        if monthly_total > self.monthly_budget * self.alert_threshold:
            self._emit_budget_warning(monthly_total)

        return cost

    def _save_log(self):
        """Save cost log to JSON"""
        try:
            # Keep only last 10,000 calls (prevent unbounded growth)
            if len(self.calls) > 10000:
                self.calls = self.calls[-10000:]

            data = {
                'calls': self.calls,
                'last_updated': datetime.now().isoformat(),
                'total_calls': len(self.calls)
            }

            with open(COST_LOG, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"   ⚠️ Could not save cost log: {e}")

    def _emit_budget_warning(self, current_total: float):
        """Emit budget warning"""
        percent = (current_total / self.monthly_budget) * 100
        remaining = self.monthly_budget - current_total

        print()
        print("="*70)
        print("⚠️ BUDGET WARNING")
        print("="*70)
        print(f"Current month spending: ${current_total:.2f}")
        print(f"Monthly budget: ${self.monthly_budget:.2f}")
        print(f"Budget used: {percent:.1f}%")
        print(f"Remaining: ${remaining:.2f}")

        if current_total > self.monthly_budget:
            print()
            print("🚨 BUDGET EXCEEDED!")
            if self.auto_downgrade:
                print("   Auto-downgrade ENABLED - switching to cheaper models")
        elif percent > 90:
            print()
            print("🔴 Critical: 90%+ of budget used!")
        elif percent > 80:
            print()
            print("🟡 Warning: 80%+ of budget used")

        print("="*70)
        print()

    def get_today_cost(self) -> float:
        """Get today's total cost"""
        today = datetime.now().strftime('%Y-%m-%d')
        return self.daily_totals[today]

    def get_month_cost(self) -> float:
        """Get current month's total cost"""
        current_month = datetime.now().strftime('%Y-%m')
        return self.monthly_totals[current_month]

    def get_budget_status(self) -> Dict[str, Any]:
        """Get budget status"""
        current_month = datetime.now().strftime('%Y-%m')
        monthly_total = self.monthly_totals[current_month]

        percent_used = (monthly_total / self.monthly_budget) * 100
        remaining = self.monthly_budget - monthly_total

        status = 'ok'
        if monthly_total > self.monthly_budget:
            status = 'exceeded'
        elif percent_used > 90:
            status = 'critical'
        elif percent_used > 80:
            status = 'warning'

        return {
            'current_spending': monthly_total,
            'budget': self.monthly_budget,
            'remaining': remaining,
            'percent_used': percent_used,
            'status': status,
            'auto_downgrade_enabled': self.auto_downgrade
        }

    def get_model_breakdown(self) -> Dict[str, Dict]:
        """Get cost breakdown per model"""
        breakdown = {}

        for model_key, stats in self.model_usage.items():
            if model_key in MODELS:
                breakdown[model_key] = {
                    'display_name': MODELS[model_key]['display_name'],
                    'calls': stats['calls'],
                    'total_cost': stats['cost'],
                    'avg_cost_per_call': stats['cost'] / stats['calls'] if stats['calls'] > 0 else 0.0
                }

        return breakdown

    def get_daily_trend(self, days: int = 7) -> Dict[str, float]:
        """Get daily cost trend for last N days"""
        trend = {}

        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            trend[date] = self.daily_totals.get(date, 0.0)

        return dict(sorted(trend.items()))

    def should_downgrade(self) -> bool:
        """Check if system should downgrade to cheaper models"""
        if not self.auto_downgrade:
            return False

        current_month = datetime.now().strftime('%Y-%m')
        monthly_total = self.monthly_totals[current_month]

        return monthly_total > self.monthly_budget

    def generate_report(self, verbose: bool = True) -> Dict[str, Any]:
        """Generate cost report"""

        report = {
            'today': {
                'cost': self.get_today_cost(),
                'calls': len([c for c in self.calls if c['timestamp'][:10] == datetime.now().strftime('%Y-%m-%d')])
            },
            'month': {
                'cost': self.get_month_cost(),
                'calls': len([c for c in self.calls if c['timestamp'][:7] == datetime.now().strftime('%Y-%m')])
            },
            'budget_status': self.get_budget_status(),
            'model_breakdown': self.get_model_breakdown(),
            'daily_trend': self.get_daily_trend(7),
            'total_calls': len(self.calls)
        }

        if verbose:
            self._print_report(report)

        return report

    def _print_report(self, report: Dict):
        """Print formatted cost report"""

        print()
        print("="*70)
        print("💰 AIKI COST REPORT")
        print("="*70)
        print()

        # Today
        print(f"📅 Today:")
        print(f"   Cost: ${report['today']['cost']:.4f}")
        print(f"   Calls: {report['today']['calls']}")
        print()

        # Month
        print(f"📊 This Month:")
        print(f"   Cost: ${report['month']['cost']:.2f}")
        print(f"   Calls: {report['month']['calls']}")
        print()

        # Budget
        budget = report['budget_status']
        print(f"💵 Budget Status:")
        print(f"   Spent: ${budget['current_spending']:.2f} / ${budget['budget']:.2f}")
        print(f"   Used: {budget['percent_used']:.1f}%")
        print(f"   Remaining: ${budget['remaining']:.2f}")

        if budget['status'] == 'exceeded':
            print(f"   Status: 🚨 EXCEEDED")
        elif budget['status'] == 'critical':
            print(f"   Status: 🔴 Critical (90%+)")
        elif budget['status'] == 'warning':
            print(f"   Status: 🟡 Warning (80%+)")
        else:
            print(f"   Status: ✅ OK")
        print()

        # Model breakdown
        print(f"🤖 Model Breakdown:")
        for model_key, stats in report['model_breakdown'].items():
            print(f"   {stats['display_name']}:")
            print(f"     Calls: {stats['calls']}")
            print(f"     Total: ${stats['total_cost']:.4f}")
            print(f"     Avg: ${stats['avg_cost_per_call']:.6f}/call")
        print()

        # Daily trend
        print(f"📈 Daily Trend (Last 7 Days):")
        for date, cost in list(report['daily_trend'].items())[-7:]:
            print(f"   {date}: ${cost:.4f}")
        print()

        print("="*70)
        print()


# ════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ════════════════════════════════════════════════════════════════════

# Global cost tracker instance
_global_tracker = None

def get_tracker() -> CostTracker:
    """Get global cost tracker instance"""
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = CostTracker()
    return _global_tracker


# ════════════════════════════════════════════════════════════════════
# QUICK TEST
# ════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("💰 AIKI Cost Tracker - Test")
    print("="*60)
    print()

    tracker = CostTracker()

    # Simulate some API calls
    print("Simulating API calls...")

    tracker.log_call('haiku', 500, 200, 'Test query 1', component='test')
    tracker.log_call('sonnet', 1000, 500, 'Test query 2', component='test')
    tracker.log_call('opus', 2000, 1000, 'Test query 3', component='test')

    print()

    # Generate report
    tracker.generate_report(verbose=True)
