"""
Enhanced mem0 - Wrapper som forbedrer mem0 med keyword pre-filtering.

Forbedringer:
1. Pre-filter søk med SQLite FTS (gratis) før mem0 embedding søk
2. Rikere metadata via keyword extraction
3. Deduplisering basert på keyword overlap

Mål: Samme kvalitet, raskere, billigere.
"""

import os
import time
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime

from mem0 import Memory
from src.config.mem0_config import get_mem0_config, setup_environment

logger = logging.getLogger(__name__)


@dataclass
class SearchMetrics:
    """Målinger for ett søk"""
    query: str
    method: str  # "mem0_only", "enhanced", "sqlite_only"
    total_time_ms: float
    sqlite_time_ms: float = 0
    mem0_time_ms: float = 0
    results_count: int = 0
    sqlite_candidates: int = 0
    api_calls_saved: int = 0


@dataclass
class BenchmarkResults:
    """Samlet benchmark-resultater"""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    total_queries: int = 0

    # Tid
    avg_mem0_only_ms: float = 0
    avg_enhanced_ms: float = 0
    time_saved_percent: float = 0

    # API-kall
    total_api_calls_saved: int = 0

    # Kvalitet (manuell vurdering)
    same_top_result_percent: float = 0

    metrics: List[SearchMetrics] = field(default_factory=list)


