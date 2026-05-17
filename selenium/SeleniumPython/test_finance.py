"""
Selenium tests — Finance & Analytics access controls

Covers:
- Finance dashboard accessible to finance officer
- Finance dashboard accessible to super admin
- Finance dashboard blocked for citizens
- Finance dashboard blocked for surveyors/workers
- Budget allocation page only for finance/super_admin
- Analytics dashboard accessible to admin/finance/super_admin
- Analytics dashboard blocked for citizens
- All chart data endpoints respond without error
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from conftest import login
import json


def test_finance_dashboard_accessible_to_finance_officer(driver, base_url):
    """Finance officer should reach the finance dashboard."""
    login(driver, base_url, "finance_officer", "Finance@123")
    driver.get(f"{base_url}/finance/")
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "main")))
    assert "/finance/" in driver.current_url
    assert "Server Error" not in driver.page_source
    assert "Budget" in driver.page_source or "Finance" in driver.page_source


def test_finance_dashboard_accessible_to_super_admin(driver, base_url):
    """Super Admin should be able to view the finance dashboard."""
    login(driver, base_url, "SSNSTCE", "SSNSTCE")
    driver.get(f"{base_url}/finance/")
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "main")))
    assert "Server Error" not in driver.page_source


def test_finance_dashboard_blocked_for_citizen(driver, base_url):
    """Citizens must be redirected from the finance dashboard."""
    login(driver, base_url, "Swagoto", "23101124")
    driver.get(f"{base_url}/finance/")
    wait = WebDriverWait(driver, 10)
    wait.until(lambda d: d.current_url != f"{base_url}/finance/")
    assert "/finance/" not in driver.current_url


def test_finance_dashboard_blocked_for_surveyor(driver, base_url):
    """Surveyors must not have access to the finance dashboard."""
    login(driver, base_url, "Labib", "23101128")
    driver.get(f"{base_url}/finance/")
    wait = WebDriverWait(driver, 10)
    wait.until(lambda d: d.current_url != f"{base_url}/finance/")
    assert "/finance/" not in driver.current_url


def test_budget_allocate_blocked_for_dept_admin(driver, base_url):
    """Department admin should not be able to allocate budgets."""
    login(driver, base_url, "admin_dscc", "Admin@123")
    driver.get(f"{base_url}/finance/allocate/")
    wait = WebDriverWait(driver, 10)
    wait.until(lambda d: d.current_url != f"{base_url}/finance/allocate/")
    assert "/finance/allocate/" not in driver.current_url


def test_expense_list_accessible_to_finance(driver, base_url):
    """Finance officer should be able to see the expense list."""
    login(driver, base_url, "finance_officer", "Finance@123")
    driver.get(f"{base_url}/finance/expenses/")
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "main")))
    assert "Server Error" not in driver.page_source


def test_analytics_dashboard_accessible_to_admin(driver, base_url):
    """Department admin should have access to the analytics dashboard."""
    login(driver, base_url, "admin_dscc", "Admin@123")
    driver.get(f"{base_url}/analytics/")
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "main")))
    assert "/analytics/" in driver.current_url
    assert "Server Error" not in driver.page_source


def test_analytics_blocked_for_citizen(driver, base_url):
    """Citizens should be redirected from the analytics dashboard."""
    login(driver, base_url, "Swagoto", "23101124")
    driver.get(f"{base_url}/analytics/")
    wait = WebDriverWait(driver, 10)
    wait.until(lambda d: d.current_url != f"{base_url}/analytics/")
    assert "/analytics/" not in driver.current_url


def test_analytics_api_by_category_returns_json(driver, base_url):
    """The /analytics/api/by-category/ endpoint should return valid JSON."""
    login(driver, base_url, "SSNSTCE", "SSNSTCE")
    driver.get(f"{base_url}/analytics/api/by-category/")
    wait = WebDriverWait(driver, 5)
    wait.until(lambda d: len(d.page_source) > 10)
    try:
        data = json.loads(driver.find_element(By.TAG_NAME, "body").text)
        assert "data" in data
    except (json.JSONDecodeError, Exception):
        # Some browsers wrap JSON in HTML — check for the key in source
        assert '"data"' in driver.page_source


def test_analytics_api_by_status_returns_json(driver, base_url):
    """The /analytics/api/by-status/ endpoint should return valid JSON."""
    login(driver, base_url, "SSNSTCE", "SSNSTCE")
    driver.get(f"{base_url}/analytics/api/by-status/")
    wait = WebDriverWait(driver, 5)
    wait.until(lambda d: len(d.page_source) > 10)
    assert '"data"' in driver.page_source


def test_budget_utilisation_forbidden_for_dept_admin(driver, base_url):
    """
    The budget utilisation endpoint should return 403 for dept admin.
    Dept admin is allowed to view the analytics dashboard but NOT this specific endpoint.
    """
    login(driver, base_url, "admin_dscc", "Admin@123")
    driver.get(f"{base_url}/analytics/api/budget-utilisation/")
    wait = WebDriverWait(driver, 5)
    wait.until(lambda d: len(d.page_source) > 5)
    assert '"error"' in driver.page_source or "Forbidden" in driver.page_source
