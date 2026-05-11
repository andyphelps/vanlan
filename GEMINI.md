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

This project uses `uv` and a `Makefile` for management.

1.  Install dependencies: `uv sync`
2.  Run the app:
    ```bash
    make dev
    ```
    *Note: Real network changes require running as root and having `nmcli` installed.*

### Building the Debian Package

The build process is containerized to support both Linux and MacOS development.

1.  Ensure Docker is running.
2.  Build the package:
    ```bash
    make build
    ```
    The resulting `.deb` package will be placed in the current directory.

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
