from __future__ import annotations

import pytest


@pytest.mark.selenium
def test_browser_can_open_local_catalog_page(browser, local_site):
    browser.get(f"{local_site}/catalog.html")

    assert browser.title == "Catalog"
