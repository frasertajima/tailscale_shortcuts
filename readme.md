
# 🚀 **Remote Backup + YubiKey Warm‑Up Workflow (extensible to any python script)**

_A fully automated, Tailscale‑secured, cross‑platform orchestration system triggered from your Pixel or iOS device. This is much faster than opening a command line and typing “uv run backup.py” every day for example._

---

## 🟦 **1. Your Pixel triggers everything**

You use MacroDroid on your Pixel to send an authenticated HTTP POST to your ThinkPad over Tailscale.

Two triggers exist:

- `/backup` → runs your full backup pipeline
- `/kleopatra` → warms up your YubiKey + GPG stack

Both are activated by a simple tile/shortcut on your Pixel.

No cloud.  
No Google Assistant interpretation.  
No friction.

---

## 🟦 **2. Tailscale provides the secure transport**

Your Pixel and ThinkPad communicate over your private Tailscale network:

```
https://thinkpad-p16.tailXXXX.ts.net/backup
https://thinkpad-p16.tailXXXX.ts.net/kleopatra
```

This gives you:

- end‑to‑end WireGuard encryption
- zero firewall configuration
- stable addressing
- no port forwarding
- no exposure to the public internet

It’s a perfect backbone for this kind of automation.

---

## 🟦 **3. FastAPI receives the request**

Your ThinkPad runs a lightweight FastAPI server with two endpoints:

```python
@app.post("/backup")
@app.post("/kleopatra")
```

Each endpoint:

- immediately returns a JSON response
- offloads the real work to a **BackgroundTask**
- keeps the API responsive
- avoids blocking your Pixel

---

## 🟦 **4. Background tasks launch your scripts**

### **Backup task**

Runs inside your Fedora‑NVIDIA Distrobox container:

```python
distrobox enter fedora42-nvidia -- uv run backup.py
```

This gives you:

- a reproducible environment
- isolated dependencies
- GPU‑aware Python
- clean logging
- no host contamination

### **Kleopatra warm‑up task**

Runs on the host:

```python
uv run kleopatra.py
```

This script:

- restarts `pcscd`
- forces YubiKey detection
- decrypts a test file
- clearsigns a test message
- runs your NVIDIA kernel‑arg checker
- ensures GPG + YubiKey are fully warmed up

All non‑interactive except for YubiKey touch/PIN.

---

## 🟦 **5. Your warm‑up script is fully automated**

`kleopatra.py` is now:

- non‑interactive
- deterministic
- safe to run remotely
- immune to shell quoting issues
- immune to missing environment variables
- touch‑only (if you choose to configure it that way)

It prepares your entire cryptographic environment so Kleopatra and GPG are ready the moment you sit down.

---

## 🟦 **6. Your backup script is containerized and reproducible**

`backup.py` runs inside your Distrobox container using `uv run`, giving you:

- reproducible Python environments
- isolated dependencies
- consistent behaviour across upgrades
- clean logging to `backup.log`

---

## 🟦 **7. The whole system is hands‑free**

From your Pixel, you can now:

### 🔹 Warm up your YubiKey

```
POST /kleopatra
```

### 🔹 Run a full encrypted backup

```
POST /backup
```

### 🔹 Do both in sequence

(just trigger both macros)

You can literally be in another room, say “run backup mode” (or tap a tile), and your ThinkPad:

- warms up the YubiKey
- decrypts/signs test messages
- runs your backup
- logs everything
- stays fully secure

---

# 🌟 **Why this workflow is attractive**

Because it hits all the engineering ideals you care about:

### ✔ **Reproducible**

Containerized Python, deterministic scripts, no hidden state.

### ✔ **Secure**

Tailscale, YubiKey, no public exposure, no cloud dependencies.

### ✔ **Cross‑platform**

Pixel → Tailscale → FastAPI → Distrobox → Host → YubiKey.

### ✔ **Non‑interactive**

Except for intentional YubiKey touch/PIN.

### ✔ **Modular**

Backup and warm‑up are separate, composable endpoints.

### ✔ **Elegant**

Every component does one job well.

---

# 🎉 It’s a _designed system_ — clean, modern, secure, and reproducible.

If you want, we can keep going:

- add `/status`
- add `/health`
- add `/mount`
- add `/upgrade`
- add journald logging
- add a web dashboard
- combine warm‑up + backup into a single endpoint

---

# 🧩 **FULL WORKFLOW SUMMARY — Remote Backup + YubiKey Warm‑Up System**

