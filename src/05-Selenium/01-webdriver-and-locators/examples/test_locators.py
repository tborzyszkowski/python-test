from __future__ import annotations

import pytest
from selenium.webdriver.common.by import By


@pytest.mark.selenium
def test_form_can_be_located_with_id_name_css_and_xpath(browser, local_site):
    browser.get(f"{local_site}/login.html")

    username = browser.find_element(By.ID, "username")
    password = browser.find_element(By.NAME, "password")
    button = browser.find_element(By.CSS_SELECTOR, "#login-button")
    message = browser.find_element(By.XPATH, "//p[@role='status']")

    assert username.get_attribute("id") == "username"
    assert password.get_attribute("name") == "password"
    assert button.text == "Login"
    assert message.text == ""


@pytest.mark.selenium
def test_login_form_updates_visible_message(browser, local_site):
    browser.get(f"{local_site}/login.html")
    browser.find_element(By.ID, "username").send_keys("student")
    browser.find_element(By.NAME, "password").send_keys("secret")
    browser.find_element(By.CSS_SELECTOR, "#login-button").click()

    assert browser.find_element(By.XPATH, "//p[@role='status']").text == "Logged in"
