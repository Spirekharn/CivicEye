import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def login(driver, username, password):
    driver.get("http://127.0.0.1:8000/accounts/login/")

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )

    driver.find_element(By.NAME, "username").clear()
    driver.find_element(By.NAME, "username").send_keys(username)

    driver.find_element(By.NAME, "password").clear()
    driver.find_element(By.NAME, "password").send_keys(password)

    driver.find_element(By.XPATH, "//button[@type='submit']").click()


def test_worker_access_control(driver):
    # WORKER LOGIN (use your worker credentials)
    login(driver, "Lamiya", "23101132")

    # Try accessing a worker-specific page
    driver.get("http://127.0.0.1:8000/worker/tasks/")

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    page = driver.page_source.lower()

    # worker should be able to see tasks
    assert (
        "task" in page
        or "tasks" in page
        or "worker" in driver.current_url.lower()
    )