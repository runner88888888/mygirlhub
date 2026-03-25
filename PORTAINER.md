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

Optional third mount (only if you prefer `/site` as a separate path in the container):

```yaml
  - /share/Container/mygirlhub/site:/site
```

If you use that third line, set **`SITE_OUTPUT=/site`** in the stack environment so `publisher.py` writes to the same folder as your web root. If you omit it, **`publisher.py` defaults to `/app/site`**, which is the same NAS folder as `.../mygirlhub/site` when the repo is mounted at `/app`.

If your NAS uses a different host path for the repo (e.g. `/share/SystemSSD/Container/mygirlhub`), use that path for the first line; keep `:/app` and `:/watch` as shown.

**Why this is in the repo:** `docker-compose.example.yml` and this section are the **source of truth**. When you pull or merge, keep the full-directory mount. Do not revert to per-file mounts (they caused uploads to the wrong path and the container not seeing updated `templates.py`).

**Publisher crash `FileNotFoundError: /site/videos.json`:** Historically `publisher.py` used `/site` while the stack only mounted `/app` and `/watch`, so `/site` was not the real `site` folder and rebuilds could fail after Bunny upload — leaving many `.mp4` files stuck in `ToPublish`. Default is now `/app/site`; use `SITE_OUTPUT=/site` only with the optional third bind.

**Videos stuck in ToPublish after restart:** The file watcher only sees **new** creates/moves. Anything already in `/watch` when the container starts was skipped. On startup, the publisher now runs a **backlog pass** (sorted filenames) over existing `.mp4`/`.mov`/etc. in `/watch`. Set `SKIP_WATCH_BACKLOG=1` in the stack env to disable that pass if you ever need a clean watcher-only start.

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

## Sync without hand-copying (Git)

1. On your PC: commit and **push** to GitHub (or your `origin`).
2. On the NAS (SSH or container console with `git` in the image):
   ```bash
   cd /share/Container/mygirlhub   # same path Portainer mounts to /app
   git pull
   ```
3. Rebuild static HTML (Portainer → publisher/rebuild console):
   ```bash
   cd /app
   PYTHONDONTWRITEBYTECODE=1 python -c "import sitebuilder; sitebuilder.build_site('site', 'site/videos.json')"
   ```

No File Station copy needed if the repo on the NAS tracks `origin` and you only change code via pull.

---

## Syncing Code Changes to the NAS

After editing `templates.py`, `sitebuilder.py`, `builder.py`, `publisher.py`, or any `.py` file, get the new code onto the NAS at:

```
/share/Container/mygirlhub/
```

**Options:**

