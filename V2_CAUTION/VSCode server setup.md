# 🧭 Step 1 — Get your Tailscale IP

Inside the Fedora Silverblue **host** (not the distrobox container):

```bash
tailscale ip -4
```

You’ll get something like:

```
100.x.y.z
```

This is the IP behind your MagicDNS name:

```
##machine_name##.tail####.ts.net
```

We will bind VS Code Server **only** to this IP. The original instructions were for `code serve-web` but installing `code-server` from Microsoft and launching that may survive a reboot better:

`code-server` can be installed inside the distrobox container with:
```bash
conda install conda-forge::code-server
```
or:
```bash
curl -fsSL https://code-server.dev/install.sh | sh
```


```bash
# assuming vscode is already installed in a distrobox container run to check it works manually (with your IP):
# code serve-web --host 100.*.*.* --port 8010 --without-connection-token
code-server --bind-addr 100.*.*.*:8010 --auth none

```

---

# 🧭 Step 2 — Connect from iPad or computer 

Just open in Safari using your tailscale MagicID details:

```
http://##machine_name##.tail###.ts.net:8010/
```

---

# Install Jupiter labs and link to one or more conda environments to replicate the VSCode kernel options (inside the same distrobox container):

```bash
# install jupyter labs
uv pip install jupyterlab

# install support for conda env py314 for example (use your own conda env):
conda activate py314
uv pip install ipykernel
python -m ipykernel install --user --name py314 --display-name "Python 3.14 (py314)"

# run jupyter labs
jupyter lab --no-browser --ip=100.*.*.* --port=9999 --ServerApp.token='' --ServerApp.password=''
```


- - -

# ￼Manual command line to check it works for automation:

```bash
# run jupyter labs and vscode serve in distrobox container
jupyter lab --no-browser --ip=100.*.*.* --port=9999 --ServerApp.token='' --ServerApp.password='' &
# code serve-web --host 100.*.*.* --port 8010 --without-connection-token
code-server --bind-addr 100.*.*.*:8010 --auth none

```

---
# Create shortcut scripts for tailscale automation

/var/home/fraser/backup_service/vscode_on.sh (use updated script in github directory):

set permissions on vscode_on.sh:
```
chmod +x /var/home/fraser/backup_service/vscode_on.sh
```

/var/home/fraser/backup_service/vscode_off.sh:
```
#!/usr/bin/env bash

# Kill JupyterLab
pkill -f "jupyter"


echo "Shutting down VS Code Server..."
# Kill code-server directly
pkill -f "code-server"

# Give it a moment to exit
sleep 1

# Double-check: kill any leftover node instance bound to your port
# (only if code-server didn't exit cleanly)
PIDS=$(ss -tulpn | grep 8010 | awk '{print $NF}' | sed 's/users:(("//;s/",.*//')
if [ -n "$PIDS" ]; then
    echo "Force-killing leftover node processes on port 8010..."
    for PID in $PIDS; do
        kill -9 "$PID"
    done
fi

echo "VS Code Server stopped."

```
set permissions on vscode_off.sh:
```
chmod +x /var/home/fraser/backup_service/vscode_off.sh
```

- copy the updated `main.py` file from the github V2 directory (it should contain /ostree_upgrade, /vscode_on, /vscode_off along with the rest)
- create your iPad and Siri shortcuts: "initiate code on" and "initiate code off" works ("initiate VSCode on" causes Siri to do a web search)

## Tailscale serve commands:

This removes all existing settings for tailscale serve and provides the working state (review before deleting):

```bash
sudo tailscale serve reset
sudo tailscale serve --bg --set-path /jupyter http://localhost:9999/jupyter/
sudo tailscale serve --bg --set-path /code http://localhost:8010
```

The result should be:

```bash
|-- /code    proxy http://localhost:8010
|-- /jupyter proxy http://localhost:9999/jupyter/
```

This ensures:

- JupyterLab loads instantly
- VS Code Server now loads Jupyter notebooks instantly (unlike with http)

---

## 🎯Working URLs

- **VS Code Server**
    `https://<magicdns>/code/`

- **JupyterLab**
    `https://<magicdns>/jupyter/`


Both load instantly on iPad Safari with no insecure warnings.

- - -
If your FastAPI ever fails to update on the iPad, check for multiple instances running by:

`ps aux | grep uvicorn`

I found two of them so I had to delete them:

`pkill -f "uvicorn main:app"`

confirm they are gone:

`ps aux | grep uvicorn`

restart:

`uv run uvicorn main:app --host 127.0.0.1 --port 8000`

then the FastAPI web-page on the iPad was updated with `/vscode_on` and `/vscode_off`. You can also check FastAPI on the host machine with `http://127.0.0.1:8000/docs`.

---
⭐ Why code-server works (and why the old method of code serve-web broke)

Fedora’s code wrapper:

    - used to support serve-web
    - now silently redirects to code‑tunnel
    - which is not the VS Code web server
    - nd is incompatible with Safari/Firefox
    - and breaks your automation

But code-server is:

    - stable
    - headless
    - browser‑native
    - not tied to Electron
    - not tied to GNOME
    - not tied to code‑tunnel
