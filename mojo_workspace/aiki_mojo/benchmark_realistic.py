#!/usr/bin/env python3
"""
🐍 Realistic AIKI Benchmark - Python/NumPy Baseline
For comparison with Mojo implementation
"""

import numpy as np
import time
from typing import Tuple


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


def benchmark_size(embedding_dim: int, num_memories: int, top_k: int, num_iterations: int) -> float:
    """Run benchmark for specific dataset size."""

    # Generate random data
    np.random.seed(42)
    query = np.random.random(embedding_dim).astype(np.float32)
    embeddings = np.random.random((num_memories, embedding_dim)).astype(np.float32)

    # Warm-up
    semantic_search_numpy(query, embeddings, top_k)

    # Benchmark
    start = time.time()
    for _ in range(num_iterations):
        semantic_search_numpy(query, embeddings, top_k)
    end = time.time()

    return (end - start) / num_iterations


def main():
    print("🐍 REALISTIC AIKI BENCHMARK - NumPy Baseline")
    print("=" * 70)

    embedding_dim = 1536  # Matching mem0/OpenAI
    top_k = 5

    print(f"\n📊 Configuration:")
    print(f"  Embedding dimension: {embedding_dim} (matching mem0)")
    print(f"  Top-K: {top_k}")
    print()

    test_sizes = [100, 500, 1000, 5000, 10000]
    iterations_per_size = [100, 50, 20, 10, 5]

    print("┌" + "─" * 68 + "┐")
    print("│ Dataset Size │ Iterations │   Avg Time    │  Per Memory   │")
    print("├" + "─" * 68 + "┤")

    results = []
    for size, iterations in zip(test_sizes, iterations_per_size):
        avg_time = benchmark_size(embedding_dim, size, top_k, iterations)
        per_memory = (avg_time / size) * 1_000_000  # microseconds

        results.append((size, avg_time))

        print(f"│ {size:12d} │ {iterations:10d} │ {avg_time*1000:10.4f} ms │ {per_memory:10.3f} μs │")

    print("└" + "─" * 68 + "┘")

    print("\n✅ Benchmark complete!")
    print("\n📊 NumPy Performance:")
    for size, avg_time in results:
        print(f"  {size:5d} memories: {avg_time*1000:8.4f} ms")


if __name__ == "__main__":
    main()
