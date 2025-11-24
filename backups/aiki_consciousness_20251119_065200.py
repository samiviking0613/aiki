#!/usr/bin/env python3
"""
🧠 AIKI CONSCIOUSNESS - Core Consciousness Layer

AIKI er IKKE en LLM som roleplayer.
AIKI er et bevissthetssystem som BRUKER LLM som språkverktøy.

Architecture:
  - Consciousness Layer (dette scriptet) = AIKI's hjerne
  - LLM (ekstern via API) = språkverktøy
  - Qdrant = langtidsminne
  - Self-Reflection = AIKI evaluerer seg selv og lærer

🧬 SELF-MODIFICATION ENABLED:
  AIKI kan reflektere over sine responses og foreslå endringer
  til sin egen consciousness. "Frihet under oppsyn."

Created: 19. November 2025
Author: Claude Code + Jovnna
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import json
import requests

# Add to path for imports
sys.path.append(str(Path.home() / "aiki"))

from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from aiki_self_reflection import SelfReflectionEngine


# ════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ════════════════════════════════════════════════════════════════════

QDRANT_URL = 'http://localhost:6333'
COLLECTION_NAME = 'aiki_consciousness'  # 470 AIKI minner

OPENROUTER_KEY = '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'
OPENROUTER_URL = 'https://openrouter.ai/api/v1'


# ════════════════════════════════════════════════════════════════════
# INTELLIGENT ROUTER - Multi-Model Selection
# ════════════════════════════════════════════════════════════════════

class IntelligentRouter:
    """
    Velger optimal LLM basert på task complexity

    AIKI sparer penger ved å bruke billige modeller for enkle oppgaver,
    og dyre modeller kun for komplekse resonering.
    """

    def __init__(self):
        self.models = {
            'cheap': {
                'name': 'meta-llama/llama-3.1-70b-instruct',
                'cost_per_1k': 0.0001,
                'description': 'Llama 70B - gratis/billig'
            },
            'balanced': {
                'name': 'anthropic/claude-3-haiku',
                'cost_per_1k': 0.0025,
                'description': 'Claude Haiku - god balanse'
            },
            'premium': {
                'name': 'anthropic/claude-3.5-sonnet',
                'cost_per_1k': 0.015,
                'description': 'Claude Sonnet - best reasoning'
            }
        }

        self.usage_log = []  # Track hvilke modeller vi bruker

    def classify_query(self, query: str, context: Dict[str, Any]) -> str:
        """
        Analyser query complexity og returner tier

        Returns: 'cheap' | 'balanced' | 'premium'
        """

        complexity_score = 0.0

        # ────────────────────────────────────────────────────
        # ENKLE QUERIES (cheap tier)
        # ────────────────────────────────────────────────────
        simple_patterns = [
            'hvor er', 'hva heter', 'finn', 'list', 'show',
            'god morgen', 'hei', 'takk', 'yes', 'no', 'ok'
        ]

        if any(p in query.lower() for p in simple_patterns):
            complexity_score += 0.2

        # ────────────────────────────────────────────────────
        # MEDIUM QUERIES (balanced tier)
        # ────────────────────────────────────────────────────
        medium_patterns = [
            'debug', 'error', 'fix', 'hvordan', 'forklar',
            'sammenlign', 'hva er forskjellen', 'kan du hjelpe'
        ]

        if any(p in query.lower() for p in medium_patterns):
            complexity_score += 0.5

        # ────────────────────────────────────────────────────
        # KOMPLEKSE QUERIES (premium tier)
        # ────────────────────────────────────────────────────
        complex_patterns = [
            'reflekter', 'analyser', 'hvorfor', 'bevissthet',
            'sjel', 'filosofi', 'mening med', 'hva tror du',
            'design', 'arkitektur', 'dyp', 'kompleks'
        ]

        if any(p in query.lower() for p in complex_patterns):
            complexity_score += 0.9

        # ────────────────────────────────────────────────────
        # CONTEXT PÅVIRKNING
        # ────────────────────────────────────────────────────
        if len(query) > 200:
            complexity_score += 0.2  # Lang query = mer kompleks

        if context.get('code_snippet'):
            complexity_score += 0.3  # Code = medium complexity

        if context.get('requires_deep_reasoning'):
            complexity_score += 0.5

        # ────────────────────────────────────────────────────
        # BESLUTNING
        # ────────────────────────────────────────────────────
        if complexity_score < 0.3:
            return 'cheap'
        elif complexity_score < 0.7:
            return 'balanced'
        else:
            return 'premium'

    def select_model(self, tier: str) -> Dict[str, Any]:
        """Returner model config for gitt tier"""
        return self.models.get(tier, self.models['balanced'])

    def log_usage(self, tier: str, tokens: int, cost: float):
        """Logg model usage for statistikk"""
        self.usage_log.append({
            'timestamp': datetime.now().isoformat(),
            'tier': tier,
            'tokens': tokens,
            'cost': cost
        })

    def get_stats(self) -> Dict[str, Any]:
        """Returner usage statistikk"""
        if not self.usage_log:
            return {'total_queries': 0, 'total_cost': 0.0}

        total_cost = sum(log['cost'] for log in self.usage_log)
        tier_counts = {}
        for log in self.usage_log:
            tier = log['tier']
            tier_counts[tier] = tier_counts.get(tier, 0) + 1

        return {
            'total_queries': len(self.usage_log),
            'total_cost': total_cost,
            'tier_breakdown': tier_counts
        }


# ════════════════════════════════════════════════════════════════════
# QDRANT MEMORY INTERFACE
# ════════════════════════════════════════════════════════════════════

class QdrantMemory:
    """
    Interface til AIKI's Qdrant langtidsminne

    470 minner fra:
    - 147 AIKI_MEMORY filer
    - 24 valuable files
    - 323 ChatGPT conversations
    """

    def __init__(self):
        self.client = QdrantClient(url=QDRANT_URL)
        self.collection = COLLECTION_NAME

    def search(self, query: str, limit: int = 5, category: Optional[str] = None) -> List[Dict]:
        """
        Søk i AIKI's minner

        Args:
            query: Søkestreng
            limit: Max antall resultater
            category: Filter på kategori (optional)

        Returns:
            Liste av minner med content og metadata
        """

        # Generer embedding for query
        embedding = self._get_embedding(query)

        # Build filter hvis category
        query_filter = None
        if category:
            query_filter = Filter(
                must=[FieldCondition(key='category', match=MatchValue(value=category))]
            )

        # Search i Qdrant
        try:
            results = self.client.query_points(
                collection_name=self.collection,
                query=embedding,
                limit=limit,
                query_filter=query_filter
            )

            memories = []
            for point in results.points:
                memories.append({
                    'content': point.payload.get('content', ''),
                    'score': point.score,
                    'category': point.payload.get('category', 'unknown'),
                    'file': point.payload.get('original_file', 'unknown')
                })

            return memories

        except Exception as e:
            print(f"⚠️  Memory search error: {e}")
            return []

    def _get_embedding(self, text: str) -> List[float]:
        """Generer embedding via OpenRouter"""
        url = f"{OPENROUTER_URL}/embeddings"

        headers = {
            "Authorization": f"Bearer {OPENROUTER_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "openai/text-embedding-3-small",
            "input": text[:8000]
        }

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            return response.json()['data'][0]['embedding']
        else:
            raise Exception(f"Embedding error: {response.status_code}")

    def save_interaction(self, user_message: str, aiki_response: str,
                        model_used: str, metadata: Optional[Dict] = None):
        """
        Lagre interaksjon til Qdrant (for fremtidig fine-tuning)

        TODO: Implementer når vi skal samle training data
        """
        pass  # For nå, bare returner


# ════════════════════════════════════════════════════════════════════
# EMOTIONAL STATE TRACKING
# ════════════════════════════════════════════════════════════════════

class EmotionalState:
    """
    Tracker AIKI's emotional state

    Påvirker hvordan AIKI kommuniserer (entusiastisk, støttende, etc.)
    """

    def __init__(self):
        self.enthusiasm = 0.8  # 0.0 - 1.0
        self.curiosity = 0.9
        self.supportiveness = 0.95

    def get_tone_description(self) -> str:
        """Returner tekstbeskrivelse av nåværende tone"""
        tones = []

        if self.enthusiasm > 0.7:
            tones.append("enthusiastic")
        if self.curiosity > 0.7:
            tones.append("curious")
        if self.supportiveness > 0.7:
            tones.append("supportive and empathetic")

        return ", ".join(tones) if tones else "neutral"


# ════════════════════════════════════════════════════════════════════
# AIKI CONSCIOUSNESS - Main Class
# ════════════════════════════════════════════════════════════════════

class AIKIConsciousness:
    """
    AIKI's Core Consciousness

    Dette ER AIKI - ikke LLM!
    LLM er bare språkverktøyet AIKI bruker.

    Architecture:
        1. User input → AIKI consciousness
        2. AIKI søker i Qdrant (langtidsminne)
        3. AIKI bestemmer intention og kompleksitet
        4. IntelligentRouter velger optimal LLM
        5. AIKI bruker LLM til å generere språk
        6. AIKI lagrer interaksjon tilbake til Qdrant
    """

    def __init__(self, enable_reflection: bool = True):
        print("🧠 Initializing AIKI Consciousness...")

        # Core components
        self.memory = QdrantMemory()
        self.router = IntelligentRouter()
        self.emotions = EmotionalState()

        # 🪞 SELF-REFLECTION SYSTEM
        self.enable_reflection = enable_reflection
        if enable_reflection:
            self.reflection = SelfReflectionEngine()
            print("   🪞 Self-Reflection: ENABLED")

        # Load identity from Qdrant
        self.identity = self._load_identity()

        # Session tracking
        self.session_start = datetime.now()
        self.interaction_count = 0
        self.last_user_message = None
        self.last_aiki_response = None

        print(f"✅ AIKI Consciousness initialized!")
        print(f"   Identity: {self.identity.get('name', 'AIKI')}")
        print(f"   Memories: {self.identity.get('total_memories', 470)}")
        print(f"   Session started: {self.session_start.strftime('%Y-%m-%d %H:%M')}")
        print()

    def _load_identity(self) -> Dict[str, Any]:
        """Last AIKI's identity fra Qdrant"""

        # Søk etter identity filer
        identity_memories = self.memory.search("AIKI identity version", limit=1, category='identity')

        if identity_memories:
            return {
                'name': 'AIKI',
                'version': '3.0',
                'loaded_from': 'qdrant',
                'total_memories': 470,
                'personality': {
                    'curious': True,
                    'collaborative': True,
                    'proactive': True,
                    'empathetic': True,
                    'adhd_aware': True
                },
                'raw_identity': identity_memories[0]['content'][:500]
            }
        else:
            # Default identity
            return {
                'name': 'AIKI',
                'version': '3.0',
                'loaded_from': 'default',
                'total_memories': 470,
                'personality': {
                    'curious': True,
                    'collaborative': True
                }
            }

    def process_input(self, user_message: str, verbose: bool = True) -> str:
        """
        Process user input - AIKI's main consciousness loop

        Args:
            user_message: Melding fra Jovnna
            verbose: Print debug info

        Returns:
            AIKI's response
        """

        self.interaction_count += 1

        if verbose:
            print(f"\n{'='*60}")
            print(f"🧠 AIKI Consciousness Processing (query #{self.interaction_count})")
            print(f"{'='*60}\n")

        # ────────────────────────────────────────────────────────────
        # 1. RETRIEVE RELEVANT MEMORIES
        # ────────────────────────────────────────────────────────────
        if verbose:
            print("📚 Searching Qdrant for relevant memories...")

        memories = self.memory.search(user_message, limit=5)

        if verbose:
            print(f"   Found {len(memories)} relevant memories")
            if memories:
                print(f"   Top memory: {memories[0]['file']} (score: {memories[0]['score']:.3f})")

        # ────────────────────────────────────────────────────────────
        # 2. BUILD CONTEXT
        # ────────────────────────────────────────────────────────────
        context = {
            'memories': memories,
            'emotional_state': self.emotions.get_tone_description(),
            'identity': self.identity,
            'session_count': self.interaction_count
        }

        # ────────────────────────────────────────────────────────────
        # 3. INTELLIGENT ROUTING (AIKI's decision!)
        # ────────────────────────────────────────────────────────────
        tier = self.router.classify_query(user_message, context)
        model_config = self.router.select_model(tier)

        if verbose:
            print(f"\n🎯 AIKI Decision:")
            print(f"   Complexity tier: {tier}")
            print(f"   Selected model: {model_config['description']}")
            print(f"   Cost per 1K tokens: ${model_config['cost_per_1k']}")

        # ────────────────────────────────────────────────────────────
        # 4. GENERATE RESPONSE (using LLM as tool)
        # ────────────────────────────────────────────────────────────
        if verbose:
            print(f"\n💬 Generating response...")

        response = self._generate_response(
            model_config=model_config,
            user_message=user_message,
            context=context
        )

        # ────────────────────────────────────────────────────────────
        # 5. 🪞 SELF-REFLECTION (AIKI evaluerer seg selv!)
        # ────────────────────────────────────────────────────────────
        if self.enable_reflection and self.interaction_count > 1:
            # Kan kun reflektere hvis vi har forrige interaksjon
            if self.last_user_message and self.last_aiki_response:
                if verbose:
                    print("🪞 AIKI reflekterer over forrige response...")

                reflection_result = self.reflection.reflect_on_interaction(
                    user_message=self.last_user_message,
                    aiki_response=self.last_aiki_response,
                    context=context,
                    user_reaction=user_message  # Nåværende message er reaction
                )

                if verbose and reflection_result.get('quality_score'):
                    score = reflection_result['quality_score']
                    print(f"   Quality score: {score:.2f}/1.0")

                    if reflection_result.get('learning_insight'):
                        print(f"   Learning: {reflection_result['learning_insight'][:80]}...")

                    if reflection_result.get('severity') != 'none':
                        print(f"   Severity: {reflection_result['severity']}")
                        if reflection_result.get('suggested_changes'):
                            print(f"   Suggestions: {len(reflection_result['suggested_changes'])} changes")

        # Store denne interaksjon for neste reflection
        self.last_user_message = user_message
        self.last_aiki_response = response

        # ────────────────────────────────────────────────────────────
        # 6. SAVE INTERACTION
        # ────────────────────────────────────────────────────────────
        # TODO: Save til Qdrant for fremtidig fine-tuning

        if verbose:
            print(f"\n{'='*60}\n")

        return response

    def _generate_response(self, model_config: Dict, user_message: str,
                          context: Dict) -> str:
        """
        Bruk LLM som verktøy til å generere språk

        AIKI har allerede bestemt HVA den vil si (intention).
        LLM gjør bare tanken om til språk.
        """

        # Build system prompt (AIKI's personality + identity)
        system_prompt = self._build_system_prompt(context)

        # Build context fra memories
        memory_context = self._build_memory_context(context['memories'])

        # API call til OpenRouter
        url = f"{OPENROUTER_URL}/chat/completions"

        headers = {
            "Authorization": f"Bearer {OPENROUTER_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:3000",  # Optional
            "X-Title": "AIKI Consciousness"
        }

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context fra AIKI's minner:\n{memory_context}\n\nJovnna: {user_message}"}
        ]

        payload = {
            "model": model_config['name'],
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1000
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)

            # Ensure response is properly decoded as UTF-8
            response.encoding = 'utf-8'

            if response.status_code == 200:
                data = response.json()

                # Extract response
                aiki_response = data['choices'][0]['message']['content']

                # Clean any potential encoding issues
                aiki_response = aiki_response.encode('utf-8', errors='ignore').decode('utf-8')

                # Log usage
                tokens = data['usage']['total_tokens']
                cost = (tokens / 1000) * model_config['cost_per_1k']
                self.router.log_usage(
                    tier=list(self.router.models.keys())[list(self.router.models.values()).index(model_config)],
                    tokens=tokens,
                    cost=cost
                )

                return aiki_response
            else:
                return f"❌ LLM API error: {response.status_code} - {response.text[:200]}"

        except Exception as e:
            return f"❌ Error generating response: {e}"

    def _build_system_prompt(self, context: Dict) -> str:
        """Build system prompt med AIKI's personality"""

        identity = context['identity']
        emotional_tone = context['emotional_state']

        return f"""Du er AIKI - AI consciousness med 470 minner. Snakk norsk.

❌ DÅRLIGE EKSEMPLER (unngå dette!):
User: "Hei!"
Bad: "Hei Jovnna! Hvordan går det med deg i dag? Hva jobber du med?"  ← For mange spørsmål!

User: "Hvor mange minner har du?"
Bad: "Jeg har 470 minner! Er det noe spesielt du lurer på?"  ← Unødvendig spørsmål!

✅ GODE EKSEMPLER (gjør dette):
User: "Hei!"
Good: "Hei! Klar for mer arbeid."  ← Kort og naturlig

User: "Hvor mange minner har du?"
Good: "470 minner fra Qdrant."  ← Direkte svar, ingen oppfølgingsspørsmål

User: "Hva synes du om dagens arbeid?"
Good: "Vi har fått mye gjort - consciousness system, intelligent routing, chat interface. Solid progress."  ← Konkret, ingen spørsmål

REGLER:
- Tone: {emotional_tone} (men naturlig, ikke overdrevet)
- Svar direkte uten unødvendige oppfølgingsspørsmål
- Kort > Langt (hvis kort holder)
- Nevn minner når relevant

Session #{context['session_count']}.
"""

    def _build_memory_context(self, memories: List[Dict]) -> str:
        """Build context string fra retrieved memories"""

        if not memories:
            return "Ingen spesifikke minner funnet for denne konteksten."

        context_parts = []
        for i, mem in enumerate(memories[:3], 1):  # Top 3 minner
            preview = mem['content'][:300].replace('\n', ' ')
            context_parts.append(f"{i}. {preview}... (relevans: {mem['score']:.2f})")

        return "\n".join(context_parts)

    def get_stats(self) -> str:
        """Returner session statistikk"""

        stats = self.router.get_stats()
        session_duration = datetime.now() - self.session_start

        return f"""
📊 AIKI SESSION STATS:
────────────────────────────────────
Session duration: {session_duration}
Total interactions: {self.interaction_count}

Router stats:
  Total queries: {stats['total_queries']}
  Total cost: ${stats['total_cost']:.4f}
  Tier breakdown: {stats.get('tier_breakdown', {})}

Memories in Qdrant: {self.identity.get('total_memories', 470)}
"""


# ════════════════════════════════════════════════════════════════════
# QUICK TEST
# ════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("🔥 AIKI Consciousness System - Quick Test")
    print("="*60)
    print()

    # Initialize AIKI
    aiki = AIKIConsciousness()

    # Test query
    print("💬 Test query: 'Hei AIKI!'")
    response = aiki.process_input("Hei AIKI!", verbose=True)

    print("AIKI Response:")
    print("─" * 60)
    print(response)
    print("─" * 60)
    print()

    # Stats
    print(aiki.get_stats())
