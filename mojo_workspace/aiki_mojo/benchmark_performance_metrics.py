#!/usr/bin/env python3
"""
🐍 Python Benchmark - Performance Metrics
Compare Python vs Mojo for statistical calculations and provider ranking
"""

import time
import random
import statistics


def mean_python(values):
    """Calculate mean using Python."""
    return sum(values) / len(values) if values else 0.0


def std_dev_python(values):
    """Calculate standard deviation using Python."""
    return statistics.stdev(values) if len(values) > 1 else 0.0


def calculate_provider_score(success_rate, avg_response_time, usage_count):
    """Calculate provider score."""
    time_score = 1.0 / (avg_response_time + 1.0) if avg_response_time < 10.0 else 0.0
    usage_score = min(usage_count / 100.0, 1.0)
    return success_rate * 0.6 + time_score * 0.3 + usage_score * 0.1


def batch_calculate_scores(success_rates, response_times, usage_counts):
    """Calculate scores for multiple providers."""
    return [
        calculate_provider_score(sr, rt, uc)
        for sr, rt, uc in zip(success_rates, response_times, usage_counts)
    ]


def find_top_k_providers(scores, k):
    """Find top-K providers by score."""
    indexed_scores = list(enumerate(scores))
    indexed_scores.sort(key=lambda x: x[1], reverse=True)
    return [idx for idx, score in indexed_scores[:k]]


def main():
    print("🐍 PYTHON PERFORMANCE METRICS BENCHMARK")
    print("=" * 70)
    print()

    # Test statistical operations
    print("📊 Testing Statistical Operations...")
    print()

    test_size = 1000
    random.seed(42)
    test_data = [random.random() * 100.0 for _ in range(test_size)]

    start = time.perf_counter()
    mean_val = mean_python(test_data)
    std_val = std_dev_python(test_data)
    min_val = min(test_data)
    max_val = max(test_data)
    end = time.perf_counter()

    stats_time = (end - start) * 1_000_000  # μs

    print(f"Test dataset (1000 values):")
    print(f"  Mean: {mean_val:.6f}")
    print(f"  Std Dev: {std_val:.6f}")
    print(f"  Min: {min_val:.6f}")
    print(f"  Max: {max_val:.6f}")
    print(f"  Time: {stats_time:.2f} μs")
    print()

    # Test score calculations
    print("📈 Testing Provider Score Calculations...")
    print()

    num_providers = 100
    random.seed(42)

    success_rates = [random.random() * 0.3 + 0.7 for _ in range(num_providers)]
    response_times = [random.random() * 5.0 + 0.5 for _ in range(num_providers)]
    usage_counts = [random.randint(10, 200) for _ in range(num_providers)]

    # Benchmark batch score calculation
    num_iterations = 100

    start = time.perf_counter()
    for _ in range(num_iterations):
        scores = batch_calculate_scores(success_rates, response_times, usage_counts)
    end = time.perf_counter()

    calc_time = ((end - start) / num_iterations) * 1_000_000  # μs

    print(f"Batch Score Calculation (100 providers): {calc_time:.2f} μs")
    print()

    # Test top-K ranking
    print("🏆 Testing Top-K Provider Ranking...")
    print()

    top_k = 5

    start = time.perf_counter()
    for _ in range(num_iterations):
        top_indices = find_top_k_providers(scores, top_k)
    end = time.perf_counter()

    rank_time = ((end - start) / num_iterations) * 1_000_000  # μs

    print(f"Top-K Ranking (K=5 from 100): {rank_time:.2f} μs")
    print()

    print("Top 5 Providers:")
    for i, idx in enumerate(top_indices, 1):
        print(f"  {i}. Provider {idx} - Score: {scores[idx]:.6f}")

    print()
    print("=" * 70)
    print("📊 PYTHON BASELINE ESTABLISHED")
    print()
    print(f"  Statistical operations: {stats_time:.2f} μs")
    print(f"  Batch score calc: {calc_time:.2f} μs")
    print(f"  Top-K ranking: {rank_time:.2f} μs")
    print()
    print("Next: Compare with Mojo Phase 3 results!")


if __name__ == "__main__":
    main()
