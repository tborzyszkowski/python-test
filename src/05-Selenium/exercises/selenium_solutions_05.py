from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait


class CatalogPage:
    PRODUCT = (By.CSS_SELECTOR, "article.product")
    ADD_BUTTONS = (By.CSS_SELECTOR, "article.product button.add")

    def __init__(self, driver: WebDriver, base_url: str) -> None:
        self.driver = driver
        self.base_url = base_url

    def open(self) -> CatalogPage:
        self.driver.get(f"{self.base_url}/catalog.html")
        return self

    def product_count(self) -> int:
        return len(self.driver.find_elements(*self.PRODUCT))

    def wait_for_product_count(self, expected: int) -> bool:
        return WebDriverWait(self.driver, 3).until(
            lambda driver: len(driver.find_elements(*self.PRODUCT)) == expected
        )
