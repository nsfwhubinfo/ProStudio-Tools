#!/usr/bin/env python3
"""
Redis Content Cache
===================

Advanced caching system using Redis for ultra-fast content retrieval
and distributed cache sharing across multiple ProStudio instances.
"""

import json
import pickle
import hashlib
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import numpy as np

# Try to import Redis
try:
    import redis
    from redis.sentinel import Sentinel
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("⚠ Redis not available, using in-memory cache")

# Try to import Redis extensions
try:
    import redis.asyncio as redis_async
    ASYNC_REDIS_AVAILABLE = True
except ImportError:
    ASYNC_REDIS_AVAILABLE = False


@dataclass
class CacheStats:
    """Cache performance statistics"""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    avg_hit_time_ms: float = 0.0
    avg_miss_time_ms: float = 0.0
    memory_usage_mb: float = 0.0
    items_cached: int = 0


class RedisContentCache:
    """
    Redis-based content caching for extreme performance
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._default_config()
        self.redis_available = REDIS_AVAILABLE
        self.stats = CacheStats()
        
        # Fallback to in-memory cache if Redis not available
        self.memory_cache = {}
        self.cache_timestamps = {}
        
        if self.redis_available:
            self._initialize_redis()
        else:
            print("📦 Using in-memory cache (install redis-py for Redis support)")
    
    def _default_config(self) -> Dict[str, Any]:
        """Default Redis configuration"""
        return {
            'host': 'localhost',
            'port': 6379,
            'db': 0,
            'password': None,
            'socket_timeout': 5,
            'connection_pool_max': 50,
            'ttl_seconds': 3600,  # 1 hour default TTL
            'max_memory_mb': 1024,  # 1GB max memory
            'eviction_policy': 'allkeys-lru',
            'enable_compression': True,
            'enable_pipeline': True,
            'enable_cluster': False,
            'enable_sentinel': False,
            'sentinel_hosts': []
        }
    
    def _initialize_redis(self):
        """Initialize Redis connection"""
        print("🔴 Initializing Redis cache...")
        
        try:
            if self.config['enable_sentinel']:
                # Redis Sentinel for HA
                sentinel = Sentinel(self.config['sentinel_hosts'])
                self.redis = sentinel.master_for('mymaster', socket_timeout=0.1)
            elif self.config['enable_cluster']:
                # Redis Cluster
                from rediscluster import RedisCluster
                startup_nodes = [{"host": self.config['host'], "port": self.config['port']}]
                self.redis = RedisCluster(startup_nodes=startup_nodes, decode_responses=True)
            else:
                # Standard Redis
                pool = redis.ConnectionPool(
                    host=self.config['host'],
                    port=self.config['port'],
                    db=self.config['db'],
                    password=self.config['password'],
                    max_connections=self.config['connection_pool_max'],
                    socket_timeout=self.config['socket_timeout']
                )
                self.redis = redis.Redis(connection_pool=pool)
            
            # Test connection
            self.redis.ping()
            
            # Configure Redis
            self._configure_redis()
            
            print(f"✓ Redis connected to {self.config['host']}:{self.config['port']}")
            
        except Exception as e:
            print(f"❌ Redis connection failed: {e}")
            self.redis_available = False
    
    def _configure_redis(self):
        """Configure Redis settings"""
        try:
            # Set max memory
            self.redis.config_set('maxmemory', f"{self.config['max_memory_mb']}mb")
            
            # Set eviction policy
            self.redis.config_set('maxmemory-policy', self.config['eviction_policy'])
            
            print(f"  ✓ Max memory: {self.config['max_memory_mb']}MB")
            print(f"  ✓ Eviction policy: {self.config['eviction_policy']}")
            
        except Exception as e:
            print(f"  ⚠ Could not configure Redis: {e}")
    
    def _generate_key(self, 
                     concept: str,
                     platform: str,
                     content_type: str,
                     params: Optional[Dict] = None) -> str:
        """Generate cache key from parameters"""
        key_data = {
            'concept': concept,
            'platform': platform,
            'content_type': content_type,
            'params': params or {}
        }
        
        # Create deterministic key
        key_str = json.dumps(key_data, sort_keys=True)
        key_hash = hashlib.sha256(key_str.encode()).hexdigest()[:16]
        
        return f"prostudio:content:{platform}:{key_hash}"
    
    def _serialize_content(self, content: Any) -> bytes:
        """Serialize content for storage"""
        if self.config['enable_compression']:
            import zlib
            data = pickle.dumps(content)
            return zlib.compress(data)
        else:
            return pickle.dumps(content)
    
    def _deserialize_content(self, data: bytes) -> Any:
        """Deserialize content from storage"""
        if self.config['enable_compression']:
            import zlib
            data = zlib.decompress(data)
        
        return pickle.loads(data)
    
    def get(self, 
            concept: str,
            platform: str,
            content_type: str,
            params: Optional[Dict] = None) -> Optional[Any]:
        """
        Get cached content
        
        Args:
            concept: Content concept
            platform: Target platform
            content_type: Type of content
            params: Additional parameters
            
        Returns:
            Cached content or None
        """
        start_time = time.time()
        key = self._generate_key(concept, platform, content_type, params)
        
        try:
            if self.redis_available:
                # Get from Redis
                data = self.redis.get(key)
                
                if data:
                    content = self._deserialize_content(data)
                    self.stats.hits += 1
                    hit_time = (time.time() - start_time) * 1000
                    self._update_hit_time(hit_time)
                    return content
                else:
                    self.stats.misses += 1
                    miss_time = (time.time() - start_time) * 1000
                    self._update_miss_time(miss_time)
                    return None
            else:
                # Get from memory cache
                if key in self.memory_cache:
                    # Check TTL
                    if time.time() - self.cache_timestamps[key] < self.config['ttl_seconds']:
                        self.stats.hits += 1
                        return self.memory_cache[key]
                    else:
                        # Expired
                        del self.memory_cache[key]
                        del self.cache_timestamps[key]
                        self.stats.evictions += 1
                
                self.stats.misses += 1
                return None
                
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    def set(self,
            concept: str,
            platform: str,
            content_type: str,
            content: Any,
            params: Optional[Dict] = None,
            ttl: Optional[int] = None) -> bool:
        """
        Cache content
        
        Args:
            concept: Content concept
            platform: Target platform
            content_type: Type of content
            content: Content to cache
            params: Additional parameters
            ttl: Time to live in seconds
            
        Returns:
            Success status
        """
        key = self._generate_key(concept, platform, content_type, params)
        ttl = ttl or self.config['ttl_seconds']
        
        try:
            if self.redis_available:
                # Set in Redis
                data = self._serialize_content(content)
                self.redis.setex(key, ttl, data)
                self.stats.items_cached = self.redis.dbsize()
                return True
            else:
                # Set in memory cache
                self.memory_cache[key] = content
                self.cache_timestamps[key] = time.time()
                
                # Simple LRU eviction if cache too large
                if len(self.memory_cache) > 1000:
                    oldest_key = min(self.cache_timestamps.keys(), 
                                   key=lambda k: self.cache_timestamps[k])
                    del self.memory_cache[oldest_key]
                    del self.cache_timestamps[oldest_key]
                    self.stats.evictions += 1
                
                self.stats.items_cached = len(self.memory_cache)
                return True
                
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    def batch_get(self, keys: List[Tuple[str, str, str]]) -> Dict[str, Any]:
        """
        Batch get multiple items
        
        Args:
            keys: List of (concept, platform, content_type) tuples
            
        Returns:
            Dictionary of key -> content
        """
        results = {}
        
        if self.redis_available and self.config['enable_pipeline']:
            # Use Redis pipeline for efficiency
            pipe = self.redis.pipeline()
            
            cache_keys = []
            for concept, platform, content_type in keys:
                key = self._generate_key(concept, platform, content_type)
                cache_keys.append(key)
                pipe.get(key)
            
            # Execute pipeline
            values = pipe.execute()
            
            # Process results
            for i, (key_tuple, value) in enumerate(zip(keys, values)):
                if value:
                    content = self._deserialize_content(value)
                    results[cache_keys[i]] = content
                    self.stats.hits += 1
                else:
                    self.stats.misses += 1
        else:
            # Sequential gets
            for concept, platform, content_type in keys:
                content = self.get(concept, platform, content_type)
                if content:
                    key = self._generate_key(concept, platform, content_type)
                    results[key] = content
        
        return results
    
    def batch_set(self, items: List[Tuple[str, str, str, Any]]) -> bool:
        """
        Batch set multiple items
        
        Args:
            items: List of (concept, platform, content_type, content) tuples
            
        Returns:
            Success status
        """
        try:
            if self.redis_available and self.config['enable_pipeline']:
                # Use Redis pipeline
                pipe = self.redis.pipeline()
                
                for concept, platform, content_type, content in items:
                    key = self._generate_key(concept, platform, content_type)
                    data = self._serialize_content(content)
                    pipe.setex(key, self.config['ttl_seconds'], data)
                
                # Execute pipeline
                pipe.execute()
                return True
            else:
                # Sequential sets
                for concept, platform, content_type, content in items:
                    self.set(concept, platform, content_type, content)
                return True
                
        except Exception as e:
            print(f"Batch set error: {e}")
            return False
    
    def invalidate(self, pattern: Optional[str] = None):
        """
        Invalidate cache entries
        
        Args:
            pattern: Optional pattern to match (e.g., "prostudio:content:tiktok:*")
        """
        try:
            if self.redis_available:
                if pattern:
                    # Delete by pattern
                    keys = self.redis.keys(pattern)
                    if keys:
                        self.redis.delete(*keys)
                        print(f"Invalidated {len(keys)} cache entries")
                else:
                    # Clear all ProStudio keys
                    keys = self.redis.keys("prostudio:*")
                    if keys:
                        self.redis.delete(*keys)
                        print(f"Cleared {len(keys)} cache entries")
            else:
                # Clear memory cache
                if pattern:
                    keys_to_delete = [k for k in self.memory_cache.keys() if pattern in k]
                    for key in keys_to_delete:
                        del self.memory_cache[key]
                        del self.cache_timestamps[key]
                else:
                    self.memory_cache.clear()
                    self.cache_timestamps.clear()
                
        except Exception as e:
            print(f"Invalidate error: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        hit_rate = self.stats.hits / (self.stats.hits + self.stats.misses) if (self.stats.hits + self.stats.misses) > 0 else 0
        
        stats_dict = asdict(self.stats)
        stats_dict['hit_rate'] = hit_rate
        
        if self.redis_available:
            try:
                info = self.redis.info()
                stats_dict['redis_memory_mb'] = info.get('used_memory', 0) / 1024 / 1024
                stats_dict['redis_connected_clients'] = info.get('connected_clients', 0)
                stats_dict['redis_total_commands'] = info.get('total_commands_processed', 0)
            except:
                pass
        
        return stats_dict
    
    def _update_hit_time(self, time_ms: float):
        """Update average hit time"""
        if self.stats.hits == 1:
            self.stats.avg_hit_time_ms = time_ms
        else:
            # Running average
            self.stats.avg_hit_time_ms = (
                (self.stats.avg_hit_time_ms * (self.stats.hits - 1) + time_ms) / 
                self.stats.hits
            )
    
    def _update_miss_time(self, time_ms: float):
        """Update average miss time"""
        if self.stats.misses == 1:
            self.stats.avg_miss_time_ms = time_ms
        else:
            # Running average
            self.stats.avg_miss_time_ms = (
                (self.stats.avg_miss_time_ms * (self.stats.misses - 1) + time_ms) / 
                self.stats.misses
            )
    
    def warm_cache(self, popular_concepts: List[str], platforms: List[str]):
        """
        Warm cache with popular content combinations
        
        Args:
            popular_concepts: List of popular concepts
            platforms: List of platforms to cache for
        """
        print("🔥 Warming Redis cache...")
        
        from ..content_engine import ContentEngine
        from ..content_types import ContentType, Platform
        
        # Create engine for content generation
        engine = ContentEngine({
            'enable_performance_mode': True,
            'enable_fa_cms': False,
            'optimization_iterations': 1
        })
        engine.initialize()
        
        warmed = 0
        
        for concept in popular_concepts:
            for platform_str in platforms:
                try:
                    # Check if already cached
                    if self.get(concept, platform_str, 'VIDEO_SHORT'):
                        continue
                    
                    # Generate and cache
                    content = engine.generate_content(
                        concept=concept,
                        content_type=ContentType.VIDEO_SHORT,
                        platform=Platform[platform_str]
                    )
                    
                    # Cache the generated content
                    self.set(concept, platform_str, 'VIDEO_SHORT', content)
                    warmed += 1
                    
                except Exception as e:
                    print(f"  ⚠ Failed to warm {concept} for {platform_str}: {e}")
        
        print(f"  ✓ Warmed {warmed} cache entries")
        
        return warmed
    
    def benchmark(self, num_operations: int = 1000) -> Dict[str, Any]:
        """
        Benchmark cache performance
        
        Args:
            num_operations: Number of operations to test
            
        Returns:
            Benchmark results
        """
        print(f"\n🚀 Redis Cache Benchmark ({num_operations} operations)")
        print("-" * 50)
        
        # Test data
        test_content = {
            'id': 'test-content',
            'data': 'x' * 1000,  # 1KB of data
            'metrics': {'engagement': 85.5, 'viral': 2.1}
        }
        
        # Write test
        print("\nWrite performance:")
        start = time.time()
        for i in range(num_operations):
            self.set(f"concept_{i}", "TIKTOK", "VIDEO_SHORT", test_content)
        write_time = time.time() - start
        write_ops_per_sec = num_operations / write_time
        
        print(f"  Time: {write_time:.3f}s")
        print(f"  Ops/sec: {write_ops_per_sec:.0f}")
        
        # Read test (all hits)
        print("\nRead performance (hits):")
        start = time.time()
        for i in range(num_operations):
            self.get(f"concept_{i}", "TIKTOK", "VIDEO_SHORT")
        read_hit_time = time.time() - start
        read_hit_ops_per_sec = num_operations / read_hit_time
        
        print(f"  Time: {read_hit_time:.3f}s")
        print(f"  Ops/sec: {read_hit_ops_per_sec:.0f}")
        
        # Read test (all misses)
        print("\nRead performance (misses):")
        start = time.time()
        for i in range(num_operations):
            self.get(f"missing_{i}", "TIKTOK", "VIDEO_SHORT")
        read_miss_time = time.time() - start
        read_miss_ops_per_sec = num_operations / read_miss_time
        
        print(f"  Time: {read_miss_time:.3f}s")
        print(f"  Ops/sec: {read_miss_ops_per_sec:.0f}")
        
        # Stats
        print("\nCache Statistics:")
        stats = self.get_stats()
        print(f"  Hit rate: {stats['hit_rate']:.1%}")
        print(f"  Avg hit time: {stats['avg_hit_time_ms']:.2f}ms")
        print(f"  Avg miss time: {stats['avg_miss_time_ms']:.2f}ms")
        
        if self.redis_available:
            print(f"  Redis memory: {stats.get('redis_memory_mb', 0):.1f}MB")
        
        return {
            'write_ops_per_sec': write_ops_per_sec,
            'read_hit_ops_per_sec': read_hit_ops_per_sec,
            'read_miss_ops_per_sec': read_miss_ops_per_sec,
            'hit_rate': stats['hit_rate']
        }
    
    def close(self):
        """Close Redis connection"""
        if self.redis_available and hasattr(self, 'redis'):
            self.redis.close()
            print("✓ Redis connection closed")


def demo_redis_cache():
    """Demonstrate Redis caching"""
    print("REDIS CONTENT CACHE DEMO")
    print("=" * 60)
    
    # Create cache
    cache = RedisContentCache()
    
    # Test 1: Basic operations
    print("\n1️⃣ Basic Cache Operations:")
    
    # Set
    test_content = {
        'id': 'demo-content',
        'engagement': 95.5,
        'viral_coefficient': 2.5
    }
    
    success = cache.set("AI viral secrets", "TIKTOK", "VIDEO_SHORT", test_content)
    print(f"  Set: {'✓' if success else '✗'}")
    
    # Get (hit)
    retrieved = cache.get("AI viral secrets", "TIKTOK", "VIDEO_SHORT")
    print(f"  Get (hit): {'✓' if retrieved else '✗'}")
    
    # Get (miss)
    missing = cache.get("nonexistent", "TIKTOK", "VIDEO_SHORT")
    print(f"  Get (miss): {'✓' if missing is None else '✗'}")
    
    # Test 2: Batch operations
    print("\n2️⃣ Batch Operations:")
    
    # Batch set
    batch_items = [
        ("Concept 1", "TIKTOK", "VIDEO_SHORT", {'id': 1}),
        ("Concept 2", "INSTAGRAM", "IMAGE_POST", {'id': 2}),
        ("Concept 3", "YOUTUBE", "VIDEO_LONG", {'id': 3})
    ]
    
    batch_success = cache.batch_set(batch_items)
    print(f"  Batch set: {'✓' if batch_success else '✗'}")
    
    # Test 3: Cache warming
    print("\n3️⃣ Cache Warming:")
    
    popular = ["How to go viral", "AI content tips", "Social media growth"]
    platforms = ["TIKTOK", "INSTAGRAM"]
    
    if REDIS_AVAILABLE:
        warmed = cache.warm_cache(popular, platforms)
        print(f"  Warmed: {warmed} entries")
    else:
        print("  ⚠ Skipping (Redis not available)")
    
    # Test 4: Performance benchmark
    print("\n4️⃣ Performance Benchmark:")
    benchmark_results = cache.benchmark(num_operations=100)
    
    # Show final stats
    print("\n📊 Final Statistics:")
    final_stats = cache.get_stats()
    print(f"  Total hits: {final_stats['hits']}")
    print(f"  Total misses: {final_stats['misses']}")
    print(f"  Hit rate: {final_stats['hit_rate']:.1%}")
    print(f"  Items cached: {final_stats['items_cached']}")
    
    # Close
    cache.close()
    
    print("\n✅ Redis cache demo complete!")
    
    if not REDIS_AVAILABLE:
        print("\n💡 Install redis-py and run Redis server for distributed caching:")
        print("   pip install redis")
        print("   docker run -d -p 6379:6379 redis:alpine")


if __name__ == "__main__":
    demo_redis_cache()