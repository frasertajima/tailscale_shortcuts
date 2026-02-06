_Feb 6: added Ollama and OCR shortcuts_



https://github.com/user-attachments/assets/b90a134c-0915-40ef-805c-4d367d9b9f37



_Jan 15: added /wol using Synology NAS, tailscale and iOS shortcuts_

_fixes to /nvidia_fix and /ostree_upgrade to make sure they are triggered._

_vscode_on.sh has been refactored to enable https connections for VS Code and Jupyter Labs. This avoids the insecure site message (even though it is secure inside Tailscale) and it also enables VS Code to load Jupyter Notebooks properly! The tailscale serve commands are set out in `update_to_https.md`. We did lose the VSCode icon on the iPad homescreen shortcut, however. Getting it back is a bit of a hassle._

_`main.py` has been refactored to be modular and enable timestamps in the logs for each shortcut. `/rpm_ostree` enables remote "rpm-ostree upgrade" in Fedora Silverblue without user intervention. Once finished, you can trigger the `/reboot` shortcut to complete the upgrade when convenient. `/vscode_on` starts up the VSCode server from Microsoft in a distrobox container that is set up as well as a Jupyter Labs server. VSCode does not seem to load Jupyter Notebooks on the iPad so Jupyter Labs is needed for machine learning work (and is fast). This enables full VSCode and Jupyter Labs access remotely on your iPad without limitations or performance issues (VSCode loads python, fortran files instantly but not Jupyter Notebooks). If you ever need to shutdown your servers cleanly, `/vscode_off` can be called by Siri (but leaving them on is not a burden)._

---

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
