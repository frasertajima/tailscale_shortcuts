from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import subprocess
from pathlib import Path
from datetime import datetime
import json
import webbrowser
from threading import Timer
from setup_thinkpad import run_setup, load_status, new_status, save_status
from missouri_query import (
    run_missouri_query,
    run_missouri_select,
    run_missouri_delete,
    run_missouri_update,
    run_missouri_insert
)

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

def open_browser():
    """Open browser after a short delay to ensure server is ready"""
    webbrowser.open('http://127.0.0.1:8000/db2_display')

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


def run_ostree_upgrade():
    log("=== OSTREE UPGRADE TRIGGERED ===")

    upgrade_script = "/var/home/fraser/backup_service/ostree_upgrade.py"

    # Spawn the upgrade script as a separate process
    result = subprocess.Popen(
        ["/usr/bin/env", "python3", upgrade_script],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    log(f"Spawned ostree upgrade script (PID {result.pid})")
    log("Upgrade will continue in background")

    return True



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
# OLLAMA ON
# -----------------------------
def run_ollama_on():
    p = subprocess.Popen(
        [
            "distrobox", "enter", CONTAINER_NAME,
            "--",
            "/var/home/fraser/backup_service/ollama_on.sh"
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    out, err = p.communicate()
    write_log("/var/home/fraser/backup_service/ollama.log",
              "OLLAMA SERVER STARTED", out, err)

# -----------------------------
# OLLAMA OFF
# -----------------------------
def run_ollama_off():
    p = subprocess.Popen(
        [
            "distrobox", "enter", CONTAINER_NAME,
            "--",
            "/var/home/fraser/backup_service/ollama_off.sh"
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    out, err = p.communicate()
    write_log("/var/home/fraser/backup_service/ollama.log",
              "OLLAMA SERVER STOPPED", out, err)

# -----------------------------
# OCR IMAGES
# -----------------------------
def run_ocr_images():
    p = subprocess.Popen(
        [
            "distrobox", "enter", CONTAINER_NAME,
            "--",
            "/var/home/fraser/backup_service/ocr_images.sh"
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    out, err = p.communicate()
    write_log("/var/home/fraser/backup_service/ollama.log",
              "OCR IMAGES TRIGGERED", out, err)

# -----------------------------
# COBOL DB2 QUERY TEST
# -----------------------------
def run_db2_query():
    """Query DB2 via COBOL program and return JSON"""
    try:
        # Submit job and get output
        result = subprocess.run([
            "zowe", "jobs", "submit", "ds", "Z89165.JCL(CBLDB21)",
            "--view-all-spool-content"
        ], capture_output=True, text=True, check=True)

        # Extract PIPEOUT section
        output = result.stdout
        start = output.find("Spool file: PIPEOUT")
        end = output.find("Spool file: SYSTSPRT")

        if start == -1 or end == -1:
            write_log("/var/home/fraser/backup_service/db2.log",
                     "DB2 QUERY FAILED", output[:500], "PIPEOUT spool not found")
            return None

        # Get pipe-delimited content
        pipe_section = output[start:end]
        lines = pipe_section.split('\n')[1:]  # Skip "Spool file:" header

        # Parse each line
        records = []
        for line in lines:
            line = line.strip()
            if not line or '|' not in line:
                continue

            parts = line.split('|')
            if len(parts) >= 6:
                records.append({
                    "account_no": parts[0].strip(),
                    "limit": float(parts[1].strip()),
                    "balance": float(parts[2].strip()),
                    "surname": parts[3].strip(),
                    "firstname": parts[4].strip(),
                    "comments": parts[5].strip()
                })

        result_json = json.dumps(records)
        write_log("/var/home/fraser/backup_service/db2.log",
                 "DB2 QUERY SUCCESS", f"Loaded {len(records)} records", "")

        return result_json

    except Exception as e:
        import traceback
        write_log("/var/home/fraser/backup_service/db2.log",
                 "DB2 QUERY ERROR", traceback.format_exc(), str(e))
        return None




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

@app.post("/ollama_on")
def trigger_ollama_on(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_ollama_on)
    return {"status": "ollama_on_started"}

@app.post("/ollama_off")
def trigger_ollama_off(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_ollama_off)
    return {"status": "ollama_off_started"}

@app.post("/ocr_images")
def trigger_ocr_images(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_ocr_images)
    return {"status": "ocr_images_started"}

# -----------------------------
# SETUP THINKPAD
# -----------------------------
@app.post("/setup_thinkpad")
def trigger_setup_thinkpad(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_setup)
    return {"status": "setup_thinkpad_started"}

@app.get("/setup_thinkpad_status")
def setup_thinkpad_status():
    return load_status()

@app.post("/setup_thinkpad_reset")
def setup_thinkpad_reset():
    status = new_status()
    save_status(status)
    return status

@app.get("/setup_thinkpad", response_class=HTMLResponse)
def setup_thinkpad_page():
    with open("/var/home/fraser/backup_service/templates/setup_thinkpad.html") as f:
        return f.read()

# -----------------------------
# COBOL DB2
# -----------------------------
@app.get("/test_db2")
def test_db2():
    """Query DB2 and return JSON results"""
    json_data = run_db2_query()

    if json_data is None:
        return {"status": "error", "message": "Failed to query DB2"}

    try:
        import json
        return json.loads(json_data)
    except json.JSONDecodeError as e:
        return {"status": "error", "message": f"Invalid JSON: {str(e)}"}

@app.get("/db2_display", response_class=HTMLResponse)
def db2_display():
    with open("/var/home/fraser/backup_service/templates/db2_display.html") as f:
        return f.read()

@app.get("/trigger_db2")
def trigger_db2(background_tasks: BackgroundTasks):
    """Opens browser and redirects to display page"""
    background_tasks.add_task(lambda: webbrowser.open('http://127.0.0.1:8000/db2_display'))
    return RedirectResponse(url="/db2_display")



# Lab 9.2: Missouri Employment data db2 ###########################################
@app.get("/missouri_main", response_class=HTMLResponse)
def missouri_main():
    with open("/var/home/fraser/backup_service/templates/missouri_main.html") as f:
        return f.read()

@app.get("/trigger_missouri_main")
def trigger_missouri_select(background_tasks: BackgroundTasks):
    background_tasks.add_task(lambda: webbrowser.open('http://127.0.0.1:8000/missouri_main'))
    return RedirectResponse(url="/missouri_main")


@app.post("/missouri_select")
def missouri_select(request_body: dict):
    """Query specific RECORDID(s). Expects JSON: {"record_ids": ["08012011", "07012011"]}"""
    ids = request_body.get("record_ids", [])
    if not ids:
        return {"status": "error", "message": "No record_ids provided"}
    json_data = run_missouri_select(ids)
    if json_data is None:
        return {"status": "error", "message": "Failed to query Missouri data"}
    try:
        return json.loads(json_data)
    except json.JSONDecodeError as e:
        return {"status": "error", "message": f"Invalid JSON: {str(e)}"}

@app.get("/missouri_select_display", response_class=HTMLResponse)
def missouri_select_display():
    with open("/var/home/fraser/backup_service/templates/missouri_select.html") as f:
        return f.read()

@app.get("/trigger_missouri_select")
def trigger_missouri_select(background_tasks: BackgroundTasks):
    background_tasks.add_task(lambda: webbrowser.open('http://127.0.0.1:8000/missouri_select_display'))
    return RedirectResponse(url="/missouri_select_display")


@app.get("/missouri_data")
def missouri_data():
    """Query Missouri unemployment data and return JSON results"""
    json_data = run_missouri_query()
    if json_data is None:
        return {"status": "error", "message": "Failed to query Missouri data"}
    try:
        return json.loads(json_data)
    except json.JSONDecodeError as e:
        return {"status": "error", "message": f"Invalid JSON: {str(e)}"}

@app.get("/missouri_display", response_class=HTMLResponse)
def missouri_display():
    with open("/var/home/fraser/backup_service/templates/missouri_display.html") as f:
        return f.read()

@app.get("/trigger_missouri")
def trigger_missouri(background_tasks: BackgroundTasks):
    background_tasks.add_task(lambda: webbrowser.open('http://127.0.0.1:8000/missouri_display'))
    return RedirectResponse(url="/missouri_display")

@app.post("/missouri_update")
def missouri_update(request_body: dict):
    """Update a RECORDID. Expects JSON: {"record_id": "09012011", "ethnicity": {...}, "age": {...}, ...}"""
    record_id = request_body.get("record_id", "")
    if not record_id:
        return {"status": "error", "message": "No record_id provided"}
    result = run_missouri_update(record_id, request_body)
    if result is None:
        return {"status": "error", "message": "Failed to update record"}
    return result

@app.post("/missouri_insert")
async def missouri_insert(request: Request):
    request_body = await request.json()
    record_id = request_body.get("record_id", "")
    if not record_id:
        return {"status": "error", "message": "No record_id provided"}
    result = run_missouri_insert(record_id, request_body)
    if result is None:
        return {"status": "error", "message": "Failed to insert record"}
    return result

@app.get("/missouri_add", response_class=HTMLResponse)
def missouri_add():
    with open("/var/home/fraser/backup_service/templates/missouri_add.html") as f:
        return f.read()


@app.post("/missouri_delete")
def missouri_delete(request_body: dict):
    """Delete a RECORDID from all 5 tables. Expects JSON: {"record_id": "08012011"}"""
    record_id = request_body.get("record_id", "")
    if not record_id:
        return {"status": "error", "message": "No record_id provided"}
    result = run_missouri_delete(record_id)
    if result is None:
        return {"status": "error", "message": "Failed to delete record"}
    return result
