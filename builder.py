#!/usr/bin/env python3
"""
MyGirlHub Migration Builder - SFTP "Final Boss" Edition (Short Title Fix)
========================================================================
- Uses Pure SFTP to bypass Hostinger's /sbin/nologin shell restriction.
- Limits video titles to 60 characters to prevent UI cutoff.
- Automatically handles folder creation on the remote server.
"""

import os, sys, json, re, time, logging, requests, subprocess
import paramiko
from pathlib import Path
from datetime import datetime
from sitebuilder import slugify, clean_performer, performer_slug, save_videos, build_site

logging.basicConfig(level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)])
log = logging.getLogger(__name__)

CONFIG = {
    "bunny_library_id":  os.environ.get("BUNNY_LIBRARY_ID", "554827"),
    "bunny_stream_key":  os.environ.get("BUNNY_STREAM_API_KEY", ""),
    "bunny_cdn":         os.environ.get("BUNNY_CDN_HOSTNAME", "vz-7f6a065c-ba7.b-cdn.net"),
    "anthropic_key":     os.environ.get("ANTHROPIC_API_KEY", ""),
    "xai_key":           os.environ.get("XAI_API_KEY", ""),
    "ssh_host":          os.environ.get("SSH_HOST", "195.35.39.252"),
    "ssh_port":          int(os.environ.get("SSH_PORT", "65002")),
    "ssh_user":          os.environ.get("SSH_USER", "u426197676"),
    "ssh_password":      os.environ.get("SSH_PASSWORD", ""),
    "remote_root":       os.environ.get("REMOTE_ROOT", "/home/u426197676/domains/mygirlhub.com/public_html"),
    "output_dir":        os.environ.get("OUTPUT_DIR", "/tmp/mygirlhub_site"),
    "data_file":         os.environ.get("DATA_FILE", os.path.join(os.environ.get("OUTPUT_DIR", "/tmp/mygirlhub_site"), "videos.json")),
    "claude_delay":      1.5, 
}

BUNNY_API = "https://video.bunnycdn.com"

def bunny_headers():
    return {"AccessKey": CONFIG["bunny_stream_key"], "accept": "application/json"}

def fetch_all_bunny_videos():
    lib = CONFIG["bunny_library_id"]
    all_videos = []
    page = 1
    while True:
        r = requests.get(f"{BUNNY_API}/library/{lib}/videos",
            headers=bunny_headers(),
            params={"page": page, "itemsPerPage": 100, "orderBy": "date"},
            timeout=30)
        if r.status_code != 200:
            log.error(f"Bunny fetch failed: {r.status_code}")
            break
        data = r.json()
        items = data.get("items", [])
        all_videos.extend(items)
        log.info(f"Fetched page {page} — {len(items)} videos ({len(all_videos)} total)")
        if len(all_videos) >= data.get("totalItems", 0):
            break
        page += 1
    return all_videos

# Phrases to strip from hints and LLM output (browser/recording artifacts)
ARTIFACT_PHRASES = [
    r"via google chrome", r"via chrome", r"google chrome", r"chrome", r"firefox", r"safari", r"edge", r"browser",
    r"myfreecams", r"mfc", r"captured live", r"screen record", r"tab", r"recorded via", r"streamed via",
    r"\d{1,2}-\d{2}-\d{2}(-\d{2})?",  # timestamps like 16-24-36
]

def _clean_artifact_phrases(text):
    """Remove browser names, recording metadata, etc. from text."""
    if not text:
        return ""
    t = text.lower()
    for p in ARTIFACT_PHRASES:
        t = re.sub(p, " ", t, flags=re.IGNORECASE)
    t = re.sub(r"\s+", " ", t).strip().strip("-").strip("_")
    return t if t else text[:50]

