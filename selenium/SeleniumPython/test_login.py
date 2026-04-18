from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

driver.get("http://127.0.0.1:8000/login")

# Enter login info
driver.find_element(By.NAME, "username").send_keys("testuser")
driver.find_element(By.NAME, "password").send_keys("1234")

# Click login button
driver.find_element(By.TAG_NAME, "button").click()

time.sleep(3)

# Check redirect (dashboard or home)
assert "dashboard" in driver.current_url.lower()

driver.quit()