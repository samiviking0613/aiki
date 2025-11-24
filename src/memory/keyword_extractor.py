"""
Smart Keyword Extraction for AIKI Memory Graph

Kombinerer:
1. Fast path: Hardkodede kjente keywords (0ms, ingen API-kall)
2. Slow path: LLM-ekstraksjon for nye topics (kun ved behov)
3. Learning: Nye topics lagres automatisk for fremtidig fast path

Bruker OpenRouter med gpt-4o-mini for billig ekstraksjon.
"""

import os
import re
import json
import logging
from typing import List, Tuple, Set, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# Fil for å lagre lærte keywords
LEARNED_KEYWORDS_PATH = Path(__file__).parent.parent.parent / "data" / "learned_keywords.json"

# Baseline kjente keywords (fra unified_memory.py)
BASELINE_PROJECTS = {
    "AIKI", "AIKI-HOME", "AIKI Ultimate", "AIKI Prime",
    "MITM", "mem0", "Qdrant", "Neo4j", "Claude Code",
    "Open Interpreter", "ChatGPT"
}

BASELINE_TOPICS = {
    "ADHD", "minne", "memory", "arkitektur", "architecture",
    "WiFi", "nettverk", "network", "proxy", "VPN", "WireGuard",
    "TikTok", "YouTube", "accountability", "produktivitet",
    "lån", "bank", "Innovasjon Norge", "økonomi",
    "traktor", "bil", "OBD2", "CAN bus", "kjøretøy",
    "Python", "TypeScript", "JavaScript", "Docker",
    "PostgreSQL", "SQLite", "Redis"
}


