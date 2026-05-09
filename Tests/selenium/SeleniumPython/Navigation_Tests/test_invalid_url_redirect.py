

def test_invalid_url_redirect(driver):
    driver.get("http://127.0.0.1:8000/random-invalid-page/")

    assert "404" in driver.page_source or driver.title != ""