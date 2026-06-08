"""
Amazon Price Tracker
Tracks product prices and sends a Telegram alert when price drops below target.
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime

TELEGRAM_TOKEN = "YOUR_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"

PRODUCTS = [
    {
        "name": "RTX 4070",
        "url": "https://www.amazon.fr/dp/ASIN_HERE",
        "target_price": 550.0
    }
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "fr-FR,fr;q=0.9"
}


def get_price(url):
    res = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(res.content, "html.parser")
    price_tag = soup.select_one(".a-price-whole")
    if not price_tag:
        return None
    price_str = price_tag.get_text().replace(",", ".").replace("\xa0", "").strip()
    return float(price_str)


def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": message})


def log(product, price):
    entry = {"date": datetime.now().isoformat(), "product": product, "price": price}
    try:
        with open("price_history.json", "r") as f:
            history = json.load(f)
    except FileNotFoundError:
        history = []
    history.append(entry)
    with open("price_history.json", "w") as f:
        json.dump(history, f, indent=2)


def run():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Checking prices...")
    for product in PRODUCTS:
        price = get_price(product["url"])
        if price is None:
            print(f"  ✗ Could not fetch: {product['name']}")
            continue
        print(f"  {product['name']}: €{price}")
        log(product["name"], price)
        if price <= product["target_price"]:
            msg = f"🔥 PRICE DROP!\n{product['name']}\nCurrent: €{price}\nTarget: €{product['target_price']}\n{product['url']}"
            send_telegram(msg)
            print(f"  → Alert sent!")


if __name__ == "__main__":
    while True:
        run()
        time.sleep(3600)  # check every hour
