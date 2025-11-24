#!/usr/bin/env mojo
"""
🔥 MOJO TASK CLASSIFIER BENCHMARK
Compare Mojo vs Python task classification performance
"""

from python import Python
from task_classifier import classify_task_mojo


fn main() raises:
    print("🔥 MOJO TASK CLASSIFIER BENCHMARK")
    print("=" * 70)
    print()

    # Test cases (same as Python benchmark)
    var test_cases = List[String]()
    test_cases.append("Can you help me debug this Python code?")
    test_cases.append("What is the latest news about AI?")
    test_cases.append("Write a creative story about a dragon")
    test_cases.append("Calculate the area of a circle with radius 5")
    test_cases.append("Translate this to Norwegian")
    test_cases.append("Summarize this article for me")
    test_cases.append("I need help optimizing my database queries")
    test_cases.append("Explain quantum computing in simple terms")
    test_cases.append("Write a function to sort this list")
    test_cases.append("Find information about climate change")

    print("📋 Test Cases Classification:")
    print()

    var python_time = Python.import_module("time")

    # Individual tests with timing
    for i in range(len(test_cases)):
        var text = test_cases[i]

        var start = python_time.perf_counter()
        var task = classify_task_mojo(text)
        var end = python_time.perf_counter()

        var elapsed_us = (Float64(end) - Float64(start)) * 1_000_000  # microseconds

        var preview = text
        if len(text) > 60:
            preview = text[:60]

        print(i+1, ".", preview)
        print("   → Task:", task, "(", elapsed_us, "μs )")
        print()

    print("=" * 70)
    print("🔥 BATCH BENCHMARK - 1000 iterations")
    print()

    var num_iterations = 1000
    var num_cases = len(test_cases)

    # Warm-up (5 iterations)
    for _ in range(5):
        for i in range(num_cases):
            _ = classify_task_mojo(test_cases[i])

    # Actual benchmark
    var start_batch = python_time.perf_counter()

    for _ in range(num_iterations):
        for i in range(num_cases):
            _ = classify_task_mojo(test_cases[i])

    var end_batch = python_time.perf_counter()

    var total_time = Float64(end_batch) - Float64(start_batch)
    var total_classifications = num_iterations * num_cases
    var avg_time = total_time / Float64(total_classifications)

    print("Total iterations:", total_classifications)
    print("Total time:", total_time, "s")
    print("Average per classification:", avg_time * 1000, "ms")
    print("Average per classification:", avg_time * 1_000_000, "μs")
    print()

    # Throughput
    var throughput = Float64(total_classifications) / total_time
    print("Throughput:", throughput, "classifications/second")
    print()

    print("=" * 70)
    print("📊 MOJO VS PYTHON COMPARISON")
    print()

    # Python baseline (from benchmark_task_classifier.py)
    var python_avg_us = 8.26
    var python_throughput = 121055.41

    var mojo_avg_us = avg_time * 1_000_000

    print("Python:")
    print("  Average:", python_avg_us, "μs")
    print("  Throughput:", python_throughput, "classifications/s")
    print()

    print("Mojo:")
    print("  Average:", mojo_avg_us, "μs")
    print("  Throughput:", throughput, "classifications/s")
    print()

    # Calculate speedup
    var speedup = python_avg_us / mojo_avg_us
    var throughput_ratio = throughput / python_throughput

    print("Speedup:", speedup, "x")
    print("Throughput improvement:", throughput_ratio, "x")
    print()

    if speedup > 1.0:
        print("✅ MOJO IS FASTER!")
    elif speedup > 0.8:
        print("⚡ MOJO IS COMPETITIVE (within 20%)")
    else:
        print("🔄 Python still faster - more optimization needed")

    print()
    print("=" * 70)
    print("🎯 PHASE 2A COMPLETE - Basic Task Classification")
    print()
    print("Next: Phase 2B - SIMD String Matching Optimization")
