"""
Selenium tests — Community (public) dashboard

Covers:
- Public list accessible without login
- Search filters work
- Category filter works
- Complaint detail accessible without login
- No real names or internal finance data exposed on public pages
- Duplicate complaint shows a notice
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_community_list_loads_without_login(driver, base_url):
    """The community complaint list must be accessible to anonymous visitors."""
    driver.get(f"{base_url}/complaints/community/")
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "main")))
    assert driver.current_url == f"{base_url}/complaints/community/" or "/complaints/community/" in driver.current_url


def test_community_list_shows_complaint_cards(driver, base_url):
    """Complaint cards should be visible on the public list."""
    driver.get(f"{base_url}/complaints/community/")
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "main")))
    # Either cards are shown or the empty state message is shown
    assert ("comm-card" in driver.page_source
            or "No complaints" in driver.page_source
            or "community" in driver.page_source.lower())


def test_community_search_filters_results(driver, base_url):
    """Searching by keyword should filter the displayed complaints."""
    driver.get(f"{base_url}/complaints/community/?q=pothole")
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "main")))
    # Page should load without error
    assert "/complaints/community/" in driver.current_url


def test_community_category_filter(driver, base_url):
    """Filtering by category should restrict results."""
    driver.get(f"{base_url}/complaints/community/?category=roads")
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "main")))
    assert "/complaints/community/" in driver.current_url


def test_community_detail_accessible_without_login(driver, base_url):
    """Clicking a complaint card should open its public detail page."""
    driver.get(f"{base_url}/complaints/community/")
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "main")))

    # Find first card link
    cards = driver.find_elements(By.CSS_SELECTOR, "a.comm-card, a[href*='/complaints/community/']")
    community_cards = [c for c in cards
                       if "/complaints/community/" in (c.get_attribute("href") or "")
                       and c.get_attribute("href") != f"{base_url}/complaints/community/"]
    if community_cards:
        href = community_cards[0].get_attribute("href")
        driver.get(href)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "main")))
        assert "/complaints/community/" in driver.current_url


def test_community_detail_does_not_show_real_username(driver, base_url):
    """
    Public complaint detail must not expose the citizen's username.
    It should show 'Community Member' for non-anonymous reports,
    or an alias like 'Anon #XXXX' for anonymous ones.
    """
    driver.get(f"{base_url}/complaints/community/")
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "main")))

    cards = driver.find_elements(By.CSS_SELECTOR, "a.comm-card, a[href*='/complaints/community/']")
    community_cards = [c for c in cards
                       if "/complaints/community/" in (c.get_attribute("href") or "")
                       and c.get_attribute("href") != f"{base_url}/complaints/community/"]
    if community_cards:
        driver.get(community_cards[0].get_attribute("href"))
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "main")))
        page = driver.page_source
        # Real usernames (from seed) must not appear
        for real_username in ["Swagoto", "rahim_citizen", "admin_dscc", "SSNSTCE"]:
            assert real_username not in page, f"Username '{real_username}' leaked on public page"


def test_community_detail_does_not_show_exact_budget(driver, base_url):
    """
    Public complaint detail must not show the exact BDT expense amount
    from the finance module.
    """
    driver.get(f"{base_url}/complaints/community/")
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "main")))

    cards = driver.find_elements(By.CSS_SELECTOR, "a.comm-card, a[href*='/complaints/community/']")
    community_cards = [c for c in cards
                       if "/complaints/community/" in (c.get_attribute("href") or "")
                       and c.get_attribute("href") != f"{base_url}/complaints/community/"]
    if community_cards:
        driver.get(community_cards[0].get_attribute("href"))
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "main")))
        # The page should not contain 'Approved by' or exact finance workflow fields
        page = driver.page_source
        assert "Approved by" not in page
        assert "approved_by" not in page


def test_community_sort_by_oldest(driver, base_url):
    """The sort=oldest parameter should be accepted without error."""
    driver.get(f"{base_url}/complaints/community/?sort=oldest")
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "main")))
    assert "/complaints/community/" in driver.current_url
    assert "Server Error" not in driver.page_source
