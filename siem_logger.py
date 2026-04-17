import socket
import json
import os
from datetime import datetime

# SIEM Connection Defaults
WAZUH_IP = os.getenv('WAZUH_HOST', '127.0.0.1')
WAZUH_PORT = int(os.getenv('WAZUH_PORT', '514'))
GRAYLOG_IP = os.getenv('GRAYLOG_HOST', '127.0.0.1')
GRAYLOG_PORT = int(os.getenv('GRAYLOG_PORT', '12201'))

def send_to_wazuh(log_data):
    """Sends structured JSON wrapped in a Syslog header to Wazuh manager."""
    try:
        app_name = log_data.get('app_name', 'CryptoVault_Frontend')
        syslog_header = f"<14>{datetime.utcnow().strftime('%b %d %H:%M:%S')} {socket.gethostname()} {app_name}: "
        payload = (syslog_header + json.dumps(log_data) + '\n').encode('utf-8')
        
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(payload, (WAZUH_IP, WAZUH_PORT))
    except Exception as e:
        print(f"[ERROR] Failed to forward to Wazuh: {e}")

def severity_to_syslog_level(severity):
    severity_map = {
        'DEBUG': 7, 'INFO': 6, 'WARNING': 4, 'ERROR': 3, 'CRITICAL': 2, 'ALERT': 1, 'EMERGENCY': 0
    }
    return severity_map.get(severity.upper(), 6)

def send_to_graylog(log_data):
    """Sends strict GELF 1.1 formatted logs to Graylog."""
    try:
        gelf_payload = {
            'version': '1.1',
            'host': socket.gethostname(),
            'short_message': f"{log_data['event_type']} - {log_data['username']}",
            'full_message': log_data.get('details', ''),
            'timestamp': datetime.utcnow().timestamp(),
            'level': severity_to_syslog_level(log_data['severity']),
            '_app_name': log_data.get('app_name', 'CryptoVault_Frontend'),
            '_event_type': log_data['event_type'],
            '_severity': log_data['severity'],
            '_username': log_data['username'],
            '_source_ip': log_data['source_ip'],
            '_log_source': log_data.get('log_source', 'AttackSimulator')
        }
        
        # Add additional fields if they exist in log_data
        for key, value in log_data.items():
            if key not in ['event_type', 'severity', 'username', 'source_ip', 'details', 'app_name', 'log_source', 'timestamp']:
                gelf_payload[f"_{key}"] = value
        
        payload = json.dumps(gelf_payload).encode('utf-8')
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(payload, (GRAYLOG_IP, GRAYLOG_PORT))
    except Exception as e:
        print(f"[ERROR] Failed to forward to Graylog: {e}")

def log_event(event_type, severity, user, ip, details="", log_source="AttackSimulator", app_name="CryptoVault_Frontend", **extra):
    """Helper to dispatch to both SIEMs."""
    log_data = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "app_name": app_name,
        "log_source": log_source,
        "event_type": event_type,
        "severity": severity,
        "username": user,
        "source_ip": ip,
        "details": details
    }
    log_data.update(extra)
    
    send_to_wazuh(log_data)
    send_to_graylog(log_data)
    print(f"[SENT] Event: {event_type} | User: {user} | Severity: {severity}")
