#!/usr/bin/env python3
"""
NETWORK CIRCLE - Nettverksdiagnostikk og problemlosning

Purpose: "Diagnose, fix, and learn from network issues across all AIKI-HOME installations"

Denne circlen samler nettverkserfaringer fra alle AIKI-HOME installasjoner
og bruker pheromone-basert laring for a anbefale losninger.

Arkitektur-valg dokumentert i: docs/architecture/NETWORK_CIRCLE_ALTERNATIVES.md
"""

import asyncio
import sys
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.circles.base_circle import BaseCircle


class NetworkProblem(Enum):
    """Kjente nettverksproblemer"""
    DOUBLE_NAT = "double_nat"
    CGNAT = "cgnat"
    UPNP_UNAVAILABLE = "upnp_unavailable"
    DNS_ISSUES = "dns_issues"
    IPV6_ONLY = "ipv6_only"
    FIREWALL_BLOCKING = "firewall_blocking"
    SLOW_CONNECTION = "slow_connection"
    INTERMITTENT = "intermittent"
    PORT_BLOCKED = "port_blocked"
    WIFI_INSTABILITY = "wifi_instability"


class SolutionType(Enum):
    """Typer losninger"""
    AUTO_FIX = "auto_fix"           # Kan fikses automatisk
    USER_ACTION = "user_action"      # Bruker ma gjore noe
    ISP_CONTACT = "isp_contact"      # Ma kontakte ISP
    HARDWARE_CHANGE = "hardware_change"  # Trenger ny hardware
    WORKAROUND = "workaround"        # Midlertidig losning


@dataclass
class ISPProfile:
    """Profil for en ISP basert pa erfaringer"""
    name: str
    country: str = "NO"
    common_problems: List[NetworkProblem] = field(default_factory=list)
    known_routers: List[str] = field(default_factory=list)
    cgnat_probability: float = 0.0
    double_nat_probability: float = 0.0
    ipv6_support: bool = False
    bridge_mode_available: bool = False
    support_quality: float = 0.5  # 0-1
    solution_success_rates: Dict[str, float] = field(default_factory=dict)


@dataclass
class NetworkSolution:
    """En losning pa et nettverksproblem"""
    problem: NetworkProblem
    solution_type: SolutionType
    steps: List[str]
    confidence: float  # 0-1, basert pa pheromone
    success_rate: float  # Historisk suksessrate
    isp_specific: Optional[str] = None
    router_specific: Optional[str] = None
    alternative: Optional[str] = None
    estimated_time_minutes: int = 5


@dataclass
class PheromoneTrail:
    """Pheromone-spor for en losning"""
    solution_hash: str
    problem: NetworkProblem
    isp: str
    strength: float  # 0-1, styrkes ved suksess, svekkes over tid
    success_count: int
    failure_count: int
    last_updated: datetime

    @property
    def success_rate(self) -> float:
        total = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 0.5


