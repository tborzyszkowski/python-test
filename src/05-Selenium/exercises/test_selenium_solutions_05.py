import pytest
from selenium_solutions_05 import CatalogPage


@pytest.mark.selenium
def test_catalog_page_solution(browser, local_site):
    page = CatalogPage(browser, local_site).open()
    assert page.product_count() == 2
    assert page.wait_for_product_count(2) is True
