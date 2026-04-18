from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# Start browser
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Open your Django app
driver.get("http://127.0.0.1:8000")

# Wait for page to load
time.sleep(3)

# Example: click first button (if exists)
try:
    button = driver.find_element(By.TAG_NAME, "button")
    button.click()
    print("Button clicked")
except Exception as e:
    print("No button found:", e)




# Close browser
driver.quit()