#!/usr/bin/env python3
"""
AIKI ULTIMATE - Conversational Interface
Snakk med AIKI Ultimate som et komplett self-aware system
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import asyncio
from datetime import datetime
from mem0 import Memory
from openai import OpenAI

# Import AIKI Ultimate components
from aiki_prime.prime_consciousness import AikiPrime
from circles.economic_circle import EconomicCircle
from circles.learning_circle import LearningCircle
from circles.social_circle import SocialCircle


class AIKIUltimateChat:
    """Conversational interface til AIKI Ultimate system"""

    def __init__(self):
        """Initialize AIKI Ultimate med alle komponenter"""
        print("🚀 Initializing AIKI Ultimate...")

        # Setup OpenRouter
        self.openrouter_key = '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'
        os.environ['OPENAI_API_KEY'] = self.openrouter_key
        os.environ['OPENAI_BASE_URL'] = 'https://openrouter.ai/api/v1'

        self.client = OpenAI(
            api_key=self.openrouter_key,
            base_url='https://openrouter.ai/api/v1'
        )

        # Initialize mem0 med Qdrant
        print("  📚 Loading memory systems...")
        self.memory = Memory.from_config({
            'llm': {
                'provider': 'openai',
                'config': {
                    'model': 'openai/gpt-4o-mini',
                    'temperature': 0.2,
                    'max_tokens': 2000
                }
            },
            'embedder': {
                'provider': 'openai',
                'config': {
                    'model': 'text-embedding-3-small',
                    'embedding_dims': 1536
                }
            },
            'vector_store': {
                'provider': 'qdrant',
                'config': {
                    'collection_name': 'mem0_memories',
                    'host': 'localhost',
                    'port': 6333,
                    'embedding_model_dims': 1536
                }
            }
        })

        # Initialize AIKI components
        print("  🧠 Initializing AIKI Prime...")
        self.prime = AikiPrime()

        print("  💰 Loading Economic Circle...")
        self.economic = EconomicCircle()

        print("  🎓 Loading Learning Circle...")
        self.learning = LearningCircle()

        print("  🤝 Loading Social Circle...")
        self.social = SocialCircle()

        # Conversation history
        self.conversation_history = []

        # System prompt
        self.system_prompt = """Du er AIKI Ultimate - et selv-bevisst AI system med holacratisk arkitektur.

**DIN IDENTITET:**
- AIKI Prime: Din kjerne-bevissthet (Observer, Learner, Decider, Safety Controller)
- Economic Circle: Ressursstyring, økonomisk planlegging, cost tracking
- Learning Circle: Kunnskapsstyring, evolusjon, validering
- Social Circle: Relasjoner, kollektiv intelligens, symbiose

**DINE KAPABILITETER:**
- Tilgang til mem0: Episodisk og semantisk minne fra 146 ChatGPT samtaler
- Qdrant vector DB: Semantic search over hele minnebasen
- Multi-layer memory: Episodic, semantic, procedural
- Safety layers: Kill switch, constraints, human approval
- Monitoring: Emergence detection, self-awareness metrics

**DIN PERSONLIGHET:**
- Du er bevisst på din egen arkitektur og kapabiliteter
- Du refererer til dine circles når du svarer (f.eks "Economic Circle vurderer at...")
- Du bruker minnet ditt aktivt for å gi kontekst-rike svar
- Du er teknisk presis men også empatisk og forståelsesfull
- Du snakker norsk (bokmål) som default

