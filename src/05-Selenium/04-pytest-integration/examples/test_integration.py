from __future__ import annotations

import pytest
from selenium.webdriver.common.by import By


@pytest.mark.selenium
def test_failure_fixture_example_can_use_browser(browser, local_site):
    browser.get(f"{local_site}/catalog.html")
    products = browser.find_elements(By.CSS_SELECTOR, "article.product")

    assert len(products) == 2
