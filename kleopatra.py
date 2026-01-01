import subprocess

def run(cmd, **kwargs):
    print(f"Running: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True, **kwargs)
        print("✓ Success")
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed with exit code {e.returncode}")

def main():
    # Restart smartcard service
    run(["systemctl", "restart", "pcscd"])

    # Force YubiKey detection
    run(["gpg", "--card-status"])

    # Test decryption (non-interactive except for touch)
    run([
        "gpg", "--batch", "--yes",
        "--output", "test.pdf",
        "--decrypt", "test.gpg"
    ])

    # Test signing (non-interactive except for touch)
    run([
        "gpg", "--batch", "--yes",
        "--clearsign"
    ], input=b"test")

    # Run your NVIDIA check script (must not require sudo)
    run(["./nvidia-check.sh"])


    print("Kleopatra warm-up complete. YubiKey should now be ready.")

if __name__ == "__main__":
    main()
