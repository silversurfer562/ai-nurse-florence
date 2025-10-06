"""
Utils package for AI Nurse Florence.

This package provides utility functions and classes following the
Conditional Imports Pattern for graceful degradation.

Utilities are organized by function:
- api_responses: Standardized API response formatting
- redis_cache: Redis caching utilities
- smart_cache: Intelligent caching with TTL management
- config: Application configuration
- exceptions: Custom exception classes
- logging: Logging utilities
- mesh_loader: Medical Subject Headings (MeSH) data loading

All utilities support conditional imports and graceful degradation
when optional dependencies are unavailable.
"""

# Utilities are imported as needed in application code
# No global exports to avoid import-time dependencies
