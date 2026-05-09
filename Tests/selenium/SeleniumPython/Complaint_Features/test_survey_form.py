import pytest
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_surveyor_queue(driver):

    # 🔍 Debug: confirm correct file is running
    print("RUNNING FROM:", os.path.abspath(__file__))

    # Step 1: Open login page
    driver.get("http://127.0.0.1:8000/accounts/login/")

    # Step 2: Wait for login form
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )

    # Step 3: Login (correct credentials)
    driver.find_element(By.NAME, "username").send_keys("Labib")
    driver.find_element(By.NAME, "password").send_keys("23101128")

    # IMPORTANT: use proper submit button selector
    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    # Step 4: Wait for login success (NO url_changes)
    WebDriverWait(driver, 10).until(
        lambda d: "login" not in d.current_url
    )

    # Step 5: Open surveyor queue page
    driver.get("http://127.0.0.1:8000/surveyor/queue/")

    # Step 6: Wait for page load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    # Step 7: Verify correct page loaded
    assert "queue" in driver.page_source.lower()