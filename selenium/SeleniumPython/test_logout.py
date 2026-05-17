"""
Selenium tests — Logout & Theme toggle behaviour

Covers:
- Sign-out via POST form
- Theme toggle button visible for logged-in users
- Guest theme button visible on public pages
- Theme persists across page loads (via localStorage for guests)
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from conftest import login, logout


def test_sign_out_clears_session(driver, base_url):
    """Sign-out should invalidate the session."""
    login(driver, base_url, "Swagoto", "23101124")

    wait = WebDriverWait(driver, 10)
    sign_out_btn = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "form[action*='logout'] button"))
    )
    sign_out_btn.click()

    wait.until(lambda d: d.current_url != f"{base_url}/accounts/dashboard/")
    driver.get(f"{base_url}/accounts/dashboard/")
    assert "/accounts/login/" in driver.current_url


def test_sign_out_redirects_to_home(driver, base_url):
    """After signing out, the user should land on the home page."""
    login(driver, base_url, "Swagoto", "23101124")
    logout(driver, base_url)
    # Should be on home or login, not dashboard
    assert "/accounts/dashboard/" not in driver.current_url


def test_theme_toggle_visible_when_logged_in(driver, base_url):
    """Logged-in users should see the theme toggle button."""
    login(driver, base_url, "Swagoto", "23101124")
    driver.get(f"{base_url}/accounts/dashboard/")
    wait = WebDriverWait(driver, 10)
    btn = wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "button.icon-btn[title='Toggle theme']")
    ))
    assert btn is not None


def test_guest_theme_button_visible_on_home(driver, base_url):
    """Unauthenticated users should see a theme toggle button on the home page."""
    driver.get(f"{base_url}/")
    wait = WebDriverWait(driver, 10)
    btn = wait.until(EC.presence_of_element_located(
        (By.ID, "guest-theme-btn")
    ))
    assert btn is not None


def test_guest_dark_theme_persists_across_pages(driver, base_url):
    """
    Switching to dark mode as a guest should persist the preference
    (stored in localStorage) when navigating to another public page.
    """
    driver.get(f"{base_url}/")
    # Set dark theme via localStorage directly
    driver.execute_script("localStorage.setItem('guest_theme', 'dark');")
    driver.refresh()
    theme = driver.execute_script("return document.documentElement.getAttribute('data-theme');")
    assert theme == "dark"

    # Navigate to community page and confirm theme still applies
    driver.get(f"{base_url}/complaints/community/")
    theme_after_nav = driver.execute_script(
        "return document.documentElement.getAttribute('data-theme');"
    )
    assert theme_after_nav == "dark"

    # Clean up
    driver.execute_script("localStorage.removeItem('guest_theme');")
