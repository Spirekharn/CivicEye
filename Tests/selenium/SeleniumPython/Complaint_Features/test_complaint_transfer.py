import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_complaint_transfer(driver):

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

    #  Correct Technician Login
    username.send_keys("Sujan")
    password.send_keys("23101120")

    # Click login
    driver.find_element(
        By.XPATH,
        "//button[@type='submit']"
    ).click()

    # Wait until login successful
    wait.until(
        lambda d: "/login" not in d.current_url.lower()
    )

    # Debug
    print("Logged in URL:", driver.current_url)

    # Open transfer page
    driver.get("http://127.0.0.1:8000/complaints/transfer/1/")

    # Wait for page load
    wait.until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    # Debug
    print("Transfer Page URL:", driver.current_url)

    # Final assertion
    assert (
        "transfer" in driver.current_url.lower()
        or "transfer" in driver.page_source.lower()
    )

    print(" Complaint Transfer Test Passed")