# CORTEX_DataStore Design & FA-CMS/FMO Integration
## Milestone CTX.1.3

### Executive Summary

CORTEX_DataStore provides a high-performance, columnar storage layer optimized for AI/ML workloads within Tenxsom AI. It integrates seamlessly with FA-CMS for consciousness data and FMO for entity relationships, while leveraging ZPTV compression and CSS field operations.

### Table of Contents
1. [Storage Architecture](#storage-architecture)
2. [Columnar Data Model](#columnar-data-model)
3. [FA-CMS Integration](#fa-cms-integration)
4. [FMO Integration](#fmo-integration)
5. [Query Optimization](#query-optimization)
6. [Implementation Specifications](#implementation-specifications)

---

## Storage Architecture

### Three-Tier Storage Hierarchy

```
┌─────────────────────────────────────────────────────────────┐
│                    CORTEX_DataStore                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                     HOT TIER                            │ │
│  │  • In-memory columnar arrays                           │ │
│  │  • Active CSS fields & I_AM vectors                    │ │
│  │  • Current ITB rules & active FMO entities             │ │
│  │  • Retention: 1 hour                                   │ │
│  │  • Access: < 1ms                                       │ │
│  └────────────────────────┬───────────────────────────────┘ │
│                           │                                  │
│  ┌────────────────────────▼───────────────────────────────┐ │
│  │                    WARM TIER                            │ │
│  │  • Memory-mapped files with columnar layout            │ │
│  │  • Recent 24hr TCS patterns & FA-CMS cache             │ │
│  │  • ZPTV-compressed fractal signatures                  │ │
│  │  • Retention: 7 days                                   │ │
│  │  • Access: < 10ms                                      │ │
│  └────────────────────────┬───────────────────────────────┘ │
│                           │                                  │
│  ┌────────────────────────▼───────────────────────────────┐ │
│  │                    COLD TIER                            │ │
│  │  • Compressed archive with indexed access              │ │
│  │  • Historical patterns & dormant entities              │ │
│  │  • Full ZPTV compression + columnar encoding           │ │
│  │  • Retention: Indefinite                               │ │
│  │  • Access: < 100ms                                     │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow Architecture

```python
class DataFlowManager:
    """Manages data movement between tiers"""
    
    def __init__(self):
        self.hot_tier = HotTierStore()
        self.warm_tier = WarmTierStore()
        self.cold_tier = ColdTierStore()
        self.tier_policies = TieringPolicies()
    
    async def ingest_from_fa_cms(self, css_snapshot):
        """Ingest CSS field data from FA-CMS"""
        # Priority placement in hot tier
        await self.hot_tier.ingest_css_fields(css_snapshot)
        
        # Schedule background tiering
        await self.schedule_tiering_task(css_snapshot.timestamp)
    
    async def tier_data_by_age(self):
        """Move data between tiers based on age and access patterns"""
        # Hot → Warm (after 1 hour)
        aged_hot_data = await self.hot_tier.get_aged_data(hours=1)
        if aged_hot_data:
            compressed = await self.compress_for_warm_tier(aged_hot_data)
            await self.warm_tier.ingest(compressed)
            await self.hot_tier.evict(aged_hot_data.keys)
        
        # Warm → Cold (after 7 days)
        aged_warm_data = await self.warm_tier.get_aged_data(days=7)
        if aged_warm_data:
            archived = await self.compress_for_cold_tier(aged_warm_data)
            await self.cold_tier.archive(archived)
            await self.warm_tier.evict(aged_warm_data.keys)
```

---

## Columnar Data Model

### Column Definitions

```python
from dataclasses import dataclass
from typing import List, Optional, Union
import numpy as np

@dataclass
class ColumnSchema:
    """Schema definition for a columnar store column"""
    name: str
    dtype: np.dtype
    compression: str = "none"  # none, zptv, dictionary, rle
    nullable: bool = False
    metadata: dict = None

class CORTEXColumnStore:
    """Columnar storage implementation for CORTEX-A"""
    
    # Core entity columns
    ENTITY_COLUMNS = [
        ColumnSchema("entity_id", np.dtype('U64'), compression="dictionary"),
        ColumnSchema("entity_type", np.dtype('U32'), compression="dictionary"),
        ColumnSchema("creation_timestamp", np.int64),
        ColumnSchema("last_modified", np.int64),
        ColumnSchema("fmo_signature", np.dtype('U128'), compression="dictionary"),
    ]
    
    # Vector columns for AI operations
    VECTOR_COLUMNS = [
        ColumnSchema("i_am_vector", np.float32, metadata={"dimensions": 512}),
        ColumnSchema("css_field_state", np.complex128, metadata={"dimensions": 256}),
        ColumnSchema("embedding_vector", np.float16, compression="zptv", metadata={"dimensions": 768}),
    ]
    
    # Fractal analysis columns
    FRACTAL_COLUMNS = [
        ColumnSchema("fractal_dimension", np.float64),
        ColumnSchema("lacunarity", np.float64),
        ColumnSchema("hurst_exponent", np.float64),
        ColumnSchema("multifractal_spectrum", np.float32, metadata={"dimensions": 20}),
    ]
    
    # Performance metrics columns
    METRIC_COLUMNS = [
        ColumnSchema("coherence_score", np.float32),
        ColumnSchema("refactorability_score", np.float32),
        ColumnSchema("css_distance_to_optimal", np.float32),
        ColumnSchema("tcs_archetype", np.dtype('U16'), compression="dictionary"),
    ]
    
    # Relationship columns (for FMO integration)
    RELATIONSHIP_COLUMNS = [
        ColumnSchema("parent_entities", np.dtype('U64'), metadata={"is_array": True}),
        ColumnSchema("child_entities", np.dtype('U64'), metadata={"is_array": True}),
        ColumnSchema("relationship_types", np.dtype('U32'), compression="dictionary"),
        ColumnSchema("relationship_strengths", np.float32),
    ]
```

### Columnar Storage Implementation

```python
class ColumnarArray:
    """Memory-efficient columnar array with compression support"""
    
    def __init__(self, schema: ColumnSchema, initial_capacity: int = 1000):
        self.schema = schema
        self.capacity = initial_capacity
        self.size = 0
        
        # Allocate backing storage
        if schema.dtype == np.dtype('object') or 'U' in str(schema.dtype):
            # String columns use dictionary encoding
            self.dictionary = {}
            self.indices = np.empty(initial_capacity, dtype=np.uint32)
        else:
            self.data = np.empty(initial_capacity, dtype=schema.dtype)
        
        # Compression buffer
        self.compressed_chunks = []
        
    def append(self, value):
        """Append value to column"""
        if self.size >= self.capacity:
            self._grow()
        
        if hasattr(self, 'dictionary'):
            # Dictionary encoding for strings
            if value not in self.dictionary:
                self.dictionary[value] = len(self.dictionary)
            self.indices[self.size] = self.dictionary[value]
        else:
            self.data[self.size] = value
        
        self.size += 1
    
    def get_slice(self, start: int, end: int) -> np.ndarray:
        """Get slice of column data"""
        if hasattr(self, 'dictionary'):
            # Decode dictionary values
            inv_dict = {v: k for k, v in self.dictionary.items()}
            indices_slice = self.indices[start:end]
            return np.array([inv_dict[idx] for idx in indices_slice])
        else:
            return self.data[start:end]
    
    def compress_chunk(self, chunk_size: int = 10000):
        """Compress completed chunks using ZPTV"""
        if self.schema.compression == "zptv" and self.size >= chunk_size:
            chunk_data = self.data[:chunk_size]
            compressed = ZPTVCompressor.compress(chunk_data)
            self.compressed_chunks.append(compressed)
            
            # Shift remaining data
            self.data[:self.size-chunk_size] = self.data[chunk_size:self.size]
            self.size -= chunk_size
```

---

## FA-CMS Integration

### CSS Field Synchronization

```python
class FACMSConnector:
    """Connector for FA-CMS integration with CORTEX_DataStore"""
    
    def __init__(self, fa_cms_instance, cortex_store):
        self.fa_cms = fa_cms_instance
        self.cortex_store = cortex_store
        self.sync_interval = 100  # milliseconds
        self._setup_sync_handlers()
    
    def _setup_sync_handlers(self):
        """Setup real-time sync handlers"""
        # Subscribe to CSS field updates
        self.fa_cms.on_css_update(self.handle_css_update)
        
        # Subscribe to consciousness state changes
        self.fa_cms.on_consciousness_change(self.handle_consciousness_change)
        
        # Subscribe to ZPTV compressions
        self.fa_cms.on_zptv_compression(self.handle_zptv_update)
    
    async def handle_css_update(self, css_event):
        """Handle CSS field update from FA-CMS"""
        # Extract columnar data
        columnar_data = {
            'entity_id': css_event.entity_id,
            'css_field_state': css_event.field_state,
            'coherence_score': css_event.coherence,
            'timestamp': css_event.timestamp
        }
        
        # Update hot tier immediately
        await self.cortex_store.hot_tier.update_css_field(columnar_data)
        
        # Trigger dependent computations
        if css_event.coherence < 0.5:
            await self.trigger_coherence_optimization(css_event.entity_id)
    
    async def extract_css_window(self, time_window, entity_filter=None):
        """Extract CSS data for analysis window"""
        # Query FA-CMS for time window
        css_data = await self.fa_cms.query_css_fields(
            start_time=time_window.start,
            end_time=time_window.end,
            entity_filter=entity_filter
        )
        
        # Convert to columnar format
        columnar_batch = self._convert_to_columnar(css_data)
        
        # Ingest into CORTEX_DataStore
        await self.cortex_store.batch_ingest(columnar_batch)
        
        return columnar_batch
    
    def _convert_to_columnar(self, css_data):
        """Convert FA-CMS CSS data to columnar format"""
        columns = {
            'entity_id': [],
            'css_field_state': [],
            'i_am_vector': [],
            'coherence_score': [],
            'timestamp': []
        }
        
        for css_entry in css_data:
            columns['entity_id'].append(css_entry.entity_id)
            columns['css_field_state'].append(css_entry.field_state)
            columns['i_am_vector'].append(css_entry.i_am_state.vector)
            columns['coherence_score'].append(css_entry.coherence)
            columns['timestamp'].append(css_entry.timestamp)
        
        # Convert to numpy arrays
        return {k: np.array(v) for k, v in columns.items()}
```

### ZPTV Compression Integration

```python
class ZPTVIntegration:
    """ZPTV compression for columnar data"""
    
    @staticmethod
    def compress_css_column(css_array: np.ndarray) -> bytes:
        """Compress CSS field column using ZPTV"""
        # Apply ZPTV's quantum-inspired compression
        # Preserves CSS field properties while achieving high compression
        
        # Step 1: Extract phase and amplitude
        phase = np.angle(css_array)
        amplitude = np.abs(css_array)
        
        # Step 2: Quantize phase (CSS fields have discrete phase states)
        quantized_phase = np.round(phase / (np.pi/8)) * (np.pi/8)
        
        # Step 3: Compress amplitude using ZPTV
        compressed_amplitude = ZPTVCompressor.compress_1d(amplitude)
        
        # Step 4: Encode phase efficiently
        phase_encoded = encode_phase_states(quantized_phase)
        
        return combine_compressed_components(phase_encoded, compressed_amplitude)
```

---

## FMO Integration

### Entity Relationship Mapping

```python
class FMOConnector:
    """FMO integration for entity relationships and patterns"""
    
    def __init__(self, fmo_instance, cortex_store):
        self.fmo = fmo_instance
        self.cortex_store = cortex_store
        self._setup_pattern_indexing()
    
    def _setup_pattern_indexing(self):
        """Setup FMO pattern indexing in columnar store"""
        # Create indexes for common FMO queries
        self.pattern_indexes = {
            'fractal_signature': ColumnarIndex('fractal_signature'),
            'entity_type': ColumnarIndex('entity_type'),
            'relationship_type': ColumnarIndex('relationship_types')
        }
    
    async def sync_fmo_entities(self, entity_batch):
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
            # Extract entity data
            columnar_data['entity_id'].append(entity.id)
            columnar_data['entity_type'].append(entity.type)
            columnar_data['fmo_signature'].append(entity.signature)
            
            # Extract fractal properties
            fractal_props = entity.get_fractal_properties()
            columnar_data['fractal_dimension'].append(fractal_props.dimension)
            
            # Extract relationships
            columnar_data['parent_entities'].append(entity.parent_ids)
            columnar_data['child_entities'].append(entity.child_ids)
        
        # Batch insert into columnar store
        await self.cortex_store.batch_insert('fmo_entities', columnar_data)
    
    async def query_by_pattern(self, fmo_pattern):
        """Query entities matching FMO pattern"""
        # Use columnar indexes for efficient pattern matching
        matching_signatures = self.pattern_indexes['fractal_signature'].find_similar(
            fmo_pattern.signature,
            threshold=0.8
        )
        
        # Retrieve columnar data
        entity_data = await self.cortex_store.get_by_signatures(matching_signatures)
        
        return entity_data
```

### Pattern-Based Sharding

```python
class FMOShardingStrategy:
    """Intelligent sharding based on FMO patterns"""
    
    def __init__(self, num_shards: int = 16):
        self.num_shards = num_shards
        self.shard_profiles = self._initialize_shard_profiles()
    
    def _initialize_shard_profiles(self):
        """Initialize shard profiles based on fractal clustering"""
        profiles = {}
        for i in range(self.num_shards):
            profiles[i] = {
                'fractal_range': (i * 0.1, (i + 1) * 0.1),  # Fractal dimension ranges
                'css_affinity': [],  # CSS fields with affinity to this shard
                'hot_entities': set()  # Frequently accessed entities
            }
        return profiles
    
    def compute_shard(self, entity_data):
        """Compute optimal shard for entity"""
        # Primary sharding by fractal dimension
        fractal_dim = entity_data.get('fractal_dimension', 1.5)
        base_shard = int((fractal_dim - 1.0) * 10) % self.num_shards
        
        # Affinity-based adjustment
        if entity_data.get('css_coupling_strength', 0) > 0.8:
            # Strong CSS coupling - check for affinity shard
            css_signature = entity_data.get('css_field_state')
            affinity_shard = self._find_css_affinity_shard(css_signature)
            if affinity_shard is not None:
                return affinity_shard
        
        # Hot entity optimization
        if entity_data['entity_id'] in self.shard_profiles[base_shard]['hot_entities']:
            return base_shard
        
        # Load balancing
        return self._load_balanced_shard(base_shard)
```

---

## Query Optimization

### CSS-Aware Query Engine

```python
class CSSQueryOptimizer:
    """Query optimizer for CSS field operations"""
    
    def __init__(self, cortex_store):
        self.cortex_store = cortex_store
        self.css_index = CSSFieldIndex()
    
    def optimize_css_distance_query(self, query_ast):
        """Optimize CSS distance calculations"""
        if self._has_css_distance_predicate(query_ast):
            # Use specialized CSS distance index
            return self._rewrite_for_css_index(query_ast)
        return query_ast
    
    def _rewrite_for_css_index(self, query_ast):
        """Rewrite query to use CSS field index"""
        # Extract CSS distance predicate
        css_predicate = self._extract_css_predicate(query_ast)
        
        # Use pre-computed CSS distance matrix if available
        if self.css_index.has_distance_matrix(css_predicate.reference_state):
            query_ast['execution_hints'] = {
                'use_css_distance_matrix': True,
                'matrix_key': css_predicate.reference_state
            }
        
        return query_ast
```

### Columnar Query Execution

```python
class ColumnarQueryExecutor:
    """Execute queries on columnar data"""
    
    def __init__(self, column_store):
        self.column_store = column_store
        self.vector_engine = VectorizedExecutionEngine()
    
    async def execute_analytical_query(self, query_plan):
        """Execute analytical query using columnar operations"""
        # Identify columns needed
        required_columns = self._identify_required_columns(query_plan)
        
        # Load columns (may span multiple tiers)
        column_data = await self._load_columns_parallel(required_columns)
        
        # Apply predicates using vectorized operations
        if query_plan.predicates:
            mask = self._evaluate_predicates_vectorized(
                query_plan.predicates, 
                column_data
            )
            column_data = self._apply_mask(column_data, mask)
        
        # Perform aggregations if needed
        if query_plan.aggregations:
            result = self._compute_aggregations(
                query_plan.aggregations,
                column_data
            )
        else:
            result = column_data
        
        return result
    
    def _evaluate_predicates_vectorized(self, predicates, column_data):
        """Evaluate predicates using SIMD operations"""
        mask = np.ones(len(column_data[list(column_data.keys())[0]]), dtype=bool)
        
        for predicate in predicates:
            if predicate.type == 'css_distance':
                # Special handling for CSS distance
                distances = self._compute_css_distances_vectorized(
                    column_data['css_field_state'],
                    predicate.reference_state
                )
                predicate_mask = distances < predicate.threshold
            else:
                # Standard comparison
                column = column_data[predicate.column]
                predicate_mask = self._evaluate_comparison(
                    column, predicate.operator, predicate.value
                )
            
            mask &= predicate_mask
        
        return mask
```

---

## Implementation Specifications

### Core CORTEX_DataStore Class

```python
class CORTEXDataStore:
    """
    Main CORTEX_DataStore implementation
    Provides columnar storage with FA-CMS/FMO integration
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Initialize storage tiers
        self.hot_tier = HotTierColumnarStore(
            capacity=config.get('hot_tier_capacity', 1_000_000)
        )
        self.warm_tier = WarmTierColumnarStore(
            path=config.get('warm_tier_path', '/var/cortex/warm'),
            max_size_gb=config.get('warm_tier_size_gb', 100)
        )
        self.cold_tier = ColdTierArchiveStore(
            path=config.get('cold_tier_path', '/var/cortex/cold')
        )
        
        # Initialize connectors
        self.fa_cms_connector = None
        self.fmo_connector = None
        
        # Query engine
        self.query_engine = ColumnarQueryExecutor(self)
        
        # Background tasks
        self.tiering_manager = DataFlowManager()
        
    def connect_fa_cms(self, fa_cms_instance):
        """Connect to FA-CMS for CSS field synchronization"""
        self.fa_cms_connector = FACMSConnector(fa_cms_instance, self)
        print("✅ Connected to FA-CMS")
    
    def connect_fmo(self, fmo_instance):
        """Connect to FMO for entity relationship mapping"""
        self.fmo_connector = FMOConnector(fmo_instance, self)
        print("✅ Connected to FMO")
    
    async def ingest(self, data: Dict[str, np.ndarray], tier: str = 'hot'):
        """Ingest columnar data into specified tier"""
        if tier == 'hot':
            await self.hot_tier.batch_insert(data)
        elif tier == 'warm':
            await self.warm_tier.batch_insert(data)
        elif tier == 'cold':
            await self.cold_tier.batch_insert(data)
        else:
            raise ValueError(f"Unknown tier: {tier}")
    
    async def query(self, cql: str) -> Dict[str, Any]:
        """Execute CQL query across all tiers"""
        # Parse query
        query_plan = CQLParser().parse(cql)
        
        # Optimize for columnar execution
        query_plan = self.optimize_query_plan(query_plan)
        
        # Execute
        result = await self.query_engine.execute_analytical_query(query_plan)
        
        return result
    
    def optimize_query_plan(self, query_plan):
        """Optimize query plan for columnar execution"""
        # CSS-specific optimizations
        if self.fa_cms_connector:
            query_plan = CSSQueryOptimizer(self).optimize_css_distance_query(query_plan)
        
        # FMO pattern optimizations
        if self.fmo_connector:
            query_plan = FMOPatternOptimizer(self).optimize_pattern_matching(query_plan)
        
        # Tier routing optimization
        query_plan = self.tiering_manager.optimize_tier_access(query_plan)
        
        return query_plan
    
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
            }
        }
```

### API Integration Points

```python
# Integration with CORTEX Planner
class CORTEXPlannerDataStoreIntegration:
    """Integration between CORTEX Planner and DataStore"""
    
    def __init__(self, planner, datastore):
        self.planner = planner
        self.datastore = datastore
        self._register_data_source()
    
    def _register_data_source(self):
        """Register DataStore as data source for planner"""
        self.planner.register_data_source(
            name='cortex_datastore',
            query_handler=self.datastore.query,
            capabilities=['columnar', 'css_native', 'fmo_aware']
        )
    
    async def execute_analytical_task(self, task: CortexTask):
        """Execute analytical task using DataStore"""
        # Extract data requirements
        data_query = self._build_data_query(task)
        
        # Query DataStore
        data = await self.datastore.query(data_query)
        
        # Pass to compute agent
        return await task.assigned_agent.process_data(data)
```

---

## Performance Characteristics

### Expected Performance Metrics

| Operation | Hot Tier | Warm Tier | Cold Tier |
|-----------|----------|-----------|-----------|
| Single Row Lookup | < 0.1ms | < 1ms | < 10ms |
| Range Scan (1M rows) | < 10ms | < 50ms | < 500ms |
| CSS Distance Calc | < 1ms | < 5ms | < 20ms |
| Columnar Aggregation | < 5ms | < 20ms | < 100ms |
| Compression Ratio | 1:1 | 5:1 | 20:1 |

### Scalability Projections

```python
def project_storage_requirements(entities: int, 
                               vectors_per_entity: int,
                               retention_days: int) -> Dict[str, float]:
    """Project storage requirements for CORTEX_DataStore"""
    
    # Base sizes
    entity_size = 1024  # 1KB base metadata
    vector_size = 512 * 4  # 512 float32 values
    css_field_size = 256 * 16  # 256 complex128 values
    
    # Per entity storage
    per_entity_storage = (
        entity_size + 
        vectors_per_entity * vector_size +
        css_field_size
    )
    
    # Tier distribution (based on access patterns)
    hot_percentage = 0.05  # 5% in hot tier
    warm_percentage = 0.20  # 20% in warm tier
    cold_percentage = 0.75  # 75% in cold tier
    
    # Compression factors
    warm_compression = 5.0
    cold_compression = 20.0
    
    # Calculate tier sizes
    hot_size_gb = (entities * hot_percentage * per_entity_storage) / (1024**3)
    warm_size_gb = (entities * warm_percentage * per_entity_storage) / (1024**3) / warm_compression
    cold_size_gb = (entities * cold_percentage * per_entity_storage) / (1024**3) / cold_compression
    
    return {
        'hot_tier_gb': hot_size_gb,
        'warm_tier_gb': warm_size_gb,
        'cold_tier_gb': cold_size_gb,
        'total_gb': hot_size_gb + warm_size_gb + cold_size_gb,
        'memory_required_gb': hot_size_gb + (warm_size_gb * 0.1)  # 10% warm tier in memory
    }
```

---

## Conclusion

CORTEX_DataStore provides a sophisticated columnar storage layer that:

1. **Integrates seamlessly** with FA-CMS for consciousness data and FMO for entity relationships
2. **Optimizes for AI workloads** with native vector and CSS field operations
3. **Scales efficiently** through intelligent tiering and compression
4. **Enables fast analytics** through columnar operations and specialized indexes

The three-tier architecture ensures that hot data remains immediately accessible while historical data is efficiently compressed, providing the best balance of performance and storage efficiency for Tenxsom AI's analytical needs.

---

*Design Document Version: 1.0*  
*Milestone: CTX.1.3*  
*Status: Ready for Implementation*