# VanLAN Router 🚐💨

A powerful, web-managed motorhome/van LAN router built for the Raspberry Pi.

VanLAN allows you to share a single internet connection (Campsite Wi-Fi, iPhone USB Tethering, or Ethernet) across all your devices via a private "Van LAN" Wi-Fi hotspot.

## Core Features

*   **🌐 Unified Gateway:** Connect all your devices to one local hotspot.
*   **📱 Multi-Source Support:** Seamlessly switch between USB Tethering (iPhone), external Wi-Fi (Campsite), and Ethernet.
*   **📡 Automatic Failover:** Intelligently prioritizes connections (Tethering > Wi-Fi > Ethernet).
*   **🔒 Web Dashboard:** Mobile-friendly interface to scan for networks, manage passwords, and monitor connected clients.
*   **⏱️ DHCP Management:** Fully configurable lease times and client tracking with hostname resolution.
*   **🛡️ Secure & Reliable:** Built on NetworkManager and Debian Trixie for enterprise-grade networking stability.

## Quick Install

To set up the official VanLAN Apt repository and install the router software on your Raspberry Pi OS (Trixie), run:

```bash
curl -fsSL https://raw.githubusercontent.com/andyphelps/vanlan/master/scripts/install.sh | sudo bash
sudo apt install vanlan-router
```

## Post-Installation

Once installed, connect your device to the **"VanLAN"** Wi-Fi network (default password: `password`) and navigate to:

*   **URL:** [http://router.local](http://router.local) or [http://10.42.0.1](http://10.42.0.1)
*   **Default Admin Password:** `admin`

You will be prompted to change these default credentials on your first visit.

## How it Works

VanLAN leverages standard Linux networking tools (`nmcli`, `dnsmasq`, `avahi`) to create a robust routing environment. It automatically handles IP forwarding and NAT (Masquerading), ensuring that your "Van LAN" remains isolated and secure while sharing the upstream internet connection.

---
*Created with ❤️ for the vanlife community.*
