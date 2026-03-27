#!/usr/bin/env python3
"""
MyGirlHub Publisher v4
=======================
Watches /watch for new video files.
Pipeline:
  1. Upload to Bunny Stream → get GUID
  2. Wait for transcode
  3. Generate title/description/tags: Composer (sidecar) > Claude > (no Grok)
  4. Build video page + update homepage/category/sitemap
  5. SFTP changed files to Hostinger
  6. Delete local file

Composer-first: If a .json file exists next to the video (same name, e.g. video.mp4 + video.json)
with {"title":"...","description":"...","tags":[...]}, that content is used. Otherwise Claude.
"""

import os, sys, json, re, time, logging, requests, paramiko
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from sitebuilder import slugify, clean_performer, performer_slug, add_video_and_rebuild

logging.basicConfig(level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)])
log = logging.getLogger(__name__)

# Output must live under the repo when only /app + /watch are mounted (see docker-compose.example.yml).
# Default: /app/site == host .../mygirlhub/site. Override with SITE_OUTPUT=/site if you bind-mount site separately.
_SITE_OUT = os.environ.get("SITE_OUTPUT", "/app/site").rstrip("/")

CONFIG = {
    "watch_folder":      "/watch",
    "output_dir":        _SITE_OUT,
    "data_file":         os.path.join(_SITE_OUT, "videos.json"),
    "bunny_library_id":  os.environ.get("BUNNY_LIBRARY_ID", "554827"),
    "bunny_stream_key":  os.environ.get("BUNNY_STREAM_API_KEY", ""),
    "bunny_cdn":         os.environ.get("BUNNY_CDN_HOSTNAME", "vz-7f6a065c-ba7.b-cdn.net"),
    "anthropic_key":     os.environ.get("ANTHROPIC_API_KEY", ""),
    "ssh_host":          os.environ.get("SSH_HOST", "195.35.39.252"),
    "ssh_port":          int(os.environ.get("SSH_PORT", "65002")),
    "ssh_user":          os.environ.get("SSH_USER", "u426197676"),
    "ssh_password":      os.environ.get("SSH_PASSWORD", ""),
    "remote_root":       os.environ.get("REMOTE_ROOT", "/home/u426197676/domains/mygirlhub.com/public_html"),
    "file_settle":       int(os.environ.get("FILE_SETTLE_TIME", "30")),
    "transcode_timeout": int(os.environ.get("TRANSCODE_TIMEOUT", "600")),
    "transcode_poll":    int(os.environ.get("TRANSCODE_POLL", "15")),
    "video_exts":        [".mp4", ".mov", ".mkv", ".avi"],
}

BUNNY_API = "https://video.bunnycdn.com"

# ── FILENAME PARSING ─────────────────────────────────────
def extract_performer(filename):
    """
    Extract the performer name from a filename.
    Rule: performer is always the FIRST word of the filename (before any
    underscore, space, or date). clean_performer() then enforces single-word.
    Examples:
      "nadiabliss_hot_show_2026-03-10.mp4"  -> "nadiabliss"
      "AlicePirce 2026-03-10.mp4"           -> "AlicePirce"
      "mfcgoddess_video_07.mp4"             -> "mfcgoddess"
    """
    stem = Path(filename).stem
    # Strip date patterns
    stem = re.sub(r'[_\s]?\d{4}[-_]?\d{2}[-_]?\d{2}', '', stem)
    stem = re.sub(r'[_\s]+\d+$', '', stem)
    stem = stem.strip('_- ')
    # First word only (split on underscore, space, or hyphen)
    first_word = re.split(r'[_\s\-]+', stem)[0]
    return clean_performer(first_word)

def extract_hint(filename):
    stem = Path(filename).stem
    stem = re.sub(r'[_\s]?\d{4}[-_]?\d{2}[-_]?\d{2}', '', stem)
    stem = re.sub(r'[_\s]+\d+$', '', stem)
    return stem.replace('_', ' ').strip()

