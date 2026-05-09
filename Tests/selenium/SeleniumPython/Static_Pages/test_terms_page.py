import pytest

def test_terms_page(driver):

    driver.get("http://127.0.0.1:8000/accounts/terms/")

    assert "terms" in driver.page_source.lower()