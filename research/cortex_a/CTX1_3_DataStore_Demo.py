#!/usr/bin/env python3
"""
Simplified CORTEX_DataStore Demo
================================
Shows key functionality without complex object storage
"""

import asyncio
import numpy as np
import time
import json
from CTX1_3_DataStore_Implementation import (
    CORTEXDataStore, CSSField, FMOEntity, ColumnSchema
)


async def demo_simplified():
    """Simplified demonstration of CORTEX_DataStore"""
    print("=" * 60)
    print("CORTEX_DATASTORE DEMONSTRATION (SIMPLIFIED)")
    print("=" * 60)
    
    # Initialize DataStore
    datastore = CORTEXDataStore({
        'hot_tier_capacity': 100_000,
    })
    
    # Test 1: Basic Columnar Storage
    print("\n📊 Test 1: Basic Columnar Storage")
    
    # Add some basic columns
    basic_data = {
        'entity_id': [f"entity_{i}" for i in range(1000)],
        'coherence_score': np.random.random(1000).astype(np.float32),
        'fractal_dimension': 1.0 + np.random.random(1000) * 0.8,
        'timestamp': np.array([time.time() + i for i in range(1000)])
    }
    
    start = time.time()
    await datastore.ingest(basic_data)
    ingest_time = (time.time() - start) * 1000
    
    print(f"✅ Ingested 1000 rows in {ingest_time:.1f}ms")
    print(f"   Throughput: {1000/(ingest_time/1000):.0f} rows/sec")
    
    # Test 2: CSS Field Integration
    print("\n📊 Test 2: CSS Field Storage")
    
    css_batch = []
    for i in range(500):
        css_field = CSSField(
            entity_id=f"css_entity_{i}",
            field_state=complex(np.random.randn(), np.random.randn()),
            coherence=np.random.random()
        )
        css_batch.append(css_field)
    
    low_coherence = sum(1 for css in css_batch if css.coherence < 0.5)
    
    start = time.time()
    await datastore.fa_cms_connector.sync_css_batch(css_batch)
    sync_time = (time.time() - start) * 1000
    
    print(f"✅ Synced {len(css_batch)} CSS fields in {sync_time:.1f}ms")
    print(f"   Low coherence entities: {low_coherence}")
    
    # Test 3: Query Performance
    print("\n📊 Test 3: Query Performance")
    
    queries = [
        {
            'name': 'All entities',
            'select': ['entity_id', 'coherence_score'],
            'from': 'all'
        },
        {
            'name': 'High coherence',
            'select': ['entity_id', 'coherence_score'],
            'where': [{'column': 'coherence_score', 'op': '>', 'value': 0.8}]
        },
        {
            'name': 'Fractal analysis',
            'select': ['entity_id', 'fractal_dimension'],
            'from': 'entities'
        }
    ]
    
    for query in queries:
        start = time.time()
        result = await datastore.query(query)
        query_time = (time.time() - start) * 1000
        
        result_count = len(result.get('entity_id', []))
        print(f"\nQuery: {query['name']}")
        print(f"  Results: {result_count} rows")
        print(f"  Time: {query_time:.2f}ms")
        if result_count > 0:
            print(f"  Latency: {query_time/result_count:.3f}ms per row")
    
    # Test 4: Storage Tiers
    print("\n📊 Test 4: Storage Tier Statistics")
    
    stats = await datastore.get_stats()
    
    print(f"\nHot Tier:")
    print(f"  Rows: {stats['hot_tier']['rows']:,}")
    print(f"  Memory: {stats['hot_tier']['memory_mb']:.2f} MB")
    print(f"  Columns: {stats['hot_tier']['columns']}")
    
    print(f"\nTotal Storage:")
    print(f"  Rows: {stats['total']['rows']:,}")
    print(f"  Size: {stats['total']['storage_gb']:.4f} GB")
    
    # Test 5: Batch Performance
    print("\n📊 Test 5: Large Batch Performance")
    
    batch_sizes = [1000, 5000, 10000, 50000]
    
    for batch_size in batch_sizes:
        large_batch = {
            'entity_id': [f"batch_{i}" for i in range(batch_size)],
            'coherence_score': np.random.random(batch_size).astype(np.float32),
            'timestamp': np.array([time.time() + i for i in range(batch_size)])
        }
        
        start = time.time()
        await datastore.ingest(large_batch)
        batch_time = (time.time() - start) * 1000
        
        print(f"\nBatch size: {batch_size:,}")
        print(f"  Time: {batch_time:.1f}ms")
        print(f"  Throughput: {batch_size/(batch_time/1000):,.0f} rows/sec")
        print(f"  Per-row: {batch_time/batch_size:.3f}ms")
    
    # Test 6: Compression
    print("\n📊 Test 6: Compression Analysis")
    
    # Get a column and test compression
    hot_tier = datastore.hot_tier
    if 'coherence_score' in hot_tier.columns:
        column = hot_tier.columns['coherence_score']
        original_size = column.size * 4  # float32 = 4 bytes
        compressed = column.compress()
        compressed_size = len(compressed)
        ratio = original_size / compressed_size
        
        print(f"\nCoherence score column:")
        print(f"  Original size: {original_size/1024:.1f} KB")
        print(f"  Compressed size: {compressed_size/1024:.1f} KB")
        print(f"  Compression ratio: {ratio:.1f}x")
    
    # Test 7: CSS Distance Calculation
    print("\n📊 Test 7: CSS Field Operations")
    
    # Get some CSS fields
    css_query = {
        'select': ['entity_id', 'css_field_state'],
        'from': 'css_fields'
    }
    
    css_result = await datastore.query(css_query)
    if 'css_field_state' in css_result and len(css_result['css_field_state']) >= 2:
        css1 = css_result['css_field_state'][0]
        css2 = css_result['css_field_state'][1]
        
        # Compute distance
        distance = datastore.fa_cms_connector.compute_css_distance(css1, css2)
        print(f"\nCSS Distance calculation:")
        print(f"  Distance between first two entities: {distance:.4f}")
        
        # Compute average coherence
        coherence_values = []
        for i in range(min(10, len(css_result['css_field_state']))):
            css_state = css_result['css_field_state'][i]
            coherence = np.abs(np.mean(css_state))
            coherence_values.append(coherence)
        
        print(f"  Average coherence (10 samples): {np.mean(coherence_values):.4f}")
    
    # Final statistics
    print("\n📈 Final Performance Summary")
    final_stats = await datastore.get_stats()
    
    total_rows = final_stats['total']['rows']
    total_storage = final_stats['total']['storage_gb'] * 1024  # Convert to MB
    
    print(f"\nTotal rows stored: {total_rows:,}")
    print(f"Total storage used: {total_storage:.2f} MB")
    print(f"Average storage per row: {total_storage*1024/total_rows:.2f} KB")
    print(f"Memory efficiency: {total_rows/(total_storage):.0f} rows/MB")
    
    print("\n✅ CORTEX_DataStore demonstration complete!")
    
    return datastore


