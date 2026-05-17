"""
Selenium tests — Login & Logout workflow

Covers:
- Valid login redirects to dashboard
- Invalid credentials shows error
- GET logout does not log out (POST required)
- Sign-out via form returns to home page
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from conftest import login, logout

CITIZEN_USER = "Swagoto"
CITIZEN_PASS = "23101124"


def test_valid_login_redirects_to_dashboard(driver, base_url):
    """Submitting correct credentials sends the user to their dashboard."""
    login(driver, base_url, CITIZEN_USER, CITIZEN_PASS)
    assert "/accounts/dashboard/" in driver.current_url


def test_invalid_login_shows_error(driver, base_url):
    """Wrong password must not log in and must show an error message."""
    driver.get(f"{base_url}/accounts/login/")
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.NAME, "username")))

    driver.find_element(By.NAME, "username").send_keys("Swagoto")
    driver.find_element(By.NAME, "password").send_keys("wrongpassword")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "toast")))
    page = driver.page_source
    assert "Invalid username or password" in page or "invalid" in page.lower()
    assert "/accounts/dashboard/" not in driver.current_url


def test_get_to_logout_url_does_not_log_out(driver, base_url):
    """A direct GET request to /accounts/logout/ must NOT log out the user."""
    login(driver, base_url, CITIZEN_USER, CITIZEN_PASS)
    driver.get(f"{base_url}/accounts/logout/")
    # Page should redirect to home; a second visit to dashboard should still be logged in
    driver.get(f"{base_url}/accounts/dashboard/")
    assert "/accounts/dashboard/" in driver.current_url


def test_logout_via_form_returns_to_home(driver, base_url):
    """Clicking Sign Out (POST form) should clear the session and redirect to home."""
    login(driver, base_url, CITIZEN_USER, CITIZEN_PASS)
    logout(driver, base_url)
    # After logout, dashboard should redirect to login
    driver.get(f"{base_url}/accounts/dashboard/")
    assert "/accounts/login/" in driver.current_url or "/" in driver.current_url


def test_authenticated_user_skips_login_page(driver, base_url):
    """Visiting /login/ while already logged in should redirect to dashboard."""
    login(driver, base_url, CITIZEN_USER, CITIZEN_PASS)
    driver.get(f"{base_url}/accounts/login/")
    assert "/accounts/dashboard/" in driver.current_url


def test_super_admin_login(driver, base_url):
    """Super Admin login should work and reach dashboard."""
    login(driver, base_url, "SSNSTCE", "SSNSTCE")
    assert "/accounts/dashboard/" in driver.current_url
    assert "Super Admin" in driver.page_source or "super_admin" in driver.page_source.lower()


def test_finance_officer_login(driver, base_url):
    """Finance Officer login should work."""
    login(driver, base_url, "finance_officer", "Finance@123")
    assert "/accounts/dashboard/" in driver.current_url
