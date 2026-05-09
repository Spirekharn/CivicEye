import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_tech_dashboard(driver):

    driver.delete_all_cookies()

    driver.get("http://127.0.0.1:8000/accounts/login/")

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )

    driver.find_element(By.NAME, "username").send_keys("sujan")
    driver.find_element(By.NAME, "password").send_keys("23101120")

    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    # wait login finish (NOT URL)
    WebDriverWait(driver, 10).until(
        lambda d: "login" not in d.current_url
    )

    print("AFTER LOGIN URL:", driver.current_url)

    # check actual page content
    assert "tech" in driver.page_source.lower() or \
           "dashboard" in driver.page_source.lower()