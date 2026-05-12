import subprocess
import re
import logging
import shlex
import os
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_command(args):
    """Runs a command and returns its stdout. Args can be a string (split by space) or a list."""
    if isinstance(args, str):
        args = shlex.split(args)
    try:
        logger.info(f"Executing: {' '.join(args)}")
        result = subprocess.run(args, capture_output=True, text=True)
        if result.stderr:
            logger.error(f"Command '{' '.join(args)}' stderr: {result.stderr.strip()}")
        return result.stdout.strip()
    except Exception as e:
        logger.error(f"Error running command: {' '.join(args)}\n{e}")
        return ""

def get_connectivity_state():
    # Returns: full, portal, limited, none, or unknown
    output = run_command(["nmcli", "-t", "networking", "connectivity"])
    return output if output else "unknown"

def get_lan_clients(interface="ap0"):
    clients = []
    # NM stores leases in /var/lib/NetworkManager/dnsmasq-<interface>.leases
    lease_file = f"/var/lib/NetworkManager/dnsmasq-{interface}.leases"
    
    if not os.path.exists(lease_file):
        # Fallback to general location
        if os.path.exists("/var/lib/misc/dnsmasq.leases"):
            lease_file = "/var/lib/misc/dnsmasq.leases"
        else:
            return clients

    try:
        with open(lease_file, "r") as f:
            for line in f:
                parts = line.split()
                if len(parts) >= 5:
                    expiry_ts, mac, ip, hostname, client_id = parts[:5]
                    # Convert expiry timestamp to readable format including date
                    expiry_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(expiry_ts)))
                    clients.append({
                        "ip": ip,
                        "mac": mac,
                        "hostname": hostname if hostname != "*" else "Unknown Device",
                        "expiry": expiry_time
                    })
    except Exception as e:
        logger.error(f"Error reading lease file {lease_file}: {e}")
    
    return clients

def get_interface_ip(interface):
    if not interface or interface == "None":
        return None
    output = run_command(["nmcli", "-t", "-f", "IP4.ADDRESS", "device", "show", interface])
    for line in output.splitlines():
        if "IP4.ADDRESS" in line:
            # line is like 'IP4.ADDRESS[1]:10.42.0.1/24'
            parts = line.split(':')
            if len(parts) >= 2:
                return parts[1].split('/')[0]
    return None

def get_primary_outbound_interface():
    """
    Asks the kernel for the interface that provides the default route.
    Returns the device name (e.g. 'wifi0') or None.
    """
    # 'ip route show default' returns routes in order of metric (lowest first)
    output = run_command("ip -4 route show default")
    if output:
        # Example: 'default via 192.168.1.1 dev wlan0 proto dhcp src 192.168.1.5 metric 600'
        first_line = output.splitlines()[0]
        parts = first_line.split()
        if "dev" in parts:
            try:
                dev_idx = parts.index("dev")
                return parts[dev_idx + 1]
            except (ValueError, IndexError):
                pass
    return None

