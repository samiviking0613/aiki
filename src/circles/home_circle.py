#!/usr/bin/env python3
"""
HOME CIRCLE - Federation Coordinator for AIKI-HOME Fleet

Purpose: "Coordinate AIKI-HOME installations while respecting privacy"

Denne circlen koordinerer alle AIKI-HOME installasjoner i federasjonen.
Den samler BARE metadata - aldri personlig data (GDPR-compliant).

Arkitektur-valg dokumentert i: docs/architecture/HOME_FEDERATION_ALTERNATIVES.md
"""

import asyncio
import sys
import hashlib
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.circles.base_circle import BaseCircle


class HomeStatus(Enum):
    """Status for et AIKI-HOME"""
    ONLINE = "online"
    OFFLINE = "offline"
    SETUP = "setup"          # Under oppstart
    DEGRADED = "degraded"    # Delvis funksjonell
    MAINTENANCE = "maintenance"


class ProfileType(Enum):
    """Anonymiserte brukerprofiler for pheromone-matching"""
    ADHD_ADULT_WFH = "adhd_adult_work_from_home"
    ADHD_ADULT_OFFICE = "adhd_adult_office"
    ADHD_TEEN_STUDENT = "adhd_teen_student"
    ADHD_CHILD = "adhd_child"
    FAMILY_MIXED = "family_mixed"
    GENERIC = "generic"


@dataclass
class HomeRegistration:
    """Registrering av et AIKI-HOME i federasjonen"""
    home_id: str  # Anonymisert hash
    profile_type: ProfileType
    registered_at: datetime
    last_seen: datetime
    status: HomeStatus
    software_version: str
    country: str = "NO"  # For ISP-matching

    # Aggregerte metrics (aldri personlig data!)
    total_rules_active: int = 0
    pheromone_contributions: int = 0


@dataclass
class PheromoneUpdate:
    """
    Pheromone-oppdatering fra et hjem

    VIKTIG: Inneholder BARE metadata, aldri personlig data!
    """
    home_id: str
    profile_type: ProfileType
    timestamp: datetime

    # Regel-effektivitet (anonymisert)
    rule_effectiveness: Dict[str, float] = field(default_factory=dict)
    # Eksempel: {'block_social_morning': 0.73, 'medication_8am': 0.95}

    # Aggregerte patterns (ikke hva, bare nar og hvor effektivt)
    patterns: Dict[str, Any] = field(default_factory=dict)
    # Eksempel: {'focus_best_hour': 10, 'productivity_weekday_vs_weekend': 1.3}


@dataclass
class GlobalPheromone:
    """Aggregert pheromone pa tvers av alle hjem"""
    rule_id: str
    strength: float  # 0-1, styrke av anbefalingen
    confidence: float  # 0-1, hvor sikker (basert pa datapunkter)
    profile_match: List[ProfileType]
    success_rate: float
    sample_size: int  # Antall hjem som har bidratt
    last_updated: datetime


