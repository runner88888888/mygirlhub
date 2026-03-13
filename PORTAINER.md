# Portainer / NAS – MyGirlHub Operations Guide

Containers mount **the whole repo** as `/app`, so the code that runs is exactly what's in your NAS project folder. Edits you make there (or sync via Git) are what the container uses.

---

## Stack volumes (canonical — do not revert)

The publisher stack **must** use a **full-directory mount**. Do not use per-file mounts; that caused path confusion and updates not reaching the container.

**Correct volumes in Portainer (mygirlhub_publisher stack):**

```yaml
volumes:
  - /share/Container/mygirlhub:/app
  - /share/ToPublish:/watch
```

If your NAS uses a different host path for the repo (e.g. `/share/SystemSSD/Container/mygirlhub`), use that path for the first line; keep `:/app` and `:/watch` as shown.

**Why this is in the repo:** `docker-compose.example.yml` and this section are the **source of truth**. When you pull or merge, keep the full-directory mount. Do not revert to per-file mounts (they caused uploads to the wrong path and the container not seeing updated `templates.py`).

---

## Known issues (fix next session)

1. **Read-only bind mounts** — With **full-directory** mount (`/share/.../mygirlhub:/app`), you can usually edit files in place on the NAS. If QNAP still makes files read-only, use this pattern:
   ```bash
   cp /app/templates.py /tmp/templates.py
   # edit /tmp/templates.py (e.g. vi, nano, or paste patched content)
   python3 -c "import shutil; shutil.copy('/tmp/templates.py', '/app/templates.py')"
   # then commit to git and rebuild
   ```

2. **Hostinger cache** — After any `rebuild_site.py` run, **clear the Hostinger cache manually** from the Hostinger dashboard, or users may see stale pages.

3. **Stale .pyc** — Always prefix rebuild commands with **`PYTHONDONTWRITEBYTECODE=1`** so Python doesn’t use stale `.pyc` files from `__pycache__` instead of the updated source.

4. **shutil.copy persistence** — Unclear whether after `shutil.copy('/tmp/templates.py', '/app/templates.py')` the change **persists across container restarts** (bind mount may overwrite `/app` on restart). **Needs testing.**

---

## Reminders

- **GitHub PAT (Cursor/git)** — Rotate before expiry. Set a **calendar reminder** (e.g. 2 weeks before expiry). When expired, `git push`/`pull` will fail with auth errors; create a new token at GitHub → Settings → Developer settings → Personal access tokens, then update the credential used by Git on this machine (and GITHUB_TOKEN/GH_PAT in Portainer if used for workflow dispatch).

---

## Directory Structure

```
/share/Container/mygirlhub/        ← repo / app code (all .py files live here)
  ├── templates.py
  ├── sitebuilder.py
  ├── publisher.py
  ├── builder.py
  ├── rebuild_site.py
  ├── .env  (your credentials)
  └── site/                        ← generated static HTML (built output)
        ├── index.html
        ├── videos.json            ← video database
        ├── privacy.html
        ├── 2257.html
        ├── sitemap.xml
        ├── robots.txt
        ├── videos/
        └── category/
```

The `/site` folder is what gets deployed to Hostinger's `public_html`.  
It maps to `/home/u426197676/domains/mygirlhub.com/public_html` on the server.

---

## Syncing Code Changes to the NAS

After editing `templates.py`, `sitebuilder.py`, or any `.py` file, copy the updated files to:

```
/share/Container/mygirlhub/
```

Options:
1. **Git** — `git pull` on the NAS inside that folder
2. **Manual copy** — SCP / drag-drop via your NAS file manager
3. **WinSCP / Filezilla** — connect to NAS and copy files across

---

## Running a Full Rebuild + Deploy

This rebuilds all HTML from `videos.json` and uploads everything to Hostinger via SFTP.  
Use this after any template or code change.

### Option A — Console (when the publisher container is running normally)

**Step 1 — Open Portainer console**
- Portainer → Containers → `mygirlhub-publisher` → Console → Connect

**Step 2 — Run rebuild**

Always use `PYTHONDONTWRITEBYTECODE=1` so updated `.py` source is used, not cached `.pyc`:

```bash
cd /app
pip install paramiko -q
PYTHONDONTWRITEBYTECODE=1 REBUILD_OUTPUT=/site REBUILD_DATA=/site/videos.json python rebuild_site.py
```

### Option B — One-off container (when the publisher is crashing too fast to use the console)

Use this when the publisher is in a restart loop and you can’t get a shell in time.

**Step 1 — Stop the publisher**
- Portainer → Containers → `mygirlhub-publisher` → **Stop**
- (Optional) Edit the container and set **Restart policy** to **Never** so it doesn’t keep restarting.

**Step 2 — Run a one-off rebuild container**

