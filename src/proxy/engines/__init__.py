"""
AIKI Traffic Intelligence Platform - Engines Package
=====================================================

Verdens mest kompliserte MITM proxy engines!

Layers:
1. TLS Fingerprinting (JA3/JA4)
2. ML App Classification
3. Behavioral Analytics
4. Content Intelligence
5. Active Intervention
6. Federation Protocol
"""

from .tls_fingerprint import TLSFingerprintEngine, get_engine as create_fingerprint_engine
from .app_classifier import (
    AppClassifierEngine,
    AppCategory,
    AddictionRisk,
    TrafficSample,
    AppClassification,
    create_classifier,
    classify_connection
)
from .behavioral_analytics import (
    BehavioralAnalyticsEngine,
    BehaviorState,
    AlertLevel,
    SessionMetrics,
    BehaviorAlert,
    DopamineLoopDetector,
    FocusTracker,
    create_analytics_engine
)
from .content_intelligence import (
    ContentIntelligenceEngine,
    ContentType,
    ContentCategory,
    EngagementTactic,
    DarkPattern,
    ContentAnalysis,
    create_content_intelligence
)
from .active_intervention import (
    ActiveInterventionEngine,
    InterventionType,
    InterventionTrigger,
    EducationalContent,
    UserQuota,
    BossBattle,
    TikTokInjector,
    create_intervention_engine
)
from .federation import (
    FederationEngine,
    NodeRole,
    MessageType,
    FederationNode,
    FederationMessage,
    AnonymizedStats,
    PatternAlert,
    create_federation_engine
)
from .app_throttler import (
    AppThrottler,
    ThrottleLevel,
    ThrottleReason,
    ThrottleConfig,
    ThrottleStats,
    DeviceProfile,
    TikTokThrottler,
    create_throttler
)

__all__ = [
    # TLS Fingerprinting
    'TLSFingerprintEngine',
    'create_fingerprint_engine',

    # App Classification
    'AppClassifierEngine',
    'AppCategory',
    'AddictionRisk',
    'TrafficSample',
    'AppClassification',
    'create_classifier',
    'classify_connection',

    # Behavioral Analytics
    'BehavioralAnalyticsEngine',
    'BehaviorState',
    'AlertLevel',
    'SessionMetrics',
    'BehaviorAlert',
    'DopamineLoopDetector',
    'FocusTracker',
    'create_analytics_engine',

    # Content Intelligence
    'ContentIntelligenceEngine',
    'ContentType',
    'ContentCategory',
    'EngagementTactic',
    'DarkPattern',
    'ContentAnalysis',
    'create_content_intelligence',

    # Active Intervention
    'ActiveInterventionEngine',
    'InterventionType',
    'InterventionTrigger',
    'EducationalContent',
    'UserQuota',
    'BossBattle',
    'TikTokInjector',
    'create_intervention_engine',

    # Federation
    'FederationEngine',
    'NodeRole',
    'MessageType',
    'FederationNode',
    'FederationMessage',
    'AnonymizedStats',
    'PatternAlert',
    'create_federation_engine',

    # App Throttler
    'AppThrottler',
    'ThrottleLevel',
    'ThrottleReason',
    'ThrottleConfig',
    'ThrottleStats',
    'DeviceProfile',
    'TikTokThrottler',
    'create_throttler',
]

__version__ = '1.0.0'
__author__ = 'AIKI / Jovnna'
