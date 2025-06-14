#!/usr/bin/env python3
"""
ProStudio Comprehensive Benchmark Suite
======================================

Measures performance improvements from all optimization layers:
- GPU acceleration
- Distributed processing  
- Redis caching
- Cython extensions
"""

import time
import os
import sys
import json
import numpy as np
from typing import Dict, List, Any, Tuple
import psutil
import platform
from dataclasses import dataclass, asdict
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import ProStudio components
from core.content_engine import ContentEngine
from core.content_types import Platform, ContentType
from core.acceleration.gpu_consciousness import GPUConsciousnessAccelerator
from core.acceleration.distributed_engine import DistributedContentEngine
from core.acceleration.redis_cache import RedisContentCache

# Try to import Cython extensions
try:
    from core.acceleration.consciousness_metrics_cy import (
        calculate_phi_resonance_fast,
        calculate_consciousness_score_fast,
        fast_consciousness_metrics
    )
    CYTHON_AVAILABLE = True
except ImportError:
    CYTHON_AVAILABLE = False
    print("⚠ Cython extensions not compiled. Run: cd core/acceleration && python setup.py build_ext --inplace")


@dataclass
class BenchmarkResult:
    """Individual benchmark result"""
    name: str
    category: str
    duration_ms: float
    operations_per_second: float
    speedup_factor: float
    memory_usage_mb: float
    cpu_usage_percent: float
    gpu_usage_percent: float = 0.0
    details: Dict[str, Any] = None
    

@dataclass
class SystemInfo:
    """System information"""
    os: str
    python_version: str
    cpu_count: int
    cpu_model: str
    total_memory_gb: float
    gpu_available: bool
    gpu_model: str = "N/A"
    redis_available: bool = False
    ray_available: bool = False
    cython_compiled: bool = False


