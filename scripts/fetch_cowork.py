#!/usr/bin/env python3
"""Pull open co-working opportunities (individual research projects and
thesis topics) from Matti's private Notion database and write them to
_data/cowork.json as a single flat JSON array, each tagged with the
Notion "Multi-select" categories it belongs to ("Small project" and/or
"Thesis topic") — content/cowork.md filters this one list into its two
sections by category.

The database lives in a private Notion workspace
(https://www.notion.so/matnel/7f67eaa07e10418497bb03da9627d632), so
reading it requires a Notion integration token with the database shared
to it: set NOTION_TOKEN (a repo secret in CI). Locally, drop it in a
gitignored .env file (NOTION_TOKEN=...) at the repo root instead of
exporting it by hand — python-dotenv, if installed, loads it
automatically below; it's a no-op if the package or file isn't there, so
this stays optional. Only rows with the "Available" checkbox on are
included — a topic's "Status" (e.g. "Topic with someone") is not
consulted, since "Available" is the field actually meant to gate what's
shown here. Run daily by .github/workflows/pages.yml.
"""
import json
import os
import pathlib

import requests

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUTPUT_PATH = ROOT / "_data" / "cowork.json"

DATABASE_ID = "7f67eaa07e10418497bb03da9627d632"
NOTION_VERSION = "2022-06-28"


def plain_text(rich_text):
    return "".join(part.get("plain_text", "") for part in rich_text or [])


def multi_select_names(prop):
    return [option["name"] for option in (prop or {}).get("multi_select", [])]


def page_to_topic(page):
    props = page["properties"]
    return {
        "title": plain_text(props["Title"]["title"]),
        "description": plain_text(props["Description"]["rich_text"]),
        "categories": multi_select_names(props.get("Multi-select")),
        "work_area": multi_select_names(props.get("Work area")),
        "paid_position": props["Paid position"]["checkbox"],
        "finnish_skill_required": props["Finnish skill required"]["checkbox"],
    }


def fetch_available_topics(token):
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }
    payload = {"filter": {"property": "Available", "checkbox": {"equals": True}}}

    topics = []
    while True:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        topics.extend(page_to_topic(page) for page in data["results"])
        if not data.get("has_more"):
            break
        payload["start_cursor"] = data["next_cursor"]
    return topics


def main():
    token = os.environ.get("NOTION_TOKEN")
    if not token:
        # A missing token is expected for local checkouts without one
        # configured — write an empty list so the page still renders
        # (just without any topics) rather than crashing the build.
        print("warning: NOTION_TOKEN not set; writing empty list")
        topics = []
    else:
        try:
            topics = fetch_available_topics(token)
        except requests.RequestException as exc:
            print(f"warning: could not fetch Notion database ({exc}); writing empty list")
            topics = []

    with open(OUTPUT_PATH, "w") as f:
        json.dump(topics, f, ensure_ascii=False)
        f.write("\n")

    print(f"Wrote {len(topics)} co-working topics to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
