from flask import Flask, render_template, jsonify, request
import network_controller

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/status')
def status():
    return jsonify(network_controller.get_status())

@app.route('/scan')
def scan():
    results = network_controller.scan_wifi()
    return jsonify(results)

@app.route('/connect', methods=['POST'])
def connect():
    data = request.json
    ssid = data.get('ssid')
    password = data.get('password')
    interface = data.get('interface', 'wlan1')
    success = network_controller.connect_wifi(interface, ssid, password)
    return jsonify({'success': success})

if __name__ == '__main__':
    # Initial setup for routing
    network_controller.setup_routing()
    app.run(host='0.0.0.0', port=5005, debug=True)
