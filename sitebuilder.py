#!/usr/bin/env python3
"""
MyGirlHub Site Builder
======================
Shared functions for building/updating the static site.
Used by both builder.py (migration) and publisher.py (new videos).

PERFORMER NAME RULE
-------------------
Performer names are ALWAYS a single word (no spaces).
  correct:   "Nadiabliss", "AlicePirce", "MFCgoddess"
  incorrect: "Nadiabliss Naked", "Alice Pirce", "MFC goddess"

Use clean_performer(name) before storing any performer value.
The performer_slug is always slugify(clean_performer(name)).
"""

import os, json, re, logging
from templates import (
    render_homepage, render_video_page,
    render_category_page, render_sitemap, render_robots,
    PER_PAGE
)

AGE_GATE_MARKER = 'id="age-gate"'
log = logging.getLogger(__name__)


# ── PERFORMER CLEANING ────────────────────────────────────────────────

def clean_performer(name):
    """
    Enforce the single-word performer name rule.

    Logic:
    - Strip leading/trailing whitespace
    - Remove trailing date/number suffixes (e.g. "2026", "07", "2025-12-05")
    - If two words remain and BOTH look like proper name components
      (capitalised, alpha only, length > 2, not a common descriptor),
      join them: "Alice Pirce" -> "AlicePirce", "Emily Kim" -> "EmilyKim"
    - Otherwise take only the first word

    Examples:
      "Nadiabliss Naked"    -> "Nadiabliss"
      "Alice Pirce"         -> "AlicePirce"
      "mfcgoddess 2026"     -> "mfcgoddess"
      "Yukenzi Big Nipples" -> "Yukenzi"
      "  nadiabliss  "      -> "nadiabliss"
      "Serene Sophie"       -> "SereneSophie"
    """
    # Common English descriptors / content words that are NOT name parts.
    # If either word of a two-word string matches these, take first word only.
    DESCRIPTORS = {
        'naked', 'nude', 'sexy', 'hot', 'big', 'huge', 'tits', 'boobs',
        'ass', 'busty', 'blonde', 'brunette', 'redhead', 'superhot', 'super',
        'cute', 'sweet', 'model', 'girl', 'cam', 'live', 'free', 'new',
        'video', 'show', 'fun', 'nice', 'wild', 'naughty', 'natural',
        'first', 'second', 'best', 'top', 'exclusive', 'special',
        'highlights', 'catalog', 'collection', 'adventure', 'vlog',
        'episode', 'series', 'great', 'amazing', 'incredible',
        # content/descriptor words seen in real data
        'blowjob', 'asian', 'latina', 'eastern', 'western', 'beautiful',
        'middle', 'topless', 'gorgeous', 'stunning', 'young', 'mature',
        'milf', 'teen', 'ebony', 'petite', 'thick', 'curvy', 'skinny',
        'long', 'dark', 'light', 'black', 'white', 'pink', 'wet',
        'sexy', 'naughty', 'dirty', 'horny', 'tight', 'perfect',
        'recording', 'screen', 'famous', 'world',
    }

    if not name:
        return "Unknown"
    name = str(name).strip()
    # Remove trailing date/number suffixes
    name = re.sub(r'\s+\d[\d\-]*$', '', name).strip()
    parts = name.split()
    if len(parts) == 1:
        return parts[0]

    # Two capitalised alpha words that look like first + last name parts
    # (neither is a known descriptor) -> join them
    if (len(parts) == 2
            and parts[0][0].isupper() and parts[1][0].isupper()
            and parts[0].isalpha() and parts[1].isalpha()
            and len(parts[0]) > 2 and len(parts[1]) > 2
            and parts[0].lower() not in DESCRIPTORS
            and parts[1].lower() not in DESCRIPTORS):
        return parts[0] + parts[1]

    # Default: first word only
    return parts[0]


def slugify(text):
    text = str(text).lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    return text.strip('-')


def performer_slug(name):
    """Always derive performer slug from the cleaned single-word name."""
    return slugify(clean_performer(name))


# ── DATA HELPERS ──────────────────────────────────────────────────────

def load_videos(data_path):
    try:
        with open(data_path) as f:
            return json.load(f)
    except Exception:
        return []


def save_videos(data_path, videos):
    with open(data_path, 'w') as f:
        json.dump(videos, f, indent=2)


def normalise_video(v):
    """
    Ensure a video dict has a clean single-word performer and matching slug.
    Safe to call on both new and existing records.
    """
    raw   = v.get('performer', 'Unknown')
    clean = clean_performer(raw)
    v['performer']      = clean
    v['performer_slug'] = slugify(clean)
    return v


