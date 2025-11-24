#!/usr/bin/env python3
"""
🧠 Test Mojo with REAL AIKI Data from Qdrant
This is the FIRST Mojo integration into AIKI system!
"""

import numpy as np
import time
from qdrant_client import QdrantClient
from typing import List, Tuple


def fetch_aiki_memories(limit: int = None) -> Tuple[List[np.ndarray], List[str]]:
    """Fetch real AIKI memories from Qdrant."""
    print("🔍 Connecting to Qdrant...")
    client = QdrantClient(path="/home/jovnna/aiki/shared_qdrant")

    print("📊 Fetching memories from mem0_memories collection...")

    # Scroll through all points
    scroll_result = client.scroll(
        collection_name="mem0_memories",
        limit=limit if limit else 10000,
        with_vectors=True,
        with_payload=True
    )

    points = scroll_result[0]

    embeddings = []
    memory_texts = []

    for point in points:
        if point.vector is not None:
            embeddings.append(np.array(point.vector, dtype=np.float32))
            # Get memory text from payload (handle different structures)
            payload = point.payload or {}

            # Try different payload structures
            if 'data' in payload:
                if isinstance(payload['data'], dict):
                    memory_text = payload['data'].get('memory', 'Unknown')
                else:
                    memory_text = str(payload['data'])
            elif 'memory' in payload:
                memory_text = payload['memory']
            else:
                memory_text = f"Memory ID: {point.id}"

            memory_texts.append(memory_text)

    print(f"✅ Fetched {len(embeddings)} memories")
    print(f"   Embedding dimension: {len(embeddings[0]) if embeddings else 'N/A'}")

    return embeddings, memory_texts


def batch_cosine_similarity_numpy(
    query: np.ndarray,
    embeddings: np.ndarray
) -> np.ndarray:
    """Compute cosine similarity using NumPy."""
    query_norm = np.linalg.norm(query)
    if query_norm == 0:
        return np.zeros(len(embeddings))

    query_normalized = query / query_norm

    embeddings_norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    embeddings_norms[embeddings_norms == 0] = 1
    embeddings_normalized = embeddings / embeddings_norms

    similarities = embeddings_normalized @ query_normalized

    return similarities


def top_k_indices(scores: np.ndarray, k: int) -> np.ndarray:
    """Find top-k indices."""
    return np.argpartition(scores, -k)[-k:][::-1]


def semantic_search_numpy(
    query_embedding: np.ndarray,
    all_embeddings: np.ndarray,
    top_k: int = 5
) -> Tuple[np.ndarray, np.ndarray]:
    """Full semantic search pipeline."""
    similarities = batch_cosine_similarity_numpy(query_embedding, all_embeddings)
    top_indices = top_k_indices(similarities, top_k)
    top_scores = similarities[top_indices]
    return top_indices, top_scores


def main():
    print("🧠 REAL AIKI DATA TEST - NumPy Baseline")
    print("=" * 70)

    # Fetch real memories
    embeddings_list, memory_texts = fetch_aiki_memories()

    if not embeddings_list:
        print("❌ No memories found!")
        return

    # Convert to numpy array
    all_embeddings = np.array(embeddings_list, dtype=np.float32)
    num_memories = len(all_embeddings)
    embedding_dim = all_embeddings.shape[1]

    print(f"\n📊 Dataset Info:")
    print(f"  Total memories: {num_memories}")
    print(f"  Embedding dimension: {embedding_dim}")
    print()

    # Use first memory as query (realistic test)
    query = all_embeddings[0]

    print("🔍 Running NumPy semantic search (100 iterations)...")

    top_k = 5
    num_iterations = 100

    # Warm-up
    semantic_search_numpy(query, all_embeddings, top_k)

    # Benchmark
    start = time.time()
    for _ in range(num_iterations):
        indices, scores = semantic_search_numpy(query, all_embeddings, top_k)
    end = time.time()

    avg_time = (end - start) / num_iterations

    print(f"✅ NumPy average time: {avg_time * 1000:.4f} ms")
    print()
    print(f"📋 Top-{top_k} similar memories (to first memory):")
    for i, (idx, score) in enumerate(zip(indices, scores), 1):
        memory_preview = memory_texts[idx][:80] + "..." if len(memory_texts[idx]) > 80 else memory_texts[idx]
        print(f"  {i}. [Score: {score:.4f}] {memory_preview}")

    print()
    print("=" * 70)
    print(f"🎯 NumPy Performance Summary:")
    print(f"  Dataset: {num_memories} real AIKI memories")
    print(f"  Dimension: {embedding_dim}")
    print(f"  Average search time: {avg_time * 1000:.4f} ms")
    print()
    print("📁 Next: Save embeddings to file for Mojo test")

    # Save for Mojo test
    output_file = "/home/jovnna/aiki/mojo_workspace/aiki_mojo/real_aiki_embeddings.npy"
    np.save(output_file, all_embeddings)
    print(f"✅ Saved embeddings to: {output_file}")

    # Save metadata
    import json
    metadata = {
        "num_memories": num_memories,
        "embedding_dim": embedding_dim,
        "numpy_avg_time_ms": avg_time * 1000,
        "top_k": top_k,
        "query_index": 0,
        "top_indices": indices.tolist(),
        "top_scores": scores.tolist()
    }

    with open("/home/jovnna/aiki/mojo_workspace/aiki_mojo/real_aiki_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    print("✅ Saved metadata for comparison")


if __name__ == "__main__":
    main()
