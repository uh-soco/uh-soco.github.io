#!/usr/bin/env python3
"""Resolve the manually curated, header-grouped course list in
_data/courses.yaml against the University of Helsinki course catalogue.

Each course entry in _data/courses.yaml needs either a `code` (resolved
here to a real link, dates and current official name for the soonest
upcoming offering, falling back to the most recent past one — any `name`
given in the yaml is ignored) or a `name` on its own, optionally with a
direct `url` (used as-is, no lookup).

Writes _data/teaching.json, preserving the header groups. Run daily by
.github/workflows/pages.yml.
"""
import datetime
import json
import pathlib
import re

import requests
import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
COURSES_PATH = ROOT / "_data" / "courses.yaml"
OUTPUT_PATH = ROOT / "_data" / "teaching.json"

SEARCH_URL = "https://studies.helsinki.fi/api/search/courses"
HEADERS = {"Accept": "application/json", "User-Agent": "social-computing-www-bot"}


def study_years():
    year = datetime.date.today().year
    return [year - 1, year, year + 1]


def hit_to_offering(hit):
    period = hit.get("activityPeriod", {}) or {}
    return {
        "name": (hit.get("cuName") or {}).get("en"),
        "start_date": period.get("startDate"),
        "end_date": period.get("endDate"),
        "url": (
            "https://studies.helsinki.fi" + hit["coursePageUrl"]
            if hit.get("coursePageUrl")
            else f"https://studies.helsinki.fi/kurssit?searchText={hit.get('code', '')}"
        ),
    }


def resolve_code(code):
    """Find offerings of `code` across nearby study years and pick the
    soonest upcoming one, falling back to the most recent past one."""
    today = datetime.date.today().isoformat()
    offerings = []
    for year in study_years():
        try:
            resp = requests.get(
                SEARCH_URL,
                params={
                    "lang": "en",
                    "page": 0,
                    "searchText": code,
                    "showExams": "false",
                    "sort": "relevance",
                    "studyYear": year,
                },
                headers=HEADERS,
                timeout=30,
            )
            resp.raise_for_status()
        except requests.RequestException as exc:
            print(f"  warning: search failed for code {code!r} year {year}: {exc}")
            continue

        for hit in resp.json().get("hits", []):
            # The API wraps codes in stray U+241F separators, e.g. "␟COS-D421␟".
            hit_code = re.sub(r"[^\w-]", "", hit.get("code") or "")
            if hit_code != code:
                continue
            offerings.append(hit_to_offering(hit))

    if not offerings:
        return None

    upcoming = sorted((o for o in offerings if (o["start_date"] or "") >= today), key=lambda o: o["start_date"])
    if upcoming:
        return upcoming[0]
    past = sorted((o for o in offerings if o["start_date"]), key=lambda o: o["start_date"], reverse=True)
    return past[0] if past else offerings[0]


def resolve_course(course):
    # A `name` in courses.yaml is only used for courses without a `code` —
    # for coded courses the real name is pulled from the API below, since
    # the university's own official name is more likely to stay current
    # than a hand-maintained copy.
    fallback_name = course.get("name") or course.get("code")
    resolved = {"name": fallback_name, "code": course.get("code")}

    if course.get("code"):
        offering = resolve_code(course["code"])
        if offering:
            resolved.update(offering)
            resolved["name"] = offering["name"] or fallback_name
        else:
            print(f"  warning: no offering found for code {course['code']!r}")
            resolved["url"] = f"https://studies.helsinki.fi/kurssit?searchText={course['code']}"
    elif course.get("url"):
        resolved["url"] = course["url"]

    return resolved


def main():
    with open(COURSES_PATH) as f:
        sections = yaml.safe_load(f)

    resolved_sections = []
    for section in sections:
        print(f"Resolving header: {section['header']}")
        courses = []
        for course in section["courses"]:
            label = course.get("name") or course.get("code")
            print(f"  {label}" + (f" ({course['code']})" if course.get("code") else ""))
            courses.append(resolve_course(course))
        resolved_sections.append({"header": section["header"], "courses": courses})

    with open(OUTPUT_PATH, "w") as f:
        json.dump(resolved_sections, f, indent=2, ensure_ascii=False)
        f.write("\n")

    total = sum(len(s["courses"]) for s in resolved_sections)
    print(f"Wrote {total} course entries across {len(resolved_sections)} headers to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