def get_status():
    status = {
        "ap": {"ssid": "Unknown", "active": False, "interface": "None", "ip": "None"},
        "outbound": {"ssid": "Disconnected", "connected": False, "interface": "None", "ip": "None"},
        "connectivity": get_connectivity_state(),
        "devices": []
    }
    
    # Get all device statuses
    output = run_command(["nmcli", "-t", "-f", "DEVICE,TYPE,STATE,CONNECTION", "device"])
    
    ap_interface = "ap0" # Default fallback
    connected_devices = {}
    
    for line in output.splitlines():
        parts = line.split(':')
        if len(parts) >= 4:
            dev, dev_type, state, conn = parts
            status["devices"].append({"device": dev, "type": dev_type, "state": state, "connection": conn})
            
            if state == "connected":
                connected_devices[dev] = {"type": dev_type, "conn": conn}
                
                # Check if this connection is a hotspot
                conn_mode = run_command(["nmcli", "-t", "-f", "802-11-wireless.mode", "connection", "show", conn])
                if "ap" in conn_mode.lower():
                    # Fetch the ACTUAL SSID (not the connection name)
                    real_ssid = run_command(["nmcli", "-t", "-f", "802-11-wireless.ssid", "connection", "show", conn])
                    if ":" in real_ssid:
                        real_ssid = real_ssid.split(':', 1)[1]
                    
                    ap_interface = dev
                    status["ap"] = {
                        "ssid": real_ssid if real_ssid else conn, 
                        "active": True, 
                        "interface": dev,
                        "ip": get_interface_ip(dev)
                    }

    # Determine the active outbound connection based on the system's default route
    primary_dev = get_primary_outbound_interface()
    
    # If the primary device is our own AP, it's not really 'outbound' for the internet
    if primary_dev and primary_dev == ap_interface:
        primary_dev = None

    if primary_dev and primary_dev in connected_devices:
        dev_info = connected_devices[primary_dev]
        dev = primary_dev
        conn = dev_info["conn"]
        
        if dev_info["type"] == "wifi":
            real_ssid = run_command(["nmcli", "-t", "-f", "802-11-wireless.ssid", "connection", "show", conn])
            if ":" in real_ssid:
                real_ssid = real_ssid.split(':', 1)[1]
            status["outbound"] = {
                "ssid": real_ssid if real_ssid else conn, 
                "connected": True, 
                "interface": dev,
                "ip": get_interface_ip(dev)
            }
        else:
            status["outbound"] = {
                "ssid": conn, 
                "connected": True, 
                "interface": dev,
                "ip": get_interface_ip(dev)
            }

    # Fetch clients for the actual AP interface
    status["clients"] = get_lan_clients(ap_interface)
    
    return status


def scan_wifi(interface="wifi0"):
    # Ensure Wi-Fi radio is on
    run_command(["nmcli", "radio", "wifi", "on"])
    output = run_command(["nmcli", "-t", "-f", "SSID,BSSID,SIGNAL,SECURITY", "device", "wifi", "list", "ifname", interface])
    networks = []
    for line in output.splitlines():
        # nmcli -t uses backslash to escape colons in MAC addresses
        # e.g. SSID:00\:11\:22\:33\:44\:55:SIGNAL:SECURITY
        # We need a regex or a more careful split
        parts = re.split(r'(?<!\\):', line)
        if len(parts) >= 4:
            ssid, bssid, signal, security = parts[:4]
            if ssid:
                # Clean up escaped colons in BSSID
                bssid = bssid.replace('\\:', ':')
                networks.append({"ssid": ssid, "bssid": bssid, "signal": signal, "security": security})
    return networks

def connect_wifi(interface, ssid, password):
    # This might take a few seconds
    run_command(["nmcli", "device", "wifi", "rescan", "ifname", interface])
    
    # Delete existing connection with this SSID to avoid conflicts/stale config
    run_command(["nmcli", "connection", "delete", ssid])
    
    # Try a more robust connection approach
    cmd = ["nmcli", "device", "wifi", "connect", ssid, "password", password, "ifname", interface]
    output = run_command(cmd)
    logger.info(f"Connect output: {output}")
    
    success = "successfully activated" in output.lower()
    
    # If direct connect fails, try to manually add the connection
    if not success:
        logger.info("Retrying with explicit connection profile creation...")
        run_command(["nmcli", "connection", "add", "type", "wifi", "con-name", ssid, "ifname", interface, "ssid", ssid, "--", "wifi-sec.key-mgmt", "wpa-psk", "wifi-sec.psk", password])
        output = run_command(["nmcli", "connection", "up", ssid])
        success = "successfully activated" in output.lower()

    if not success:
        logger.error(f"Failed to connect to {ssid} on {interface}")
    else:
        # Trigger an immediate connectivity check to detect captive portals faster
        logger.info("Connection successful, triggering immediate connectivity check...")
        run_command(["nmcli", "networking", "connectivity", "check"])

    return success

def forget_wifi(ssid):
    logger.info(f"Forgetting Wi-Fi connection: {ssid}")
    # NM connection names for Wi-Fi often match the SSID
    output = run_command(["nmcli", "connection", "delete", ssid])
    return "successfully deleted" in output.lower() or "not found" in output.lower()

