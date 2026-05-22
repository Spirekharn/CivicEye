from selenium.webdriver.common.by import By

BASE_URL = "http://127.0.0.1:8000"


def test_login_required_redirect(driver):

    # PROTECTED ROLE-BASED PAGES
    protected_pages = [
        "/admin/",
        "/finance/dashboard/",
        "/department/dashboard/",
        "/surveyor/dashboard/",
        "/worker/dashboard/",
        "/technician/dashboard/",
        "/citizen/dashboard/",
    ]

    for page in protected_pages:

        # ACCESS WITHOUT LOGIN
        driver.get(BASE_URL + page)

        current_url = driver.current_url.lower()
        page_source = driver.page_source.lower()

        # VALID SECURITY RESPONSES
        is_login_redirect = "/login" in current_url
        is_admin_login = "/admin/login" in current_url

        is_forbidden = (
            "403" in page_source
            or "forbidden" in page_source
            or "permission denied" in page_source
            or "unauthorized" in page_source
        )

        is_not_found = (
            "page not found" in page_source
            or "404" in page_source
        )

        is_login_page = (
            "log in" in page_source
            or "username" in page_source
            or "password" in page_source
        )

        assert (
            is_login_redirect
            or is_admin_login
            or is_forbidden
            or is_not_found
            or is_login_page
        ), f"Unauthorized access allowed for {page}"