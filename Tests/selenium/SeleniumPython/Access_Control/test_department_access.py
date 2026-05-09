from selenium.webdriver.common.by import By

BASE_URL = "http://127.0.0.1:8000"

def login(driver, username, password):
    driver.get(f"{BASE_URL}/accounts/login/")
    driver.find_element(By.NAME, "username").send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.XPATH, "//button[@type='submit']").click()

def test_department_page_access(driver):
    login(driver, "SSNS", "SSNSTCE")
    driver.get(f"{BASE_URL}/departments/")
    assert "Department" in driver.page_source