def generate_content(title_hint):
    # Clean hint before sending — strip browser/recording junk
    clean_hint = _clean_artifact_phrases(title_hint)
    parts = re.split(r'[\s_–\-]+', clean_hint.strip())
    # Single word only — first token is the performer handle
    raw_performer = parts[0] if parts else "Model"
    perf = clean_performer(raw_performer)

    prompt = (
        "Adult cam video content (18+ legal). Attract viewers new to this kind of site. NEVER mention any platform names (MyFreeCams, MFC, etc.).\n\n"
        f"Performer: {perf}. Video hint: {clean_hint}.\n\n"
        "Return ONLY JSON: {\"title\":\"...\",\"description\":\"...\",\"tags\":[]}\n\n"
        "EXAMPLES — copy this style exactly:\n"
        '1. {"title": "gorgeous young woman with giant boobs", "description": "XAngelina gorgeous young woman with giant boobs plays with her pussy", "tags": ["gorgeous", "giant boobs", "masturbation"]}\n'
        '2. {"title": "Linaresjesica Big Tits Blowjob", "description": "Linaresjesica shows her fantastic Big Tits and Blowjob skills", "tags": ["Big Tits", "Blowjob"]}\n\n'
        "RULES: Title = content-led (looks/vibe) or performer + key acts, under 60 chars. Description = performer name + physical + action. Tags = 3-6 terms. No platform names."
    )

    def _parse_result(text):
        text = text.strip().replace("```json", "").replace("```", "").strip()
        data = json.loads(text)
        clean_title = _clean_artifact_phrases(data.get("title", title_hint).strip())
        if not clean_title:
            clean_title = clean_hint[:50] if clean_hint else perf
        if len(clean_title) > 60:
            clean_title = clean_title[:57] + "..."
        clean_desc = _clean_artifact_phrases(data.get("description", "").strip())
        return {"title": clean_title, "description": clean_desc, "tags": data.get("tags", [perf, "camgirl"]), "performer": perf}

    # 1. Try Claude first
    if CONFIG["anthropic_key"]:
        try:
            r = requests.post("https://api.anthropic.com/v1/messages",
                headers={"x-api-key": CONFIG["anthropic_key"], "anthropic-version": "2023-06-01", "content-type": "application/json"},
                json={"model": "claude-3-5-sonnet-20240620", "max_tokens": 400,
                      "messages": [{"role": "user", "content": prompt}]},
                timeout=30)
            if r.status_code == 200:
                text = r.json()["content"][0]["text"]
                return _parse_result(text)
        except Exception as e:
            log.warning(f"Claude error: {e}")

    # Grok disabled — use basic fallback if Claude fails
    # 3. Basic fallback
    return {"title": title_hint[:57] + "...", "description": "", "tags": [perf, "camgirl"], "performer": perf}

def upload_via_sftp(local_dir, remote_dir):
    """Upload only site artifacts (no .py, .yml, etc.)."""
    SITE_FILES = {"index.html", "robots.txt", "sitemap.xml", "videos.json"}
    SITE_DIRS = {"videos", "category"}
    log.info("Uploading site files only: index.html, robots.txt, sitemap.xml, videos.json, videos/, category/")
    log.info(f"Starting Pure SFTP Upload to {CONFIG['ssh_host']}...")
    try:
        transport = paramiko.Transport((CONFIG["ssh_host"], CONFIG["ssh_port"]))
        transport.connect(username=CONFIG["ssh_user"], password=CONFIG["ssh_password"])
        sftp = paramiko.SFTPClient.from_transport(transport)
        
        def mkdir_p(remote_path):
            dirs = remote_path.split('/')
            current = ""
            for d in dirs:
                if not d: continue
                current += "/" + d
                if current.startswith("/home"):
                    try:
                        sftp.mkdir(current)
                    except:
                        pass 

        count = 0
        for root, dirs, files in os.walk(local_dir):
            rel_root = os.path.relpath(root, local_dir)
            if rel_root == ".":
                top_files = set(files)
                top_dirs = set(dirs)
                for filename in files:
                    if filename in SITE_FILES:
                        local_path = os.path.join(root, filename)
                        remote_path = os.path.join(remote_dir, filename).replace("\\", "/")
                        sftp.put(local_path, remote_path)
                        count += 1
                        if count % 25 == 0:
                            log.info(f"Progress: {count} files uploaded...")
                for d in dirs:
                    if d in SITE_DIRS:
                        for sub_root, _, sub_files in os.walk(os.path.join(root, d)):
                            for filename in sub_files:
                                local_path = os.path.join(sub_root, filename)
                                rel_path = os.path.relpath(local_path, local_dir)
                                remote_path = os.path.join(remote_dir, rel_path).replace("\\", "/")
                                mkdir_p(os.path.dirname(remote_path))
                                sftp.put(local_path, remote_path)
                                count += 1
                                if count % 25 == 0:
                                    log.info(f"Progress: {count} files uploaded...")
                break
        sftp.close()
        transport.close()
        log.info(f"SUCCESS! {count} files moved to mygirlhub.com.")
    except Exception as e:
        log.error(f"SFTP CRITICAL FAILURE: {e}")

