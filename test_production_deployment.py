"""
Test Production Deployment - AI Nurse Florence

Tests Railway deployment to verify:
1. Application is running
2. Environment variables are loaded
3. AI provider configuration is correct
4. Health endpoints respond properly
"""

import asyncio
import sys
from typing import Any, Dict

try:
    import httpx
except ImportError:
    print("❌ httpx not installed. Run: pip install httpx")
    sys.exit(1)


# CONFIGURATION
# Update this with your actual Railway URL
# Production: https://ai-nurse-florence-production.up.railway.app
# Staging: https://ai-nurse-florence-staging.up.railway.app
PRODUCTION_URL = "https://ai-nurse-florence-production.up.railway.app"


async def test_endpoint(
    client: httpx.AsyncClient, endpoint: str, name: str
) -> Dict[str, Any]:
    """Test a single endpoint."""
    url = f"{PRODUCTION_URL}{endpoint}"
    print(f"\n🔍 Testing: {name}")
    print(f"   URL: {url}")

    try:
        response = await client.get(url, timeout=30.0)

        if response.status_code == 200:
            print(f"   ✅ Status: {response.status_code}")
            try:
                data = response.json()
                return {"success": True, "data": data, "url": url}
            except Exception:
                return {"success": True, "data": response.text[:200], "url": url}
        else:
            print(f"   ❌ Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return {"success": False, "status": response.status_code, "url": url}

    except httpx.ConnectError as e:
        print(f"   ❌ Connection failed: {e}")
        return {"success": False, "error": "connection_failed", "url": url}
    except httpx.TimeoutException:
        print("   ❌ Request timed out")
        return {"success": False, "error": "timeout", "url": url}
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return {"success": False, "error": str(e), "url": url}


async def main():
    """Run all production deployment tests."""

    print("=" * 80)
    print("PRODUCTION DEPLOYMENT TEST - AI NURSE FLORENCE")
    print("=" * 80)
    print(f"\nTesting deployment at: {PRODUCTION_URL}")

    if "your-app" in PRODUCTION_URL:
        print(
            "\n⚠️  WARNING: You need to update PRODUCTION_URL with your actual Railway domain!"
        )
        print("   Find it in Railway dashboard or run: railway domain")
        return

    async with httpx.AsyncClient() as client:

        # Test 1: Basic Health Check
        print("\n" + "=" * 80)
        print("TEST 1: Basic Health Check")
        print("=" * 80)

        health_result = await test_endpoint(client, "/health", "Main Health Endpoint")

        if health_result["success"]:
            health_data = health_result["data"]
            print(f"\n   📊 Service: {health_data.get('service', 'unknown')}")
            print(f"   📊 Version: {health_data.get('version', 'unknown')}")
            print(f"   📊 Status: {health_data.get('status', 'unknown')}")
            print(f"   📊 Environment: {health_data.get('environment', 'unknown')}")

        # Test 2: AI Provider Configuration
        print("\n" + "=" * 80)
        print("TEST 2: AI Provider Configuration")
        print("=" * 80)

        ai_result = await test_endpoint(
            client, "/api/v1/health/ai", "AI Health Endpoint"
        )

        if ai_result["success"]:
            ai_data = ai_result["data"]
            ai_system = ai_data.get("ai_system", {})

            print(
                f"\n   🤖 Primary Provider: {ai_system.get('primary_provider', 'unknown')}"
            )
            print(
                f"   🤖 Fallback Provider: {ai_system.get('fallback_provider', 'None')}"
            )
            print(f"   🤖 Fallback Enabled: {ai_system.get('fallback_enabled', False)}")

            providers = ai_system.get("providers_available", {})
            print("\n   📊 Provider Availability:")
            print(f"      OpenAI: {'✅' if providers.get('openai') else '❌'}")
            print(f"      Anthropic: {'✅' if providers.get('anthropic') else '❌'}")

            circuit_breakers = ai_system.get("circuit_breakers", {})
            print("\n   🔌 Circuit Breaker Status:")
            for provider, state in circuit_breakers.items():
                status = state.get("state", "unknown")
                failures = state.get("failure_count", 0)
                threshold = state.get("threshold", 0)
                emoji = (
                    "✅"
                    if status == "CLOSED"
                    else "⚠️" if status == "HALF_OPEN" else "❌"
                )
                print(
                    f"      {provider}: {emoji} {status} (failures: {failures}/{threshold})"
                )

        # Test 3: Configuration Check
        print("\n" + "=" * 80)
        print("TEST 3: Configuration Details")
        print("=" * 80)

        if health_result["success"]:
            health_data = health_result["data"]
            config = health_data.get("configuration", {})

            print(f"\n   AI Provider: {config.get('ai_provider', 'not set')}")
            print(
                f"   AI Fallback Enabled: {config.get('ai_fallback_enabled', 'not set')}"
            )
            print(f"   OpenAI Available: {config.get('openai_available', False)}")
            print(f"   Anthropic Available: {config.get('anthropic_available', False)}")
            print(f"   Redis Available: {config.get('redis_available', False)}")
            print(f"   Rate Limiting: {config.get('rate_limiting', False)}")

        # Test 4: API Endpoints
        print("\n" + "=" * 80)
        print("TEST 4: Core API Endpoints")
        print("=" * 80)

        await test_endpoint(client, "/api/v1/health", "API Health v1")
        await test_endpoint(client, "/docs", "API Documentation")

        # Summary
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)

        issues = []

        if not health_result["success"]:
            issues.append("❌ Main health endpoint not responding")

        if ai_result["success"]:
            ai_system = ai_result["data"].get("ai_system", {})
            providers = ai_system.get("providers_available", {})

            if not providers.get("openai"):
                issues.append("⚠️  OpenAI API key not configured")
            if not providers.get("anthropic"):
                issues.append(
                    "⚠️  Anthropic API key not configured (fallback unavailable)"
                )

            fallback = ai_system.get("fallback_provider")

            if not fallback and ai_system.get("fallback_enabled"):
                issues.append(
                    "⚠️  Fallback enabled but no alternate provider configured"
                )
        else:
            issues.append("❌ AI health endpoint not responding")

        if issues:
            print("\n⚠️  Issues Found:")
            for issue in issues:
                print(f"   {issue}")
        else:
            print("\n✅ All systems operational!")

        print("\n" + "=" * 80)
        print("RECOMMENDATIONS")
        print("=" * 80)

        if ai_result["success"]:
            ai_system = ai_result["data"].get("ai_system", {})
            providers = ai_system.get("providers_available", {})

            print("\n📋 Environment Variables Needed:")

            if not providers.get("anthropic"):
                print("\n   For quality-first production with fallback:")
                print("   ```")
                print("   AI_PROVIDER=anthropic")
                print("   ANTHROPIC_API_KEY=your-anthropic-key")
                print("   ANTHROPIC_MODEL=claude-3-5-sonnet-20241022")
                print("   AI_FALLBACK_ENABLED=true")
                print("   AI_FALLBACK_PROVIDER=openai")
                print("   ```")

            if not providers.get("openai"):
                print("\n   For OpenAI configuration:")
                print("   ```")
                print("   OPENAI_API_KEY=your-openai-key")
                print("   OPENAI_MODEL=gpt-4o")
                print("   ```")

            if providers.get("openai") and providers.get("anthropic"):
                print("\n   ✅ Both providers configured - fallback system ready!")

        print("\n" + "=" * 80)


if __name__ == "__main__":
    print(
        "\n💡 TIP: Update PRODUCTION_URL at the top of this file with your Railway domain"
    )
    print("   Find it with: railway domain")
    print("   Or in Railway dashboard under your service settings\n")

    asyncio.run(main())
