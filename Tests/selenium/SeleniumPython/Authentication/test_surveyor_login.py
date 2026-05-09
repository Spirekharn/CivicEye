from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def test_surveyor_login(driver):

    # clear cookies
    driver.delete_all_cookies()

    # open login page
    driver.get("http://127.0.0.1:8000/accounts/login/")

    # wait for login form
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )

    # enter surveyor credentials
    driver.find_element(By.NAME, "username").send_keys("Labib")
    driver.find_element(By.NAME, "password").send_keys("23101128")

    # click login button
    driver.find_element(By.CSS_SELECTOR, "form button").click()

    # wait for dashboard redirect
    WebDriverWait(driver, 10).until(
        EC.url_contains("/accounts/dashboard/")
    )

    # print current URL
    print("Current URL:", driver.current_url)

    # verify successful login
    assert "dashboard" in driver.current_url