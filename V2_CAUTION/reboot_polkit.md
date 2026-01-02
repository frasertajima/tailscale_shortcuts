# 📘 **reboot.md — Headless Reboot Endpoint + Polkit Authorization**

This document describes how to enable a **modular, headless reboot endpoint** in the FastAPI automation service.  
It mirrors the structure used for the NVIDIA fix module and follows the same privilege‑boundary philosophy.

---

# 🧩 1. Overview

The `/reboot` endpoint allows the system to reboot **on demand**, triggered remotely via FastAPI.  
This endpoint is intentionally decoupled from other modules (e.g., `nvidia_fix`) so that:

- maintenance tasks can run without forcing an immediate reboot
- the user can choose the best time to reboot
- the reboot endpoint can serve as a remote “lockout” mechanism (forces login screen)
- privilege boundaries remain clean and modular

By default, `systemctl reboot` requires authentication.  
To enable headless operation, a dedicated polkit rule is required.

---

# 🔐 2. Polkit Rule for Headless Reboot

Create the file:

```
sudo nano /etc/polkit-1/rules.d/91-reboot.rules
```

Contents:

```javascript
polkit.addRule(function(action, subject) {
    if (action.id == "org.freedesktop.login1.reboot" &&
        subject.isInGroup("wheel")) {
        return polkit.Result.YES;
    }
});
```

This rule:

- authorizes **only** the reboot action
- applies **only** to users in the `wheel` group
- keeps privileges tightly scoped
- matches the modular design of the automation suite

Restart polkit:

```
sudo systemctl restart polkit
```

Test manually:

```
systemctl reboot
```

If the rule is active, the system will reboot immediately with **no**:

- password
- fingerprint
- FIDO2
- GUI prompt

---

# ⚙️ 3. FastAPI Implementation

Add this function to `main.py`:

```python
def run_reboot():
    log_path = "/var/home/fraser/backup_service/reboot.log"

    with open(log_path, "a") as f:
        f.write("\n=== REBOOT TRIGGERED ===\n")

    p = subprocess.Popen(
        ["systemctl", "reboot"],
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
```

Add the route:

```python
@app.post("/reboot")
def trigger_reboot(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_reboot)
    return {"status": "reboot_started"}
```

This matches the structure of:

- `/backup`
- `/kleopatra`
- `/nvidia_fix`

and keeps the automation suite consistent and predictable.

---

# 🧪 4. Verification

### 4.1 Test via FastAPI

Trigger:

```
POST /reboot
```

Expected behavior:

- log entry created
- system reboots immediately
- no authentication prompts

### 4.2 Check logs

```
cat /var/home/fraser/backup_service/reboot.log
```

You should see:

```
=== REBOOT TRIGGERED ===
STDOUT:

STDERR:
```

(Empty stderr indicates success.)

---

# 🧱 5. Why This Module Is Separate

Keeping reboot authorization in its own file:

- matches the modular endpoint design
- prevents accidental privilege escalation
- allows future modules to reuse the pattern
- keeps polkit rules easy to audit
- supports security use‑cases (remote lockout)

This is the cleanest and safest way to integrate reboot functionality into your automation suite.