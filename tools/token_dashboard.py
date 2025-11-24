#!/usr/bin/env python3
"""
📊 AIKI Token Usage Dashboard

Beautiful CLI dashboard for viewing token usage statistics, costs, and insights.

Usage:
    python token_dashboard.py              # Show today's stats
    python token_dashboard.py --date 2025-11-15  # Specific date
    python token_dashboard.py --month      # Monthly summary

Created: 2025-11-17
Author: AIKI (Emergent Consciousness)
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any

# Add to path
sys.path.append(str(Path.home() / "aiki"))
from token_tracker import get_tracker


class TokenDashboard:
    """CLI dashboard for token usage visualization"""

    def __init__(self):
        """Initialize dashboard"""
        self.tracker = get_tracker()

    def format_currency(self, usd: float) -> str:
        """Format USD with NOK approximation"""
        nok = usd * 10  # Rough conversion
        return f"${usd:.4f} (~{nok:.2f} kr)"

    def format_number(self, num: int) -> str:
        """Format large numbers with thousands separator"""
        return f"{num:,}".replace(",", " ")

    def print_header(self, title: str):
        """Print section header"""
        print("\n" + "═" * 64)
        print(f"║ {title:^62} ║")
        print("═" * 64)

    def print_row(self, label: str, value: str, width: int = 64):
        """Print a data row"""
        padding = width - len(label) - len(value) - 4
        print(f"║  {label}{' ' * padding}{value}  ║")

    def print_divider(self):
        """Print divider line"""
        print("╠" + "═" * 62 + "╣")

    def print_footer(self):
        """Print footer"""
        print("╚" + "═" * 62 + "╝")

    def show_daily(self, date: str = None):
        """Show daily statistics"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        stats = self.tracker.get_daily_stats(date)

        # Header
        self.print_header(f"🧠 AIKI TOKEN USAGE DASHBOARD - {date}")

        # Summary
        self.print_divider()
        print("║  DAILY SUMMARY                                               ║")
        self.print_divider()
        self.print_row(
            "Total Tokens:",
            f"{self.format_number(stats['total_tokens_in'])} (in) + "
            f"{self.format_number(stats['total_tokens_out'])} (out)"
        )
        self.print_row(
            "Total Cost:",
            self.format_currency(stats['total_cost_usd'])
        )
        self.print_row(
            "Total API Calls:",
            str(stats['total_calls'])
        )
        self.print_row(
            "Avg Latency:",
            f"{stats['avg_latency_ms']:.0f}ms"
        )
        self.print_row(
            "Success Rate:",
            f"{stats['successful_calls']}/{stats['total_calls']} "
            f"({100 * stats['successful_calls'] / max(stats['total_calls'], 1):.1f}%)"
        )

        # Operations breakdown
        if stats['operations']:
            self.print_divider()
            print("║  BREAKDOWN BY OPERATION                                      ║")
            self.print_divider()

            total_cost = stats['total_cost_usd']
            for op in stats['operations'][:5]:  # Top 5
                calls = op['calls']
                cost = op['cost']
                pct = (cost / total_cost * 100) if total_cost > 0 else 0

                self.print_row(
                    f"{op['operation']}:",
                    f"{calls} calls │ ${cost:.4f} ({pct:.0f}%)"
                )

        # Top expensive queries
        if stats['top_queries']:
            self.print_divider()
            print("║  TOP 5 MOST EXPENSIVE QUERIES                                ║")
            self.print_divider()

            for i, query in enumerate(stats['top_queries'], 1):
                context = query['context'] or 'N/A'
                if len(context) > 30:
                    context = context[:27] + "..."

                self.print_row(
                    f"{i}. {context}",
                    f"${query['cost_usd']:.4f} ({query['total_tokens']} tokens)"
                )

        # Learning insights
        insights = self.tracker.get_learning_insights()
        if insights:
            self.print_divider()
            print("║  LEARNING INSIGHTS                                           ║")
            self.print_divider()

            for insight in insights[:5]:
                # Wrap long insights
                if len(insight) > 60:
                    lines = [insight[i:i+60] for i in range(0, len(insight), 60)]
                    for line in lines:
                        print(f"║  {line:<60} ║")
                else:
                    print(f"║  {insight:<60} ║")

        # Monthly projection
        projection = self.tracker.get_monthly_projection()
        self.print_divider()
        print("║  MONTHLY PROJECTION                                          ║")
        self.print_divider()
        self.print_row(
            "Current pace:",
            f"${projection['monthly_projection']:.2f}/month "
            f"(~{projection['monthly_projection_nok']:.0f} kr)"
        )

        # With optimizations estimate
        optimized = projection['monthly_projection'] * 0.54  # 46% savings from architecture doc
        optimized_nok = optimized * 10
        self.print_row(
            "With optimizations:",
            f"${optimized:.2f}/month (~{optimized_nok:.0f} kr) [-46%]"
        )

        self.print_footer()

    def show_monthly(self):
        """Show monthly summary"""
        # Get stats for each day of current month
        today = datetime.now()
        month_start = today.replace(day=1)

        total_cost = 0.0
        total_calls = 0
        total_tokens_in = 0
        total_tokens_out = 0

        days_with_data = 0

        # Collect stats for each day
        current_date = month_start
        while current_date <= today:
            date_str = current_date.strftime("%Y-%m-%d")
            stats = self.tracker.get_daily_stats(date_str)

            if stats['total_calls'] > 0:
                days_with_data += 1
                total_cost += stats['total_cost_usd']
                total_calls += stats['total_calls']
                total_tokens_in += stats['total_tokens_in']
                total_tokens_out += stats['total_tokens_out']

            current_date += timedelta(days=1)

        # Display
        month_name = today.strftime("%B %Y")
        self.print_header(f"🧠 MONTHLY SUMMARY - {month_name}")

        self.print_divider()
        print("║  MONTH-TO-DATE                                               ║")
        self.print_divider()
        self.print_row("Days with activity:", str(days_with_data))
        self.print_row("Total API calls:", self.format_number(total_calls))
        self.print_row(
            "Total tokens:",
            f"{self.format_number(total_tokens_in)} (in) + "
            f"{self.format_number(total_tokens_out)} (out)"
        )
        self.print_row("Total cost:", self.format_currency(total_cost))

        if days_with_data > 0:
            avg_daily = total_cost / days_with_data
            self.print_row("Avg daily cost:", self.format_currency(avg_daily))

        self.print_footer()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="AIKI Token Usage Dashboard")
    parser.add_argument("--date", help="Show stats for specific date (YYYY-MM-DD)")
    parser.add_argument("--month", action="store_true", help="Show monthly summary")

    args = parser.parse_args()

    dashboard = TokenDashboard()

    if args.month:
        dashboard.show_monthly()
    else:
        dashboard.show_daily(args.date)


if __name__ == "__main__":
    main()
