# 📘 **ostree_upgrade.md — Headless rpm‑ostree Upgrade Endpoint**

This document describes how to enable a **headless, remotely triggerable rpm‑ostree upgrade** through the FastAPI automation service.  
It follows the same modular design as the `nvidia_fix`, `reboot`, and other v2 endpoints.

---

# 🧩 1. Overview

The `/ostree_upgrade` endpoint allows the system to:

- refresh rpm‑md metadata
- resolve dependencies
- stage a new OSTree deployment (if available)
- log all output

…without requiring interactive authentication.

This endpoint is intentionally decoupled from rebooting.  
After an upgrade, the user may choose to reboot immediately via `/reboot` or wait until convenient.

---

# 🔐 2. Polkit Authorization (Broader Scope)

Unlike kernel‑args or reboot, the `rpm‑ostree upgrade` action does **not** consistently expose a single, stable polkit action ID across Fedora Silverblue versions.  
In practice:

- some versions use `org.projectatomic.rpmostree1.upgrade`
- others use `org.projectatomic.rpmostree1.deploy`
- others use `org.projectatomic.rpmostree1.osc`
- some use multiple actions depending on the upgrade path

Because of this variability, and because polkit logs do not always surface the action ID reliably, we temporarily authorize **all rpm‑ostree D‑Bus actions** for `wheel` users.

This is a controlled, explicit tradeoff that matches the v2 automation model.

### **Polkit rule: `/etc/polkit-1/rules.d/92-rpm-ostree.rules`**

```javascript
polkit.addRule(function(action, subject) {
    // Allow wheel users to perform rpm-ostree operations without interactive auth
    if (action.id.indexOf("org.projectatomic.rpmostree1") === 0 &&
        subject.isInGroup("wheel")) {
        return polkit.Result.YES;
    }
});
```

Restart polkit:

```
sudo systemctl restart polkit
```

### ⚠️ Note on scope

This rule authorizes:

- `rpm-ostree upgrade`
- `rpm-ostree rebase`
- `rpm-ostree deploy`
- `rpm-ostree cleanup` (if privileged)
- any future rpm‑ostree D‑Bus actions

This is safe within your threat model because:

- all automation runs under your user account
- your user is already in `wheel`
- Tailscale restricts API access
- the endpoint is modular and auditable

Later, when Fedora stabilizes the action ID or when logs reveal the exact identifier, this rule can be narrowed to a single action.

---

# ⚙️ 3. FastAPI Implementation

Add the upgrade function to `main.py`:

```python
def run_ostree_upgrade():
    log_path = "/var/home/fraser/backup_service/ostree_upgrade.log"

    with open(log_path, "a") as f:
        f.write("\n=== OSTREE UPGRADE TRIGGERED ===\n")

    p = subprocess.Popen(
        ["rpm-ostree", "upgrade"],
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

Add the FastAPI route:

```python
@app.post("/ostree_upgrade")
def trigger_ostree_upgrade(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_ostree_upgrade)
    return {"status": "upgrade_started"}
```

This matches the structure of all other v2 modules.

---

# 🧪 4. Verification

### 4.1 Trigger via API

```
POST /ostree_upgrade
```

Expected behavior:

- metadata refresh
- dependency resolution
- staging of new deployment (if available)
- clean log output
- no authentication prompts

### 4.2 Check logs

```
cat /var/home/fraser/backup_service/ostree_upgrade.log
```

You should see:

- metadata updates
- repo refresh
- dependency resolution
- either a new deployment or “No upgrade available.”

---

# 🧱 5. Why This Module Is Separate

Keeping upgrade authorization in its own rule file:

- matches the modular endpoint design
- keeps privilege boundaries clear
- allows future refinement
- avoids mixing unrelated permissions
- supports voice‑triggered maintenance workflows

This is the cleanest and safest way to integrate rpm‑ostree upgrades into your automation suite.

---

# 🔮 6. Future Refinement

When a future upgrade triggers a clear polkit action ID, this rule can be narrowed to:

```javascript
if (action.id == "org.projectatomic.rpmostree1.upgrade" && ...)
```

Until then, the broader namespace rule provides reliable, headless operation.
