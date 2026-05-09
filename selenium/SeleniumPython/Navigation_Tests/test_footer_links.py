from selenium.webdriver.common.by import By

def test_footer_links(driver):
    driver.get("http://127.0.0.1:8000/")

    footer_links = driver.find_elements(By.TAG_NAME, "a")

    assert len(footer_links) > 0