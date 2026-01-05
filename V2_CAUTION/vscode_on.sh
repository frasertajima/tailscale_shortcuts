#!/usr/bin/env bash
set -euo pipefail

JUPYTER_PORT=9999
CODE_PORT=8010

start_jupyter() {
  echo "[vscode_on] Starting JupyterLab..."

  # Kill stale instances
  pkill -f "jupyter-lab" 2>/dev/null || true

    jupyter lab \
      --no-browser \
      --ip=127.0.0.1 \
      --port=9999 \
      --ServerApp.allow_remote_access=True \
      --ServerApp.allow_origin='*' \
      --ServerApp.trust_xheaders=True \
      --ServerApp.token='' \
      --ServerApp.password='' \
      --ServerApp.base_url=/jupyter/ \
      --notebook-dir=/home/fraser \
      >/tmp/jupyter.log 2>&1 &
}

start_code_server() {
  echo "[vscode_on] Starting VS Code Server..."

  # Kill stale instances
  pkill -f "code-server" 2>/dev/null || true

  code-server \
    --bind-addr 127.0.0.1:${CODE_PORT} \
    --auth none \
    >/tmp/code-server.log 2>&1 &
}

echo "[vscode_on] Initializing remote dev environment..."
start_jupyter
start_code_server
echo "[vscode_on] Environment ready."