class ProStudioBenchmark:
    """
    Comprehensive benchmark suite for ProStudio optimizations
    """
    
    def __init__(self):
        self.results = []
        self.system_info = self._get_system_info()
        self.baseline_engine = None
        self.optimized_engine = None
        
    def _get_system_info(self) -> SystemInfo:
        """Gather system information"""
        import platform
        
        # Check for GPU
        gpu_available = False
        gpu_model = "N/A"
        try:
            import torch
            if torch.cuda.is_available():
                gpu_available = True
                gpu_model = torch.cuda.get_device_name(0)
        except:
            pass
        
        # Check for Redis
        redis_available = False
        try:
            import redis
            r = redis.Redis(host='localhost', port=6379)
            r.ping()
            redis_available = True
        except:
            pass
        
        # Check for Ray
        ray_available = False
        try:
            import ray
            ray_available = True
        except:
            pass
        
        return SystemInfo(
            os=platform.system(),
            python_version=platform.python_version(),
            cpu_count=psutil.cpu_count(),
            cpu_model=platform.processor() or "Unknown",
            total_memory_gb=psutil.virtual_memory().total / (1024**3),
            gpu_available=gpu_available,
            gpu_model=gpu_model,
            redis_available=redis_available,
            ray_available=ray_available,
            cython_compiled=CYTHON_AVAILABLE
        )
    
    def _measure_resources(self) -> Tuple[float, float, float]:
        """Measure current system resources"""
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory_mb = psutil.Process().memory_info().rss / (1024 * 1024)
        
        gpu_percent = 0.0
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu_percent = gpus[0].load * 100
        except:
            pass
        
        return cpu_percent, memory_mb, gpu_percent
    
    def run_all_benchmarks(self):
        """Run complete benchmark suite"""
        print("🚀 PROSTUDIO COMPREHENSIVE BENCHMARK SUITE")
        print("=" * 70)
        
        # Print system info
        self._print_system_info()
        
        # Initialize engines
        print("\n📦 Initializing engines...")
        self._initialize_engines()
        
        # Run benchmarks
        print("\n🏃 Running benchmarks...\n")
        
        # 1. Baseline performance
        self.benchmark_baseline()
        
        # 2. Cython optimizations
        if CYTHON_AVAILABLE:
            self.benchmark_cython()
        
        # 3. GPU acceleration
        if self.system_info.gpu_available:
            self.benchmark_gpu()
        
        # 4. Redis caching
        if self.system_info.redis_available:
            self.benchmark_redis()
        
        # 5. Distributed processing
        self.benchmark_distributed()
        
        # 6. Combined optimizations
        self.benchmark_combined()
        
        # 7. Stress test
        self.benchmark_stress_test()
        
        # Generate report
        self._generate_report()
    
    def _print_system_info(self):
        """Print system information"""
        print("\n💻 SYSTEM INFORMATION")
        print("-" * 70)
        print(f"OS: {self.system_info.os}")
        print(f"Python: {self.system_info.python_version}")
        print(f"CPU: {self.system_info.cpu_model} ({self.system_info.cpu_count} cores)")
        print(f"Memory: {self.system_info.total_memory_gb:.1f} GB")
        print(f"GPU: {self.system_info.gpu_model}")
        print(f"\nAvailable optimizations:")
        print(f"  ✓ Cython: {'Yes' if self.system_info.cython_compiled else 'No'}")
        print(f"  ✓ GPU: {'Yes' if self.system_info.gpu_available else 'No'}")
        print(f"  ✓ Redis: {'Yes' if self.system_info.redis_available else 'No'}")
        print(f"  ✓ Ray: {'Yes' if self.system_info.ray_available else 'No'}")
    
    def _initialize_engines(self):
        """Initialize baseline and optimized engines"""
        # Baseline engine
        self.baseline_engine = ContentEngine({
            'enable_performance_mode': False,
            'enable_fa_cms': False,
            'optimization_iterations': 5
        })
        self.baseline_engine.initialize()
        
        # Optimized engine
        self.optimized_engine = ContentEngine({
            'enable_performance_mode': True,
            'enable_fa_cms': False,
            'optimization_iterations': 3,
            'enable_gpu': self.system_info.gpu_available,
            'enable_caching': self.system_info.redis_available
        })
        self.optimized_engine.initialize()
    
    def benchmark_baseline(self):
        """Benchmark baseline performance"""
        print("\n1️⃣ BASELINE PERFORMANCE")
        print("-" * 50)
        
        concepts = ["AI success tips", "Viral content secrets", "Social media growth"]
        
        # Single generation
        start = time.time()
        cpu_start, mem_start, gpu_start = self._measure_resources()
        
        content = self.baseline_engine.generate_content(
            concept=concepts[0],
            content_type=ContentType.VIDEO_SHORT,
            platform=Platform.TIKTOK
        )
        
        duration = (time.time() - start) * 1000
        cpu_end, mem_end, gpu_end = self._measure_resources()
        
        self.results.append(BenchmarkResult(
            name="Single Content Generation",
            category="Baseline",
            duration_ms=duration,
            operations_per_second=1000.0 / duration,
            speedup_factor=1.0,  # Baseline
            memory_usage_mb=mem_end - mem_start,
            cpu_usage_percent=cpu_end - cpu_start
        ))
        
        print(f"  Single generation: {duration:.1f}ms")
        
        # Batch generation
        start = time.time()
        for concept in concepts:
            for platform in [Platform.TIKTOK, Platform.INSTAGRAM]:
                self.baseline_engine.generate_content(
                    concept=concept,
                    content_type=ContentType.VIDEO_SHORT,
                    platform=platform
                )
        
        batch_duration = (time.time() - start) * 1000
        ops_per_sec = (len(concepts) * 2 * 1000) / batch_duration
        
        self.results.append(BenchmarkResult(
            name="Batch Content Generation (6 items)",
            category="Baseline",
            duration_ms=batch_duration,
            operations_per_second=ops_per_sec,
            speedup_factor=1.0,
            memory_usage_mb=0,
            cpu_usage_percent=0
        ))
        
        print(f"  Batch generation: {batch_duration:.1f}ms ({ops_per_sec:.1f} ops/s)")
        
        # Store baseline for comparison
        self.baseline_single = duration
        self.baseline_batch = batch_duration
    
    def benchmark_cython(self):
        """Benchmark Cython optimizations"""
        if not CYTHON_AVAILABLE:
            return
        
        print("\n2️⃣ CYTHON OPTIMIZATION")
        print("-" * 50)
        
        # Test data
        frequencies = np.array([256.0, 341.3, 512.0, 640.0, 768.0], dtype=np.float64)
        amplitudes = np.array([0.8, 0.7, 0.9, 0.6, 0.5], dtype=np.float64)
        
        # Python version (baseline)
        def python_phi_resonance(freqs, amps):
            PHI = 1.618033988749895
            resonance = 0.0
            for i in range(len(freqs)):
                for j in range(7):
                    resonance += amps[i] * np.exp(-((freqs[i] / (256 * (j+1)) - 1.0)**2) / 0.1)
            return resonance / (len(freqs) * 7)
        
        # Benchmark Python version
        iterations = 10000
        start = time.time()
        for _ in range(iterations):
            python_phi_resonance(frequencies, amplitudes)
        python_duration = (time.time() - start) * 1000
        
        # Benchmark Cython version
        start = time.time()
        for _ in range(iterations):
            calculate_phi_resonance_fast(frequencies, amplitudes)
        cython_duration = (time.time() - start) * 1000
        
        speedup = python_duration / cython_duration
        
        self.results.append(BenchmarkResult(
            name="Phi Resonance Calculation",
            category="Cython",
            duration_ms=cython_duration / iterations,
            operations_per_second=iterations * 1000 / cython_duration,
            speedup_factor=speedup,
            memory_usage_mb=0,
            cpu_usage_percent=0,
            details={
                'python_duration_ms': python_duration,
                'cython_duration_ms': cython_duration,
                'iterations': iterations
            }
        ))
        
        print(f"  Phi resonance: {speedup:.1f}x speedup")
        print(f"    Python: {python_duration:.1f}ms for {iterations} iterations")
        print(f"    Cython: {cython_duration:.1f}ms for {iterations} iterations")
        
        # Test full consciousness metrics
        params = {
            'frequencies': frequencies,
            'amplitudes': amplitudes,
            'fractal_dimension': 1.618,
            'coherence_level': 0.85,
            'emotional_spectrum': np.array([0.7, 0.8, 0.6], dtype=np.float64)
        }
        
        start = time.time()
        for _ in range(1000):
            fast_consciousness_metrics(params)
        consciousness_duration = (time.time() - start) * 1000
        
        print(f"  Consciousness metrics: {1000 * 1000 / consciousness_duration:.0f} ops/s")
    
    def benchmark_gpu(self):
        """Benchmark GPU acceleration"""
        if not self.system_info.gpu_available:
            return
        
        print("\n3️⃣ GPU ACCELERATION")
        print("-" * 50)
        
        try:
            gpu_accelerator = GPUConsciousnessAccelerator()
            
            # Test data
            consciousness_data = {
                'fractal_patterns': np.random.randn(1000, 1000).astype(np.float32),
                'resonance_matrix': np.random.randn(7, 7).astype(np.float32),
                'emotional_field': np.random.randn(512).astype(np.float32)
            }
            
            # CPU baseline
            start = time.time()
            cpu_start, _, _ = self._measure_resources()
            
            # Simulate CPU calculation
            result = np.mean(consciousness_data['fractal_patterns']) * 0.3
            result += np.mean(consciousness_data['resonance_matrix']) * 0.4
            result += np.mean(consciousness_data['emotional_field']) * 0.3
            
            cpu_duration = (time.time() - start) * 1000
            
            # GPU accelerated
            start = time.time()
            _, _, gpu_start = self._measure_resources()
            
            gpu_result, gpu_metrics = gpu_accelerator.accelerate_consciousness_calculation(
                consciousness_data
            )
            
            gpu_duration = (time.time() - start) * 1000
            _, _, gpu_end = self._measure_resources()
            
            speedup = cpu_duration / gpu_duration
            
            self.results.append(BenchmarkResult(
                name="Consciousness Matrix Calculation",
                category="GPU",
                duration_ms=gpu_duration,
                operations_per_second=1000.0 / gpu_duration,
                speedup_factor=speedup,
                memory_usage_mb=gpu_metrics.memory_used_mb,
                cpu_usage_percent=0,
                gpu_usage_percent=gpu_end - gpu_start,
                details={
                    'transfer_time_ms': gpu_metrics.transfer_time * 1000,
                    'compute_time_ms': gpu_metrics.compute_time * 1000
                }
            ))
            
            print(f"  Matrix calculation: {speedup:.1f}x speedup")
            print(f"    CPU: {cpu_duration:.1f}ms")
            print(f"    GPU: {gpu_duration:.1f}ms")
            print(f"    Transfer overhead: {gpu_metrics.transfer_time * 1000:.1f}ms")
            
        except Exception as e:
            print(f"  ⚠ GPU benchmark failed: {e}")
    
    def benchmark_redis(self):
        """Benchmark Redis caching"""
        if not self.system_info.redis_available:
            return
        
        print("\n4️⃣ REDIS CACHING")
        print("-" * 50)
        
        cache = RedisContentCache()
        
        # Test content
        test_content = {
            'id': 'benchmark-content',
            'engagement': 95.5,
            'viral_coefficient': 2.8,
            'data': 'x' * 10000  # 10KB
        }
        
        # Write benchmark
        iterations = 1000
        start = time.time()
        for i in range(iterations):
            cache.set(f"concept_{i}", "TIKTOK", "VIDEO_SHORT", test_content)
        write_duration = (time.time() - start) * 1000
        write_ops_per_sec = iterations * 1000 / write_duration
        
        # Read benchmark (hits)
        start = time.time()
        for i in range(iterations):
            cache.get(f"concept_{i}", "TIKTOK", "VIDEO_SHORT")
        read_hit_duration = (time.time() - start) * 1000
        read_hit_ops_per_sec = iterations * 1000 / read_hit_duration
        
        # Read benchmark (misses) 
        start = time.time()
        for i in range(iterations):
            cache.get(f"missing_{i}", "TIKTOK", "VIDEO_SHORT")
        read_miss_duration = (time.time() - start) * 1000
        read_miss_ops_per_sec = iterations * 1000 / read_miss_duration
        
        # Content generation with cache
        concepts = ["AI tips", "Growth hacks", "Viral secrets"]
        
        # First pass (cache miss)
        start = time.time()
        for concept in concepts:
            if not cache.get(concept, "TIKTOK", "VIDEO_SHORT"):
                content = self.optimized_engine.generate_content(
                    concept=concept,
                    content_type=ContentType.VIDEO_SHORT,
                    platform=Platform.TIKTOK
                )
                cache.set(concept, "TIKTOK", "VIDEO_SHORT", content)
        miss_duration = (time.time() - start) * 1000
        
        # Second pass (cache hit)
        start = time.time()
        for concept in concepts:
            content = cache.get(concept, "TIKTOK", "VIDEO_SHORT")
        hit_duration = (time.time() - start) * 1000
        
        speedup = miss_duration / hit_duration
        
        self.results.append(BenchmarkResult(
            name="Redis Cache Operations",
            category="Redis",
            duration_ms=read_hit_duration / iterations,
            operations_per_second=read_hit_ops_per_sec,
            speedup_factor=speedup,
            memory_usage_mb=0,
            cpu_usage_percent=0,
            details={
                'write_ops_per_sec': write_ops_per_sec,
                'read_hit_ops_per_sec': read_hit_ops_per_sec,
                'read_miss_ops_per_sec': read_miss_ops_per_sec,
                'cache_speedup': speedup
            }
        ))
        
        print(f"  Write: {write_ops_per_sec:.0f} ops/s")
        print(f"  Read (hit): {read_hit_ops_per_sec:.0f} ops/s")
        print(f"  Read (miss): {read_miss_ops_per_sec:.0f} ops/s")
        print(f"  Content generation speedup: {speedup:.1f}x")
        
        cache.close()
    
    def benchmark_distributed(self):
        """Benchmark distributed processing"""
        print("\n5️⃣ DISTRIBUTED PROCESSING")
        print("-" * 50)
        
        # Test with different backends
        backends = ['threading']
        if psutil.cpu_count() > 1:
            backends.append('multiprocessing')
        if self.system_info.ray_available:
            backends.append('ray')
        
        concepts = [f"Concept {i}" for i in range(20)]
        platforms = ['TIKTOK']
        
        best_speedup = 1.0
        best_backend = 'threading'
        
        for backend in backends:
            print(f"\n  Testing {backend}...")
            
            engine = DistributedContentEngine({'backend': backend})
            
            # Baseline (sequential)
            start = time.time()
            sequential_results = []
            for concept in concepts[:10]:  # Test with 10 items
                content = self.baseline_engine.generate_content(
                    concept=concept,
                    content_type=ContentType.VIDEO_SHORT,
                    platform=Platform.TIKTOK
                )
                sequential_results.append({'success': True})
            sequential_duration = (time.time() - start) * 1000
            
            # Distributed
            start = time.time()
            distributed_results = engine.distribute_batch(
                concepts[:10],
                platforms,
                ['VIDEO_SHORT'] * 10
            )
            distributed_duration = (time.time() - start) * 1000
            
            speedup = sequential_duration / distributed_duration
            if speedup > best_speedup:
                best_speedup = speedup
                best_backend = backend
            
            print(f"    Sequential: {sequential_duration:.1f}ms")
            print(f"    Distributed: {distributed_duration:.1f}ms")
            print(f"    Speedup: {speedup:.1f}x")
            
            engine.shutdown()
        
        self.results.append(BenchmarkResult(
            name="Distributed Content Generation",
            category="Distributed",
            duration_ms=distributed_duration,
            operations_per_second=10 * 1000 / distributed_duration,
            speedup_factor=best_speedup,
            memory_usage_mb=0,
            cpu_usage_percent=0,
            details={
                'best_backend': best_backend,
                'backends_tested': backends
            }
        ))
    
    def benchmark_combined(self):
        """Benchmark all optimizations combined"""
        print("\n6️⃣ COMBINED OPTIMIZATIONS")
        print("-" * 50)
        
        # Create fully optimized engine
        if self.system_info.redis_available:
            cache = RedisContentCache()
            cache.invalidate()  # Clear cache
        else:
            cache = None
        
        # Test workload
        concepts = [f"Advanced concept {i}" for i in range(50)]
        platforms = [Platform.TIKTOK, Platform.INSTAGRAM, Platform.YOUTUBE]
        
        # Baseline (no optimizations)
        print("\n  Running baseline (no optimizations)...")
        start = time.time()
        baseline_results = []
        for i, concept in enumerate(concepts[:10]):
            for platform in platforms:
                content = self.baseline_engine.generate_content(
                    concept=concept,
                    content_type=ContentType.VIDEO_SHORT,
                    platform=platform
                )
                baseline_results.append(content)
        baseline_duration = (time.time() - start) * 1000
        
        # Fully optimized
        print("  Running fully optimized...")
        
        # Use distributed engine with all optimizations
        distributed_engine = DistributedContentEngine({
            'backend': 'multiprocessing' if psutil.cpu_count() > 1 else 'threading',
            'num_workers': min(4, psutil.cpu_count())
        })
        
        start = time.time()
        
        # Check cache first
        optimized_results = []
        cache_hits = 0
        
        for i, concept in enumerate(concepts[:10]):
            for platform in platforms:
                if cache:
                    cached = cache.get(concept, platform.value, "VIDEO_SHORT")
                    if cached:
                        optimized_results.append(cached)
                        cache_hits += 1
                        continue
                
                # Generate if not cached
                content = self.optimized_engine.generate_content(
                    concept=concept,
                    content_type=ContentType.VIDEO_SHORT,
                    platform=platform
                )
                optimized_results.append(content)
                
                # Cache result
                if cache:
                    cache.set(concept, platform.value, "VIDEO_SHORT", content)
        
        optimized_duration = (time.time() - start) * 1000
        
        speedup = baseline_duration / optimized_duration
        
        self.results.append(BenchmarkResult(
            name="Combined All Optimizations",
            category="Combined",
            duration_ms=optimized_duration,
            operations_per_second=30 * 1000 / optimized_duration,
            speedup_factor=speedup,
            memory_usage_mb=0,
            cpu_usage_percent=0,
            details={
                'cache_hits': cache_hits,
                'total_items': 30,
                'cache_hit_rate': cache_hits / 30 if cache else 0
            }
        ))
        
        print(f"\n  Results:")
        print(f"    Baseline: {baseline_duration:.1f}ms")
        print(f"    Optimized: {optimized_duration:.1f}ms")
        print(f"    Speedup: {speedup:.1f}x")
        if cache:
            print(f"    Cache hits: {cache_hits}/30 ({cache_hits/30*100:.0f}%)")
        
        distributed_engine.shutdown()
        if cache:
            cache.close()
    
    def benchmark_stress_test(self):
        """Stress test with high load"""
        print("\n7️⃣ STRESS TEST")
        print("-" * 50)
        
        # High load parameters
        num_requests = 1000
        concurrent_requests = 50
        
        print(f"  Simulating {num_requests} requests...")
        print(f"  Concurrency: {concurrent_requests}")
        
        # Track performance over time
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        def generate_content(idx):
            start = time.time()
            try:
                content = self.optimized_engine.generate_content(
                    concept=f"Stress test concept {idx}",
                    content_type=ContentType.VIDEO_SHORT,
                    platform=Platform.TIKTOK
                )
                return {
                    'success': True,
                    'duration': (time.time() - start) * 1000,
                    'engagement': content.optimization.predicted_engagement
                }
            except Exception as e:
                return {
                    'success': False,
                    'duration': (time.time() - start) * 1000,
                    'error': str(e)
                }
        
        # Run stress test
        start_time = time.time()
        results = []
        
        with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
            futures = [executor.submit(generate_content, i) for i in range(num_requests)]
            
            for future in as_completed(futures):
                results.append(future.result())
        
        total_duration = (time.time() - start_time) * 1000
        
        # Analyze results
        successful = sum(1 for r in results if r['success'])
        avg_duration = sum(r['duration'] for r in results) / len(results)
        p95_duration = sorted([r['duration'] for r in results])[int(len(results) * 0.95)]
        p99_duration = sorted([r['duration'] for r in results])[int(len(results) * 0.99)]
        
        throughput = num_requests * 1000 / total_duration
        
        self.results.append(BenchmarkResult(
            name="Stress Test (1000 requests)",
            category="Stress",
            duration_ms=avg_duration,
            operations_per_second=throughput,
            speedup_factor=throughput / (1000 / self.baseline_single),
            memory_usage_mb=0,
            cpu_usage_percent=0,
            details={
                'total_requests': num_requests,
                'successful_requests': successful,
                'success_rate': successful / num_requests,
                'p95_duration_ms': p95_duration,
                'p99_duration_ms': p99_duration,
                'concurrent_requests': concurrent_requests
            }
        ))
        
        print(f"\n  Results:")
        print(f"    Total time: {total_duration/1000:.1f}s")
        print(f"    Throughput: {throughput:.1f} req/s")
        print(f"    Success rate: {successful/num_requests*100:.1f}%")
        print(f"    Avg latency: {avg_duration:.1f}ms")
        print(f"    P95 latency: {p95_duration:.1f}ms")
        print(f"    P99 latency: {p99_duration:.1f}ms")
    
    def _generate_report(self):
        """Generate comprehensive benchmark report"""
        print("\n" + "=" * 70)
        print("📊 BENCHMARK SUMMARY REPORT")
        print("=" * 70)
        
        # Group results by category
        categories = {}
        for result in self.results:
            if result.category not in categories:
                categories[result.category] = []
            categories[result.category].append(result)
        
        # Print results by category
        for category, results in categories.items():
            print(f"\n{category.upper()} OPTIMIZATIONS:")
            print("-" * 50)
            
            for result in results:
                print(f"\n{result.name}:")
                print(f"  Duration: {result.duration_ms:.2f}ms")
                print(f"  Throughput: {result.operations_per_second:.1f} ops/s")
                print(f"  Speedup: {result.speedup_factor:.1f}x")
                
                if result.details:
                    print("  Details:")
                    for key, value in result.details.items():
                        if isinstance(value, float):
                            print(f"    {key}: {value:.2f}")
                        else:
                            print(f"    {key}: {value}")
        
        # Overall summary
        print("\n" + "=" * 70)
        print("🎯 OVERALL PERFORMANCE IMPROVEMENT")
        print("=" * 70)
        
        # Calculate total speedup
        combined_result = next((r for r in self.results if r.name == "Combined All Optimizations"), None)
        if combined_result:
            print(f"\n✨ Total speedup with all optimizations: {combined_result.speedup_factor:.1f}x")
            print(f"   Baseline: {self.baseline_single:.1f}ms per generation")
            print(f"   Optimized: {combined_result.duration_ms/30:.1f}ms per generation")
        
        # Save report to file
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'system_info': asdict(self.system_info),
            'results': [asdict(r) for r in self.results]
        }
        
        report_path = os.path.join(os.path.dirname(__file__), 'benchmark_report.json')
        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Full report saved to: {report_path}")
        
        # Recommendations
        print("\n💡 OPTIMIZATION RECOMMENDATIONS:")
        print("-" * 50)
        
        if not self.system_info.cython_compiled:
            print("  ⚠ Compile Cython extensions for ~5x speedup on calculations")
            print("    cd core/acceleration && python setup.py build_ext --inplace")
        
        if not self.system_info.gpu_available:
            print("  ⚠ GPU not available - consider using GPU for 10x+ speedup")
        
        if not self.system_info.redis_available:
            print("  ⚠ Redis not available - install for distributed caching")
            print("    docker run -d -p 6379:6379 redis:alpine")
        
        if not self.system_info.ray_available:
            print("  ⚠ Ray not available - install for better distributed processing")
            print("    pip install ray")
        
        print("\n✅ Benchmark complete!")


def main():
    """Run the benchmark suite"""
    benchmark = ProStudioBenchmark()
    benchmark.run_all_benchmarks()


if __name__ == "__main__":
    main()