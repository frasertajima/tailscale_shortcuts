#!/usr/bin/env python3
import subprocess
from datetime import datetime
from pathlib import Path

BASE_DIR = Path("/var/home/fraser/backup_service")
LOG_FILE = BASE_DIR / "ostree_upgrade.log"

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with LOG_FILE.open("a") as f:
        f.write(f"{timestamp} {msg}\n")
    print(msg)

def run(cmd):
    log(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        log("✓ Success")
        if result.stdout.strip():
            log(f"stdout: {result.stdout.strip()}")
    else:
        log(f"✗ Failed with exit code {result.returncode}")
        if result.stderr.strip():
            log(f"stderr: {result.stderr.strip()}")
    return result

def main():
    log("=== OSTREE UPGRADE STARTED ===")

    result = run(["rpm-ostree", "upgrade"])
    if result.returncode != 0:
        log("ERROR: rpm-ostree upgrade failed")
        return

    if not result.stdout.strip():
        log("System already up to date (no new deployment staged)")

    log("=== OSTREE UPGRADE COMPLETED ===")

if __name__ == "__main__":
    main()
