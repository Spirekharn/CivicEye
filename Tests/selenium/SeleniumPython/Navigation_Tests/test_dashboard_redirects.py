from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_sidebar_navigation(driver):
    driver.get("http://127.0.0.1:8000/accounts/login/")

    driver.find_element(By.NAME, "username").send_keys("SSNSTCE")
    driver.find_element(By.NAME, "password").send_keys("SSNSTCE")

    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    # WAIT FOR DASHBOARD UI (NOT URL)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "nav"))
    )

    # FINAL ASSERTION
    assert driver.find_element(By.TAG_NAME, "nav").is_displayed()