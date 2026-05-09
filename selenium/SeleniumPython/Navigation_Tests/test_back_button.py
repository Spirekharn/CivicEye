from selenium.webdriver.common.by import By

def test_back_button(driver):
    driver.get("http://127.0.0.1:8000/")

    first_url = driver.current_url

    driver.get("http://127.0.0.1:8000/about/")

    driver.back()

    assert driver.current_url == first_url