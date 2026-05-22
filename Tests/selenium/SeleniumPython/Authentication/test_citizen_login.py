from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_citizen_login(driver):

    citizens = [
        ("Swagoto", "23101124"),
        ("Nabiha", "23101125"),
    ]

    for username_value, password_value in citizens:

        # 🔥 HARD RESET SESSION
        driver.delete_all_cookies()

        # OPEN LOGIN PAGE
        driver.get("http://127.0.0.1:8000/accounts/login/")

        # WAIT FOR LOGIN FORM
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )

        username = driver.find_element(By.NAME, "username")
        password = driver.find_element(By.NAME, "password")

        username.clear()
        password.clear()

        username.send_keys(username_value)
        password.send_keys(password_value)

        driver.find_element(By.CSS_SELECTOR, "form button").click()

        WebDriverWait(driver, 10).until(
            lambda d: "/login" not in d.current_url.lower()
        )

        print(f"Logged in as {username_value} → {driver.current_url}")

        assert (
            "login" not in driver.current_url.lower()
            and (
                "citizen" in driver.page_source.lower()
                or "dashboard" in driver.page_source.lower()
                or "complaint" in driver.page_source.lower()
                or "tracking" in driver.page_source.lower()
            )
        )