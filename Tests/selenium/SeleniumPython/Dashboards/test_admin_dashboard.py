import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_admin_dashboard(driver):

    driver.get("http://127.0.0.1:8000/accounts/login/")

    driver.find_element(By.NAME, "username").send_keys("SSNS")
    driver.find_element(By.NAME, "password").send_keys("SSNSTCE")

    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    # wait until login page disappears OR body loads
    WebDriverWait(driver, 10).until(
        lambda d: "login" not in d.current_url
    )

    print("AFTER LOGIN URL:", driver.current_url)

    assert "dashboard" in driver.page_source.lower()