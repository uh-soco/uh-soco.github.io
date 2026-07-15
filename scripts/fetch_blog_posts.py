#!/usr/bin/env python3
"""Pull recent posts from the group's Substack blog
(https://sociallycompute.substack.com) and write them to
_data/blog_posts.json. Run daily by .github/workflows/update-data.yml.
"""
import datetime
import email.utils
import json
import pathlib
import xml.etree.ElementTree as ET

import requests

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUTPUT_PATH = ROOT / "_data" / "blog_posts.json"

FEED_URL = "https://sociallycompute.substack.com/feed"
HEADERS = {"User-Agent": "social-computing-www-bot"}
MAX_POSTS = 10


def parse_date(pub_date):
    dt = email.utils.parsedate_to_datetime(pub_date)
    return dt.strftime("%Y-%m-%d")


def main():
    resp = requests.get(FEED_URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    root = ET.fromstring(resp.content)

    posts = []
    for item in root.findall("./channel/item")[:MAX_POSTS]:
        title = item.findtext("title")
        link = item.findtext("link")
        description = item.findtext("description")
        pub_date = item.findtext("pubDate")
        posts.append(
            {
                "title": title,
                "url": link,
                "description": description,
                "date": parse_date(pub_date) if pub_date else None,
            }
        )

    with open(OUTPUT_PATH, "w") as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Wrote {len(posts)} blog posts to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
