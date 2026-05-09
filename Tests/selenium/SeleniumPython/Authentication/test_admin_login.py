from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def test_admin_login(driver):

    driver.get("http://127.0.0.1:8000/accounts/login/")

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )

    username = driver.find_element(By.NAME, "username")
    password = driver.find_element(By.NAME, "password")

    username.clear()
    password.clear()

    username.send_keys("SSNS")
    password.send_keys("SSNSTCE")

    # safer button selection
    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    time.sleep(5)

    print("Current URL:", driver.current_url)
    print("Page Source:")
    print(driver.page_source)

    assert "login" not in driver.current_url