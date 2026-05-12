# Refactoring Plan: NetworkManager Integration for Van LAN

## Overview
The goal is to simplify the routing logic by fully utilizing NetworkManager's built-in capabilities on Debian Trixie (Raspberry Pi OS), removing redundant manual scripts, and adding robust Captive Portal detection.

## 1. Eliminate Manual Routing (Rely on NM `shared` method)
**Current Issue:** `network_controller.py` manually runs `sysctl` and `iptables`/`nftables` commands in `setup_routing()`. However, `nmcli device wifi hotspot` creates a connection profile that implicitly uses `ipv4.method shared`. This built-in NetworkManager method automatically:
- Enables IP forwarding (`net.ipv4.ip_forward`).
- Sets up NAT (Masquerading) using the system's active firewall framework (iptables/nftables).
- Starts a local `dnsmasq` instance to serve DHCP and forward DNS to the Van LAN clients.

**Action:**
- Delete the `setup_routing()` function entirely from `network_controller.py` and `app.py`.
- Ensure the `start_ap()` function continues to use `nmcli device wifi hotspot` or explicitly sets `ipv4.method shared`.
- This creates a minimal, robust solution handled entirely by the NetworkManager daemon.

## 2. Captive Portal Detection
**Goal:** Detect when the upstream campsite Wi-Fi has a captive portal and notify the user via the Van LAN UI, mirroring how smartphones behave.

**How Captive Portals work over NAT:**
Because NetworkManager uses standard NAT, the connected clients (smartphones/laptops) will naturally have their own native captive portal detections triggered (e.g., Apple devices requesting `captive.apple.com`). The DNS requests and HTTP checks pass through the Pi, are intercepted by the campsite network, and the client displays the login page.
However, we also want the Pi's own Dashboard to be aware of the portal state.

**Action:**
1.  **Configure NM Connectivity Check:** We will create a configuration file at `/etc/NetworkManager/conf.d/20-connectivity.conf` (applied during package installation or via a setup script) with the following content:
    ```ini
    [connectivity]
    uri=http://connectivity-check.ubuntu.com/
    interval=300
    response=NetworkManager is online
    ```
    *(Alternatively, we can use Apple's `http://captive.apple.com/hotspot-detect.html` or similar)*

2.  **Monitor State in Python:** Update `network_controller.py` (`get_status()`) to query this state using `nmcli networking connectivity`. This command returns:
    - `full`: Internet access is fully available.
    - `portal`: A captive portal is intercepting requests.
    - `limited`/`none`: No connectivity.

3.  **UI Updates:** Update the Flask app and Frontend. If the status is `portal`, display a prominent alert banner on the dashboard: *"Captive Portal Detected. Click here to authenticate."* The link will point to a plain HTTP site (e.g., `http://neverssl.com` or the gateway IP) to force the user's browser to hit the upstream captive portal, log in, and authorize the Pi's MAC address.

## 3. Debian Trixie Considerations
- Ensure the Debian package dependencies (`debian/control`) include `dnsmasq-base`. NetworkManager requires this binary to run its internal `shared` method DHCP server.
- Ensure we do *not* run a standalone `dnsmasq` service, as it will conflict with NetworkManager's internal instance.

## Summary of Code Changes
1.  **`network_controller.py`**:
    - Remove `setup_routing()`.
    - Add `get_connectivity_state()` using `nmcli networking connectivity`.
    - Include this state in the `get_status()` return dictionary.
2.  **`app.py`**:
    - Remove calls to `setup_routing()`.
    - Pass connectivity state to the `index.html` template.
3.  **`templates/index.html`**:
    - Add a banner/alert for the "Captive Portal" state.
4.  **`debian/install` / `scripts/setup/`**:
    - Add the deployment of the `20-connectivity.conf` NetworkManager config file.
    - Update dependencies if needed.

Please review this plan. If approved, I will proceed with the codebase refactoring.