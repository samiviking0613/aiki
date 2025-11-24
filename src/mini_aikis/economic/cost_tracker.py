#!/usr/bin/env python3
"""
MINI-AIKI 3: COST TRACKER

Purpose: "Monitor and alert on budget status"

Strategy:
- Track real-time costs per component
- Predict budget overrun risk
- Alert when approaching limits (80%, 90%, 100%)
- Suggest cost-saving optimizations

Responsibilities:
- Monitor daily/monthly costs
- Track cost per model, per Circle, per mini-AIKI
- Predict end-of-day/month costs
- Alert on budget approach
- Recommend throttling strategies
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime, timezone, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.mini_aikis.base_mini_aiki import BaseMiniAiki, MiniAikiTask


class CostTracker(BaseMiniAiki):
    """
    Cost Tracker - Monitors budget status and alerts

    Proactive cost monitoring with predictive alerts.
    Helps prevent budget overruns.
    """

    def __init__(self):
        super().__init__(
            mini_id="mini_3_cost_tracker",
            purpose="Monitor and alert on budget status",
            parent_circle="economic",
            responsibilities=[
                "Track real-time costs (daily/monthly)",
                "Monitor cost per component",
                "Predict budget overrun risk",
                "Alert at 80%, 90%, 100% thresholds",
                "Recommend cost-saving actions"
            ]
        )

        # Cost data
        self.daily_budget = 500.0  # NOK
        self.monthly_budget = 3000.0  # NOK
        self.current_daily_cost = 0.0
        self.current_monthly_cost = 0.0

        # Cost breakdown
        self.costs_by_component: Dict[str, float] = {}
        self.costs_by_model: Dict[str, float] = {}

        # Alerts
        self.alert_thresholds = [0.8, 0.9, 1.0]  # 80%, 90%, 100%
        self.alerts_sent = set()

        # Metrics
        self.metrics = {
            'total_costs_tracked': 0.0,
            'daily_pct_used': 0.0,
            'monthly_pct_used': 0.0,
            'alerts_triggered': 0,
            'predicted_eod_cost': 0.0,
            'risk_level': 'low'  # low, medium, high, critical
        }

    async def _execute_task(self, task: MiniAikiTask) -> Any:
        """
        Execute cost tracking task

        Input: {
            'action': 'record_cost' | 'get_status' | 'predict_overrun',
            'amount': float,
            'component': str,
            'model': str
        }
        Output: Depends on action
        """
        action = task.input_data.get('action', 'get_status')

        if action == 'record_cost':
            return await self._record_cost(task.input_data)
        elif action == 'get_status':
            return self._get_cost_status()
        elif action == 'predict_overrun':
            return self._predict_overrun()
        else:
            return {'error': f'Unknown action: {action}'}

    async def _record_cost(self, data: Dict) -> Dict:
        """Record a cost"""
        amount = data.get('amount', 0.0)
        component = data.get('component', 'unknown')
        model = data.get('model', 'unknown')

        # Update totals
        self.current_daily_cost += amount
        self.current_monthly_cost += amount

        # Update breakdowns
        self.costs_by_component[component] = self.costs_by_component.get(component, 0.0) + amount
        self.costs_by_model[model] = self.costs_by_model.get(model, 0.0) + amount

        # Update metrics
        self.metrics['total_costs_tracked'] += amount
        self.metrics['daily_pct_used'] = (self.current_daily_cost / self.daily_budget) * 100
        self.metrics['monthly_pct_used'] = (self.current_monthly_cost / self.monthly_budget) * 100

        # Check for alerts
        alerts = await self._check_alerts()

        # Update risk level
        self.metrics['risk_level'] = self._calculate_risk_level()

        return {
            'cost_recorded': amount,
            'daily_total': self.current_daily_cost,
            'monthly_total': self.current_monthly_cost,
            'alerts': alerts
        }

    def _get_cost_status(self) -> Dict:
        """Get current cost status"""
        return {
            'daily': {
                'current': self.current_daily_cost,
                'budget': self.daily_budget,
                'pct_used': self.metrics['daily_pct_used']
            },
            'monthly': {
                'current': self.current_monthly_cost,
                'budget': self.monthly_budget,
                'pct_used': self.metrics['monthly_pct_used']
            },
            'by_component': self.costs_by_component,
            'by_model': self.costs_by_model,
            'risk_level': self.metrics['risk_level'],
            'alerts_triggered': self.metrics['alerts_triggered']
        }

    def _predict_overrun(self) -> Dict:
        """Predict if we'll exceed budget"""
        # Simple prediction: project current rate to end of day/month
        now = datetime.now()
        hour_of_day = now.hour
        hours_remaining = 24 - hour_of_day

        if hour_of_day > 0:
            hourly_rate = self.current_daily_cost / hour_of_day
            predicted_eod = self.current_daily_cost + (hourly_rate * hours_remaining)
        else:
            predicted_eod = self.current_daily_cost

        self.metrics['predicted_eod_cost'] = predicted_eod

        return {
            'predicted_eod_cost': predicted_eod,
            'daily_budget': self.daily_budget,
            'overrun_risk': predicted_eod > self.daily_budget,
            'overrun_amount': max(0, predicted_eod - self.daily_budget),
            'recommendation': self._get_recommendation(predicted_eod)
        }

    async def _check_alerts(self) -> List[str]:
        """Check if any alert thresholds crossed"""
        alerts = []
        daily_pct = self.metrics['daily_pct_used'] / 100

        for threshold in self.alert_thresholds:
            alert_key = f"daily_{threshold}"
            if daily_pct >= threshold and alert_key not in self.alerts_sent:
                alerts.append(f"⚠️ Daily budget {threshold*100:.0f}% used ({self.current_daily_cost:.2f} / {self.daily_budget:.2f} NOK)")
                self.alerts_sent.add(alert_key)
                self.metrics['alerts_triggered'] += 1

        return alerts

    def _calculate_risk_level(self) -> str:
        """Calculate risk level based on cost status"""
        daily_pct = self.metrics['daily_pct_used']

        if daily_pct >= 100:
            return 'critical'
        elif daily_pct >= 90:
            return 'high'
        elif daily_pct >= 80:
            return 'medium'
        else:
            return 'low'

    def _get_recommendation(self, predicted_eod: float) -> str:
        """Get cost-saving recommendation"""
        if predicted_eod > self.daily_budget:
            overrun_pct = ((predicted_eod - self.daily_budget) / self.daily_budget) * 100
            if overrun_pct > 20:
                return "Switch to Haiku-only mode for rest of day"
            elif overrun_pct > 10:
                return "Avoid Opus, prefer Sonnet/Haiku"
            else:
                return "Monitor closely, reduce Sonnet usage"
        else:
            return "No action needed, within budget"


