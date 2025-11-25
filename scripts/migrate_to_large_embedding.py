#!/usr/bin/env python3
"""
Migrerer minner fra text-embedding-3-small (1536) til text-embedding-3-large (3072).

Prosess:
1. Hent alle minner fra gammel collection (mem0_memories)
2. Re-embed hver med large modellen
3. Lagre i ny collection (mem0_memories_large)

Estimert kostnad: ~$0.24 for 1740 minner

Kjør: python scripts/migrate_to_large_embedding.py
"""

import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import time
from datetime import datetime
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from mem0 import Memory

# Gammel konfigurasjon (small)
OLD_CONFIG = {
    'llm': {'provider': 'openai', 'config': {'model': 'openai/gpt-4o-mini', 'temperature': 0.2, 'max_tokens': 2000}},
    'embedder': {'provider': 'openai', 'config': {'model': 'text-embedding-3-small', 'embedding_dims': 1536}},
    'vector_store': {'provider': 'qdrant', 'config': {'collection_name': 'mem0_memories', 'host': 'localhost', 'port': 6333, 'embedding_model_dims': 1536}}
}

# Ny konfigurasjon (large)
NEW_CONFIG = {
    'llm': {'provider': 'openai', 'config': {'model': 'openai/gpt-4o-mini', 'temperature': 0.2, 'max_tokens': 2000}},
    'embedder': {'provider': 'openai', 'config': {'model': 'text-embedding-3-large', 'embedding_dims': 3072}},
    'vector_store': {'provider': 'qdrant', 'config': {'collection_name': 'mem0_memories_large', 'host': 'localhost', 'port': 6333, 'embedding_model_dims': 3072}}
}


def migrate():
    print("=" * 60)
    print("EMBEDDING MIGRATION: small (1536) → large (3072)")
    print(f"Startet: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()

    # Setup environment
    os.environ['OPENAI_API_KEY'] = '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'
    os.environ['OPENAI_BASE_URL'] = 'https://openrouter.ai/api/v1'

    # Connect to Qdrant
    client = QdrantClient(host='localhost', port=6333)

    # Check old collection
    try:
        old_info = client.get_collection('mem0_memories')
        total_memories = old_info.points_count
        print(f"Gamle minner funnet: {total_memories}")
    except Exception as e:
        print(f"Kunne ikke finne gammel collection: {e}")
        return

    # Create new collection if needed
    try:
        client.get_collection('mem0_memories_large')
        print("Ny collection eksisterer allerede")
    except:
        print("Oppretter ny collection med 3072 dimensjoner...")
        client.create_collection(
            collection_name='mem0_memories_large',
            vectors_config=VectorParams(size=3072, distance=Distance.COSINE)
        )
        print("Collection opprettet!")

    # Initialize mem0 instances
    print("\nInitialiserer mem0...")
    old_mem0 = Memory.from_config(OLD_CONFIG)
    new_mem0 = Memory.from_config(NEW_CONFIG)

    # Get all memories from old collection
    print("Henter alle minner fra gammel collection...")
    all_memories = old_mem0.get_all(user_id='jovnna')

    if not all_memories or 'results' not in all_memories:
        print("Ingen minner funnet!")
        return

    memories = all_memories['results']
    print(f"Hentet {len(memories)} minner")

    # Estimate cost
    total_chars = sum(len(m.get('memory', '')) for m in memories)
    estimated_tokens = total_chars // 4
    estimated_cost = (estimated_tokens / 1_000_000) * 0.13  # large price
    print(f"\nEstimert tokens: {estimated_tokens:,}")
    print(f"Estimert kostnad: ${estimated_cost:.4f} (~{estimated_cost * 11:.2f} kr)")

    input("\nTrykk ENTER for å starte migrering...")

    # Migrate each memory
    print("\n" + "=" * 60)
    print("STARTER MIGRERING")
    print("=" * 60)

    success = 0
    failed = 0
    start_time = time.time()

    for i, mem in enumerate(memories, 1):
        memory_text = mem.get('memory', '')
        metadata = mem.get('metadata', {})

        if not memory_text:
            print(f"[{i}/{len(memories)}] Hopper over tomt minne")
            continue

        try:
            # Add to new collection with large embedding
            result = new_mem0.add(
                [{'role': 'user', 'content': memory_text}],
                user_id='jovnna',
                metadata=metadata
            )
            success += 1

            if i % 10 == 0:
                elapsed = time.time() - start_time
                rate = i / elapsed
                eta = (len(memories) - i) / rate
                print(f"[{i}/{len(memories)}] OK - {rate:.1f}/sek - ETA: {eta/60:.1f} min")

        except Exception as e:
            failed += 1
            print(f"[{i}/{len(memories)}] FEILET: {str(e)[:50]}")

        # Rate limiting
        time.sleep(0.1)

    # Summary
    elapsed = time.time() - start_time
    print("\n" + "=" * 60)
    print("MIGRERING FULLFØRT")
    print("=" * 60)
    print(f"Tid brukt: {elapsed/60:.1f} minutter")
    print(f"Vellykket: {success}/{len(memories)}")
    print(f"Feilet: {failed}")

    # Verify new collection
    new_info = client.get_collection('mem0_memories_large')
    print(f"\nNy collection: {new_info.points_count} minner med {new_info.config.params.vectors.size} dims")


if __name__ == "__main__":
    migrate()
