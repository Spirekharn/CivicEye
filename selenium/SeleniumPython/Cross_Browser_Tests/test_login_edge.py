from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_login_edge():
    driver = webdriver.Edge()
    driver.get("http://127.0.0.1:8000/accounts/login/")

    driver.find_element(By.NAME, "username").send_keys("SSNS")
    driver.find_element(By.NAME, "password").send_keys("SSNSTCE")
    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    # wait for redirect OR dashboard element
    WebDriverWait(driver, 10).until(
        lambda d: "dashboard" in d.current_url or "login" not in d.current_url
    )

    assert "dashboard" in driver.current_url.lower()

    driver.quit()