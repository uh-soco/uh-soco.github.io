#!/usr/bin/env python3
"""Pull publications from ORCID for every current (non-alumni) group member
and write them to _data/publications.json as a single list.

A paper co-authored by more than one group member is written once, with an
`authors` list naming every group member found on it — not once per author.
Deduplicated by DOI, falling back to a slugified title for the rare work
without one.

Run daily by .github/workflows/update-data.yml.
"""
import json
import pathlib
import re

import requests
import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
PEOPLE_PATH = ROOT / "_data" / "people.yaml"
OUTPUT_PATH = ROOT / "_data" / "publications.json"

HEADERS = {"Accept": "application/json", "User-Agent": "social-computing-www-bot"}
TRANSLIT = str.maketrans("äöåÄÖÅ", "aoaAOA")
DOI_PREFIX_RE = re.compile(r"^(https?://)?(dx\.)?doi\.org/|^doi:", re.IGNORECASE)


def slugify(text):
    text = text.translate(TRANSLIT)
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:80] or "untitled"


def load_current_members():
    with open(PEOPLE_PATH) as f:
        people = yaml.safe_load(f)
    return [p for p in people if not p.get("alumni") and p.get("orcid")]


def external_id(external_ids, id_type):
    for eid in (external_ids or {}).get("external-id", []):
        if eid.get("external-id-type") == id_type:
            return eid.get("external-id-value")
    return None


def normalize_doi(doi):
    return DOI_PREFIX_RE.sub("", doi).strip("/ ") if doi else None


def fetch_works(orcid_id):
    resp = requests.get(f"https://pub.orcid.org/v3.0/{orcid_id}/works", headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.json().get("group", [])


def group_to_publication(group):
    summary = group["work-summary"][0]
    title = summary.get("title", {}).get("title", {}).get("value") or "Untitled"
    date = summary.get("publication-date") or {}
    year = (date.get("year") or {}).get("value")
    month = (date.get("month") or {}).get("value") or "01"
    day = (date.get("day") or {}).get("value") or "01"
    journal = (summary.get("journal-title") or {}).get("value")
    doi = normalize_doi(external_id(summary.get("external-ids"), "doi"))
    url = (summary.get("url") or {}).get("value")
    return {
        "title": title,
        "year": int(year) if year else None,
        "date": f"{year}-{month}-{day}" if year else "1900-01-01",
        "venue": journal,
        "type": summary.get("type"),
        "doi": doi,
        "url": url,
    }


def dedup_key(pub):
    return pub["doi"] or slugify(pub["title"])


def main():
    members = load_current_members()
    publications = {}

    for member in members:
        print(f"Fetching works for {member['name']} (ORCID {member['orcid']})")
        for group in fetch_works(member["orcid"]):
            pub = group_to_publication(group)
            if pub["title"] == "Untitled":
                continue
            key = dedup_key(pub)
            if key not in publications:
                pub["authors"] = set()
                publications[key] = pub
            publications[key]["authors"].add(member["name"])

    result = []
    for pub in publications.values():
        pub["authors"] = sorted(pub["authors"])
        result.append(pub)
    result.sort(key=lambda p: p["date"], reverse=True)

    with open(OUTPUT_PATH, "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Wrote {len(result)} publications to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
