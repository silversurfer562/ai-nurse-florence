#!/usr/bin/env python3
"""
Configuration validation script for Notion-GitHub integration.

This script helps verify that all required environment variables are set
correctly for the integration to work.
"""
import os
import sys
from typing import List, Tuple

def check_environment() -> Tuple[bool, List[str]]:
    """
    Check if all required environment variables are set.
    
    Returns:
        Tuple of (all_good: bool, issues: List[str])
    """
    issues = []
    
    # Core application settings
    if not os.getenv("OPENAI_API_KEY"):
        issues.append("❌ OPENAI_API_KEY is not set")
    else:
        issues.append("✅ OPENAI_API_KEY is set")
    
    if not os.getenv("API_BEARER"):
        issues.append("❌ API_BEARER is not set")  
    else:
        issues.append("✅ API_BEARER is set")
    
    # Notion integration settings
    notion_token = os.getenv("NOTION_TOKEN")
    if not notion_token:
        issues.append("❌ NOTION_TOKEN is not set (required for Notion integration)")
    elif not notion_token.startswith("secret_"):
        issues.append("⚠️  NOTION_TOKEN should start with 'secret_'")
    else:
        issues.append("✅ NOTION_TOKEN is set correctly")
    
    notion_db_id = os.getenv("NOTION_DATABASE_ID")
    if not notion_db_id:
        issues.append("❌ NOTION_DATABASE_ID is not set (required for Notion integration)")
    elif len(notion_db_id) != 32:
        issues.append("⚠️  NOTION_DATABASE_ID should be 32 characters long")
    else:
        issues.append("✅ NOTION_DATABASE_ID is set correctly")
    
    # GitHub webhook settings
    webhook_secret = os.getenv("GITHUB_WEBHOOK_SECRET")
    if not webhook_secret:
        issues.append("❌ GITHUB_WEBHOOK_SECRET is not set (required for webhook security)")
    elif len(webhook_secret) < 20:
        issues.append("⚠️  GITHUB_WEBHOOK_SECRET should be at least 20 characters long")
    else:
        issues.append("✅ GITHUB_WEBHOOK_SECRET is set correctly")
    
    # Optional settings
    enable_notion = os.getenv("ENABLE_NOTION_SYNC", "false").lower()
    if enable_notion in ["true", "1", "yes"]:
        issues.append("✅ ENABLE_NOTION_SYNC is enabled")
    else:
        issues.append("ℹ️  ENABLE_NOTION_SYNC is disabled (webhook will still work)")
    
    # Count errors and warnings
    errors = [issue for issue in issues if issue.startswith("❌")]
    warnings = [issue for issue in issues if issue.startswith("⚠️")]
    
    return len(errors) == 0, issues

def test_notion_connection():
    """Test connection to Notion API."""
    try:
        import httpx
        import asyncio
        
        async def test_connection():
            token = os.getenv("NOTION_TOKEN")
            db_id = os.getenv("NOTION_DATABASE_ID")
            
            if not token or not db_id:
                return False, "Missing Notion credentials"
                
            headers = {
                "Authorization": f"Bearer {token}",
                "Notion-Version": "2022-06-28"
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                try:
                    response = await client.get(
                        f"https://api.notion.com/v1/databases/{db_id}",
                        headers=headers
                    )
                    if response.status_code == 200:
                        db_info = response.json()
                        return True, f"Connected to database: {db_info.get('title', [{}])[0].get('plain_text', 'Untitled')}"
                    else:
                        return False, f"HTTP {response.status_code}: {response.text}"
                except Exception as e:
                    return False, f"Connection error: {str(e)}"
        
        success, message = asyncio.run(test_connection())
        return success, message
        
    except ImportError:
        return None, "httpx not available for connection test"
    except Exception as e:
        return False, f"Test failed: {str(e)}"

def main():
    """Main validation function."""
    print("🔍 Notion-GitHub Integration Configuration Validator")
    print("=" * 55)
    print()
    
    # Check environment variables
    all_good, issues = check_environment()
    
    print("📋 Environment Variables:")
    for issue in issues:
        print(f"  {issue}")
    print()
    
    # Test Notion connection if possible
    if os.getenv("NOTION_TOKEN") and os.getenv("NOTION_DATABASE_ID"):
        print("🔌 Testing Notion Connection:")
        success, message = test_notion_connection()
        if success is True:
            print(f"  ✅ {message}")
        elif success is False:
            print(f"  ❌ {message}")
        else:
            print(f"  ℹ️  {message}")
        print()
    
    # Summary
    errors = [issue for issue in issues if issue.startswith("❌")]
    warnings = [issue for issue in issues if issue.startswith("⚠️")]
    
    print("📊 Summary:")
    if not errors:
        print("  ✅ Configuration looks good!")
        if warnings:
            print(f"  ⚠️  {len(warnings)} warning(s) - review recommended")
    else:
        print(f"  ❌ {len(errors)} error(s) need to be fixed")
        if warnings:
            print(f"  ⚠️  {len(warnings)} warning(s) - review recommended")
    
    print()
    print("🚀 Next Steps:")
    if errors:
        print("  1. Fix the configuration errors above")
        print("  2. Re-run this script to verify")
    else:
        print("  1. Deploy your application")
        print("  2. Configure GitHub webhook: https://your-domain.com/webhooks/github")
        print("  3. Test with GitHub events")
        print("  4. Monitor webhook health: https://your-domain.com/webhooks/health")
    
    print()
    print("📚 For setup help, see: docs/NOTION_GITHUB_SETUP.md")
    
    return 0 if all_good else 1

if __name__ == "__main__":
    sys.exit(main())