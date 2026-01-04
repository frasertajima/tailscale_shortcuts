from fastapi import FastAPI, BackgroundTasks
import subprocess
from pathlib import Path
from datetime import datetime

app = FastAPI()

# Host scripts
KLEO_SCRIPT = Path("/var/home/fraser/backup_service/kleopatra.py")
NVIDIA_SCRIPT = Path("/var/home/fraser/backup_service/nvidia_fix.py")

# Container script
BACKUP_SCRIPT = "/var/home/fraser/backup_service/backup.py"
CONTAINER_NAME = "fedora42-nvidia"


# -----------------------------
# HELPERS
# -----------------------------
def ts():
    return datetime.now().strftime("%Y-%m-%d %I:%M %p")

def write_log(path, header, stdout, stderr):
    with open(path, "a") as f:
        f.write(f"\n=== {header} @ {ts()} ===\n")
        f.write("STDOUT:\n")
        f.write(stdout or "")
        f.write("\nSTDERR:\n")
        f.write(stderr or "")
        f.write(f"\n=== END @ {ts()} ===\n")


# -----------------------------
# BACKUP MODULE
# -----------------------------
def run_backup():
    p = subprocess.Popen(
        [
            "distrobox", "enter", CONTAINER_NAME,
            "--",
            "/var/home/fraser/.cargo/bin/uv", "run",
            BACKUP_SCRIPT
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    out, err = p.communicate()
    write_log("/var/home/fraser/backup_service/backup.log",
              "BACKUP TRIGGERED", out, err)


# -----------------------------
# KLEOPATRA MODULE
# -----------------------------
def run_kleopatra():
    p = subprocess.Popen(
        ["/var/home/fraser/.cargo/bin/uv", "run", str(KLEO_SCRIPT)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    out, err = p.communicate()
    write_log("/var/home/fraser/backup_service/kleopatra.log",
              "KLEOPATRA TRIGGERED", out, err)


# -----------------------------
# NVIDIA FIX MODULE
# -----------------------------
def run_nvidia_fix():
    p = subprocess.Popen(
        ["/var/home/fraser/.cargo/bin/uv", "run", str(NVIDIA_SCRIPT)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    out, err = p.communicate()
    write_log("/var/home/fraser/backup_service/nvidia_fix.log",
              "NVIDIA FIX TRIGGERED", out, err)


# -----------------------------
# REBOOT MODULE
# -----------------------------
def run_reboot():
    p = subprocess.Popen(
        ["systemctl", "reboot"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    out, err = p.communicate()
    write_log("/var/home/fraser/backup_service/reboot.log",
              "REBOOT TRIGGERED", out, err)


# -----------------------------
# RPM-OSTREE UPGRADE
# -----------------------------
def run_ostree_upgrade():
    p = subprocess.Popen(
        ["rpm-ostree", "upgrade"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    out, err = p.communicate()
    write_log("/var/home/fraser/backup_service/ostree_upgrade.log",
              "OSTREE UPGRADE TRIGGERED", out, err)

# -----------------------------
# VSCODE + JUPYTER LABS ON
# -----------------------------
def run_vscode_on():
    p = subprocess.Popen(
        [
            "distrobox", "enter", CONTAINER_NAME,
            "--",
            "/var/home/fraser/backup_service/vscode_on.sh"
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    out, err = p.communicate()
    write_log("/var/home/fraser/backup_service/vscode_on.log",
              "VSCODE + JUPYTER STARTED", out, err)


# -----------------------------
# VSCODE + JUPYTER LABS OFF
# -----------------------------
def run_vscode_off():
    p = subprocess.Popen(
        [
            "distrobox", "enter", CONTAINER_NAME,
            "--",
            "/var/home/fraser/backup_service/vscode_off.sh"
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    out, err = p.communicate()
    write_log("/var/home/fraser/backup_service/vscode_off.log",
              "VSCODE + JUPYTER STOPPED", out, err)


# -----------------------------
# FASTAPI ROUTES
# -----------------------------
@app.post("/backup")
def trigger_backup(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_backup)
    return {"status": "backup_started"}

@app.post("/kleopatra")
def trigger_kleopatra(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_kleopatra)
    return {"status": "kleopatra_started"}

@app.post("/nvidia_fix")
def trigger_nvidia_fix(background_tasks: BackgroundTasks):
    if not NVIDIA_SCRIPT.exists():
        return {"status": "error", "message": "nvidia_fix.py not found"}

    background_tasks.add_task(run_nvidia_fix)
    return {"status": "nvidia_fix_started", "message": "System will reboot shortly."}

@app.post("/reboot")
def trigger_reboot(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_reboot)
    return {"status": "reboot_started"}

@app.post("/ostree_upgrade")
def trigger_ostree_upgrade(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_ostree_upgrade)
    return {"status": "upgrade_started"}

@app.post("/vscode_on")
def trigger_vscode_on(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_vscode_on)
    return {"status": "vscode_on_started"}

@app.post("/vscode_off")
def trigger_vscode_off(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_vscode_off)
    return {"status": "vscode_off_started"}