def get_categories(videos):
    """
    Build category list. Groups by performer_slug so one performer = one
    category regardless of any historical name variations.
    """
    cats = {}
    for v in videos:
        slug = v['performer_slug']
        name = v['performer']
        if slug not in cats:
            cats[slug] = {'name': name, 'slug': slug, 'count': 0}
        cats[slug]['count'] += 1
    return list(cats.values())


# ── FILE WRITING ──────────────────────────────────────────────────────

def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    log.info(f"Written: {path}")


def _ensure_age_gate_in_html(html_content, label="page"):
    if AGE_GATE_MARKER not in html_content:
        raise RuntimeError(f"Age gate missing in {label}")


# ── SLUG DEDUPLICATION ────────────────────────────────────────────────

def _dedup_slug(slug, seen_slugs):
    """Append -2, -3 etc. until slug is unique. Mutates seen_slugs."""
    if slug not in seen_slugs:
        seen_slugs.add(slug)
        return slug
    counter = 2
    while f"{slug}-{counter}" in seen_slugs:
        counter += 1
    unique = f"{slug}-{counter}"
    seen_slugs.add(unique)
    return unique


# ── PAGE BUILDERS ─────────────────────────────────────────────────────

def _build_homepage_pages(output_dir, videos, categories):
    total_pages = max(1, (len(videos) + PER_PAGE - 1) // PER_PAGE)
    for page in range(1, total_pages + 1):
        html = render_homepage(videos, categories, page=page)
        _ensure_age_gate_in_html(html, f"index page {page}")
        if page == 1:
            write(f"{output_dir}/index.html", html)
        else:
            write(f"{output_dir}/page/{page}/index.html", html)


def _build_category_pages(output_dir, cat, cat_videos):
    slug = cat['slug'] if isinstance(cat, dict) else cat
    name = cat['name'] if isinstance(cat, dict) else cat
    total_pages = max(1, (len(cat_videos) + PER_PAGE - 1) // PER_PAGE)
    for page in range(1, total_pages + 1):
        html = render_category_page(name, slug, cat_videos, page=page)
        _ensure_age_gate_in_html(html, f"category/{slug} page {page}")
        if page == 1:
            write(f"{output_dir}/category/{slug}/index.html", html)
        else:
            write(f"{output_dir}/category/{slug}/page/{page}/index.html", html)


# ── MAIN BUILD ────────────────────────────────────────────────────────

def build_site(output_dir, data_path):
    """Rebuild entire site from videos data."""
    raw_videos = load_videos(data_path)

    # Enforce single-word performer rule on every record
    videos = [normalise_video(v) for v in raw_videos]

    # Deduplicate slugs
    seen = set()
    for v in videos:
        v['slug'] = _dedup_slug(v['slug'], seen)

    categories = get_categories(videos)
    log.info(f"Building site: {len(videos)} videos, {len(categories)} performers")

    _build_homepage_pages(output_dir, videos, categories)

    for v in videos:
        html = render_video_page(v, all_videos=videos)
        _ensure_age_gate_in_html(html, f"video/{v['slug']}")
        write(f"{output_dir}/videos/{v['slug']}/index.html", html)

    for cat in categories:
        cat_videos = [v for v in videos if v['performer_slug'] == cat['slug']]
        _build_category_pages(output_dir, cat, cat_videos)

    write(f"{output_dir}/sitemap.xml", render_sitemap(videos))
    write(f"{output_dir}/robots.txt", render_robots())
    _write_legal_pages(output_dir)

    log.info("Site build complete")
    return len(videos)


def add_video_and_rebuild(output_dir, data_path, new_video):
    """Add one new video and rebuild only affected pages."""
    videos = load_videos(data_path)

    normalise_video(new_video)

    if any(v['guid'] == new_video['guid'] for v in videos):
        log.warning(f"Duplicate GUID skipped: {new_video['guid']}")
        return False

    seen = {v['slug'] for v in videos}
    new_video['slug'] = _dedup_slug(new_video['slug'], seen)

    videos.insert(0, new_video)
    videos = [normalise_video(v) for v in videos]
    save_videos(data_path, videos)

    categories = get_categories(videos)

    _build_homepage_pages(output_dir, videos, categories)

    html = render_video_page(new_video, all_videos=videos)
    _ensure_age_gate_in_html(html, f"video/{new_video['slug']}")
    write(f"{output_dir}/videos/{new_video['slug']}/index.html", html)

    slug = new_video['performer_slug']
    cat_videos = [v for v in videos if v['performer_slug'] == slug]
    cat = {'name': new_video['performer'], 'slug': slug}
    _build_category_pages(output_dir, cat, cat_videos)

    write(f"{output_dir}/sitemap.xml", render_sitemap(videos))

    log.info(f"Site updated: {new_video['title']}")
    return True


# ── LEGAL PAGES ───────────────────────────────────────────────────────

def _write_legal_pages(output_dir):
    from templates import HEAD_CSS, GA_HEAD, BODY_START, SITE_URL, header_html, footer_html

    privacy = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Privacy Policy | MyGirlHub</title>
<link rel="canonical" href="{SITE_URL}/privacy.html">
{GA_HEAD}{HEAD_CSS}
</head>
{BODY_START}{header_html()}
<div class="page-wrap"><div class="main-content" style="max-width:800px;">
<h1 style="font-family:'Bebas Neue',sans-serif;font-size:32px;letter-spacing:2px;margin-bottom:24px;">Privacy Policy</h1>
<p style="color:var(--muted);font-size:12px;margin-bottom:24px;">Last updated: March 2026</p>
<h2 style="font-size:16px;font-weight:600;margin-bottom:10px;color:var(--text2);">1. Information We Collect</h2>
<p style="color:var(--text2);font-size:14px;line-height:1.75;margin-bottom:20px;">We collect anonymised usage data through Google Analytics (page views, session duration, device type). We do not collect personally identifiable information. Age verification uses a session cookie storing only a verification flag — no date of birth is retained.</p>
<h2 style="font-size:16px;font-weight:600;margin-bottom:10px;color:var(--text2);">2. Cookies</h2>
<p style="color:var(--text2);font-size:14px;line-height:1.75;margin-bottom:20px;">We use: (a) an age verification cookie (30-day expiry); (b) Google Analytics for aggregate traffic analysis. Disabling cookies will require re-verification of age on each visit.</p>
<h2 style="font-size:16px;font-weight:600;margin-bottom:10px;color:var(--text2);">3. Third-Party Services</h2>
<p style="color:var(--text2);font-size:14px;line-height:1.75;margin-bottom:20px;">Video content is embedded via Bunny.net CDN and live cam widgets via MyFreeCams. These services may set their own cookies. Affiliate links are governed by those sites' own privacy policies.</p>
<h2 style="font-size:16px;font-weight:600;margin-bottom:10px;color:var(--text2);">4. Australian Privacy Act Compliance</h2>
<p style="color:var(--text2);font-size:14px;line-height:1.75;margin-bottom:20px;">This site complies with the Australian Privacy Act 1988 and the Online Safety Act 2021. Age assurance is implemented before displaying explicit content. Contact us via the <a href="/content-removal.html" style="color:var(--accent);">DMCA / Content Removal</a> page for privacy enquiries.</p>
</div></div>
{footer_html()}
</body></html>'''

    c2257 = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>18 U.S.C. 2257 Compliance | MyGirlHub</title>
<link rel="canonical" href="{SITE_URL}/2257.html">
{GA_HEAD}{HEAD_CSS}
</head>
{BODY_START}{header_html()}
<div class="page-wrap"><div class="main-content" style="max-width:800px;">
<h1 style="font-family:'Bebas Neue',sans-serif;font-size:32px;letter-spacing:2px;margin-bottom:24px;">18 U.S.C. 2257 Compliance</h1>
<p style="color:var(--text2);font-size:14px;line-height:1.75;margin-bottom:20px;">MyGirlHub.com is a content aggregation and linking website. All videos are hosted by third-party providers including Bunny.net CDN and sourced from licensed cam platforms.</p>
<p style="color:var(--text2);font-size:14px;line-height:1.75;margin-bottom:20px;">All models, actors, actresses and other persons appearing in any visual depiction of sexually explicit conduct were over the age of eighteen (18) at the time of creation of such depictions.</p>
<p style="color:var(--text2);font-size:14px;line-height:1.75;margin-bottom:20px;">Records required by 18 U.S.C. §2257 and 28 C.F.R. §75 are maintained by the original content producers. MyGirlHub.com is not the primary producer of content displayed herein.</p>
<p style="color:var(--text2);font-size:14px;line-height:1.75;margin-bottom:20px;">For removal requests: <a href="/content-removal.html" style="color:var(--accent);">DMCA / Content Removal</a>.</p>
</div></div>
{footer_html()}
</body></html>'''

    write(f"{output_dir}/privacy.html", privacy)
    write(f"{output_dir}/2257.html", c2257)