def main():
    if not CONFIG["bunny_stream_key"] or not CONFIG["anthropic_key"] or not CONFIG["ssh_password"]:
        log.error("Missing required environment variables in Portainer.")
        sys.exit(1)

    log.info("Using Claude for titles, descriptions, and tags (no Grok)")
    os.makedirs(CONFIG["output_dir"], exist_ok=True)

    if os.path.exists(CONFIG["data_file"]):
        log.info(f"Found {CONFIG['data_file']}. Skipping Claude processing.")
        with open(CONFIG["data_file"], 'r') as f:
            videos = json.load(f)
    else:
        log.info("Fetching videos from Bunny Stream...")
        bunny_videos = fetch_all_bunny_videos()
        videos = []
        for i, bv in enumerate(bunny_videos):
            guid = bv.get("guid", "")
            title_hint = bv.get("title", guid)
            date = bv.get("dateUploaded", datetime.now().strftime("%Y-%m-%d"))[:10]
            log.info(f"[{i+1}/{len(bunny_videos)}] Processing: {title_hint[:50]}")
            content = generate_content(title_hint)
            videos.append({
                "guid": guid, "cdn": CONFIG["bunny_cdn"], "library_id": CONFIG["bunny_library_id"],
                "title": content["title"], "description": content["description"],
                "performer": content["performer"],
                "performer_slug": performer_slug(content["performer"]),
                "slug": f"{slugify(content['title'])}-{date}", "tags": content["tags"],
                "date": date, "views": bv.get("views", 0)
            })
            time.sleep(CONFIG["claude_delay"])
        save_videos(CONFIG["data_file"], videos)

    log.info("Building static site files...")
    build_site(CONFIG["output_dir"], CONFIG["data_file"])
    log.info("Starting SFTP Upload Phase...")
    upload_via_sftp(CONFIG["output_dir"], CONFIG["remote_root"])

    log.info("━" * 50)
    log.info("MIGRATION COMPLETE")
    log.info("━" * 50)

    # Trigger deploy workflow so NAS runner rsyncs site to Hostinger (if GITHUB_TOKEN set)
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_PAT")
    if token:
        try:
            r = requests.post(
                "https://api.github.com/repos/runner88888888/mygirlhub/actions/workflows/deploy.yml/dispatches",
                headers={"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"},
                json={"ref": "master"},
                timeout=10,
            )
            if r.status_code == 204:
                log.info("Deploy workflow triggered.")
            else:
                log.warning(f"Deploy trigger failed: {r.status_code} {r.text[:200]}")
        except Exception as e:
            log.warning(f"Deploy trigger error: {e}")
    else:
        log.info("Set GITHUB_TOKEN or GH_PAT to auto-trigger deploy after build.")

if __name__ == "__main__":
    main()