#!/usr/bin/env mojo
"""
🔥 Realistic AIKI Benchmark - Large Dataset
Testing with actual AIKI memory dimensions:
- 1536-dim embeddings (matching mem0/OpenAI)
- 1000, 5000, 10000 memories
"""

from algorithm import vectorize, parallelize
from math import sqrt
from memory import memset_zero, UnsafePointer, alloc
from python import Python


fn dot_product_vectorized(
    a: UnsafePointer[Float32],
    b: UnsafePointer[Float32],
    size: Int
) -> Float32:
    var result: Float32 = 0.0
    alias simd_width = 8

    @parameter
    fn compute_chunk[width: Int](i: Int):
        var chunk_a = a.load[width=width](i)
        var chunk_b = b.load[width=width](i)
        var products = chunk_a * chunk_b
        for j in range(width):
            result += products[j]

    var num_chunks = size // simd_width
    vectorize[compute_chunk, simd_width](num_chunks * simd_width)

    for i in range(num_chunks * simd_width, size):
        result += a[i] * b[i]

    return result


fn vector_norm(
    vec: UnsafePointer[Float32],
    size: Int
) -> Float32:
    var sum_squares: Float32 = 0.0
    alias simd_width = 8

    @parameter
    fn compute_chunk[width: Int](i: Int):
        var chunk = vec.load[width=width](i)
        var squares = chunk * chunk
        for j in range(width):
            sum_squares += squares[j]

    var num_chunks = size // simd_width
    vectorize[compute_chunk, simd_width](num_chunks * simd_width)

    for i in range(num_chunks * simd_width, size):
        sum_squares += vec[i] * vec[i]

    return sqrt(sum_squares)


fn cosine_similarity(
    a: UnsafePointer[Float32],
    b: UnsafePointer[Float32],
    size: Int
) -> Float32:
    var dot = dot_product_vectorized(a, b, size)
    var norm_a = vector_norm(a, size)
    var norm_b = vector_norm(b, size)

    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    return dot / (norm_a * norm_b)


fn batch_cosine_similarity[
    O: Origin[True]
](
    query: UnsafePointer[Float32],
    embeddings: UnsafePointer[Float32],
    num_embeddings: Int,
    embedding_dim: Int,
    results: UnsafePointer[Float32, O]
):
    @parameter
    fn compute_similarity(i: Int):
        var embedding_ptr = embeddings + (i * embedding_dim)
        var sim = cosine_similarity(query, embedding_ptr, embedding_dim)
        results[i] = sim

    parallelize[compute_similarity](num_embeddings, num_embeddings)


fn top_k_indices[
    O: Origin[True]
](
    scores: UnsafePointer[Float32],
    num_scores: Int,
    k: Int,
    result_indices: UnsafePointer[Int32, O]
):
    var indices = alloc[Int32](num_scores)
    for i in range(num_scores):
        indices[i] = i

    for i in range(k):
        var max_idx = i
        var max_score = scores[indices[i]]

        for j in range(i + 1, num_scores):
            if scores[indices[j]] > max_score:
                max_idx = j
                max_score = scores[indices[j]]

        if max_idx != i:
            var temp = indices[i]
            indices[i] = indices[max_idx]
            indices[max_idx] = temp

    for i in range(k):
        result_indices[i] = indices[i]

    indices.free()


fn semantic_search[
    O: Origin[True]
](
    query_embedding: UnsafePointer[Float32],
    all_embeddings: UnsafePointer[Float32],
    num_memories: Int,
    embedding_dim: Int,
    top_k: Int,
    result_indices: UnsafePointer[Int32, O]
):
    var scores = alloc[Float32](num_memories)

    batch_cosine_similarity(
        query_embedding,
        all_embeddings,
        num_memories,
        embedding_dim,
        scores
    )

    top_k_indices(scores, num_memories, top_k, result_indices)

    scores.free()


fn benchmark_size(
    embedding_dim: Int,
    num_memories: Int,
    top_k: Int,
    num_iterations: Int
) raises -> Float64:
    """Run benchmark for specific dataset size."""

    # Allocate memory
    var query = alloc[Float32](embedding_dim)
    var embeddings = alloc[Float32](num_memories * embedding_dim)
    var result_indices = alloc[Int32](top_k)

    # Fill with realistic random-ish data
    var python_random = Python.import_module("random")
    python_random.seed(42)

    for i in range(embedding_dim):
        query[i] = Float32(python_random.random())

    for emb_idx in range(num_memories):
        for dim_idx in range(embedding_dim):
            embeddings[emb_idx * embedding_dim + dim_idx] = Float32(python_random.random())

    # Warm-up run
    semantic_search(query, embeddings, num_memories, embedding_dim, top_k, result_indices)

    # Benchmark
    var python_time = Python.import_module("time")
    var start = python_time.time()

    for _ in range(num_iterations):
        semantic_search(query, embeddings, num_memories, embedding_dim, top_k, result_indices)

    var end = python_time.time()
    var total_time = Float64(end) - Float64(start)
    var avg_time = total_time / Float64(num_iterations)

    # Cleanup
    query.free()
    embeddings.free()
    result_indices.free()

    return avg_time


fn main() raises:
    print("🔥 REALISTIC AIKI BENCHMARK - Large Dataset")
    print("=" * 70)

    var embedding_dim = 1536  # Matching mem0/OpenAI embeddings
    var top_k = 5

    print("\n📊 Configuration:")
    print("  Embedding dimension:", embedding_dim, "(matching mem0)")
    print("  Top-K:", top_k)
    print()

    # Test different dataset sizes
    print("Testing 5 dataset sizes...")
    print()

    # 100 memories
    print("Testing 100 memories...")
    var time_100 = benchmark_size(embedding_dim, 100, top_k, 100)
    print("  Avg time:", time_100 * 1000.0, "ms")

    # 500 memories
    print("Testing 500 memories...")
    var time_500 = benchmark_size(embedding_dim, 500, top_k, 50)
    print("  Avg time:", time_500 * 1000.0, "ms")

    # 1000 memories
    print("Testing 1000 memories...")
    var time_1000 = benchmark_size(embedding_dim, 1000, top_k, 20)
    print("  Avg time:", time_1000 * 1000.0, "ms")

    # 5000 memories
    print("Testing 5000 memories...")
    var time_5000 = benchmark_size(embedding_dim, 5000, top_k, 10)
    print("  Avg time:", time_5000 * 1000.0, "ms")

    # 10000 memories
    print("Testing 10000 memories...")
    var time_10000 = benchmark_size(embedding_dim, 10000, top_k, 5)
    print("  Avg time:", time_10000 * 1000.0, "ms")

    print()
    print("=" * 50)
    print("MOJO RESULTS:")
    print("  100 memories:", time_100 * 1000.0, "ms")
    print("  500 memories:", time_500 * 1000.0, "ms")
    print(" 1000 memories:", time_1000 * 1000.0, "ms")
    print(" 5000 memories:", time_5000 * 1000.0, "ms")
    print("10000 memories:", time_10000 * 1000.0, "ms")

    print("\n✅ Benchmark complete!")
    print("\n🎯 Observations:")
    print("  - SIMD vectorization (8-wide Float32)")
    print("  - Parallel batch processing")
    print("  - Real memory allocation overhead included")
    print("  - Performance scales with dataset size")
