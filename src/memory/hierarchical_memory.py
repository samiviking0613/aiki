#!/usr/bin/env python3
"""
AIKI HIERARCHICAL MEMORY SYSTEM

Token-efficient memory retrieval with 3 levels:
- L0: Index (always loaded, ~200 tokens)
- L1: Summaries (loaded on relevant match, ~500 tokens)
- L2: Full details (loaded on-demand)

Also includes Sensory Memory - the 10th memory type for human interaction.

Usage:
    from src.memory.hierarchical_memory import (
        HierarchicalMemory,
        store_sensory_memory,
        get_sensory_context
    )

    hm = HierarchicalMemory()

    # Get token-efficient context for a query
    context = await hm.get_smart_context("user feels cold inside")
    # Returns: relevant memories at appropriate detail level
"""

import os
import asyncio
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import logging

# Setup
os.environ['OPENAI_API_KEY'] = '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'
os.environ['OPENAI_BASE_URL'] = 'https://openrouter.ai/api/v1'

from mem0 import Memory

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIG
# ============================================================================

MEM0_CONFIG = {
    'llm': {
        'provider': 'openai',
        'config': {
            'model': 'openai/gpt-4o-mini',
            'temperature': 0.2,
            'max_tokens': 2000,
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
            'url': 'http://localhost:6333',
            'embedding_model_dims': 1536
        }
    }
}


# ============================================================================
# SENSORY MEMORY - 10th Memory Type
# ============================================================================

class SensoryCategory(Enum):
    """Categories of sensory experiences"""
    TEMPERATURE = "temperature"      # varme, kulde
    TEXTURE = "texture"              # glatt, ru, myk, hard
    PRESSURE = "pressure"            # tyngde, letthet, trykk
    MOVEMENT = "movement"            # stillstand, fart, svimmelhet
    PAIN = "pain"                    # skarp, dump, brennende
    COMFORT = "comfort"              # behagelig, ubehagelig


# Pre-loaded sensory-to-meaning mappings (token-efficient)
SENSORY_MAPPINGS: Dict[str, Dict[str, List[str]]] = {
    "temperature": {
        "varme": ["trygghet", "kjærlighet", "komfort", "aksept", "omsorg"],
        "kulde": ["avvisning", "ensomhet", "frykt", "nummenhet", "isolasjon"],
        "brennende": ["sinne", "skam", "intens smerte", "desperasjon"],
        "frysende": ["angst", "sjokk", "paralyse", "handlingslammelse"],
    },
    "texture": {
        "glatt": ["letthet", "friksjonsfritt", "overfladisk", "skjørt"],
        "ru": ["motstand", "ubehag", "virkelighet", "autentisk"],
        "myk": ["trøst", "sårbarhet", "åpenhet", "mottakelighet"],
        "hard": ["motstand", "beskyttelse", "lukkethet", "styrke"],
        "klissete": ["ubehag", "vanskelig å slippe", "komplisert"],
    },
    "pressure": {
        "tyngde": ["ansvar", "depresjon", "byrde", "overveldet", "utmattelse"],
        "letthet": ["frihet", "glede", "lettelse", "håp", "energi"],
        "trykk": ["stress", "press", "forventning", "angst"],
        "ekspansjon": ["vekst", "frigjøring", "muligheter", "åpenhet"],
    },
    "movement": {
        "stillstand": ["fastlåst", "stagnasjon", "venting", "meditasjon"],
        "fart": ["fremgang", "kaos", "stress", "effektivitet"],
        "svimmelhet": ["forvirring", "overveldelse", "tap av kontroll"],
        "flyt": ["harmoni", "mestringsfølelse", "fokus", "flow-state"],
        "sirup": ["tregt", "tungt", "frustrerende", "krevende"],
    },
    "pain": {
        "skarp": ["akutt problem", "plutselig innsikt", "krise"],
        "dump": ["kronisk", "vedvarende", "bakgrunn", "nummenhet"],
        "brennende": ["intens", "akutt", "desperat", "uholdbar"],
        "stikkende": ["påminnelse", "skyldfølelse", "anger"],
    },
    "comfort": {
        "behagelig": ["tilfredshet", "aksept", "ro", "trygghet"],
        "ubehagelig": ["motstand", "advarsel", "behov for endring"],
        "kløe": ["irritasjon", "utålmodighet", "noe som må adresseres"],
    }
}


@dataclass
class SensoryMemory:
    """A sensory memory entry"""
    sensation: str              # e.g., "kulde"
    category: SensoryCategory
    meanings: List[str]         # emotional/mental meanings
    contexts: List[str]         # example contexts where used
    intensity_scale: str        # how intensity affects meaning
    cultural_notes: Optional[str] = None


