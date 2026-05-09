import pytest

def test_privacy_page(driver):

    driver.get("http://127.0.0.1:8000/accounts/privacy/")

    assert "privacy" in driver.page_source.lower()