"""MeSH Loader Service - lightweight local loader for MeSH terms

Provides a fallback JSON loader for MeSH index data used by the disease service.
This keeps external dependencies optional and testable.
"""
import json
from pathlib import Path
from typing import Dict, Optional

_MESH_INDEX: Optional[Dict[str, Dict]] = None


def _default_mesh_path() -> Path:
    return Path(__file__).resolve().parents[1] / 'data' / 'mesh_stub.json'


def load_mesh_index(path: Optional[str] = None) -> Dict[str, Dict]:
    global _MESH_INDEX
    if _MESH_INDEX is not None:
        return _MESH_INDEX

    p = Path(path) if path else _default_mesh_path()
    if not p.exists():
        # Return empty index if file missing
        _MESH_INDEX = {}
        return _MESH_INDEX

    with p.open('r', encoding='utf-8') as fh:
        data = json.load(fh)

    # Expecting mapping of mesh_id -> metadata
    _MESH_INDEX = data
    return _MESH_INDEX


def get_mesh_term(mesh_id: str) -> Optional[Dict]:
    if _MESH_INDEX is None:
        load_mesh_index()
    return _MESH_INDEX.get(mesh_id)
