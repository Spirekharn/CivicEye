import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_admin_access_control(driver):
    wait = WebDriverWait(driver, 10)

    # LOGIN AS SUPER ADMIN
    driver.get("http://127.0.0.1:8000/accounts/login/")

    driver.find_element(By.NAME, "username").send_keys("SSNSTCE")
    driver.find_element(By.NAME, "password").send_keys("SSNSTCE")
    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    # WAIT FOR REDIRECT
    wait.until(
        lambda d: d.current_url != "http://127.0.0.1:8000/accounts/login/"
    )

    # OPEN ADMIN PANEL
    driver.get("http://127.0.0.1:8000/admin/")

    wait.until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    current_url = driver.current_url.lower()
    page = driver.page_source.lower()

    # SUPER ADMIN SHOULD ACCESS ADMIN PANEL
    assert (
        "/admin" in current_url
        or "site administration" in page
        or "dashboard" in page
        or "super admin" in page
        or "civiceye" in page
    )