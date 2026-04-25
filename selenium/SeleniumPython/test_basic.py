def test_site_loads(driver, live_server):
    driver.get(live_server.url)

    assert driver.current_url == live_server.url + "/"