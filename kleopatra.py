import subprocess
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

    # 1. Force YubiKey detection
    ok &= run(["gpg", "--card-status"])

    # 2. Optional signing test
    ok &= run([
        "gpg", "--batch", "--yes",
        "--clearsign"
    ], input=b"test")

    # 3. NVIDIA check (optional)
    nvidia_script = BASE_DIR / "nvidia-check.sh"
    if nvidia_script.exists():
        ok &= run([str(nvidia_script)])
    else:
        print("Skipping NVIDIA check (script not found)")

    print("Kleopatra warm-up complete. YubiKey should now be ready. Check kleopatra.log.")

if __name__ == "__main__":
    main()
