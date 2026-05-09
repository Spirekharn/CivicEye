import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_surveyor_queue(driver):

    driver.get("http://127.0.0.1:8000/accounts/login/")

    # wait for login form
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )

    # login
    driver.find_element(By.NAME, "username").send_keys("Labib")
    driver.find_element(By.NAME, "password").send_keys("23101128")

    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    # ✅ DO NOT use url_changes
    WebDriverWait(driver, 10).until(
        lambda d: "login" not in d.current_url
    )

    # open queue page
    driver.get("http://127.0.0.1:8000/surveyor/queue/")

    # wait page load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    assert "queue" in driver.page_source.lower()