class EnhancedMem0:
    """
    Forbedret mem0 med keyword pre-filtering.

    Strategi:
    1. Ekstraher keywords fra query
    2. Søk SQLite FTS først (gratis, ~1ms)
    3. Hvis treff: Filtrer mem0 søk til kun disse session_ids
    4. Hvis ingen treff: Fall tilbake til vanlig mem0 søk
    """

    def __init__(self, user_id: str = "jovnna"):
        self.user_id = user_id
        self._mem0: Optional[Memory] = None
        self._raw_store = None
        self._keyword_extractor = None
        self._metrics: List[SearchMetrics] = []

    @property
    def mem0(self) -> Memory:
        """Lazy-load mem0"""
        if self._mem0 is None:
            setup_environment()
            self._mem0 = Memory.from_config(get_mem0_config())
        return self._mem0

    @property
    def raw_store(self):
        """Lazy-load raw conversation store"""
        if self._raw_store is None:
            from .raw_conversation_store import RawConversationStore
            self._raw_store = RawConversationStore()
        return self._raw_store

    @property
    def keyword_extractor(self):
        """Lazy-load keyword extractor"""
        if self._keyword_extractor is None:
            from .keyword_extractor import get_keyword_extractor
            self._keyword_extractor = get_keyword_extractor(use_llm=False)
        return self._keyword_extractor

    def search_mem0_only(self, query: str, limit: int = 10) -> Tuple[List[Dict], SearchMetrics]:
        """Vanlig mem0 søk (baseline for sammenligning)"""
        start = time.perf_counter()

        results = self.mem0.search(query, user_id=self.user_id, limit=limit)

        elapsed_ms = (time.perf_counter() - start) * 1000

        metrics = SearchMetrics(
            query=query,
            method="mem0_only",
            total_time_ms=elapsed_ms,
            mem0_time_ms=elapsed_ms,
            results_count=len(results.get('results', []))
        )

        return results.get('results', []), metrics

    def search_enhanced(self, query: str, limit: int = 10) -> Tuple[List[Dict], SearchMetrics]:
        """
        Forbedret søk med pre-filtering.

        1. Ekstraher keywords fra query
        2. Søk SQLite FTS først
        3. Hvis treff: Bruk som filter-hint for mem0
        4. Kombiner resultater
        """
        total_start = time.perf_counter()

        # Steg 1: Ekstraher keywords (gratis, ~0.1ms)
        projects, topics = self.keyword_extractor.extract_fast(query)
        all_keywords = projects + topics

        # Steg 2: SQLite FTS søk (gratis, ~1-5ms)
        sqlite_start = time.perf_counter()
        sqlite_results = []

        if all_keywords:
            # Søk med kjente keywords
            for kw in all_keywords[:3]:  # Maks 3 for å unngå for bredt søk
                hits = self.raw_store.search_exact_text(kw, limit=20)
                sqlite_results.extend(hits)
        else:
            # Ingen kjente keywords - søk med query-ord direkte
            query_words = self._extract_query_words(query)
            if query_words:
                fts_query = " OR ".join(query_words[:5])
                sqlite_results = self.raw_store.search_exact_text(fts_query, limit=20)

        sqlite_time_ms = (time.perf_counter() - sqlite_start) * 1000

        # Dedupliser SQLite resultater
        seen_sessions = set()
        unique_sqlite = []
        for r in sqlite_results:
            sid = r.get('session_id')
            if sid and sid not in seen_sessions:
                seen_sessions.add(sid)
                unique_sqlite.append(r)

        # Steg 3: mem0 søk
        mem0_start = time.perf_counter()

        if unique_sqlite:
            # Har SQLite treff - mem0 brukes for ranking/utvidelse
            # TODO: Kunne filtrere mem0 til kun disse sessions, men mem0 API støtter ikke det direkte
            # For nå: Kjør mem0 uansett, men vi har allerede kandidater
            mem0_results = self.mem0.search(query, user_id=self.user_id, limit=limit)
            api_calls_saved = 0  # Ingen spart enda, men vi har backup
        else:
            # Ingen SQLite treff - full mem0 søk
            mem0_results = self.mem0.search(query, user_id=self.user_id, limit=limit)
            api_calls_saved = 0

        mem0_time_ms = (time.perf_counter() - mem0_start) * 1000

        # Steg 4: Kombiner resultater
        # Prioriter mem0 (semantisk), men inkluder SQLite-unike
        final_results = mem0_results.get('results', [])

        # Legg til SQLite-resultater som mem0 ikke fant
        mem0_texts = {r.get('memory', '').lower() for r in final_results}
        for sqlite_r in unique_sqlite[:5]:
            content = sqlite_r.get('content', '').lower()
            # Sjekk om lignende allerede i resultater
            if not any(content[:50] in m or m[:50] in content for m in mem0_texts if m):
                final_results.append({
                    'memory': sqlite_r.get('content', ''),
                    'source': 'sqlite_fts',
                    'session_id': sqlite_r.get('session_id'),
                    'score': 0.5  # Lavere enn mem0
                })

        total_time_ms = (time.perf_counter() - total_start) * 1000

        metrics = SearchMetrics(
            query=query,
            method="enhanced",
            total_time_ms=total_time_ms,
            sqlite_time_ms=sqlite_time_ms,
            mem0_time_ms=mem0_time_ms,
            results_count=len(final_results),
            sqlite_candidates=len(unique_sqlite),
            api_calls_saved=api_calls_saved
        )

        return final_results[:limit], metrics

    def _extract_query_words(self, query: str) -> List[str]:
        """Ekstraher meningsfulle ord fra en spørring"""
        # Norske stoppord
        stopwords = {
            'jeg', 'du', 'han', 'hun', 'den', 'det', 'vi', 'de', 'dem',
            'meg', 'deg', 'seg', 'oss', 'dere',
            'er', 'var', 'har', 'hadde', 'blir', 'ble', 'være', 'vært',
            'kan', 'kunne', 'vil', 'ville', 'skal', 'skulle', 'må', 'måtte',
            'og', 'eller', 'men', 'for', 'så', 'om', 'at', 'hvis', 'når',
            'med', 'på', 'i', 'til', 'fra', 'av', 'ved', 'etter', 'over', 'under',
            'en', 'et', 'ei', 'den', 'det', 'de', 'denne', 'dette', 'disse',
            'min', 'din', 'sin', 'vår', 'deres', 'mitt', 'ditt', 'sitt',
            'hva', 'hvem', 'hvor', 'hvordan', 'hvorfor', 'hvilken', 'hvilket',
            'ikke', 'bare', 'også', 'da', 'nå', 'her', 'der',
            'alle', 'noen', 'ingen', 'hver', 'mange', 'mye', 'lite', 'få',
            'sa', 'sier', 'gjør', 'gjorde', 'gikk', 'kom', 'går',
            'om', 'ang', 'vedr', 'the', 'a', 'an', 'is', 'are', 'was', 'were'
        }

        words = query.lower().split()
        meaningful = [w.strip('.,!?()[]{}":;') for w in words
                     if w.lower() not in stopwords and len(w) > 2]
        return meaningful

    def search(self, query: str, limit: int = 10, method: str = "enhanced") -> List[Dict]:
        """
        Hovedsøkemetode.

        Args:
            query: Søkespørring
            limit: Maks antall resultater
            method: "enhanced" (anbefalt), "mem0_only", eller "both" (for testing)
        """
        if method == "mem0_only":
            results, metrics = self.search_mem0_only(query, limit)
        elif method == "enhanced":
            results, metrics = self.search_enhanced(query, limit)
        elif method == "both":
            # Kjør begge for sammenligning
            results_mem0, metrics_mem0 = self.search_mem0_only(query, limit)
            results_enhanced, metrics_enhanced = self.search_enhanced(query, limit)
            self._metrics.extend([metrics_mem0, metrics_enhanced])
            return results_enhanced  # Returner enhanced
        else:
            results, metrics = self.search_enhanced(query, limit)

        self._metrics.append(metrics)
        return results

    def add(self, content: str, metadata: Optional[Dict] = None) -> Dict:
        """
        Lagre minne med forbedret metadata.

        Automatisk:
        1. Ekstraher keywords
        2. Legg til som metadata
        3. Lagre via mem0
        """
        # Ekstraher keywords
        projects, topics = self.keyword_extractor.extract_fast(content)

        # Bygg metadata
        enhanced_metadata = metadata or {}
        if projects:
            enhanced_metadata['projects'] = projects
        if topics:
            enhanced_metadata['topics'] = topics
        enhanced_metadata['timestamp'] = datetime.now().isoformat()

        # Lagre via mem0
        messages = [{'role': 'user', 'content': content}]
        result = self.mem0.add(messages, user_id=self.user_id, metadata=enhanced_metadata)

        return result

    def get_metrics(self) -> List[SearchMetrics]:
        """Hent alle målinger"""
        return self._metrics

    def clear_metrics(self):
        """Nullstill målinger"""
        self._metrics = []

    def get_benchmark_summary(self) -> BenchmarkResults:
        """Generer benchmark-oppsummering"""
        if not self._metrics:
            return BenchmarkResults()

        mem0_only = [m for m in self._metrics if m.method == "mem0_only"]
        enhanced = [m for m in self._metrics if m.method == "enhanced"]

        avg_mem0 = sum(m.total_time_ms for m in mem0_only) / len(mem0_only) if mem0_only else 0
        avg_enhanced = sum(m.total_time_ms for m in enhanced) / len(enhanced) if enhanced else 0

        time_saved = ((avg_mem0 - avg_enhanced) / avg_mem0 * 100) if avg_mem0 > 0 else 0

        return BenchmarkResults(
            total_queries=len(self._metrics),
            avg_mem0_only_ms=avg_mem0,
            avg_enhanced_ms=avg_enhanced,
            time_saved_percent=time_saved,
            total_api_calls_saved=sum(m.api_calls_saved for m in self._metrics),
            metrics=self._metrics
        )


# Singleton
_enhanced_mem0: Optional[EnhancedMem0] = None

def get_enhanced_mem0(user_id: str = "jovnna") -> EnhancedMem0:
    """Hent singleton EnhancedMem0"""
    global _enhanced_mem0
    if _enhanced_mem0 is None:
        _enhanced_mem0 = EnhancedMem0(user_id=user_id)
    return _enhanced_mem0
