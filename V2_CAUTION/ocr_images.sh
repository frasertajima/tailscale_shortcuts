#!/bin/bash
# OCR all images in /var/home/fraser/Pictures/orc_this using ollama glm-ocr
# This script runs INSIDE fedora42-nvidia via distrobox enter
# Outputs .md files alongside each image

OCR_DIR="/var/home/fraser/Pictures/orc_this"
MODEL="glm-ocr"

# Strip ANSI escape sequences from ollama output
strip_ansi() {
    sed 's/\x1b\[[0-9;]*[a-zA-Z]//g; s/\x1b\[[?][0-9]*[a-zA-Z]//g; s/\x1b\[K//g; s/\r//g' | tr -d '\r' | sed '/^[[:space:]]*$/d'
}

echo "[ocr_images] Starting OCR on images in $OCR_DIR"

cd "$OCR_DIR" || { echo "[ocr_images] ERROR: Cannot cd to $OCR_DIR"; exit 1; }

# Check ollama is running, start it if not
if ! ollama list >/dev/null 2>&1; then
    echo "[ocr_images] Ollama not running, starting it..."
    /var/home/fraser/backup_service/ollama_on.sh
    # Give it a few extra seconds to fully initialize
    sleep 3
    if ! ollama list >/dev/null 2>&1; then
        echo "[ocr_images] ERROR: Failed to start ollama server."
        exit 1
    fi
    echo "[ocr_images] Ollama server is ready."
fi

count=0
errors=0

for img in *.png *.jpg *.jpeg *.bmp *.tiff *.webp; do
    # Skip if glob didn't match (literal pattern remains)
    [ -f "$img" ] || continue

    md_file="${img%.*}.md"

    echo "[ocr_images] Processing: $img"
    result=$(TERM=dumb ollama run "$MODEL" "Text Recognition: ./$img" 2>/dev/null | strip_ansi)

    if [ $? -eq 0 ] && [ -n "$result" ]; then
        echo "$result" > "$md_file"
        echo "[ocr_images] Output saved to: $md_file"
        count=$((count + 1))
    else
        echo "[ocr_images] ERROR processing $img"
        errors=$((errors + 1))
    fi
done

echo "[ocr_images] Done. Processed: $count, Errors: $errors"
