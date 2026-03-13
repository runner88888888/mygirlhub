# Backlog

Pending items for future sessions.

---

## SEO (priority)

- **SEO strategy and implementation plan** — ✅ Done. See [SEO_STRATEGY.md](SEO_STRATEGY.md) for full strategy and phased implementation plan.

---

## Site / content

- **Junk category pages** — Delete junk categories (ScreenRecording, MFCgoddessAsian, LinaresjesicaBig, etc.) and **recategorise videos properly**. Rule: **first word of the description (no spaces) = model name = category**. So e.g. "MFCgoddess Asian" → performer/category = `MFCgoddess`; clean category names only. Implement filtering/recategorisation in `sitebuilder.py` (or a one-off data fix in `videos.json` + rebuild).

- **Refine use of tags** — ✅ Tag links now go to `/tag/{slug}/` and show all videos with that tag (e.g. “live cam” → live-cam). Generation and SEO can be refined further if needed.

---

## UX / display

- **Gallery layout redesign** — Thumb-on-top, compact label block (less vertical space, smaller fonts, line-clamp). Responsive. More visuals, less text, no brick pattern. See discussion in chat.

- **Galleries load in random order** — Make video grids (homepage, category pages) load in **random order** instead of fixed date/title order, so returning visitors see variety.

---

## Analytics

- **Set up Google Analytics** — Proper GA4 setup: property, streams, goals, and integration in templates (verify existing GA_HEAD usage and complete configuration).

---

## Infrastructure

- **MySQL database migration on Hostinger** — Someday maybe; keep as backlog note for now.
