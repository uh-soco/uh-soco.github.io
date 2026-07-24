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
# Substack sits behind Cloudflare, which blocks requests from datacenter/cloud
# IP ranges (including GitHub Actions runners) with a 403 regardless of
# headers sent — a browser-like User-Agent is still worth sending since it
# costs nothing, but it won't reliably prevent the block. When that happens,
# fall back to rss2json's public feed-to-JSON proxy: it fetches the same
# public feed from its own (differently-reputationed) IPs and hands back
# JSON, which sidesteps the block without needing any credentials.
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.8",
}
RSS2JSON_URL = "https://api.rss2json.com/v1/api.json"
MAX_POSTS = 10


def parse_rfc822_date(pub_date):
    dt = email.utils.parsedate_to_datetime(pub_date)
    return dt.strftime("%Y-%m-%d")


def fetch_direct():
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
                "date": parse_rfc822_date(pub_date) if pub_date else None,
            }
        )
    return posts


def fetch_via_rss2json():
    resp = requests.get(RSS2JSON_URL, params={"rss_url": FEED_URL}, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if data.get("status") != "ok":
        raise requests.RequestException(f"rss2json returned status {data.get('status')!r}")

    posts = []
    for item in data.get("items", [])[:MAX_POSTS]:
        pub_date = item.get("pubDate")  # "YYYY-MM-DD HH:MM:SS", not RFC822
        date = None
        if pub_date:
            date = datetime.datetime.strptime(pub_date, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
        posts.append(
            {
                "title": item.get("title"),
                "url": item.get("link"),
                "description": item.get("description"),
                "date": date,
            }
        )
    return posts


def main():
    posts = []
    try:
        posts = fetch_direct()
    except (requests.RequestException, ET.ParseError) as exc:
        print(f"warning: direct blog feed fetch failed ({exc}); trying rss2json fallback")
        try:
            posts = fetch_via_rss2json()
        except requests.RequestException as exc2:
            # The blog feed is a nice-to-have on the homepage, not core
            # content — don't fail the whole site build/deploy over a
            # blocked fetch. Write an empty list so the site still renders
            # (just without recent posts) rather than crashing the workflow.
            print(f"warning: rss2json fallback also failed ({exc2}); writing empty list")

    with open(OUTPUT_PATH, "w") as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Wrote {len(posts)} blog posts to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
