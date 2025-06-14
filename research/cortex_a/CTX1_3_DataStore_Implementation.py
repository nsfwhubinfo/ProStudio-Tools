#!/usr/bin/env python3
"""
CORTEX_DataStore Implementation
===============================
Milestone CTX.1.3: Columnar storage with FA-CMS/FMO integration

This implementation provides:
1. Three-tier columnar storage (Hot/Warm/Cold)
2. FA-CMS connector for CSS field synchronization
3. FMO connector for entity relationships
4. Columnar query execution engine
5. ZPTV compression simulation
"""

import asyncio
import numpy as np
import time
import json
import mmap
import os
import pickle
import zlib
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple, Union
from enum import Enum
from datetime import datetime, timedelta
import threading
from collections import defaultdict


# ============================================================================
# Column Schema and Types
# ============================================================================

@dataclass
class ColumnSchema:
    """Schema definition for a columnar store column"""
    name: str
    dtype: np.dtype
    dimensions: Optional[int] = None
    compression: str = "none"  # none, zptv, dictionary, rle
    nullable: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


class CompressionType(Enum):
    """Supported compression types"""
    NONE = "none"
    ZPTV = "zptv"
    DICTIONARY = "dictionary"
    RLE = "rle"


# ============================================================================
# Columnar Array Implementation
# ============================================================================

class ColumnarArray:
    """Memory-efficient columnar array with compression support"""
    
    def __init__(self, schema: ColumnSchema, initial_capacity: int = 10000):
        self.schema = schema
        self.capacity = initial_capacity
        self.size = 0
        self.null_bitmap = None
        
        # Initialize storage based on type
        if schema.dtype == np.dtype('object') or 'U' in str(schema.dtype):
            # String columns use dictionary encoding
            self.dictionary = {}
            self.reverse_dict = {}
            self.indices = np.empty(initial_capacity, dtype=np.uint32)
            self.dict_size = 0
        else:
            # Numeric columns
            if schema.dimensions:
                # Multi-dimensional (vectors)
                self.data = np.empty((initial_capacity, schema.dimensions), dtype=schema.dtype)
            else:
                # Scalar
                self.data = np.empty(initial_capacity, dtype=schema.dtype)
        
        # Compression
        self.compressed_chunks = []
        self.compression_ratio = 1.0
    
    def append(self, value: Any):
        """Append value to column"""
        if self.size >= self.capacity:
            self._grow()
        
        if value is None and self.schema.nullable:
            if self.null_bitmap is None:
                self.null_bitmap = np.zeros(self.capacity, dtype=bool)
            self.null_bitmap[self.size] = True
        
        if hasattr(self, 'dictionary'):
            # Dictionary encoding for strings
            # Handle lists by converting to string
            if isinstance(value, list):
                value_key = json.dumps(value)
            else:
                value_key = value
                
            if value_key not in self.dictionary:
                self.dictionary[value_key] = self.dict_size
                self.reverse_dict[self.dict_size] = value
                self.dict_size += 1
            self.indices[self.size] = self.dictionary[value_key]
        else:
            self.data[self.size] = value
        
        self.size += 1
    
    def get_slice(self, start: int, end: int) -> np.ndarray:
        """Get slice of column data"""
        if hasattr(self, 'dictionary'):
            # Decode dictionary values
            indices_slice = self.indices[start:end]
            return np.array([self.reverse_dict.get(idx, None) for idx in indices_slice])
        else:
            return self.data[start:end].copy()
    
    def get_item(self, index: int) -> Any:
        """Get single item"""
        if self.null_bitmap is not None and self.null_bitmap[index]:
            return None
        
        if hasattr(self, 'dictionary'):
            return self.reverse_dict.get(self.indices[index], None)
        else:
            return self.data[index]
    
    def _grow(self):
        """Grow array capacity"""
        new_capacity = int(self.capacity * 1.5)
        
        if hasattr(self, 'dictionary'):
            new_indices = np.empty(new_capacity, dtype=np.uint32)
            new_indices[:self.size] = self.indices[:self.size]
            self.indices = new_indices
        else:
            if self.schema.dimensions:
                new_data = np.empty((new_capacity, self.schema.dimensions), dtype=self.schema.dtype)
                new_data[:self.size] = self.data[:self.size]
            else:
                new_data = np.empty(new_capacity, dtype=self.schema.dtype)
                new_data[:self.size] = self.data[:self.size]
            self.data = new_data
        
        if self.null_bitmap is not None:
            new_bitmap = np.zeros(new_capacity, dtype=bool)
            new_bitmap[:self.size] = self.null_bitmap[:self.size]
            self.null_bitmap = new_bitmap
        
        self.capacity = new_capacity
    
    def compress(self) -> bytes:
        """Compress column data"""
        if self.schema.compression == CompressionType.ZPTV.value:
            return self._compress_zptv()
        elif self.schema.compression == CompressionType.RLE.value:
            return self._compress_rle()
        else:
            # Default zlib compression
            if hasattr(self, 'dictionary'):
                data_bytes = pickle.dumps((self.dictionary, self.indices[:self.size]))
            else:
                data_bytes = self.data[:self.size].tobytes()
            return zlib.compress(data_bytes)
    
    def _compress_zptv(self) -> bytes:
        """ZPTV compression (simulated)"""
        # Simulate ZPTV's quantum-inspired compression
        # In reality, this would use the actual ZPTV algorithm
        if hasattr(self, 'data'):
            # For numeric data, use advanced compression
            if self.schema.dtype == np.complex128:
                # Special handling for CSS fields
                phase = np.angle(self.data[:self.size])
                amplitude = np.abs(self.data[:self.size])
                
                # Quantize phase for better compression
                quantized_phase = np.round(phase / (np.pi/8)) * (np.pi/8)
                
                compressed = pickle.dumps({
                    'phase': quantized_phase,
                    'amplitude': amplitude,
                    'type': 'css_field'
                })
            else:
                compressed = pickle.dumps(self.data[:self.size])
        else:
            compressed = pickle.dumps((self.dictionary, self.indices[:self.size]))
        
        # Apply zlib on top
        compressed = zlib.compress(compressed, level=9)
        self.compression_ratio = len(compressed) / (self.size * self.schema.dtype.itemsize)
        return compressed


