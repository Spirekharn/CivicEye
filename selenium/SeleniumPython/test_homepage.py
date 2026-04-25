import time
from selenium.webdriver.common.by import By

def test_homepage_title(driver, live_server):
    driver.get(live_server.url + "/accounts/login/")
    time.sleep(2)

    assert "CivicEye" in driver.title


def test_navigation_to_login(driver, live_server):
    driver.get(live_server.url + "/accounts/dashboard/")
    time.sleep(2)

    # Click login link
    driver.find_element(By.LINK_TEXT, "Login").click()
    time.sleep(2)

    assert "login" in driver.current_url.lower()