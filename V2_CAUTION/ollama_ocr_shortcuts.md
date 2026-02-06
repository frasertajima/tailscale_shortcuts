# Ollama OCR Shortcuts

Three new Tailscale/FastAPI shortcuts for running OCR from the iPad using ollama's `glm-ocr` model. All commands execute inside the `fedora42-nvidia` distrobox to leverage GPU acceleration. You will have to modify the distrobox name and user directory for your own use.

## Shortcuts

| Shortcut | Method | Description |
|---|---|---|
| `/ollama_on` | POST | Starts the ollama server |
| `/ollama_off` | POST | Stops the ollama server |
| `/ocr_images` | POST | OCRs all images in the `orc_this` folder |

## Workflow

1. Copy screenshots/images to `/var/home/[user]/Pictures/orc_this`
2. Hit `/ocr_images` -- it auto-starts ollama if it isn't already running
3. Each image gets a `.md` file with the extracted text alongside it
4. Hit `/ollama_off` when done to free GPU resources

## Details

- **OCR folder**: `/var/home/[user]/Pictures/orc_this`
- **Supported formats**: png, jpg, jpeg, bmp, tiff, webp
- **Model**: `glm-ocr` (via ollama)
- **Output**: `.md` files saved next to each image (e.g. `screenshot.png` produces `screenshot.md`)
- **Logs**: All activity logged to `/var/home/fraser/backup_service/ollama.log`

## Scripts

- `ollama_on.sh` -- starts `ollama serve` in background, verifies startup
- `ollama_off.sh` -- graceful shutdown with force-kill fallback
- `ocr_images.sh` -- checks/starts ollama, iterates images, strips ANSI noise, saves clean markdown
