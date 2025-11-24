#!/usr/bin/env python3
"""
🐍 Python Benchmark - Task Classification
Compare Python vs Mojo task classification performance
"""

import sys
import time

# Add AIKI_v3 to path to import TaskClassifier
sys.path.append('/run/media/jovnna/CEVAULT2TB/AIKI_v3')

from ai_proxy.core.task_classifier import TaskClassifier


def benchmark_python_classifier():
    """Benchmark Python TaskClassifier"""

    print("🐍 PYTHON TASK CLASSIFIER BENCHMARK")
    print("=" * 70)
    print()

    # Test cases (same as Mojo)
    test_cases = [
        "Can you help me debug this Python code?",
        "What is the latest news about AI?",
        "Write a creative story about a dragon",
        "Calculate the area of a circle with radius 5",
        "Translate this to Norwegian",
        "Summarize this article for me",
        # Additional realistic cases
        "I need help optimizing my database queries",
        "Explain quantum computing in simple terms",
        "Write a function to sort this list",
        "Find information about climate change",
    ]

    print("📋 Test Cases Classification:")
    print()

    for i, text in enumerate(test_cases, 1):
        # Convert to messages format
        messages = [{"role": "user", "content": text}]

        # Classify
        start = time.perf_counter()
        tasks = TaskClassifier.classify_task(messages)
        end = time.perf_counter()

        primary_task = tasks[0] if tasks else "general"
        elapsed_us = (end - start) * 1_000_000  # microseconds

        print(f"{i}. {text[:60]}")
        print(f"   → Task: {primary_task} ({elapsed_us:.2f} μs)")
        print()

    print("=" * 70)
    print("🔥 BATCH BENCHMARK - 1000 iterations")
    print()

    # Benchmark with many iterations
    num_iterations = 1000
    all_messages = [{"role": "user", "content": text} for text in test_cases]

    start = time.perf_counter()

    for _ in range(num_iterations):
        for messages_list in all_messages:
            messages = [messages_list]
            _ = TaskClassifier.classify_task(messages)

    end = time.perf_counter()

    total_time = end - start
    avg_time = total_time / num_iterations / len(test_cases)

    print(f"Total iterations: {num_iterations * len(test_cases)}")
    print(f"Total time: {total_time:.4f} s")
    print(f"Average per classification: {avg_time * 1000:.4f} ms")
    print(f"Average per classification: {avg_time * 1_000_000:.2f} μs")
    print()

    # Throughput
    throughput = (num_iterations * len(test_cases)) / total_time
    print(f"Throughput: {throughput:.2f} classifications/second")
    print()

    return avg_time, throughput


if __name__ == "__main__":
    avg_time, throughput = benchmark_python_classifier()

    print("=" * 70)
    print("📊 PYTHON BASELINE ESTABLISHED")
    print()
    print(f"  Average: {avg_time * 1000:.4f} ms")
    print(f"  Throughput: {throughput:.2f} classifications/s")
    print()
    print("Next: Run Mojo benchmark and compare!")
    print("      /home/jovnna/.pixi/bin/pixi run mojo run benchmark_task_classifier.mojo")
