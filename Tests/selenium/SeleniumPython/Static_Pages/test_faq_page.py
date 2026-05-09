import pytest

def test_faq_page(driver):

    driver.get("http://127.0.0.1:8000/accounts/faq/")

    assert "faq" in driver.page_source.lower()
    