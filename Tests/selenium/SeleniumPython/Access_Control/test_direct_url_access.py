from selenium.webdriver.common.by import By

BASE_URL = "http://127.0.0.1:8000"


def login(driver, username, password):
    driver.get(f"{BASE_URL}/accounts/login/")

    driver.find_element(By.NAME, "username").send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)

    driver.find_element(
        By.XPATH,
        "//button[@type='submit']"
    ).click()


def test_direct_url_bypass_block(driver):

    # RESTRICTED ROLE-BASED PAGES
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

        current_url = driver.current_url.lower()
        page = driver.page_source.lower()

        # VALID SECURITY RESPONSES
        redirected_to_login = "/login" in current_url
        admin_login_redirect = "/admin/login" in current_url

        forbidden = (
            "403" in page
            or "forbidden" in page
            or "permission denied" in page
            or "unauthorized" in page
        )

        not_found = (
            "page not found" in page
            or "404" in page
        )

        login_page = (
            "log in" in page
            or "username" in page
            or "password" in page
        )

        assert (
            redirected_to_login
            or admin_login_redirect
            or forbidden
            or not_found
            or login_page
        ), f"Access control failed for {url}"


def test_department_page_access(driver):

    # LOGIN AS DEPARTMENT ADMIN
    login(driver, "admin_dscc", "Admin@123")

    # OPEN DEPARTMENT PAGE
    driver.get(f"{BASE_URL}/departments/")

    page = driver.page_source.lower()

    # VERIFY PAGE CONTENT
    assert (
        "department" in page
        or "dscc" in page
        or "complaint" in page
        or "assign" in page
    )