from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_login_chrome():
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 15)

    try:
        driver.get("http://127.0.0.1:8000/accounts/login/")

        username = wait.until(
            EC.presence_of_element_located((By.NAME, "username"))
        )

        password = driver.find_element(By.NAME, "password")

        username.clear()
        password.clear()

        # Super Admin Login
        username.send_keys("SSNSTCE")
        password.send_keys("SSNSTCE")

        driver.find_element(
            By.XPATH,
            "//button[@type='submit']"
        ).click()

        # Wait until redirected
        wait.until(
            lambda d: "/login" not in d.current_url.lower()
        )

        assert "/login" not in driver.current_url.lower()

        print("✅ Chrome Login Successful")

    finally:
        driver.quit()