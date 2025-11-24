#!/usr/bin/env python3
"""
Smart Model Selector for AIKI Chat v2
Forenklet versjon av IntelligentRouter tilpasset for chat_with_aiki_v2.py

Velger optimal LLM modell basert på kompleksitet:
- Haiku 4.5 (11 kr/M) for enkle samtaler
- Sonnet 4.5 (33 kr/M) for standard samtaler
- Opus 4 (165 kr/M) kun for ekstremt komplekse oppgaver

VIKTIG: Bruker DIREKTE API-er (ikke OpenRouter) for å spare penger!
"""

import re
from typing import Dict, Any, List, Tuple, Literal
from datetime import datetime

# Provider typer
Provider = Literal['anthropic', 'openai']

class SmartModelSelector:
    """Forenklet modellvelger for AIKI chat"""

    def __init__(self):
        # Kompleksitetsindikatorer
        self.complex_indicators = [
            # Koding
            r'\b(kod|code|function|class|debug|error|implementer|refaktor)\b',
            # Analyse
            r'\b(analys|arkitektur|design|evaluér|sammenlign|vurder)\b',
            # Komplekse oppgaver
            r'\b(plan|strategi|løsning|problem|kompleks|avansert)\b',
            # Kreativt arbeid
            r'\b(skriv|lag|design|kreativ|innovasjon)\b',
        ]

        self.simple_indicators = [
            # Enkle spørsmål
            r'\b(hva|hvem|hvor|når|hvorfor|hvordan)\s+(er|var|blir|kan)\b',
            # Greeting/small talk
            r'\b(hei|hallo|hi|hello|hvordan går det|takk)\b',
            # Ja/nei spørsmål
            r'\b(er det|kan du|vil du|har du)\b',
            # Korte meldinger (under 20 ord)
        ]

        # Modellpriser (kr per million tokens)
        self.model_costs = {
            'haiku': {'input': 11, 'output': 55},
            'sonnet': {'input': 33, 'output': 165},
            'opus': {'input': 165, 'output': 825}
        }

        # Routing history for analyse
        self.routing_history = []

    def select_model(self, user_message: str, conversation_history: List[Dict] = None) -> Tuple[str, str, Provider, Dict[str, Any]]:
        """
        Velg optimal modell basert på melding

        Returns:
            (model_name, model_id, provider, reasoning)
        """

        # Analyser kompleksitet
        complexity_score = self._calculate_complexity(user_message, conversation_history)

        # Velg modell basert på score (OPPDATERT TIL 4.5!)
        if complexity_score < 0.3:
            model = 'haiku'
            model_id = 'claude-3-5-haiku-20241022'  # Direkte Anthropic API
            provider = 'anthropic'
            reason = 'Enkel samtale - bruker Haiku 4.5 for hastighet (11 kr/M, direkte API)'

        elif complexity_score < 0.7:
            model = 'sonnet'
            model_id = 'claude-sonnet-4-20250514'  # NYESTE Sonnet 4 (ikke 3.5!)
            provider = 'anthropic'
            reason = 'Standard samtale - bruker Sonnet 4 for balanse (33 kr/M, direkte API)'

        else:
            model = 'opus'
            model_id = 'claude-opus-4-20250514'  # Opus 4
            provider = 'anthropic'
            reason = 'Kompleks oppgave - bruker Opus 4 for kvalitet (165 kr/M, direkte API)'

        # Logg beslutning
        routing_decision = {
            'timestamp': datetime.now().isoformat(),
            'user_message_length': len(user_message),
            'complexity_score': complexity_score,
            'selected_model': model,
            'model_id': model_id,
            'provider': provider,
            'reasoning': reason
        }

        self.routing_history.append(routing_decision)

        # Behold kun siste 100 beslutninger
        if len(self.routing_history) > 100:
            self.routing_history = self.routing_history[-100:]

        return model, model_id, provider, routing_decision

    def _calculate_complexity(self, message: str, history: List[Dict] = None) -> float:
        """
        Beregn kompleksitetsscore (0.0 - 1.0)

        Faktorer:
        - Lengde på melding
        - Kompleksitetsindikatorer (regex patterns)
        - Samtalehistorikk
        """

        score = 0.5  # Start på midten
        message_lower = message.lower()

        # 1. Lengde (kortere = enklere)
        word_count = len(message.split())
        if word_count < 10:
            score -= 0.2  # Veldig kort = enkel
        elif word_count > 50:
            score += 0.2  # Lang melding = kompleks

        # 2. Kompleksitetsindikatorer
        complex_matches = sum(1 for pattern in self.complex_indicators
                             if re.search(pattern, message_lower, re.IGNORECASE))

        simple_matches = sum(1 for pattern in self.simple_indicators
                            if re.search(pattern, message_lower, re.IGNORECASE))

        if complex_matches > 0:
            score += 0.3 * complex_matches

        if simple_matches > 0:
            score -= 0.2 * simple_matches

        # 3. Kodeblokker eller tekniske symboler
        if '```' in message or 'def ' in message or 'class ' in message:
            score += 0.3  # Kode = kompleks

        # 4. Spørsmålstegn (mange spørsmål = ofte enklere)
        question_count = message.count('?')
        if question_count > 1:
            score -= 0.1

        # 5. Samtalehistorikk (lang samtale = mer kontekst = kompleks)
        if history and len(history) > 10:
            score += 0.1

        # Normaliser til 0.0 - 1.0
        return max(0.0, min(1.0, score))

    def get_routing_stats(self) -> Dict[str, Any]:
        """Hent statistikk over modellvalg"""

        if not self.routing_history:
            return {
                'total_requests': 0,
                'message': 'Ingen routing history enda'
            }

        total = len(self.routing_history)

        # Tell modellbruk
        model_usage = {}
        total_cost_estimate = 0.0

        for entry in self.routing_history:
            model = entry['selected_model']
            model_usage[model] = model_usage.get(model, 0) + 1

            # Estimert kostnad (antar ~1000 tokens per melding)
            total_cost_estimate += self.model_costs[model]['input'] * 0.001

        # Beregn gjennomsnittlig kompleksitet
        avg_complexity = sum(e['complexity_score'] for e in self.routing_history) / total

        # Kostnadssammenligning
        if_all_opus_cost = total * self.model_costs['opus']['input'] * 0.001
        savings_percent = ((if_all_opus_cost - total_cost_estimate) / if_all_opus_cost * 100) if if_all_opus_cost > 0 else 0

        return {
            'total_requests': total,
            'model_usage': {
                model: {
                    'count': count,
                    'percent': round(count / total * 100, 1)
                }
                for model, count in model_usage.items()
            },
            'avg_complexity': round(avg_complexity, 2),
            'estimated_cost_kr': round(total_cost_estimate, 2),
            'if_all_opus_kr': round(if_all_opus_cost, 2),
            'savings_percent': round(savings_percent, 1),
            'last_5_decisions': [
                {
                    'time': e['timestamp'],
                    'model': e['selected_model'],
                    'complexity': round(e['complexity_score'], 2),
                    'reason': e['reasoning']
                }
                for e in self.routing_history[-5:]
            ]
        }


# Singleton instance
_selector = None

def get_model_selector() -> SmartModelSelector:
    """Get singleton instance"""
    global _selector
    if _selector is None:
        _selector = SmartModelSelector()
    return _selector
