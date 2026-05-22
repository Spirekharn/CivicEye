import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_citizen_dashboard(driver):

    driver.delete_all_cookies()

    driver.get("http://127.0.0.1:8000/accounts/login/")

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )

    driver.find_element(By.NAME, "username").send_keys("Nabiha")
    driver.find_element(By.NAME, "password").send_keys("23101125")

    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    # ✅ WAIT FOR LOGIN SUCCESS (NOT URL CHANGE)
    WebDriverWait(driver, 10).until(
        lambda d: "login" not in d.current_url
    )

    print("AFTER LOGIN URL:", driver.current_url)

    assert "dashboard" in driver.page_source.lower()