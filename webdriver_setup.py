from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import chromedriver_autoinstaller

def create_chrome_driver():
    # Auto-install matching ChromeDriver
    chromedriver_autoinstaller.install()

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    return webdriver.Chrome(options=chrome_options)

