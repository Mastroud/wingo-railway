import os
import json
import base64
import time
import requests
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_setup import create_chrome_driver

# Load Google credentials from env var
b64_key = os.getenv("GOOGLE_CREDENTIALS_B64")
key_dict = json.loads(base64.b64decode(b64_key).decode())

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(key_dict, scope)
client = gspread.authorize(creds)

# Connect to Google Sheet
sheet = client.open_by_key("1SCQl-hZGKPV7rTzP14bEL_0_PGqQ2ZJ9sr6zB9GjwOI").sheet1

# Constants
RECEIVER_URL = "https://e779-2405-201-680d-d94d-a01a-7bfe-cdc6-e548.ngrok-free.app/receive"
TELEGRAM_TOKEN = "8115443756:AAEhJVJRDaHSS43x8I7kVNI1hj-9M41hZ90"
TELEGRAM_CHAT_ID = "221114906"

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": msg}
    try:
        requests.post(url, data=data)
    except Exception:
        pass

def get_color(num):
    if num == 0:
        return ["Red", "Violet"]
    elif num == 5:
        return ["Green", "Violet"]
    elif num % 2 == 0:
        return ["Red"]
    else:
        return ["Green"]

def get_size(num):
    return "Big" if num >= 5 else "Small"

def scrape_and_send():
    try:
        driver = create_chrome_driver()
        driver.get("https://bdgclubs.in/#/home/AllLotteryGames/WinGo?typeId=1")
        time.sleep(3)

        period = driver.find_element(By.CSS_SELECTOR, ".game-record > div > div:nth-child(1) > div:nth-child(1)").text.strip()
        result = int(driver.find_element(By.CSS_SELECTOR, ".game-record > div > div:nth-child(1) > div:nth-child(2)").text.strip())

        color = ",".join(get_color(result))
        size = get_size(result)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        result_msg = f"{timestamp},{period},{result},{size},{color}"
        requests.post(RECEIVER_URL, json={"message": result_msg})

        sheet.append_row([timestamp, period, result, size, color])
        print(f"✅ Sent: {result_msg}")

        driver.quit()
    except Exception as e:
        send_telegram(f"❌ SCRAPER ERROR:\n{e}")
        print(f"❌ Error: {e}")

# Loop every minute at 7s
while True:
    now = datetime.utcnow()
    if now.second == 7:
        scrape_and_send()
        time.sleep(1)
    time.sleep(0.2)
