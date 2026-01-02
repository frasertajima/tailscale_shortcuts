_This folder contains version 2 of our tailscale shortcuts that includes a shortcut to fix the nvidia driver (whenever Fedora Silverblue updates, there is a good chance that `nvidia-smi` will no longer access the driver so we have to fix it manually)._

_Normally, the rpm-ostree change requires 'systemctl reboot' but rather than bunch that in with the  
/nvidia_fix, we also created a separate /reboot automation that can be used (carefully) for all sorts of purposes. This enables the user to remotely fix the nvidia driver and wait until later to reboot._

_You should replace the `main.py` file from version 2 in your original `/backup_services` directory on your local machine if you wish to add /nvidia_fix and /reboot to your automations (they are kept separate if not needed so that the user can add or skip new shortcuts over time). You will also need to add Android and iOS automations as outlined in the earlier documentation with the new endpoints._

_Also, because these shortcuts operate without user intervention or screen output, you should always review the `***.log` files saved in the `/backup_services` directory to double check that /backup or other shortcuts have completed. Obviously Kleopatra will have worked if you can use the app and /shutdown will be obvious as well, but for shortcuts like /backup, it is useful to make sure all operations worked as expected._

# 📘 **How to Update `main.py` and Restart the FastAPI Automation Service**

This document describes the exact steps required to update the automation service and restart it safely.  
Use this whenever you modify:

- `main.py`
- any module scripts
- logging paths
- subprocess calls
- polkit rules that affect automation behavior

---

# 🧩 **1. Edit `main.py`**

```
nano /var/home/fraser/backup_service/main.py
```

Make your changes:

- add new automation modules
- refactor existing modules
- update script paths
- adjust logging
- modify subprocess calls

Save and exit.

---

# 🧪 **2. Validate the code (optional but recommended)**

```
uv run /var/home/fraser/backup_service/main.py --help
```

This catches:

- syntax errors
- missing imports
- missing dependencies

---

# 🔄 **3. Restart the FastAPI systemd service**

Your service is a **system‑level** service, not a user service.

Restart it with:

```
sudo systemctl restart backup_service
```

Check status:

```
sudo systemctl status backup_service
```

You should see:

- `Active: active (running)`
- no Python tracebacks
- no import errors

---

# 🌐 **4. Verify the API is running**

Open:

```
http://localhost:8000/docs
```

(or your Tailscale IP)

Confirm:

- `/backup`
- `/kleopatra`
- `/nvidia_fix`
- `/reboot`
-  `/...`, as new shortcuts are added

all appear and load correctly.

---

# 📜 **5. Optional: Tail logs**

If you want to watch the service in real time:

```
sudo journalctl -u backup_service -f
```

This is useful after adding new modules.

---

# 🚀 **Quick Reference**

```
# Edit main.py
nano ~/backup_service/main.py

# Validate
uv run ~/backup_service/main.py --help

# Restart service
sudo systemctl restart backup_service

# Check status
sudo systemctl status backup_service

# View API
http://localhost:8000/docs
```
