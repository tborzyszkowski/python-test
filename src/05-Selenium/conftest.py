"""Wspolne fixture'y Selenium: lokalny serwer, przegladarka i screenshoty."""

from __future__ import annotations

import os
import threading
from collections.abc import Iterator
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.common.exceptions import WebDriverException

MODULE_ROOT = Path(__file__).resolve().parent
WEB_ROOT = MODULE_ROOT / "web"
ARTIFACTS = MODULE_ROOT / "artifacts"


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        pass


@pytest.fixture(scope="session")
def local_site() -> Iterator[str]:
    def handler(*args, **kwargs):
        return QuietHandler(*args, directory=str(WEB_ROOT), **kwargs)

    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        thread.join(timeout=2)


@pytest.fixture
def browser(request: pytest.FixtureRequest, local_site: str):
    browser_name = os.getenv("SELENIUM_BROWSER", "chrome").lower()
    if browser_name == "firefox":
        options = webdriver.FirefoxOptions()
        options.add_argument("-headless")

        def factory():
            return webdriver.Firefox(options=options)

    else:
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1280,900")
        options.add_argument("--disable-gpu")

        def factory():
            return webdriver.Chrome(options=options)

    try:
        driver = factory()
    except WebDriverException as exc:
        pytest.skip(f"Brak gotowej przegladarki/sterownika Selenium: {exc}")

    driver.implicitly_wait(0)
    try:
        yield driver
    finally:
        report = getattr(request.node, "rep_call", None)
        if report is not None and report.failed:
            ARTIFACTS.mkdir(exist_ok=True)
            safe_name = request.node.nodeid.replace("/", "_").replace("\\", "_").replace(":", "_")
            driver.save_screenshot(str(ARTIFACTS / f"{safe_name}.png"))
        driver.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[object]):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)
