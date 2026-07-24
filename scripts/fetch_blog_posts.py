#!/usr/bin/env python3
"""Pull recent posts from every RSS/Atom feed listed in _data/feeds.yaml,
merge them, and write the newest MAX_POSTS across all feeds to
_data/blog_posts.json. Run daily by .github/workflows/pages.yml.

Each feed is fetched independently and soft-fails to no posts (with a
warning) rather than taking down the others — see fetch_feed(). Posts are
gathered from every feed uncapped, then sorted by date and capped at
MAX_POSTS exactly once at the end, so a feed that happens to publish less
often never has a genuinely-newer post wrongly dropped by a per-feed cap.
"""
import datetime
import email.utils
import json
import pathlib
import xml.etree.ElementTree as ET

import requests
import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
FEEDS_PATH = ROOT / "_data" / "feeds.yaml"
OUTPUT_PATH = ROOT / "_data" / "blog_posts.json"

# Substack (and possibly other feeds) sit behind Cloudflare, which blocks
# requests from datacenter/cloud IP ranges (including GitHub Actions
# runners) with a 403 regardless of headers sent — a browser-like
# User-Agent is still worth sending since it costs nothing, but it won't
# reliably prevent the block. When that happens, fall back to rss2json's
# public feed-to-JSON proxy: it fetches the same public feed from its own
# (differently-reputationed) IPs and hands back JSON, which sidesteps the
# block without needing any credentials.
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.8",
}
RSS2JSON_URL = "https://api.rss2json.com/v1/api.json"
MAX_POSTS = 10


def load_feeds():
    with open(FEEDS_PATH) as f:
        return yaml.safe_load(f)


def parse_rfc822_date(pub_date):
    dt = email.utils.parsedate_to_datetime(pub_date)
    return dt.strftime("%Y-%m-%d")


def fetch_direct(feed_url):
    resp = requests.get(feed_url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    root = ET.fromstring(resp.content)

    posts = []
    for item in root.findall("./channel/item"):
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


def fetch_via_rss2json(feed_url):
    resp = requests.get(RSS2JSON_URL, params={"rss_url": feed_url}, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if data.get("status") != "ok":
        raise requests.RequestException(f"rss2json returned status {data.get('status')!r}")

    posts = []
    for item in data.get("items", []):
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


def fetch_feed(url):
    try:
        return fetch_direct(url)
    except (requests.RequestException, ET.ParseError) as exc:
        print(f"warning: direct fetch of {url!r} failed ({exc}); trying rss2json fallback")

    try:
        return fetch_via_rss2json(url)
    except requests.RequestException as exc2:
        # A single feed being unreachable is a nice-to-have on the
        # homepage, not core content — don't fail the whole site
        # build/deploy over it. Skip this feed rather than crashing the
        # workflow; the others still contribute their posts.
        print(f"warning: rss2json fallback for {url!r} also failed ({exc2}); skipping this feed")
        return []


def main():
    try:
        feeds = load_feeds() or []
    except FileNotFoundError:
        print(f"warning: {FEEDS_PATH} not found; writing empty list")
        feeds = []

    all_posts = []
    for url in feeds:
        all_posts.extend(fetch_feed(url))

    # No cross-feed dedup — add if/when a real duplicate-URL case shows up.
    all_posts.sort(key=lambda p: p["date"] or "", reverse=True)
    posts = all_posts[:MAX_POSTS]

    with open(OUTPUT_PATH, "w") as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Wrote {len(posts)} blog posts (from {len(feeds)} feed(s)) to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
