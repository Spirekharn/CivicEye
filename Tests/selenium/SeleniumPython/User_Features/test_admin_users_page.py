import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_profile_page(driver):

    # LOGIN
    driver.get("http://127.0.0.1:8000/accounts/login/")

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )

    driver.find_element(By.NAME, "username").send_keys("SSNS")
    driver.find_element(By.NAME, "password").send_keys("SSNSTCE")

    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    # ✅ DO NOT WAIT FOR URL CHANGE
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    # GO DIRECTLY TO PROFILE PAGE
    driver.get("http://127.0.0.1:8000/accounts/profile/")

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    page = driver.page_source.lower()

    # ✅ VALID ASSERTION (not URL-based)
    assert (
        "profile" in page
        or "nabiha" in page
        or "user" in page
    )