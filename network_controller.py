import subprocess
import re

def run_command(command):
    try:
        result = subprocess.run(command, capture_output=True, text=True, shell=True)
        return result.stdout
    except Exception as e:
        print(f"Error running command: {command}\n{e}")
        return ""

def get_status():
    status = {
        "ap": {"ssid": "Unknown", "active": False},
        "outbound": {"ssid": "Disconnected", "connected": False, "interface": "None"}
    }
    
    # Get active connections
    output = run_command("nmcli -t -f DEVICE,TYPE,STATE,CONNECTION device")
    for line in output.splitlines():
        parts = line.split(':')
        if len(parts) >= 4:
            dev, dev_type, state, conn = parts
            if state == "connected":
                if dev == "wlan0": # Assuming wlan0 is AP
                    status["ap"] = {"ssid": conn, "active": True}
                elif dev in ["wlan1", "usb0", "eth0"]: # Outbound
                    status["outbound"] = {"ssid": conn, "connected": True, "interface": dev}
    return status

def scan_wifi(interface="wlan1"):
    output = run_command(f"nmcli -t -f SSID,SIGNAL,SECURITY device wifi list ifname {interface}")
    networks = []
    for line in output.splitlines():
        parts = line.split(':')
        if len(parts) >= 3:
            ssid, signal, security = parts
            if ssid:
                networks.append({"ssid": ssid, "signal": signal, "security": security})
    return networks

def connect_wifi(interface, ssid, password):
    # This might take a few seconds
    cmd = f"nmcli device wifi connect '{ssid}' password '{password}' ifname {interface}"
    output = run_command(cmd)
    return "successfully activated" in output.lower()

def setup_routing():
    # Enable IP forwarding
    run_command("sudo sysctl -w net.ipv4.ip_forward=1")
    
    # Check if iptables is available
    if run_command("which iptables"):
        # Basic NAT setup (assuming wlan0 is AP and wlan1/usb0 are internet)
        run_command("sudo iptables -t nat -A POSTROUTING -o wlan1 -j MASQUERADE")
        run_command("sudo iptables -t nat -A POSTROUTING -o usb0 -j MASQUERADE")
    elif run_command("which nft"):
        # Basic nftables NAT setup
        run_command("sudo nft add table ip nat")
        run_command("sudo nft add chain ip nat postrouting { type nat hook postrouting priority 100 \; }")
        run_command("sudo nft add rule ip nat postrouting oifname 'wlan1' masquerade")
        run_command("sudo nft add rule ip nat postrouting oifname 'usb0' masquerade")

def start_ap(interface="wlan0", ssid="VanLAN", password="password"):
    # cmd = f"nmcli device wifi hotspot ifname {interface} ssid '{ssid}' password '{password}'"
    return True
