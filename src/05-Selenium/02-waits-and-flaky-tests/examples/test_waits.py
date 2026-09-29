from __future__ import annotations

import pytest
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC  # noqa: N812
from selenium.webdriver.support.ui import WebDriverWait


@pytest.mark.selenium
def test_explicit_wait_observes_dynamic_result(browser, local_site):
    browser.get(f"{local_site}/dynamic.html")
    browser.find_element(By.ID, "load-button").click()

    result = WebDriverWait(browser, 3).until(
        EC.text_to_be_present_in_element((By.ID, "result"), "Loaded")
    )

    assert result is True
    assert browser.find_element(By.ID, "result").text == "Loaded"


@pytest.mark.selenium
def test_wait_can_return_clickable_element(browser, local_site):
    browser.get(f"{local_site}/dynamic.html")

    button = WebDriverWait(browser, 3).until(
        EC.element_to_be_clickable((By.ID, "load-button"))
    )

    assert button.get_attribute("id") == "load-button"


@pytest.mark.selenium
def test_timeout_is_observable_for_missing_condition(browser, local_site):
    browser.get(f"{local_site}/dynamic.html")

    with pytest.raises(TimeoutException):
        WebDriverWait(browser, 0.2).until(
            EC.text_to_be_present_in_element((By.ID, "result"), "Never appears")
        )
