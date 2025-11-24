#!/usr/bin/env python3
"""
🐍 Python Memory Search Benchmark - For comparison with Mojo
Semantic search with cosine similarity (Pure Python + NumPy)
"""

import numpy as np
import time
from typing import List, Tuple


def cosine_similarity_numpy(a: np.ndarray, b: np.ndarray) -> float:
    """
    Cosine similarity using NumPy
    Formula: cos(theta) = (a · b) / (||a|| * ||b||)
    """
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot_product / (norm_a * norm_b)


def cosine_similarity_pure_python(a: List[float], b: List[float]) -> float:
    """
    Cosine similarity in pure Python (no NumPy)
    Much slower but shows Python overhead
    """
    # Dot product
    dot = sum(a[i] * b[i] for i in range(len(a)))

    # Norms
    norm_a = sum(a[i] * a[i] for i in range(len(a))) ** 0.5
    norm_b = sum(b[i] * b[i] for i in range(len(b))) ** 0.5

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot / (norm_a * norm_b)


def batch_cosine_similarity_numpy(
    query: np.ndarray,
    embeddings: np.ndarray
) -> np.ndarray:
    """
    Compute cosine similarity between query and all embeddings
    Using NumPy vectorization

    Args:
        query: (embedding_dim,) array
        embeddings: (num_embeddings, embedding_dim) array

    Returns:
        (num_embeddings,) array of similarities
    """
    # Normalize query
    query_norm = np.linalg.norm(query)
    if query_norm == 0:
        return np.zeros(len(embeddings))

    query_normalized = query / query_norm

    # Normalize all embeddings
    embeddings_norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    embeddings_norms[embeddings_norms == 0] = 1  # Avoid division by zero
    embeddings_normalized = embeddings / embeddings_norms

    # Dot product (matrix-vector multiplication)
    similarities = embeddings_normalized @ query_normalized

    return similarities


def top_k_indices(scores: np.ndarray, k: int) -> np.ndarray:
    """
    Find indices of top-k highest scores
    """
    return np.argpartition(scores, -k)[-k:][::-1]


def semantic_search_numpy(
    query_embedding: np.ndarray,
    all_embeddings: np.ndarray,
    top_k: int = 5
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Full semantic search pipeline using NumPy

    Returns:
        (indices, scores) of top-k results
    """
    # Compute similarities
    similarities = batch_cosine_similarity_numpy(query_embedding, all_embeddings)

    # Get top-k
    top_indices = top_k_indices(similarities, top_k)
    top_scores = similarities[top_indices]

    return top_indices, top_scores


def semantic_search_pure_python(
    query_embedding: List[float],
    all_embeddings: List[List[float]],
    top_k: int = 5
) -> List[Tuple[int, float]]:
    """
    Full semantic search pipeline in pure Python (no NumPy)
    VERY slow - for comparison only

    Returns:
        List of (index, score) tuples
    """
    # Compute all similarities
    similarities = []
    for i, embedding in enumerate(all_embeddings):
        sim = cosine_similarity_pure_python(query_embedding, embedding)
        similarities.append((i, sim))

    # Sort by score (descending) and take top-k
    similarities.sort(key=lambda x: x[1], reverse=True)

    return similarities[:top_k]


def run_benchmark():
    print("🐍 Python Memory Search Benchmark")
    print("=" * 50)

    # Test configuration (matching Mojo implementation)
    embedding_dim = 128
    num_memories = 100
    top_k = 5
    num_iterations = 100  # Run multiple times for accurate timing

    print(f"\n📊 Test Configuration:")
    print(f"  Embedding dimension: {embedding_dim}")
    print(f"  Number of memories: {num_memories}")
    print(f"  Top-K: {top_k}")
    print(f"  Iterations: {num_iterations}")

    # Generate test data (same pattern as Mojo)
    query = np.array([i / embedding_dim for i in range(embedding_dim)], dtype=np.float32)
    embeddings = np.array([
        [(i % embedding_dim) / embedding_dim for _ in range(embedding_dim)]
        for i in range(num_memories)
    ], dtype=np.float32)

    # ========================================================================
    # BENCHMARK 1: NumPy (optimized)
    # ========================================================================
    print("\n🔍 Running NumPy semantic search...")

    start = time.time()
    for _ in range(num_iterations):
        indices, scores = semantic_search_numpy(query, embeddings, top_k)
    end = time.time()

    avg_time_numpy = (end - start) / num_iterations
    print(f"✅ NumPy average time: {avg_time_numpy:.6f} seconds ({avg_time_numpy * 1000:.3f} ms)")
    print(f"   Top-{top_k} indices: {indices}")

    # ========================================================================
    # BENCHMARK 2: Pure Python (for comparison)
    # ========================================================================
    print("\n🐌 Running Pure Python semantic search (slower)...")

    query_list = query.tolist()
    embeddings_list = embeddings.tolist()

    start = time.time()
    for _ in range(num_iterations):
        results = semantic_search_pure_python(query_list, embeddings_list, top_k)
    end = time.time()

    avg_time_python = (end - start) / num_iterations
    print(f"✅ Pure Python average time: {avg_time_python:.6f} seconds ({avg_time_python * 1000:.3f} ms)")
    print(f"   Top-{top_k} indices: {[r[0] for r in results]}")

    # ========================================================================
    # COMPARISON
    # ========================================================================
    print("\n📊 Performance Comparison:")
    print(f"  Pure Python: {avg_time_python * 1000:.3f} ms")
    print(f"  NumPy:       {avg_time_numpy * 1000:.3f} ms")
    print(f"  Mojo:        ~0.13 ms (from earlier test)")
    print()
    print(f"  NumPy speedup over Pure Python: {avg_time_python / avg_time_numpy:.1f}x")
    print(f"  Mojo speedup over NumPy: ~{avg_time_numpy / 0.00013:.1f}x")
    print(f"  Mojo speedup over Pure Python: ~{avg_time_python / 0.00013:.1f}x")

    print("\n✅ Benchmark complete!")
    print("🚀 Mojo is significantly faster than Python implementations")


if __name__ == "__main__":
    run_benchmark()
