# NVIDIA Driver Setup on Fedora rpm-ostree (Silverblue/Kinoite)

## Problem

On Fedora rpm-ostree systems with Secure Boot enabled, the NVIDIA driver requires:

1. A MOK (Machine Owner Key) to be enrolled for the signed kernel modules to load.
2. The `nouveau` open-source driver to be blacklisted, otherwise it claims the GPU before the NVIDIA driver can.

Without these, `nvidia-smi` fails and the NVIDIA GPU is unavailable after each boot (or after an rpm-ostree upgrade).

### Root cause: MOK key name mismatch

The RPM Fusion NVIDIA setup generates keys named `nvidia_mok.der` / `nvidia_mok.priv` under `/etc/pki/akmods/`, but `kmodtool` looks for the fixed names `public_key.der` / `private_key.priv` in that same directory. With no symlinks bridging the two, the kmod either failed to sign or was signed with a fallback key.

Separately, `nvidia_mok.der` was never enrolled in the UEFI MOK database, so even a correctly signed kmod would have been rejected by Secure Boot at load time.

The ThinkPad also has its own platform MOK key enrolled, which can make it appear as though MOK setup is complete when the NVIDIA-specific key is still missing.

**In short:** `kmodtool` couldn't find the right key by name, and the correct cert was never enrolled in the MOK database.

## Fix

### 1. Symlink the nvidia MOK key to the expected names and enroll it

```bash
sudo ln -sf /etc/pki/akmods/certs/nvidia_mok.der /etc/pki/akmods/certs/public_key.der
sudo ln -sf /etc/pki/akmods/private/nvidia_mok.priv /etc/pki/akmods/private/private_key.priv
sudo mokutil --import /etc/pki/akmods/certs/nvidia_mok.der
```

Then reboot and complete the MOK enrollment in the UEFI MOK manager when prompted.

### 2. Set persistent kernel arguments

```bash
rpm-ostree kargs \
  --append=initcall_blacklist=simpledrm_platform_driver_init \
  --append=modprobe.blacklist=nouveau \
  --append=rd.driver.blacklist=nouveau \
  --append=nvidia-drm.modeset=1
```

Because kargs are stored in the ostree boot configuration, these persist across rpm-ostree upgrades automatically — no need to re-apply after each upgrade.

### 3. Verify

After rebooting:

```bash
nvidia-smi
```

## Environment

- Machine: ThinkPad P16
- GPU: NVIDIA RTX A1000 Laptop GPU
- Driver: 595.58.03
- CUDA: 13.2
- OS: Fedora rpm-ostree (Silverblue/Kinoite)
