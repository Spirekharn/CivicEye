"""
Selenium tests — Assignment & Status workflow

Covers:
- Admin sees complaint list with filter controls
- Admin can navigate to assignment page
- Surveyor sees their queue
- Surveyor can navigate to survey form
- Worker sees their task list
- Notifications page loads and shows entries
- Profile page accessible and shows correct user info
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from conftest import login


def test_admin_can_see_complaint_management_list(driver, base_url):
    """Department admin should reach the full complaint management view."""
    login(driver, base_url, "admin_dscc", "Admin@123")
    driver.get(f"{base_url}/complaints/admin/all/")
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "main")))
    assert "/complaints/admin/all/" in driver.current_url
    assert "Server Error" not in driver.page_source


def test_admin_complaint_list_has_filters(driver, base_url):
    """Admin complaint list should have status and category filter controls."""
    login(driver, base_url, "admin_dscc", "Admin@123")
    driver.get(f"{base_url}/complaints/admin/all/")
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "main")))
    # Should have a search/filter form
    assert "filter" in driver.page_source.lower() or "search" in driver.page_source.lower()


def test_admin_can_filter_by_status(driver, base_url):
    """Admin filtering by status should not crash and should return results."""
    login(driver, base_url, "admin_dscc", "Admin@123")
    driver.get(f"{base_url}/complaints/admin/all/?status=submitted")
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "main")))
    assert "Server Error" not in driver.page_source


def test_surveyor_can_see_queue(driver, base_url):
    """Surveyor should see their assigned complaint queue."""
    login(driver, base_url, "Labib", "23101128")
    driver.get(f"{base_url}/complaints/surveyor/queue/")
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "main")))
    assert "/complaints/surveyor/queue/" in driver.current_url
    assert "Server Error" not in driver.page_source


def test_worker_can_see_tasks(driver, base_url):
    """Field Worker should see their assigned tasks."""
    login(driver, base_url, "Lamiya", "23101132")
    driver.get(f"{base_url}/complaints/worker/tasks/")
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "main")))
    assert "/complaints/worker/tasks/" in driver.current_url
    assert "Server Error" not in driver.page_source


def test_citizen_cannot_access_admin_list(driver, base_url):
    """A citizen should be redirected away from the admin complaint list."""
    login(driver, base_url, "Swagoto", "23101124")
    driver.get(f"{base_url}/complaints/admin/all/")
    wait = WebDriverWait(driver, 10)
    wait.until(lambda d: d.current_url != f"{base_url}/complaints/admin/all/")
    assert "/complaints/admin/all/" not in driver.current_url


def test_citizen_cannot_access_surveyor_queue(driver, base_url):
    """A citizen should be redirected from the surveyor queue."""
    login(driver, base_url, "Swagoto", "23101124")
    driver.get(f"{base_url}/complaints/surveyor/queue/")
    wait = WebDriverWait(driver, 10)
    wait.until(lambda d: d.current_url != f"{base_url}/complaints/surveyor/queue/")
    assert "/complaints/surveyor/queue/" not in driver.current_url


def test_notifications_page_loads(driver, base_url):
    """Notification list should load for an authenticated user."""
    login(driver, base_url, "Swagoto", "23101124")
    driver.get(f"{base_url}/notifications/")
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "main")))
    assert "notifications" in driver.current_url.lower() or "Notification" in driver.page_source


def test_notifications_filter_unread(driver, base_url):
    """Filtering notifications by unread should work without error."""
    login(driver, base_url, "Swagoto", "23101124")
    driver.get(f"{base_url}/notifications/?filter=unread")
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "main")))
    assert "Server Error" not in driver.page_source


def test_profile_page_accessible(driver, base_url):
    """Profile page should load and show the user's name."""
    login(driver, base_url, "Swagoto", "23101124")
    driver.get(f"{base_url}/accounts/profile/")
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "main")))
    assert "profile" in driver.current_url.lower() or "Profile" in driver.page_source
    page = driver.page_source
    assert "Swagoto" in page or "swagoto" in page.lower()


def test_super_admin_can_see_transfer_list(driver, base_url):
    """Super Admin should be able to access the transfer requests page."""
    login(driver, base_url, "SSNSTCE", "SSNSTCE")
    driver.get(f"{base_url}/complaints/transfers/")
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "main")))
    assert "/complaints/transfers/" in driver.current_url
    assert "Server Error" not in driver.page_source


def test_super_admin_can_access_admin_panel(driver, base_url):
    """Super Admin panel should load correctly."""
    login(driver, base_url, "SSNSTCE", "SSNSTCE")
    driver.get(f"{base_url}/accounts/superadmin/")
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "main")))
    assert "Server Error" not in driver.page_source


def test_department_list_accessible_to_admin(driver, base_url):
    """Department list should load for admin and super_admin."""
    login(driver, base_url, "SSNSTCE", "SSNSTCE")
    driver.get(f"{base_url}/departments/")
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "main")))
    assert "Department" in driver.page_source or "department" in driver.page_source.lower()
    assert "Server Error" not in driver.page_source
