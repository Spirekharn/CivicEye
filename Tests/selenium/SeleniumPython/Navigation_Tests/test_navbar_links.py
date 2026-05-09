from selenium.webdriver.common.by import By

def test_navbar_links(driver):
    driver.get("http://127.0.0.1:8000/")

    links = driver.find_elements(By.TAG_NAME, "a")

    assert len(links) > 0