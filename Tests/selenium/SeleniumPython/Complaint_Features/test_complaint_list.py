import pytest
from selenium.webdriver.common.by import By

def test_complaint_list(driver):

    driver.get("http://127.0.0.1:8000/complaints/")

    assert "complaint" in driver.page_source.lower()