class NetworkCircle(BaseCircle):
    """
    Network Circle - Federert nettverkslosning

    Ansvar:
    1. Samle nettverkserfaringer fra alle AIKI-HOME
    2. Bygge ISP knowledge base
    3. Anbefale losninger basert pa pheromone
    4. Lare fra suksess/feil
    """

    def __init__(self):
        super().__init__(
            circle_id='network',
            purpose='Diagnose, fix, and learn from network issues',
            domain=['network_diagnostics', 'isp_knowledge', 'connectivity_solutions'],
            accountabilities=[
                'Collect network diagnostics from AIKI-HOME fleet',
                'Build ISP knowledge base from experiences',
                'Recommend solutions based on pheromone trails',
                'Learn from success/failure feedback',
                'Provide plug-and-play network setup'
            ]
        )
        self.name = 'network'  # For backwards compatibility

        # ISP Knowledge Base (starter med norske ISPer)
        self.isp_profiles: Dict[str, ISPProfile] = {
            'telenor': ISPProfile(
                name='Telenor Norge',
                common_problems=[NetworkProblem.DOUBLE_NAT, NetworkProblem.CGNAT],
                known_routers=['Zyxel T-50', 'Zyxel T-54', 'Sagemcom'],
                cgnat_probability=0.3,
                double_nat_probability=0.4,
                ipv6_support=True,
                bridge_mode_available=True,
                support_quality=0.6
            ),
            'altibox': ISPProfile(
                name='Altibox',
                common_problems=[NetworkProblem.DOUBLE_NAT],
                known_routers=['Altibox router', 'ZyXEL'],
                cgnat_probability=0.1,
                double_nat_probability=0.5,
                ipv6_support=True,
                bridge_mode_available=True,
                support_quality=0.7
            ),
            'telia': ISPProfile(
                name='Telia Norge',
                common_problems=[NetworkProblem.CGNAT, NetworkProblem.DNS_ISSUES],
                known_routers=['Telia Box', 'Technicolor'],
                cgnat_probability=0.5,
                double_nat_probability=0.2,
                ipv6_support=True,
                bridge_mode_available=False,
                support_quality=0.5
            ),
            'nextgentel': ISPProfile(
                name='NextGenTel',
                common_problems=[NetworkProblem.UPNP_UNAVAILABLE],
                known_routers=['Various'],
                cgnat_probability=0.2,
                double_nat_probability=0.3,
                ipv6_support=False,
                bridge_mode_available=True,
                support_quality=0.6
            ),
        }

        # Pheromone trails - lart fra erfaringer
        self.pheromone_trails: Dict[str, PheromoneTrail] = {}

        # Solution templates
        self.solution_templates = self._init_solution_templates()

        # Metrics
        self.metrics = {
            'diagnostics_received': 0,
            'solutions_recommended': 0,
            'success_feedback': 0,
            'failure_feedback': 0,
            'isp_profiles_updated': 0
        }

    def _init_solution_templates(self) -> Dict[NetworkProblem, List[NetworkSolution]]:
        """Initialiser losnings-templates"""
        return {
            NetworkProblem.DOUBLE_NAT: [
                NetworkSolution(
                    problem=NetworkProblem.DOUBLE_NAT,
                    solution_type=SolutionType.AUTO_FIX,
                    steps=[
                        "Aktiverer UPnP port forwarding automatisk",
                        "Setter opp NAT-PMP som backup",
                    ],
                    confidence=0.7,
                    success_rate=0.6,
                    estimated_time_minutes=1
                ),
                NetworkSolution(
                    problem=NetworkProblem.DOUBLE_NAT,
                    solution_type=SolutionType.USER_ACTION,
                    steps=[
                        "Logg inn pa router (vanligvis 192.168.1.1)",
                        "Finn NAT/Port Forwarding innstillinger",
                        "Aktiver DMZ for AIKI-HOME IP-adresse",
                        "Eller: Sett opp port forwarding for port 8080, 443",
                    ],
                    confidence=0.8,
                    success_rate=0.75,
                    estimated_time_minutes=10
                ),
                NetworkSolution(
                    problem=NetworkProblem.DOUBLE_NAT,
                    solution_type=SolutionType.ISP_CONTACT,
                    steps=[
                        "Ring ISP kundeservice",
                        "Be om 'bridge mode' pa routeren",
                        "Alternativt: Be om offentlig IP-adresse",
                        "Vent pa at ISP aktiverer endringen (1-24 timer)",
                    ],
                    confidence=0.9,
                    success_rate=0.85,
                    alternative="Bruk Wireguard VPN som workaround",
                    estimated_time_minutes=30
                ),
            ],
            NetworkProblem.CGNAT: [
                NetworkSolution(
                    problem=NetworkProblem.CGNAT,
                    solution_type=SolutionType.ISP_CONTACT,
                    steps=[
                        "Ring ISP og spor om de bruker CGNAT",
                        "Be om offentlig IPv4-adresse (kan koste ekstra)",
                        "Alternativ: Spor om IPv6 er tilgjengelig",
                    ],
                    confidence=0.6,
                    success_rate=0.5,
                    alternative="Bruk Wireguard tunnel via VPS",
                    estimated_time_minutes=30
                ),
                NetworkSolution(
                    problem=NetworkProblem.CGNAT,
                    solution_type=SolutionType.WORKAROUND,
                    steps=[
                        "Setter opp Wireguard tunnel til AIKI Prime",
                        "All trafikk routes gjennom tunnel",
                        "Fungerer uavhengig av CGNAT",
                    ],
                    confidence=0.95,
                    success_rate=0.92,
                    estimated_time_minutes=5
                ),
            ],
            NetworkProblem.DNS_ISSUES: [
                NetworkSolution(
                    problem=NetworkProblem.DNS_ISSUES,
                    solution_type=SolutionType.AUTO_FIX,
                    steps=[
                        "Bytter til Cloudflare DNS (1.1.1.1)",
                        "Aktiverer DNS-over-HTTPS",
                    ],
                    confidence=0.9,
                    success_rate=0.88,
                    estimated_time_minutes=1
                ),
            ],
            NetworkProblem.WIFI_INSTABILITY: [
                NetworkSolution(
                    problem=NetworkProblem.WIFI_INSTABILITY,
                    solution_type=SolutionType.USER_ACTION,
                    steps=[
                        "Koble AIKI-HOME til Ethernet hvis mulig",
                        "Eller: Flytt narmere router",
                        "Eller: Bytt WiFi-kanal (1, 6, eller 11 for 2.4GHz)",
                    ],
                    confidence=0.7,
                    success_rate=0.65,
                    alternative="Bruk WiFi-extender eller mesh",
                    estimated_time_minutes=15
                ),
            ],
        }

    async def receive_diagnostic(self, diagnostic: Dict[str, Any]) -> Dict[str, Any]:
        """
        Motta diagnostikk fra et AIKI-HOME

        Input: {
            'home_id': str (anonymisert hash),
            'public_ip': str,
            'local_ip': str,
            'gateway': str,
            'isp_detected': str,
            'router_model': str,
            'problems_detected': List[str],
            'upnp_available': bool,
            'ipv6': bool,
            'latency_ms': float,
            'bandwidth_mbps': float
        }
        """
        self.metrics['diagnostics_received'] += 1

        # Anonymiser sensitive data
        home_id = diagnostic.get('home_id', self._generate_anonymous_id())

        # Detekter ISP
        isp = self._detect_isp(diagnostic.get('isp_detected', ''))

        # Finn problemer
        problems = self._analyze_problems(diagnostic)

        # Hent losninger
        solutions = await self._get_solutions(problems, isp, diagnostic)

        self.metrics['solutions_recommended'] += len(solutions)

        return {
            'home_id': home_id,
            'isp_detected': isp,
            'problems_found': [p.value for p in problems],
            'solutions': [
                {
                    'problem': s.problem.value,
                    'type': s.solution_type.value,
                    'steps': s.steps,
                    'confidence': s.confidence,
                    'success_rate': s.success_rate,
                    'estimated_minutes': s.estimated_time_minutes,
                    'alternative': s.alternative
                }
                for s in solutions
            ],
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

    async def receive_feedback(
        self,
        home_id: str,
        solution_hash: str,
        success: bool,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Motta feedback pa en losning - oppdaterer pheromone

        Dette er kjernen i laeringssystemet!
        """
        if success:
            self.metrics['success_feedback'] += 1
        else:
            self.metrics['failure_feedback'] += 1

        # Oppdater pheromone trail
        if solution_hash in self.pheromone_trails:
            trail = self.pheromone_trails[solution_hash]
            if success:
                trail.success_count += 1
                trail.strength = min(1.0, trail.strength + 0.05)
            else:
                trail.failure_count += 1
                trail.strength = max(0.1, trail.strength - 0.1)
            trail.last_updated = datetime.now(timezone.utc)

        return {
            'acknowledged': True,
            'new_confidence': self.pheromone_trails.get(solution_hash, {}).strength if solution_hash in self.pheromone_trails else None
        }

    def _detect_isp(self, isp_string: str) -> str:
        """Detekter ISP fra AS-navn eller annen info"""
        isp_lower = isp_string.lower()

        for isp_key, profile in self.isp_profiles.items():
            if isp_key in isp_lower or profile.name.lower() in isp_lower:
                return isp_key

        return 'unknown'

    def _analyze_problems(self, diagnostic: Dict[str, Any]) -> List[NetworkProblem]:
        """Analyser diagnostikk og finn problemer"""
        problems = []

        # Sjekk eksplisitt rapporterte problemer
        for prob_str in diagnostic.get('problems_detected', []):
            try:
                problems.append(NetworkProblem(prob_str))
            except ValueError:
                pass

        # Detekter Double NAT
        local_ip = diagnostic.get('local_ip', '')
        gateway = diagnostic.get('gateway', '')
        if local_ip.startswith('192.168.') and gateway.startswith('192.168.'):
            # Kan indikere double NAT - trenger mer analyse
            if not diagnostic.get('upnp_available', True):
                problems.append(NetworkProblem.DOUBLE_NAT)

        # Detekter CGNAT (100.64.x.x range)
        public_ip = diagnostic.get('public_ip', '')
        if public_ip.startswith('100.64.') or public_ip.startswith('100.65.'):
            problems.append(NetworkProblem.CGNAT)

        # Detekter UPnP-problemer
        if not diagnostic.get('upnp_available', True):
            problems.append(NetworkProblem.UPNP_UNAVAILABLE)

        # Detekter lav hastighet
        bandwidth = diagnostic.get('bandwidth_mbps', 100)
        if bandwidth < 10:
            problems.append(NetworkProblem.SLOW_CONNECTION)

        return list(set(problems))  # Fjern duplikater

    async def _get_solutions(
        self,
        problems: List[NetworkProblem],
        isp: str,
        diagnostic: Dict[str, Any]
    ) -> List[NetworkSolution]:
        """Hent losninger basert pa problemer og pheromone"""
        solutions = []

        for problem in problems:
            if problem in self.solution_templates:
                templates = self.solution_templates[problem]

                # Sorter etter pheromone-styrke for denne ISP-en
                scored_templates = []
                for template in templates:
                    # Beregn score basert pa pheromone
                    trail_key = self._solution_hash(problem, isp, template.solution_type)

                    if trail_key in self.pheromone_trails:
                        trail = self.pheromone_trails[trail_key]
                        score = trail.strength * trail.success_rate
                    else:
                        score = template.confidence * template.success_rate

                    # Juster for ISP-spesifikk info
                    if isp in self.isp_profiles:
                        profile = self.isp_profiles[isp]
                        if template.solution_type == SolutionType.ISP_CONTACT:
                            score *= profile.support_quality

                    scored_templates.append((score, template))

                # Sorter og returner beste
                scored_templates.sort(key=lambda x: x[0], reverse=True)

                # Legg til topp 2 losninger per problem
                for score, template in scored_templates[:2]:
                    solution = NetworkSolution(
                        problem=template.problem,
                        solution_type=template.solution_type,
                        steps=template.steps.copy(),
                        confidence=score,
                        success_rate=template.success_rate,
                        isp_specific=isp if isp != 'unknown' else None,
                        alternative=template.alternative,
                        estimated_time_minutes=template.estimated_time_minutes
                    )
                    solutions.append(solution)

        return solutions

    def _solution_hash(self, problem: NetworkProblem, isp: str, solution_type: SolutionType) -> str:
        """Generer unik hash for en losning"""
        key = f"{problem.value}:{isp}:{solution_type.value}"
        return hashlib.sha256(key.encode()).hexdigest()[:16]

    def _generate_anonymous_id(self) -> str:
        """Generer anonym ID for et hjem"""
        import random
        return hashlib.sha256(str(random.random()).encode()).hexdigest()[:12]

    def get_isp_stats(self, isp: str) -> Dict[str, Any]:
        """Hent statistikk for en ISP"""
        if isp not in self.isp_profiles:
            return {'error': f'Unknown ISP: {isp}'}

        profile = self.isp_profiles[isp]

        # Tell relevante pheromone trails
        trails = [t for k, t in self.pheromone_trails.items() if isp in k]

        return {
            'isp': profile.name,
            'common_problems': [p.value for p in profile.common_problems],
            'cgnat_probability': profile.cgnat_probability,
            'bridge_mode_available': profile.bridge_mode_available,
            'support_quality': profile.support_quality,
            'total_experiences': sum(t.success_count + t.failure_count for t in trails),
            'average_success_rate': sum(t.success_rate for t in trails) / len(trails) if trails else 0.5
        }

    def get_metrics(self) -> Dict[str, Any]:
        """Hent circle metrics"""
        return {
            **self.metrics,
            'isp_profiles_count': len(self.isp_profiles),
            'pheromone_trails_count': len(self.pheromone_trails),
            'total_feedback': self.metrics['success_feedback'] + self.metrics['failure_feedback']
        }


async def main():
    """Test Network Circle"""
    import logging
    logging.basicConfig(level=logging.INFO)

    circle = NetworkCircle()

    # Simuler diagnostikk fra et hjem
    print("\n=== Test 1: Motta diagnostikk ===")
    diagnostic = {
        'home_id': 'test-home-001',
        'public_ip': '84.212.45.123',
        'local_ip': '192.168.1.100',
        'gateway': '192.168.1.1',
        'isp_detected': 'Telenor Norge AS',
        'router_model': 'Zyxel T-50',
        'problems_detected': [],
        'upnp_available': False,
        'ipv6': True,
        'latency_ms': 15.0,
        'bandwidth_mbps': 95.0
    }

    result = await circle.receive_diagnostic(diagnostic)
    print(f"ISP: {result['isp_detected']}")
    print(f"Problemer: {result['problems_found']}")
    print(f"Antall losninger: {len(result['solutions'])}")
    for sol in result['solutions']:
        print(f"  - {sol['problem']}: {sol['type']} (confidence: {sol['confidence']:.2f})")

    # Test ISP stats
    print("\n=== Test 2: ISP Statistikk ===")
    stats = circle.get_isp_stats('telenor')
    print(f"Telenor stats: {stats}")

    # Test metrics
    print("\n=== Test 3: Circle Metrics ===")
    metrics = circle.get_metrics()
    print(f"Metrics: {metrics}")


if __name__ == "__main__":
    asyncio.run(main())
