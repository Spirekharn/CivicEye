import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys


def test_register(driver):

    driver.delete_all_cookies()

    driver.get("http://127.0.0.1:8000/accounts/register/")

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )

    unique_user = f"user{int(time.time())}"

    driver.find_element(By.NAME, "username").send_keys(unique_user)
    driver.find_element(By.NAME, "email").send_keys(f"{unique_user}@gmail.com")
    driver.find_element(By.NAME, "password1").send_keys("Testpass123")
    driver.find_element(By.NAME, "password2").send_keys("Testpass123")

    time.sleep(1)

    driver.find_element(By.NAME, "password2").send_keys(Keys.ENTER)

    time.sleep(5)

    print("\nCURRENT URL:", driver.current_url)
    print("\nPAGE SOURCE:\n")
    print(driver.page_source)

    assert "errorlist" not in driver.page_source.lower()