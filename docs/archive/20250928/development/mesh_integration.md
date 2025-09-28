# MeSH integration

This project includes a small MeSH index loader to help normalize clinical queries to controlled vocabulary terms.

Files added
- `src/utils/mesh_loader.py` — in-memory MeSH index with simple matching
- `src/services/mesh_service.py` — service wrapper that loads index from `MESH_JSON_PATH` env var

How to obtain MeSH JSON
1. Download official MeSH data from NLM (RDF/XML) and convert to JSON. A simple conversion script can use `xmltodict`:

```python
import xmltodict, json
doc = xmltodict.parse(open('desc2019.xml').read())
# extract descriptors -> build mapping
open('mesh.json','w').write(json.dumps(mapping))
```

2. Alternatively, use an existing community-converted JSON of MeSH (verify license/terms). Place the file locally and set `MESH_JSON_PATH` to its path.

Usage
1. Set env var:

```bash
export MESH_JSON_PATH=/path/to/mesh.json
```

2. The service exposes `src.services.mesh_service.map_to_mesh(term)` which returns `[{term, mesh_id, score}, ...]`.

Testing
- Unit tests added: `tests/test_mesh.py` (uses small inline JSON fixtures).

Notes
- Matching is intentionally simple. For production, consider using a proper tokeniser and search index (Whoosh/Elasticsearch) or using official MeSH APIs.
