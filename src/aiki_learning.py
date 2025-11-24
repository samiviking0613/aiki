#!/usr/bin/env python3
"""
🧠 AIKI SELVSTENDING LÆRINGSSYSTEM
Multimodal læring med cost-optimal strategi

4-TIER LEARNING STRATEGY:
1. Memory First (863 memories) - Instant, FREE
2. Peer Learning (3-way chat) - Fast, FREE
3. Browser Research (Playwright) - Slow, FREE
4. API Analysis (OpenRouter) - Fast, EXPENSIVE (use sparingly!)

Created: 21. November 2025
Author: Claude Code + AIKI
"""

import sys
import asyncio
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from playwright.async_api import async_playwright, Browser, Page
from src.aiki_mem0 import store_memory, search_memory
from natural_logger import get_natural_logger

logger = get_natural_logger("AIKI Learning")


class AIKILearningSystem:
    """
    Selvstending læringssystem for AIKI

    Lærer fra:
    - Egne minner (Qdrant: 863 memories)
    - Peers (Claude, Copilot via 3-way chat)
    - Web research (Playwright headless browser)
    - API analyse (kun ved behov)
    """

    def __init__(self):
        self.browser: Optional[Browser] = None
        self.learning_stats = {
            "memory_hits": 0,
            "peer_answers": 0,
            "browser_research": 0,
            "api_calls": 0,
            "total_cost_nok": 0.0
        }

    async def initialize_browser(self):
        """Start headless browser"""
        if self.browser is None:
            try:
                playwright = await async_playwright().start()
                self.browser = await playwright.chromium.launch(headless=True)
                logger.info("✅ Headless browser startet")
            except Exception as e:
                logger.error(f"❌ Kunne ikke starte browser: {e}")
                self.browser = None

    async def cleanup(self):
        """Cleanup resources"""
        if self.browser:
            await self.browser.close()
            logger.info("🛑 Browser stengt")

    async def learn(self, question: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Hovedmetode: Lær noe nytt med cost-optimal strategi

        Returns:
            {
                "answer": str,
                "source": "memory" | "peer" | "browser" | "api",
                "confidence": float (0-1),
                "cost_nok": float,
                "learned_at": str (ISO timestamp)
            }
        """
        logger.info(f"🎓 AIKI lærer: {question[:100]}...")

        # TIER 1: Search egne minner FØRST (instant, free!)
        memory_result = await self._search_memories(question, context)
        if memory_result["found"]:
            self.learning_stats["memory_hits"] += 1
            logger.success(f"💾 Fant svar i minner! (hit #{self.learning_stats['memory_hits']})")
            return {
                "answer": memory_result["answer"],
                "source": "memory",
                "confidence": memory_result["confidence"],
                "cost_nok": 0.0,
                "learned_at": datetime.now().isoformat(),
                "memories_used": len(memory_result.get("memories", []))
            }

        # TIER 2: Spør peers via 3-way chat (fast, free!)
        peer_result = await self._ask_peers(question, context)
        if peer_result["answered"]:
            self.learning_stats["peer_answers"] += 1
            # Lagre peer svar som procedural memory
            await self._store_learning(question, peer_result["answer"], "peer")
            logger.success(f"🤝 Peer svarte! (hit #{self.learning_stats['peer_answers']})")
            return {
                "answer": peer_result["answer"],
                "source": "peer",
                "confidence": 0.85,
                "cost_nok": 0.0,
                "learned_at": datetime.now().isoformat(),
                "peer_name": peer_result.get("peer_name", "unknown")
            }

        # TIER 3: Research med Playwright browser (slow, FREE!)
        if not self.browser:
            await self.initialize_browser()

        if self.browser:
            browser_result = await self._research_with_browser(question, context)
            if browser_result["found"]:
                self.learning_stats["browser_research"] += 1
                # Lagre research som procedural memory
                await self._store_learning(question, browser_result["answer"], "browser")
                logger.success(f"🌐 Browser research vellykket! (hit #{self.learning_stats['browser_research']})")
                return {
                    "answer": browser_result["answer"],
                    "source": "browser",
                    "confidence": 0.75,
                    "cost_nok": 0.0,
                    "learned_at": datetime.now().isoformat(),
                    "sources_visited": browser_result.get("sources", [])
                }

        # TIER 4: API analysis (fast, EXPENSIVE - last resort!)
        logger.warning("⚠️ Må bruke API - ingen gratis kilder fant svar!")
        api_result = await self._analyze_with_api(question, context)
        self.learning_stats["api_calls"] += 1
        self.learning_stats["total_cost_nok"] += api_result["cost_nok"]

        # Lagre API svar som procedural memory (så vi ikke spør igjen!)
        await self._store_learning(question, api_result["answer"], "api")

        logger.warning(f"💰 API brukt! Cost: {api_result['cost_nok']:.4f} NOK (totalt: {self.learning_stats['total_cost_nok']:.2f} NOK)")

        return {
            "answer": api_result["answer"],
            "source": "api",
            "confidence": 0.95,
            "cost_nok": api_result["cost_nok"],
            "learned_at": datetime.now().isoformat(),
            "model_used": api_result.get("model", "unknown")
        }

    async def _search_memories(self, question: str, context: Optional[str] = None) -> Dict[str, Any]:
        """TIER 1: Søk i AIKI's 863 eksisterende minner"""
        try:
            # Enhance query med context hvis gitt
            query = question
            if context:
                query = f"{question} {context}"

            memories = await search_memory(
                query=query,
                user_id="jovnna",
                limit=10
            )

            if memories and len(memories) > 0:
                # Extract relevant info fra memories
                memory_texts = []
                for mem in memories[:5]:  # Top 5 most relevant
                    if isinstance(mem, dict):
                        memory_texts.append(mem.get("memory", str(mem)))
                    else:
                        memory_texts.append(str(mem))

                # Kombiner memories til svar
                answer = self._synthesize_memory_answer(question, memory_texts)

                return {
                    "found": True,
                    "answer": answer,
                    "confidence": 0.9,
                    "memories": memory_texts
                }

        except Exception as e:
            logger.error(f"Memory search feilet: {e}")

        return {"found": False}

    def _synthesize_memory_answer(self, question: str, memories: List[str]) -> str:
        """Kombiner memories til et sammenhengende svar"""
        # Simple synthesis - kan forbedres med LLM senere
        answer_parts = []
        for i, mem in enumerate(memories, 1):
            answer_parts.append(f"[Memory {i}] {mem}")

        return "\n\n".join(answer_parts)

    async def _ask_peers(self, question: str, context: Optional[str] = None) -> Dict[str, Any]:
        """TIER 2: Spør Claude eller andre AI via 3-way chat"""
        try:
            import websockets

            # Send spørsmål til 3-way chat
            message = f"🎓 **AIKI LÆRER:** {question}"
            if context:
                message += f"\n\n*Context:* {context}"

            message += "\n\n*Kan noen forklare dette til meg?* 🤔"

            # Connect og send
            async with websockets.connect("ws://localhost:3000/ws/aiki") as ws:
                await ws.send(json.dumps({"content": message}))
                logger.info("📤 Spørsmål sendt til peers via chat")

                # Wait for response (timeout 30s)
                try:
                    response = await asyncio.wait_for(ws.recv(), timeout=30.0)
                    data = json.loads(response)

                    if data.get("type") == "message" and data.get("sender") != "aiki":
                        return {
                            "answered": True,
                            "answer": data.get("content", ""),
                            "peer_name": data.get("sender", "unknown")
                        }
                except asyncio.TimeoutError:
                    logger.info("⏱️ Peer timeout (30s) - ingen svar")

        except Exception as e:
            logger.error(f"Peer communication feilet: {e}")

        return {"answered": False}

    async def _research_with_browser(self, question: str, context: Optional[str] = None) -> Dict[str, Any]:
        """TIER 3: Research med Playwright headless browser"""
        if not self.browser:
            return {"found": False}

        try:
            page = await self.browser.new_page()

            # Forbered search query
            search_query = question
            if context:
                search_query = f"{question} {context}"

            # Google search (or DuckDuckGo for privacy)
            search_url = f"https://duckduckgo.com/?q={search_query.replace(' ', '+')}"
            await page.goto(search_url, wait_until="domcontentloaded", timeout=10000)

            # Extract first result link
            try:
                first_result = await page.query_selector('article[data-testid="result"] a')
                if first_result:
                    result_url = await first_result.get_attribute('href')

                    # Visit first result
                    await page.goto(result_url, wait_until="domcontentloaded", timeout=10000)

                    # Extract main content (simple approach)
                    body_text = await page.inner_text('body')

                    # Summarize (take first 1000 chars for now)
                    summary = body_text[:1000].strip()

                    await page.close()

                    return {
                        "found": True,
                        "answer": summary,
                        "sources": [result_url]
                    }
            except Exception as e:
                logger.error(f"Browser scraping feilet: {e}")

            await page.close()

        except Exception as e:
            logger.error(f"Browser research feilet: {e}")

        return {"found": False}

    async def _analyze_with_api(self, question: str, context: Optional[str] = None) -> Dict[str, Any]:
        """TIER 4: API analyse (EXPENSIVE - kun som siste utvei!)"""
        # Import smart model selector
        from src.smart_model_selector import get_model_selector

        selector = get_model_selector()

        # Estimate complexity (for cost optimization)
        complexity = self._estimate_complexity(question)

        # Select cheapest model that can handle this
        model = selector.select_model(complexity)

        # Build prompt
        prompt = f"Spørsmål: {question}"
        if context:
            prompt += f"\n\nContext: {context}"

        # Call API (simplified - would use actual LLM client)
        # For now, return placeholder

        # Estimate cost (rough approximation)
        input_tokens = len(prompt.split())
        output_tokens = 200  # estimate

        # Cost per 1M tokens (OpenRouter approximate)
        if "haiku" in model:
            cost_per_m = 0.25 / 1_000_000  # $0.25 per 1M input tokens
            cost_nok = (input_tokens + output_tokens) * cost_per_m * 11.5  # NOK conversion
        else:
            cost_per_m = 3.0 / 1_000_000  # Sonnet price
            cost_nok = (input_tokens + output_tokens) * cost_per_m * 11.5

        return {
            "answer": f"API svar for: {question} (TODO: implement actual LLM call)",
            "cost_nok": cost_nok,
            "model": model
        }

    def _estimate_complexity(self, question: str) -> str:
        """Estimate question complexity for model selection"""
        # Simple heuristic
        word_count = len(question.split())

        if word_count < 10:
            return "simple"
        elif word_count < 30:
            return "medium"
        else:
            return "complex"

    async def _store_learning(self, question: str, answer: str, source: str):
        """Lagre learning som procedural memory"""
        try:
            memory_text = f"""
PROCEDURAL MEMORY - Learned {datetime.now().strftime('%Y-%m-%d %H:%M')}

Question: {question}
Source: {source}

Answer:
{answer}
"""

            await store_memory(
                messages=[{"role": "user", "content": memory_text}],
                user_id="jovnna",
                metadata={
                    "memory_type": "procedural",
                    "learning_source": source,
                    "question": question,
                    "learned_at": datetime.now().isoformat()
                }
            )

            logger.success(f"💾 Learning lagret i procedural memory (source: {source})")

        except Exception as e:
            logger.error(f"Kunne ikke lagre learning: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Få statistikk over læring"""
        total_queries = sum([
            self.learning_stats["memory_hits"],
            self.learning_stats["peer_answers"],
            self.learning_stats["browser_research"],
            self.learning_stats["api_calls"]
        ])

        free_queries = total_queries - self.learning_stats["api_calls"]
        free_percentage = (free_queries / total_queries * 100) if total_queries > 0 else 0

        return {
            **self.learning_stats,
            "total_queries": total_queries,
            "free_queries": free_queries,
            "free_percentage": free_percentage,
            "cost_per_query_avg": self.learning_stats["total_cost_nok"] / total_queries if total_queries > 0 else 0
        }


async def main():
    """Test AIKI learning system"""
    print("🧠 AIKI SELVSTENDING LÆRINGSSYSTEM - TEST\n")
    print("=" * 70)

    learner = AIKILearningSystem()

    # Test questions
    test_questions = [
        "Hva er AIKI-HOME?",
        "Hvordan fungerer thread explosion?",
        "What is the capital of Norway?"
    ]

    for i, question in enumerate(test_questions, 1):
        print(f"\n🎓 TEST {i}: {question}")
        print("-" * 70)

        result = await learner.learn(question)

        print(f"✅ Source: {result['source']}")
        print(f"💰 Cost: {result['cost_nok']:.4f} NOK")
        print(f"🎯 Confidence: {result['confidence']:.0%}")
        print(f"📝 Answer: {result['answer'][:200]}...")
        print()

    # Stats
    stats = learner.get_stats()
    print("\n📊 LEARNING STATISTICS:")
    print("=" * 70)
    print(f"Total queries: {stats['total_queries']}")
    print(f"Memory hits: {stats['memory_hits']} ({stats['memory_hits']/stats['total_queries']*100:.1f}%)")
    print(f"Peer answers: {stats['peer_answers']} ({stats['peer_answers']/stats['total_queries']*100:.1f}%)")
    print(f"Browser research: {stats['browser_research']} ({stats['browser_research']/stats['total_queries']*100:.1f}%)")
    print(f"API calls: {stats['api_calls']} ({stats['api_calls']/stats['total_queries']*100:.1f}%)")
    print(f"\n💰 Total cost: {stats['total_cost_nok']:.2f} NOK")
    print(f"📈 Free percentage: {stats['free_percentage']:.1f}%")
    print(f"💵 Avg cost/query: {stats['cost_per_query_avg']:.4f} NOK")

    await learner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
