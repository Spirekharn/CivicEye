from selenium.webdriver.common.by import By

BASE_URL = "http://127.0.0.1:8000"


def test_login_required_redirect(driver):
    protected_pages = [
        "/admin/dashboard/",
        "/worker/dashboard/",
        "/citizen/dashboard/",
    ]

    for page in protected_pages:
        driver.get(BASE_URL + page)

        current_url = driver.current_url.lower()
        page_source = driver.page_source.lower()

        # ✔ valid behaviors
        is_login_redirect = "/login" in current_url
        is_admin_login = "/admin/login" in current_url
        is_forbidden = "403" in page_source or "forbidden" in page_source
        is_not_found = "page not found" in page_source or "404" in page_source

        assert is_login_redirect or is_admin_login or is_forbidden or is_not_found