async def main():
    """Test Cost Tracker"""
    tracker = CostTracker()

    # Record some costs
    task1 = await tracker.assign_task(
        task_type='cost_tracking',
        description='Record Haiku cost',
        input_data={
            'action': 'record_cost',
            'amount': 50.0,
            'component': 'economic_circle',
            'model': 'haiku-4.5'
        }
    )

    task2 = await tracker.assign_task(
        task_type='cost_tracking',
        description='Record Sonnet cost',
        input_data={
            'action': 'record_cost',
            'amount': 200.0,
            'component': 'learning_circle',
            'model': 'sonnet-4.5'
        }
    )

    task3 = await tracker.assign_task(
        task_type='cost_tracking',
        description='Record Opus cost',
        input_data={
            'action': 'record_cost',
            'amount': 300.0,
            'component': 'social_circle',
            'model': 'opus-4'
        }
    )

    # Process
    await tracker._process_tasks()

    # Get results
    result1 = tracker.get_task_result(task1)
    result2 = tracker.get_task_result(task2)
    result3 = tracker.get_task_result(task3)

    print(f"\nCost recording results:")
    print(f"Haiku: {result1}")
    print(f"Sonnet: {result2}")
    print(f"Opus: {result3}")

    # Get status
    task_status = await tracker.assign_task(
        task_type='cost_tracking',
        description='Get cost status',
        input_data={'action': 'get_status'}
    )
    await tracker._process_tasks()
    status = tracker.get_task_result(task_status)
    print(f"\nCost status: {status}")

    # Predict overrun
    task_predict = await tracker.assign_task(
        task_type='cost_tracking',
        description='Predict overrun',
        input_data={'action': 'predict_overrun'}
    )
    await tracker._process_tasks()
    prediction = tracker.get_task_result(task_predict)
    print(f"\nOverrun prediction: {prediction}")


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
