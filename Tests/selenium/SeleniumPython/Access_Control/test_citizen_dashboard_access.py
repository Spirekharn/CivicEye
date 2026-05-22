import pytest

BASE_URL = "http://127.0.0.1:8000"


def test_direct_url_bypass_block(driver):

    # RESTRICTED DASHBOARDS / PANELS
    restricted_urls = [
        "/admin/",
        "/finance/dashboard/",
        "/department/dashboard/",
        "/surveyor/dashboard/",
        "/worker/dashboard/",
        "/technician/dashboard/",
        "/citizen/dashboard/",
    ]

    for url in restricted_urls:

        # TRY ACCESS WITHOUT LOGIN
        driver.get(BASE_URL + url)

        current = driver.current_url.lower()
        page = driver.page_source.lower()

        # VALID SECURITY BEHAVIOR
        blocked_by_login_redirect = "/login" in current
        admin_login_redirect = "/admin/login" in current

        login_page_shown = (
            "log in" in page
            or "username" in page
            or "password" in page
        )

        access_denied = (
            "access denied" in page
            or "permission denied" in page
            or "unauthorized" in page
        )

        not_found = "page not found" in page

        assert (
            blocked_by_login_redirect
            or admin_login_redirect
            or login_page_shown
            or access_denied
            or not_found
        ), f"Access control failed for {url}"