class KeywordExtractor:
    """
    Smart keyword-ekstraktor med læring.

    Fast path: ~0ms (string matching)
    Slow path: ~500ms (LLM ekstraksjon, kun ved behov)
    """

    def __init__(self, use_llm: bool = True):
        self.use_llm = use_llm
        self._known_projects: Set[str] = set(BASELINE_PROJECTS)
        self._known_topics: Set[str] = set(BASELINE_TOPICS)
        self._load_learned_keywords()

    def _load_learned_keywords(self):
        """Last inn tidligere lærte keywords"""
        if LEARNED_KEYWORDS_PATH.exists():
            try:
                with open(LEARNED_KEYWORDS_PATH, 'r') as f:
                    data = json.load(f)
                    self._known_projects.update(data.get("projects", []))
                    self._known_topics.update(data.get("topics", []))
                    logger.debug(f"Lastet {len(data.get('projects', []))} lærte projects, {len(data.get('topics', []))} lærte topics")
            except Exception as e:
                logger.warning(f"Kunne ikke laste learned_keywords.json: {e}")

    def _save_learned_keywords(self, new_projects: List[str], new_topics: List[str]):
        """Lagre nye lærte keywords"""
        if not new_projects and not new_topics:
            return

        # Oppdater i minne
        self._known_projects.update(new_projects)
        self._known_topics.update(new_topics)

        # Lagre til fil
        LEARNED_KEYWORDS_PATH.parent.mkdir(parents=True, exist_ok=True)

        # Les eksisterende
        existing = {"projects": [], "topics": []}
        if LEARNED_KEYWORDS_PATH.exists():
            try:
                with open(LEARNED_KEYWORDS_PATH, 'r') as f:
                    existing = json.load(f)
            except:
                pass

        # Merge
        all_projects = list(set(existing.get("projects", [])) | set(new_projects))
        all_topics = list(set(existing.get("topics", [])) | set(new_topics))

        with open(LEARNED_KEYWORDS_PATH, 'w') as f:
            json.dump({
                "projects": sorted(all_projects),
                "topics": sorted(all_topics)
            }, f, indent=2, ensure_ascii=False)

        logger.info(f"Lagret {len(new_projects)} nye projects, {len(new_topics)} nye topics")

    def _word_boundary_match(self, keyword: str, text_lower: str) -> bool:
        """Sjekk om keyword finnes som helt ord (ikke del av annet ord)"""
        keyword_lower = keyword.lower()

        # Bruk word boundaries for alle keywords
        # Dette forhindrer at "network" matcher i "networks"
        # og at "bil" matcher i "bildeklassifisering"
        pattern = rf'\b{re.escape(keyword_lower)}\b'
        return bool(re.search(pattern, text_lower))

    def extract_fast(self, text: str) -> Tuple[List[str], List[str]]:
        """
        Fast path: Ekstraher kun kjente keywords (0ms, ingen API).
        Bruker word boundary matching for å unngå false positives.

        Returns:
            (projects, topics)
        """
        text_lower = text.lower()

        projects = [p for p in self._known_projects if self._word_boundary_match(p, text_lower)]
        topics = [t for t in self._known_topics if self._word_boundary_match(t, text_lower)]

        return projects, topics

    def extract_with_llm(self, text: str, max_tokens: int = 500) -> Tuple[List[str], List[str]]:
        """
        Slow path: Bruk LLM for å ekstrahere keywords.
        Oppdager nye topics og projects automatisk.

        Returns:
            (projects, topics)
        """
        if not self.use_llm:
            return self.extract_fast(text)

        # Begrens tekst-lengde
        if len(text) > 2000:
            text = text[:2000] + "..."

        try:
            import openai

            # Bruk OpenRouter
            client = openai.OpenAI(
                api_key=os.environ.get("OPENAI_API_KEY", "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"),
                base_url=os.environ.get("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
            )

            prompt = f"""Analyser denne teksten og ekstraher:
1. PROJECTS: Navngitte prosjekter, produkter, eller systemer (f.eks. "AIKI", "Neo4j")
2. TOPICS: Hovedtemaer/emner teksten handler om (f.eks. "ADHD", "nettverk", "minne")

Returner BARE JSON i dette formatet:
{{"projects": ["Project1", "Project2"], "topics": ["Topic1", "Topic2"]}}

Tekst:
{text}"""

            response = client.chat.completions.create(
                model="openai/gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.1
            )

            content = response.choices[0].message.content.strip()

            # Parse JSON fra response
            json_match = re.search(r'\{[^}]+\}', content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                llm_projects = data.get("projects", [])
                llm_topics = data.get("topics", [])

                # Finn nye keywords (ikke i baseline)
                new_projects = [p for p in llm_projects if p not in self._known_projects]
                new_topics = [t for t in llm_topics if t not in self._known_topics]

                # Lagre nye for fremtidig fast path
                if new_projects or new_topics:
                    self._save_learned_keywords(new_projects, new_topics)

                return llm_projects, llm_topics

        except Exception as e:
            logger.warning(f"LLM keyword-ekstraksjon feilet: {e}")

        # Fallback til fast path
        return self.extract_fast(text)

    def extract(
        self,
        text: str,
        use_llm_if_no_matches: bool = True
    ) -> Tuple[List[str], List[str]]:
        """
        Smart ekstraksjon: Fast path først, LLM kun ved behov.

        Args:
            text: Teksten å analysere
            use_llm_if_no_matches: Bruk LLM hvis fast path gir 0 treff

        Returns:
            (projects, topics)
        """
        # Prøv fast path først
        projects, topics = self.extract_fast(text)

        # Hvis ingen treff og LLM er aktivert, prøv slow path
        if use_llm_if_no_matches and not projects and not topics and self.use_llm:
            logger.debug("Ingen fast-path treff, bruker LLM...")
            return self.extract_with_llm(text)

        return projects, topics

    def get_all_known_keywords(self) -> dict:
        """Returner alle kjente keywords"""
        return {
            "projects": sorted(self._known_projects),
            "topics": sorted(self._known_topics)
        }


# Singleton
_extractor: Optional[KeywordExtractor] = None

def get_keyword_extractor(use_llm: bool = True) -> KeywordExtractor:
    """Hent singleton KeywordExtractor"""
    global _extractor
    if _extractor is None:
        _extractor = KeywordExtractor(use_llm=use_llm)
    return _extractor


def extract_keywords(text: str, use_llm: bool = False) -> Tuple[List[str], List[str]]:
    """
    Enkel funksjon for keyword-ekstraksjon.

    Args:
        text: Teksten å analysere
        use_llm: Bruk LLM for smartere ekstraksjon (standard: False for bakover-kompatibilitet)

    Returns:
        (projects, topics)
    """
    extractor = get_keyword_extractor(use_llm=use_llm)
    return extractor.extract(text, use_llm_if_no_matches=use_llm)
