import pytest
import time
from selenium.webdriver.common.by import By

@pytest.mark.django_db
def test_login_page(driver, live_server):
    driver.get(live_server.url + "/accounts/login/")
    time.sleep(2)

    assert "login" in driver.page_source.lower()


@pytest.mark.django_db
def test_login_function(driver, live_server):
    driver.get(live_server.url + "/accounts/login/")
    time.sleep(2)

    # Enter username & password
    driver.find_element(By.NAME, "username").send_keys("testuser")
    driver.find_element(By.NAME, "password").send_keys("1234")

    # Click login
    driver.find_element(By.TAG_NAME, "button").click()
    time.sleep(2)

    # Check if redirected
    assert "dashboard" in driver.current_url.lower()