- Portainer → **Containers** → **+ Add container**
- **Name:** `mygirlhub-rebuild-once` (or any name)
- **Image:** same as your publisher (e.g. `python:3.11-alpine`)
- **Volumes:** add the **same** volume mounts as the publisher:
  - `/share/Container/mygirlhub` (or `/share/SystemSSD/Container/mygirlhub`) → **Container:** `/app`
  - `/share/Container/mygirlhub/site` (or your actual site path) → **Container:** `/site`
- **Env:** use **Env from stack** if your stack has env vars, or add the same variables (at least `SSH_HOST`, `SSH_PORT`, `SSH_USER`, `SSH_PASSWORD`, `REMOTE_ROOT`) so deploy works.
- **Command:** override with this (paste as one line):

  ```text
  sh -c "cd /app && pip install paramiko -q && PYTHONDONTWRITEBYTECODE=1 REBUILD_OUTPUT=/site REBUILD_DATA=/site/videos.json python rebuild_site.py"
  ```

- **Restart policy:** **Never**
- Click **Deploy the container**.

**Step 3 — Watch the logs**
- Containers → `mygirlhub-rebuild-once` → **Logs**
- The container will run the rebuild (and SFTP deploy), then **exit**. Logs will show success or any error (e.g. `ImportError` if `templates.py` on the NAS is still missing `render_sitemap`).

**Step 4 — Start the publisher again**
- Start `mygirlhub-publisher` again (and set Restart policy back to **Always** if you changed it).

**Path note:** If your publisher uses `/share/SystemSSD/Container/mygirlhub` for the repo, use that same path in the one-off container’s `/app` volume.

---

After the run, **clear the Hostinger cache** from the dashboard so visitors see the new content.

Expected output:
```
[INFO] Rebuilding site from /site/videos.json → /site
[INFO] Written: /site/index.html
[INFO] Written: /site/videos/...
...
[INFO] Build complete — 142 videos.
[INFO] Deploying to 195.35.39.252 → /home/u426197676/domains/mygirlhub.com/public_html
[INFO] Connecting to 195.35.39.252:65002 as u426197676 ...
[INFO]   ↑ index.html
[INFO]   ↑ sitemap.xml
...
[INFO] Deploy complete — 312 files uploaded, 1 skipped.
```

**No GitHub token needed.** Deploy goes directly via SFTP using credentials in `.env`.

---

## Compose Services

- **mygirlhub-publisher** — runs automatically; watches `/watch` for new `.mp4` files, processes them through Bunny + Claude, builds pages, SFTPs to Hostinger.
- **mygirlhub-builder** — run manually for a full rebuild from Bunny Stream (fetches all videos, regenerates everything).

Start publisher stack normally. For builder, use profile `manual`:
```bash
docker compose --profile manual run --rm mygirlhub-builder
```

---

## Environment Variables

All credentials live in `.env` (copy `_env` → `.env` and fill in):

| Variable | Purpose |
|---|---|
| `BUNNY_STREAM_API_KEY` | Bunny Stream API key |
| `BUNNY_CDN_HOSTNAME` | Bunny CDN hostname |
| `ANTHROPIC_API_KEY` | Claude API for title/description generation |
| `SSH_HOST` | Hostinger server IP |
| `SSH_PORT` | Hostinger SSH port |
| `SSH_USER` | Hostinger SSH username |
| `SSH_PASSWORD` | Hostinger SSH password |
| `REMOTE_ROOT` | Remote path on Hostinger (default: `/home/u426197676/domains/mygirlhub.com/public_html`) |

---

## Publisher Workflow (automatic)

When a `.mp4` is dropped into `/watch`:
1. Uploads to Bunny Stream → gets GUID
2. Waits for transcode
3. Generates title/description/tags via Claude (or sidecar `.json` if present)
4. Builds the new video page + updates homepage/category/sitemap
5. SFTPs only the changed files to Hostinger
6. Deletes local file

To add a video manually with custom metadata, drop a `.json` sidecar alongside the video:
```json
{
  "title": "Jane Doe – Hot New Show",
  "description": "Watch Jane's latest live cam show...",
  "tags": ["jane doe", "camgirl", "free cam"]
}
```

---

## Troubleshooting

**Build succeeds but deploy skipped:**
- Check `SSH_PASSWORD` is set: `echo $SSH_PASSWORD`
- Make sure `.env` is loaded: `source /app/.env` then re-run

**`videos.json not found`:**
- Run `builder.py` first to populate it, or copy an existing `videos.json` to `/site/`

**`paramiko` not installed:**
- Run `pip install paramiko -q` before the rebuild command

**Future template edits (safe pattern):**
```bash
cp /app/templates.py /tmp/templates.py
# edit /tmp/templates.py
python3 -c "import shutil; shutil.copy('/tmp/templates.py', '/app/templates.py')"
# then commit to git and rebuild
```

**Pages look old after deploy:**
- **Clear Hostinger cache** from the dashboard (required after every rebuild).
- Hard refresh browser (Ctrl+Shift+R) — Hostinger may cache aggressively
- Check file timestamps on server via SFTP client to confirm upload worked
