import pytest

def test_about_page(driver):

    driver.get("http://127.0.0.1:8000/about/")

    assert "about" in driver.page_source.lower()