def setup_interface_priorities():
    """
    Ensure ethernet (debug0) has a lower priority (higher metric) than 
    wireless (wifi0) or USB (tether0) to allow debug0 to be used for debugging
    without hijacking the default route.
    """
    logger.info("Configuring network interface priorities...")
    conns = run_command(["nmcli", "-t", "-f", "NAME,TYPE,DEVICE", "connection", "show"])
    
    for line in conns.splitlines():
        parts = line.split(':')
        if len(parts) >= 3:
            name, c_type, dev = parts
            
            # Skip the AP connection
            if dev == "ap0":
                continue

            metric = None
            if dev == "debug0":
                metric = "2000" # Internal Ethernet is the Debug Port
            elif dev == "tether0":
                metric = "500"  # iPhone / USB Tethering (High Priority)
            elif dev == "wifi0":
                metric = "600"  # Campsite Wi-Fi (Medium Priority)
            elif c_type == "802-3-ethernet":
                # Any other Ethernet adapter (e.g. secondary USB-Eth)
                metric = "700"  
            
            if metric:
                logger.info(f"Setting metric {metric} for connection '{name}' on {dev}")
                run_command(["nmcli", "connection", "modify", name, "ipv4.route-metric", metric])

def wait_for_network_manager(timeout=30):
    """Wait for NetworkManager to be available and responsive."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        output = run_command(["nmcli", "-t", "-f", "STATE", "g"])
        if output:
            return True
        logger.info("Waiting for NetworkManager...")
        time.sleep(2)
    return False

def start_ap(interface="ap0", ssid="VanLAN", password="password", lease_time="259200"):
    logger.info(f"Starting AP on {interface} with SSID {ssid} and lease time {lease_time}")
    
    if not wait_for_network_manager():
        logger.error("NetworkManager not available. Cannot start AP.")
        return False

    # Ensure Wi-Fi radio is on
    run_command(["nmcli", "radio", "wifi", "on"])
    
    # Throroughly clean up ALL existing connections on this interface that might be hotspots
    # to avoid "Hotspot-1" style naming conflicts
    all_conns = run_command(["nmcli", "-t", "-f", "NAME,TYPE,DEVICE", "connection", "show"])
    for line in all_conns.splitlines():
        parts = line.split(':')
        if len(parts) >= 3:
            c_name, c_type, c_dev = parts
            if c_dev == interface or (c_type == "802-11-wireless" and not c_dev):
                # Check if it's an AP mode connection
                mode = run_command(["nmcli", "-t", "-f", "802-11-wireless.mode", "connection", "show", c_name])
                if "ap" in mode.lower() or c_name == ssid:
                    logger.info(f"Cleaning up old AP connection: {c_name}")
                    run_command(["nmcli", "connection", "down", c_name])
                    run_command(["nmcli", "connection", "delete", c_name])
    
    # Create the hotspot connection explicitly. 
    output = run_command(["nmcli", "device", "wifi", "hotspot", "ifname", interface, "ssid", ssid, "password", password])
    
    if "successfully activated" in output.lower():
        # Find the newly created connection (it's the active one on the interface)
        new_conn = run_command(["nmcli", "-t", "-f", "CONNECTION", "device", "show", interface]).split('\n')[0].split(':')[-1]
        if new_conn:
            # Standardize the connection name to the SSID and ensure it uses shared method
            # Also disable IPv6 to prevent routing leaks/issues
            run_command(["nmcli", "connection", "modify", new_conn, "connection.id", ssid, "connection.autoconnect", "yes", "ipv4.method", "shared", "ipv6.method", "ignore", "ipv4.dhcp-lease-time", str(lease_time)])
        return True
    
    logger.error(f"Failed to start AP: {output}")
    # Fallback: try manual connection creation
    logger.info("Attempting manual AP profile creation...")
    run_command(["nmcli", "connection", "add", "type", "wifi", "ifname", interface, "con-name", ssid, "autoconnect", "yes", "ssid", ssid, "mode", "ap", "802-11-wireless.band", "bg", "ipv4.method", "shared", "ipv6.method", "ignore", "wifi-sec.key-mgmt", "wpa-psk", "wifi-sec.psk", password, "ipv4.dhcp-lease-time", str(lease_time)])
    output = run_command(["nmcli", "connection", "up", ssid])
    return "successfully activated" in output.lower()
