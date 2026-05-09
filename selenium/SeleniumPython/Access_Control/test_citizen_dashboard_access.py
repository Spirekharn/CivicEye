import pytest

BASE_URL = "http://127.0.0.1:8000"


def test_direct_url_bypass_block(driver):
    restricted_urls = [
        "/admin/dashboard/",
        "/worker/dashboard/",
        "/citizen/dashboard/",
        "/finance/reports/",
    ]

    for url in restricted_urls:
        driver.get(BASE_URL + url)

        current = driver.current_url.lower()
        page = driver.page_source.lower()

        # VALID access-control outcomes in your system:
        blocked_by_login_redirect = "/login" in current
        admin_login_redirect = "/admin/login" in current
        login_page_shown = "log in" in page or "username" in page
        not_found = "page not found" in page

        assert (
            blocked_by_login_redirect
            or admin_login_redirect
            or login_page_shown
            or not_found
        ), f"Access control failed for {url}"