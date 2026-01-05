
# HTTPS Access to VS Code Server + JupyterLab via Tailscale Serve (not caddy)

This documents the final working configuration for exposing **VS Code Server** and **JupyterLab** over **HTTPS** using **Tailscale Serve**, with correct path handling, correct base URLs, and full compatibility with iPad Safari and Firefox. This setup for Fedora Silverblue is very different from tailscale's own documentation (https://tailscale.com/kb/1166/vscode-ipad) which uses `caddy` (a nightmare in Fedora Silverblue). What I don't understand is why Tailscale did not point out that *tailscale serve provides https*!



---

## Tailscale serve commands:

This removes all existing settings for tailscale serve and provides the working state (review before deleting):

```bash
sudo tailscale serve reset
sudo tailscale serve --bg --set-path /jupyter http://localhost:9999/jupyter/
sudo tailscale serve --bg --set-path /code http://localhost:8010
```

The result should be:

```bash
|-- /code    proxy http://localhost:8010
|-- /jupyter proxy http://localhost:9999/jupyter/
```

This ensures:

- JupyterLab loads instantly
- VS Code Server now loads Jupyter notebooks instantly (unlike with http)

---

## 🎯Working URLs

- **VS Code Server**
    `https://<magicdns>/code/`

- **JupyterLab**
    `https://<magicdns>/jupyter/`


Both load instantly on iPad Safari with no insecure warnings.

---

## 🎯 1. Root Cause of All Issues

There were **two independent problems**:

### **A. JupyterLab was running with a base URL (`/jupyter/`)**

But Tailscale Serve was stripping the prefix and forwarding incorrectly:

```
/jupyter/lab → forwarded as /lab
```

Jupyter expected:

```
/jupyter/lab
```

This mismatch caused:

- white screen
- Jupyter 404 page
- missing static assets
- notebooks failing to load in VS Code

### **B. VS Code Server + Jupyter notebooks require HTTPS**

Safari on iPad blocks insecure WebSocket and service worker traffic. Once everything was behind Tailscale’s HTTPS proxy, VS Code could finally open `.ipynb` files.

---

## 🎯 2. The Correct JupyterLab Startup

Jupyter must be started with a base URL:

```bash
--ServerApp.base_url=/jupyter/
```

This makes all assets live under:

```
/jupyter/lab
/jupyter/static
/jupyter/api
```

And the API endpoint becomes:

```
/jupyter/api/status
```
---

## 🎯 3. The Correct Tailscale Serve Rules

The key fix was to **preserve the prefix** when forwarding.

### ❌ Incorrect (prefix stripped)

```
/jupyter → http://localhost:9999
```

### ✔ Correct (prefix preserved)

```
/jupyter → http://localhost:9999/jupyter/
```


## 🎯 4. Why the VS Code icon disappeared

Safari only shows a site icon when:

- the site provides a favicon at `/favicon.ico`, or
- the PWA manifest includes an icon

VS Code Server’s icon was previously loaded over HTTP. Once you switched to HTTPS, Safari no longer reused the insecure icon.


---

# 🎉 Final Result

- VS Code Server loads fast
- JupyterLab loads fast
- Notebooks open inside VS Code
- Everything is HTTPS
- Everything is iPad‑friendly
- Everything is cleanly namespaced
- Everything is reproducible
