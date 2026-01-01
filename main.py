from fastapi import FastAPI, BackgroundTasks
import subprocess
from pathlib import Path

app = FastAPI()

# Host script
KLEO_SCRIPT = Path("/var/home/fraser/backup_service/kleopatra.py")

# Container script
BACKUP_SCRIPT = "/var/home/fraser/backup_service/backup.py"
CONTAINER_NAME = "fedora42-nvidia"

def run_backup():
    log_path = "/var/home/fraser/backup_service/backup.log"

    with open(log_path, "a") as f:
        f.write("\n=== BACKUP TRIGGERED ===\n")

    p = subprocess.Popen(
        [
            "distrobox", "enter", CONTAINER_NAME,
            "--",
            "/var/home/fraser/.cargo/bin/uv", "run",
            "/var/home/fraser/backup_service/backup.py"
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    out, err = p.communicate()

    with open(log_path, "a") as f:
        f.write("STDOUT:\n")
        f.write(out or "")
        f.write("\nSTDERR:\n")
        f.write(err or "")
        f.write("\n=== END ===\n")


def run_kleopatra():
    p = subprocess.Popen(
        ["/var/home/fraser/.cargo/bin/uv", "run", str(KLEO_SCRIPT)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    out, err = p.communicate()

    with open("/var/home/fraser/backup_service/kleopatra.log", "a") as f:
        f.write("\n=== KLEOPATRA TRIGGERED ===\n")
        f.write("STDOUT:\n")
        f.write(out or "")
        f.write("\nSTDERR:\n")
        f.write(err or "")
        f.write("\n=== END ===\n")


@app.post("/backup")
def trigger_backup(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_backup)
    return {"status": "backup_started"}


@app.post("/kleopatra")
def trigger_kleopatra(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_kleopatra)
    return {"status": "kleopatra_started"}