# ── BUNNY ────────────────────────────────────────────────
def bunny_headers():
    return {"AccessKey": CONFIG["bunny_stream_key"], "accept": "application/json", "content-type": "application/json"}

def bunny_create(title):
    lib = CONFIG["bunny_library_id"]
    r = requests.post(f"{BUNNY_API}/library/{lib}/videos",
        headers=bunny_headers(), json={"title": title}, timeout=30)
    if r.status_code == 200:
        guid = r.json().get("guid")
        log.info(f"Bunny GUID: {guid}")
        return guid
    log.error(f"Bunny create failed: {r.status_code}")
    return None

def bunny_upload(filepath, guid):
    lib = CONFIG["bunny_library_id"]
    mb = os.path.getsize(filepath) / 1024 / 1024
    log.info(f"Uploading {mb:.1f} MB...")
    with open(filepath, "rb") as f:
        r = requests.put(f"{BUNNY_API}/library/{lib}/videos/{guid}",
            headers={"AccessKey": CONFIG["bunny_stream_key"], "Content-Type": "application/octet-stream"},
            data=f, timeout=1800)
    if r.status_code == 200:
        log.info("Upload complete"); return True
    log.error(f"Upload failed: {r.status_code}"); return False

def bunny_wait(guid):
    lib = CONFIG["bunny_library_id"]
    elapsed = 0
    while elapsed < CONFIG["transcode_timeout"]:
        time.sleep(CONFIG["transcode_poll"])
        elapsed += CONFIG["transcode_poll"]
        try:
            r = requests.get(f"{BUNNY_API}/library/{lib}/videos/{guid}",
                headers=bunny_headers(), timeout=15)
            if r.status_code != 200: continue
            data = r.json()
            status   = data.get("status", 0)
            progress = data.get("encodeProgress", 0)
            log.info(f"Transcode status={status} progress={progress}% [{elapsed}s]")
            if status in (3, 4): log.info("Transcode complete"); return True
            if status == 5: log.error("Transcode failed"); return False
        except Exception as e:
            log.warning(f"Poll error: {e}")
    log.warning("Transcode timeout — proceeding"); return True

# ── CLAUDE ───────────────────────────────────────────────
def generate_content(performer, hint):
    log.info(f"Generating content: {performer}")
    prompt = (
        "Adult cam video website (18+ legal). Attract viewers new to this kind of site. NEVER mention any platform names (MyFreeCams, MFC, etc.).\n\n"
        f"Performer (model name): {performer}\n"
        f"Video hint (often from filename): {hint}\n\n"
        "IMPORTANT — If the hint looks like a browser/recording filename (e.g. contains 'Chat Room', 'MyFreeCams', 'Google Chrome', 'Chrome', dates like 2026-03-13, etc.), IGNORE the entire hint. Use ONLY the performer name. Your job is to invent a good title, description, and tags from the performer name alone. Do not copy or use any part of the filename except the model name.\n\n"
        "Return ONLY JSON: {\"title\":\"...\",\"description\":\"...\",\"tags\":[...]}\n\n"
        "EXAMPLES — copy this style exactly:\n"
        '1. {"title": "gorgeous young woman with giant boobs", "description": "XAngelina gorgeous young woman with giant boobs plays with her pussy", "tags": ["gorgeous", "giant boobs", "masturbation"]}\n'
        '2. {"title": "Linaresjesica Big Tits Blowjob", "description": "Linaresjesica shows her fantastic Big Tits and Blowjob skills", "tags": ["Big Tits", "Blowjob"]}\n\n'
        "RULES: Title = content-led (looks/vibe or performer + key acts). Description = performer + physical/action, direct and explicit. Tags = 3–6 audience terms (big tits, blowjob, masturbation, etc.). No platform names."
    )
    try:
        r = requests.post("https://api.anthropic.com/v1/messages",
            headers={"x-api-key": CONFIG["anthropic_key"], "anthropic-version": "2023-06-01", "content-type": "application/json"},
            json={"model": "claude-sonnet-4-20250514", "max_tokens": 400,
                  "messages": [{"role": "user", "content": prompt}]},
            timeout=30)
        if r.status_code == 200:
            text = r.json()["content"][0]["text"].strip().replace("```json","").replace("```","").strip()
            data = json.loads(text)
            return {
                "title":       data.get("title", hint).strip(),
                "description": data.get("description", "").strip(),
                "tags":        data.get("tags", [performer, "camgirl", "free cam video"])
            }
    except Exception as e:
        log.error(f"Claude error: {e}")
    return {"title": hint[:70], "description": "", "tags": [performer, "camgirl", "free cam video", "live cam"]}

