from src.services import mesh_loader


def test_load_mesh_index_from_stub():
    idx = mesh_loader.load_mesh_index()
    assert isinstance(idx, dict)
    assert 'D001922' in idx
    assert idx['D001922']['term'] == 'Hypertension'


def test_get_mesh_term_existing():
    term = mesh_loader.get_mesh_term('D001922')
    assert term is not None
    assert term['uid'] == 'D001922'


def test_get_mesh_term_missing():
    term = mesh_loader.get_mesh_term('DOES_NOT_EXIST')
    assert term is None
