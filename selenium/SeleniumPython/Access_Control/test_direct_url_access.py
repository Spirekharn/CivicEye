from selenium.webdriver.common.by import By

BASE_URL = "http://127.0.0.1:8000"


def login(driver, username, password):
    driver.get(f"{BASE_URL}/accounts/login/")
    driver.find_element(By.NAME, "username").send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.XPATH, "//button[@type='submit']").click()


def test_direct_url_bypass_block(driver):
    restricted_urls = [
        "/admin/dashboard/",
        "/worker/dashboard/",
        "/citizen/dashboard/",
        "/finance/reports/",
    ]

    for url in restricted_urls:
        driver.get(BASE_URL + url)

        current_url = driver.current_url.lower()
        page = driver.page_source.lower()

        # ✔ valid outcomes:
        redirected_to_login = "/login" in current_url
        forbidden = "403" in page or "forbidden" in page
        not_found = "page not found" in page or "404" in page

        assert redirected_to_login or forbidden or not_found


def test_department_page_access(driver):
    login(driver, "SSNS", "SSNSTCE")

    driver.get(f"{BASE_URL}/departments/")

    assert "department" in driver.page_source.lower()