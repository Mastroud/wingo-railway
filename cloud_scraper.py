
from webdriver_setup import setup_driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import datetime, time, requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials

RECEIVER_URL = "https://8f0d-2405-201-680d-d94d-a01a-7bfe-cdc6-e548.ngrok-free.app/receive"
SPREADSHEET_ID = "1SCQl-hZGKPV7rTzP14bEL_0_PGqQ2ZJ9sr6zB9GjwOI"
TELEGRAM_TOKEN = "8115443756:AAEhJVJRDaHSS43x8I7kVNI1hj-9M41hZ90"
TELEGRAM_CHAT_ID = "221114906"

key_dict = {
  "type": "service_account",
  "project_id": "wingo-scraper-419709",
  "private_key_id": "ec38c8ba7f69e7a51d1d4e65b9084f3c3ea4fc8d",
  "private_key": """-----BEGIN PRIVATE KEY-----
MIIEv...YOUR_FULL_PRIVATE_KEY_HERE...
-----END PRIVATE KEY-----""",
  "client_email": "wingo-logger@wingo-scraper-419709.iam.gserviceaccount.com",
  "client_id": "116600263750120579422",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/wingo-logger%40wingo-scraper-419709.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(key_dict, scope)
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

while True:
    wait_until_7th_second()
    scrape_and_send()
    time.sleep(1)