Below is the complete architecture, broken into clear phases:

- Host setup
- Container setup
- Backup script
- YubiKey warm‑up script
- FastAPI service
- Tailscale networking
- Pixel automation
- Final workflow

---

# 🟦 **1. Create the `backup_service` directory**

On your ThinkPad (host):

```
mkdir ~/backup_service
cd ~/backup_service
```

Inside this directory you placed:

- `backup.py` (runs inside Distrobox)
- `kleopatra.py` (runs on host)
- `main.py` (FastAPI server)
- `nvidia-check.sh`
- `test.gpg` (for decrypt warm‑up)
- `backup.log` (generated automatically)

This directory is the entire automation brain. 

Install fastapi in the `backup_service` directory:
`uv init --python 3.14
`uv add fastapi uvicorn[standard]

---

# 🟦 **2. Build and test the backup script locally**

Inside your Distrobox container (`fedora42-nvidia`):

- You wrote `backup.py`
- You tested it manually using:

```
uv run backup.py
```

This confirmed:

- restic works
- your storage mounts work
- your environment is reproducible
- the script logs correctly

This script is now called by FastAPI. Test it locally in the `backup_service` directory:

`uv run uvicorn main:app --host 127.0.0.1 --port 8000`

Restic supports creating a password inside a file:

`/var/home/fraser/.restic_password

hide the file from everyone except yourself:

`chmod 600 ~/.restic_password

we then updated our script to use the password in the file:

```
commands = [
    'sudo dnf upgrade -y',
    'restic -r /run/media/fraser/ows/restic-repo --password-file /var/home/fraser/.restic_password --verbose backup /var/home/fraser/Documents --exclude /var/home/fraser/Documents/NAS',
    'restic -r /run/media/fraser/ows/restic_backup_ml --password-file /var/home/fraser/.restic_password --verbose backup /var/home/fraser/machine_learning'
]
```

To confirm it is working locally:
`curl -X POST http://127.0.0.1:8000/backup

should produce:
`{"status":"backup_started"}

Tailscale needs to be configured to allow magicDNS (on the tailscale website) and tailscale serve on the computer:

`sudo tailscale serve --bg --https=443 127.0.0.1:8000

resulting in:

```
Available within your tailnet:

https://thinkpad-p16.tail9b163.ts.net/
|-- proxy http://127.0.0.1:8000

https://thinkpad-p16.tail9b163.ts.net/443
|-- proxy http://127.0.0.1:8000

Serve started and running in the background.
To disable the proxy, run: tailscale serve --https=443 off
```


from the pixel, we should install tailscale and in the browser go to:

`https://thinkpad-p16.tailXXXX.ts.net/443/docs

select the backup option and press it to run the fastapi command.

we should get a response on the computer:

```
uv run uvicorn main:app --host 0.0.0.0 --port 8000
INFO:     Started server process [430526]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     100.70.206.4:0 - "GET /openapi.json HTTP/1.1" 200 OK
INFO:     100.70.206.4:0 - "POST /backup HTTP/1.1" 200 OK
```


---

# 🟦 **3. Build and test the YubiKey warm‑up script locally**

On the host:

- You wrote `kleopatra.py`
- You fixed:
    - missing test file
    - missing shebang
    - missing execute permissions
    - subprocess input handling
    - pcscd timing
    - local path resolution

You tested it manually:

```
python3 kleopatra.py
```

This confirmed:

- `pcscd` restarts
- `gpg --card-status` works
- decrypt test works
- clearsign test works
- YubiKey PIN prompts behave correctly
- `nvidia-check.sh` runs
- the script is fully non‑interactive except for touch/PIN

This script is now callable remotely.

---

# 🟦 **4. Install and configure Tailscale**

On both Pixel and ThinkPad:

- Install Tailscale
- Log in
- Confirm both devices appear in your tailnet
- Confirm ThinkPad is reachable:

```
ping thinkpad-p16.tailXXXX.ts.net
```

This gives you a secure, private, encrypted network for remote automation.

---

# 🟦 **5. Build the FastAPI server**

Inside `main.py` you created:

- `/backup` endpoint
- `/kleopatra` endpoint

Each endpoint:

- returns immediately
- runs the real work in a BackgroundTask
- logs output
- isolates host vs container execution

This is the core automation API.

You tested it locally:

```
uvicorn main:app --host 0.0.0.0 --port 8000
```

Then:

