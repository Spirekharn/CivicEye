from selenium import webdriver
from selenium.webdriver.common.by import By

test_results = []

driver = webdriver.Chrome()

# TEST 1
try:
    driver.get("https://example.com")
    if "Example" in driver.title:
        test_results.append(("Open Example", "PASS", "Title correct"))
    else:
        test_results.append(("Open Example", "FAIL", "Title mismatch"))
except Exception as e:
    test_results.append(("Open Example", "FAIL", str(e)))

# TEST 2
try:
    driver.get("https://google.com")
    driver.find_element(By.NAME, "q")
    test_results.append(("Google Search Box", "PASS", "Found search box"))
except Exception as e:
    test_results.append(("Google Search Box", "FAIL", str(e)))

driver.quit()

# GENERATE HTML
html = """
<html>
<head>
<style>
table {width:100%; border-collapse:collapse;}
th, td {border:1px solid black; padding:10px;}
th {background:blue; color:white;}
.PASS {color:green; font-weight:bold;}
.FAIL {color:red; font-weight:bold;}
</style>
</head>
<body>
<h1>Selenium Custom Report</h1>
<table>
<tr><th>Test</th><th>Status</th><th>Details</th></tr>
"""

for t in test_results:
    html += f"""
    <tr>
        <td>{t[0]}</td>
        <td class="{t[1]}">{t[1]}</td>
        <td>{t[2]}</td>
    </tr>
    """

html += "</table></body></html>"

with open("selenium_custom_report.html", "w", encoding="utf-8") as f:
    f.write(html)

print("OPEN selenium_custom_report.html")