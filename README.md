# Social Computing

Jekyll site for the [Helsinki Social Computing Group](https://www.helsinki.fi/en/researchgroups/social-computing),
built for GitHub Pages.

## Design system

Built on the real [University of Helsinki Design System component
library](https://designsystem.helsinki.fi/2de013a32/p/574a88-developers)
(`@uh-design-system/component-library`), loaded from Datacloud — the
no-build-step distribution channel, appropriate since this is a plain Jekyll
site with no npm build step. See `_layouts/default.html` for the three
`<link>`/`<script>` tags (component CSS, fonts CSS, loader script) and
`_config.yml` for the pinned `ds_version`. Datacloud only serves specific
versions (no "latest" alias), so bumping the library means bumping
`ds_version` by hand — check [the package on
npm](https://www.npmjs.com/package/@uh-design-system/component-library) for
the current release.

Templates use the actual `<ds-*>` custom elements (`ds-card`, `ds-link`,
`ds-button`, `ds-action-menu`, `ds-badge`, `ds-divider`, `ds-grid`) rather
than hand-rolled markup — see `_includes/nav.html` and `content/people.md`.
`assets/css/layout.css` handles page composition only (header/nav/footer
layout, grid spacing) and reuses the `--ds-*` custom properties the
component library already defines at `:root`; it does not redeclare any
design tokens itself.

The footer carries the University of Helsinki crest
(`_includes/uh-logo.html`, included from `_includes/footer.html`), just
the emblem mark with no wordmark. It isn't part of the public component
library, so its SVG path was extracted directly from the real site's own
`hy-icon-hy-logo` component bundle. It's inlined as raw `<svg
fill="currentColor">` rather than `<img src="...">`, so it can actually
pick up this context's CSS color — an `<img>`-referenced SVG can't see
page CSS. `.uh-logo__mark` in `assets/css/layout.css` has a 2rem fallback
size so the crest never silently collapses to 0×0 (an `<svg>` with only a
`viewBox`, no `width`/`height`, does that as a flex child) if it isn't
otherwise sized.

Checked against the official rules at
https://www.helsinki.fi/en/brand-book/brand-and-logo: the emblem should be
"almost exclusively" paired with the "UNIVERSITY OF HELSINKI" wordmark,
never shown alone, and only ever black on light surfaces or white
(negative) on dark/photo surfaces. The current markup shows the emblem
alone (white, on the black footer), which departs from that "never shown
alone" rule — `assets/css/layout.css` still has `.uh-logo--header`/
`.uh-logo--footer` rules built for a wordmark-plus-emblem lockup (the
brand book's centred "basic format"), but `_includes/uh-logo.html` no
longer renders any wordmark markup for those rules to size or position,
so they're currently inert. The header doesn't show any UH logo at all.

## Structure

### Content & navigation

All editorial pages live under `content/`. The main menu
(`_includes/nav.html`) is generated from that folder's layout, ordered by
each page's `nav_order` front matter (currently Home=0, People=1,
Research=2, Methodological development=3, Publications=4, Teaching=5 —
edit that field to reorder; pages without it sort last):

- A file directly in `content/` (e.g. `content/people.md`) becomes a
  top-level menu link, rendered as a real `<ds-link>` anchor. This includes
  `content/index.md` itself (the homepage), which shows up as "Home".
- A subfolder would become a dropdown (`<ds-action-menu>`/
  `<ds-action-list-item>`, the design system's own disclosure-menu pattern),
  with each file inside it as a popup item — see `assets/js/nav.js` for the
  `dsSelect`-based navigation this requires, since `ds-action-list-item` has
  no `href` of its own. Nothing currently uses this (Research is a single
  page, see below), but the mechanism is there if a section ever needs it.
  `jekyll-sitemap` is enabled so pages reachable only from inside a
  JS-driven popup would still stay crawlable.

Nav text (link labels, the "MENU" mobile toggle, the brand name) is
uppercased with Liquid's `| upcase` on the source string in
`_includes/nav.html`, not CSS `text-transform`. The `ds-button`/`ds-link`/
`ds-action-menu` components are Stencil "scoped" components, not real
shadow DOM (`element.shadowRoot` is `null`), but they still render their
label text through their own internal markup, which has its own
`text-transform` that wins over anything inherited from an ancestor — so
forcing the actual case at the template level is the only reliable fix.
The nav also sets `font-family: var(--ds-fontFamily-body)` explicitly on
`.site-nav` (Open Sans) — this one *is* just inheritance, already true by
default since `body` sets the same, but stated so the nav doesn't silently
depend on that.

### Data

- `_data/people.yaml` — group members (name, image, description, alumni
  status, ORCID iD). Rendered on `content/people.md`, alphabetically by
  first name, current members separate from alumni. One-off data, not
  auto-updated. Photos are downloaded to `assets/images/people/` by
  `scripts/download_people_images.py` (re-run by hand after changing an
  image URL in this file). `orcid` is only populated for current members —
  it drives publication fetching (see below) — and left blank where no
  public ORCID record could be found (currently just Otso Rajala).
- `_data/focus_areas.yaml` — the group's two research focus areas (name,
  `slug`, banner image, description mirroring
  https://www.helsinki.fi/en/researchgroups/social-computing/projects).
  Slugs are short and simple (`digital-society`, `dcm`) — this is the
  cross-reference key: `_data/people.yaml` lists which slugs a person
  belongs to (`focus_areas: [slug, ...]` — e.g. Matti Nelimarkka has both),
  and `_data/projects.yaml` tags each project with one
  (`focus_area: slug`). Rename a slug and update it in both files to match.
  Rendered on `content/projects.md` (served at `/research/` — see below) as
  a hero-style block per area (large image left, heading/description/
  researchers right — matching
  https://www.helsinki.fi/en/researchgroups/social-computing/projects,
  stacking to image-on-top on mobile), each with `id="{{ area.slug }}"` so
  `/research/#dcm` links straight to a section, followed by that area's
  projects. Researchers (current members whose `focus_areas` contains the
  slug) show as a small photo (capped at 50px, see `.researcher-chip` in
  `assets/css/layout.css`) + name chip, not a text badge — missing photos
  (e.g. Jesse Haapoja) fall back to a plain grey circle. One-off data, not
  auto-updated.
- `_data/projects.yaml` — research projects (name, description, funder,
  start/end year, `focus_area` slug). One-off data, not auto-updated.
- `content/methods.md` (`/methods/`) is plain markdown, not data-driven —
  each method is just a `##` heading, a paragraph and a couple of markdown
  links, copied from
  https://www.helsinki.fi/en/researchgroups/social-computing/methodological-development.
  There used to be a `_data/methods.yaml` backing it; it was folded
  straight into the page to make editing a method (or adding a new one) a
  single markdown edit instead of touching two files.
- `_data/courses.yaml` — the manually curated, editable source for the
  Teaching page: a list of headers (currently "Digital society and
  politics" and "Digital and computational methods", matching
  https://www.helsinki.fi/en/researchgroups/social-computing/teaching), each
  with a list of courses. A course needs either a `code` (University of
  Helsinki course code, e.g. `COS-D421` — resolved daily against the course
  catalogue for its real link, dates, *and* current official name; any
  `name` given alongside a `code` is ignored, kept only as a trailing
  comment for human reference when hand-editing) or a `name` on its own,
  optionally with a direct `url` (used as-is, no lookup — most of the
  source page's course names don't map to a code we know).
- `_data/teaching.json` — generated daily by `scripts/fetch_teaching.py`
  (JSON, like `publications.json` and `blog_posts.json`, for consistency —
  `_data/courses.yaml` is the only hand-edited course data), which resolves
  every `code` in `_data/courses.yaml` against the [course search
  API](https://studies.helsinki.fi/kurssit) (the soonest upcoming offering,
  falling back to the most recent past one) while preserving the
  header groups. Do not edit by hand — edit `_data/courses.yaml` instead.
  Note: that API wraps course codes in stray `␟` separator characters
  (e.g. `␟COS-D421␟`), so the lookup strips those before comparing. The
  Teaching page itself (`content/teaching.md`) renders this through
  `_includes/course-list.html`, which also decides whether to label each
  course "next teaching time" or "last teaching time" by comparing
  today's date against the resolved `start_date`.
- `_data/publications.json` — a single JSON array, generated daily by
  `scripts/fetch_publications.py`, which fetches from the
  [ORCID public API](https://pub.orcid.org) for every current member with an
  `orcid` in `_data/people.yaml`. A paper co-authored by more than one group
  member is written once — deduplicated by DOI (falling back to a slugified
  title for the rare work without one) — with an `authors` list naming
  every group member found on it. Each publication with a DOI also gets a
  full, untruncated `abstract`: pulled from the same Crossref lookup already
  used for author matching where available (~60% of DOIs in practice, tags
  stripped), falling back to one batched
  [Semantic Scholar Graph API](https://api.semanticscholar.org) lookup for
  any DOI Crossref missed. No DOI, or neither source has an abstract, means
  no `abstract` key — same soft-fail spirit as `blog_posts.json`. Do not edit
  by hand. Powers the "Recent publications" list on `content/index.md` (5
  most recent, sorted by full publication date where ORCID provides one;
  format: "Title: Venue (Year) [Author] [Author]", plus an abstract teaser
  — `{{ pub.abstract | truncatewords: 30 }}` — styled to match the "Recent
  blog posts" column right next to it), `content/publications.md` (all of
  them, same format *without* the abstract teaser, 25 at a time with a "Load
  more" button — see `assets/js/load-more.js`), and the hand-rolled RSS feed
  at `feed/publications.xml` (`/feed/publications.xml` — a plain Liquid
  template over `site.data.publications`, not a Jekyll collection, since
  there's no per-publication page anymore).
- `_data/blog_posts.json` — generated daily by `scripts/fetch_blog_posts.py`
  from the group's Substack RSS feed
  (https://sociallycompute.substack.com/feed — this is the actual feed
  behind "Recent blog posts" on the source homepage; found by inspecting the
  network requests the live site's blog widget makes, since the widget
  itself just points at an internal Drupal block id). Do not edit by hand.
  Powers the "Recent blog posts" column on `content/index.md` (5 most
  recent).
- `_data/cowork.json` — a single JSON array, generated daily by
  `scripts/fetch_cowork.py` from a private Notion database
  (https://www.notion.so/matnel/7f67eaa07e10418497bb03da9627d632) where
  Matti tracks individual research project and thesis topic ideas. Only
  rows with the "Available" checkbox on are included; each entry carries
  its Notion "Multi-select" categories (`"Small project"` and/or
  `"Thesis topic"`). Reading the database needs a Notion integration token
  with the database shared to it, set as the `NOTION_TOKEN` secret/env var
  — without it the script writes an empty list rather than failing the
  build. Do not edit by hand. Powers `content/cowork.md` (`/work-with-us`),
  which filters this one list into its "Individual research project" and
  "Master thesis supervision" sections via `_includes/cowork-list.html`,
  rendering each topic as a `<ds-accordion>` (header = title, content =
  description plus work-area/paid-position/Finnish-skill badges).

`content/index.md` otherwise mirrors
https://www.helsinki.fi/en/researchgroups/social-computing directly: the
same hero image and intro copy, the same three image link-boxes (Research
projects / People / Methods renewal, rendered as `<ds-card>`), and — where
the source page has "Recent blog posts" above "Recent academic
publications" stacked vertically — a two-column `<ds-grid>` with blog posts
and publications side by side. Images for all of this live in
`assets/images/home/`.

The hero itself (`.hero` in `assets/css/layout.css`) is full viewport width
— it breaks out of `main.wrapper`'s centered max-width with the standard
`width: 100vw; margin-left: calc(50% - 50vw)` trick — with the photo as a
true background and the heading/tagline overlaid on top of a dark gradient
scrim for contrast (a horizontal gradient on desktop, since the text sits
on the left; a bottom-heavy vertical one on mobile, since the text stacks
at the bottom of the image there). The source page uses a fancier `hy-hero`
component with a colour variant that isn't part of the public component
library, so this is a hand-styled equivalent, not a 1:1 copy.

## Automation

`.github/workflows/pages.yml` is the only workflow. On every push to `main`,
on a daily schedule (04:00 UTC), and on manual dispatch, it: fetches
publications, blog posts, teaching data and co-working opportunities fresh
into the checkout, builds the Jekyll site with that data, and deploys the
result to GitHub Pages. The `NOTION_TOKEN` secret (see `_data/cowork.json`
above) needs to be set in the repo's Actions secrets for the co-working
fetch to return real data; it fails soft (empty list) if missing.

The fetched data is **never committed back to the repo** — it only ever
lives in that run's build output, uploaded as the Pages deployment
artifact. This keeps the repo's history free of daily bot commits; the
tradeoff is that a fresh local checkout won't have current publications/
blog posts/teaching data until you run the fetch scripts yourself (see
below) — `site.data.publications` etc. are just empty/undefined until you
do, which Jekyll and Liquid handle fine (empty lists, not errors).

## Local development

```sh
bundle install
bundle exec jekyll serve
```

To refresh the generated data by hand:

```sh
pip install requests pyyaml python-dotenv
python scripts/fetch_publications.py
python scripts/fetch_blog_posts.py
python scripts/fetch_teaching.py
python scripts/fetch_cowork.py  # needs a Notion integration token — see below
python scripts/download_people_images.py  # after editing image URLs in _data/people.yaml
```

`fetch_cowork.py` needs `NOTION_TOKEN` set. Rather than exporting it by hand every
time, drop it in a `.env` file at the repo root (already gitignored, never
committed):

```sh
echo "NOTION_TOKEN=<your integration token>" > .env
```

`python-dotenv` (installed above) loads it automatically; if it's not
installed, the script just skips loading `.env` and falls back to
whatever's already in the environment.
