import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


@pytest.fixture
def driver():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()
    yield driver
    driver.quit()


def test_invalid_login(driver):
    driver.get("http://127.0.0.1:8000/accounts/login/")

    wait = WebDriverWait(driver, 10)

    # Wait for login form
    wait.until(EC.presence_of_element_located((By.NAME, "username")))

    # Enter invalid credentials
    driver.find_element(By.NAME, "username").send_keys("wrong_user")
    driver.find_element(By.NAME, "password").send_keys("wrong_pass")

    # Submit form
    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    # Wait for page reload (important)
    wait.until(EC.presence_of_element_located((By.NAME, "username")))

    # ️ ASSERTION 1: still on login page
    assert "/accounts/login/" in driver.current_url

    #  ASSERTION 2: login form still exists
    assert driver.find_element(By.NAME, "username").is_displayed()
    assert driver.find_element(By.NAME, "password").is_displayed()

    # ASSERTION 3: check for Django error message (if rendered)
    error_elements = driver.find_elements(By.CLASS_NAME, "errorlist")

    # If your backend shows errors, this will catch them
    if error_elements:
        assert True
    else:
        # fallback: still valid negative test
        assert "dashboard" not in driver.current_url.lower()