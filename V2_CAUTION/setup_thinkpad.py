import subprocess
import json
from datetime import datetime
from pathlib import Path

BASE_DIR = Path("/var/home/fraser/backup_service")
STATUS_FILE = BASE_DIR / "setup_thinkpad_status.json"
LOG_FILE = BASE_DIR / "setup_thinkpad.log"
CONTAINER_NAME = "fedora42-nvidia"


def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{timestamp} {msg}"
    with LOG_FILE.open("a") as f:
        f.write(line + "\n")
    print(line)


def load_status():
    if STATUS_FILE.exists():
        with STATUS_FILE.open() as f:
            return json.load(f)
    return new_status()


def new_status():
    return {
        "phase": "ostree_upgrade",
        "started": datetime.now().isoformat(),
        "updated": datetime.now().isoformat(),
        "steps": {
            "ostree_upgrade": {"status": "pending", "detail": ""},
            "nvidia_fix": {"status": "pending", "detail": ""},
            "security_key": {"status": "pending", "detail": ""},
            "vscode_on": {"status": "pending", "detail": ""},
            "backup": {"status": "pending", "detail": ""},
        },
    }


def save_status(status):
    status["updated"] = datetime.now().isoformat()
    with STATUS_FILE.open("w") as f:
        json.dump(status, f, indent=2)


def run_cmd(cmd, **kwargs):
    log(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, **kwargs)
    if result.stdout.strip():
        log(f"stdout: {result.stdout.strip()}")
    if result.stderr.strip():
        log(f"stderr: {result.stderr.strip()}")
    return result


def nvidia_smi_ok():
    """Check if nvidia-smi works (run inside the container)."""
    result = subprocess.run(
        ["distrobox", "enter", CONTAINER_NAME, "--", "nvidia-smi"],
        capture_output=True, text=True,
    )
    return result.returncode == 0


# ---------------------
# PHASE: ostree_upgrade
# ---------------------
def phase_ostree_upgrade(status):
    log("=== PHASE: ostree_upgrade ===")
    status["steps"]["ostree_upgrade"]["status"] = "running"
    save_status(status)

    result = run_cmd(["rpm-ostree", "upgrade"])

    if result.returncode != 0:
        status["steps"]["ostree_upgrade"]["status"] = "failed"
        status["steps"]["ostree_upgrade"]["detail"] = (
            f"rpm-ostree upgrade failed: {result.stderr.strip()}"
        )
        save_status(status)
        return False

    stdout = result.stdout.strip()

    # "Staging deployment...done" = new deployment staged, reboot needed
    # "No upgrade available." = already up to date
    upgraded = "staging deployment" in stdout.lower()

    if upgraded:
        status["steps"]["ostree_upgrade"]["status"] = "done_needs_reboot"
        status["steps"]["ostree_upgrade"]["detail"] = (
            "Upgrade staged. Reboot required, then run /setup_thinkpad again."
        )
        status["phase"] = "post_reboot_check"
        save_status(status)
        log("Upgrade staged - reboot needed before continuing")
        return False  # stop here, user must reboot
    else:
        status["steps"]["ostree_upgrade"]["status"] = "skipped"
        status["steps"]["ostree_upgrade"]["detail"] = "Already up to date"
        status["phase"] = "post_reboot_check"
        save_status(status)
        log("System already up to date, skipping reboot")
        return True  # continue immediately


# ---------------------
# PHASE: post_reboot_check (nvidia)
# ---------------------
def phase_post_reboot_check(status):
    log("=== PHASE: post_reboot_check (nvidia) ===")
    status["steps"]["nvidia_fix"]["status"] = "running"
    save_status(status)

    if nvidia_smi_ok():
        status["steps"]["nvidia_fix"]["status"] = "skipped"
        status["steps"]["nvidia_fix"]["detail"] = "nvidia-smi works, no fix needed"
        status["phase"] = "security_key"
        save_status(status)
        log("nvidia-smi OK, skipping nvidia_fix")
        return True

    log("nvidia-smi broken, running nvidia_fix")
    result = run_cmd([
        "/var/home/fraser/.cargo/bin/uv", "run",
        str(BASE_DIR / "nvidia_fix.py"),
    ])

    if result.returncode != 0:
        status["steps"]["nvidia_fix"]["status"] = "failed"
        status["steps"]["nvidia_fix"]["detail"] = (
            f"nvidia_fix.py failed: {result.stderr.strip()}"
        )
        save_status(status)
        return False

    status["steps"]["nvidia_fix"]["status"] = "done_needs_reboot"
    status["steps"]["nvidia_fix"]["detail"] = (
        "Kernel args updated. Reboot required, then run /setup_thinkpad again."
    )
    status["phase"] = "security_key"
    save_status(status)
    log("nvidia_fix applied - reboot needed before continuing")
    return False  # stop here, user must reboot