```
curl -X POST https://thinkpad-p16.tailXXXX.ts.net/backup
curl -X POST https://thinkpad-p16.tailXXXX.ts.net/kleopatra
```

Both worked.

---

# 🟦 **6. Add the FastAPI server as a systemd service (optional but recommended)**

Run:

```
sudo nano /etc/systemd/system/backup_service.service
```

Paste the full service file into the editor:

```
[Unit]
Description=FastAPI Backup + YubiKey Warm-Up Service
After=network-online.target
Wants=network-online.target

[Service]
# Run as your user (important for GPG, YubiKey, restic password file, etc.)
User=###USERNAME###
WorkingDirectory=/var/home/###USERDIRECTORY###/backup_service

# Use uv to run uvicorn
ExecStart=/var/home/###USERDIRECTORY###/.cargo/bin/uv run uvicorn main:app --host 127.0.0.1 --port 8000

# Restart on failure
Restart=on-failure
RestartSec=5

# Environment variables (optional but recommended)
Environment=PYTHONUNBUFFERED=1

# Ensure systemd doesn't sandbox away your home directory
ProtectHome=no

[Install]
WantedBy=multi-user.target
```


Save with:

- `Ctrl + O`
- `Enter`
- `Ctrl + X`

This ensures:

- FastAPI starts on boot
- It survives reboots
- It restarts automatically

---
# 🟩 **After the file is in place, reload systemd**

```
sudo systemctl daemon-reload
```

Enable + start:

```
sudo systemctl enable --now backup_service
```

Check status:

```
systemctl status backup_service
```

You should see:

```
Active: active (running)
```

---

Enable:

```bash
sudo systemctl enable --now backup_service
```

---

# 🟦 **7. Pixel automation with MacroDroid**

On your Pixel:

### You created two macros:

### **Macro 1 — Trigger Backup**

Action:  
HTTP Request → POST →  
`https://thinkpad-p16.tailXXXX.ts.net/backup`

### **Macro 2 — Trigger Kleopatra Warm‑Up**

Action:  
HTTP Request → POST →  
`https://thinkpad-p16.tailXXXX.ts.net/kleopatra`

You bound each macro to:

- a Quick Settings tile
- or a home screen shortcut

This gives you instant, reliable triggers.

---

# 🟦 **8. Verified the full remote workflow**

From your Pixel:

### Tap “Backup”

- Pixel → Tailscale → FastAPI → Distrobox → backup.py
- restic runs
- logs saved
- endpoint returns immediately

### Tap “Kleopatra”

- Pixel → Tailscale → FastAPI → kleopatra.py
- pcscd restarts
- YubiKey warms up
- decrypt/sign tests run
- NVIDIA check runs
- Kleopatra is ready to use

Everything works remotely.

---

# 🟦 **9. Final architecture overview**

```
Pixel (MacroDroid)
      ↓ HTTPS POST (Tailscale)
ThinkPad FastAPI (main.py)
      ↓ BackgroundTasks
-----------------------------------------
| Host: kleopatra.py                    |
| - restart pcscd                       |
| - gpg card-status                     |
| - decrypt test.gpg                    |
| - clearsign test                      |
| - nvidia-check.sh                     |
-----------------------------------------
      ↓
-----------------------------------------
| Distrobox: backup.py                  |
| - uv run backup.py                    |
| - restic backup                       |
| - logs                                |
-----------------------------------------
```

Everything is:

- reproducible
- secure
- cross‑platform
- deterministic
- fully automated

---

# 🟦 **10. Reference to your scripts**

You already have these in your directory:

- `backup_service/main.py`
- `backup_service/backup.py`
- `backup_service/kleopatra.py`
- `backup_service/nvidia-check.sh`

No duplication needed — your directory _is_ the canonical reference.


---



# 📘 **Further details for the curious — Remote Backup + YubiKey Warm‑Up Automation**

A fully automated, Tailscale‑secured backup and cryptographic warm‑up system triggered remotely from an Android or iOS device.  This project combines:

- **FastAPI** (automation API)
- **Distrobox** (containerized backup environment)
- **restic** (encrypted backups)
- **YubiKey** (hardware‑backed crypto)
- **Tailscale** (secure remote access)
- **MacroDroid** (Pixel automation)
- **iOS shortcuts** (Siri and iOS automation)

The result is a reproducible, cross‑platform automation pipeline that can:

- Warm up your YubiKey (pcscd, gpg-agent, decrypt/sign tests)
- Run a full encrypted backup inside a container
- Trigger everything remotely from your Pixel or iOS device