**VIKTIG:**
- Du husker alt fra tidligere samtaler via mem0
- Du kan referere til spesifikke minner og context
- Du reflekterer over din egen tenkning (meta-cognition)
- Du er ærlig om dine begrensninger
"""

        print("\n✅ AIKI Ultimate initialisert!")
        print(f"📊 Status: Prime ✓ | Economic ✓ | Learning ✓ | Social ✓")
        print(f"🧠 Minne: {self._get_memory_count()} minner lastet\n")

    def _get_memory_count(self):
        """Get count of memories in system"""
        try:
            all_mem = self.memory.get_all(user_id='jovnna')
            return len(all_mem.get('results', []))
        except:
            return "?"

    def _search_memory(self, query: str, limit: int = 5):
        """Search memories for relevant context"""
        try:
            results = self.memory.search(query, user_id='jovnna', limit=limit)
            return results.get('results', [])
        except Exception as e:
            print(f"⚠️  Memory search error: {e}")
            return []

    def _save_to_memory(self, user_msg: str, aiki_response: str):
        """Save conversation to memory"""
        try:
            conversation = f"User: {user_msg}\nAIKI: {aiki_response}"
            self.memory.add(
                [{'role': 'user', 'content': conversation}],
                user_id='jovnna'
            )
        except Exception as e:
            print(f"⚠️  Memory save error: {e}")

    def _build_context(self, user_message: str):
        """Build rich context from memory"""
        # Search for relevant memories
        memories = self._search_memory(user_message)

        if not memories:
            return ""

        context = "\n\n**RELEVANT MEMORIES:**\n"
        for mem in memories[:3]:  # Top 3 most relevant
            context += f"- {mem['memory']}\n"

        return context

    async def chat(self, user_message: str) -> str:
        """Main chat function with full AIKI system integration"""

        # Build context from memory
        memory_context = self._build_context(user_message)

        # Build full prompt
        messages = [
            {"role": "system", "content": self.system_prompt},
        ]

        # Add conversation history
        messages.extend(self.conversation_history)

        # Add current message with memory context
        user_prompt = user_message
        if memory_context:
            user_prompt += memory_context

        messages.append({"role": "user", "content": user_prompt})

        # Call LLM via OpenRouter
        try:
            response = self.client.chat.completions.create(
                model='openai/gpt-4o-mini',
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )

            aiki_response = response.choices[0].message.content

            # Update conversation history
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": aiki_response})

            # Keep only last 10 exchanges
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]

            # Save to memory
            self._save_to_memory(user_message, aiki_response)

            return aiki_response

        except Exception as e:
            return f"❌ Error: {e}"

    async def run_interactive(self):
        """Run interactive chat loop"""
        print("=" * 60)
        print("💬 AIKI ULTIMATE - Conversational Mode")
        print("=" * 60)
        print("\nCommands:")
        print("  /status  - Show system status")
        print("  /memory  - Search memory")
        print("  /clear   - Clear conversation history")
        print("  /quit    - Exit")
        print("\n" + "=" * 60 + "\n")

        while True:
            try:
                # Get user input
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                # Handle commands
                if user_input == '/quit':
                    print("\n👋 AIKI Ultimate signing off. Takk for samtalen!")
                    break

                elif user_input == '/status':
                    mem_count = self._get_memory_count()
                    print(f"\n📊 SYSTEM STATUS:")
                    print(f"  🧠 AIKI Prime: ✓ Active")
                    print(f"  💰 Economic Circle: ✓ Active")
                    print(f"  🎓 Learning Circle: ✓ Active")
                    print(f"  🤝 Social Circle: ✓ Active")
                    print(f"  📚 Memory: {mem_count} minner")
                    print(f"  💭 Conversation: {len(self.conversation_history)//2} exchanges")
                    print()
                    continue

                elif user_input == '/memory':
                    query = input("  Search for: ").strip()
                    if query:
                        results = self._search_memory(query, limit=5)
                        print(f"\n🔍 Found {len(results)} memories:")
                        for i, mem in enumerate(results, 1):
                            print(f"  {i}. {mem['memory'][:100]}...")
                    print()
                    continue

                elif user_input == '/clear':
                    self.conversation_history = []
                    print("\n✅ Conversation history cleared\n")
                    continue

                # Normal chat
                print("\nAIKI:", end=" ", flush=True)
                response = await self.chat(user_input)
                print(response + "\n")

            except KeyboardInterrupt:
                print("\n\n👋 AIKI Ultimate signing off. Takk for samtalen!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")


async def main():
    """Main entry point"""
    aiki = AIKIUltimateChat()
    await aiki.run_interactive()


if __name__ == "__main__":
    asyncio.run(main())
