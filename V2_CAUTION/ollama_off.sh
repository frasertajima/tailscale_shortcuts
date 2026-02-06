#!/bin/bash
# Stop ollama server inside the distrobox
# This script runs INSIDE fedora42-nvidia via distrobox enter

echo "[ollama_off] Stopping ollama server..."

pkill -f "ollama serve" 2>/dev/null

sleep 1

# Verify it stopped
if pgrep -f "ollama serve" >/dev/null 2>&1; then
    echo "[ollama_off] WARNING: ollama still running, force killing..."
    pkill -9 -f "ollama serve" 2>/dev/null
    sleep 1
fi

if pgrep -f "ollama serve" >/dev/null 2>&1; then
    echo "[ollama_off] ERROR: Failed to stop ollama server"
else
    echo "[ollama_off] Ollama server stopped."
fi
