from selenium import webdriver
from selenium.webdriver.common.by import By
import time

driver = webdriver.Chrome()

driver.get("http://127.0.0.1:8000/accounts/login/")

time.sleep(2)

driver.find_element(By.NAME, "username").send_keys("testuser")
driver.find_element(By.NAME, "password").send_keys("testpass123")

time.sleep(2)

driver.quit()