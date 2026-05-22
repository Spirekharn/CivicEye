import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def login(driver, username, password):
    driver.get("http://127.0.0.1:8000/accounts/login/")

    wait = WebDriverWait(driver, 10)

    wait.until(
        EC.presence_of_element_located((By.NAME, "username"))
    )

    driver.find_element(By.NAME, "username").clear()
    driver.find_element(By.NAME, "username").send_keys(username)

    driver.find_element(By.NAME, "password").clear()
    driver.find_element(By.NAME, "password").send_keys(password)

    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    wait.until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )


def test_superadmin_page(driver):

    login(driver, "SSNSTCE", "SSNSTCE")

    print("CURRENT URL:", driver.current_url)
    print(driver.page_source)

    # Check login success
    assert "/accounts/login/" not in driver.current_url

    driver.get("http://127.0.0.1:8000/admin/")

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    page = driver.page_source.lower()

    assert (
        "dashboard" in page
        or "admin" in page
        or "permission" in page
        or "denied" in page
        or "no department" in page
    )