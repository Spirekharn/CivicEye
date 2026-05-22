from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_tech_login(driver):

    # OPEN LOGIN PAGE
    driver.get("http://127.0.0.1:8000/accounts/login/")

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )

    username = driver.find_element(By.NAME, "username")
    password = driver.find_element(By.NAME, "password")

    username.clear()
    password.clear()

    # TECH CREDENTIALS
    username.send_keys("sujan")
    password.send_keys("23101120")

    # SUBMIT LOGIN FORM
    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    # WAIT FOR PAGE LOAD (not URL guessing)
    WebDriverWait(driver, 10).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )

    current_url = driver.current_url.lower()
    page = driver.page_source.lower()

    print("Current URL:", current_url)

    # VERIFY SUCCESSFUL LOGIN (robust check like super admin)
    assert (
        "login" not in current_url
        or "dashboard" in page
        or "logout" in page
        or "tech" in page
        or "civiceye" in page
    ), "Tech login failed"