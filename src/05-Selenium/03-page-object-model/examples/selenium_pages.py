from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait


class LoginPage:
    USERNAME = (By.ID, "username")
    PASSWORD = (By.NAME, "password")
    SUBMIT = (By.CSS_SELECTOR, "#login-button")
    MESSAGE = (By.XPATH, "//p[@role='status']")

    def __init__(self, driver: WebDriver, base_url: str) -> None:
        self.driver = driver
        self.base_url = base_url

    def open(self) -> LoginPage:
        self.driver.get(f"{self.base_url}/login.html")
        return self

    def login(self, username: str, password: str) -> LoginPage:
        self.driver.find_element(*self.USERNAME).send_keys(username)
        self.driver.find_element(*self.PASSWORD).send_keys(password)
        self.driver.find_element(*self.SUBMIT).click()
        return self

    def message(self) -> str:
        return self.driver.find_element(*self.MESSAGE).text


class CatalogPage:
    PRODUCTS = (By.CSS_SELECTOR, "article.product")
    ADD_BUTTON = (By.CSS_SELECTOR, "button.add")
    CART_COUNT = (By.ID, "cart-count")

    def __init__(self, driver: WebDriver, base_url: str) -> None:
        self.driver = driver
        self.base_url = base_url

    def open(self) -> CatalogPage:
        self.driver.get(f"{self.base_url}/catalog.html")
        return self

    def product_skus(self) -> list[str]:
        return [
            sku
            for product in self.driver.find_elements(*self.PRODUCTS)
            if (sku := product.get_attribute("data-sku"))
        ]

    def _product(self, sku: str) -> WebElement:
        for product in self.driver.find_elements(*self.PRODUCTS):
            if product.get_attribute("data-sku") == sku:
                return product
        raise LookupError(f"product not found: {sku}")

    def add_product(self, sku: str) -> CatalogPage:
        self._product(sku).find_element(*self.ADD_BUTTON).click()
        return self

    def cart_count(self) -> int:
        return int(self.driver.find_element(*self.CART_COUNT).text)

    def wait_for_cart_count(self, expected: int, timeout: float = 3) -> int:
        def count_reached(driver: WebDriver) -> int | bool:
            count = int(driver.find_element(*self.CART_COUNT).text)
            return count if count >= expected else False

        return WebDriverWait(self.driver, timeout).until(count_reached)
