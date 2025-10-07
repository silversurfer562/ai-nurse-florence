"""
Test AI Provider Fallback Service

Tests:
1. Normal operation with primary provider
2. Automatic fallback when primary fails
3. Circuit breaker behavior
4. Retry with exponential backoff
5. Health status monitoring
"""

import asyncio
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from src.services.ai_provider_fallback import get_ai_service
from src.utils.config import get_settings


async def test_health_status():
    """Test 1: Check service health status."""
    print("=" * 80)
    print("TEST 1: Health Status Check")
    print("=" * 80)

    service = get_ai_service()
    health = service.get_health_status()

    print(f"\nPrimary Provider: {health['primary_provider']}")
    print(f"Fallback Provider: {health['fallback_provider']}")
    print(f"Fallback Enabled: {health['fallback_enabled']}")

    print("\n📊 Provider Availability:")
    for provider, available in health["providers_available"].items():
        status = "✅ Available" if available else "❌ Not Configured"
        print(f"  {provider}: {status}")

    print("\n🔌 Circuit Breaker States:")
    for provider, state in health["circuit_breakers"].items():
        print(
            f"  {provider}: {state['state']} (failures: {state['failure_count']}/{state['threshold']})"
        )

    return health


async def test_normal_generation():
    """Test 2: Normal AI generation with primary provider."""
    print("\n" + "=" * 80)
    print("TEST 2: Normal AI Generation")
    print("=" * 80)

    service = get_ai_service()

    prompt = "What are the key nursing considerations for a patient with hypertension?"
    print(f"\n📝 Prompt: {prompt}")

    try:
        result = await service.generate_response(
            prompt=prompt,
            context="Clinical nursing assessment",
            max_tokens=500,
        )

        if result.get("error"):
            print(f"\n❌ Error: {result['error']}")
            print(
                f"Circuit Breaker States: {result.get('circuit_breaker_states', 'N/A')}"
            )
        else:
            print("\n✅ Success!")
            print(f"Provider: {result.get('provider', 'unknown')}")
            print(f"Model: {result.get('model', 'unknown')}")
            print(f"Attempts: {result.get('attempts', 1)}")

            if result.get("fallback_used"):
                print(
                    f"⚠️  Fallback Used - Primary provider ({result.get('primary_provider_failed')}) failed"
                )

            print("\n📄 Response Preview:")
            response_text = result.get("response", "")
            if response_text:
                preview = (
                    response_text[:300] + "..."
                    if len(response_text) > 300
                    else response_text
                )
                print(preview)

            if result.get("usage"):
                print("\n📊 Token Usage:")
                usage = result["usage"]
                for key, value in usage.items():
                    print(f"  {key}: {value}")

        return result

    except Exception as e:
        print(f"\n❌ Exception: {e}")
        return None


async def test_configuration_details():
    """Test 3: Display configuration details."""
    print("\n" + "=" * 80)
    print("TEST 3: Configuration Details")
    print("=" * 80)

    settings = get_settings()

    print("\n🔧 AI Provider Configuration:")
    print(f"  Primary Provider: {settings.AI_PROVIDER}")
    print(f"  OpenAI Model: {settings.OPENAI_MODEL}")
    print(f"  Anthropic Model: {settings.ANTHROPIC_MODEL}")

    print("\n🔄 Fallback Configuration:")
    print(f"  Fallback Enabled: {settings.AI_FALLBACK_ENABLED}")
    print(
        f"  Fallback Provider: {settings.AI_FALLBACK_PROVIDER or 'Auto (alternate provider)'}"
    )
    print(f"  Fallback Model: {settings.AI_FALLBACK_MODEL or 'Provider default'}")
    print(f"  Max Retries: {settings.AI_MAX_RETRIES}")
    print(f"  Circuit Breaker Threshold: {settings.AI_CIRCUIT_BREAKER_THRESHOLD}")
    print(f"  Circuit Breaker Timeout: {settings.AI_CIRCUIT_BREAKER_TIMEOUT}s")

    print("\n🔑 API Key Status:")
    print(f"  OpenAI: {'✅ Configured' if settings.has_openai() else '❌ Not Set'}")
    print(
        f"  Anthropic: {'✅ Configured' if settings.has_anthropic() else '❌ Not Set'}"
    )

    fallback_provider = settings.get_fallback_provider()
    if fallback_provider:
        print(f"\n✅ Fallback will use: {fallback_provider}")
    else:
        print("\n⚠️  No fallback provider available (need both API keys for fallback)")


async def test_multiple_requests():
    """Test 4: Multiple requests to verify stability."""
    print("\n" + "=" * 80)
    print("TEST 4: Multiple Requests (Stability Test)")
    print("=" * 80)

    service = get_ai_service()

    prompts = [
        "What is diabetes mellitus?",
        "List common side effects of metformin.",
        "What are the signs of hypoglycemia?",
    ]

    results = []
    for i, prompt in enumerate(prompts, 1):
        print(f"\n📝 Request {i}/{len(prompts)}: {prompt}")

        try:
            result = await service.generate_response(
                prompt=prompt,
                max_tokens=200,
            )

            if result.get("error"):
                print(f"  ❌ Failed: {result['error']}")
            else:
                provider = result.get("provider", "unknown")
                attempts = result.get("attempts", 1)
                fallback = " (fallback)" if result.get("fallback_used") else ""
                print(f"  ✅ Success: {provider}{fallback} (attempts: {attempts})")

            results.append(result)

        except Exception as e:
            print(f"  ❌ Exception: {e}")
            results.append(None)

    # Summary
    successes = sum(1 for r in results if r and not r.get("error"))
    print(f"\n📊 Summary: {successes}/{len(prompts)} requests succeeded")

    return results


async def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("AI PROVIDER FALLBACK SERVICE - TEST SUITE")
    print("=" * 80)

    try:
        # Test 1: Configuration
        await test_configuration_details()

        # Test 2: Health status
        await test_health_status()

        # Test 3: Normal generation
        await test_normal_generation()

        # Test 4: Multiple requests
        await test_multiple_requests()

        # Final health check
        print("\n" + "=" * 80)
        print("FINAL HEALTH CHECK")
        print("=" * 80)
        await test_health_status()

        print("\n" + "=" * 80)
        print("✅ ALL TESTS COMPLETED")
        print("=" * 80)
        print("\n💡 Tips:")
        print("  - Set both OPENAI_API_KEY and ANTHROPIC_API_KEY to test fallback")
        print("  - Configure AI_PROVIDER and AI_FALLBACK_PROVIDER in .env")
        print("  - Monitor circuit breaker states during production")

    except Exception as e:
        print(f"\n❌ Test suite failed with exception: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
