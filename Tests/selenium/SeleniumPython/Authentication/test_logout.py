import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_logout(driver):
    driver.delete_all_cookies()

    # ---------------- LOGIN ----------------
    driver.get("http://127.0.0.1:8000/accounts/login/")

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )

    driver.find_element(By.NAME, "username").send_keys("Nabiha")
    driver.find_element(By.NAME, "password").send_keys("23101125")
    driver.find_element(By.CSS_SELECTOR, "form button").click()

    # wait for dashboard
    WebDriverWait(driver, 10).until(
        lambda d: "/dashboard" in d.current_url
    )

    print("Logged in URL:", driver.current_url)

    # ---------------- LOGOUT ----------------
    logout_form = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'form[action="/accounts/logout/"]')
        )
    )

    # IMPORTANT: submit instead of clicking disabled button
    driver.execute_script("arguments[0].submit();", logout_form)

    # ---------------- WAIT FOR REDIRECT ----------------
    WebDriverWait(driver, 10).until(
        lambda d: "/dashboard" not in d.current_url
    )

    print("After logout URL:", driver.current_url)

    # ---------------- ASSERTIONS ----------------
    assert "/dashboard" not in driver.current_url
    assert "sign out" not in driver.page_source.lower()