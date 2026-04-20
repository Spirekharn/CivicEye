import pytest
import time
from selenium.webdriver.common.by import By

def login(driver, base_url):
    driver.get(base_url + "/accounts/login/")
    time.sleep(2)

    driver.find_element(By.NAME, "username").send_keys("testuser")
    driver.find_element(By.NAME, "password").send_keys("1234")

    driver.find_element(By.TAG_NAME, "button").click()
    time.sleep(2)


@pytest.mark.django_db
def test_create_complaint(driver, live_server):
    base_url = live_server.url

    login(driver, base_url)

    driver.get(base_url + "/complaints/")
    time.sleep(2)

    driver.find_element(By.NAME, "title").send_keys("Broken Road")
    driver.find_element(By.NAME, "description").send_keys("Very bad condition")

    driver.find_element(By.TAG_NAME, "button").click()
    time.sleep(2)

    assert "success" in driver.page_source.lower()