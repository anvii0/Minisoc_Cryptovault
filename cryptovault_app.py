import json
import logging
import logging.handlers
import os
import socket
from flask import Flask, request, render_template, render_template_string, redirect, url_for, session, jsonify
from datetime import datetime

import attack_simulator
import attack_1_initial_access
import attack_2_lateral_movement
import attack_3_exfiltration
import attack_4_ransomware

app = Flask(__name__)
# Required for session management
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'super-secure-key-1234')

# --- 1. SET UP THE LOGGING ENGINE ---
logger = logging.getLogger('CryptoVaultLogger')
logger.setLevel(logging.INFO)
logger.propagate = False

LOG_FILE = os.getenv('CRYPTOVAULT_LOG_FILE', 'cryptovault_audit.log')
APP_NAME = os.getenv('CRYPTOVAULT_APP_NAME', 'CryptoVault_Frontend')

# SIEM Connection Settings
# Use 127.0.0.1 for local testing if Docker ports are exposed.
WAZUH_IP = os.getenv('WAZUH_HOST', '127.0.0.1').strip()
WAZUH_PORT = int(os.getenv('WAZUH_PORT', '514'))
GRAYLOG_IP = os.getenv('GRAYLOG_HOST', '127.0.0.1').strip()
GRAYLOG_PORT = int(os.getenv('GRAYLOG_PORT', '12201'))
GRAYLOG_SOURCE = os.getenv('GRAYLOG_SOURCE', socket.gethostname())

if not logger.handlers:
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setFormatter(logging.Formatter('%(message)s'))
    logger.addHandler(file_handler)

def send_to_wazuh(log_data):
    """Refactored: Sends structured JSON wrapped in a Syslog header to Wazuh."""
    if not WAZUH_IP:
        return
    try:
        # Wrap JSON in a syslog-compatible string (RFC 3164/5424 style header)
        # <14> is Facility 1 (user-level), Severity 6 (info)
        syslog_header = f"<14>{datetime.utcnow().strftime('%b %d %H:%M:%S')} {socket.gethostname()} {APP_NAME}: "
        payload = (syslog_header + json.dumps(log_data) + '\n').encode('utf-8')
        
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(payload, (WAZUH_IP, WAZUH_PORT))
        print(f"[DEBUG] Sent log to Wazuh Syslog at {WAZUH_IP}:{WAZUH_PORT}")
    except Exception as e:
        print(f"[ERROR] Failed to forward event to Wazuh at {WAZUH_IP}:{WAZUH_PORT}: {e}")

def severity_to_syslog_level(severity):
    severity_map = {
        'DEBUG': 7,
        'INFO': 6,
        'WARNING': 4,
        'ERROR': 3,
        'CRITICAL': 2,
    }
    return severity_map.get(severity.upper(), 6)

def send_to_graylog(log_data):
    """Refactored: Sends strict GELF 1.1 formatted logs to Graylog."""
    if not GRAYLOG_IP:
        return

    try:
        # Strict GELF 1.1 Payload
        gelf_payload = {
            'version': '1.1',
            'host': GRAYLOG_SOURCE,
            'short_message': f"{log_data['event_type']} - {log_data['username']}",
            'full_message': log_data['details'],
            'timestamp': datetime.utcnow().timestamp(),
            'level': severity_to_syslog_level(log_data['severity']),
            '_app_name': APP_NAME,
            '_event_type': log_data['event_type'],
            '_severity': log_data['severity'],
            '_username': log_data['username'],
            '_source_ip': log_data['source_ip'],
            '_log_source': log_data.get('log_source', 'Application')
        }
        
        payload = json.dumps(gelf_payload).encode('utf-8')
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(payload, (GRAYLOG_IP, GRAYLOG_PORT))
        print(f"[DEBUG] Sent GELF to Graylog at {GRAYLOG_IP}:{GRAYLOG_PORT}")
    except Exception as e:
        print(f"[ERROR] Failed to forward event to Graylog at {GRAYLOG_IP}:{GRAYLOG_PORT}: {e}")

def generate_log(event_type, severity, user, ip, details="", log_source="Application Logs"):
    """Creates a structured JSON log entry and dispatches to SIEM targets."""
    log_data = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "app_name": APP_NAME,
        "log_source": log_source,
        "event_type": event_type,
        "severity": severity,
        "username": user,
        "source_ip": ip,
        "details": details
    }
    
    # 1. Local Audit Log
    payload = json.dumps(log_data)
    logger.info(payload)
    
    # 2. SIEM Dispatch
    send_to_wazuh(log_data)
    send_to_graylog(log_data)

# --- 3. ROUTES & EVENT TRIGGERS ---

