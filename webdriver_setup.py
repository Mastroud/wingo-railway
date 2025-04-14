from playwright.sync_api import sync_playwright

def create_chrome_driver():
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()
    return playwright, browser, page

