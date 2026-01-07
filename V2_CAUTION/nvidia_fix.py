#!/usr/bin/env python3
import subprocess
from datetime import datetime
from pathlib import Path

BASE_DIR = Path("/var/home/fraser/backup_service")
LOG_FILE = BASE_DIR / "nvidia_fix.log"

REQUIRED_ARGS = [
    "rd.driver.blacklist=nouveau",
    "nvidia-drm.modeset=1",
]

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
    log("=== NVIDIA FIX STARTED ===")

    # Read current kernel args
    result = run(["rpm-ostree", "kargs"])
    if result.returncode != 0:
        log("ERROR: Could not read kernel args")
        return

    current_args = result.stdout.strip().split()
    log(f"Current kernel args:\n{' '.join(current_args)}")

    # Build atomic rpm-ostree command
    cmd = ["rpm-ostree", "kargs"]

    # Delete any existing copies of required args
    for arg in REQUIRED_ARGS:
        if arg in current_args:
            cmd.append(f"--delete={arg}")

    # Append clean copies
    for arg in REQUIRED_ARGS:
        cmd.append(f"--append={arg}")

    # Apply update
    result = run(cmd)
    if result.returncode != 0:
        log("ERROR: Failed to update kernel args")
        return

    log("=== NVIDIA FIX COMPLETED ===")

if __name__ == "__main__":
    main()
