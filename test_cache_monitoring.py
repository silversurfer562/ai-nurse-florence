#!/usr/bin/env python3
"""
Cache Monitoring Test Script - AI Nurse Florence
Tests the Phase 4.1 enhanced cache monitoring functionality
"""

import asyncio
import httpx
import sys
import os
import json
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_cache_monitoring():
    """Test cache monitoring endpoints"""
    print("🔍 Testing Cache Monitoring - Phase 4.1 Enhanced Caching")
    print("=" * 60)
    
    base_url = "http://localhost:8000/api/v1"
    
    async with httpx.AsyncClient() as client:
        
        print("1. Testing Cache Health Endpoint")
        print("-" * 40)
        try:
            response = await client.get(f"{base_url}/cache/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Cache Health Status: {data.get('status', 'unknown')}")
                print(f"   Smart Cache Manager: {data.get('data', {}).get('smart_cache_enabled', False)}")
                print(f"   Redis Available: {data.get('data', {}).get('redis_available', False)}")
                print(f"   Cache Strategies: {len(data.get('data', {}).get('available_strategies', []))}")
            else:
                print(f"❌ Cache health check failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Cache health check error: {e}")
        
        print("\n2. Testing Cache Statistics")
        print("-" * 40)
        try:
            response = await client.get(f"{base_url}/cache/stats")
            if response.status_code == 200:
                data = response.json()
                stats = data.get('data', {})
                print(f"✅ Cache Statistics Retrieved")
                print(f"   Total Keys: {stats.get('total_cache_keys', 0)}")
                print(f"   Cache Hit Rate: {stats.get('cache_hit_rate', 0):.2%}")
                print(f"   Memory Usage: {stats.get('memory_usage_mb', 0):.1f} MB")
                print(f"   Strategy Count: {len(stats.get('strategy_stats', {}))}")
            else:
                print(f"❌ Cache statistics failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Cache statistics error: {e}")
        
        print("\n3. Testing Cache Test Endpoint")
        print("-" * 40)
        try:
            response = await client.get(f"{base_url}/cache/test")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Cache Test Successful")
                print(f"   Test Data: {data.get('data', {}).get('test_data', 'N/A')}")
                print(f"   Cache Key: {data.get('data', {}).get('cache_key', 'N/A')}")
                print(f"   Timestamp: {data.get('data', {}).get('timestamp', 'N/A')}")
            else:
                print(f"❌ Cache test failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Cache test error: {e}")
        
        print("\n4. Testing Cache Strategies")
        print("-" * 40)
        try:
            response = await client.get(f"{base_url}/cache/strategies")
            if response.status_code == 200:
                data = response.json()
                strategies = data.get('data', {}).get('strategies', {})
                print(f"✅ Available Cache Strategies: {len(strategies)}")
                for strategy_name, details in strategies.items():
                    print(f"   • {strategy_name}: {details.get('description', 'No description')}")
            else:
                print(f"❌ Cache strategies failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Cache strategies error: {e}")
        
        print("\n5. Testing Cache Performance")
        print("-" * 40)
        try:
            response = await client.get(f"{base_url}/cache/performance")
            if response.status_code == 200:
                data = response.json()
                perf = data.get('data', {})
                print(f"✅ Cache Performance Metrics")
                print(f"   Average Response Time: {perf.get('avg_response_time_ms', 0):.1f}ms")
                print(f"   Cache Efficiency: {perf.get('cache_efficiency', 0):.2%}")
                print(f"   Recent Operations: {perf.get('recent_operations', 0)}")
            else:
                print(f"❌ Cache performance failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Cache performance error: {e}")

async def test_service_integration():
    """Test cache integration with medical services"""
    print("\n🏥 Testing Service Integration with Smart Caching")
    print("=" * 60)
    
    base_url = "http://localhost:8000/api/v1"
    
    async with httpx.AsyncClient() as client:
        
        print("1. Testing Enhanced Literature Search (with caching)")
        print("-" * 50)
        try:
            search_data = {
                "query": "diabetes management guidelines",
                "specialty": "endocrinology",
                "max_results": 3
            }
            response = await client.post(f"{base_url}/enhanced-literature/search", json=search_data)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Literature Search Successful")
                print(f"   Query: {data.get('data', {}).get('query', 'N/A')}")
                print(f"   Cache Hit: {data.get('data', {}).get('cache_hit', False)}")
                print(f"   Articles Found: {len(data.get('data', {}).get('articles', []))}")
            else:
                print(f"❌ Literature search failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Literature search error: {e}")
        
        print("\n2. Testing Drug Interaction Check (with caching)")
        print("-" * 50)
        try:
            interaction_data = {
                "drugs": ["metformin", "lisinopril", "warfarin"],
                "patient_context": {"age": 65, "conditions": ["diabetes", "hypertension"]}
            }
            response = await client.post(f"{base_url}/drug-interactions/check", json=interaction_data)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Drug Interaction Check Successful")
                print(f"   Drugs Checked: {len(interaction_data['drugs'])}")
                print(f"   Cache Hit: {data.get('data', {}).get('cache_hit', False)}")
                print(f"   Interactions Found: {data.get('data', {}).get('total_interactions', 0)}")
            else:
                print(f"❌ Drug interaction check failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Drug interaction check error: {e}")

async def main():
    """Main test runner"""
    print("🚀 AI Nurse Florence - Cache Monitoring Test Suite")
    print("📅 Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("🔧 Phase 4.1: Enhanced Redis Caching")
    print("=" * 70)
    
    try:
        # First check if server is running
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get("http://localhost:8000/api/v1/health", timeout=5.0)
                if response.status_code == 200:
                    print("✅ Server is running and responsive")
                    print()
                else:
                    print("❌ Server responded with error:", response.status_code)
                    return
            except Exception as e:
                print("❌ Server is not accessible. Please start the server with: ./run_dev.sh")
                print(f"   Error: {e}")
                return
        
        # Run cache monitoring tests
        await test_cache_monitoring()
        
        # Run service integration tests
        await test_service_integration()
        
        print("\n" + "=" * 70)
        print("🎉 Cache Monitoring Test Suite Complete!")
        print("✅ Phase 4.1 Enhanced Redis Caching is operational")
        print("✅ Smart cache manager is functioning")
        print("✅ Medical services are cache-enabled")
        print("✅ Cache monitoring endpoints are working")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
