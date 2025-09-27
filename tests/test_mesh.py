import json

from src.utils.mesh_loader import MeshIndex
from src.services.mesh_service import get_mesh_index, map_to_mesh


def test_mesh_index_basic_mapping(tmp_path):
    data = {
        "Hypertension": {"mesh_id": "D006973", "synonyms": ["High blood pressure"]},
        "Diabetes Mellitus": {"mesh_id": "D003920", "synonyms": ["Diabetes"]}
    }
    p = tmp_path / "mesh.json"
    p.write_text(json.dumps(data), encoding="utf8")

    mi = MeshIndex.from_json_file(str(p))

    # exact
    res = mi.map("Hypertension")
    assert res and res[0]["mesh_id"] == "D006973"

    # synonym
    res2 = mi.map("high blood pressure")
    assert res2 and res2[0]["mesh_id"] == "D006973"

    # token overlap
    res3 = mi.map("diabetes")
    assert res3 and res3[0]["mesh_id"] == "D003920"


def test_mesh_service_env_loading(tmp_path, monkeypatch):
    data = {"Asthma": "D001249"}
    p = tmp_path / "mesh2.json"
    p.write_text(json.dumps(data), encoding="utf8")

    monkeypatch.setenv("MESH_JSON_PATH", str(p))
    idx = get_mesh_index()
    assert idx is not None

    m = map_to_mesh("asthma")
    assert m and m[0]["mesh_id"] == "D001249"
