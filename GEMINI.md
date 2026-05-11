# Van LAN Router

A Raspberry Pi-based motorhome LAN router with a web management interface. It allows you to share a single internet connection (Campsite Wi-Fi via USB dongle or iPhone via USB tethering) across multiple local devices via a "Van LAN" Wi-Fi hotspot.

## Project Overview

*   **Purpose:** Provide a centralized gateway for motorhome/van internet access.
*   **Technologies:** 
    *   **Backend:** Python 3 + Flask
    *   **Frontend:** Bootstrap 5 (Responsive UI)
    *   **Networking:** NetworkManager (`nmcli`), `iptables` (NAT/Routing)
    *   **Packaging:** Debian Package (`.deb`)

## Architecture

1.  **Web Interface (`app.py` & `templates/`):** A mobile-friendly dashboard to monitor connection status and scan/connect to external Wi-Fi networks.
2.  **Networking Core (`network_controller.py`):** Wraps `nmcli` commands to interact with the system's network stack.
3.  **Deployment:** The application is intended to run as a systemd service (`vanlan-router.service`) with root privileges to manage system networking.

## Building and Running

### Local Development

This project uses `uv` for dependency management and virtual environments.

1.  Install `uv` if you haven't already: [https://github.com/astral-sh/uv](https://github.com/astral-sh/uv)
2.  Install dependencies and create a venv:
    ```bash
    uv sync
    ```
3.  Run the app:
    ```bash
    uv run app.py
    ```
    *Note: Real network changes require running as root and having `nmcli` installed.*

### Building the Debian Package

To build the `.deb` package for installation on a Raspberry Pi:

1.  Install build tools:
    ```bash
    sudo apt update && sudo apt install -y debhelper devscripts
    ```
2.  Build the package:
    ```bash
    dpkg-buildpackage -us -uc -b
    ```
3.  Install the generated package:
    ```bash
    sudo dpkg -i ../vanlan-router_1.0.0_all.deb
    sudo apt-get install -f  # To fix missing dependencies
    ```

## Development Conventions

*   **Networking:** Always use `nmcli` via the `network_controller.py` wrapper to ensure consistency.
*   **Privileges:** The production service runs as `root` to allow `sysctl` and `iptables` modifications.
*   **Interfaces:** 
    *   `wlan0`: Default interface for the Local AP (Van LAN).
    *   `wlan1`: Default interface for scanning and connecting to external Wi-Fi.
    *   `usb0`: Default interface for iPhone tethering.

## TODO / Future Improvements

- [ ] Implement manual IP configuration.
- [ ] Add bandwidth monitoring.
- [ ] Support for multiple outbound priority (Failover).
- [ ] VPN integration (e.g., WireGuard).