class HomeCircle(BaseCircle):
    """
    HOME Circle - Federation Coordinator

    Ansvar:
    1. Holde oversikt over alle AIKI-HOME installasjoner
    2. Samle og aggregere pheromone (metadata) fra hjemmene
    3. Distribuere globale pheromone tilbake
    4. Garantere GDPR-compliance (aldri lagre personlig data)
    """

    def __init__(self):
        super().__init__(
            circle_id='home',
            purpose='Coordinate AIKI-HOME fleet while respecting privacy',
            domain=['aiki_home_fleet', 'pheromone_aggregation', 'gdpr_compliance'],
            accountabilities=[
                'Register and track AIKI-HOME installations',
                'Collect anonymized pheromone updates',
                'Aggregate patterns across the fleet',
                'Distribute recommendations to new homes',
                'Ensure GDPR compliance at all times'
            ]
        )
        self.name = 'home'  # For backwards compatibility

        # Registrerte hjem (anonymisert)
        self.registered_homes: Dict[str, HomeRegistration] = {}

        # Global pheromone database
        self.global_pheromones: Dict[str, GlobalPheromone] = {}

        # Pheromone per profil-type
        self.profile_pheromones: Dict[ProfileType, Dict[str, float]] = {
            pt: {} for pt in ProfileType
        }

        # GDPR: Set med aldri-tillatte data-felt
        self.gdpr_forbidden_fields: Set[str] = {
            'name', 'email', 'phone', 'address', 'ip_address',
            'browsing_history', 'search_queries', 'messages',
            'location', 'device_id', 'mac_address', 'ssn',
            'bank_account', 'credit_card', 'health_records'
        }

        # Metrics
        self.metrics = {
            'homes_registered': 0,
            'homes_online': 0,
            'pheromone_updates_received': 0,
            'recommendations_served': 0,
            'gdpr_violations_blocked': 0
        }

    async def register_home(
        self,
        home_id: str,
        profile_type: str,
        software_version: str,
        country: str = "NO"
    ) -> Dict[str, Any]:
        """
        Registrer nytt AIKI-HOME i federasjonen

        Returnerer initielle anbefalinger basert pa profil
        """
        # Valider profile type
        try:
            profile = ProfileType(profile_type)
        except ValueError:
            profile = ProfileType.GENERIC

        # Opprett registrering
        registration = HomeRegistration(
            home_id=home_id,
            profile_type=profile,
            registered_at=datetime.now(timezone.utc),
            last_seen=datetime.now(timezone.utc),
            status=HomeStatus.SETUP,
            software_version=software_version,
            country=country
        )

        self.registered_homes[home_id] = registration
        self.metrics['homes_registered'] += 1

        # Hent initielle anbefalinger
        recommendations = await self._get_recommendations_for_profile(profile)

        return {
            'registered': True,
            'home_id': home_id,
            'profile': profile.value,
            'initial_recommendations': recommendations,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

    async def receive_pheromone_update(self, update: Dict[str, Any]) -> Dict[str, Any]:
        """
        Motta pheromone-oppdatering fra et hjem

        GDPR: Validerer at ingen personlig data er inkludert!
        """
        # GDPR-sjekk forst!
        gdpr_check = self._gdpr_validate(update)
        if not gdpr_check['valid']:
            self.metrics['gdpr_violations_blocked'] += 1
            return {
                'accepted': False,
                'reason': 'GDPR violation detected',
                'forbidden_fields': gdpr_check['violations']
            }

        home_id = update.get('home_id')

        # Oppdater last_seen
        if home_id in self.registered_homes:
            self.registered_homes[home_id].last_seen = datetime.now(timezone.utc)
            self.registered_homes[home_id].status = HomeStatus.ONLINE
            self.registered_homes[home_id].pheromone_contributions += 1

        # Parse pheromone data
        try:
            profile = ProfileType(update.get('profile_type', 'generic'))
        except ValueError:
            profile = ProfileType.GENERIC

        rule_effectiveness = update.get('rule_effectiveness', {})

        # Oppdater global pheromone
        for rule_id, effectiveness in rule_effectiveness.items():
            await self._update_global_pheromone(rule_id, profile, effectiveness)

        self.metrics['pheromone_updates_received'] += 1

        return {
            'accepted': True,
            'rules_updated': len(rule_effectiveness),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

    async def get_recommendations(
        self,
        home_id: str,
        profile_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Hent anbefalinger for et hjem"""

        # Finn profil
        if home_id in self.registered_homes:
            profile = self.registered_homes[home_id].profile_type
        elif profile_type:
            try:
                profile = ProfileType(profile_type)
            except ValueError:
                profile = ProfileType.GENERIC
        else:
            profile = ProfileType.GENERIC

        recommendations = await self._get_recommendations_for_profile(profile)
        self.metrics['recommendations_served'] += 1

        return {
            'home_id': home_id,
            'profile': profile.value,
            'recommendations': recommendations,
            'based_on_homes': self._count_homes_with_profile(profile),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

    def _gdpr_validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valider at data ikke inneholder GDPR-sensitive felt

        Dette er KRITISK for federation-modellen!
        """
        violations = []

        def check_dict(d: Dict, path: str = ""):
            for key, value in d.items():
                full_path = f"{path}.{key}" if path else key

                # Sjekk om nokkel er forbudt
                if key.lower() in self.gdpr_forbidden_fields:
                    violations.append(full_path)

                # Sjekk nested dicts
                if isinstance(value, dict):
                    check_dict(value, full_path)

        check_dict(data)

        return {
            'valid': len(violations) == 0,
            'violations': violations
        }

    async def _update_global_pheromone(
        self,
        rule_id: str,
        profile: ProfileType,
        effectiveness: float
    ):
        """Oppdater global pheromone for en regel"""

        # Oppdater profil-spesifikk pheromone
        if rule_id not in self.profile_pheromones[profile]:
            self.profile_pheromones[profile][rule_id] = effectiveness
        else:
            # Exponential moving average
            alpha = 0.1
            current = self.profile_pheromones[profile][rule_id]
            self.profile_pheromones[profile][rule_id] = current * (1 - alpha) + effectiveness * alpha

        # Oppdater global pheromone
        if rule_id not in self.global_pheromones:
            self.global_pheromones[rule_id] = GlobalPheromone(
                rule_id=rule_id,
                strength=effectiveness,
                confidence=0.3,  # Lav confidence til vi har mer data
                profile_match=[profile],
                success_rate=effectiveness,
                sample_size=1,
                last_updated=datetime.now(timezone.utc)
            )
        else:
            pheromone = self.global_pheromones[rule_id]

            # Oppdater med nytt datapunkt
            n = pheromone.sample_size
            pheromone.strength = (pheromone.strength * n + effectiveness) / (n + 1)
            pheromone.success_rate = (pheromone.success_rate * n + effectiveness) / (n + 1)
            pheromone.sample_size += 1
            pheromone.confidence = min(0.95, 0.3 + (pheromone.sample_size * 0.02))

            if profile not in pheromone.profile_match:
                pheromone.profile_match.append(profile)

            pheromone.last_updated = datetime.now(timezone.utc)

    async def _get_recommendations_for_profile(
        self,
        profile: ProfileType
    ) -> List[Dict[str, Any]]:
        """Hent anbefalinger for en profil"""
        recommendations = []

        # Profil-spesifikke pheromones forst
        profile_rules = self.profile_pheromones.get(profile, {})

        for rule_id, strength in sorted(profile_rules.items(), key=lambda x: x[1], reverse=True)[:10]:
            global_pheromone = self.global_pheromones.get(rule_id)

            recommendations.append({
                'rule_id': rule_id,
                'strength': strength,
                'confidence': global_pheromone.confidence if global_pheromone else 0.5,
                'success_rate': global_pheromone.success_rate if global_pheromone else strength,
                'sample_size': global_pheromone.sample_size if global_pheromone else 1,
                'profile_specific': True
            })

        # Fyll opp med globale hvis for fa profil-spesifikke
        if len(recommendations) < 5:
            for rule_id, pheromone in sorted(
                self.global_pheromones.items(),
                key=lambda x: x[1].strength * x[1].confidence,
                reverse=True
            ):
                if rule_id not in [r['rule_id'] for r in recommendations]:
                    recommendations.append({
                        'rule_id': rule_id,
                        'strength': pheromone.strength,
                        'confidence': pheromone.confidence,
                        'success_rate': pheromone.success_rate,
                        'sample_size': pheromone.sample_size,
                        'profile_specific': False
                    })

                    if len(recommendations) >= 10:
                        break

        return recommendations

    def _count_homes_with_profile(self, profile: ProfileType) -> int:
        """Tell antall hjem med en profil"""
        return sum(
            1 for h in self.registered_homes.values()
            if h.profile_type == profile
        )

    def get_fleet_status(self) -> Dict[str, Any]:
        """Hent status for hele flaten"""
        now = datetime.now(timezone.utc)

        # Oppdater online/offline status
        online_count = 0
        for home in self.registered_homes.values():
            if (now - home.last_seen) < timedelta(minutes=5):
                home.status = HomeStatus.ONLINE
                online_count += 1
            elif home.status == HomeStatus.ONLINE:
                home.status = HomeStatus.OFFLINE

        self.metrics['homes_online'] = online_count

        # Tell per profil
        profile_counts = {}
        for profile in ProfileType:
            profile_counts[profile.value] = self._count_homes_with_profile(profile)

        return {
            'total_homes': len(self.registered_homes),
            'online': online_count,
            'offline': len(self.registered_homes) - online_count,
            'by_profile': profile_counts,
            'total_pheromone_rules': len(self.global_pheromones),
            'total_contributions': self.metrics['pheromone_updates_received'],
            'gdpr_violations_blocked': self.metrics['gdpr_violations_blocked']
        }

    def get_metrics(self) -> Dict[str, Any]:
        """Hent circle metrics"""
        return {
            **self.metrics,
            'global_pheromones_count': len(self.global_pheromones),
            'average_confidence': sum(p.confidence for p in self.global_pheromones.values()) / max(len(self.global_pheromones), 1)
        }


async def main():
    """Test HOME Circle"""
    import logging
    logging.basicConfig(level=logging.INFO)

    circle = HomeCircle()

    # Test 1: Registrer hjem
    print("\n=== Test 1: Registrer hjem ===")
    result = await circle.register_home(
        home_id='home-001-hash',
        profile_type='adhd_adult_work_from_home',
        software_version='1.0.0',
        country='NO'
    )
    print(f"Registrert: {result['registered']}")
    print(f"Anbefalinger: {len(result['initial_recommendations'])}")

    # Test 2: Send pheromone update
    print("\n=== Test 2: Pheromone Update ===")
    update = {
        'home_id': 'home-001-hash',
        'profile_type': 'adhd_adult_work_from_home',
        'rule_effectiveness': {
            'block_social_morning': 0.73,
            'medication_reminder_8am': 0.95,
            'focus_mode_pomodoro': 0.68
        }
    }
    result = await circle.receive_pheromone_update(update)
    print(f"Akseptert: {result['accepted']}")

    # Test 3: GDPR-sjekk
    print("\n=== Test 3: GDPR Validation ===")
    bad_update = {
        'home_id': 'home-002-hash',
        'email': 'test@example.com',  # FORBUDT!
        'rule_effectiveness': {'rule1': 0.5}
    }
    result = await circle.receive_pheromone_update(bad_update)
    print(f"Akseptert: {result['accepted']}")
    print(f"Grunn: {result.get('reason', 'N/A')}")

    # Test 4: Hent anbefalinger
    print("\n=== Test 4: Hent Anbefalinger ===")
    result = await circle.get_recommendations('home-001-hash')
    print(f"Anbefalinger for profil {result['profile']}:")
    for rec in result['recommendations'][:3]:
        print(f"  - {rec['rule_id']}: strength={rec['strength']:.2f}")

    # Test 5: Fleet status
    print("\n=== Test 5: Fleet Status ===")
    status = circle.get_fleet_status()
    print(f"Total hjem: {status['total_homes']}")
    print(f"Online: {status['online']}")
    print(f"GDPR-brudd blokkert: {status['gdpr_violations_blocked']}")


if __name__ == "__main__":
    asyncio.run(main())
