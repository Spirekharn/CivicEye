"""
Selenium test configuration for CivicEye.

Assumes the Django development server is running at http://127.0.0.1:8000
with seed data already loaded:
    python manage.py seed_data
    python manage.py create_demo_data  (optional, for richer data)
    python manage.py runserver

Run tests with:
    pytest selenium/SeleniumPython/ -v
    pytest selenium/SeleniumPython/ -v --screenshots  (saves screenshots on failure)

Chrome must be installed. chromedriver is managed automatically.
"""

import os
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

try:
    from webdriver_manager.chrome import ChromeDriverManager
    _USE_WDM = True
except ImportError:
    _USE_WDM = False


BASE_URL = os.environ.get("CIVICEYE_TEST_URL", "http://127.0.0.1:8000")


def pytest_addoption(parser):
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="Run Chrome in headless mode (no browser window)"
    )
    parser.addoption(
        "--screenshots",
        action="store_true",
        default=False,
        help="Save screenshot on test failure"
    )


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture
def driver(request):
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-extensions")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    if request.config.getoption("--headless"):
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")

    if _USE_WDM:
        d = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
    else:
        # Falls back to PATH-installed chromedriver
        d = webdriver.Chrome(options=options)

    d.implicitly_wait(2)

    yield d

    if request.config.getoption("--screenshots") and request.node.rep_call.failed:
        screenshot_dir = os.path.join(os.path.dirname(__file__), "screenshots")
        os.makedirs(screenshot_dir, exist_ok=True)

        name = request.node.name.replace("/", "_").replace(":", "_")
        path = os.path.join(screenshot_dir, f"{name}.png")

        d.save_screenshot(path)
        print(f"\nScreenshot saved: {path}")

    d.quit()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


# Shared login helper
def login(driver, base_url, username, password):
    """Navigate to login page and authenticate."""
    driver.get(f"{base_url}/accounts/login/")

    wait = WebDriverWait(driver, 10)

    wait.until(
        EC.presence_of_element_located((By.NAME, "username"))
    )

    driver.find_element(By.NAME, "username").clear()
    driver.find_element(By.NAME, "username").send_keys(username)

    driver.find_element(By.NAME, "password").clear()
    driver.find_element(By.NAME, "password").send_keys(password)

    driver.find_element(
        By.CSS_SELECTOR,
        "button[type='submit']"
    ).click()

    wait.until(
        EC.url_contains("/accounts/dashboard/")
    )


def logout(driver, base_url):
    """Submit the sign-out form."""
    driver.get(f"{base_url}/accounts/dashboard/")

    wait = WebDriverWait(driver, 10)

    btn = wait.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "form[action*='logout'] button")
        )
    )

    btn.click()

    wait.until(
        EC.url_contains("/")
    )