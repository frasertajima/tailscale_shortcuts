# Wake‑on‑LAN via Synology NAS + FastAPI + Tailscale Serve

A reproducible, tailnet‑native automation pipeline

This document describes how to expose a Wake‑on‑LAN (WOL) endpoint from a Synology NAS using FastAPI (Python 3.14) and Tailscale Serve. The endpoint can be triggered from iOS Shortcuts to wake a remote Linux workstation (e.g., Fedora Silverblue).

The design is fully modular, reproducible, and requires no port‑forwarding or public exposure. No iOS or Android apps are required.

---

## 1. Prerequisites

Synology NAS

• Python 3.14 installed via Synology Package Centre (Community)
• Tailscale installed and logged in the NAS and computer
• SSH access enabled


Target machine (e.g., Fedora Silverblue)

• Ethernet connection
• WOL enabled in BIOS
• MAC address available


Client

• iOS device with Shortcuts app
• Tailscale installed


---

## 2. Configure Python 3.14 on Synology

Synology installs the community Python 3.14 package in a versioned directory that is not on $PATH. To run `pip`, install the community Python 3.14 package from the Synology app store and use `python3.14` not `python3` and `pip3.14` not `pip3`. Synology does not like the Python version to be changed so we will only use `python3.14` to gain access to `pip3.14` for installing the utilities below.

## 3. Install FastAPI, Uvicorn, and wakeonlan on the NAS

`pip3.14 install fastapi uvicorn wakeonlan`

Confirm to make sure installation worked:

`uvicorn —version` or `wakeonlan —version`

---

## 4. Create the FastAPI WOL service

Create:

`/volume1/homes/<user>/wol_api.py`


Contents:

```
from fastapi import FastAPI
from wakeonlan import send_magic_packet

app = FastAPI()

MAC = "AA:BB:CC:DD:EE:FF"   # Replace with your machine's MAC

@app.post("/wol")
def wol():
    send_magic_packet(MAC)
    return {"status": "sent"}

# Accept both /wol and /wol/ to avoid redirect loops from iOS Shortcuts
@app.post("/wol/")
def wol_slash():
    return wol()
```

---

## 5. Run FastAPI on the NAS

`uvicorn /volume1/homes/<user>/wol_api:app --host 0.0.0.0 --port 8000`

Test locally (open another ssh session to the NAS):

`curl -X POST http://127.0.0.1:8000/wol`


Expected:

`{"status": "sent"}`


---

## 6. Expose the endpoint using Tailscale Serve on the NAS

Reset old Serve config (optional—CAUTION DELETES EXISTING ENTRIES; this should not be necessary on a new Synology NAS setup):

`sudo tailscale serve reset`


Create the Serve rule:

`sudo tailscale serve --bg --set-path /wol http://127.0.0.1:8000/`


Verify:

`tailscale serve status`


Expected:

`/wol proxy http://127.0.0.1:8000/wol`


MagicDNS URL

Tailscale prints something like:

```Available within your tailnet:
https://frasertajima.<magicdns>.ts.net/wol
```

Use exactly that URL in your Shortcut.

---

## 7. Create the iOS Shortcut

1. Add Get Contents of URL
2. URL:


`https://frasertajima.<magicdns>.ts.net/wol`


1. Method: POST
2. Request Body: None
3. Show When Run: Off


Running the Shortcut should return:

`{"status": "sent"}`


This confirms the NAS received the request and sent the magic packet.

---

## 8. Fixing Wake‑on‑LAN on Fedora Silverblue

Silverblue resets NIC state after sleep/wake.
Even if ethtool shows Wake-on: `g`, the NIC may not actually be listening.

### 8.1 Persistent WOL after boot


```
sudo nmcli connection modify enp5s0 802-3-ethernet.wake-on-lan magic
sudo systemctl restart NetworkManager
```

### 8.2 Persistent WOL after wake (Silverblue‑compatible)


Create a NetworkManager dispatcher script:

`sudo nano /etc/NetworkManager/dispatcher.d/99-wol`


Add:
```
#!/bin/bash
if [ "$2" = "up" ]; then
    /usr/sbin/ethtool -s enp5s0 wol g
fi
```

Make executable:

`sudo chmod +x /etc/NetworkManager/dispatcher.d/99-wol`


This re‑applies WOL every time the system wakes.

---

## 9. Architecture Overview
```
iOS Shortcut (POST /wol)
        ↓
Tailscale MagicDNS
        ↓
Tailscale Serve on Synology NAS
        ↓
FastAPI
        ↓
wakeonlan → Magic Packet
        ↓
Fedora Silverblue Desktop Wakes
```

---

## 10. Troubleshooting

Shortcut returns 307 Temporary Redirect

• You are hitting /wol/ instead of /wol
• Fix: FastAPI route for /wol/ (included above)


Shortcut returns 200 OK but machine does not wake

• NIC lost WOL after sleep → install dispatcher script
• Wrong MAC address (Wi‑Fi instead of Ethernet)
• NIC LED off → no standby power
• BIOS settings incorrect (ErP enabled, S5 WOL disabled)


NAS cannot find Python 3.14

• need to use `python3.14` not `python3` in Synology; also, `pip3.14` not `pip3`.


---

## 11. Conclusion

This setup provides:

• A secure, tailnet‑only WOL endpoint
• A FastAPI microservice running on the NAS
• A clean Tailscale Serve integration
• A Siri‑triggerable automation pipeline
• A Silverblue‑compatible WOL persistence fix


Once configured, waking your workstation becomes a single voice command.
