import pytest

def test_home_page(driver):

    driver.get("http://127.0.0.1:8000/")

    assert "civiceye" in driver.page_source.lower()