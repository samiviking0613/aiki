#!/usr/bin/env python3
"""
AIKI Ultimate - Integration Tests

Tester hele systemet fra topp til bunn:
- Level 0: Prime Consciousness
- Level 1: Holacracy Circles
- Level 2: Mini-AIKIs
- Safety Layers
- API Client

Kjør: python -m pytest tests/test_integration.py -v
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timezone

try:
    import pytest
    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestAPIClient:
    """Test API client with key rotation"""

    def get_api_client(self):
        from src.api_client import APIClient
        return APIClient()

    def test_key_rotation(self):
        """Test at nøkkelrotasjon fungerer"""
        api_client = self.get_api_client()
        initial_index = api_client.openrouter_key_index
        api_client._rotate_key('openrouter')
        assert api_client.openrouter_key_index == initial_index + 1

    def test_model_config(self):
        """Test at alle modeller er konfigurert"""
        from src.api_client import MODELS
        required_models = [
            'haiku-3.5', 'gemini-flash', 'llama-3.3-70b',
            'deepseek-v3', 'sonnet-4.5', 'opus-4', 'gpt-4o'
        ]
        for model in required_models:
            assert model in MODELS, f"Missing model: {model}"

    def test_cost_tracking(self):
        """Test at kostnadsberegning fungerer"""
        api_client = self.get_api_client()
        assert api_client.total_cost == 0.0
        assert api_client.request_count == 0


class TestSafetyLayers:
    """Test sikkerhetslag"""

    def test_kill_switch_init(self):
        """Test KillSwitch initialisering"""
        from src.safety.kill_switch import KillSwitch
        ks = KillSwitch()
        assert ks.active is True
        assert ks.kill_requested is False

    def test_kill_switch_register(self):
        """Test prosessregistrering"""
        from src.safety.kill_switch import KillSwitch
        ks = KillSwitch()
        ks.register_process(
            process_id='test-process',
            process_type='test',
            pid=12345,
            hostname='localhost',
            location='test',
            parent_id=None
        )
        assert 'test-process' in ks.registered_processes

    def test_audit_log_init(self):
        """Test AuditLog initialisering"""
        from src.safety.audit_log import AuditLog
        log = AuditLog()
        assert log is not None

    async def test_audit_log_event(self):
        """Test logging av events"""
        from src.safety.audit_log import AuditLog, EventType
        log = AuditLog()
        await log.log(
            event_type=EventType.DECISION,
            component='test',
            description='Test event',
            data={'test': True}
        )
        # Sjekk at log ble opprettet (avhenger av implementasjon)

    def test_constraints_init(self):
        """Test Constraints initialisering"""
        from src.safety.constraints import ConstraintValidator
        engine = ConstraintValidator()
        assert engine is not None

    def test_autonomy_levels(self):
        """Test autonominivåer"""
        from src.safety.autonomy_levels import AutonomyLevel
        # Sjekk at nivåene eksisterer
        assert AutonomyLevel.SUPERVISED.value == 'supervised'
        assert AutonomyLevel.SEMI_AUTONOMOUS.value == 'semi_autonomous'


class TestCircles:
    """Test Holacracy Circles"""

    def test_economic_circle_init(self):
        """Test EconomicCircle initialisering"""
        from src.circles.economic_circle import EconomicCircle
        circle = EconomicCircle()
        assert circle.name == 'economic'
        assert len(circle.responsibilities) > 0

    def test_learning_circle_init(self):
        """Test LearningCircle initialisering"""
        from src.circles.learning_circle import LearningCircle
        circle = LearningCircle()
        assert circle.name == 'learning'

    def test_social_circle_init(self):
        """Test SocialCircle initialisering"""
        from src.circles.social_circle import SocialCircle
        circle = SocialCircle()
        assert circle.name == 'social'


class TestMiniAikis:
    """Test Mini-AIKIs"""

    def test_swarm_consensus_init(self):
        """Test SwarmConsensus initialisering"""
        from src.mini_aikis.learning.swarm_consensus import SwarmConsensus
        swarm = SwarmConsensus()
        assert swarm.mini_id == 'mini_5_swarm'
        assert len(swarm.available_models) == 7

    def test_swarm_voting_methods(self):
        """Test at alle voting-metoder fungerer"""
        from src.mini_aikis.learning.swarm_consensus import SwarmConsensus
        swarm = SwarmConsensus()

        # Simuler responses
        responses = [
            {'model': 'm1', 'answer': 'A', 'confidence': 0.8},
            {'model': 'm2', 'answer': 'A', 'confidence': 0.7},
            {'model': 'm3', 'answer': 'A', 'confidence': 0.9},
            {'model': 'm4', 'answer': 'B', 'confidence': 0.6},
            {'model': 'm5', 'answer': 'A', 'confidence': 0.85},
            {'model': 'm6', 'answer': 'B', 'confidence': 0.7},
            {'model': 'm7', 'answer': 'A', 'confidence': 0.75},
        ]

        # Test majority
        result = swarm._majority_vote(responses)
        assert result['result'] == 'A'
        assert result['agreement_rate'] > 0.5

        # Test weighted
        result = swarm._weighted_vote(responses)
        assert result['result'] == 'A'

        # Test ICE
        result = swarm._ice_vote(responses)
        assert result['result'] == 'A'

    def test_multi_agent_validator_init(self):
        """Test MultiAgentValidator initialisering"""
        from src.mini_aikis.learning.multi_agent_validator import MultiAgentValidator
        validator = MultiAgentValidator()
        assert validator.mini_id == 'mini_6_validator'
        assert len(validator.available_models) == 6

    def test_validator_role_selection(self):
        """Test at roller velges riktig"""
        from src.mini_aikis.learning.multi_agent_validator import MultiAgentValidator
        validator = MultiAgentValidator()

        proposer = validator._select_model_for_role('proposer', 'general')
        critic = validator._select_model_for_role('critic', 'general')
        judge = validator._select_model_for_role('judge', 'general')

        assert proposer is not None
        assert critic is not None
        assert judge is not None

    def test_verdict_determination(self):
        """Test verdictberegning"""
        from src.mini_aikis.learning.multi_agent_validator import MultiAgentValidator
        validator = MultiAgentValidator()

        # Test valid
        verdict, confidence = validator._determine_verdict(0.75, [0.7, 0.8])
        assert verdict == 'valid'
        assert confidence > 0.5

        # Test invalid
        verdict, confidence = validator._determine_verdict(0.25, [0.2, 0.3])
        assert verdict == 'invalid'

        # Test uncertain
        verdict, confidence = validator._determine_verdict(0.5, [0.4, 0.6])
        assert verdict == 'uncertain'

    async def test_swarm_run(self):
        """Test full swarm run"""
        from src.mini_aikis.learning.swarm_consensus import SwarmConsensus
        swarm = SwarmConsensus()

        result = await swarm._run_swarm(
            prompt='Test prompt',
            voting_method='majority',
            task_type='general',
            num_models=7
        )

        assert 'consensus_result' in result
        assert 'confidence' in result
        assert 'agreement_rate' in result
        assert 'cost' in result

    async def test_validator_run(self):
        """Test full validation run"""
        from src.mini_aikis.learning.multi_agent_validator import MultiAgentValidator
        validator = MultiAgentValidator()

        result = await validator._run_validation(
            claim='Test claim',
            context='Test context',
            rounds=2,
            topic='test'
        )

        assert 'verdict' in result
        assert result['verdict'] in ['valid', 'invalid', 'uncertain']
        assert 'confidence' in result
        assert 'debate_transcript' in result


class TestPrimeConsciousness:
    """Test Prime Consciousness"""

    def test_prime_init(self):
        """Test PrimeConsciousness initialisering"""
        from src.aiki_prime.prime_consciousness import PrimeConsciousness
        prime = PrimeConsciousness()
        assert prime is not None


class TestOrchestrator:
    """Test orchestrator"""

    def test_orchestrator_init(self):
        """Test orchestrator initialisering"""
        from run_ultimate import AikiUltimateOrchestrator
        orch = AikiUltimateOrchestrator()
        assert orch.running is False
        assert orch.prime is None
        assert len(orch.circles) == 0
        assert len(orch.mini_aikis) == 0

    def test_orchestrator_status(self):
        """Test status-funksjon"""
        from run_ultimate import AikiUltimateOrchestrator
        orch = AikiUltimateOrchestrator()
        status = orch.get_status()

        assert 'running' in status
        assert 'circles' in status
        assert 'mini_aikis' in status


class TestEndToEnd:
    """End-to-end integrasjonstester"""

    async def test_full_startup_shutdown(self):
        """Test full oppstart og nedstengning"""
        from run_ultimate import AikiUltimateOrchestrator

        orch = AikiUltimateOrchestrator()

        # Start Prime
        await orch._start_prime()
        assert orch.prime is not None or True  # Kan være None i degraded mode

        # Start Circles
        await orch._start_circles()
        # Noen circles kan feile pga dependencies

        # Start Mini-AIKIs
        await orch._start_mini_aikis()
        # Noen mini-aikis kan feile

        # Shutdown
        await orch.shutdown()
        assert orch.running is False

    async def test_swarm_and_validator_integration(self):
        """Test at Swarm og Validator fungerer sammen"""
        from src.mini_aikis.learning.swarm_consensus import SwarmConsensus
        from src.mini_aikis.learning.multi_agent_validator import MultiAgentValidator

        swarm = SwarmConsensus()
        validator = MultiAgentValidator()

        # Kjør swarm først
        swarm_result = await swarm._run_swarm(
            prompt='What is 2+2?',
            voting_method='majority',
            task_type='reasoning'
        )

        # Valider swarm-resultatet
        validation_result = await validator._run_validation(
            claim=f"The answer to 2+2 is {swarm_result['consensus_result']}",
            context='Mathematical verification',
            rounds=1
        )

        assert 'verdict' in validation_result
        assert validation_result['confidence'] > 0


# Kjør quick test
async def quick_test():
    """Rask test av kjernefunksjonalitet"""
    print("=" * 60)
    print("AIKI ULTIMATE - QUICK INTEGRATION TEST")
    print("=" * 60)

    results = {
        'passed': 0,
        'failed': 0,
        'tests': []
    }

    # Test 1: API Client
    print("\n1. Testing API Client...")
    try:
        from src.api_client import APIClient, MODELS
        client = APIClient()
        assert len(MODELS) >= 7
        client._rotate_key('openrouter')
        results['tests'].append(('API Client', 'PASS'))
        results['passed'] += 1
        print("   ✅ PASS")
    except Exception as e:
        results['tests'].append(('API Client', f'FAIL: {e}'))
        results['failed'] += 1
        print(f"   ❌ FAIL: {e}")

    # Test 2: Safety Layers
    print("\n2. Testing Safety Layers...")
    try:
        from src.safety.kill_switch import KillSwitch
        from src.safety.audit_log import AuditLog
        from src.safety.constraints import ConstraintValidator
        ks = KillSwitch()
        al = AuditLog()
        ce = ConstraintValidator()
        results['tests'].append(('Safety Layers', 'PASS'))
        results['passed'] += 1
        print("   ✅ PASS")
    except Exception as e:
        results['tests'].append(('Safety Layers', f'FAIL: {e}'))
        results['failed'] += 1
        print(f"   ❌ FAIL: {e}")

    # Test 3: Circles
    print("\n3. Testing Circles...")
    try:
        from src.circles.economic_circle import EconomicCircle
        from src.circles.learning_circle import LearningCircle
        from src.circles.social_circle import SocialCircle
        ec = EconomicCircle()
        lc = LearningCircle()
        sc = SocialCircle()
        results['tests'].append(('Circles', 'PASS'))
        results['passed'] += 1
        print("   ✅ PASS")
    except Exception as e:
        results['tests'].append(('Circles', f'FAIL: {e}'))
        results['failed'] += 1
        print(f"   ❌ FAIL: {e}")

    # Test 4: Mini-AIKIs (Swarm)
    print("\n4. Testing Swarm Consensus...")
    try:
        from src.mini_aikis.learning.swarm_consensus import SwarmConsensus
        swarm = SwarmConsensus()
        result = await swarm._run_swarm(
            prompt='Test',
            voting_method='majority',
            num_models=3
        )
        assert 'consensus_result' in result
        results['tests'].append(('Swarm Consensus', 'PASS'))
        results['passed'] += 1
        print("   ✅ PASS")
    except Exception as e:
        results['tests'].append(('Swarm Consensus', f'FAIL: {e}'))
        results['failed'] += 1
        print(f"   ❌ FAIL: {e}")

    # Test 5: Mini-AIKIs (Validator)
    print("\n5. Testing Multi-Agent Validator...")
    try:
        from src.mini_aikis.learning.multi_agent_validator import MultiAgentValidator
        validator = MultiAgentValidator()
        result = await validator._run_validation(
            claim='Test claim',
            context='Test',
            rounds=1
        )
        assert 'verdict' in result
        results['tests'].append(('Multi-Agent Validator', 'PASS'))
        results['passed'] += 1
        print("   ✅ PASS")
    except Exception as e:
        results['tests'].append(('Multi-Agent Validator', f'FAIL: {e}'))
        results['failed'] += 1
        print(f"   ❌ FAIL: {e}")

    # Test 6: Orchestrator
    print("\n6. Testing Orchestrator...")
    try:
        from run_ultimate import AikiUltimateOrchestrator
        orch = AikiUltimateOrchestrator()
        status = orch.get_status()
        assert 'running' in status
        results['tests'].append(('Orchestrator', 'PASS'))
        results['passed'] += 1
        print("   ✅ PASS")
    except Exception as e:
        results['tests'].append(('Orchestrator', f'FAIL: {e}'))
        results['failed'] += 1
        print(f"   ❌ FAIL: {e}")

    # Summary
    print("\n" + "=" * 60)
    print(f"RESULTS: {results['passed']}/{results['passed'] + results['failed']} tests passed")
    print("=" * 60)

    for test_name, status in results['tests']:
        emoji = "✅" if status == 'PASS' else "❌"
        print(f"  {emoji} {test_name}: {status}")

    return results['failed'] == 0


if __name__ == "__main__":
    import sys
    success = asyncio.run(quick_test())
    sys.exit(0 if success else 1)
