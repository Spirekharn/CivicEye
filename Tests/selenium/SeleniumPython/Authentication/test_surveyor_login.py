from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_surveyor_login(driver):

    driver.delete_all_cookies()

    # ---------------- OPEN LOGIN ----------------
    driver.get("http://127.0.0.1:8000/accounts/login/")

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )

    # ---------------- FILL FORM ----------------
    driver.find_element(By.NAME, "username").send_keys("Labib")
    driver.find_element(By.NAME, "password").send_keys("23101128")

    # ---------------- SAFE CLICK ----------------
    login_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "form button"))
    )

    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", login_btn)
    login_btn.click()

    # ---------------- WAIT FOR LOGIN ----------------
    WebDriverWait(driver, 10).until(
        lambda d: "/accounts/dashboard/" in d.current_url
    )

    print("Current URL:", driver.current_url)

    # ---------------- STRONG ASSERTION ----------------
    assert "/accounts/dashboard/" in driver.current_url
    assert "login" not in driver.current_url.lower()