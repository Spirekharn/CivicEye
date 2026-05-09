import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_surveyor_dashboard(driver):

    driver.delete_all_cookies()

    driver.get("http://127.0.0.1:8000/accounts/login/")

    driver.find_element(By.NAME, "username").send_keys("Labib")
    driver.find_element(By.NAME, "password").send_keys("23101128")

    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    # wait for login completion (NOT URL)
    WebDriverWait(driver, 10).until(
        lambda d: "login" not in d.current_url
    )

    print("AFTER LOGIN:", driver.current_url)

    # check actual UI content instead of URL
    assert "surveyor" in driver.page_source.lower() or \
           "queue" in driver.page_source.lower()