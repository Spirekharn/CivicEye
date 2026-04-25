import pytest
import time
from selenium.webdriver.common.by import By

@pytest.mark.django_db
def test_account_page_load(driver, live_server):
    driver.get(live_server.url + "/accounts/login/")
    time.sleep(2)

    assert "login" in driver.page_source.lower()


@pytest.mark.django_db
def test_dashboard_access(driver, live_server):
    driver.get(live_server.url + "/accounts/dashboard/")
    time.sleep(2)

    # Just check page opens
    assert driver.current_url.endswith("/accounts/dashboard/")