
from webdriver_setup import setup_driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import datetime, time, requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# === CONFIG ===
RECEIVER_URL = "https://8f0d-2405-201-680d-d94d-a01a-7bfe-cdc6-e548.ngrok-free.app/receive"
SPREADSHEET_ID = "1SCQl-hZGKPV7rTzP14bEL_0_PGqQ2ZJ9sr6zB9GjwOI"
TELEGRAM_TOKEN = "8115443756:AAEhJVJRDaHSS43x8I7kVNI1hj-9M41hZ90"
TELEGRAM_CHAT_ID = "221114906"

# === Google Sheets Setup ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("gspread_key.json", scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SPREADSHEET_ID).sheet1

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    try:
        requests.post(url, data=data)
    except Exception as ex:
        print(f"Telegram error: {ex}")

def wait_until_7th_second():
    while True:
        now = datetime.datetime.now()
        if now.second == 7:
            return
        time.sleep(0.3)

def scrape_and_send():
    driver = setup_driver()
    driver.get("https://bdgclubs.in/#/home/AllLotteryGames/WinGo?typeId=1")

    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".GameRecord__C-body"))
        )

        base = "#app > div.WinGo__C > div.GameRecord__C.game-record > div.GameRecord__C-body > div:nth-child(1)"
        period = driver.find_element(By.CSS_SELECTOR, f"{base} > div.van-col.van-col--9").text
        number = driver.find_element(By.CSS_SELECTOR, f"{base} > div.van-col.van-col--5.numcenter > div").text
        num = int(number)
        size = "Big" if num >= 5 else "Small"
        color = (
            ["Red", "Violet"] if num == 0 else
            ["Green", "Violet"] if num == 5 else
            ["Red"] if num % 2 == 0 else
            ["Green"]
        )
        result_msg = f"🧠 SYSTEM REPORT:\nPeriod: {period}\nNumber: {number}\nSize: {size}\nColor(s): {', '.join(color)}"

        requests.post(RECEIVER_URL, json={"message": result_msg})
        print(f"✅ Sent to receiver: {result_msg.replace(chr(10), ' | ')}")

        sheet.append_row([
            str(datetime.datetime.now()), period, number, size, ", ".join(color)
        ])
        print("✅ Logged to Google Sheet.")

    except Exception as e:
        error_msg = f"❌ SCRAPER ERROR:\n{e}"
        print(error_msg)
        send_telegram(error_msg)

    driver.quit()

# Run loop
while True:
    wait_until_7th_second()
    scrape_and_send()
    time.sleep(1)
