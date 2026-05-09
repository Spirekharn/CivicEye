from selenium import webdriver
from selenium.webdriver.common.by import By

def test_login_firefox():
    driver = webdriver.Firefox()
    driver.get("http://127.0.0.1:8000/accounts/login/")

    driver.find_element(By.NAME, "username").send_keys("SSNS")
    driver.find_element(By.NAME, "password").send_keys("SSNSTCE")
    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    assert "dashboard" in driver.current_url.lower()

    driver.quit()