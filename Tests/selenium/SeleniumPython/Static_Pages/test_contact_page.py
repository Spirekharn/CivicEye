import pytest

def test_contact_page(driver):

    driver.get("http://127.0.0.1:8000/accounts/contact/")

    assert "contact" in driver.page_source.lower()