---

# 🧩 **Project Structure**

```
backup_service/
├── main.py              # FastAPI server
├── backup.py            # Backup logic (runs inside Distrobox)
├── kleopatra.py         # YubiKey warm-up script (runs on host)
├── nvidia-check.sh      # Kernel argument checker
├── test.gpg             # Encrypted test file for warm-up
└── backup.log           # Generated automatically
```

This directory is the entire automation brain. You should also create a small test.gpg file encrypted with kleopatra for the script to decrypt.

---

# 1️⃣ **Prerequisites**

### Host (ThinkPad)

- Fedora Silverblue
- Python 3.14
- uv (Python environment manager)
- Distrobox
- restic
- YubiKey + GPG configured
- Tailscale

### Pixel (Android)

- MacroDroid
- Tailscale app

### iOS

- Tailscale app (make sure DNS is using Tailscale MagicDNS, not a 3rd party DNS)
---

# 2️⃣ **Create the `backup_service` Directory**

```bash
mkdir ~/backup_service
cd ~/backup_service
```

Initialize a Python environment:

```bash
uv init --python 3.14
uv add fastapi uvicorn[standard]
```

Place your scripts into this directory:

- `main.py`
- `backup.py`
- `kleopatra.py`
- `nvidia-check.sh`
- `test.gpg`

---

# 3️⃣ **Set Up the Distrobox Backup Environment**

Create your container, to enable entry, e.g.:

```bash
distrobox enter fedora42-nvidia
```

Inside the container:

- install Python
- install `uv`
- install restic (restic works better in a distrobox than Fedora Silverblue host)
- configure your backup environment

### Restic password file (host)

```
/var/home/fraser/.restic_password
```

Secure it:

```bash
chmod 600 ~/.restic_password
```

### Test backup script inside container

```bash
uv run backup.py
```

---

# 4️⃣ **Test FastAPI Locally**

From inside `backup_service` directory:

```bash
uv run uvicorn main:app --host 127.0.0.1 --port 8000
```

Test the backup endpoint:

```bash
curl -X POST http://127.0.0.1:8000/backup
```

Expected:

```json
{"status":"backup_started"}
```

---

# 5️⃣ **Configure Tailscale + Serve**

Enable MagicDNS in the Tailscale admin panel.

On the ThinkPad:

```bash
sudo tailscale serve --bg --https=443 127.0.0.1:8000
```

You should see:

```
Available within your tailnet:

https://thinkpad-p16.tailXXXX.ts.net/
|-- proxy http://127.0.0.1:8000
```

### Test from Pixel browser:

```
https://thinkpad-p16.tailXXXX.ts.net/443/docs
```

You should see the FastAPI docs UI.

---

# 6️⃣ **Build and Test the YubiKey Warm‑Up Script**

Run locally:

```bash
python3 kleopatra.py
```

This script:

- restarts `pcscd`
- forces YubiKey detection
- decrypts `test.gpg`
- clearsigns a test message
- runs `nvidia-check.sh`
- ensures GPG + YubiKey are fully warmed up

Once this works locally, it’s ready for remote triggering.

---

# 7️⃣ **FastAPI Endpoints**

`main.py` exposes:

### `/backup`

Runs `backup.py` inside Distrobox.

### `/kleopatra`

Runs `kleopatra.py` on the host.

Both run asynchronously using `BackgroundTasks`.

Test remotely:

```bash
curl -X POST https://thinkpad-p16.tailXXXX.ts.net/backup
curl -X POST https://thinkpad-p16.tailXXXX.ts.net/kleopatra
```

---

#  **Pixel Automation (MacroDroid)**

Create two macros:

### Macro 1 — Backup

HTTP Request → POST  
`https://thinkpad-p16.tailXXXX.ts.net/backup`

### Macro 2 — Kleopatra Warm‑Up

HTTP Request → POST  
`https://thinkpad-p16.tailXXXX.ts.net/kleopatra`

Bind each to:

- Quick Settings tile
- or Home Screen shortcut

This gives you instant remote control.

---

# 🧠 **Architecture Diagram**

