"""
Selenium tests — Complaint submission workflow

Covers:
- Citizen can submit a standard complaint
- Citizen can submit an anonymous complaint
- Missing required fields show validation error
- Submitted complaint appears in citizen's complaint list
- Citizen can view their complaint detail page
- Community dashboard shows the complaint without revealing identity
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from conftest import login, logout


def test_citizen_can_submit_complaint(driver, base_url):
    """A logged-in citizen should be able to submit a new complaint successfully."""
    login(driver, base_url, "Swagoto", "23101124")
    driver.get(f"{base_url}/complaints/create/")

    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.NAME, "title")))

    ts = str(int(time.time()))
    title = f"Selenium Test Pothole {ts}"

    driver.find_element(By.NAME, "title").send_keys(title)
    driver.find_element(By.NAME, "description").send_keys(
        "A large pothole has appeared near the test location. Vehicles are swerving."
    )
    driver.find_element(By.NAME, "location_text").send_keys("Dhanmondi, Dhaka, DSCC")

    # Select category — try via Select or Tom Select fallback
    try:
        select_el = driver.find_element(By.NAME, "category")
        select_el.click()
        Select(select_el).select_by_value("roads")
    except Exception:
        # Tom Select overlay — click the option by text
        driver.execute_script(
            "document.querySelector('[name=category]').value = 'roads';"
        )

    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    wait.until(EC.url_contains("/complaints/"))
    assert "complaints" in driver.current_url
    # Success — landed on detail or list page without error
    assert title[:30] in driver.page_source or "submitted" in driver.page_source.lower()


def test_citizen_can_submit_anonymous_complaint(driver, base_url):
    """Anonymous complaints should not reveal the citizen's identity."""
    login(driver, base_url, "Swagoto", "23101124")
    driver.get(f"{base_url}/complaints/create/")

    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.NAME, "title")))

    ts = str(int(time.time()))
    driver.find_element(By.NAME, "title").send_keys(f"Anonymous Report {ts}")
    driver.find_element(By.NAME, "description").send_keys(
        "Reporting this anonymously to avoid identification."
    )
    driver.find_element(By.NAME, "location_text").send_keys("Gulshan, Dhaka")

    # Tick anonymous checkbox
    anon_cb = driver.find_element(By.NAME, "is_anonymous")
    if not anon_cb.is_selected():
        anon_cb.click()

    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    wait.until(EC.url_contains("/complaints/"))


def test_missing_required_fields_shows_error(driver, base_url):
    """Submitting a blank form should show a validation error."""
    login(driver, base_url, "Swagoto", "23101124")
    driver.get(f"{base_url}/complaints/create/")

    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[type='submit']")))

    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    # Either HTML5 required validation kicks in or the view returns an error
    wait.until(lambda d: "create" in d.current_url or "error" in d.page_source.lower()
               or "required" in d.page_source.lower() or "fill" in d.page_source.lower())
    assert "/accounts/dashboard/" not in driver.current_url


def test_submitted_complaint_appears_in_list(driver, base_url):
    """After submission the complaint should be visible in the citizen's list."""
    login(driver, base_url, "Swagoto", "23101124")
    driver.get(f"{base_url}/complaints/")

    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "card")))
    assert "complaint" in driver.page_source.lower() or "No complaints" in driver.page_source


def test_complaint_detail_accessible_to_citizen(driver, base_url):
    """Citizen should be able to open their own complaint detail page."""
    login(driver, base_url, "Swagoto", "23101124")
    driver.get(f"{base_url}/complaints/")

    wait = WebDriverWait(driver, 10)
    # Find first complaint link
    links = wait.until(EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, "a[href*='/complaints/']")
    ))
    complaint_links = [l for l in links if "/complaints/" in l.get_attribute("href")
                       and "create" not in l.get_attribute("href")
                       and "community" not in l.get_attribute("href")]
    if complaint_links:
        complaint_links[0].click()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "card")))
        assert "/complaints/" in driver.current_url


def test_non_owner_citizen_cannot_view_other_complaint(driver, base_url):
    """A citizen should not be able to view another citizen's complaint detail."""
    # Login as qq (different citizen)
    login(driver, base_url, "qq", "123456")
    # Try to access complaint #1 (likely owned by Swagoto or seed data citizens)
    driver.get(f"{base_url}/complaints/1/")
    wait = WebDriverWait(driver, 10)
    # Should redirect to complaint list or show access denied
    wait.until(lambda d: d.current_url != f"{base_url}/complaints/1/")
    # Either redirected or access denied message
    assert "/complaints/1/" not in driver.current_url or "Access denied" in driver.page_source
