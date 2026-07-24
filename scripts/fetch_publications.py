#!/usr/bin/env python3
"""Pull publications from ORCID for every current (non-alumni) group member
and write them to _data/publications.json as a single list.

Which papers get included is still discovered via current members' ORCID
records, but who gets *credited* on each paper is decided separately: for
every publication with a DOI, the actual author list is fetched from
Crossref and matched by name against the *full* roster in
_data/people.yaml (current members and alumni alike). This catches
co-authors ORCID search alone would miss — e.g. a group member whose own
ORCID profile has no linked works, or an alumnus who's no longer searched
by ORCID at all but is a real co-author. Falls back to the ORCID-search
attribution if a paper has no DOI or the Crossref lookup fails.

A paper co-authored by more than one group member is written once, with an
`authors` list naming every group member found on it — not once per author.
Deduplicated by DOI, falling back to a slugified title for the rare work
without one.

Each publication with a DOI also gets an `abstract` (full text, untruncated —
display-time truncation is the templates' job), pulled from the same Crossref
lookup used for author matching where available. Crossref only has an
abstract for roughly 60% of DOIs in practice, so any DOI it misses is
retried in one batched Semantic Scholar Graph API call. A publication with no
DOI, or where neither source has an abstract, simply has no `abstract` key —
same soft-fail spirit as the rest of this script.

Run daily by .github/workflows/pages.yml.
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
CROSSREF_HEADERS = {
    "Accept": "application/json",
    "User-Agent": "social-computing-www-bot (mailto:matti.nelimarkka@helsinki.fi)",
}
SEMANTIC_SCHOLAR_BATCH_URL = "https://api.semanticscholar.org/graph/v1/paper/batch"
TRANSLIT = str.maketrans("äöåÄÖÅ", "aoaAOA")
DOI_PREFIX_RE = re.compile(r"^(https?://)?(dx\.)?doi\.org/|^doi:", re.IGNORECASE)
TAG_RE = re.compile(r"<[^>]+>")
ABSTRACT_LABEL_RE = re.compile(r"^\s*abstract\s*[:.\-]?\s*", re.IGNORECASE)
WHITESPACE_RE = re.compile(r"\s+")


def slugify(text):
    text = text.translate(TRANSLIT)
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:80] or "untitled"


def clean_abstract(raw):
    """Crossref abstracts come wrapped in JATS-ish tags, e.g.
    "<jats:title>Abstract</jats:title><jats:p>...</jats:p>" — strip the
    tags, drop the leftover "Abstract" label, and collapse the whitespace
    that stripping tags leaves behind. Semantic Scholar abstracts are
    already plain text, but running them through this too is harmless."""
    if not raw:
        return None
    text = TAG_RE.sub(" ", raw)
    text = ABSTRACT_LABEL_RE.sub("", text)
    text = WHITESPACE_RE.sub(" ", text).strip()
    return text or None


def load_people():
    with open(PEOPLE_PATH) as f:
        return yaml.safe_load(f)


def load_current_members(people):
    return [p for p in people if not p.get("alumni") and p.get("orcid")]


def build_roster_index(people):
    """(family_name, full_name) for every group member, current or
    alumni, for matching Crossref authors."""
    roster = []
    for person in people:
        parts = person["name"].split()
        roster.append((parts[-1], person["name"]))
    return roster


NAME_TOKEN_RE = re.compile(r"[a-zA-ZäöåÄÖÅ]+")


def match_authors_to_roster(crossref_authors, roster):
    """Match by surname as a whole-word token of "given family", rather
    than an exact split on Crossref's own given/family fields — those
    fields are inconsistently split across papers (e.g. Felix Anand Epp
    shows up as given="Felix Anand"/family="Epp" on one paper and
    given="Felix"/family="Anand Epp" on another), so a straight
    family-field match misses real co-authors. Our roster's surnames are
    distinctive enough that a surname-token match alone is reliable."""
    matched = set()
    for author in crossref_authors:
        full_name = f"{author.get('given') or ''} {author.get('family') or ''}"
        tokens = set(t.lower() for t in NAME_TOKEN_RE.findall(full_name))
        for family_name, roster_full_name in roster:
            if family_name.lower() in tokens:
                matched.add(roster_full_name)
    return matched


def fetch_crossref_work(doi):
    try:
        resp = requests.get(f"https://api.crossref.org/works/{doi}", headers=CROSSREF_HEADERS, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as exc:
        print(f"  warning: Crossref lookup failed for {doi!r}: {exc}")
        return None
    return resp.json().get("message", {})


def fetch_semantic_scholar_abstracts(dois):
    """One batched lookup for every DOI Crossref didn't have an abstract
    for — the batch endpoint takes up to 500 IDs per call, comfortably
    covering this group's whole publication list in a single request. A
    failure here just means no fallback abstracts this run, not a broken
    build (same soft-fail spirit as the rest of this script)."""
    if not dois:
        return {}
    try:
        resp = requests.post(
            SEMANTIC_SCHOLAR_BATCH_URL,
            params={"fields": "abstract"},
            json={"ids": [f"DOI:{doi}" for doi in dois]},
            headers=HEADERS,
            timeout=30,
        )
        resp.raise_for_status()
    except requests.RequestException as exc:
        print(f"  warning: Semantic Scholar batch lookup failed: {exc}")
        return {}
    # Response is positionally aligned with the request `ids`; unmatched
    # DOIs come back as `null`, which is a normal "not available" — not an
    # error worth warning about.
    return {doi: paper["abstract"] for doi, paper in zip(dois, resp.json()) if paper and paper.get("abstract")}


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
    people = load_people()
    members = load_current_members(people)
    roster = build_roster_index(people)
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

    for pub in publications.values():
        if not pub["doi"]:
            continue
        work = fetch_crossref_work(pub["doi"])
        if not work:
            continue
        roster_matches = match_authors_to_roster(work.get("author") or [], roster)
        if roster_matches:
            pub["authors"] = roster_matches
        pub["abstract"] = clean_abstract(work.get("abstract"))

    missing_dois = [pub["doi"] for pub in publications.values() if pub["doi"] and not pub.get("abstract")]
    if missing_dois:
        print(f"Looking up {len(missing_dois)} missing abstracts on Semantic Scholar")
        fallback_abstracts = fetch_semantic_scholar_abstracts(missing_dois)
        for pub in publications.values():
            if pub["doi"] in fallback_abstracts:
                pub["abstract"] = clean_abstract(fallback_abstracts[pub["doi"]])

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
