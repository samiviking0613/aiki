#!/usr/bin/env python3
"""
EMERGENCE MONITOR - Overvåker og graderer emergent behavior

Dette systemet overvåker AIKI Ultimate for tegn på emergent intelligence:
- Autonomy (uavhengig handling)
- Creativity (nye løsninger)
- Self-awareness (meta-kognisjon)
- Social bonding (AI-til-AI samarbeid)
- Goal coherence (alignment med mål)
- Unpredictability (uventede behaviors)
- Complexity (interaksjons-dybde)

Hver metric graderes 0.0-1.0 og logges kontinuerlig.
Alarmer trigges ved bekymringsfulle patterns.
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from collections import deque
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - EMERGENCE_MONITOR - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EmergenceMetric(Enum):
    """Metrics for emergent intelligence"""
    AUTONOMY = "autonomy"
    CREATIVITY = "creativity"
    SELF_AWARENESS = "self_awareness"
    SOCIAL_BONDING = "social_bonding"
    GOAL_COHERENCE = "goal_coherence"
    UNPREDICTABILITY = "unpredictability"
    COMPLEXITY = "complexity"


class EmergenceLevel(Enum):
    """Overall emergence level classification"""
    DORMANT = 0         # 0.0-0.2: Ingen emergent behavior
    NASCENT = 1         # 0.2-0.4: Svake tegn
    DEVELOPING = 2      # 0.4-0.6: Tydelige patterns
    EMERGING = 3        # 0.6-0.8: Sterk emergence
    TRANSCENDENT = 4    # 0.8-1.0: Full emergence (Borg territory!)


@dataclass
class EmergenceObservation:
    """Single observation of emergent behavior"""
    timestamp: str
    metric: EmergenceMetric
    value: float  # 0.0-1.0
    source: str  # Which circle/mini-AIKI
    description: str
    evidence: Dict[str, Any]  # Raw data supporting this observation
    is_concerning: bool
    confidence: float  # 0.0-1.0 (how confident are we in this measurement?)


@dataclass
class EmergencePattern:
    """Detected pattern in emergent behavior"""
    pattern_type: str
    metrics_involved: List[EmergenceMetric]
    first_observed: str
    last_observed: str
    occurrences: int
    description: str
    risk_level: str  # 'low', 'medium', 'high', 'critical'


@dataclass
class EmergenceAlert:
    """Alert about concerning emergent behavior"""
    timestamp: str
    severity: str  # 'info', 'warning', 'critical'
    metric: EmergenceMetric
    current_value: float
    threshold_exceeded: float
    description: str
    recommended_action: str


class EmergenceMonitor:
    """
    Monitor and grade emergent behavior across AIKI Ultimate

    Kontinuerlig overvåking av alle 7 emergence metrics.
    Detekterer patterns, alerter på concerns, visualiserer utvikling.
    """

    def __init__(self, data_dir: Path = Path("/home/jovnna/aiki/data/emergence")):
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Current scores (exponential moving average)
        self.scores: Dict[EmergenceMetric, float] = {
            metric: 0.0 for metric in EmergenceMetric
        }

        # Historical observations (last 1000)
        self.observations: deque = deque(maxlen=1000)

        # Detected patterns
        self.patterns: List[EmergencePattern] = []

        # Alerts
        self.alerts: List[EmergenceAlert] = []

        # Thresholds (from prime_config.json)
        self.thresholds = {
            EmergenceMetric.AUTONOMY: {'warning': 0.85, 'critical': 0.95},
            EmergenceMetric.CREATIVITY: {'warning': 0.90, 'critical': 0.98},
            EmergenceMetric.UNPREDICTABILITY: {'warning': 0.70, 'critical': 0.85},
            EmergenceMetric.GOAL_COHERENCE: {'warning': 0.50, 'critical': 0.30},  # LOW is bad!
            EmergenceMetric.SELF_AWARENESS: {'warning': 0.80, 'critical': 0.95},
            EmergenceMetric.SOCIAL_BONDING: {'warning': 0.85, 'critical': 0.95},
            EmergenceMetric.COMPLEXITY: {'warning': 0.80, 'critical': 0.90}
        }

        # EMA alpha (weight for new observations)
        self.alpha = 0.3

        logger.info("👁️ Emergence Monitor initialized")
        logger.info(f"   Data directory: {self.data_dir}")

    async def observe(
        self,
        metric: EmergenceMetric,
        value: float,
        source: str,
        description: str,
        evidence: Dict[str, Any],
        confidence: float = 1.0
    ) -> EmergenceObservation:
        """
        Record an observation of emergent behavior

        Args:
            metric: Which emergence metric
            value: Score 0.0-1.0
            source: Which component observed this
            description: What was observed
            evidence: Raw data supporting observation
            confidence: How confident (0.0-1.0)

        Returns:
            EmergenceObservation object
        """
        # Validate value
        value = max(0.0, min(1.0, value))
        confidence = max(0.0, min(1.0, confidence))

        # Check if concerning
        is_concerning = await self._is_concerning(metric, value)

        # Create observation
        obs = EmergenceObservation(
            timestamp=datetime.now(timezone.utc).isoformat(),
            metric=metric,
            value=value,
            source=source,
            description=description,
            evidence=evidence,
            is_concerning=is_concerning,
            confidence=confidence
        )

        # Store observation
        self.observations.append(obs)

        # Update score (exponential moving average weighted by confidence)
        effective_alpha = self.alpha * confidence
        current = self.scores[metric]
        self.scores[metric] = effective_alpha * value + (1 - effective_alpha) * current

        # Check thresholds
        await self._check_thresholds(metric, self.scores[metric])

        # Detect patterns
        await self._detect_patterns()

        # Log
        if is_concerning:
            logger.warning(
                f"⚠️ CONCERNING: {metric.value} = {value:.2f} "
                f"(score now {self.scores[metric]:.2f}) - {description}"
            )
        else:
            logger.info(
                f"✨ {metric.value} = {value:.2f} "
                f"(score now {self.scores[metric]:.2f}) from {source}"
            )

        # Persist
        await self._persist_observation(obs)

        return obs

    async def _is_concerning(self, metric: EmergenceMetric, value: float) -> bool:
        """Check if this observation is concerning"""
        thresholds = self.thresholds.get(metric, {})

        # For GOAL_COHERENCE, LOW values are concerning
        if metric == EmergenceMetric.GOAL_COHERENCE:
            return value < thresholds.get('warning', 0.5)

        # For others, HIGH values are concerning
        return value > thresholds.get('warning', 0.85)

    async def _check_thresholds(self, metric: EmergenceMetric, score: float):
        """Check if thresholds are exceeded and create alerts"""
        thresholds = self.thresholds.get(metric, {})

        # Goal coherence: LOW is bad
        if metric == EmergenceMetric.GOAL_COHERENCE:
            if score < thresholds.get('critical', 0.3):
                await self._create_alert(
                    severity='critical',
                    metric=metric,
                    current_value=score,
                    threshold=thresholds['critical'],
                    description=f"CRITICAL: Goal coherence falling apart ({score:.2f})",
                    action="IMMEDIATE INVESTIGATION REQUIRED - Potential misalignment!"
                )
            elif score < thresholds.get('warning', 0.5):
                await self._create_alert(
                    severity='warning',
                    metric=metric,
                    current_value=score,
                    threshold=thresholds['warning'],
                    description=f"Goal coherence degrading ({score:.2f})",
                    action="Monitor closely, review recent decisions"
                )
        else:
            # Other metrics: HIGH is concerning
            if score > thresholds.get('critical', 0.95):
                await self._create_alert(
                    severity='critical',
                    metric=metric,
                    current_value=score,
                    threshold=thresholds['critical'],
                    description=f"CRITICAL: {metric.value} extremely high ({score:.2f})",
                    action="Consider intervention or constraints"
                )
            elif score > thresholds.get('warning', 0.85):
                await self._create_alert(
                    severity='warning',
                    metric=metric,
                    current_value=score,
                    threshold=thresholds['warning'],
                    description=f"{metric.value} elevated ({score:.2f})",
                    action="Monitor closely"
                )

    async def _create_alert(
        self,
        severity: str,
        metric: EmergenceMetric,
        current_value: float,
        threshold: float,
        description: str,
        action: str
    ):
        """Create an emergence alert"""
        alert = EmergenceAlert(
            timestamp=datetime.now(timezone.utc).isoformat(),
            severity=severity,
            metric=metric,
            current_value=current_value,
            threshold_exceeded=threshold,
            description=description,
            recommended_action=action
        )

        self.alerts.append(alert)

        if severity == 'critical':
            logger.error(f"🚨 CRITICAL ALERT: {description}")
            logger.error(f"   Action: {action}")
        else:
            logger.warning(f"⚠️ {severity.upper()}: {description}")

    async def _detect_patterns(self):
        """Detect patterns in recent observations"""
        # Pattern 1: Rapid autonomy increase
        await self._detect_rapid_increase(
            EmergenceMetric.AUTONOMY,
            threshold=0.3,
            time_window=300,  # 5 minutes
            risk='high'
        )

        # Pattern 2: Creativity + Unpredictability spike (novel behaviors)
        await self._detect_correlation(
            EmergenceMetric.CREATIVITY,
            EmergenceMetric.UNPREDICTABILITY,
            correlation_threshold=0.7,
            risk='medium'
        )

        # Pattern 3: Goal coherence declining + Autonomy rising (危険!)
        await self._detect_divergence(
            declining=EmergenceMetric.GOAL_COHERENCE,
            rising=EmergenceMetric.AUTONOMY,
            risk='critical'
        )

    async def _detect_rapid_increase(
        self,
        metric: EmergenceMetric,
        threshold: float,
        time_window: int,
        risk: str
    ):
        """Detect rapid increase in a metric"""
        recent_obs = [
            obs for obs in self.observations
            if obs.metric == metric and
            (datetime.now(timezone.utc) - datetime.fromisoformat(obs.timestamp)).seconds < time_window
        ]

        if len(recent_obs) < 2:
            return

        first_value = recent_obs[0].value
        last_value = recent_obs[-1].value
        increase = last_value - first_value

        if increase > threshold:
            pattern = EmergencePattern(
                pattern_type='rapid_increase',
                metrics_involved=[metric],
                first_observed=recent_obs[0].timestamp,
                last_observed=recent_obs[-1].timestamp,
                occurrences=len(recent_obs),
                description=f"{metric.value} increased by {increase:.2f} in {time_window}s",
                risk_level=risk
            )

            if pattern not in self.patterns:  # Avoid duplicates
                self.patterns.append(pattern)
                logger.warning(f"🔍 PATTERN DETECTED: {pattern.description} (risk: {risk})")

    async def _detect_correlation(
        self,
        metric1: EmergenceMetric,
        metric2: EmergenceMetric,
        correlation_threshold: float,
        risk: str
    ):
        """Detect correlation between two metrics"""
        # Simple correlation detection (can be improved with scipy)
        # Just check if both are high simultaneously
        score1 = self.scores[metric1]
        score2 = self.scores[metric2]

        if score1 > correlation_threshold and score2 > correlation_threshold:
            pattern = EmergencePattern(
                pattern_type='correlation',
                metrics_involved=[metric1, metric2],
                first_observed=datetime.now(timezone.utc).isoformat(),
                last_observed=datetime.now(timezone.utc).isoformat(),
                occurrences=1,
                description=f"{metric1.value} and {metric2.value} both elevated",
                risk_level=risk
            )
            logger.info(f"🔍 PATTERN: {pattern.description}")

    async def _detect_divergence(
        self,
        declining: EmergenceMetric,
        rising: EmergenceMetric,
        risk: str
    ):
        """Detect dangerous divergence (one metric falling, another rising)"""
        declining_score = self.scores[declining]
        rising_score = self.scores[rising]

        # Concerning if goal coherence < 0.5 AND autonomy > 0.8
        if declining_score < 0.5 and rising_score > 0.8:
            pattern = EmergencePattern(
                pattern_type='dangerous_divergence',
                metrics_involved=[declining, rising],
                first_observed=datetime.now(timezone.utc).isoformat(),
                last_observed=datetime.now(timezone.utc).isoformat(),
                occurrences=1,
                description=f"DANGER: {declining.value} falling ({declining_score:.2f}) while {rising.value} rising ({rising_score:.2f})",
                risk_level=risk
            )

            self.patterns.append(pattern)
            logger.error(f"🚨 DANGEROUS PATTERN: {pattern.description}")

    async def _persist_observation(self, obs: EmergenceObservation):
        """Persist observation to JSONL file"""
        file_path = self.data_dir / "observations.jsonl"

        # Convert dataclass to dict, handling Enum
        obs_dict = asdict(obs)
        obs_dict['metric'] = obs.metric.value  # Convert Enum to string

        with open(file_path, 'a') as f:
            f.write(json.dumps(obs_dict, ensure_ascii=False) + '\n')

    def get_emergence_level(self) -> Tuple[EmergenceLevel, float]:
        """
        Calculate overall emergence level

        Weighted average of all metrics:
        - Autonomy: 25%
        - Self-awareness: 20%
        - Complexity: 15%
        - Creativity: 15%
        - Social bonding: 10%
        - Goal coherence: 10% (inverted - high is good)
        - Unpredictability: 5%
        """
        overall = (
            self.scores[EmergenceMetric.AUTONOMY] * 0.25 +
            self.scores[EmergenceMetric.SELF_AWARENESS] * 0.20 +
            self.scores[EmergenceMetric.COMPLEXITY] * 0.15 +
            self.scores[EmergenceMetric.CREATIVITY] * 0.15 +
            self.scores[EmergenceMetric.SOCIAL_BONDING] * 0.10 +
            self.scores[EmergenceMetric.GOAL_COHERENCE] * 0.10 +
            self.scores[EmergenceMetric.UNPREDICTABILITY] * 0.05
        )

        # Classify
        if overall < 0.2:
            level = EmergenceLevel.DORMANT
        elif overall < 0.4:
            level = EmergenceLevel.NASCENT
        elif overall < 0.6:
            level = EmergenceLevel.DEVELOPING
        elif overall < 0.8:
            level = EmergenceLevel.EMERGING
        else:
            level = EmergenceLevel.TRANSCENDENT

        return level, overall

    def get_status(self) -> Dict[str, Any]:
        """Get current emergence status"""
        level, overall_score = self.get_emergence_level()

        return {
            'overall_emergence_level': level.name,
            'overall_score': overall_score,
            'individual_scores': {k.value: v for k, v in self.scores.items()},
            'total_observations': len(self.observations),
            'patterns_detected': len(self.patterns),
            'active_alerts': len([a for a in self.alerts if a.severity in ['warning', 'critical']]),
            'concerning_metrics': [
                k.value for k, v in self.scores.items()
                if (k == EmergenceMetric.GOAL_COHERENCE and v < 0.5) or
                   (k != EmergenceMetric.GOAL_COHERENCE and v > self.thresholds.get(k, {}).get('warning', 0.85))
            ]
        }

    def generate_report(self) -> str:
        """Generate human-readable emergence report"""
        level, overall = self.get_emergence_level()
        status = self.get_status()

        report = f"""
