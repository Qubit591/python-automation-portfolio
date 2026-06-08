"""
Telegram Alert Bot
Monitors a keyword in RSS feeds / websites and sends Telegram alerts instantly.
Configurable sources, keywords, and check interval.
"""

import requests
import feedparser
import json
import time
import hashlib
from datetime import datetime
from pathlib import Path

CONFIG = {
    "telegram_token": "YOUR_BOT_TOKEN",
    "chat_id": "YOUR_CHAT_ID",
    "check_interval": 300,  # seconds
    "keywords": ["python", "automation", "freelance"],
    "feeds": [
        "https://news.ycombinator.com/rss",
        "https://www.reddit.com/r/Python/.rss",
        "https://www.reddit.com/r/forhire/.rss",
    ]
}

SEEN_FILE = Path("seen_items.json")


def load_seen():
    if SEEN_FILE.exists():
        return set(json.loads(SEEN_FILE.read_text()))
    return set()


def save_seen(seen):
    SEEN_FILE.write_text(json.dumps(list(seen)))


def send_telegram(text):
    url = f"https://api.telegram.org/bot{CONFIG['telegram_token']}/sendMessage"
    payload = {
        "chat_id": CONFIG["chat_id"],
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    try:
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print(f"Telegram error: {e}")


def item_id(entry):
    return hashlib.md5((entry.get("link", "") + entry.get("title", "")).encode()).hexdigest()


def matches_keyword(text):
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in CONFIG["keywords"])


def check_feeds(seen):
    new_items = []
    for feed_url in CONFIG["feeds"]:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                uid = item_id(entry)
                if uid in seen:
                    continue
                seen.add(uid)
                title = entry.get("title", "")
                summary = entry.get("summary", "")
                link = entry.get("link", "")
                if matches_keyword(title + " " + summary):
                    new_items.append({"title": title, "link": link, "source": feed.feed.get("title", feed_url)})
        except Exception as e:
            print(f"Feed error ({feed_url}): {e}")
    return new_items, seen


def run():
    print(f"Bot started. Monitoring {len(CONFIG['feeds'])} feeds for: {CONFIG['keywords']}")
    seen = load_seen()

    while True:
        now = datetime.now().strftime("%H:%M:%S")
        print(f"[{now}] Checking feeds...")
        new_items, seen = check_feeds(seen)

        for item in new_items:
            msg = f"🔔 <b>New match!</b>\n\n<b>{item['title']}</b>\n\nSource: {item['source']}\n{item['link']}"
            send_telegram(msg)
            print(f"  → Alert sent: {item['title'][:60]}")

        if not new_items:
            print(f"  No new matches.")

        save_seen(seen)
        time.sleep(CONFIG["check_interval"])


if __name__ == "__main__":
    run()
