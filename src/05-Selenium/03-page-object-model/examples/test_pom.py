from __future__ import annotations

import pytest
from selenium_pages import LoginPage


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
