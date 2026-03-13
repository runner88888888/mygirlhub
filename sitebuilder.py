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
    render_category_page, render_tag_page,
    render_sitemap, render_robots,
    PER_PAGE
)

AGE_GATE_MARKER = 'id="age-gate"'
log = logging.getLogger(__name__)

# Category slugs we never expose (no category page, no pill). Videos are recategorised from description when possible.
JUNK_CATEGORY_SLUGS = {
    'screenrecording', 'mfcgoddessasian', 'linaresjesicabig',
    'recording', 'screen', 'unknown',
}


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


def _first_word_from_description(desc):
    """First word (no spaces) of description for recategorising junk performer data."""
    if not desc:
        return None
    parts = str(desc).strip().split()
    return parts[0] if parts else None


def normalise_video(v):
    """
    Ensure a video dict has a clean single-word performer and matching slug.
    Safe to call on both new and existing records.
    If current performer_slug is in JUNK_CATEGORY_SLUGS, try to recategorise
    from the first word of description (rule: first word = model name = category).
    """
    raw   = v.get('performer', 'Unknown')
    clean = clean_performer(raw)
    v['performer']      = clean
    v['performer_slug'] = slugify(clean)

    if v['performer_slug'] in JUNK_CATEGORY_SLUGS and v.get('description'):
        first = _first_word_from_description(v['description'])
        if first:
            recat = clean_performer(first)
            recat_slug = slugify(recat)
            if recat_slug and recat_slug not in JUNK_CATEGORY_SLUGS:
                v['performer'] = recat
                v['performer_slug'] = recat_slug
                log.debug("Recategorised video from description: %s -> %s", raw, recat)
    return v


def get_categories(videos):
    """
    Build category list. Groups by performer_slug so one performer = one
    category regardless of any historical name variations.
    Junk category slugs are excluded (no category page or nav pill).
    """
    cats = {}
    for v in videos:
        slug = v['performer_slug']
        if slug in JUNK_CATEGORY_SLUGS:
            continue
        name = v['performer']
        if slug not in cats:
            cats[slug] = {'name': name, 'slug': slug, 'count': 0}
        cats[slug]['count'] += 1
    return list(cats.values())


def get_tags(videos):
    """
    Build tag list from all videos. Each unique tag (by slug) appears once.
    Tags that slugify to the same (e.g. 'Live Cam' and 'live cam') are merged.
    """
    by_slug = {}
    for v in videos:
        for t in v.get('tags') or []:
            if not t or not str(t).strip():
                continue
            slug = slugify(str(t).strip())
            if not slug:
                continue
            if slug not in by_slug:
                by_slug[slug] = {'name': str(t).strip(), 'slug': slug, 'count': 0}
            by_slug[slug]['count'] += 1
    return list(by_slug.values())


def _build_tag_pages(output_dir, tag, tag_videos):
    slug = tag['slug']
    name = tag['name']
    total_pages = max(1, (len(tag_videos) + PER_PAGE - 1) // PER_PAGE)
    for page in range(1, total_pages + 1):
        html = render_tag_page(name, slug, tag_videos, page=page)
        _ensure_age_gate_in_html(html, f"tag/{slug} page {page}")
        if page == 1:
            write(f"{output_dir}/tag/{slug}/index.html", html)
        else:
            write(f"{output_dir}/tag/{slug}/page/{page}/index.html", html)


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

    tags = get_tags(videos)
    for tag in tags:
        tag_videos = [v for v in videos if tag['slug'] in [slugify(str(t).strip()) for t in (v.get('tags') or []) if t]]
        _build_tag_pages(output_dir, tag, tag_videos)

    write(f"{output_dir}/sitemap.xml", render_sitemap(videos, category_slugs={c['slug'] for c in categories}, tag_slugs={t['slug'] for t in tags}))
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
    if slug not in JUNK_CATEGORY_SLUGS:
        cat_videos = [v for v in videos if v['performer_slug'] == slug]
        cat = {'name': new_video['performer'], 'slug': slug}
        _build_category_pages(output_dir, cat, cat_videos)

    tags = get_tags(videos)
    for tag in tags:
        tag_videos = [v for v in videos if tag['slug'] in [slugify(str(t).strip()) for t in (v.get('tags') or []) if t]]
        _build_tag_pages(output_dir, tag, tag_videos)

    write(f"{output_dir}/sitemap.xml", render_sitemap(videos, category_slugs={c['slug'] for c in categories}, tag_slugs={t['slug'] for t in tags}))

    log.info(f"Site updated: {new_video['title']}")
    return True


# ── LEGAL PAGES ───────────────────────────────────────────────────────

def _write_legal_pages(output_dir):
    from templates import (
        render_privacy,
        render_2257,
        render_dmca,
        render_terms,
        render_contact,
    )

    write(f"{output_dir}/privacy.html", render_privacy())
    write(f"{output_dir}/2257.html", render_2257())
    write(f"{output_dir}/content-removal.html", render_dmca())
    write(f"{output_dir}/terms.html", render_terms())
    write(f"{output_dir}/contact.html", render_contact())
