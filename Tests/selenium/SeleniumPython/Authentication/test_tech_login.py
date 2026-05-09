import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# Role-based test credentials
@pytest.mark.parametrize("username,password", [

    ("sujan", "23101120"),       # tech

])
def test_login_multiple_roles(driver, username, password):

    driver.get("http://127.0.0.1:8000/accounts/login/")

    # Wait for fields
    username_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )

    password_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "password"))
    )

    # Input credentials
    username_field.clear()
    username_field.send_keys(username)

    password_field.clear()
    password_field.send_keys(password)

    # Submit
    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    # Wait for redirect or page change
    WebDriverWait(driver, 10).until(
        EC.url_changes("http://127.0.0.1:8000/accounts/login/")
    )

    # Basic assertion
    assert "login" not in driver.current_url