def load_composer_content(filepath):
    """Composer-first: load title/desc/tags from sidecar .json if present."""
    base = os.path.splitext(filepath)[0]
    sidecar = base + ".json"
    if not os.path.exists(sidecar):
        return None
    try:
        with open(sidecar, "r", encoding="utf-8") as f:
            data = json.load(f)
        title = data.get("title", "").strip()
        desc = data.get("description", "").strip()
        tags = data.get("tags", [])
        if title and isinstance(tags, list):
            log.info("Using Composer content from sidecar .json")
            return {"title": title, "description": desc, "tags": tags}
    except Exception as e:
        log.warning(f"Sidecar JSON invalid: {e}")
    return None

# ── SFTP — upload only changed files ────────────────────
def sftp_upload_files(file_paths):
    """Upload a specific list of local paths to Hostinger."""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(CONFIG["ssh_host"], port=CONFIG["ssh_port"],
                username=CONFIG["ssh_user"], password=CONFIG["ssh_password"], timeout=15)
    sftp = ssh.open_sftp()

    def mkdir_p(path):
        parts = path.split('/')
        current = ''
        for p in parts:
            if not p: continue
            current += '/' + p
            try: sftp.mkdir(current)
            except: pass

    for local_path in file_paths:
        rel = os.path.relpath(local_path, CONFIG["output_dir"])
        remote = CONFIG["remote_root"] + '/' + rel.replace('\\', '/')
        mkdir_p('/'.join(remote.split('/')[:-1]))
        sftp.put(local_path, remote)
        log.info(f"Uploaded: {rel}")

    sftp.close()
    ssh.close()

# ── PIPELINE ─────────────────────────────────────────────
processed = set()

def log_thumb_referrer_regression_check(paths=None):
    """
    Detect regression where generated HTML contains referrerpolicy="no-referrer",
    which causes Bunny thumbnail/preview 403s (missing Referer).
    """
    if paths is None:
        paths = [
            f"{CONFIG['output_dir']}/index.html",
            f"{CONFIG['output_dir']}/page/2/index.html",
        ]
    total_hits = 0
    scanned = 0
    for p in paths:
        if not os.path.exists(p):
            continue
        scanned += 1
        try:
            with open(p, "r", encoding="utf-8", errors="ignore") as f:
                html = f.read()
            hits = html.count('referrerpolicy="no-referrer"')
            total_hits += hits
            if hits:
                log.warning("⚠️ Thumb regression check: %s contains %d no-referrer attrs", p, hits)
        except Exception as e:
            log.warning("Thumb regression check failed for %s: %s", p, e)
    if scanned == 0:
        log.info("Thumb regression check: no HTML files found yet")
    elif total_hits == 0:
        log.info("✅ Thumb regression check: no no-referrer attrs found")
    else:
        log.warning("⚠️ Thumb regression check failed: total no-referrer attrs=%d", total_hits)

