import json
import re
from pathlib import Path
from typing import Dict, List, Optional


class MeshIndex:
    """Simple in-memory MeSH index.

    Expected JSON format (flexible):
    {
       "Hypertension": {"mesh_id": "D006973", "synonyms": ["High blood pressure"]},
       "Diabetes Mellitus": "D003920"
    }

    The loader supports either a map term->mesh_id (string) or term->object with mesh_id and synonyms.
    Matching is intentionally simple: exact (case-insensitive), prefix, then token-overlap scoring.
    """

    def __init__(self, index: Optional[Dict[str, Dict]] = None):
        self.index = {}
        if index:
            for term, data in index.items():
                self._add_entry(term, data)

    @classmethod
    def from_json_file(cls, path: str) -> "MeshIndex":
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"MeSH JSON file not found: {path}")

        raw = json.loads(p.read_text(encoding="utf8"))
        return cls(raw)

    def _add_entry(self, term: str, data):
        term_norm = term.strip()
        if isinstance(data, str):
            mesh_id = data
            synonyms = []
        elif isinstance(data, dict):
            mesh_id = data.get("mesh_id") or data.get("id") or data.get("MeshID")
            synonyms = data.get("synonyms") or data.get("alt") or []
        else:
            mesh_id = None
            synonyms = []

        if not mesh_id:
            return

        # store primary term and synonyms
        self.index[term_norm.lower()] = {"term": term_norm, "mesh_id": mesh_id, "synonyms": [s for s in synonyms]}
        for s in synonyms:
            self.index[str(s).strip().lower()] = {"term": term_norm, "mesh_id": mesh_id, "synonyms": [s for s in synonyms]}

    def map(self, query: str, top_k: int = 5) -> List[Dict]:
        q = (query or "").strip()
        if not q:
            return []

        q_low = q.lower()

        # exact match
        if q_low in self.index:
            entry = self.index[q_low]
            return [{"term": entry["term"], "mesh_id": entry["mesh_id"], "score": 1.0}]

        # prefix match
        candidates = []
        for key, entry in self.index.items():
            if key.startswith(q_low):
                candidates.append((entry, 0.9))

        # token overlap scoring fallback
        if not candidates:
            q_tokens = set(re.findall(r"\w+", q_low))
            for key, entry in self.index.items():
                key_tokens = set(re.findall(r"\w+", key))
                if not key_tokens:
                    continue
                overlap = q_tokens.intersection(key_tokens)
                score = len(overlap) / max(len(q_tokens), len(key_tokens))
                if score > 0:
                    candidates.append((entry, round(score, 3)))

        # sort and return top_k
        candidates_sorted = sorted(candidates, key=lambda t: t[1], reverse=True)
        results = []
        seen = set()
        for entry, score in candidates_sorted[:top_k]:
            key = (entry['mesh_id'])
            if key in seen:
                continue
            seen.add(key)
            results.append({"term": entry["term"], "mesh_id": entry["mesh_id"], "score": float(score)})

        return results


__all__ = ["MeshIndex"]
