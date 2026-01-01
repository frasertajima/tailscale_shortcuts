#!/usr/bin/env bash
set -euo pipefail

# Desired kernel arguments
declare -a REQUIRED_KARGS=(
  "rd.driver.blacklist=nouveau"
  "modprobe.blacklist=nouveau"
  "nvidia-drm.modeset=1"
)

# Check current kernel arguments
CURRENT_KARGS=$(cat /proc/cmdline)

# Function to check if all required kargs are present
missing_kargs=()
for arg in "${REQUIRED_KARGS[@]}"; do
  if ! grep -qw "$arg" <<< "$CURRENT_KARGS"; then
    missing_kargs+=("$arg")
  fi
done

if [ "${#missing_kargs[@]}" -eq 0 ]; then
  echo "✅ All required Nvidia kernel arguments are already present. No action needed."
  exit 0
fi

echo "⚠️ Missing kernel arguments detected:"
for arg in "${missing_kargs[@]}"; do
  echo "  - $arg"
done

echo "📦 Applying missing kernel arguments via rpm-ostree..."
rpm-ostree kargs --append="${missing_kargs[*]}"

echo "🔁 Kernel arguments updated. Please reboot to apply changes:"
echo "    sudo systemctl reboot"