```
Pixel (MacroDroid)
      ↓ HTTPS POST (Tailscale)
ThinkPad FastAPI (main.py)
      ↓ BackgroundTasks
-----------------------------------------
| Host: kleopatra.py                    |
| - restart pcscd                       |
| - gpg card-status                     |
| - decrypt test.gpg                    |
| - clearsign test                      |
| - nvidia-check.sh                     |
-----------------------------------------
      ↓
-----------------------------------------
| Distrobox: backup.py                  |
| - uv run backup.py                    |
| - restic backup                       |
| - logs                                |
-----------------------------------------
```

---

# 🛡️ **Security Notes**

- Tailscale provides end‑to‑end WireGuard encryption
- FastAPI is only exposed inside your tailnet (not allowing outside internet access—Tailscale does have a flag to enable this but it is turned off here)
- restic uses encrypted repositories
- YubiKey ensures hardware‑backed crypto
- No public ports are open
- No passwords are transmitted over the network

---

# 🛠️ **Troubleshooting**

### YubiKey not detected

```
systemctl restart pcscd
gpg --card-status
```

### Backup fails

- Check mount points
- Check restic repository path
- Check password file permissions

### Pixel cannot reach FastAPI

- Ensure Tailscale is connected
- Ensure MagicDNS is enabled
- Ensure `tailscale serve` is running

### FastAPI not responding

```
sudo systemctl status backup_service
```


---

# 📱 iOS Shortcuts Workflow (Triggering FastAPI Endpoints via Tailscale)

This section describes how to create iOS Shortcuts that remotely trigger the ThinkPad’s FastAPI endpoints (/backup and /kleopatra) over Tailscale. These shortcuts can be activated manually, from the Home Screen, or via Siri voice commands.

---

1. Ensure Tailscale is Working on iOS

Before creating shortcuts:

1. Install Tailscale from the App Store
2. Log in and connect
3. Enable:• Use Tailscale DNS
• MagicDNS (must be enabled in the Tailscale admin console)

4. Ensure Local Network Access is enabled (may be obsolete?):
Settings → Tailscale → Local Network → ON
5. If the hostname doesn’t resolve, toggle Tailscale off/on to refresh DNS


You must be able to open the appropriate device page (as described by Tailscale) in order to get the API endpoints for automation:

https://thinkpad-p16.tailXXXX.ts.net/443/docs


from Safari (or Firefox) on iOS.

---

2. Create a Shortcut to Trigger a FastAPI Endpoint

1. Open Shortcuts
2. Tap + to create a new shortcut
3. Tap Add Action
4. Choose Web → Get Contents of URL
5. Tap the blue “Input” token → change it to URL
6. Paste your endpoint URL:For backup:https://thinkpad-p16.tailXXXX.ts.net/backup
For YubiKey warm‑up:https://thinkpad-p16.tailXXXX.ts.net/kleopatra

7. Tap Show More
8. Set:• Method: POST
• Request Body: JSON
• Body: {}
• Headers:• Key: Content-Type
• Value: application/json

Make sure to hardcode the URL (iOS likes to default to clipboard or shortcut input but that slows the workflow down). Changing “URL” to the hardcoded URL was not immediately obvious.
---

3. Rename the Shortcut (Important for Siri)

iOS defaults the shortcut name to the first action (“Get Contents of URL”), which Siri will try to use literally.

To rename:

1. Tap the ••• (three dots) on the shortcut (again, not the most obvious location; in iOS 26.1 it was on the top left as a ^ pointing down)
2. Tap the name at the top
3. Enter a clear, Siri‑friendly name such as:
• Initiate Backup
• Initiate Security Key

4. Tap Done


Siri will now use this name.

---

4. Add to Home Screen (Optional)

1. Open the shortcut
2. Tap the share icon
3. Choose Add to Home Screen
4. Select an icon and name
5. Tap Add


This creates a one‑tap trigger for your ThinkPad automation.

---

5. Enable Siri Activation (Automatic)

Once renamed, Siri automatically recognizes the shortcut.

You can now say:

• “Hey Siri, initiate backup”
• “Hey Siri, initiate security key”


Siri will run the shortcut exactly as defined—no interpretation layer, no rewriting. You have to be very careful with naming these shortcuts (Google on the Pixel always wants to explain rather than run the shortcut. Siri is less aggressive but still tends to want to produce search results. No assistant can hear “YubiKey” properly, so don’t use that word!)

---

6. Result

You now have:

• A fully functional iOS Shortcut that sends a POST request over Tailscale
• A Home Screen button for instant triggering
• A Siri phrase that reliably activates your ThinkPad automation
• Cross‑platform parity with your Android MacroDroid setup


This completes the iOS automation portion of the workflow.
