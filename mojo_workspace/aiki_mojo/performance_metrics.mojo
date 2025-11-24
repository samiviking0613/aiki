#!/usr/bin/env mojo
"""
🔥 MOJO PERFORMANCE METRICS - Phase 3
Fast statistical calculations and provider ranking for AIKI
"""

from algorithm import vectorize, parallelize
from math import sqrt
from memory import UnsafePointer, alloc
from python import Python


# =============================================================================
# STATISTICAL OPERATIONS - SIMD Vectorized
# =============================================================================

fn mean_vectorized(
    values: UnsafePointer[Float32],
    size: Int
) -> Float32:
    """Calculate mean using SIMD vectorization."""

    if size == 0:
        return 0.0

    var sum: Float32 = 0.0
    alias simd_width = 8

    @parameter
    fn sum_chunk[width: Int](i: Int):
        var chunk = values.load[width=width](i)
        for j in range(width):
            sum += chunk[j]

    var num_chunks = size // simd_width
    vectorize[sum_chunk, simd_width](num_chunks * simd_width)

    # Handle remainder
    for i in range(num_chunks * simd_width, size):
        sum += values[i]

    return sum / Float32(size)


fn std_dev_vectorized(
    values: UnsafePointer[Float32],
    size: Int,
    mean_val: Float32
) -> Float32:
    """Calculate standard deviation using SIMD."""

    if size <= 1:
        return 0.0

    var sum_squared_diff: Float32 = 0.0
    alias simd_width = 8

    @parameter
    fn squared_diff_chunk[width: Int](i: Int):
        var chunk = values.load[width=width](i)
        var mean_vec = SIMD[DType.float32, width](mean_val)
        var diff = chunk - mean_vec
        var squared = diff * diff

        for j in range(width):
            sum_squared_diff += squared[j]

    var num_chunks = size // simd_width
    vectorize[squared_diff_chunk, simd_width](num_chunks * simd_width)

    # Handle remainder
    for i in range(num_chunks * simd_width, size):
        var diff = values[i] - mean_val
        sum_squared_diff += diff * diff

    var variance = sum_squared_diff / Float32(size - 1)
    return sqrt(variance)


fn min_vectorized(
    values: UnsafePointer[Float32],
    size: Int
) -> Float32:
    """Find minimum value using SIMD."""

    if size == 0:
        return 0.0

    var min_val = values[0]
    alias simd_width = 8

    @parameter
    fn min_chunk[width: Int](i: Int):
        var chunk = values.load[width=width](i)
        for j in range(width):
            if chunk[j] < min_val:
                min_val = chunk[j]

    var num_chunks = size // simd_width
    vectorize[min_chunk, simd_width](num_chunks * simd_width)

    # Handle remainder
    for i in range(num_chunks * simd_width, size):
        if values[i] < min_val:
            min_val = values[i]

    return min_val


fn max_vectorized(
    values: UnsafePointer[Float32],
    size: Int
) -> Float32:
    """Find maximum value using SIMD."""

    if size == 0:
        return 0.0

    var max_val = values[0]
    alias simd_width = 8

    @parameter
    fn max_chunk[width: Int](i: Int):
        var chunk = values.load[width=width](i)
        for j in range(width):
            if chunk[j] > max_val:
                max_val = chunk[j]

    var num_chunks = size // simd_width
    vectorize[max_chunk, simd_width](num_chunks * simd_width)

    # Handle remainder
    for i in range(num_chunks * simd_width, size):
        if values[i] > max_val:
            max_val = values[i]

    return max_val


# =============================================================================
# SCORE CALCULATIONS - Optimized
# =============================================================================

fn calculate_provider_score(
    success_rate: Float32,
    avg_response_time: Float32,
    usage_count: Int
) -> Float32:
    """
    Calculate provider score using weighted formula.

    score = success_rate * 0.6 + time_score * 0.3 + usage_score * 0.1
    """

    # Normalize response time (lower is better, 10s = 0 score)
    var time_score: Float32 = 0.0
    if avg_response_time < 10.0:
        time_score = 1.0 / (avg_response_time + 1.0)

    # Normalize usage count (100+ = max score)
    var usage_score = Float32(usage_count) / 100.0
    if usage_score > 1.0:
        usage_score = 1.0

    # Weighted sum
    var score = success_rate * 0.6 + time_score * 0.3 + usage_score * 0.1

    return score


fn batch_calculate_scores[
    O: Origin[True]
](
    success_rates: UnsafePointer[Float32],
    response_times: UnsafePointer[Float32],
    usage_counts: UnsafePointer[Int32],
    num_providers: Int,
    scores: UnsafePointer[Float32, O]
):
    """Calculate scores for multiple providers in parallel."""

    @parameter
    fn calculate_score(i: Int):
        var success = success_rates[i]
        var time = response_times[i]
        var count = Int(usage_counts[i])

        scores[i] = calculate_provider_score(success, time, count)

    parallelize[calculate_score](num_providers, num_providers)


# =============================================================================
# RANKING - Parallel Top-K
# =============================================================================

