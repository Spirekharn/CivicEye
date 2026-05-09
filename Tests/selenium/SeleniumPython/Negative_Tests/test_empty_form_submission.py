from selenium import webdriver
from selenium.webdriver.common.by import By

def test_empty_login_form():
    driver = webdriver.Chrome()
    driver.get("http://127.0.0.1:8000/accounts/login/")

    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    # Should NOT allow login, page should still show login form
    assert "login" in driver.current_url.lower()

    driver.quit()