# ---------------------
# PHASE: security_key
# ---------------------
def phase_security_key(status):
    log("=== PHASE: security_key ===")
    status["steps"]["security_key"]["status"] = "running"
    save_status(status)

    result = run_cmd([
        "/var/home/fraser/.cargo/bin/uv", "run",
        str(BASE_DIR / "kleopatra.py"),
    ])

    if result.returncode != 0:
        status["steps"]["security_key"]["status"] = "failed"
        status["steps"]["security_key"]["detail"] = (
            f"kleopatra.py failed: {result.stderr.strip()}"
        )
        save_status(status)
        return False

    status["steps"]["security_key"]["status"] = "done"
    status["steps"]["security_key"]["detail"] = "YubiKey initialized"
    status["phase"] = "vscode_on"
    save_status(status)
    return True


# ---------------------
# PHASE: vscode_on
# ---------------------
def phase_vscode_on(status):
    log("=== PHASE: vscode_on ===")
    status["steps"]["vscode_on"]["status"] = "running"
    save_status(status)

    result = run_cmd([
        "distrobox", "enter", CONTAINER_NAME,
        "--", "/var/home/fraser/backup_service/vscode_on.sh",
    ])

    if result.returncode != 0:
        status["steps"]["vscode_on"]["status"] = "failed"
        status["steps"]["vscode_on"]["detail"] = (
            f"vscode_on.sh failed: {result.stderr.strip()}"
        )
        save_status(status)
        return False

    status["steps"]["vscode_on"]["status"] = "done"
    status["steps"]["vscode_on"]["detail"] = "VS Code + Jupyter started"
    status["phase"] = "backup"
    save_status(status)
    return True


# ---------------------
# PHASE: backup
# ---------------------
def phase_backup(status):
    log("=== PHASE: backup ===")
    status["steps"]["backup"]["status"] = "running"
    save_status(status)

    result = run_cmd([
        "distrobox", "enter", CONTAINER_NAME,
        "--", "/var/home/fraser/.cargo/bin/uv", "run",
        "/var/home/fraser/backup_service/backup.py",
    ])

    if result.returncode != 0:
        status["steps"]["backup"]["status"] = "failed"
        status["steps"]["backup"]["detail"] = (
            f"backup.py failed: {result.stderr.strip()}"
        )
        save_status(status)
        return False

    status["steps"]["backup"]["status"] = "done"
    status["steps"]["backup"]["detail"] = "Backup complete"
    status["phase"] = "complete"
    save_status(status)
    return True


# ---------------------
# MAIN ORCHESTRATOR
# ---------------------
PHASES = {
    "ostree_upgrade": phase_ostree_upgrade,
    "post_reboot_check": phase_post_reboot_check,
    "security_key": phase_security_key,
    "vscode_on": phase_vscode_on,
    "backup": phase_backup,
}


def run_setup():
    status = load_status()

    # If a previous run completed, start fresh
    if status["phase"] == "complete":
        status = new_status()
        save_status(status)

    log(f"=== SETUP THINKPAD STARTED (resuming at: {status['phase']}) ===")

    while status["phase"] in PHASES:
        phase_fn = PHASES[status["phase"]]
        should_continue = phase_fn(status)
        if not should_continue:
            log(f"=== SETUP PAUSED at phase: {status['phase']} ===")
            return status

    log("=== SETUP THINKPAD COMPLETE ===")
    return status


if __name__ == "__main__":
    run_setup()
