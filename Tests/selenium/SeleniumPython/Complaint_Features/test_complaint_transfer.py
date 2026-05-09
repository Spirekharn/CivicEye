import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_complaint_transfer(driver):

    driver.get("http://127.0.0.1:8000/accounts/login/")

    # Login
    driver.find_element(By.NAME, "username").send_keys("sujan")
    driver.find_element(By.NAME, "password").send_keys("23101120")

    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    # Wait for successful login (DON'T use URL check)
    WebDriverWait(driver, 10).until(
        lambda d: "login" not in d.current_url
    )

    # Open transfer page
    driver.get("http://127.0.0.1:8000/complaints/transfer/1/")

    # Wait for page load properly
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    # Final assertion
    assert "transfer" in driver.page_source.lower()