import pytest
from selenium.webdriver.common.by import By

def test_transfer_review(driver):

    driver.get("http://127.0.0.1:8000/transfers/")

    assert "transfer" in driver.page_source.lower()