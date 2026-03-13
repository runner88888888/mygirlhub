#!/usr/bin/env python3
"""
MyGirlHub Rebuild Site
======================
Rebuilds the static site from existing videos.json (no LLM calls).
Outputs to /site then deploys ALL files to Hostinger via SFTP.
Run this after template changes to regenerate and publish HTML.

Usage (in Portainer console):
  cd /app
  REBUILD_OUTPUT=/site REBUILD_DATA=/site/videos.json python rebuild_site.py

All credentials are read from environment variables (set in your .env / stack).
"""

import os, sys, logging, subprocess
from pathlib import Path
from sitebuilder import build_site
import paramiko

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__name__)

OUTPUT_DIR  = os.environ.get("REBUILD_OUTPUT", "/site")
DATA_FILE   = os.environ.get("REBUILD_DATA",   "/site/videos.json")

# SFTP config — same vars used by publisher.py
SSH_HOST    = os.environ.get("SSH_HOST",    "195.35.39.252")
SSH_PORT    = int(os.environ.get("SSH_PORT", "65002"))
SSH_USER    = os.environ.get("SSH_USER",    "u426197676")
SSH_PASS    = os.environ.get("SSH_PASSWORD", "")
REMOTE_ROOT = os.environ.get("REMOTE_ROOT", "/home/u426197676/domains/mygirlhub.com/public_html")

# File extensions to upload (skip videos.json source data and other non-web files)
UPLOAD_EXTS = {".html", ".xml", ".txt", ".css", ".js", ".ico", ".png", ".jpg", ".svg", ".webp"}


def git_pull_app_dir():
    """Run 'git pull' in the app (repo) directory so the NAS has latest code. No-op if git missing or not a repo."""
    app_dir = os.path.dirname(os.path.abspath(__file__)) or "."
    if not os.path.isdir(os.path.join(app_dir, ".git")):
        return
    try:
        r = subprocess.run(
            ["git", "pull", "--ff-only"],
            cwd=app_dir,
            capture_output=True,
            text=True,
            timeout=60,
        )
        if r.returncode == 0:
            log.info("git pull: %s", (r.stdout or "").strip() or "already up to date")
        else:
            log.warning("git pull failed: %s", (r.stderr or r.stdout or "").strip())
    except FileNotFoundError:
        log.info("git not installed in container — skipping pull (upload files or use image with git)")
    except subprocess.TimeoutExpired:
        log.warning("git pull timed out — continuing with existing code")
    except Exception as e:
        log.warning("git pull error: %s — continuing with existing code", e)


def sftp_deploy_all(local_root, remote_root):
    """Walk local_root and upload every web file to remote_root via SFTP."""
    if not SSH_PASS:
        log.warning("SSH_PASSWORD not set — skipping SFTP deploy.")
        log.warning("Set SSH_PASSWORD in your environment or .env file.")
        return

    log.info(f"Connecting to {SSH_HOST}:{SSH_PORT} as {SSH_USER} ...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SSH_HOST, port=SSH_PORT, username=SSH_USER, password=SSH_PASS, timeout=20)
    sftp = ssh.open_sftp()

    created_dirs = set()

    def mkdir_p(remote_path):
        """Create remote directory tree, skipping already-created ones."""
        parts = remote_path.rstrip('/').split('/')
        current = ''
        for part in parts:
            if not part:
                continue
            current += '/' + part
            if current not in created_dirs:
                try:
                    sftp.mkdir(current)
                except OSError:
                    pass  # already exists
                created_dirs.add(current)

    uploaded = 0
    skipped  = 0

    for dirpath, dirnames, filenames in os.walk(local_root):
        # Skip hidden dirs
        dirnames[:] = [d for d in dirnames if not d.startswith('.')]
        for filename in filenames:
            if filename.startswith('.'):
                continue
            ext = Path(filename).suffix.lower()
            if ext not in UPLOAD_EXTS:
                skipped += 1
                continue

            local_path  = os.path.join(dirpath, filename)
            rel_path    = os.path.relpath(local_path, local_root).replace('\\', '/')
            remote_path = remote_root.rstrip('/') + '/' + rel_path
            remote_dir  = '/'.join(remote_path.split('/')[:-1])

            mkdir_p(remote_dir)
            sftp.put(local_path, remote_path)
            log.info(f"  ↑ {rel_path}")
            uploaded += 1

    sftp.close()
    ssh.close()
    log.info(f"Deploy complete — {uploaded} files uploaded, {skipped} skipped.")


def main():
    git_pull_app_dir()

    if not os.path.exists(DATA_FILE):
        log.error(f"videos.json not found at: {DATA_FILE}")
        log.error("Run builder.py first to create it, or copy an existing videos.json to /site/")
        sys.exit(1)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    log.info(f"Rebuilding site from {DATA_FILE} → {OUTPUT_DIR}")
    count = build_site(OUTPUT_DIR, DATA_FILE)
    log.info(f"Build complete — {count} videos.")

    log.info(f"Deploying to {SSH_HOST} → {REMOTE_ROOT}")
    sftp_deploy_all(OUTPUT_DIR, REMOTE_ROOT)


if __name__ == "__main__":
    main()
