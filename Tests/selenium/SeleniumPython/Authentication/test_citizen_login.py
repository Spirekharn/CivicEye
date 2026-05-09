from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def test_citizen_login(driver):

    # open login page
    driver.get("http://127.0.0.1:8000/accounts/login/")

    # wait for username field
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )

    # find fields
    username = driver.find_element(By.NAME, "username")
    password = driver.find_element(By.NAME, "password")

    # clear fields
    username.clear()
    password.clear()

    # enter credentials
    username.send_keys("nabiha")
    password.send_keys("nnnnnn")

    # click login button
    driver.find_element(By.CSS_SELECTOR, "form button").click()

    # wait after login attempt
    time.sleep(5)

    # debug info
    print("Current URL:", driver.current_url)
    print(driver.page_source)

    # verify login success
    assert "login" not in driver.current_url