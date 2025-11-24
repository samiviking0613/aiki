#!/usr/bin/env mojo
"""
🔥 STANDALONE MOJO SEARCH - Callable from Python
Loads embeddings from file and performs semantic search
"""

from algorithm import vectorize, parallelize
from math import sqrt
from memory import UnsafePointer, alloc
from python import Python


fn dot_product_vectorized(
    a: UnsafePointer[Float32],
    b: UnsafePointer[Float32],
    size: Int
) -> Float32:
    """SIMD vectorized dot product."""
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
    """Calculate vector norm."""
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
    """Calculate cosine similarity."""
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
    """Compute cosine similarities for all embeddings in parallel."""
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
    """Find top-K highest scoring indices."""
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
    """Perform semantic search and return top-K results."""
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
    """
    Load embeddings from files and perform search.

    Expected files:
    - /tmp/mojo_query.npy: Query embedding
    - /tmp/mojo_embeddings.npy: All embeddings matrix
    - /tmp/mojo_top_k.txt: Number of results to return

    Outputs:
    - /tmp/mojo_results_indices.npy: Top-K indices
    - /tmp/mojo_results_scores.npy: Top-K scores
    - /tmp/mojo_time.txt: Search time in milliseconds
    """

    var np = Python.import_module("numpy")
    var python_time = Python.import_module("time")

    # Load input files
    var query_np = np.load("/tmp/mojo_query.npy")
    var embeddings_np = np.load("/tmp/mojo_embeddings.npy")

    # Read top_k from file
    var top_k_file = open("/tmp/mojo_top_k.txt", "r")
    var top_k_str = top_k_file.read()
    top_k_file.close()
    var top_k = Int(top_k_str.strip())

    # Get dimensions
    var num_memories = Int(embeddings_np.shape[0])
    var embedding_dim = Int(embeddings_np.shape[1])

    # Allocate Mojo arrays
    var query = alloc[Float32](embedding_dim)
    var embeddings = alloc[Float32](num_memories * embedding_dim)
    var result_indices = alloc[Int32](top_k)

    # Load data
    for i in range(embedding_dim):
        query[i] = Float32(query_np[i])

    for emb_idx in range(num_memories):
        for dim_idx in range(embedding_dim):
            embeddings[emb_idx * embedding_dim + dim_idx] = Float32(embeddings_np[emb_idx][dim_idx])

    # Warm-up
    semantic_search(query, embeddings, num_memories, embedding_dim, top_k, result_indices)

    # Benchmark (single run for now)
    var start = python_time.perf_counter()
    semantic_search(query, embeddings, num_memories, embedding_dim, top_k, result_indices)
    var end = python_time.perf_counter()

    var search_time = (Float64(end) - Float64(start)) * 1000.0  # milliseconds

    # Save results
    var indices_list = Python.evaluate("list()")
    for i in range(top_k):
        _ = indices_list.append(Int(result_indices[i]))

    var indices_np = np.array(indices_list, dtype=np.int32)
    np.save("/tmp/mojo_results_indices.npy", indices_np)

    # Save timing
    var time_file = open("/tmp/mojo_time.txt", "w")
    _ = time_file.write(String(search_time))
    time_file.close()

    # Cleanup
    query.free()
    embeddings.free()
    result_indices.free()

    print("✅ Mojo search complete:", search_time, "ms")
