import pytest
from selenium.webdriver.common.by import By

def test_complaint_detail(driver):

    driver.get("http://127.0.0.1:8000/complaints/1/")

    assert "complaint" in driver.page_source.lower()