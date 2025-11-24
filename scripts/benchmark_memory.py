#!/usr/bin/env python3
"""
Benchmark: Enhanced mem0 vs Standard mem0

Måler:
1. Søketid (ms)
2. Antall resultater
3. Kvalitet (om samme topp-resultat)
4. SQLite pre-filter effektivitet

Kjør: python scripts/benchmark_memory.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import time
from datetime import datetime
from typing import List, Dict

from src.memory.enhanced_mem0 import EnhancedMem0, SearchMetrics

# Test-queries - realistiske søk for AIKI
TEST_QUERIES = [
    # Kjente keywords (bør treffe SQLite først)
    "hva vet du om AIKI prosjektet?",
    "fortell meg om ADHD og fokus",
    "WiFi problemer og nettverk",
    "Innovasjon Norge søknad",

    # Vage/assosiative (tester semantisk søk)
    "den greia med bilen og kodene",
    "hvordan deployer jeg systemet?",
    "hva sa jeg om traktor?",

    # Emosjonelle/personlige
    "når ble jeg frustrert sist?",
    "hva liker Jovnna?",

    # Tekniske
    "Neo4j graf struktur",
    "mem0 konfigurasjon",
    "SQLite FTS5 søk",
]


def run_benchmark():
    """Kjør benchmark og sammenlign metodene"""
    print("=" * 60)
    print("AIKI MEMORY BENCHMARK")
    print(f"Tid: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()

    enhanced = EnhancedMem0(user_id="jovnna")
    results = []

    print(f"Kjører {len(TEST_QUERIES)} test-queries...\n")

    for i, query in enumerate(TEST_QUERIES, 1):
        print(f"[{i}/{len(TEST_QUERIES)}] \"{query[:40]}...\"")

        # Metode 1: Standard mem0
        try:
            result_mem0, metrics_mem0 = enhanced.search_mem0_only(query, limit=5)
        except Exception as e:
            print(f"   ❌ mem0_only feilet: {e}")
            metrics_mem0 = SearchMetrics(query=query, method="mem0_only", total_time_ms=0)
            result_mem0 = []

        # Metode 2: Enhanced (med pre-filter)
        try:
            result_enhanced, metrics_enhanced = enhanced.search_enhanced(query, limit=5)
        except Exception as e:
            print(f"   ❌ enhanced feilet: {e}")
            metrics_enhanced = SearchMetrics(query=query, method="enhanced", total_time_ms=0)
            result_enhanced = []

        # Sammenlign topp-resultat
        top_mem0 = result_mem0[0].get('memory', '')[:50] if result_mem0 else ""
        top_enhanced = result_enhanced[0].get('memory', '')[:50] if result_enhanced else ""
        same_top = top_mem0 == top_enhanced

        results.append({
            'query': query,
            'mem0_only': {
                'time_ms': metrics_mem0.total_time_ms,
                'results': len(result_mem0),
                'top_result': top_mem0
            },
            'enhanced': {
                'time_ms': metrics_enhanced.total_time_ms,
                'sqlite_time_ms': metrics_enhanced.sqlite_time_ms,
                'mem0_time_ms': metrics_enhanced.mem0_time_ms,
                'results': len(result_enhanced),
                'sqlite_candidates': metrics_enhanced.sqlite_candidates,
                'top_result': top_enhanced
            },
            'same_top_result': same_top
        })

        # Print progress
        speedup = metrics_mem0.total_time_ms / metrics_enhanced.total_time_ms if metrics_enhanced.total_time_ms > 0 else 0
        sqlite_hit = "✓" if metrics_enhanced.sqlite_candidates > 0 else "✗"
        same_marker = "=" if same_top else "≠"

        print(f"   mem0: {metrics_mem0.total_time_ms:.0f}ms | enhanced: {metrics_enhanced.total_time_ms:.0f}ms | "
              f"SQLite: {sqlite_hit} ({metrics_enhanced.sqlite_candidates}) | Top: {same_marker}")
        print()

    # Oppsummering
    print("\n" + "=" * 60)
    print("OPPSUMMERING")
    print("=" * 60)

    avg_mem0 = sum(r['mem0_only']['time_ms'] for r in results) / len(results)
    avg_enhanced = sum(r['enhanced']['time_ms'] for r in results) / len(results)
    avg_sqlite = sum(r['enhanced']['sqlite_time_ms'] for r in results) / len(results)

    same_top_count = sum(1 for r in results if r['same_top_result'])
    sqlite_hit_count = sum(1 for r in results if r['enhanced']['sqlite_candidates'] > 0)

    print(f"\n⏱️  TID:")
    print(f"   Gjennomsnitt mem0_only:  {avg_mem0:.1f}ms")
    print(f"   Gjennomsnitt enhanced:   {avg_enhanced:.1f}ms")
    print(f"   Gjennomsnitt SQLite:     {avg_sqlite:.1f}ms")

    if avg_enhanced > 0:
        speedup = (avg_mem0 - avg_enhanced) / avg_mem0 * 100
        print(f"   Endring:                 {speedup:+.1f}%")

    print(f"\n🎯 KVALITET:")
    print(f"   Samme topp-resultat:     {same_top_count}/{len(results)} ({same_top_count/len(results)*100:.0f}%)")
    print(f"   SQLite pre-filter treff: {sqlite_hit_count}/{len(results)} ({sqlite_hit_count/len(results)*100:.0f}%)")

    print(f"\n📊 SQLITE EFFEKTIVITET:")
    total_sqlite_candidates = sum(r['enhanced']['sqlite_candidates'] for r in results)
    print(f"   Totalt kandidater funnet: {total_sqlite_candidates}")
    print(f"   Gjennomsnitt per søk:     {total_sqlite_candidates/len(results):.1f}")

    # Lagre resultater
    output_path = Path(__file__).parent.parent / "data" / "benchmark_results.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    benchmark_data = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total_queries': len(results),
            'avg_mem0_only_ms': avg_mem0,
            'avg_enhanced_ms': avg_enhanced,
            'avg_sqlite_ms': avg_sqlite,
            'time_change_percent': speedup if avg_enhanced > 0 else 0,
            'same_top_result_percent': same_top_count / len(results) * 100,
            'sqlite_hit_rate_percent': sqlite_hit_count / len(results) * 100
        },
        'queries': results
    }

    with open(output_path, 'w') as f:
        json.dump(benchmark_data, f, indent=2, ensure_ascii=False)

    print(f"\n📁 Resultater lagret: {output_path}")

    # Vurdering
    print("\n" + "=" * 60)
    print("VURDERING")
    print("=" * 60)

    if speedup > 10:
        print("✅ Enhanced er RASKERE")
    elif speedup < -10:
        print("⚠️  Enhanced er TREGERE (overhead fra SQLite)")
    else:
        print("➡️  Omtrent lik hastighet")

    if same_top_count / len(results) >= 0.8:
        print("✅ Kvalitet BEVART (≥80% samme topp-resultat)")
    elif same_top_count / len(results) >= 0.6:
        print("⚠️  Kvalitet DELVIS bevart (60-80%)")
    else:
        print("❌ Kvalitet REDUSERT (<60% samme topp-resultat)")

    if sqlite_hit_count / len(results) >= 0.5:
        print("✅ SQLite pre-filter er EFFEKTIV (≥50% treff)")
    else:
        print("⚠️  SQLite pre-filter lite effektiv (<50% treff)")

    return benchmark_data


if __name__ == "__main__":
    run_benchmark()
