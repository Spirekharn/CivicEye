from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_logout(driver, live_server):
    driver.get(f"{live_server.url}/accounts/login/")

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )

    driver.find_element(By.NAME, "username").send_keys("testuser123")
    driver.find_element(By.NAME, "password").send_keys("password123")

    driver.find_element(By.XPATH, "//button[@type='submit']").click()


    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "logout"))
    )

    driver.find_element(By.ID, "logout").click()

    WebDriverWait(driver, 10).until(
        EC.url_contains("login")
    )


    assert "login" in driver.current_url