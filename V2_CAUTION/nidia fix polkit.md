


# 📘 **Silverblue Automation Module: Kernel Args + Polkit + Headless Execution**

This document describes the complete workflow for building a headless automation module on Fedora Silverblue that performs privileged system mutations (e.g., kernel argument changes) without requiring biometric, password, or FIDO2 authentication.
It is based on the successful implementation of the `nvidia_fix` module.

---

## 🧩 **1. Overview**

Silverblue’s rpm‑ostree model requires privileged operations for:

- modifying kernel arguments
- triggering new deployments
- rebooting the system

By default, these operations require authentication via:

- fingerprint
- password
- FIDO2
- GNOME polkit agent

To automate these operations safely and remotely, we configure:

1. A minimal, idempotent script that performs the mutation
2. A FastAPI endpoint that triggers it
3. A polkit rule that authorizes the exact action ID
4. A verification workflow to ensure correctness

This pattern is reusable for any future module that needs privileged access.

---

## ⚙️ **2. Minimal NVIDIA Fix Script (example module)**

Purpose: enforce the single required kernel argument:

```
rd.driver.blacklist=nouveau
```

The script:

- reads current kernel args
- deletes the arg if present
- appends a clean copy
- performs one atomic rpm‑ostree operation
- reboots the system

This ensures a consistent, reproducible NVIDIA driver environment.

---

## 🔐 **3. Polkit Authorization**

### **3.1 Why polkit is required**

`rpm-ostree kargs` is not a simple command; it calls into `rpmostreed` over D‑Bus.
The D‑Bus method is:

```
KernelArgs
```

But the _authorization_ is controlled by a polkit action ID.

### **3.2 Discovering the correct action ID**

Silverblue versions differ, so we capture the real ID via polkit debug logs:

```
journalctl -u polkit -n 50
```

For this system, the action ID is:

```
org.projectatomic.rpmostree1.bootconfig
```

This is the key to headless execution.

---

## 🛡️ **4. Final Polkit Rule**

Create:

```
/etc/polkit-1/rules.d/90-nvidia-fix.rules
```

Contents:

```javascript
polkit.addRule(function(action, subject) {
    // Allow wheel users to modify kernel arguments via rpm-ostree
    if (action.id == "org.projectatomic.rpmostree1.bootconfig" &&
        subject.isInGroup("wheel")) {
        return polkit.Result.YES;
    }
});
```

Reload:

```
sudo systemctl restart polkit
```

---

## 🧪 **5. Verification Workflow**

### **5.1 Test kernel-arg mutation**

```
rpm-ostree kargs --append=test_arg=1
rpm-ostree kargs --delete=test_arg=1
```

Expected result:

- No fingerprint prompt
- No password prompt
- No FIDO2 prompt
- No GUI dialog

### **5.2 Test script execution**

```
uv run nvidia_fix.py
```

Should run fully headless and reboot the system.

### **5.3 Test FastAPI endpoint**

Trigger `/nvidia_fix` remotely.

Expected:

- HTTP 200
- System reboots
- NVIDIA stack loads cleanly

---

## 🧱 **6. Reusable Pattern for Future Modules**

Any future module that needs privileged operations can follow this pattern:

1. **Identify the D‑Bus method**
    Use `busctl introspect` to find the method being called.

2. **Trigger the operation once**
    Let polkit prompt.

3. **Capture the action ID**
    Using:

    ```
    journalctl -u polkit -n 50
    ```

4. **Write a polkit rule**
    Authorize that action for wheel users.

5. **Verify headless execution**
    Ensure no authentication prompts appear.

6. **Wrap in a FastAPI endpoint**
    Now safe to trigger remotely.


This gives you a scalable, modular automation framework for Silverblue.

---

## 🚀 **7. Why this matters**

You now have:

- a repeatable automation pattern
- a safe way to perform privileged operations
- a headless, remote‑triggerable fix pipeline
- a foundation for future modules (backup, warmup, health checks, etc.)

This is exactly the kind of infrastructure that makes day‑to‑day system maintenance effortless.
