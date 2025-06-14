#!/usr/bin/env python3
"""
Distributed Content Engine
==========================

Multi-node distributed processing for massive scale content generation.
Supports both local multiprocessing and network-based distribution.
"""

import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
import asyncio
from typing import Dict, List, Optional, Any, Tuple, Callable
import time
import json
import pickle
import socket
import os
from dataclasses import dataclass
from queue import Queue
import threading

# Try to import distributed computing libraries
try:
    import ray
    RAY_AVAILABLE = True
except ImportError:
    RAY_AVAILABLE = False
    print("⚠ Ray not available for distributed computing")

try:
    from mpi4py import MPI
    MPI_AVAILABLE = True
except ImportError:
    MPI_AVAILABLE = False


@dataclass
class NodeMetrics:
    """Metrics for distributed node"""
    node_id: str
    tasks_completed: int
    avg_task_time: float
    cpu_usage: float
    memory_usage: float
    network_latency: float


@dataclass
class DistributedTask:
    """Task for distributed processing"""
    task_id: str
    task_type: str
    concept: str
    platform: str
    parameters: Dict[str, Any]
    priority: int = 5


class DistributedContentEngine:
    """
    Distributed content generation engine for massive scale
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._default_config()
        self.nodes = {}
        self.task_queue = Queue()
        self.results_queue = Queue()
        self.metrics = {}
        
        # Initialize based on available backends
        self.backend = self._detect_backend()
        self.executor = None
        
        if self.backend == "ray" and RAY_AVAILABLE:
            self._initialize_ray()
        elif self.backend == "multiprocessing":
            self._initialize_multiprocessing()
        else:
            self._initialize_threading()
    
    def _default_config(self) -> Dict[str, Any]:
        """Default distributed configuration"""
        return {
            'backend': 'auto',  # auto, ray, multiprocessing, threading
            'num_workers': mp.cpu_count(),
            'max_tasks_per_worker': 100,
            'task_timeout': 30,
            'enable_load_balancing': True,
            'enable_fault_tolerance': True,
            'checkpoint_interval': 100,
            'network_timeout': 5.0
        }
    
    def _detect_backend(self) -> str:
        """Detect best available backend"""
        if self.config['backend'] != 'auto':
            return self.config['backend']
        
        if RAY_AVAILABLE:
            return 'ray'
        elif mp.cpu_count() > 1:
            return 'multiprocessing'
        else:
            return 'threading'
    
    def _initialize_ray(self):
        """Initialize Ray for distributed processing"""
        print("🌐 Initializing Ray distributed backend...")
        
        # Initialize Ray
        if not ray.is_initialized():
            ray.init(num_cpus=self.config['num_workers'])
        
        # Create Ray actors for content generation
        @ray.remote
        class ContentWorker:
            def __init__(self, worker_id: int):
                self.worker_id = worker_id
                self.tasks_completed = 0
                # Import inside worker to avoid serialization issues
                from ..content_engine import ContentEngine
                self.engine = ContentEngine({
                    'enable_performance_mode': True,
                    'enable_fa_cms': False,
                    'optimization_iterations': 1  # Fast mode
                })
                self.engine.initialize()
            
            def generate_content(self, task: Dict) -> Dict:
                """Generate content for a task"""
                start_time = time.time()
                
                try:
                    from ..content_types import ContentType, Platform
                    
                    content = self.engine.generate_content(
                        concept=task['concept'],
                        content_type=ContentType[task['content_type']],
                        platform=Platform[task['platform']]
                    )
                    
                    self.tasks_completed += 1
                    
                    return {
                        'success': True,
                        'content_id': content.id,
                        'engagement': content.optimization.predicted_engagement,
                        'viral_coefficient': content.optimization.viral_coefficient,
                        'generation_time': time.time() - start_time,
                        'worker_id': self.worker_id
                    }
                except Exception as e:
                    return {
                        'success': False,
                        'error': str(e),
                        'worker_id': self.worker_id
                    }
            
            def get_metrics(self) -> Dict:
                """Get worker metrics"""
                return {
                    'worker_id': self.worker_id,
                    'tasks_completed': self.tasks_completed
                }
        
        # Create worker actors
        self.workers = [ContentWorker.remote(i) for i in range(self.config['num_workers'])]
        print(f"✓ Created {len(self.workers)} Ray workers")
    
    def _initialize_multiprocessing(self):
        """Initialize multiprocessing backend"""
        print(f"🔧 Initializing multiprocessing backend ({self.config['num_workers']} workers)...")
        
        self.executor = ProcessPoolExecutor(max_workers=self.config['num_workers'])
        
        # Create shared memory for metrics
        self.manager = mp.Manager()
        self.shared_metrics = self.manager.dict()
        
        print(f"✓ Multiprocessing pool ready")
    
    def _initialize_threading(self):
        """Initialize threading backend (fallback)"""
        print(f"🧵 Initializing threading backend ({self.config['num_workers']} threads)...")
        
        self.executor = ThreadPoolExecutor(max_workers=self.config['num_workers'])
        
        print(f"✓ Thread pool ready")
    
    def distribute_batch(self, 
                        concepts: List[str],
                        platforms: List[str],
                        content_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Distribute content generation across nodes
        
        Args:
            concepts: List of content concepts
            platforms: List of platforms
            content_types: Optional list of content types
            
        Returns:
            List of results
        """
        start_time = time.time()
        
        print(f"\n📡 Distributing {len(concepts) * len(platforms)} tasks across {self.backend} backend...")
        
        # Create tasks
        tasks = []
        for i, concept in enumerate(concepts):
            for platform in platforms:
                task = {
                    'task_id': f"task_{i}_{platform}",
                    'concept': concept,
                    'platform': platform,
                    'content_type': content_types[i] if content_types else 'VIDEO_SHORT'
                }
                tasks.append(task)
        
        # Distribute based on backend
        if self.backend == 'ray':
            results = self._distribute_ray(tasks)
        elif self.backend == 'multiprocessing':
            results = self._distribute_multiprocessing(tasks)
        else:
            results = self._distribute_threading(tasks)
        
        total_time = time.time() - start_time
        
        # Calculate metrics
        successful = sum(1 for r in results if r.get('success', False))
        avg_gen_time = sum(r.get('generation_time', 0) for r in results) / len(results) if results else 0
        
        print(f"\n✅ Distributed generation complete:")
        print(f"  Total tasks: {len(tasks)}")
        print(f"  Successful: {successful}")
        print(f"  Total time: {total_time:.2f}s")
        print(f"  Avg time per task: {avg_gen_time:.3f}s")
        print(f"  Parallelism efficiency: {(avg_gen_time * len(tasks)) / total_time:.1f}x")
        
        return results
    
    def _distribute_ray(self, tasks: List[Dict]) -> List[Dict]:
        """Distribute tasks using Ray"""
        if not hasattr(self, 'workers'):
            self._initialize_ray()
        
        # Submit tasks to workers
        futures = []
        for i, task in enumerate(tasks):
            worker_idx = i % len(self.workers)
            future = self.workers[worker_idx].generate_content.remote(task)
            futures.append(future)
        
        # Collect results
        results = ray.get(futures)
        
        return results
    
    def _distribute_multiprocessing(self, tasks: List[Dict]) -> List[Dict]:
        """Distribute tasks using multiprocessing"""
        from ..content_engine import ContentEngine
        from ..content_types import ContentType, Platform
        
        def worker_generate(task: Dict) -> Dict:
            """Worker function for multiprocessing"""
            # Each process creates its own engine
            engine = ContentEngine({
                'enable_performance_mode': True,
                'enable_fa_cms': False,
                'optimization_iterations': 1
            })
            engine.initialize()
            
            start_time = time.time()
            
            try:
                content = engine.generate_content(
                    concept=task['concept'],
                    content_type=ContentType[task['content_type']],
                    platform=Platform[task['platform']]
                )
                
                return {
                    'success': True,
                    'task_id': task['task_id'],
                    'content_id': content.id,
                    'engagement': content.optimization.predicted_engagement,
                    'viral_coefficient': content.optimization.viral_coefficient,
                    'generation_time': time.time() - start_time
                }
            except Exception as e:
                return {
                    'success': False,
                    'task_id': task['task_id'],
                    'error': str(e)
                }
        
        # Submit tasks
        futures = []
        for task in tasks:
            future = self.executor.submit(worker_generate, task)
            futures.append(future)
        
        # Collect results
        results = []
        for future in as_completed(futures):
            results.append(future.result())
        
        return results
    
    def _distribute_threading(self, tasks: List[Dict]) -> List[Dict]:
        """Distribute tasks using threading (single engine)"""
        # Import here to avoid circular imports
        from ..content_engine import ContentEngine
        from ..content_types import ContentType, Platform
        
        # Single shared engine for threads
        engine = ContentEngine({
            'enable_performance_mode': True,
            'enable_fa_cms': False,
            'optimization_iterations': 1
        })
        engine.initialize()
        
        def worker_generate(task: Dict) -> Dict:
            """Worker function for threading"""
            start_time = time.time()
            
            try:
                content = engine.generate_content(
                    concept=task['concept'],
                    content_type=ContentType[task['content_type']],
                    platform=Platform[task['platform']]
                )
                
                return {
                    'success': True,
                    'task_id': task['task_id'],
                    'content_id': content.id,
                    'engagement': content.optimization.predicted_engagement,
                    'viral_coefficient': content.optimization.viral_coefficient,
                    'generation_time': time.time() - start_time
                }
            except Exception as e:
                return {
                    'success': False,
                    'task_id': task['task_id'],
                    'error': str(e)
                }
        
        # Submit tasks
        futures = []
        for task in tasks:
            future = self.executor.submit(worker_generate, task)
            futures.append(future)
        
        # Collect results
        results = []
        for future in as_completed(futures):
            results.append(future.result())
        
        return results
    
    def scale_test(self, num_tasks: int = 100) -> Dict[str, Any]:
        """
        Test scalability with increasing number of tasks
        
        Args:
            num_tasks: Number of tasks to test
            
        Returns:
            Scalability metrics
        """
        print(f"\n🚀 Scalability Test ({self.backend} backend)")
        print(f"   Testing with {num_tasks} tasks...")
        print("-" * 50)
        
        # Test different batch sizes
        batch_sizes = [1, 10, 50, num_tasks]
        results = {}
        
        concepts = [f"Test concept {i}" for i in range(num_tasks)]
        platforms = ['TIKTOK', 'INSTAGRAM', 'YOUTUBE']
        
        for batch_size in batch_sizes:
            if batch_size > num_tasks:
                continue
            
            # Process in batches
            start_time = time.time()
            all_results = []
            
            for i in range(0, num_tasks, batch_size):
                batch_concepts = concepts[i:i+batch_size]
                batch_results = self.distribute_batch(
                    batch_concepts,
                    platforms[:1],  # Single platform for consistency
                    ['VIDEO_SHORT'] * len(batch_concepts)
                )
                all_results.extend(batch_results)
            
            total_time = time.time() - start_time
            
            results[batch_size] = {
                'total_time': total_time,
                'tasks_per_second': num_tasks / total_time,
                'avg_time_per_task': total_time / num_tasks
            }
            
            print(f"\nBatch size {batch_size}:")
            print(f"  Total time: {total_time:.2f}s")
            print(f"  Tasks/second: {results[batch_size]['tasks_per_second']:.1f}")
        
        # Calculate optimal batch size
        optimal_batch = min(results.keys(), key=lambda k: results[k]['total_time'])
        
        print(f"\n✅ Optimal batch size: {optimal_batch}")
        print(f"   Best performance: {results[optimal_batch]['tasks_per_second']:.1f} tasks/second")
        
        return results
    
    def benchmark_backends(self) -> Dict[str, Any]:
        """Benchmark different backend options"""
        print("\n🏁 Backend Benchmark Comparison")
        print("=" * 50)
        
        results = {}
        test_tasks = 20
        
        # Test each available backend
        backends = []
        if RAY_AVAILABLE:
            backends.append('ray')
        backends.extend(['multiprocessing', 'threading'])
        
        original_backend = self.backend
        
        for backend in backends:
            print(f"\nTesting {backend}...")
            
            # Reinitialize with different backend
            self.backend = backend
            self.config['backend'] = backend
            
            if backend == 'ray':
                self._initialize_ray()
            elif backend == 'multiprocessing':
                self._initialize_multiprocessing()
            else:
                self._initialize_threading()
            
            # Run test
            start = time.time()
            batch_results = self.distribute_batch(
                [f"Test {i}" for i in range(test_tasks)],
                ['TIKTOK'],
                ['VIDEO_SHORT'] * test_tasks
            )
            total_time = time.time() - start
            
            results[backend] = {
                'total_time': total_time,
                'tasks_per_second': test_tasks / total_time,
                'success_rate': sum(1 for r in batch_results if r.get('success', False)) / len(batch_results)
            }
            
            print(f"  Time: {total_time:.2f}s")
            print(f"  Speed: {results[backend]['tasks_per_second']:.1f} tasks/s")
            print(f"  Success: {results[backend]['success_rate']:.0%}")
        
        # Restore original backend
        self.backend = original_backend
        
        # Find best backend
        best_backend = max(results.keys(), key=lambda k: results[k]['tasks_per_second'])
        
        print(f"\n🏆 Best backend: {best_backend}")
        print(f"   Speed: {results[best_backend]['tasks_per_second']:.1f} tasks/second")
        
        return results
    
    def shutdown(self):
        """Shutdown distributed engine"""
        print("\n🛑 Shutting down distributed engine...")
        
        if self.backend == 'ray' and ray.is_initialized():
            ray.shutdown()
        elif self.executor:
            self.executor.shutdown(wait=True)
        
        print("✓ Distributed engine shutdown complete")


def demo_distributed_engine():
    """Demonstrate distributed content generation"""
    print("DISTRIBUTED CONTENT ENGINE DEMO")
    print("=" * 60)
    
    # Create distributed engine
    engine = DistributedContentEngine()
    
    # Test 1: Basic distribution
    print("\n1️⃣ Basic Distributed Generation:")
    
    concepts = [
        "AI-powered social media success",
        "The secret to viral content",
        "Transform your content strategy"
    ]
    platforms = ['TIKTOK', 'INSTAGRAM', 'YOUTUBE']
    
    results = engine.distribute_batch(concepts, platforms)
    
    successful = sum(1 for r in results if r.get('success', False))
    print(f"\n  Generated: {successful}/{len(results)} successful")
    
    # Test 2: Scalability test
    print("\n2️⃣ Scalability Test:")
    scale_results = engine.scale_test(num_tasks=50)
    
    # Test 3: Backend comparison (if available)
    if RAY_AVAILABLE or mp.cpu_count() > 1:
        print("\n3️⃣ Backend Comparison:")
        backend_results = engine.benchmark_backends()
    
    # Shutdown
    engine.shutdown()
    
    print("\n✅ Distributed engine demo complete!")


if __name__ == "__main__":
    demo_distributed_engine()