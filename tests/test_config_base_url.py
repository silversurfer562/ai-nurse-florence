import os

from src.utils import config


def _reset_settings_module():
    # Clear cached settings so get_settings() will re-initialize from env
    try:
        config._settings = None
    except Exception:
        pass


def test_get_base_url_uses_app_base_url_if_set(monkeypatch):
    orig_env = dict(os.environ)
    try:
        # Set APP_BASE_URL and a conflicting FORCE_HTTPS value
        monkeypatch.setenv('APP_BASE_URL', 'https://api.example.com')
        monkeypatch.setenv('FORCE_HTTPS', 'false')
        _reset_settings_module()

        base = config.get_base_url()
        assert base == 'https://api.example.com'
    finally:
        os.environ.clear()
        os.environ.update(orig_env)
        _reset_settings_module()


def test_get_base_url_constructs_scheme_using_force_https(monkeypatch):
    orig_env = dict(os.environ)
    try:
        # Ensure APP_BASE_URL is not set
        monkeypatch.delenv('APP_BASE_URL', raising=False)

        # Set HOST/PORT and FORCE_HTTPS to true
        monkeypatch.setenv('HOST', 'myhost.local')
        monkeypatch.setenv('PORT', '12345')
        monkeypatch.setenv('FORCE_HTTPS', 'true')
        _reset_settings_module()

        base = config.get_base_url()
        assert base.startswith('https://')
        assert 'myhost.local' in base
        assert ':12345' in base
    finally:
        os.environ.clear()
        os.environ.update(orig_env)
        _reset_settings_module()
