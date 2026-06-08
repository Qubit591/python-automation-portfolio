"""
Instagram Hashtag Scraper
Extracts public posts data from a hashtag using Instaloader.
Exports to CSV with post URL, likes, date, caption.
"""

import instaloader
import csv
from datetime import datetime
import sys
import time


def scrape_hashtag(hashtag, max_posts=50, output_file=None):
    L = instaloader.Instaloader(
        download_pictures=False,
        download_videos=False,
        download_comments=False,
        save_metadata=False,
        quiet=True
    )

    results = []
    print(f"Scraping #{hashtag} (max {max_posts} posts)...")

    try:
        posts = instaloader.Hashtag.from_name(L.context, hashtag).get_posts()
        for i, post in enumerate(posts):
            if i >= max_posts:
                break
            results.append({
                "shortcode": post.shortcode,
                "url": f"https://www.instagram.com/p/{post.shortcode}/",
                "date": post.date_local.strftime("%Y-%m-%d %H:%M"),
                "likes": post.likes,
                "comments": post.comments,
                "owner": post.owner_username,
                "caption": post.caption[:200] if post.caption else "",
                "hashtags": " ".join(post.caption_hashtags) if post.caption_hashtags else ""
            })
            print(f"  [{i+1}/{max_posts}] @{post.owner_username} — {post.likes} likes")
            time.sleep(1.5)  # polite delay

    except Exception as e:
        print(f"Error: {e}")

    if not results:
        print("No results found.")
        return

    output = output_file or f"{hashtag}_{datetime.now().strftime('%Y%m%d')}.csv"
    with open(output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    print(f"\n✅ {len(results)} posts exported → {output}")
    print(f"Top post: {max(results, key=lambda x: x['likes'])['url']}")


if __name__ == "__main__":
    tag = sys.argv[1] if len(sys.argv) > 1 else "python"
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    scrape_hashtag(tag, limit)
