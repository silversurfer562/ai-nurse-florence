from typing import List, Dict, Optional
import os
from pathlib import Path

from src.utils.mesh_loader import MeshIndex


_mesh_index: Optional[MeshIndex] = None


def _load_mesh_index_from_env() -> Optional[MeshIndex]:
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
    global _mesh_index
    if _mesh_index is not None:
        return _mesh_index
    _mesh_index = _load_mesh_index_from_env()
    return _mesh_index


def map_to_mesh(term: str, top_k: int = 5) -> List[Dict]:
    """Map an arbitrary query term to MeSH terms.

    Returns a list of dicts: {term, mesh_id, score}
    If no index configured or no match, returns empty list.
    """
    idx = get_mesh_index()
    if not idx:
        return []
    return idx.map(term, top_k=top_k)


__all__ = ["get_mesh_index", "map_to_mesh"]