@app.route('/', methods=['GET', 'POST'])
def login():
    if session.get('logged_in'):
        return redirect(url_for('dashboard'))
        
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        client_ip = request.remote_addr

        # Trigger 1: Authentication Log
        if username == 'admin' and password == 'secure123':
            generate_log("LOGIN_SUCCESS", "INFO", username, client_ip, "Successful authentication.", log_source="Active Directory")
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            # Trigger: Failed Login
            generate_log("LOGIN_FAILED", "WARNING", username, client_ip, "Invalid credentials provided.", log_source="Active Directory")
            error = "Invalid credentials provided."
            
    return render_template('login.html', error=error)

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    client_ip = request.remote_addr
    generate_log("PAGE_ACCESS", "INFO", session.get('username'), client_ip, "Accessed the Secure Vault dashboard.", log_source="Application Logs")
    
    # Check for success messages passed via redirect
    message = request.args.get('message')
    return render_template('dashboard.html', message=message)

@app.route('/simulator')
def simulator():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    client_ip = request.remote_addr
    generate_log("PAGE_ACCESS", "INFO", session.get('username'), client_ip, "Accessed the Simulator panel.", log_source="Application Logs")
    return render_template('simulator.html')

@app.route('/logout')
def logout():
    client_ip = request.remote_addr
    user = session.get('username', 'anonymous')
    generate_log("LOGOUT_SUCCESS", "INFO", user, client_ip, "Disconnected Ledger / Logged out.", log_source="Active Directory")
    session.clear()
    return redirect(url_for('login'))

@app.route('/withdraw', methods=['POST'])
def withdraw():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    client_ip = request.remote_addr
    amount = request.form.get('amount')
    address = request.form.get('address')
    
    # Trigger 2: Application Log (Withdrawal Spike Simulation)
    details = f"Transfer of {amount} BTC initiated to address: {address}"
    user = session.get('username')
    generate_log("WITHDRAWAL_INITIATED", "CRITICAL", user, client_ip, details, log_source="Application Logs")
    
    return redirect(url_for('dashboard', message=f"Transfer processing: {amount} BTC to {address}"))

@app.route('/simulate_impossible_travel', methods=['POST'])
def simulate_impossible_travel():
    # Stage 1: Initial Access
    attack_1_initial_access.run_simulation()
    return redirect(url_for('simulator'))

@app.route('/simulate_beaconing', methods=['POST'])
def simulate_beaconing():
    # Stage 3: Data Exfiltration
    attack_3_exfiltration.run_simulation()
    return redirect(url_for('simulator'))

@app.route('/simulate_clipboard', methods=['POST'])
def simulate_clipboard():
    # Stage 2: Lateral Movement
    attack_2_lateral_movement.run_simulation()
    return redirect(url_for('simulator'))

@app.route('/simulate_ransomware', methods=['POST'])
def simulate_ransomware():
    # Stage 4: Ransomware
    attack_4_ransomware.run_simulation()
    return jsonify({"status": "success", "message": "Stage 4 Ransomware Simulation completed."})

@app.errorhandler(404)
def page_not_found(e):
    client_ip = request.remote_addr
    # Trigger 3: Web Log (Scanning/Reconnaissance)
    generate_log("404_NOT_FOUND", "WARNING", "anonymous", client_ip, f"Attempted to access missing path: {request.path}", log_source="Nginx / Apache")
    
    not_found_html = """
        {% extends "base.html" %}
        {% block content %}
        <div class="glass-card">
            <div class="logo" style="text-align: center;">404</div>
            <h2 style="text-align: center; margin-top: 1rem;">Restricted Area</h2>
            <p style="text-align: center;">The path you are looking for is encrypted or doesn't exist.</p>
            <div style="text-align: center; margin-top: 2rem;">
                <a href="{{ url_for('login') }}" class="btn" style="width: auto;">Return to Safety</a>
            </div>
        </div>
        {% endblock %}
    """
    return render_template_string(not_found_html, show_nav=False), 404

if __name__ == '__main__':
    app_host = os.getenv('CRYPTOVAULT_HOST', '127.0.0.1')
    app_port = int(os.getenv('CRYPTOVAULT_PORT', '5000'))
    print(f"Starting CryptoVault Frontend on http://{app_host}:{app_port}")
    print(f"Wazuh SIEM forwarding: {WAZUH_IP}:{WAZUH_PORT}")
    print(f"Graylog GELF forwarding: {GRAYLOG_IP}:{GRAYLOG_PORT}")
    print(f"Local audit log file: {LOG_FILE}")
    app.run(debug=True, host=app_host, port=app_port)