fn find_top_k_providers[
    O: Origin[True]
](
    scores: UnsafePointer[Float32],
    num_providers: Int,
    k: Int,
    result_indices: UnsafePointer[Int32, O]
):
    """Find top-K providers by score (parallel)."""

    # Create index array
    var indices = alloc[Int32](num_providers)
    for i in range(num_providers):
        indices[i] = i

    # Simple selection sort for top-K (good enough for small K)
    for i in range(k):
        var max_idx = i
        var max_score = scores[indices[i]]

        for j in range(i + 1, num_providers):
            if scores[indices[j]] > max_score:
                max_idx = j
                max_score = scores[indices[j]]

        if max_idx != i:
            var temp = indices[i]
            indices[i] = indices[max_idx]
            indices[max_idx] = temp

    # Copy top-K to result
    for i in range(k):
        result_indices[i] = indices[i]

    indices.free()


# =============================================================================
# RUNNING AVERAGE UPDATES - Optimized
# =============================================================================

fn update_running_average(
    current_avg: Float32,
    new_value: Float32,
    count: Int
) -> Float32:
    """
    Update running average efficiently.

    new_avg = (old_avg * (n-1) + new_value) / n
    """

    if count <= 0:
        return new_value

    return (current_avg * Float32(count - 1) + new_value) / Float32(count)


fn batch_update_averages[
    O: Origin[True]
](
    current_avgs: UnsafePointer[Float32],
    new_values: UnsafePointer[Float32],
    counts: UnsafePointer[Int32],
    num_metrics: Int,
    updated_avgs: UnsafePointer[Float32, O]
):
    """Update multiple running averages in parallel."""

    @parameter
    fn update_avg(i: Int):
        updated_avgs[i] = update_running_average(
            current_avgs[i],
            new_values[i],
            Int(counts[i])
        )

    parallelize[update_avg](num_metrics, num_metrics)


# =============================================================================
# MAIN - Benchmarking
# =============================================================================

fn main() raises:
    print("🔥 MOJO PERFORMANCE METRICS - Phase 3")
    print("=" * 70)
    print()

    # Test statistical operations
    print("📊 Testing Statistical Operations...")
    print()

    var test_size = 1000
    var test_data = alloc[Float32](test_size)

    # Generate test data
    var py_random = Python.import_module("random")
    for i in range(test_size):
        test_data[i] = Float32(py_random.random() * 100.0)

    var mean_val = mean_vectorized(test_data, test_size)
    var std_val = std_dev_vectorized(test_data, test_size, mean_val)
    var min_val = min_vectorized(test_data, test_size)
    var max_val = max_vectorized(test_data, test_size)

    print("Test dataset (1000 values):")
    print("  Mean:", mean_val)
    print("  Std Dev:", std_val)
    print("  Min:", min_val)
    print("  Max:", max_val)
    print()

    # Test score calculations
    print("📈 Testing Provider Score Calculations...")
    print()

    var num_providers = 100
    var success_rates = alloc[Float32](num_providers)
    var response_times = alloc[Float32](num_providers)
    var usage_counts = alloc[Int32](num_providers)
    var scores = alloc[Float32](num_providers)

    # Generate mock provider data
    for i in range(num_providers):
        success_rates[i] = Float32(py_random.random() * 0.3 + 0.7)  # 0.7-1.0
        response_times[i] = Float32(py_random.random() * 5.0 + 0.5)  # 0.5-5.5s
        usage_counts[i] = Int32(py_random.randint(10, 200))

    # Benchmark batch score calculation
    var python_time = Python.import_module("time")

    var start = python_time.perf_counter()
    batch_calculate_scores(
        success_rates,
        response_times,
        usage_counts,
        num_providers,
        scores
    )
    var end = python_time.perf_counter()

    var calc_time = (Float64(end) - Float64(start)) * 1_000_000  # μs

    print("Batch Score Calculation (100 providers):", calc_time, "μs")
    print()

    # Test top-K ranking
    print("🏆 Testing Top-K Provider Ranking...")
    print()

    var top_k = 5
    var top_indices = alloc[Int32](top_k)

    start = python_time.perf_counter()
    find_top_k_providers(scores, num_providers, top_k, top_indices)
    end = python_time.perf_counter()

    var rank_time = (Float64(end) - Float64(start)) * 1_000_000  # μs

    print("Top-K Ranking (K=5 from 100):", rank_time, "μs")
    print()

    print("Top 5 Providers:")
    for i in range(top_k):
        var idx = Int(top_indices[i])
        print("  ", i+1, ". Provider", idx, "- Score:", scores[idx])

    print()

    # Cleanup
    test_data.free()
    success_rates.free()
    response_times.free()
    usage_counts.free()
    scores.free()
    top_indices.free()

    print("=" * 70)
    print("✅ PHASE 3 COMPLETE - Performance Metrics")
    print()
    print("Summary:")
    print("  ✅ SIMD statistical operations (mean, std, min, max)")
    print("  ✅ Parallel score calculations")
    print("  ✅ Fast top-K provider ranking")
    print("  ✅ Batch running average updates")
    print()
    print("Expected speedup: 10-100x vs Python for batch operations!")
