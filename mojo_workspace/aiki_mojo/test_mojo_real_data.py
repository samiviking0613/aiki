#!/usr/bin/env python3
"""
🔥 Test Mojo with Real AIKI Data
Load saved embeddings and call Mojo semantic search
"""

import numpy as np
import subprocess
import json
import time


def test_mojo_with_real_data():
    print("🔥 MOJO TEST - Real AIKI Data")
    print("=" * 70)

    # Load saved embeddings
    embeddings_file = "/home/jovnna/aiki/mojo_workspace/aiki_mojo/real_aiki_embeddings.npy"
    metadata_file = "/home/jovnna/aiki/mojo_workspace/aiki_mojo/real_aiki_metadata.json"

    embeddings = np.load(embeddings_file)

    with open(metadata_file, "r") as f:
        metadata = json.load(f)

    num_memories = metadata["num_memories"]
    embedding_dim = metadata["embedding_dim"]
    numpy_time = metadata["numpy_avg_time_ms"]

    print(f"📊 Dataset Info:")
    print(f"  Memories: {num_memories}")
    print(f"  Dimension: {embedding_dim}")
    print(f"  NumPy time: {numpy_time:.4f} ms")
    print()

    # For small dataset, we need to generate more data for fair Mojo test
    print("⚠️  Only 7 memories - too small for meaningful Mojo benchmark!")
    print("📈 Generating synthetic dataset (871 memories, matching AIKI target)...")

    # Generate 871 memories by replicating and adding noise
    target_size = 871
    np.random.seed(42)

    synthetic_embeddings = []
    for i in range(target_size):
        # Take base embedding and add small random noise
        base_idx = i % num_memories
        noise = np.random.normal(0, 0.01, embedding_dim).astype(np.float32)
        synthetic_emb = embeddings[base_idx] + noise
        # Normalize
        norm = np.linalg.norm(synthetic_emb)
        if norm > 0:
            synthetic_emb = synthetic_emb / norm
        synthetic_embeddings.append(synthetic_emb)

    synthetic_embeddings = np.array(synthetic_embeddings, dtype=np.float32)

    print(f"✅ Generated {len(synthetic_embeddings)} synthetic memories")
    print()

    # Save for Mojo
    np.save("synthetic_aiki_embeddings.npy", synthetic_embeddings)

    # Benchmark NumPy with synthetic data
    print("🐍 Benchmarking NumPy with 871 memories...")

    query = synthetic_embeddings[0]
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
    semantic_search_numpy(query, synthetic_embeddings, top_k)

    # Benchmark
    start = time.time()
    for _ in range(num_iterations):
        indices, scores = semantic_search_numpy(query, synthetic_embeddings, top_k)
    end = time.time()

    numpy_avg = (end - start) / num_iterations
    print(f"✅ NumPy (871 mem): {numpy_avg * 1000:.4f} ms")
    print()

    print("=" * 70)
    print("📊 COMPARISON:")
    print(f"  NumPy (7 real memories):   {numpy_time:.4f} ms")
    print(f"  NumPy (871 synthetic):     {numpy_avg * 1000:.4f} ms")
    print()
    print("✅ Ready for Mojo integration!")
    print()
    print("🎯 Next Step: Write Mojo Python wrapper to call memory_search.mojo")


if __name__ == "__main__":
    test_mojo_with_real_data()
