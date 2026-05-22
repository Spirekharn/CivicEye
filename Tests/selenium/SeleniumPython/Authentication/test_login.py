from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_login(driver):

    citizens = [
        ("qq", "123456"),

        ("Nabiha", "23101125"),
    ]

    for username_value, password_value in citizens:

        driver.delete_all_cookies()

        driver.get("http://127.0.0.1:8000/accounts/login/")

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )

        driver.find_element(By.NAME, "username").send_keys(username_value)
        driver.find_element(By.NAME, "password").send_keys(password_value)

        driver.find_element(By.CSS_SELECTOR, "form button").click()

        # WAIT FOR DASHBOARD INSTEAD OF URL
        WebDriverWait(driver, 10).until(
            lambda d: "dashboard" in d.current_url.lower()
            or "dashboard" in d.page_source.lower()
        )

        print(f"Logged in as {username_value} → {driver.current_url}")

        assert (
            "dashboard" in driver.current_url.lower()
            or "citizen" in driver.page_source.lower()
            or "complaint" in driver.page_source.lower()
            or "tracking" in driver.page_source.lower()
        )