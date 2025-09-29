#!/usr/bin/env python3
"""Test monitoring router loading"""

import sys
import os

# Add project root to path
sys.path.insert(0, '/Users/patrickroebuck/projects/ai-nurse-florence')

try:
    print("Testing monitoring router import...")
    from src.routers.monitoring import router
    print(f"✅ Monitoring router loaded successfully")
    print(f"Router prefix: {router.prefix}")
    print(f"Router tags: {router.tags}")
    print(f"Number of routes: {len(router.routes)}")
except Exception as e:
    print(f"❌ Failed to load monitoring router: {e}")
    import traceback
    traceback.print_exc()
