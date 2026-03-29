# NVIDIA Driver Setup on Fedora rpm-ostree (Silverblue/Kinoite)

## Problem

On Fedora rpm-ostree systems with Secure Boot enabled, the NVIDIA driver requires:

1. A MOK (Machine Owner Key) to be enrolled for the signed kernel modules to load.
2. The `nouveau` open-source driver to be blacklisted, otherwise it claims the GPU before the NVIDIA driver can.

Without these, `nvidia-smi` fails and the NVIDIA GPU is unavailable after each boot (or after an rpm-ostree upgrade).

### Root cause: MOK key mismatch

The Fedora NVIDIA/akmods setup can end up with two separate MOK keys:

- `/etc/pki/akmods/` — the default signing key path used by `kmodtool`
- `/etc/pki/akmods-keys/` — the path used when `akmods-keys` is installed, which provides `/etc/rpm/macros.kmodtool` to override the default

If `akmods-keys` is not installed (or its macro file is absent), `kmodtool` falls back to `/etc/pki/akmods`. The NVIDIA kmod then gets signed with those keys — but only the *other* key (from `/etc/pki/akmods-keys/`) may have been enrolled in the UEFI MOK manager. Secure Boot rejects the module at load time, and the proprietary driver silently fails to load.

The ThinkPad itself also has its own platform MOK key, which can further obscure which key is actually enrolled and active.

**In short:** the kmod was signed with an unenrolled key because `kmodtool` was not pointing at the enrolled key's path.

## Fix

### 1. Install `akmods-keys` and enroll the correct MOK key

Install `akmods-keys` to ensure `/etc/rpm/macros.kmodtool` exists and points `kmodtool` at `/etc/pki/akmods-keys/` as the signing key path. Then enroll the key from that path in the UEFI MOK manager and reboot to confirm enrollment.

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
