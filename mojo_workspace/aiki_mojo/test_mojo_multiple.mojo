#!/usr/bin/env mojo
"""
Test Mojo memory search with multiple iterations for fair comparison
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

    # Selection sort for top-k
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


fn main() raises:
    print("🔥 Mojo Memory Search - Multiple Iterations Benchmark")
    print("=" * 50)

    var embedding_dim = 128
    var num_memories = 100
    var top_k = 5
    var num_iterations = 100

    print("\n📊 Test Configuration:")
    print("  Embedding dimension:", embedding_dim)
    print("  Number of memories:", num_memories)
    print("  Top-K:", top_k)
    print("  Iterations:", num_iterations)

    var query = alloc[Float32](embedding_dim)
    var embeddings = alloc[Float32](num_memories * embedding_dim)
    var result_indices = alloc[Int32](top_k)

    # Fill with same pattern as Python benchmark
    for i in range(embedding_dim):
        query[i] = Float32(i) / Float32(embedding_dim)

    # Each embedding has all values set to (embedding_idx % embedding_dim) / embedding_dim
    for emb_idx in range(num_memories):
        var value = Float32(emb_idx % embedding_dim) / Float32(embedding_dim)
        for dim_idx in range(embedding_dim):
            embeddings[emb_idx * embedding_dim + dim_idx] = value

    print("\n🔍 Running Mojo semantic search...")

    var python_time = Python.import_module("time")
    var start = python_time.time()

    for _ in range(num_iterations):
        semantic_search(query, embeddings, num_memories, embedding_dim, top_k, result_indices)

    var end = python_time.time()
    var total_time = end - start
    var avg_time = total_time / num_iterations

    print("✅ Total time:", total_time, "seconds")
    print("✅ Average time:", avg_time, "seconds (", avg_time * 1000.0, "ms)")

    print("\n📋 Top-", top_k, "results (indices):")
    for i in range(top_k):
        print(" ", i+1, ". Memory index:", result_indices[i])

    query.free()
    embeddings.free()
    result_indices.free()

    print("\n✅ Benchmark complete!")
