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

We will bind VS Code Server **only** to this IP.

```bash
# assuming vscode is already installed in a distrobox container run to check it works manually (with your IP):
code serve-web --host 100.*.*.* --port 8010 --without-connection-token
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
code serve-web --host 100.*.*.* --port 8010 --without-connection-token
```

---
# Create shortcut scripts for tailscale automation

/var/home/fraser/backup_service/vscode_on.sh (put in your own IP address and user home folder):
```
#!/usr/bin/env bash

# Start JupyterLab
jupyter lab \
  --no-browser \
  --ip=100.*.*.* \
  --port=9999 \
  --ServerApp.token='' \
  --ServerApp.password='' \
  --notebook-dir=/home/##user## &

# Start VS Code Server (Microsoft version)
code serve-web \
  --host 100.*.*.* \
  --port 8010 \
  --without-connection-token &

```
set permissions on vscode_on.sh:
```
chmod +x /var/home/fraser/backup_service/vscode_on.sh
```

/var/home/fraser/backup_service/vscode_off.sh:
```
#!/usr/bin/env bash

# Kill JupyterLab
pkill -f "jupyter-lab"
pkill -f "jupyter lab"

# Kill VS Code Server
pkill -f "code serve-web"

```
set permissions on vscode_off.sh:
```
chmod +x /var/home/fraser/backup_service/vscode_off.sh
```

- copy the updated `main.py` file from the github V2 directory (it should contain /ostree_upgrade, /vscode_on, /vscode_off along with the rest)
- create your iPad and Siri shortcuts: "initiate code on" and "initiate code off" works ("initiate VSCode on" causes Siri to do a web search)
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


