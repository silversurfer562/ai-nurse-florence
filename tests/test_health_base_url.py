import os
import importlib

from fastapi.testclient import TestClient


def _reset_settings_module():
    try:
        import src.utils.config as config
        config._settings = None
    except Exception:
        pass


def test_health_endpoint_includes_effective_base_url(monkeypatch):
    orig_env = dict(os.environ)
    try:
        monkeypatch.delenv('APP_BASE_URL', raising=False)
        monkeypatch.setenv('FORCE_HTTPS', 'true')
        monkeypatch.setenv('HOST', 'health.test')
        monkeypatch.setenv('PORT', '8443')

        _reset_settings_module()

        app_module = importlib.import_module('app')
        with TestClient(app_module.app) as client:
            resp = client.get('/api/v1/health/')
            assert resp.status_code == 200
            data = resp.json()
            assert data.get('base_url', '').startswith('https://health.test:8443')
    finally:
        os.environ.clear()
        os.environ.update(orig_env)
        _reset_settings_module()
