import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_worker_dashboard(driver):

    driver.delete_all_cookies()

    driver.get("http://127.0.0.1:8000/accounts/login/")

    driver.find_element(By.NAME, "username").send_keys("Lamiya")
    driver.find_element(By.NAME, "password").send_keys("23101132")

    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    # wait login completion
    WebDriverWait(driver, 10).until(
        lambda d: "login" not in d.current_url
    )

    print("AFTER LOGIN URL:", driver.current_url)

    # check real worker page content
    assert "worker" in driver.page_source.lower() or \
           "task" in driver.page_source.lower()