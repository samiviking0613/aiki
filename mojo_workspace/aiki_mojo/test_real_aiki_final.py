#!/usr/bin/env python3
"""
🧠 FINAL TEST - Mojo with REAL 898 AIKI Memories from Qdrant SERVER
"""

import sys
sys.path.append('/home/jovnna/aiki')

from MEM0_CONFIG_CORRECT import validate_qdrant_connection
from qdrant_client import QdrantClient
import numpy as np
import time


def main():
    print("🧠 REAL AIKI DATA TEST - 898 Memories from Qdrant SERVER")
    print("=" * 70)

    # Validate using correct database
    count = validate_qdrant_connection()
    print()

    # Connect to SERVER (not local!)
    print("📥 Fetching ALL memories from Qdrant SERVER...")
    client = QdrantClient(url='http://localhost:6333')

    scroll_result = client.scroll(
        collection_name='mem0_memories',
        limit=count,
        with_vectors=True,
        with_payload=True
    )

    points = scroll_result[0]

    embeddings = []
    memory_texts = []

    for point in points:
        if point.vector is not None:
            embeddings.append(np.array(point.vector, dtype=np.float32))

            # Get memory text
            payload = point.payload or {}
            if 'data' in payload and isinstance(payload['data'], dict):
                memory_text = payload['data'].get('memory', f'ID: {point.id}')
            elif 'memory' in payload:
                memory_text = payload['memory']
            else:
                memory_text = f'Memory ID: {point.id}'

            memory_texts.append(memory_text)

    embeddings = np.array(embeddings, dtype=np.float32)

    print(f"✅ Loaded {len(embeddings)} real AIKI memories")
    print(f"   Embedding dimension: {embeddings.shape[1]}")
    print()

    # Save for Mojo test
    np.save("real_aiki_898_embeddings.npy", embeddings)
    print("💾 Saved embeddings for Mojo test")
    print()

    # Benchmark NumPy
    print("🐍 Benchmarking NumPy with 898 REAL memories...")

    query = embeddings[0]
    top_k = 5
    num_iterations = 20

    def semantic_search_numpy(query, embeddings, k):
        query_norm = np.linalg.norm(query)
        if query_norm == 0:
            return np.zeros(k, dtype=np.int32), np.zeros(k)
        query_normalized = query / query_norm

        embeddings_norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        embeddings_norms[embeddings_norms == 0] = 1
        embeddings_normalized = embeddings / embeddings_norms

        similarities = embeddings_normalized @ query_normalized
        top_indices = np.argpartition(similarities, -k)[-k:][::-1]
        return top_indices, similarities[top_indices]

    # Warm-up
    semantic_search_numpy(query, embeddings, top_k)

    # Benchmark
    start = time.time()
    for _ in range(num_iterations):
        indices, scores = semantic_search_numpy(query, embeddings, top_k)
    end = time.time()

    numpy_avg = (end - start) / num_iterations

    print(f"✅ NumPy average: {numpy_avg * 1000:.4f} ms")
    print()
    print(f"📋 Top-{top_k} similar memories:")
    for i, (idx, score) in enumerate(zip(indices, scores), 1):
        preview = memory_texts[idx][:70] + "..." if len(memory_texts[idx]) > 70 else memory_texts[idx]
        print(f"  {i}. [Score: {score:.4f}] {preview}")

    print()
    print("=" * 70)
    print("🎯 NumPy Performance with REAL AIKI data (898 memories):")
    print(f"   Average search time: {numpy_avg * 1000:.4f} ms")
    print()
    print("✅ Data ready for Mojo test!")
    print("   Run: pixi run mojo run test_mojo_898.mojo")


if __name__ == "__main__":
    main()