async def store_sensory_memory(
    sensation: str,
    category: str,
    meanings: List[str],
    example_contexts: List[str],
    intensity_note: str = "",
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Store a sensory memory mapping.

    Args:
        sensation: The sensory word (e.g., "kulde", "tyngde")
        category: Category from SensoryCategory
        meanings: List of emotional/mental meanings
        example_contexts: Example phrases/contexts
        intensity_note: How intensity changes meaning
        metadata: Additional metadata

    Example:
        await store_sensory_memory(
            sensation="kulde",
            category="temperature",
            meanings=["avvisning", "ensomhet", "frykt"],
            example_contexts=[
                "føler meg kald inne i meg",
                "fikk kald skulder",
                "isende blikk"
            ],
            intensity_note="Sterkere kulde = sterkere avvisning/isolasjon"
        )
    """
    memory = Memory.from_config(MEM0_CONFIG)

    content = f"""SENSORY MEMORY: {sensation.upper()} ({category})

Emotional/Mental Meanings: {', '.join(meanings)}

Example Contexts:
{chr(10).join(f'- "{ctx}"' for ctx in example_contexts)}

Intensity: {intensity_note or 'Linear scaling'}
"""

    sensory_metadata = {
        "type": "sensory",
        "sensation": sensation,
        "category": category,
        "meanings": meanings,
        "timestamp": datetime.now().isoformat()
    }

    if metadata:
        sensory_metadata.update(metadata)

    result = memory.add(
        [{"role": "user", "content": content}],
        user_id="jovnna",
        metadata=sensory_metadata
    )

    logger.info(f"🌡️ Stored sensory memory: {sensation} ({category})")
    return result


def get_sensory_context(text: str) -> Dict[str, Any]:
    """
    Quick lookup of sensory meanings from pre-loaded mappings.
    NO API call needed - instant, zero tokens.

    Args:
        text: User input text

    Returns:
        Dict with detected sensory words and their meanings
    """
    text_lower = text.lower()
    detected = {}

    for category, mappings in SENSORY_MAPPINGS.items():
        for sensation, meanings in mappings.items():
            if sensation in text_lower:
                detected[sensation] = {
                    "category": category,
                    "meanings": meanings,
                    "relevance": "direct_match"
                }

    return {
        "detected_sensory": detected,
        "has_sensory": len(detected) > 0,
        "summary": _summarize_sensory(detected) if detected else None
    }


def _summarize_sensory(detected: Dict) -> str:
    """Create a brief summary of detected sensory context"""
    if not detected:
        return ""

    parts = []
    for sensation, data in detected.items():
        meanings = data["meanings"][:3]  # Top 3
        parts.append(f"{sensation}→{'/'.join(meanings)}")

    return "; ".join(parts)


# ============================================================================
# HIERARCHICAL MEMORY SYSTEM
# ============================================================================

@dataclass
class MemoryIndex:
    """L0: Lightweight index entry"""
    cluster_id: str
    category: str
    keywords: List[str]
    memory_count: int
    last_updated: datetime

    def to_compact(self) -> str:
        """Compact representation (~20 tokens)"""
        return f"{self.category}:{','.join(self.keywords[:5])}({self.memory_count})"


@dataclass
class MemorySummary:
    """L1: Summary of a memory cluster"""
    cluster_id: str
    summary: str           # 1-2 sentences
    key_facts: List[str]   # Top 3-5 facts
    memory_ids: List[str]  # References to full memories

    def to_compact(self) -> str:
        """Compact representation (~50-100 tokens)"""
        facts = "; ".join(self.key_facts[:3])
        return f"{self.summary} [{facts}]"


class HierarchicalMemory:
    """
    Token-efficient memory retrieval system.

    Always loads L0 index (~200 tokens)
    Loads L1 summaries for relevant clusters (~500 tokens)
    Loads L2 full memories only when needed
    """

    def __init__(self):
        self.memory = Memory.from_config(MEM0_CONFIG)
        self._index_cache: Dict[str, MemoryIndex] = {}
        self._summary_cache: Dict[str, MemorySummary] = {}

        # Thresholds
        self.l1_threshold = 0.6  # Minimum score to load L1
        self.l2_threshold = 0.8  # Minimum score to load L2
        self.max_l2_memories = 3  # Max full memories to load

    async def get_smart_context(
        self,
        query: str,
        user_id: str = "jovnna",
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """
        Get token-efficient context for a query.

        Returns appropriate level of detail based on relevance.

        Args:
            query: User's input/question
            user_id: User ID
            max_tokens: Approximate max tokens to return

        Returns:
            Dict with:
            - sensory_context: Instant sensory mappings (0 tokens from API)
            - l0_index: Always included, relevant categories
            - l1_summaries: Included if relevant clusters found
            - l2_details: Included only for highly relevant memories
            - estimated_tokens: Approximate token count
        """
        result = {
            "query": query,
            "sensory_context": None,
            "l0_index": [],
            "l1_summaries": [],
            "l2_details": [],
            "estimated_tokens": 0
        }

        # Step 1: Instant sensory lookup (0 API tokens)
        sensory = get_sensory_context(query)
        if sensory["has_sensory"]:
            result["sensory_context"] = sensory
            result["estimated_tokens"] += 50  # Approximate

        # Step 2: Vector search for relevant memories
        search_results = self.memory.search(
            query=query,
            user_id=user_id,
            limit=10
        )

        if not search_results or 'results' not in search_results:
            return result

        memories = search_results['results']

        # Step 3: Categorize by relevance
        high_relevance = []  # Score > 0.8 -> L2
        medium_relevance = []  # Score 0.6-0.8 -> L1
        low_relevance = []  # Score < 0.6 -> L0 only

        for mem in memories:
            if mem is None:
                continue
            score = mem.get('score', 0)
            if score >= self.l2_threshold:
                high_relevance.append(mem)
            elif score >= self.l1_threshold:
                medium_relevance.append(mem)
            else:
                low_relevance.append(mem)

        # Step 4: Build response at appropriate levels

        # L0: Index (always included, minimal tokens)
        categories = set()
        for mem in memories:
            if mem is None:
                continue
            metadata = mem.get('metadata') or {}
            mem_type = metadata.get('type', 'general')
            categories.add(mem_type)

        result["l0_index"] = list(categories)
        result["estimated_tokens"] += len(categories) * 10

        # L1: Summaries for medium relevance
        for mem in medium_relevance[:5]:
            summary = self._create_summary(mem)
            result["l1_summaries"].append(summary)
            result["estimated_tokens"] += 80

        # L2: Full details for high relevance (limited)
        for mem in high_relevance[:self.max_l2_memories]:
            result["l2_details"].append({
                "memory": mem.get('memory', ''),
                "score": mem.get('score', 0),
                "metadata": mem.get('metadata', {})
            })
            # Estimate tokens from memory length
            mem_text = mem.get('memory', '')
            result["estimated_tokens"] += len(mem_text.split()) * 1.3

        return result

    def _create_summary(self, memory: Dict) -> Dict[str, Any]:
        """Create L1 summary from a memory"""
        if memory is None:
            return {"summary": "", "type": "unknown", "score": 0}

        mem_text = memory.get('memory', '') or ''
        metadata = memory.get('metadata') or {}

        # Simple summarization: first sentence + type
        first_sentence = mem_text.split('.')[0] if '.' in mem_text else mem_text[:100]

        return {
            "summary": first_sentence,
            "type": metadata.get('type', 'general') if metadata else 'general',
            "score": memory.get('score', 0)
        }

    async def build_index(self, user_id: str = "jovnna") -> Dict[str, Any]:
        """
        Build/rebuild the L0 index from all memories.
        Run this periodically (daily/weekly).

        Returns:
            Stats about the index
        """
        logger.info("📊 Building hierarchical memory index...")

        # Get all memories
        all_memories = self.memory.get_all(user_id=user_id)

        if not all_memories:
            return {"status": "empty", "count": 0}

        # Group by type/category
        clusters: Dict[str, List] = {}

        for mem in all_memories:
            metadata = mem.get('metadata', {})
            mem_type = metadata.get('type', 'general')

            if mem_type not in clusters:
                clusters[mem_type] = []
            clusters[mem_type].append(mem)

        # Build index entries
        self._index_cache = {}
        for category, memories in clusters.items():
            # Extract keywords from memories
            keywords = self._extract_keywords(memories)

            index = MemoryIndex(
                cluster_id=f"cluster_{category}",
                category=category,
                keywords=keywords,
                memory_count=len(memories),
                last_updated=datetime.now()
            )
            self._index_cache[category] = index

        # Store index in memory for persistence
        index_content = self._serialize_index()
        self.memory.add(
            [{"role": "user", "content": index_content}],
            user_id=user_id,
            metadata={
                "type": "memory_index",
                "version": "1.0",
                "cluster_count": len(clusters),
                "total_memories": len(all_memories),
                "generated_at": datetime.now().isoformat()
            }
        )

        logger.info(f"✅ Index built: {len(clusters)} clusters, {len(all_memories)} memories")

        return {
            "status": "success",
            "clusters": len(clusters),
            "total_memories": len(all_memories),
            "categories": list(clusters.keys())
        }

    def _extract_keywords(self, memories: List[Dict], max_keywords: int = 10) -> List[str]:
        """Extract top keywords from a list of memories"""
        word_freq: Dict[str, int] = {}

        stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
                     'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                     'would', 'could', 'should', 'may', 'might', 'must', 'shall',
                     'for', 'and', 'nor', 'but', 'or', 'yet', 'so', 'to', 'of',
                     'in', 'on', 'at', 'by', 'with', 'from', 'as', 'into', 'that',
                     'this', 'it', 'er', 'en', 'et', 'og', 'i', 'på', 'for', 'med'}

        for mem in memories:
            text = mem.get('memory', '').lower()
            words = text.split()
            for word in words:
                word = ''.join(c for c in word if c.isalnum())
                if len(word) > 3 and word not in stopwords:
                    word_freq[word] = word_freq.get(word, 0) + 1

        # Sort by frequency
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, _ in sorted_words[:max_keywords]]

    def _serialize_index(self) -> str:
        """Serialize index to compact string for storage"""
        lines = ["MEMORY INDEX (L0):", ""]

        for category, index in self._index_cache.items():
            lines.append(index.to_compact())

        return "\n".join(lines)

    def get_index_summary(self) -> str:
        """Get compact index for context injection (~200 tokens)"""
        if not self._index_cache:
            return "No index built yet. Run build_index() first."

        lines = ["Memory Categories:"]
        for category, index in self._index_cache.items():
            lines.append(f"- {index.to_compact()}")

        return "\n".join(lines)


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

async def initialize_sensory_memories():
    """Populate sensory memory with base mappings"""
    logger.info("🌡️ Initializing sensory memory database...")

    for category, mappings in SENSORY_MAPPINGS.items():
        for sensation, meanings in mappings.items():
            await store_sensory_memory(
                sensation=sensation,
                category=category,
                meanings=meanings,
                example_contexts=[f"føler {sensation}", f"som {sensation}"],
                intensity_note=f"Sterkere {sensation} = sterkere effekt"
            )

    logger.info("✅ Sensory memory initialized!")


async def get_efficient_context(query: str, max_tokens: int = 800) -> str:
    """
    One-liner to get token-efficient context for any query.

    Use this in prompts:
        context = await get_efficient_context(user_input)
        prompt = f"Context: {context}\n\nUser: {user_input}"
    """
    hm = HierarchicalMemory()
    result = await hm.get_smart_context(query, max_tokens=max_tokens)

    parts = []

    # Sensory context (if any)
    if result["sensory_context"]:
        parts.append(f"[Sensory: {result['sensory_context']['summary']}]")

    # Categories
    if result["l0_index"]:
        parts.append(f"[Categories: {', '.join(result['l0_index'])}]")

    # Summaries
    for s in result["l1_summaries"]:
        parts.append(f"• {s['summary']}")

    # Full details
    for d in result["l2_details"]:
        parts.append(f"▸ {d['memory'][:200]}...")

    return "\n".join(parts) if parts else "No relevant context found."


# ============================================================================
# MAIN (TEST)
# ============================================================================

async def main():
    """Test hierarchical memory system"""
    print("🧠 Testing Hierarchical Memory System")
    print("=" * 60)

    # Test 1: Sensory context (instant, no API)
    print("\n1️⃣ Testing sensory context (instant lookup)...")
    test_phrases = [
        "jeg føler meg kald inne i meg",
        "det er som å gå i sirup",
        "hjertet mitt føles tungt",
        "fikk en varm følelse"
    ]

    for phrase in test_phrases:
        result = get_sensory_context(phrase)
        if result["has_sensory"]:
            print(f"  '{phrase}'")
            print(f"  → {result['summary']}")
        else:
            print(f"  '{phrase}' → No sensory detected")

    # Test 2: Smart context retrieval
    print("\n2️⃣ Testing smart context retrieval...")
    hm = HierarchicalMemory()

    context = await hm.get_smart_context("AIKI-HOME arkitektur")
    print(f"  Query: 'AIKI-HOME arkitektur'")
    print(f"  L0 categories: {context['l0_index']}")
    print(f"  L1 summaries: {len(context['l1_summaries'])}")
    print(f"  L2 details: {len(context['l2_details'])}")
    print(f"  Estimated tokens: ~{context['estimated_tokens']}")

    # Test 3: Build index
    print("\n3️⃣ Building memory index...")
    stats = await hm.build_index()
    print(f"  Status: {stats['status']}")
    print(f"  Categories: {stats.get('categories', [])}")

    print("\n" + "=" * 60)
    print("✅ Hierarchical Memory System ready!")
    print("   - Sensory memory: Instant lookup (0 API tokens)")
    print("   - L0 Index: ~200 tokens")
    print("   - L1 Summaries: ~500 tokens")
    print("   - L2 Details: On-demand")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