1. **Git (recommended)** — On the NAS, in the repo folder, run `git pull`. Then run the rebuild so the container uses the latest code.  
   (Optional reminder: *“After I push code, run `git pull` in `/share/Container/mygirlhub` (or your mygirlhub repo path), then run the rebuild so the container uses the latest code.”* This doc is the reference.

2. **Manual upload** — Copy only the changed files (e.g. `templates.py`, `sitebuilder.py`, `builder.py`) to the NAS project folder via File Station, WinSCP, or drag‑drop. No git on the NAS needed.

3. **WinSCP / Filezilla** — Same as manual: connect to the NAS and copy the updated files into the mygirlhub directory.

**Minimum for template/code updates:** upload `templates.py` and `sitebuilder.py` (and `builder.py` / `publisher.py` if you changed them). Then run a rebuild so the new HTML is generated and deployed.

**Keeping git in sync:** Commit and push from your PC (e.g. in Cursor). See **Automatic git pull** below so you don’t have to run `git pull` on the NAS yourself.

---

## Automatic git pull (no manual pull on the NAS)

`rebuild_site.py` runs **`git pull`** at the start of every rebuild. So when you run the rebuild from the Portainer console, the container updates the code in `/app` (your NAS folder) from GitHub, then builds and deploys.

**Requirement:** The container must have **git** installed. Two options:

1. **Use the repo’s Dockerfile (recommended)**  
   In Portainer, build an image from the repo (e.g. build from `/share/Container/mygirlhub` with Dockerfile there), then set your stack to use that image instead of `python:3.11-alpine`. The Dockerfile adds `git` (and paramiko) so pull works.

2. **Keep using `python:3.11-alpine`**  
   Then git is not installed; the script logs *"git not installed — skipping pull"* and continues. You can still upload files manually or run `git pull` yourself on the NAS if you ever use a shell there.

**Summary:** Push from PC → run rebuild in Portainer → container runs `git pull` then rebuild and deploy. No need to run git on the NAS yourself.

---

## One-time: Switch stack to image with git (+ private repo)

Do this once so the container has git and can run `git pull` (including for a **private** repo).

### Step 1 — Let the NAS repo do `git pull` (private repo)

The container runs `git pull` inside the folder mounted from the NAS. So that folder must be a git clone that can authenticate to GitHub.

**Option A — HTTPS with Personal Access Token (simplest)**

1. Create a **GitHub Personal Access Token** (classic): GitHub → Settings → Developer settings → Personal access tokens → Generate. Give it `repo` scope.
2. On the NAS, open the repo folder (e.g. in File Station go to `Container/mygirlhub`). You need to run one command that configures the remote to use the token.  
   - If you have **SSH** or **Task Scheduler** on the NAS that can run a shell, run:
     ```bash
     cd /share/Container/mygirlhub
     git remote set-url origin https://YOUR_GITHUB_USERNAME:YOUR_TOKEN@github.com/YOUR_USERNAME/mygirlhub.git
     ```
     Replace `YOUR_GITHUB_USERNAME`, `YOUR_TOKEN`, and `YOUR_USERNAME/mygirlhub` with your GitHub username, token, and repo path. Then run `git pull` once to confirm it works.
   - If you **don’t** have a shell on the NAS: clone the repo again on a PC with the token in the URL, then copy the whole folder (including `.git`) to the NAS, overwriting the existing folder. Then the clone on the NAS will use that remote and the container’s `git pull` will work.

**Option B — SSH key on the NAS**

If the NAS repo was cloned with `git@github.com:...` and an SSH key is set up for GitHub on the NAS, no change needed. If not, set up an SSH key on the NAS and add the public key to GitHub, then ensure the repo’s `origin` is the SSH URL.

After this, from the NAS (or from the container console with `cd /app && git pull`) a `git pull` should succeed without asking for a password.

---

### Step 2 — Build the image in Portainer

1. In **Portainer**, go to **Images**.
2. Click **Build a new image** (or **Add image** → **Build from build context**).
3. **Build context:**
   - If Portainer shows **Path**: enter the path to the repo on the NAS, e.g. `/share/Container/mygirlhub` (or `/share/SystemSSD/Container/mygirlhub` if that’s where the repo lives).
   - If it only offers **Upload** or **Git repository**: upload a zip of the repo (including the `Dockerfile` at the root), or use “Git repository” only if you can paste a URL with token for the private repo. Then use that as the build context.
4. **Image name:** e.g. `mygirlhub-publisher:local`.
5. **Dockerfile path:** leave default `Dockerfile` (it’s at the root of the repo).
6. Click **Build** and wait until the image appears in the list.

---

### Step 3 — Point the stack at the new image

1. Go to **Stacks** → open your publisher stack (e.g. `mygirlhub_publisher`).
2. Click **Editor** (or **Web editor**).
3. Find the line that sets the **image** for the publisher service (e.g. `image: python:3.11-alpine`).
4. Change it to the image you built, e.g. `image: mygirlhub-publisher:local`.
5. Click **Update the stack** (or **Deploy**). Portainer will recreate the container with the new image.

---

### Step 4 — Test

1. **Containers** → select `mygirlhub-publisher` → **Console** → Connect.
2. Run:
   ```bash
   cd /app
   PYTHONDONTWRITEBYTECODE=1 REBUILD_OUTPUT=/site REBUILD_DATA=/site/videos.json python rebuild_site.py
   ```
3. In the logs you should see a line like `git pull: Already up to date.` (or a commit message). If you see `git not installed`, the container is still using the old image — repeat Step 3 and ensure the stack uses `mygirlhub-publisher:local` (or your image name).

After this one-time setup, every time you run the rebuild from the console, the container will run `git pull` then build and deploy. No need to run git on the NAS yourself.

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

**HTML-only rebuild (NAS `site` folder, no SFTP)** — for `dev.*` or when Hostinger is not the target:

```bash
cd /app
PYTHONDONTWRITEBYTECODE=1 python -c "import sitebuilder; sitebuilder.build_site('site', 'site/videos.json')"
```

You should see a line like `[sitebuilder] 188 videos from /app/site/videos.json -> /app/site`.  
**Wrong:** `build_site('site', 'videos.json')` — that looks for `/app/videos.json`, which usually does not exist; the builder now falls back to `site/videos.json` with a warning, but always prefer `site/videos.json` explicitly.

**Host folder name must match the stack:** Portainer must bind the same NAS folder you keep in Git (e.g. `/share/Container/mygirlhub` → `/app`). Edits anywhere else on the NAS are invisible to the container.

### NAS production mounts — confirmed (Portainer screenshot, Mar 2026)

The live **`mygirlhub-publisher`** stack matches the intended layout:

| Host (QNAP) | Container |
|---------------|-----------|
| `/share/Container/mygirlhub` | `/app` |
| `/share/Container/mygirlhub/site` | `/site` |
| `/share/ToPublish` | `/watch` |

Service label: **`com.docker.compose.service: mygirlhub-publisher`**. Edits under **`Container/mygirlhub`** on the NAS are what `/app` sees; **`site/`** and **`videos.json`** are the same data whether accessed as **`/app/site`** or **`/site`**.

Optional env: **`SITE_OUTPUT=/site`** so `publisher.py` writes explicitly via the `/site` mount (equivalent to `/app/site` for this host layout).

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

## GitHub Actions — “Awaiting a runner” / Cancelled deploy (URGENT)

If you see a workflow run **Cancelled** with an error like **“The job has exceeded the maximum execution time while awaiting a runner for 24h0m0s”**, that is **not a git problem**. The job never started because **no runner was available**.

**What’s going on:** The “Deploy to Hostinger” workflow is set up to run on a **self-hosted runner** (e.g. on your NAS). When that runner is offline or not registered, GitHub waits up to 24 hours for it, then cancels the run.

**Plan — pick one:**

1. **Fix the self-hosted runner (if you want to keep using the workflow)**  
   - On the machine that should run the job (usually the NAS): install or start the **GitHub Actions runner** and register it to the repo (`runner88888888/mygirlhub`).  
   - GitHub → Repo → **Settings** → **Actions** → **Runners**: see if a self-hosted runner is listed and “Idle”. If it’s missing or “Offline”, (re)install and start the runner there so the next workflow run gets a runner.

2. **Stop using the workflow for deploy (recommended for now)**  
   - You already deploy via **Portainer** and **rebuild_site.py** (SFTP from the container to Hostinger). You don’t need the GitHub Action for that.  
   - To avoid queuing a job that will never run: when running the builder (e.g. full build from Bunny), set **`SKIP_DEPLOY_WORKFLOW=1`** in the container env so it doesn’t trigger the deploy workflow.  
   - For normal deploys: use **Portainer** → console → run `rebuild_site.py` (with optional `git pull`). No Actions needed.

**Summary:** Git (commit, push, pull) is fine. The failure is “no runner”. Either get the self-hosted runner online or rely on Portainer + `rebuild_site.py` and skip the workflow trigger.

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
| `SKIP_DEPLOY_WORKFLOW` | Set to `1` to avoid triggering the GitHub Actions deploy workflow (recommended: use Portainer rebuild instead). |
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
