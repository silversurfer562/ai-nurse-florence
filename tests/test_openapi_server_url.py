import os

from fastapi.testclient import TestClient


def _reset_settings_module():
    try:
        import src.utils.config as config
        config._settings = None
    except Exception:
        pass


def test_openapi_servers_include_effective_base(monkeypatch):
    orig_env = dict(os.environ)
    try:
        # Ensure APP_BASE_URL absent and force https
        monkeypatch.delenv('APP_BASE_URL', raising=False)
        monkeypatch.setenv('FORCE_HTTPS', 'true')
        monkeypatch.setenv('HOST', 'openapi.test')
        monkeypatch.setenv('PORT', '4443')

        _reset_settings_module()

        # Import app fresh
        import importlib
        app_module = importlib.import_module('app')
        # Use TestClient as context manager to run lifespan startup where app.openapi_schema is populated
        with TestClient(app_module.app) as client:
            schema = client.get('/openapi.json').json()
        servers = schema.get('servers', [])
        assert any(s.get('url', '').startswith('https://openapi.test:4443') for s in servers)
    finally:
        os.environ.clear()
        os.environ.update(orig_env)
        _reset_settings_module()
