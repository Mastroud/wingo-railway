
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

# === Google Sheets Setup ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("gspread_key.json", scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SPREADSHEET_ID).sheet1

# === Wait until 7th second of the minute ===
def wait_until_7th_second():
    while True:
        now = datetime.datetime.now()
        if now.second == 7:
            return
        time.sleep(0.3)

# === Scrape, Send, Log ===
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

        # Send to local receiver
        requests.post(RECEIVER_URL, json={"message": result_msg})
        print(f"✅ Sent to receiver: {result_msg.replace(chr(10), ' | ')}")

        # Append to Google Sheet
        sheet.append_row([
            str(datetime.datetime.now()), period, number, size, ", ".join(color)
        ])
        print("✅ Logged to Google Sheet.")

    except Exception as e:
        print(f"❌ ERROR: {e}")

    driver.quit()

# === Run Loop ===
while True:
    wait_until_7th_second()
    scrape_and_send()
    time.sleep(1)
