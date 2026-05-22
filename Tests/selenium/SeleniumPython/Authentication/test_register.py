import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_register(driver):

    driver.delete_all_cookies()
    driver.get("http://127.0.0.1:8000/accounts/register/")

    # wait for form
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )

    unique_user = f"user{int(time.time())}"

    # fill form
    driver.find_element(By.NAME, "username").send_keys(unique_user)
    driver.find_element(By.NAME, "email").send_keys(f"{unique_user}@gmail.com")
    driver.find_element(By.NAME, "password1").send_keys("Testpass123")
    driver.find_element(By.NAME, "password2").send_keys("Testpass123")

    # IMPORTANT: submit form safely (avoids click interception)
    form = driver.find_element(By.TAG_NAME, "form")
    form.submit()

    # wait for redirect (adjust if your app redirects differently)
    WebDriverWait(driver, 10).until(
        lambda d: "dashboard" in d.current_url.lower()
        or d.current_url == "http://127.0.0.1:8000/"
    )

    print("REGISTER SUCCESS URL:", driver.current_url)

    assert "errorlist" not in driver.page_source.lower()