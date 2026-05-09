import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_login_chrome():
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 10)

    driver.get("http://127.0.0.1:8000/accounts/login/")

    # login
    driver.find_element(By.NAME, "username").send_keys("SSNS")
    driver.find_element(By.NAME, "password").send_keys("SSNSTCE")
    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    # ✅ WAIT for either redirect OR dashboard element
    wait.until(
        lambda d: "/dashboard" in d.current_url.lower()
        or "dashboard" in d.page_source.lower()
    )

    current_url = driver.current_url.lower()

    assert (
        "dashboard" in current_url
        or "dashboard" in driver.page_source.lower()
    )

    driver.quit()