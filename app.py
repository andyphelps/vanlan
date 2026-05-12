from flask import Flask, render_template, jsonify, request, session, redirect, url_for
import network_controller
import config_manager
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.urandom(24)

def is_authenticated():
    return session.get('authenticated', False)

@app.route('/')
def index():
    if not is_authenticated():
        return render_template('login.html')
    if config_manager.is_default_config():
        return render_template('setup.html')
    return render_template('index.html')

@app.route('/setup', methods=['POST'])
def setup():
    # Only allow setup if authenticated AND using defaults
    if not is_authenticated() or not config_manager.is_default_config():
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    new_ssid = data.get('ap_ssid')
    new_wifi_pass = data.get('ap_password')
    new_admin_pass = data.get('admin_password')

    # Force all three to be provided and non-default
    if not all([new_ssid, new_wifi_pass, new_admin_pass]):
        return jsonify({'success': False, 'message': 'All fields are required'}), 400
    
    defaults = config_manager.DEFAULT_CONFIG
    if new_ssid == defaults['ap_ssid'] or new_wifi_pass == defaults['ap_password'] or new_admin_pass == defaults['admin_password']:
        return jsonify({'success': False, 'message': 'Values must be different from defaults'}), 400

    if len(new_wifi_pass) < 8:
        return jsonify({'success': False, 'message': 'Wi-Fi password must be at least 8 characters'}), 400

    config = {
        'ap_ssid': new_ssid,
        'ap_password': new_wifi_pass,
        'admin_password': new_admin_pass
    }
    
    if config_manager.save_config(config):
        network_controller.start_ap(interface="wlan0", ssid=new_ssid, password=new_wifi_pass)
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Failed to save config'}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    config = config_manager.load_config()
    if data.get('password') == config['admin_password']:
        session['authenticated'] = True
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Invalid password'}), 401

@app.route('/logout')
def logout():
    session.pop('authenticated', None)
    return redirect(url_for('index'))

@app.route('/status')
def status():
    if not is_authenticated():
        return jsonify({'error': 'Unauthorized'}), 401
    status_data = network_controller.get_status()
    return jsonify(status_data)

@app.route('/scan')
def scan():
    if not is_authenticated():
        return jsonify({'error': 'Unauthorized'}), 401
    results = network_controller.scan_wifi()
    return jsonify(results)

@app.route('/connect', methods=['POST'])
def connect():
    if not is_authenticated():
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    ssid = data.get('ssid')
    password = data.get('password')
    interface = data.get('interface', 'wifi0')
    success = network_controller.connect_wifi(interface, ssid, password)
    return jsonify({'success': success})

@app.route('/settings', methods=['POST'])
def update_settings():
    if not is_authenticated():
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    config = config_manager.load_config()
    
    new_ap_ssid = data.get('ap_ssid')
    new_ap_password = data.get('ap_password')
    new_admin_password = data.get('admin_password')
    new_lease_hours = data.get('lease_hours')
    
    if (new_ap_ssid): config['ap_ssid'] = new_ap_ssid
    if (new_ap_password): config['ap_password'] = new_ap_password
    if (new_admin_password): config['admin_password'] = new_admin_password
    
    if new_lease_hours:
        try:
            # Convert hours to seconds
            seconds = int(new_lease_hours) * 3600
            config['dhcp_lease_time'] = str(seconds)
        except ValueError:
            return jsonify({'success': False, 'message': 'Invalid lease time'}), 400
    
    if config_manager.save_config(config):
        # Apply AP changes immediately if SSID, Password, or Lease Time changed
        if new_ap_ssid or new_ap_password or new_lease_hours:
            network_controller.start_ap(
                interface="wlan0", 
                ssid=config['ap_ssid'], 
                password=config['ap_password'],
                lease_time=config.get('dhcp_lease_time', '259200')
            )
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Failed to save config'}), 500

if __name__ == '__main__':
    config = config_manager.load_config()
    
    # Configure interface priorities (prefer Wi-Fi/USB over Ethernet)
    network_controller.setup_interface_priorities()

    # Start the local Access Point with configured credentials
    network_controller.start_ap(
        interface="ap0", 
        ssid=config['ap_ssid'], 
        password=config['ap_password'],
        lease_time=config.get('dhcp_lease_time', '259200')
    )
    
    app.run(host='0.0.0.0', port=80, debug=False)

