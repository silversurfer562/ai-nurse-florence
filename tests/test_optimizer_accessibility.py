import pytest

try:
    from playwright.sync_api import sync_playwright
    _has_playwright = True
except Exception:
    _has_playwright = False


@pytest.mark.skipif(not _has_playwright, reason="Playwright not installed in this environment")
def test_modal_focus_trap_and_escape_opens_and_closes(tmp_path):
    """Simple accessibility smoke test: open the optimizer page, trigger View Results,
    ensure modal is focused and Esc closes it. Runs only when Playwright is installed.
    """
    url = 'http://127.0.0.1:8000/clinical-assessment-optimizer.html'
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)

        # Wait for the View Results button
        page.wait_for_selector('#viewResultsBtn', timeout=5000)
        page.click('#viewResultsBtn')

        # Wait for modal to appear
        page.wait_for_selector('[role="dialog"]', timeout=5000)
        dialog = page.query_selector('[role="dialog"]')
        assert dialog is not None

        # Focus should be inside the dialog
        active = page.evaluate('document.activeElement.id')
        assert active != 'viewResultsBtn'

        # Press Escape to close
        page.keyboard.press('Escape')
        # Ensure dialog is removed
        assert page.query_selector('[role="dialog"]') is None

        browser.close()