async def performance_analysis():
    """Analyze performance characteristics"""
    print("\n" + "=" * 60)
    print("CORTEX_DATASTORE PERFORMANCE ANALYSIS")
    print("=" * 60)
    
    datastore = CORTEXDataStore()
    
    # Test different data types
    print("\n📊 Data Type Performance:")
    
    test_cases = [
        {
            'name': 'Integers',
            'data': {'int_col': np.random.randint(0, 1000, 10000)}
        },
        {
            'name': 'Floats',
            'data': {'float_col': np.random.random(10000).astype(np.float32)}
        },
        {
            'name': 'Complex',
            'data': {'complex_col': np.random.randn(10000) + 1j*np.random.randn(10000)}
        },
        {
            'name': 'Strings',
            'data': {'string_col': [f"string_{i%100}" for i in range(10000)]}
        }
    ]
    
    for test in test_cases:
        start = time.time()
        await datastore.ingest(test['data'])
        ingest_time = (time.time() - start) * 1000
        
        print(f"\n{test['name']}:")
        print(f"  Ingest time: {ingest_time:.1f}ms")
        print(f"  Rate: {10000/(ingest_time/1000):,.0f} items/sec")
    
    # Query performance by selectivity
    print("\n📊 Query Selectivity Performance:")
    
    # Add test data with known distribution
    test_data = {
        'id': list(range(100000)),
        'value': np.random.exponential(1.0, 100000),  # Skewed distribution
        'category': [f"cat_{i%10}" for i in range(100000)]
    }
    
    await datastore.ingest(test_data)
    
    selectivities = [0.01, 0.1, 0.5, 0.9, 1.0]
    
    for selectivity in selectivities:
        threshold = np.percentile(test_data['value'], (1-selectivity)*100)
        
        query = {
            'select': ['id', 'value'],
            'where': [{'column': 'value', 'op': '>', 'value': threshold}]
        }
        
        start = time.time()
        result = await datastore.query(query)
        query_time = (time.time() - start) * 1000
        
        result_count = len(result.get('id', []))
        print(f"\nSelectivity {selectivity*100:.0f}%:")
        print(f"  Results: {result_count:,} rows")
        print(f"  Time: {query_time:.1f}ms")
        print(f"  Throughput: {result_count/(query_time/1000):,.0f} rows/sec")


if __name__ == "__main__":
    # Run demonstrations
    asyncio.run(demo_simplified())
    asyncio.run(performance_analysis())
    
    print("\n✨ All tests complete!")