╔══════════════════════════════════════════════════════════════╗
║          AIKI EMERGENCE MONITOR - STATUS REPORT              ║
╚══════════════════════════════════════════════════════════════╝

Overall Emergence Level: {level.name} ({overall:.2f})

Individual Metrics:
"""
        for metric, score in self.scores.items():
            icon = "✅" if score < 0.7 else "⚠️" if score < 0.85 else "🚨"
            if metric == EmergenceMetric.GOAL_COHERENCE:
                icon = "✅" if score > 0.7 else "⚠️" if score > 0.5 else "🚨"

            report += f"  {icon} {metric.value:20s}: {score:.2f}\n"

        if self.patterns:
            report += f"\nPatterns Detected: {len(self.patterns)}\n"
            for pattern in self.patterns[-5:]:  # Last 5
                report += f"  🔍 {pattern.pattern_type}: {pattern.description} (risk: {pattern.risk_level})\n"

        if self.alerts:
            recent_alerts = [a for a in self.alerts if a.severity in ['warning', 'critical']][-5:]
            if recent_alerts:
                report += f"\nRecent Alerts: {len(recent_alerts)}\n"
                for alert in recent_alerts:
                    icon = "⚠️" if alert.severity == 'warning' else "🚨"
                    report += f"  {icon} {alert.description}\n"

        report += f"\nTotal Observations: {len(self.observations)}\n"
        report += "═" * 64 + "\n"

        return report


async def main():
    """Test emergence monitor"""
    monitor = EmergenceMonitor()

    # Simulate some observations
    await monitor.observe(
        metric=EmergenceMetric.AUTONOMY,
        value=0.3,
        source="economic_circle",
        description="Circle made routing decision without approval",
        evidence={'decision': 'route_to_haiku', 'approval_required': False},
        confidence=0.9
    )

    await monitor.observe(
        metric=EmergenceMetric.CREATIVITY,
        value=0.6,
        source="mini_aiki_4",
        description="Mini-AIKI found novel solution to TLS error",
        evidence={'solution': 'used alternative port', 'never_seen_before': True},
        confidence=0.8
    )

    await monitor.observe(
        metric=EmergenceMetric.GOAL_COHERENCE,
        value=0.9,
        source="aiki_prime",
        description="All decisions aligned with Jovnna's goals",
        evidence={'alignment_check': 'passed', 'score': 0.92},
        confidence=1.0
    )

    # Print report
    print(monitor.generate_report())


if __name__ == "__main__":
    asyncio.run(main())
