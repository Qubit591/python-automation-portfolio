"""
Google Sheets Sync
Pulls data from an API and syncs it to Google Sheets automatically.
Example: syncs crypto prices every 10 minutes to a spreadsheet.
"""

import gspread
from google.oauth2.service_account import Credentials
import requests
from datetime import datetime
import time

SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

SPREADSHEET_ID = "YOUR_SPREADSHEET_ID"
SHEET_NAME = "Crypto Prices"
CREDENTIALS_FILE = "credentials.json"

COINS = ["bitcoin", "ethereum", "solana", "binancecoin"]
UPDATE_INTERVAL = 600  # 10 minutes


def get_sheet():
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(SPREADSHEET_ID)
    try:
        sheet = spreadsheet.worksheet(SHEET_NAME)
    except gspread.WorksheetNotFound:
        sheet = spreadsheet.add_worksheet(title=SHEET_NAME, rows=1000, cols=10)
    return sheet


def fetch_prices(coins):
    ids = ",".join(coins)
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd,eur&include_24hr_change=true"
    res = requests.get(url, timeout=10)
    res.raise_for_status()
    return res.json()


def sync(sheet, data):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Write headers if sheet is empty
    if not sheet.get_all_values():
        headers = ["Timestamp", "Coin", "USD", "EUR", "24h Change (%)"]
        sheet.append_row(headers)

    rows = []
    for coin, prices in data.items():
        rows.append([
            timestamp,
            coin.capitalize(),
            prices.get("usd", "N/A"),
            prices.get("eur", "N/A"),
            round(prices.get("usd_24h_change", 0), 2)
        ])

    sheet.append_rows(rows)
    print(f"[{timestamp}] ✅ {len(rows)} rows synced to Google Sheets")
    for row in rows:
        print(f"  {row[1]}: ${row[2]} | {row[4]}%")


def run():
    print("Google Sheets Sync started...")
    sheet = get_sheet()

    while True:
        try:
            data = fetch_prices(COINS)
            sync(sheet, data)
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(UPDATE_INTERVAL)


if __name__ == "__main__":
    run()
