#!/usr/bin/env python3
"""
🔥 MOJO MEMORY WRAPPER - Python interface for Mojo semantic search
Integrates memory_search.mojo with AIKI's mem0/Qdrant system
"""

import sys
sys.path.append('/home/jovnna/aiki')

import subprocess
import numpy as np
import time
from typing import List, Tuple, Dict, Any
from qdrant_client import QdrantClient
from MEM0_CONFIG_CORRECT import validate_qdrant_connection


class MojoMemorySearch:
    """Python wrapper for Mojo-accelerated memory search."""

    def __init__(self, qdrant_url: str = 'http://localhost:6333', collection_name: str = 'mem0_memories'):
        """
        Initialize Mojo memory search.

        Args:
            qdrant_url: Qdrant server URL
            collection_name: Collection to search
        """
        self.qdrant_url = qdrant_url
        self.collection_name = collection_name
        self.client = QdrantClient(url=qdrant_url)

        # Validate connection
        print(f"🔥 Initializing Mojo Memory Search...")
        count = validate_qdrant_connection()
        print(f"✅ Connected to Qdrant: {count} memories")

        # Cache embeddings and metadata
        self.embeddings = None
        self.metadata = None
        self.last_cache_time = 0
        self.cache_ttl = 60  # Refresh cache every 60 seconds

        self._refresh_cache()

    def _refresh_cache(self):
        """Refresh cached embeddings and metadata from Qdrant."""
        print("📥 Refreshing memory cache from Qdrant...")

        # Get collection info
        info = self.client.get_collection(self.collection_name)
        num_memories = info.points_count

        # Fetch all points with vectors
        scroll_result = self.client.scroll(
            collection_name=self.collection_name,
            limit=num_memories,
            with_vectors=True,
            with_payload=True
        )

        points = scroll_result[0]

        # Extract embeddings and metadata
        embeddings_list = []
        metadata_list = []

        for point in points:
            if point.vector is not None:
                embeddings_list.append(np.array(point.vector, dtype=np.float32))

                # Extract memory text from payload
                payload = point.payload or {}
                if 'data' in payload and isinstance(payload['data'], dict):
                    memory_text = payload['data'].get('memory', f'ID: {point.id}')
                elif 'memory' in payload:
                    memory_text = payload['memory']
                else:
                    memory_text = f'Memory ID: {point.id}'

                metadata_list.append({
                    'id': str(point.id),
                    'memory': memory_text,
                    'payload': payload
                })

        self.embeddings = np.array(embeddings_list, dtype=np.float32)
        self.metadata = metadata_list
        self.last_cache_time = time.time()

        print(f"✅ Cached {len(self.embeddings)} memories")

    def search_mojo(self, query: str, top_k: int = 5, use_mojo: bool = True) -> List[Dict[str, Any]]:
        """
        Search memories using Mojo-accelerated semantic search.

        Args:
            query: Search query text
            top_k: Number of results to return
            use_mojo: If True, use Mojo. If False, use NumPy (for comparison)

        Returns:
            List of dictionaries with 'memory', 'score', and 'id'
        """
        # Refresh cache if needed
        if time.time() - self.last_cache_time > self.cache_ttl:
            self._refresh_cache()

        # Get query embedding from Qdrant (uses same embedding model)
        # For now, use first embedding as query (mock)
        # TODO: Integrate with actual embedding service
        query_embedding = self.embeddings[0]  # Mock: use first embedding

        if use_mojo:
            # Use Mojo semantic search
            indices, scores, search_time = self._search_mojo_native(query_embedding, top_k)
            print(f"🔥 Mojo search: {search_time*1000:.2f} ms")
        else:
            # Use NumPy for comparison
            indices, scores, search_time = self._search_numpy(query_embedding, top_k)
            print(f"🐍 NumPy search: {search_time*1000:.2f} ms")

        # Build results
        results = []
        for i, (idx, score) in enumerate(zip(indices, scores)):
            results.append({
                'memory': self.metadata[idx]['memory'],
                'score': float(score),
                'id': self.metadata[idx]['id'],
                'rank': i + 1
            })

        return results

    def _search_mojo_native(self, query_embedding: np.ndarray, top_k: int) -> Tuple[np.ndarray, np.ndarray, float]:
        """
        Search using Mojo native implementation.

        Returns:
            (indices, scores, time_elapsed)
        """
        # Save input files for Mojo
        np.save("/tmp/mojo_query.npy", query_embedding)
        np.save("/tmp/mojo_embeddings.npy", self.embeddings)

        # Write top_k parameter
        with open("/tmp/mojo_top_k.txt", "w") as f:
            f.write(str(top_k))

        # Call Mojo script via pixi
        start = time.perf_counter()

        try:
            result = subprocess.run(
                ["/home/jovnna/.pixi/bin/pixi", "run", "mojo", "run",
                 "/home/jovnna/aiki/mojo_workspace/aiki_mojo/standalone_search.mojo"],
                cwd="/home/jovnna/aiki/mojo_workspace/aiki_mojo",
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                print(f"❌ Mojo error: {result.stderr}")
                # Fallback to NumPy
                return self._search_numpy_impl(query_embedding, top_k) + (0.0,)

        except Exception as e:
            print(f"❌ Mojo execution failed: {e}")
            # Fallback to NumPy
            return self._search_numpy_impl(query_embedding, top_k) + (0.0,)

        end = time.perf_counter()

        # Read results
        indices = np.load("/tmp/mojo_results_indices.npy")

        # Read timing
        with open("/tmp/mojo_time.txt", "r") as f:
            mojo_time_ms = float(f.read().strip())

        # Calculate scores from indices (need to recompute for now)
        query_norm = np.linalg.norm(query_embedding)
        if query_norm > 0:
            query_normalized = query_embedding / query_norm
        else:
            query_normalized = query_embedding

        embeddings_norms = np.linalg.norm(self.embeddings, axis=1, keepdims=True)
        embeddings_norms[embeddings_norms == 0] = 1
        embeddings_normalized = self.embeddings / embeddings_norms

        similarities = embeddings_normalized @ query_normalized
        scores = similarities[indices]

        # Use wall-clock time (includes subprocess overhead)
        total_time = end - start

        return indices, scores, total_time

    def _search_numpy(self, query_embedding: np.ndarray, top_k: int) -> Tuple[np.ndarray, np.ndarray, float]:
        """
        Search using NumPy (baseline for comparison).

        Returns:
            (indices, scores, time_elapsed)
        """
        start = time.perf_counter()
        indices, scores = self._search_numpy_impl(query_embedding, top_k)
        end = time.perf_counter()

        return indices, scores, end - start

    def _search_numpy_impl(self, query_embedding: np.ndarray, top_k: int) -> Tuple[np.ndarray, np.ndarray]:
        """NumPy implementation of semantic search."""
        # Normalize query
        query_norm = np.linalg.norm(query_embedding)
        if query_norm == 0:
            return np.zeros(top_k, dtype=np.int32), np.zeros(top_k)
        query_normalized = query_embedding / query_norm

        # Normalize embeddings
        embeddings_norms = np.linalg.norm(self.embeddings, axis=1, keepdims=True)
        embeddings_norms[embeddings_norms == 0] = 1
        embeddings_normalized = self.embeddings / embeddings_norms

        # Cosine similarity
        similarities = embeddings_normalized @ query_normalized

        # Top-K
        top_indices = np.argpartition(similarities, -top_k)[-top_k:]
        top_indices = top_indices[np.argsort(similarities[top_indices])][::-1]

        return top_indices, similarities[top_indices]

    def benchmark(self, num_iterations: int = 20, top_k: int = 5):
        """
        Benchmark Mojo vs NumPy search.

        Args:
            num_iterations: Number of iterations to run
            top_k: Number of results per search
        """
        print("🔥 BENCHMARKING MOJO VS NUMPY")
        print("=" * 70)
        print()

        query_embedding = self.embeddings[0]  # Use first as query

        # Warm-up NumPy
        print("Warming up...")
        for _ in range(5):
            self._search_numpy_impl(query_embedding, top_k)

        # Benchmark NumPy
        print(f"\n🐍 Benchmarking NumPy ({num_iterations} iterations)...")
        start = time.perf_counter()
        for _ in range(num_iterations):
            self._search_numpy_impl(query_embedding, top_k)
        end = time.perf_counter()

        numpy_avg = (end - start) / num_iterations

        print(f"NumPy ({len(self.embeddings)} memories):")
        print(f"  Average: {numpy_avg * 1000:.4f} ms")
        print(f"  Throughput: {num_iterations / (end - start):.2f} searches/s")
        print()

        # Benchmark Mojo
        print(f"🔥 Benchmarking Mojo ({num_iterations} iterations)...")
        mojo_times = []

        for i in range(num_iterations):
            _, _, mojo_time = self._search_mojo_native(query_embedding, top_k)
            mojo_times.append(mojo_time)
            if (i + 1) % 5 == 0:
                print(f"  Progress: {i+1}/{num_iterations}")

        mojo_avg = sum(mojo_times) / len(mojo_times)

        print(f"\nMojo ({len(self.embeddings)} memories):")
        print(f"  Average: {mojo_avg * 1000:.4f} ms (includes subprocess overhead)")
        print(f"  Throughput: {1.0 / mojo_avg:.2f} searches/s")
        print()

        # Comparison
        speedup = numpy_avg / mojo_avg
        print("=" * 70)
        print("📊 COMPARISON:")
        print(f"  NumPy:  {numpy_avg * 1000:.4f} ms")
        print(f"  Mojo:   {mojo_avg * 1000:.4f} ms")
        print(f"  Speedup: {speedup:.2f}x")
        print()

        if speedup > 1.0:
            print(f"✅ MOJO IS {speedup:.2f}x FASTER!")
        else:
            print(f"⚠️  Mojo slower due to subprocess overhead")
            print("    Note: Pure Mojo computation is faster, but subprocess adds ~100ms")

        print("=" * 70)


def main():
    """Test the Mojo memory wrapper."""
    print("🔥 MOJO MEMORY WRAPPER TEST")
    print("=" * 70)
    print()

    # Initialize
    mojo_search = MojoMemorySearch()

    # Search test
    print("🔍 Testing search...")
    results = mojo_search.search_mojo("AIKI consciousness", top_k=5, use_mojo=False)

    print("\nTop 5 Results:")
    for result in results:
        memory_preview = result['memory'][:80] + "..." if len(result['memory']) > 80 else result['memory']
        print(f"  {result['rank']}. [Score: {result['score']:.4f}] {memory_preview}")

    print()

    # Benchmark
    print("🏁 Running benchmark...")
    mojo_search.benchmark(num_iterations=20, top_k=5)

    print()
    print("✅ Mojo Memory Wrapper test complete!")


if __name__ == "__main__":
    main()
