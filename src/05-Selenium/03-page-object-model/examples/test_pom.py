from __future__ import annotations

import pytest
from selenium_pages import CatalogPage, LoginPage


@pytest.mark.selenium
def test_login_page_object_hides_locators(browser, local_site):
    page = LoginPage(browser, local_site)

    page.open().login("student", "secret")

    assert page.message() == "Logged in"


@pytest.mark.selenium
def test_login_page_object_reports_invalid_form(browser, local_site):
    page = LoginPage(browser, local_site)

    page.open().login("", "")

    assert page.message() == "Missing credentials"


@pytest.mark.selenium
def test_catalog_page_adds_selected_product_and_waits_for_cart(browser, local_site):
    page = CatalogPage(browser, local_site).open()

    assert page.product_skus() == ["book-1", "book-2"]
    assert page.cart_count() == 0

    page.add_product("book-2")

    assert page.wait_for_cart_count(1) == 1


@pytest.mark.selenium
def test_catalog_page_reports_unknown_product(browser, local_site):
    page = CatalogPage(browser, local_site).open()

    with pytest.raises(LookupError, match="product not found"):
        page.add_product("missing")

    assert page.cart_count() == 0
