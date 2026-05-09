from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def test_logout(driver):

    # clear cookies
    driver.delete_all_cookies()

    # open login page
    driver.get("http://127.0.0.1:8000/accounts/login/")

    # wait for login form
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )

    # enter credentials
    driver.find_element(By.NAME, "username").send_keys("qq")
    driver.find_element(By.NAME, "password").send_keys("123456")

    # click login
    driver.find_element(By.CSS_SELECTOR, "form button").click()

    # wait for dashboard
    WebDriverWait(driver, 10).until(
        EC.url_contains("/accounts/dashboard/")
    )

    print("Logged in URL:", driver.current_url)

    # logout
    driver.get("http://127.0.0.1:8000/accounts/logout/")

    # wait after logout
    time.sleep(3)

    print("After logout URL:", driver.current_url)

    # verify logout success
    assert driver.current_url == "http://127.0.0.1:8000/"