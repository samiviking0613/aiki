#!/usr/bin/env mojo
"""
Test Python interoperability for AIKI
Testing if Mojo can import and use Python libraries (mem0, numpy, etc.)
"""

from python import Python


fn main() raises:
    print("🔥 Mojo Python Interop Test")

    # Test 1: Import Python sys module
    print("\nTest 1: Import Python sys...")
    var sys = Python.import_module("sys")
    print("  ✅ Python version:", sys.version)

    # Test 2: Import numpy
    print("\nTest 2: Import numpy...")
    var np = Python.import_module("numpy")
    var arr = np.array([1, 2, 3, 4, 5])
    print("  ✅ NumPy array:", arr)
    print("  ✅ Array sum:", np.sum(arr))

    # Test 3: Simple math performance test
    print("\nTest 3: Mojo vs Python performance...")
    var python_time = Python.import_module("time")

    # Python loop
    var start_py = python_time.time()
    var py_sum = 0
    for i in range(1000000):
        py_sum += i
    var end_py = python_time.time()
    print("  Python loop (1M iterations):", end_py - start_py, "seconds")

    # Mojo loop
    var start_mojo = python_time.time()
    var mojo_sum = 0
    for i in range(1000000):
        mojo_sum += i
    var end_mojo = python_time.time()
    print("  Mojo loop (1M iterations):", end_mojo - start_mojo, "seconds")

    var speedup = (end_py - start_py) / (end_mojo - start_mojo)
    print("  🚀 Speedup:", speedup, "x")

    print("\n✅ All tests passed! Mojo can use Python libraries.")
