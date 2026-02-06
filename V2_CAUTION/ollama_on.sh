#!/bin/bash
# Start ollama server inside the distrobox
# This script runs INSIDE fedora42-nvidia via distrobox enter

echo "[ollama_on] Starting ollama server..."

# Kill any existing ollama serve process
pkill -f "ollama serve" 2>/dev/null || true
sleep 1

# Start ollama serve in background
nohup ollama serve >/tmp/ollama_serve.log 2>&1 &

# Wait briefly and verify it started
sleep 2
if pgrep -f "ollama serve" >/dev/null 2>&1; then
    echo "[ollama_on] Ollama server started successfully (PID: $(pgrep -f 'ollama serve'))"
else
    echo "[ollama_on] ERROR: Ollama server failed to start. Check /tmp/ollama_serve.log"
    cat /tmp/ollama_serve.log 2>/dev/null
fi
