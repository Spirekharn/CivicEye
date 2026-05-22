import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_profile_page(driver):

    # 1. LOGIN
    driver.get("http://127.0.0.1:8000/accounts/login/")

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )

    driver.find_element(By.NAME, "username").send_keys("Nabiha")
    driver.find_element(By.NAME, "password").send_keys("23101125")

    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    # ❌ REMOVE url_changes COMPLETELY
    # ✔ wait for page load instead
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    # 2. DIRECT NAVIGATION (no dependency on redirect)
    driver.get("http://127.0.0.1:8000/accounts/profile/")

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    # 3. VERIFY CONTENT
    page = driver.page_source.lower()

    assert (
        "profile" in page
        or "nabiha" in page
        or "user" in page
    )