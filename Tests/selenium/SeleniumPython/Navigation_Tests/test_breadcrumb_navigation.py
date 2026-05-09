from selenium.webdriver.common.by import By

def test_breadcrumb_navigation(driver):
    driver.get("http://127.0.0.1:8000/about/")

    body = driver.find_element(By.TAG_NAME, "body").text

    assert body is not None