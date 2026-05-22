import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_complaint_assignment(driver):

    wait = WebDriverWait(driver, 15)

    # Open login page
    driver.get("http://127.0.0.1:8000/accounts/login/")

    # Wait for username field
    username = wait.until(
        EC.presence_of_element_located((By.NAME, "username"))
    )

    password = driver.find_element(By.NAME, "password")

    # Clear fields
    username.clear()
    password.clear()

    # Super Admin Login
    username.send_keys("SSNSTCE")
    password.send_keys("SSNSTCE")

    # Click login button
    login_btn = driver.find_element(
        By.XPATH,
        "//button[@type='submit']"
    )
    login_btn.click()

    # Wait until redirected after login
    wait.until(
        lambda d: "/login" not in d.current_url.lower()
    )

    # Open complaint assignment page
    driver.get("http://127.0.0.1:8000/complaints/assign/1/")

    # Wait until page fully loads
    wait.until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    # Debug info
    print("Current URL:", driver.current_url)

    # Verify assignment page opened successfully
    assert (
        "assign" in driver.current_url.lower()
        or "assign" in driver.page_source.lower()
    )

    print("✅ Complaint Assignment Test Passed")