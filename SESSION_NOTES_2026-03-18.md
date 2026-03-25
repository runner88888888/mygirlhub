# Session notes — 18 Mar 2026 (end of day)

## Docker / deploy (source of truth)

- **Container mounts (Portainer):**
  - `/share/Container/mygirlhub` → `/app` (code + builder)
  - `/share/Container/mygirlhub/site` → `/site` (static output)
  - `/share/ToPublish` → `/watch`
- **Rebuild command** (inside container, from `/app`):
  ```bash
  cd /app
  # Second arg must be site/videos.json (NOT bare videos.json — that resolves to /app/videos.json).
  python -c "import sitebuilder; sitebuilder.build_site('site', 'site/videos.json')"
  ```
  Safer: use `rebuild_site.py` with `REBUILD_DATA=/site/videos.json` (see PORTAINER.md).
- **`python sitebuilder.py` alone does nothing** — no `if __name__ == "__main__"`; use the `-c` line above.

## PC vs NAS — “old code” feeling

- **Cursor / `Documents\Mygirlhub`** is **not** what the container reads.
- The container only sees **NAS** `/share/Container/mygirlhub` as `/app`.
- After editing on PC: **sync to NAS** (git pull on NAS, copy files, etc.) **then** rebuild. Otherwise rebuild uses stale NAS files.

## Video cards / grey tiles (what we learned)

- User confirmed **Bunny thumbs and Cloudflare** are OK for their checks; focus stayed on HTML/JS.
- **Hover preview** (`THUMB_PREVIEW_SCRIPT` in `templates.py`): only attaches if each card has `.thumb-wrap img` with both `data-thumb-url` and `data-preview-url`.
- **Empty `<a class="video-card" href="..."></a>`** in Elements = that card has **no inner HTML** in what the browser got (not normal for current `video_card_html`). Worth checking **View page source** for same `href` vs live DOM after load.
- **`THUMB_HEALTH_SCRIPT`**: was hiding cards when thumbs looked “broken”; user saw grid flash then collapse. **Change applied in repo:** script is now a **no-op** (disabled) so cards are not removed client-side. **Ensure NAS `templates.py` matches repo** after sync + rebuild.

## Next session (optional)

1. Confirm NAS `templates.py` includes the disabled thumb-health no-op (match git/PC).
2. If empty `video-card` links still appear: inspect generated `site/index.html` on NAS for that slug; trace whether `_filter_displayable` or another path emits incomplete markup.
3. Optional: add `if __name__ == "__main__":` in `sitebuilder.py` calling `build_site` so `python sitebuilder.py` is enough.

---
*End here for 18 Mar 2026.*
