import os
import subprocess
import sys

repo1 = "/run/media/fraser/ows/restic-repo"
repo2 = "/run/media/fraser/ows/restic_backup_ml"

if not os.path.isdir(repo1) or not os.path.isdir(repo2):
    print("Backup drive not mounted. Aborting.")
    sys.exit(1)

commands = [
    "sudo dnf upgrade -y",
    "restic -r /run/media/fraser/ows/restic-repo --password-file ~/.restic_password --verbose backup ~/Documents --exclude ~/Documents/NAS",
    "restic -r /run/media/fraser/ows/restic_backup_ml --password-file ~/.restic_password --verbose backup ~/machine_learning"
]

for cmd in commands:
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"Command failed: {cmd}")
        break