def process_video(filepath):
    if filepath in processed: return
    processed.add(filepath)

    filename = os.path.basename(filepath)
    log.info("━" * 40)
    log.info(f"Processing: {filename}")

    time.sleep(CONFIG["file_settle"])

    if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
        log.error("File missing or empty"); return

    performer = extract_performer(filename)
    hint      = extract_hint(filename)
    log.info(f"Performer : {performer}")
    log.info(f"Hint      : {hint}")

    guid = bunny_create(hint)
    if not guid: return

    if not bunny_upload(filepath, guid): return

    bunny_wait(guid)

    # Composer > Claude (no Grok)
    content = load_composer_content(filepath)
    if content is None:
        content = generate_content(performer, hint)
    log.info(f"Title     : {content['title']}")

    today          = datetime.now().strftime("%Y-%m-%d")
    perf_clean     = clean_performer(performer)
    perf_slug      = performer_slug(performer)
    base_slug      = slugify(content['title'])
    slug           = f"{base_slug}-{today}"

    new_video = {
        "guid":           guid,
        "cdn":            CONFIG["bunny_cdn"],
        "library_id":     CONFIG["bunny_library_id"],
        "title":          content["title"],
        "description":    content["description"],
        "performer":      perf_clean,
        "performer_slug": perf_slug,
        "slug":           slug,
        "tags":           content["tags"],
        "date":           today,
        "views":          0
    }

    # Rebuild affected pages and get list of changed files
    os.makedirs(CONFIG["output_dir"], exist_ok=True)
    if not os.path.exists(CONFIG["data_file"]):
        with open(CONFIG["data_file"], 'w') as f: f.write('[]')

    add_video_and_rebuild(CONFIG["output_dir"], CONFIG["data_file"], new_video)
    log_thumb_referrer_regression_check()

    # Upload changed files
    changed = [
        f"{CONFIG['output_dir']}/index.html",
        f"{CONFIG['output_dir']}/videos/{slug}/index.html",
        f"{CONFIG['output_dir']}/category/{perf_slug}/index.html",
        f"{CONFIG['output_dir']}/sitemap.xml",
        CONFIG["data_file"],
    ]
    changed = [p for p in changed if os.path.exists(p)]

    try:
        sftp_upload_files(changed)
        log.info(f"Live: https://mygirlhub.com/videos/{slug}/")
    except Exception as e:
        log.error(f"Upload failed: {e}")

    try:
        os.remove(filepath)
        log.info("Local file deleted")
    except Exception as e:
        log.warning(f"Delete failed: {e}")
    sidecar = os.path.splitext(filepath)[0] + ".json"
    if os.path.exists(sidecar):
        try:
            os.remove(sidecar)
            log.info("Sidecar .json deleted")
        except Exception:
            pass

    log.info("━" * 40)

# ── WATCHER ──────────────────────────────────────────────
class Handler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory: self._handle(event.src_path)
    def on_moved(self, event):
        if not event.is_directory: self._handle(event.dest_path)
    def _handle(self, path):
        if Path(path).suffix.lower() in CONFIG["video_exts"]:
            process_video(path)


def process_watch_folder_backlog():
    """
    Watchdog only fires on create/move. Files already sitting in /watch when the
    container starts are invisible to the watcher — process them once on startup.
    """
    watch = CONFIG["watch_folder"]
    try:
        names = sorted(os.listdir(watch))
    except OSError as e:
        log.warning("Could not list watch folder %s: %s", watch, e)
        return
    for name in names:
        path = os.path.join(watch, name)
        if not os.path.isfile(path):
            continue
        if Path(path).suffix.lower() not in CONFIG["video_exts"]:
            continue
        log.info("📥 Backlog (already in watch): %s", name)
        process_video(path)


def main():
    os.makedirs(CONFIG["watch_folder"], exist_ok=True)
    os.makedirs(CONFIG["output_dir"], exist_ok=True)
    log.info("🚀 MyGirlHub Publisher v4")
    log.info(f"📁 Watching : {CONFIG['watch_folder']}")
    log.info(f"🌐 Remote   : {CONFIG['ssh_host']}")
    log_thumb_referrer_regression_check()

    if os.environ.get("SKIP_WATCH_BACKLOG", "").strip().lower() not in ("1", "true", "yes"):
        process_watch_folder_backlog()
    else:
        log.info("SKIP_WATCH_BACKLOG set — not processing existing files in watch folder")

    observer = Observer()
    observer.schedule(Handler(), CONFIG["watch_folder"], recursive=False)
    observer.start()
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()