# ============================================================================
# Storage Tiers
# ============================================================================

class HotTierColumnarStore:
    """In-memory columnar store for hot data"""
    
    def __init__(self, capacity: int = 1_000_000):
        self.capacity = capacity
        self.columns: Dict[str, ColumnarArray] = {}
        self.row_count = 0
        self.memory_usage_mb = 0.0
        self.last_access = {}
        self._lock = threading.Lock()
    
    def add_column(self, schema: ColumnSchema):
        """Add a new column"""
        with self._lock:
            if schema.name not in self.columns:
                self.columns[schema.name] = ColumnarArray(schema)
    
    async def batch_insert(self, data: Dict[str, Union[List, np.ndarray]]):
        """Insert batch of columnar data"""
        with self._lock:
            # Validate all columns have same length
            lengths = [len(v) for v in data.values()]
            if len(set(lengths)) != 1:
                raise ValueError("All columns must have same length")
            
            batch_size = lengths[0]
            
            # Ensure columns exist
            for col_name in data.keys():
                if col_name not in self.columns:
                    # Auto-detect schema
                    sample = data[col_name][0] if isinstance(data[col_name], list) else data[col_name][0]
                    if isinstance(sample, str):
                        dtype = np.dtype('object')
                    elif isinstance(sample, complex):
                        dtype = np.complex128
                    else:
                        dtype = np.array([sample]).dtype
                    
                    schema = ColumnSchema(col_name, dtype)
                    self.add_column(schema)
            
            # Insert data
            for col_name, values in data.items():
                column = self.columns[col_name]
                for value in values:
                    column.append(value)
            
            self.row_count += batch_size
            self._update_memory_usage()
    
    async def get_aged_data(self, hours: int = 1) -> Dict[str, np.ndarray]:
        """Get data older than specified hours"""
        cutoff_time = time.time() - (hours * 3600)
        aged_indices = []
        
        # For demo, simulate aging based on row position
        # In production, would track actual timestamps
        if self.row_count > 1000:
            aged_count = min(100, self.row_count // 10)
            aged_indices = list(range(aged_count))
            
            if aged_indices:
                aged_data = {}
                for col_name, column in self.columns.items():
                    aged_data[col_name] = column.get_slice(0, aged_count)
                
                return aged_data
        
        return {}
    
    async def evict(self, keys: List[Any]):
        """Evict data from hot tier"""
        # For demo, we'll just track eviction
        # In production, would actually remove data
        evict_count = len(keys)
        print(f"📤 Evicting {evict_count} rows from hot tier")
    
    def query(self, columns: List[str], predicate=None) -> Dict[str, np.ndarray]:
        """Query data from hot tier"""
        with self._lock:
            result = {}
            
            for col_name in columns:
                if col_name in self.columns:
                    column = self.columns[col_name]
                    data = column.get_slice(0, column.size)
                    
                    # Apply predicate if provided
                    if predicate:
                        mask = predicate(data)
                        data = data[mask]
                    
                    result[col_name] = data
                    self.last_access[col_name] = time.time()
            
            return result
    
    def _update_memory_usage(self):
        """Update memory usage estimate"""
        total_bytes = 0
        for column in self.columns.values():
            if hasattr(column, 'data'):
                total_bytes += column.data.nbytes
            else:
                # Dictionary encoded
                total_bytes += column.indices.nbytes
                total_bytes += sum(len(str(k)) + 4 for k in column.dictionary.keys())
        
        self.memory_usage_mb = total_bytes / (1024 * 1024)


class WarmTierColumnarStore:
    """Memory-mapped columnar store for warm data"""
    
    def __init__(self, path: str = "/tmp/cortex_warm", max_size_gb: int = 10):
        self.path = path
        self.max_size_gb = max_size_gb
        self.columns = {}
        self.row_count = 0
        self.disk_usage_gb = 0.0
        self.compression_ratio = 1.0
        
        # Create directory
        os.makedirs(path, exist_ok=True)
    
    async def batch_insert(self, data: Dict[str, np.ndarray]):
        """Insert compressed data into warm tier"""
        # Simulate compression and storage
        for col_name, values in data.items():
            file_path = os.path.join(self.path, f"{col_name}.mmap")
            
            # Compress data
            compressed = zlib.compress(pickle.dumps(values), level=6)
            self.compression_ratio = len(compressed) / values.nbytes
            
            # Write to file
            with open(file_path, 'ab') as f:
                f.write(compressed)
            
            self.columns[col_name] = {
                'path': file_path,
                'count': len(values),
                'compressed_size': len(compressed)
            }
        
        self.row_count += len(next(iter(data.values())))
        self._update_disk_usage()
    
    async def get_aged_data(self, days: int = 7) -> Dict[str, np.ndarray]:
        """Get data older than specified days"""
        # For demo, return empty
        return {}
    
    def _update_disk_usage(self):
        """Update disk usage estimate"""
        total_bytes = sum(col['compressed_size'] for col in self.columns.values())
        self.disk_usage_gb = total_bytes / (1024**3)


class ColdTierArchiveStore:
    """Compressed archive store for cold data"""
    
    def __init__(self, path: str = "/tmp/cortex_cold"):
        self.path = path
        self.row_count = 0
        self.disk_usage_gb = 0.0
        self.archive_count = 0
        
        os.makedirs(path, exist_ok=True)
    
    async def archive(self, data: Dict[str, np.ndarray]):
        """Archive data with maximum compression"""
        archive_path = os.path.join(self.path, f"archive_{self.archive_count}.zptv")
        
        # Maximum compression
        compressed = zlib.compress(pickle.dumps(data), level=9)
        
        with open(archive_path, 'wb') as f:
            f.write(compressed)
        
        self.archive_count += 1
        self.row_count += len(next(iter(data.values())))
        self.disk_usage_gb += len(compressed) / (1024**3)


# ============================================================================
# FA-CMS Integration
# ============================================================================

class CSSField:
    """Simulated CSS field from FA-CMS"""
    
    def __init__(self, entity_id: str, field_state: complex, coherence: float):
        self.entity_id = entity_id
        self.field_state = field_state
        self.coherence = coherence
        self.timestamp = time.time()
        self.i_am_state = type('IAMState', (), {'vector': np.random.randn(512)})()


class FACMSConnector:
    """Connector for FA-CMS integration"""
    
    def __init__(self, cortex_store):
        self.cortex_store = cortex_store
        self.sync_callbacks = []
        self._setup_columns()
    
    def _setup_columns(self):
        """Setup FA-CMS related columns"""
        schemas = [
            ColumnSchema('entity_id', np.dtype('U64'), compression='dictionary'),
            ColumnSchema('css_field_state', np.complex128, dimensions=256),
            ColumnSchema('i_am_vector', np.float32, dimensions=512),
            ColumnSchema('coherence_score', np.float32),
            ColumnSchema('timestamp', np.float64)
        ]
        
        for schema in schemas:
            self.cortex_store.hot_tier.add_column(schema)
    
    async def sync_css_batch(self, css_batch: List[CSSField]):
        """Sync batch of CSS fields to CORTEX_DataStore"""
        columnar_data = {
            'entity_id': [],
            'css_field_state': [],
            'i_am_vector': [],
            'coherence_score': [],
            'timestamp': []
        }
        
        for css_field in css_batch:
            columnar_data['entity_id'].append(css_field.entity_id)
            
            # Generate CSS field state vector
            css_vector = np.array([css_field.field_state] * 256)
            columnar_data['css_field_state'].append(css_vector)
            
            columnar_data['i_am_vector'].append(css_field.i_am_state.vector)
            columnar_data['coherence_score'].append(css_field.coherence)
            columnar_data['timestamp'].append(css_field.timestamp)
        
        await self.cortex_store.ingest(columnar_data, tier='hot')
        
        # Trigger coherence optimization for low coherence
        low_coherence = [css for css in css_batch if css.coherence < 0.5]
        if low_coherence:
            print(f"⚠️ {len(low_coherence)} entities with low coherence detected")
    
    def compute_css_distance(self, css_state_1: np.ndarray, css_state_2: np.ndarray) -> float:
        """Compute distance between CSS field states"""
        # Quantum-inspired distance metric
        phase_diff = np.angle(css_state_1) - np.angle(css_state_2)
        amplitude_diff = np.abs(css_state_1) - np.abs(css_state_2)
        
        # Combine phase and amplitude distances
        distance = np.sqrt(np.mean(phase_diff**2) + np.mean(amplitude_diff**2))
        return float(distance)


# ============================================================================
# FMO Integration
# ============================================================================

@dataclass
class FMOEntity:
    """Simulated FMO entity"""
    id: str
    type: str
    signature: str
    fractal_dimension: float
    parent_ids: List[str] = field(default_factory=list)
    child_ids: List[str] = field(default_factory=list)
    
    def get_fractal_properties(self):
        """Get fractal properties"""
        return type('FractalProps', (), {
            'dimension': self.fractal_dimension,
            'lacunarity': np.random.random() * 2,
            'hurst_exponent': np.random.random()
        })()


class FMOConnector:
    """FMO integration for entity relationships"""
    
    def __init__(self, cortex_store):
        self.cortex_store = cortex_store
        self._setup_columns()
        self.pattern_cache = {}
    
    def _setup_columns(self):
        """Setup FMO related columns"""
        schemas = [
            ColumnSchema('fmo_signature', np.dtype('U128'), compression='dictionary'),
            ColumnSchema('entity_type', np.dtype('U32'), compression='dictionary'),
            ColumnSchema('fractal_dimension', np.float64),
            ColumnSchema('lacunarity', np.float64),
            ColumnSchema('parent_entities', np.dtype('object')),  # List storage
            ColumnSchema('child_entities', np.dtype('object'))    # List storage
        ]
        
        for schema in schemas:
            self.cortex_store.hot_tier.add_column(schema)
    
    async def sync_fmo_entities(self, entity_batch: List[FMOEntity]):
        """Sync FMO entities to columnar store"""
        columnar_data = {
            'entity_id': [],
            'entity_type': [],
            'fmo_signature': [],
            'fractal_dimension': [],
            'parent_entities': [],
            'child_entities': []
        }
        
        for entity in entity_batch:
            columnar_data['entity_id'].append(entity.id)
            columnar_data['entity_type'].append(entity.type)
            columnar_data['fmo_signature'].append(entity.signature)
            
            fractal_props = entity.get_fractal_properties()
            columnar_data['fractal_dimension'].append(fractal_props.dimension)
            
            columnar_data['parent_entities'].append(entity.parent_ids)
            columnar_data['child_entities'].append(entity.child_ids)
        
        await self.cortex_store.ingest(columnar_data, tier='hot')
    
    def compute_pattern_similarity(self, signature1: str, signature2: str) -> float:
        """Compute similarity between FMO signatures"""
        # Simple hash-based similarity for demo
        hash1 = int(hashlib.md5(signature1.encode()).hexdigest()[:8], 16)
        hash2 = int(hashlib.md5(signature2.encode()).hexdigest()[:8], 16)
        
        # Normalize difference
        max_hash = 0xFFFFFFFF
        similarity = 1.0 - (abs(hash1 - hash2) / max_hash)
        return similarity


# ============================================================================
# Query Engine
# ============================================================================

class ColumnarQueryExecutor:
    """Execute queries on columnar data"""
    
    def __init__(self, datastore):
        self.datastore = datastore
        self.query_cache = {}
    
    async def execute_query(self, query: Dict[str, Any]) -> Dict[str, np.ndarray]:
        """Execute analytical query"""
        # Extract query components
        columns = query.get('select', [])
        table = query.get('from', 'default')
        predicates = query.get('where', [])
        
        # Check cache
        query_hash = hashlib.md5(json.dumps(query, sort_keys=True).encode()).hexdigest()
        if query_hash in self.query_cache:
            print("📊 Query cache hit!")
            return self.query_cache[query_hash]
        
        # Execute across tiers
        results = []
        
        # Hot tier first
        hot_result = await self._query_tier(self.datastore.hot_tier, columns, predicates)
        if hot_result:
            results.append(hot_result)
        
        # Warm tier if needed
        if not results or query.get('include_warm', False):
            warm_result = await self._query_tier(self.datastore.warm_tier, columns, predicates)
            if warm_result:
                results.append(warm_result)
        
        # Combine results
        final_result = self._combine_results(results)
        
        # Cache result
        self.query_cache[query_hash] = final_result
        
        return final_result
    
    async def _query_tier(self, tier, columns: List[str], predicates: List[Dict]) -> Dict[str, np.ndarray]:
        """Query a specific tier"""
        if hasattr(tier, 'query'):
            # Hot tier has direct query method
            return tier.query(columns, self._build_predicate_function(predicates))
        else:
            # Warm/Cold tiers need decompression
            # For demo, return empty
            return {}
    
    def _build_predicate_function(self, predicates: List[Dict]):
        """Build predicate function from query predicates"""
        def predicate_fn(data):
            mask = np.ones(len(data), dtype=bool)
            # Simple predicate evaluation for demo
            return mask
        
        return predicate_fn if predicates else None
    
    def _combine_results(self, results: List[Dict[str, np.ndarray]]) -> Dict[str, np.ndarray]:
        """Combine results from multiple tiers"""
        if not results:
            return {}
        
        if len(results) == 1:
            return results[0]
        
        # Concatenate arrays
        combined = {}
        for key in results[0].keys():
            arrays = [r[key] for r in results if key in r]
            combined[key] = np.concatenate(arrays)
        
        return combined


# ============================================================================
# Main CORTEX_DataStore Implementation
# ============================================================================

class CORTEXDataStore:
    """
    Main CORTEX_DataStore implementation
    Provides columnar storage with FA-CMS/FMO integration
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Initialize storage tiers
        self.hot_tier = HotTierColumnarStore(
            capacity=self.config.get('hot_tier_capacity', 1_000_000)
        )
        self.warm_tier = WarmTierColumnarStore(
            path=self.config.get('warm_tier_path', '/tmp/cortex_warm'),
            max_size_gb=self.config.get('warm_tier_size_gb', 10)
        )
        self.cold_tier = ColdTierArchiveStore(
            path=self.config.get('cold_tier_path', '/tmp/cortex_cold')
        )
        
        # Initialize connectors
        self.fa_cms_connector = FACMSConnector(self)
        self.fmo_connector = FMOConnector(self)
        
        # Query engine
        self.query_engine = ColumnarQueryExecutor(self)
        
        # Background tasks
        self._start_background_tasks()
        
        print("✅ CORTEX_DataStore initialized")
    
    def _start_background_tasks(self):
        """Start background maintenance tasks"""
        async def tiering_task():
            """Background task for data tiering"""
            while True:
                await asyncio.sleep(60)  # Run every minute
                
                # Move aged data from hot to warm
                aged_data = await self.hot_tier.get_aged_data(hours=1)
                if aged_data:
                    print(f"📦 Moving {len(next(iter(aged_data.values())))} rows to warm tier")
                    await self.warm_tier.batch_insert(aged_data)
                    await self.hot_tier.evict(list(range(len(next(iter(aged_data.values()))))))
        
        # Start background task
        asyncio.create_task(tiering_task())
    
    async def ingest(self, data: Dict[str, Union[List, np.ndarray]], tier: str = 'hot'):
        """Ingest columnar data into specified tier"""
        if tier == 'hot':
            await self.hot_tier.batch_insert(data)
        elif tier == 'warm':
            # Convert lists to numpy arrays
            np_data = {k: np.array(v) if isinstance(v, list) else v for k, v in data.items()}
            await self.warm_tier.batch_insert(np_data)
        elif tier == 'cold':
            np_data = {k: np.array(v) if isinstance(v, list) else v for k, v in data.items()}
            await self.cold_tier.archive(np_data)
        else:
            raise ValueError(f"Unknown tier: {tier}")
    
    async def query(self, query_dict: Dict[str, Any]) -> Dict[str, np.ndarray]:
        """Execute query across all tiers"""
        return await self.query_engine.execute_query(query_dict)
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        return {
            'hot_tier': {
                'rows': self.hot_tier.row_count,
                'memory_mb': self.hot_tier.memory_usage_mb,
                'columns': len(self.hot_tier.columns)
            },
            'warm_tier': {
                'rows': self.warm_tier.row_count,
                'disk_gb': self.warm_tier.disk_usage_gb,
                'compression_ratio': self.warm_tier.compression_ratio
            },
            'cold_tier': {
                'rows': self.cold_tier.row_count,
                'disk_gb': self.cold_tier.disk_usage_gb,
                'archives': self.cold_tier.archive_count
            },
            'total': {
                'rows': (self.hot_tier.row_count + 
                        self.warm_tier.row_count + 
                        self.cold_tier.row_count),
                'storage_gb': (self.hot_tier.memory_usage_mb / 1024 +
                             self.warm_tier.disk_usage_gb +
                             self.cold_tier.disk_usage_gb)
            }
        }


# ============================================================================
# Demo and Testing
# ============================================================================

async def demo_cortex_datastore():
    """Demonstrate CORTEX_DataStore functionality"""
    print("=" * 60)
    print("CORTEX_DATASTORE DEMONSTRATION")
    print("=" * 60)
    
    # Initialize DataStore
    datastore = CORTEXDataStore({
        'hot_tier_capacity': 100_000,
        'warm_tier_path': '/tmp/cortex_demo_warm',
        'cold_tier_path': '/tmp/cortex_demo_cold'
    })
    
    # Test 1: FA-CMS Integration
    print("\n📊 Test 1: FA-CMS CSS Field Synchronization")
    
    # Generate sample CSS fields
    css_batch = []
    for i in range(100):
        css_field = CSSField(
            entity_id=f"entity_{i}",
            field_state=complex(np.random.randn(), np.random.randn()),
            coherence=np.random.random()
        )
        css_batch.append(css_field)
    
    # Sync to DataStore
    await datastore.fa_cms_connector.sync_css_batch(css_batch)
    print(f"✅ Synced {len(css_batch)} CSS fields")
    
    # Test 2: FMO Integration
    print("\n📊 Test 2: FMO Entity Synchronization")
    
    # Generate sample FMO entities
    fmo_batch = []
    for i in range(50):
        entity = FMOEntity(
            id=f"fmo_entity_{i}",
            type="agent" if i % 2 == 0 else "service",
            signature=f"sig_{hashlib.md5(str(i).encode()).hexdigest()}",
            fractal_dimension=1.0 + np.random.random() * 0.8,
            parent_ids=[f"fmo_entity_{i-1}"] if i > 0 else [],
            child_ids=[f"fmo_entity_{i+1}"] if i < 49 else []
        )
        fmo_batch.append(entity)
    
    await datastore.fmo_connector.sync_fmo_entities(fmo_batch)
    print(f"✅ Synced {len(fmo_batch)} FMO entities")
    
    # Test 3: Query Execution
    print("\n📊 Test 3: Columnar Query Execution")
    
    # Query 1: Get entities with low coherence
    query1 = {
        'select': ['entity_id', 'coherence_score', 'css_field_state'],
        'from': 'css_fields',
        'where': [{'column': 'coherence_score', 'op': '<', 'value': 0.5}]
    }
    
    start_time = time.time()
    result1 = await datastore.query(query1)
    query_time = (time.time() - start_time) * 1000
    
    print(f"Query 1 - Low coherence entities:")
    print(f"  Results: {len(result1.get('entity_id', []))} entities")
    print(f"  Query time: {query_time:.2f}ms")
    
    # Query 2: Get fractal dimensions
    query2 = {
        'select': ['entity_id', 'fractal_dimension', 'entity_type'],
        'from': 'fmo_entities'
    }
    
    start_time = time.time()
    result2 = await datastore.query(query2)
    query_time = (time.time() - start_time) * 1000
    
    print(f"\nQuery 2 - Fractal dimensions:")
    print(f"  Results: {len(result2.get('entity_id', []))} entities")
    print(f"  Query time: {query_time:.2f}ms")
    if 'fractal_dimension' in result2:
        print(f"  Avg dimension: {np.mean(result2['fractal_dimension']):.3f}")
    
    # Test 4: Storage Statistics
    print("\n📊 Test 4: Storage Statistics")
    stats = await datastore.get_stats()
    
    print(f"\nStorage Tiers:")
    print(f"  Hot Tier:")
    print(f"    - Rows: {stats['hot_tier']['rows']:,}")
    print(f"    - Memory: {stats['hot_tier']['memory_mb']:.2f} MB")
    print(f"    - Columns: {stats['hot_tier']['columns']}")
    
    print(f"  Warm Tier:")
    print(f"    - Rows: {stats['warm_tier']['rows']:,}")
    print(f"    - Disk: {stats['warm_tier']['disk_gb']:.4f} GB")
    print(f"    - Compression: {stats['warm_tier']['compression_ratio']:.2f}x")
    
    print(f"  Total:")
    print(f"    - Rows: {stats['total']['rows']:,}")
    print(f"    - Storage: {stats['total']['storage_gb']:.4f} GB")
    
    # Test 5: CSS Distance Calculation
    print("\n📊 Test 5: CSS Distance Calculations")
    
    if 'css_field_state' in result1 and len(result1['css_field_state']) >= 2:
        css1 = result1['css_field_state'][0]
        css2 = result1['css_field_state'][1]
        
        distance = datastore.fa_cms_connector.compute_css_distance(css1, css2)
        print(f"  CSS Distance between entities: {distance:.4f}")
    
    # Test 6: Batch Performance
    print("\n📊 Test 6: Batch Ingestion Performance")
    
    # Large batch test
    large_batch = {
        'entity_id': [f"perf_test_{i}" for i in range(10000)],
        'coherence_score': np.random.random(10000).astype(np.float32),
        'timestamp': np.array([time.time() + i for i in range(10000)])
    }
    
    start_time = time.time()
    await datastore.ingest(large_batch)
    ingest_time = (time.time() - start_time) * 1000
    
    print(f"  Batch size: 10,000 rows")
    print(f"  Ingest time: {ingest_time:.2f}ms")
    print(f"  Throughput: {10000/(ingest_time/1000):.0f} rows/sec")
    
    print("\n✅ CORTEX_DataStore demonstration complete!")


async def stress_test_datastore():
    """Stress test the DataStore"""
    print("\n" + "=" * 60)
    print("CORTEX_DATASTORE STRESS TEST")
    print("=" * 60)
    
    datastore = CORTEXDataStore()
    
    # Generate large dataset
    print("\n🚀 Generating large dataset...")
    num_entities = 100_000
    
    # CSS fields
    css_data = {
        'entity_id': [f"stress_entity_{i}" for i in range(num_entities)],
        'css_field_state': [complex(np.random.randn(), np.random.randn()) 
                           for _ in range(num_entities)],
        'coherence_score': np.random.random(num_entities).astype(np.float32),
        'timestamp': np.array([time.time() + i for i in range(num_entities)])
    }
    
    # Ingest in batches
    batch_size = 10_000
    total_time = 0
    
    for i in range(0, num_entities, batch_size):
        batch = {k: v[i:i+batch_size] for k, v in css_data.items()}
        
        start = time.time()
        await datastore.ingest(batch)
        batch_time = time.time() - start
        total_time += batch_time
        
        print(f"  Batch {i//batch_size + 1}: {batch_time*1000:.1f}ms")
    
    print(f"\n✅ Total ingestion:")
    print(f"  Rows: {num_entities:,}")
    print(f"  Time: {total_time:.2f}s")
    print(f"  Throughput: {num_entities/total_time:,.0f} rows/sec")
    
    # Query performance
    print("\n📊 Query Performance:")
    
    queries = [
        {
            'name': 'Full scan',
            'select': ['entity_id', 'coherence_score'],
            'from': 'all'
        },
        {
            'name': 'Filtered scan',
            'select': ['entity_id', 'coherence_score'],
            'where': [{'column': 'coherence_score', 'op': '>', 'value': 0.8}]
        }
    ]
    
    for query_def in queries:
        start = time.time()
        result = await datastore.query(query_def)
        query_time = (time.time() - start) * 1000
        
        print(f"\n  {query_def['name']}:")
        print(f"    Results: {len(result.get('entity_id', []))} rows")
        print(f"    Time: {query_time:.1f}ms")
        print(f"    Throughput: {len(result.get('entity_id', []))/(query_time/1000):,.0f} rows/sec")
    
    # Final stats
    stats = await datastore.get_stats()
    print(f"\n📈 Final Statistics:")
    print(f"  Total rows: {stats['total']['rows']:,}")
    print(f"  Total storage: {stats['total']['storage_gb']:.3f} GB")
    print(f"  Compression ratio: {stats['warm_tier']['compression_ratio']:.1f}x")


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    # Run demonstrations
    asyncio.run(demo_cortex_datastore())
    asyncio.run(stress_test_datastore())
    
    print("\n✨ CORTEX_DataStore implementation complete!")
    print("Next steps: Implement CQL parser and agent skill evolution")