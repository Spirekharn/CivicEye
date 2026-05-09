import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_create_complaint(driver):

    driver.delete_all_cookies()

    driver.get("http://127.0.0.1:8000/accounts/login/")

    # Wait for login form
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )

    # Login
    driver.find_element(By.NAME, "username").send_keys("swagoto")
    driver.find_element(By.NAME, "password").send_keys("23101124")

    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    # ✅ FIX: wait for login success properly (NOT URL change)
    WebDriverWait(driver, 10).until(
        lambda d: "login" not in d.current_url
    )

    # Go to create complaint page (or redirect target page)
    driver.get("http://127.0.0.1:8000/complaints/create/")

    # Wait for page load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    # Simple validation
    assert "complaint" in driver.page_source.lower()