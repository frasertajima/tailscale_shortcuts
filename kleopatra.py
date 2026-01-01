import subprocess
import time
from pathlib import Path

STATUS_FILE = Path("/var/home/fraser/backup_service/kleopatra_status.txt")
BASE_DIR = Path("/var/home/fraser/backup_service")

def run(cmd, **kwargs):
    print(f"Running: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True, **kwargs)
        print("✓ Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed with exit code {e.returncode}")
        return False

def main():
    ok = True

    # 0. Reset all GnuPG daemons (scdaemon, gpg-agent, etc.)
    ok &= run(["gpgconf", "--kill", "all"])

    # 1. Restart pcscd (polkit rule allows this without sudo)
    ok &= run(["systemctl", "restart", "pcscd"])

    # 2. Give pcscd a moment to rebind to the YubiKey
    time.sleep(1)

    # 3. Force YubiKey detection
    ok &= run(["gpg", "--card-status"])

    # 4. Optional signing test
    ok &= run([
        "gpg", "--batch", "--yes",
        "--clearsign"
    ], input=b"test")

    # 5. NVIDIA check (optional)
    nvidia_script = BASE_DIR / "nvidia-check.sh"
    if nvidia_script.exists():
        ok &= run([str(nvidia_script)])
    else:
        print("Skipping NVIDIA check (script not found)")

    print("Kleopatra warm-up complete. YubiKey should now be ready. Check kleopatra.log.")

if __name__ == "__main__":
    main()
