"""
MeSH (Medical Subject Headings) Service - AI Nurse Florence

This service provides integration with the NLM MeSH controlled vocabulary for
standardizing medical terminology. It maps free-text medical terms to official
MeSH descriptors, enabling consistent disease/condition naming across the application.

Key Features:
    - Lazy loading of MeSH index from JSON file
    - Global singleton pattern for memory efficiency
    - Fuzzy matching of medical terms to MeSH descriptors
    - Graceful degradation when MeSH data unavailable

Architecture Patterns:
    - Singleton Pattern: Single global MeshIndex instance
    - Lazy Loading: Index loaded only when first requested
    - Graceful Degradation: Returns empty list if MeSH unavailable

Dependencies:
    Required: src.utils.mesh_loader.MeshIndex
    Optional: MESH_JSON_PATH environment variable

Data Source:
    MeSH vocabulary from NLM (National Library of Medicine)
    https://www.nlm.nih.gov/mesh/

Examples:
    >>> # Map disease name to MeSH term
    >>> results = map_to_mesh("diabetes", top_k=3)
    >>> for result in results:
    ...     print(f"{result['term']} ({result['mesh_id']}): {result['score']}")
    Diabetes Mellitus (D003920): 0.95

    >>> # Get MeSH index directly
    >>> index = get_mesh_index()
    >>> if index:
    ...     terms = index.map("hypertension", top_k=5)

Self-Improvement Checklist:
    [ ] Add unit tests for map_to_mesh() with various medical terms
    [ ] Add caching for frequently queried terms (Redis/memory)
    [ ] Add telemetry/metrics for MeSH mapping accuracy
    [ ] Consider adding synonym expansion (diabetes -> DM, T2DM, etc.)
    [ ] Add support for MeSH tree navigation (hierarchical relationships)
    [ ] Add batch mapping function for multiple terms
    [ ] Document expected MESH_JSON_PATH file format/schema
    [ ] Add validation for MeSH JSON file integrity on load

Version: 2.4.2
Last Updated: 2025-10-04
"""

import os
from pathlib import Path
from typing import Dict, List, Optional

from src.utils.mesh_loader import MeshIndex

# Global singleton MeshIndex instance (lazy-loaded)
_mesh_index: Optional[MeshIndex] = None


def _load_mesh_index_from_env() -> Optional[MeshIndex]:
    """
    Internal function to load MeSH index from file specified in environment.

    Reads the MESH_JSON_PATH environment variable and attempts to load the
    MeSH index from that JSON file. This function is called once by get_mesh_index()
    and the result is cached globally.

    Environment Variables:
        MESH_JSON_PATH: Absolute path to MeSH JSON file
            Example: "/app/data/mesh_index.json"

    Returns:
        Optional[MeshIndex]: Loaded MeSH index, or None if:
            - MESH_JSON_PATH not set
            - File doesn't exist at specified path
            - JSON file is malformed or loading fails

    Note:
        Exceptions are silently caught and None returned for graceful degradation.
        The application should function without MeSH (using fallback disease lists).

    Examples:
        >>> # Typically called by get_mesh_index(), not directly
        >>> index = _load_mesh_index_from_env()
        >>> if index:
        ...     print("MeSH index loaded successfully")
    """
    mesh_path = os.getenv("MESH_JSON_PATH")
    if not mesh_path:
        return None
    p = Path(mesh_path)
    if not p.exists():
        return None
    try:
        return MeshIndex.from_json_file(str(p))
    except Exception:
        return None


def get_mesh_index() -> Optional[MeshIndex]:
    """
    Get the global MeSH index instance (singleton pattern with lazy loading).

    This function returns the cached MeSH index if already loaded, otherwise
    loads it from the file specified in MESH_JSON_PATH environment variable.
    The index is loaded only once and reused for all subsequent calls.

    Returns:
        Optional[MeshIndex]: Global MeSH index instance, or None if unavailable

    Thread Safety:
        This function is NOT thread-safe. If called concurrently during startup,
        multiple index instances may be created. For production, consider adding
        a lock or using a startup hook to pre-load the index.

    Examples:
        >>> index = get_mesh_index()
        >>> if index:
        ...     results = index.map("diabetes", top_k=5)
        ...     print(f"Found {len(results)} MeSH terms")
        ... else:
        ...     print("MeSH index not available")

    Notes:
        - First call may take 1-2 seconds to load JSON file
        - Subsequent calls return immediately (cached)
        - Returns None if MESH_JSON_PATH not set or file not found
        - Application should handle None gracefully (use fallbacks)
    """
    global _mesh_index
    if _mesh_index is not None:
        return _mesh_index
    _mesh_index = _load_mesh_index_from_env()
    return _mesh_index


def map_to_mesh(term: str, top_k: int = 5) -> List[Dict]:
    """
    Map a free-text medical term to standardized MeSH controlled vocabulary terms.

    This function provides the primary interface for converting user-entered
    medical terminology into official NLM MeSH descriptors. It uses fuzzy matching
    to find the most relevant MeSH terms even when input contains typos or
    informal medical language.

    Args:
        term (str): Free-text medical term, condition, or disease name
            Examples: "diabetes", "high blood pressure", "heart attack", "DM"
        top_k (int, optional): Maximum number of MeSH terms to return, ranked by
            relevance score. Defaults to 5.

    Returns:
        List[Dict]: List of MeSH term matches, ordered by relevance (best first).
            Each dict contains:
            {
                "term": str,      # Official MeSH descriptor name
                "mesh_id": str,   # MeSH unique identifier (e.g., "D003920")
                "score": float    # Relevance score (0.0 to 1.0, higher is better)
            }
            Returns empty list [] if:
            - MeSH index not available (MESH_JSON_PATH not set)
            - No matching terms found for query
            - term is empty string

    Examples:
        >>> # Basic disease mapping
        >>> results = map_to_mesh("diabetes")
        >>> for match in results:
        ...     print(f"{match['term']} ({match['mesh_id']}): {match['score']:.2f}")
        Diabetes Mellitus (D003920): 0.95
        Diabetes Mellitus, Type 2 (D003924): 0.88
        Diabetes Mellitus, Type 1 (D003922): 0.85

        >>> # Informal term mapping
        >>> results = map_to_mesh("high blood pressure", top_k=3)
        >>> print(results[0]['term'])
        Hypertension

        >>> # Handle no results gracefully
        >>> results = map_to_mesh("xyz123nonexistent")
        >>> if not results:
        ...     print("No MeSH terms found - use original term")

    Use Cases:
        - Disease autocomplete in clinical trials search
        - Standardizing diagnosis terms for research queries
        - Mapping patient-entered symptoms to medical terminology
        - Normalizing drug indication searches

    Notes:
        - Uses fuzzy string matching (not exact match required)
        - Case-insensitive matching
        - Returns empty list if MeSH not configured (graceful degradation)
        - Consider caching results for frequently queried terms
        - Performance: ~10-50ms per query depending on index size
    """
    idx = get_mesh_index()
    if not idx:
        return []
    return idx.map(term, top_k=top_k)


__all__ = ["get_mesh_index", "map_to_mesh"]
