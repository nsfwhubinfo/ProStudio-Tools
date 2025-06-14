#!/usr/bin/env python3
"""
ProStudio API Test Client
=========================

Simple client to test the ProStudio API.
"""

import requests
import json
import time
import sys
from typing import Dict, List

# API configuration
API_URL = "http://localhost:8000"


def test_health():
    """Test health endpoint"""
    print("🏥 Testing health endpoint...")
    try:
        response = requests.get(f"{API_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Server is healthy!")
            print(f"   Version: {data.get('version')}")
            print(f"   Framework: {data.get('framework')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Is it running?")
        print(f"   Start with: python api_server.py")
        return False


def test_generate_single():
    """Test single content generation"""
    print("\n📝 Testing single content generation...")
    
    payload = {
        "concept": "5 AI tools every creator needs",
        "platform": "TIKTOK",
        "content_type": "VIDEO_SHORT"
    }
    
    try:
        start = time.time()
        response = requests.post(f"{API_URL}/generate", json=payload)
        request_time = (time.time() - start) * 1000
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Content generated successfully!")
            print(f"   ID: {data.get('id')}")
            print(f"   Generation time: {data.get('generation_time_ms', 0):.1f}ms")
            print(f"   Request time: {request_time:.1f}ms")
            print(f"   Predicted engagement: {data.get('predicted_engagement', 0):.1f}%")
            print(f"   Viral coefficient: {data.get('viral_coefficient', 0):.2f}")
            
            if data.get('script'):
                print(f"\n   Script preview:")
                script_lines = data['script'].split('\n')
                for line in script_lines[:3]:
                    if line.strip():
                        print(f"   > {line}")
                if len(script_lines) > 3:
                    print(f"   > ... ({len(script_lines)-3} more lines)")
            
            if data.get('hashtags'):
                print(f"\n   Hashtags: {', '.join(data['hashtags'][:5])}")
            
            return True
        else:
            print(f"❌ Generation failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False


def test_batch_generation():
    """Test batch content generation"""
    print("\n📦 Testing batch generation...")
    
    payload = {
        "concepts": [
            "How to grow on TikTok in 2024",
            "Instagram Reels vs TikTok",
            "YouTube Shorts monetization tips"
        ],
        "platforms": ["TIKTOK", "INSTAGRAM"],
        "count": 6
    }
    
    try:
        start = time.time()
        response = requests.post(f"{API_URL}/batch", json=payload)
        request_time = (time.time() - start) * 1000
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            
            print(f"✅ Batch generation complete!")
            print(f"   Generated: {len(results)} items")
            print(f"   Total time: {data.get('total_time_ms', 0):.1f}ms")
            print(f"   Average time: {data.get('avg_time_ms', 0):.1f}ms per item")
            print(f"   Throughput: {len(results)*1000/request_time:.1f} items/sec")
            
            # Show sample results
            print(f"\n   Sample results:")
            for i, result in enumerate(results[:3]):
                print(f"   {i+1}. {result['concept']} ({result['platform']})")
                print(f"      Engagement: {result['engagement']:.1f}%")
            
            if len(results) > 3:
                print(f"   ... and {len(results)-3} more")
            
            return True
        else:
            print(f"❌ Batch generation failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False


def test_performance():
    """Test API performance"""
    print("\n⚡ Testing API performance...")
    
    # Single request latency
    latencies = []
    for i in range(10):
        start = time.time()
        response = requests.post(f"{API_URL}/generate", json={
            "concept": f"Test concept {i}",
            "platform": "TIKTOK"
        })
        latency = (time.time() - start) * 1000
        if response.status_code == 200:
            latencies.append(latency)
    
    if latencies:
        avg_latency = sum(latencies) / len(latencies)
        min_latency = min(latencies)
        max_latency = max(latencies)
        
        print(f"✅ Performance test complete!")
        print(f"   Requests: {len(latencies)}")
        print(f"   Avg latency: {avg_latency:.1f}ms")
        print(f"   Min latency: {min_latency:.1f}ms")
        print(f"   Max latency: {max_latency:.1f}ms")
        
        # Throughput test
        print(f"\n   Running throughput test...")
        start = time.time()
        successful = 0
        
        for i in range(50):
            response = requests.post(f"{API_URL}/generate", json={
                "concept": f"Throughput test {i}",
                "platform": "INSTAGRAM"
            })
            if response.status_code == 200:
                successful += 1
        
        duration = time.time() - start
        throughput = successful / duration
        
        print(f"   Throughput: {throughput:.1f} req/sec")
        print(f"   Success rate: {successful/50*100:.0f}%")
        
        return True
    else:
        print("❌ Performance test failed - no successful requests")
        return False


def test_stats():
    """Test stats endpoint"""
    print("\n📊 Testing stats endpoint...")
    
    try:
        response = requests.get(f"{API_URL}/stats")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Stats retrieved!")
            
            # Engine config
            if 'engine_config' in data:
                print(f"\n   Engine configuration:")
                for key, value in data['engine_config'].items():
                    print(f"   - {key}: {value}")
            
            # Cache stats
            if 'cache_stats' in data and data['cache_stats']:
                stats = data['cache_stats']
                print(f"\n   Cache statistics:")
                print(f"   - Hit rate: {stats.get('hit_rate', 0)*100:.1f}%")
                print(f"   - Items cached: {stats.get('items_cached', 0)}")
                
            return True
        else:
            print(f"❌ Stats request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Stats request failed: {e}")
        return False


def run_all_tests():
    """Run all API tests"""
    print("🚀 ProStudio API Test Suite")
    print("=" * 50)
    
    # Check if server is running
    if not test_health():
        print("\n⚠️  Please start the API server first:")
        print("   python api_server.py")
        return
    
    # Run tests
    tests = [
        test_generate_single,
        test_batch_generation,
        test_performance,
        test_stats
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        time.sleep(0.5)  # Small delay between tests
    
    # Summary
    print("\n" + "=" * 50)
    print(f"✅ Tests passed: {passed}/{len(tests)}")
    
    if passed == len(tests):
        print("\n🎉 All tests passed! The API is working correctly.")
    else:
        print(f"\n⚠️  Some tests failed. Check the server logs.")


def interactive_mode():
    """Interactive API testing mode"""
    print("\n🎮 Interactive Mode")
    print("=" * 50)
    
    while True:
        print("\nEnter a concept (or 'quit' to exit):")
        concept = input("> ").strip()
        
        if concept.lower() in ['quit', 'exit', 'q']:
            break
        
        if not concept:
            continue
        
        print("\nSelect platform:")
        print("1. TikTok")
        print("2. Instagram")
        print("3. YouTube")
        
        platform_choice = input("> ").strip()
        platforms = {
            '1': 'TIKTOK',
            '2': 'INSTAGRAM', 
            '3': 'YOUTUBE'
        }
        platform = platforms.get(platform_choice, 'TIKTOK')
        
        print(f"\nGenerating content for '{concept}' on {platform}...")
        
        try:
            response = requests.post(f"{API_URL}/generate", json={
                "concept": concept,
                "platform": platform,
                "content_type": "VIDEO_SHORT"
            })
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n✅ Generated in {data['generation_time_ms']:.1f}ms")
                print(f"Predicted engagement: {data['predicted_engagement']:.1f}%")
                
                if data.get('script'):
                    print(f"\nScript:\n{data['script']}")
                
                if data.get('hashtags'):
                    print(f"\nHashtags: {' '.join(data['hashtags'])}")
            else:
                print(f"❌ Generation failed: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")


def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == 'interactive':
        interactive_mode()
    else:
        run_all_tests()


if __name__ == "__main__":
    main()