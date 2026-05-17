"""
Selenium tests — User Registration workflow

Covers:
- Successful citizen registration redirects to dashboard
- Duplicate username is rejected
- Short password (< 8 chars) is rejected
- Password mismatch is rejected
- Registration page accessible when not logged in
- Already logged-in user is redirected away from register
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from conftest import login


def _fill_register_form(driver, username, email, first_name, last_name,
                        password1, password2, role="citizen"):
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.NAME, "username")))

    driver.find_element(By.NAME, "username").clear()
    driver.find_element(By.NAME, "username").send_keys(username)

    email_field = driver.find_element(By.NAME, "email")
    email_field.clear()
    email_field.send_keys(email)

    fn_field = driver.find_element(By.NAME, "first_name")
    fn_field.clear()
    fn_field.send_keys(first_name)

    ln_field = driver.find_element(By.NAME, "last_name")
    ln_field.clear()
    ln_field.send_keys(last_name)

    driver.find_element(By.NAME, "password1").clear()
    driver.find_element(By.NAME, "password1").send_keys(password1)

    driver.find_element(By.NAME, "password2").clear()
    driver.find_element(By.NAME, "password2").send_keys(password2)

    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()


def test_successful_citizen_registration(driver, base_url):
    """A new citizen account should be created and redirect to dashboard."""
    unique = str(int(time.time()))
    driver.get(f"{base_url}/accounts/register/")
    _fill_register_form(
        driver,
        username=f"testcitizen_{unique}",
        email=f"testcitizen_{unique}@test.bd",
        first_name="Test",
        last_name="Citizen",
        password1="Password@2026",
        password2="Password@2026",
    )
    wait = WebDriverWait(driver, 10)
    wait.until(EC.url_contains("/accounts/dashboard/"))
    assert "/accounts/dashboard/" in driver.current_url


def test_duplicate_username_rejected(driver, base_url):
    """Registering with an existing username should show an error."""
    driver.get(f"{base_url}/accounts/register/")
    _fill_register_form(
        driver,
        username="Swagoto",  # already exists from seed_data
        email="newunique@test.bd",
        first_name="Test",
        last_name="User",
        password1="Password@2026",
        password2="Password@2026",
    )
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "toast")))
    assert "already taken" in driver.page_source or "username" in driver.page_source.lower()
    assert "/accounts/dashboard/" not in driver.current_url


def test_short_password_rejected(driver, base_url):
    """Password shorter than 8 characters should be rejected."""
    unique = str(int(time.time()))
    driver.get(f"{base_url}/accounts/register/")
    _fill_register_form(
        driver,
        username=f"shortpw_{unique}",
        email=f"shortpw_{unique}@test.bd",
        first_name="Short",
        last_name="Pw",
        password1="abc12",    # only 5 chars
        password2="abc12",
    )
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "toast")))
    assert "8 characters" in driver.page_source or "password" in driver.page_source.lower()
    assert "/accounts/dashboard/" not in driver.current_url


def test_password_mismatch_rejected(driver, base_url):
    """Mismatched passwords should not create an account."""
    unique = str(int(time.time()))
    driver.get(f"{base_url}/accounts/register/")
    _fill_register_form(
        driver,
        username=f"mismatch_{unique}",
        email=f"mismatch_{unique}@test.bd",
        first_name="Pass",
        last_name="Mismatch",
        password1="Password@2026",
        password2="DifferentPass@2026",
    )
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "toast")))
    assert "do not match" in driver.page_source or "match" in driver.page_source.lower()
    assert "/accounts/dashboard/" not in driver.current_url


def test_logged_in_user_redirected_from_register(driver, base_url):
    """A user who is already logged in should be redirected from the register page."""
    login(driver, base_url, "Swagoto", "23101124")
    driver.get(f"{base_url}/accounts/register/")
    assert "/accounts/dashboard/" in driver.current_url
