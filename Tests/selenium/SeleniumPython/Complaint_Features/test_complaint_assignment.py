import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_complaint_assignment(driver):

    driver.get("http://127.0.0.1:8000/accounts/login/")

    # Login
    driver.find_element(By.NAME, "username").send_keys("SSNS")
    driver.find_element(By.NAME, "password").send_keys("SSNSTCE")

    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    # Wait for successful login (better than URL check)
    WebDriverWait(driver, 10).until(
        lambda d: "login" not in d.current_url
    )

    # Now go to assignment page
    driver.get("http://127.0.0.1:8000/complaints/assign/1/")

    # Wait for page load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    assert "assign" in driver.page_source.lower()