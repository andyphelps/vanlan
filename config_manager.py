import configparser
import os

CONFIG_PATH = '/etc/vanlan-router.config'
DEFAULT_CONFIG = {
    'admin_password': 'admin',
    'ap_ssid': 'VanLAN',
    'ap_password': 'password',
    'dhcp_lease_time': '259200' # 3 days in seconds
}

def load_config():
    config = configparser.ConfigParser()
    
    # Initialize with defaults
    full_config = DEFAULT_CONFIG.copy()
    
    if not os.path.exists(CONFIG_PATH):
        return full_config
        
    try:
        config.read(CONFIG_PATH)
        if 'Settings' in config:
            for key in DEFAULT_CONFIG:
                if key in config['Settings']:
                    full_config[key] = config['Settings'][key]
    except Exception:
        pass
        
    return full_config

def save_config(config_dict):
    config = configparser.ConfigParser()
    config['Settings'] = config_dict
    
    try:
        with open(CONFIG_PATH, 'w') as f:
            config.write(f)
        return True
    except Exception:
        return False

def is_default_config():
    config = load_config()
    return (config['ap_ssid'] == DEFAULT_CONFIG['ap_ssid'] or 
            config['ap_password'] == DEFAULT_CONFIG['ap_password'] or 
            config['admin_password'] == DEFAULT_CONFIG['admin_password'])
