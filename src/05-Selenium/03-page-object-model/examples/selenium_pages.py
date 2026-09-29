from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver


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
