from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_super_admin_login(driver):

    # OPEN LOGIN PAGE
    driver.get("http://127.0.0.1:8000/accounts/login/")

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )

    username = driver.find_element(By.NAME, "username")
    password = driver.find_element(By.NAME, "password")

    username.clear()
    password.clear()

    # LOGIN AS SUPER ADMIN
    username.send_keys("SSNSTCE")
    password.send_keys("SSNSTCE")

    # SUBMIT LOGIN FORM
    driver.find_element(
        By.XPATH,
        "//button[@type='submit']"
    ).click()

    # WAIT FOR REDIRECT
    WebDriverWait(driver, 10).until(
        lambda d: "/login" not in d.current_url.lower()
    )

    current_url = driver.current_url.lower()
    page = driver.page_source.lower()

    print("Current URL:", current_url)

    # VERIFY SUCCESSFUL LOGIN
    assert (
        "login" not in current_url
        or "dashboard" in page
        or "super admin" in page
        or "civiceye" in page
    )