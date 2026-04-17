import socket
import json
import time
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
        print(f"[+] Sent: {payload['short_message']} (Event: {payload.get('_event_type', 'N/A')})")
    except Exception as e:
        print(f"[!] Error: {e}")

def create_base_gelf(short_msg, level=6):
    return {
        "version": "1.1",
        "host": "soc-workstation-01",
        "short_message": short_msg,
        "timestamp": datetime.utcnow().timestamp(),
        "level": level,
        "_app_name": "CryptoVault_SOC_Demo"
    }

def populate_dashboard():
    print(f"=== Populating Graylog Dashboard Widgets ===")
    print(f"Target: {GRAYLOG_IP}:{GRAYLOG_PORT}\n")

    # 1. Widget: Initial Access Monitor
    print("Populating: Initial Access Monitor...")
    payloads = [
        {
            **create_base_gelf("PowerShell Malicious Script Execution", level=4),
            "_event_type": "process_creation",
            "_process_name": "powershell.exe",
            "_command_line": "powershell.exe -ep bypass -Enc SUVYIChOZXctT2JqZWN0IE5ldC5XZWJDbGllbnQpLkRv..."
        },
        {
            **create_base_gelf("Rundll32 Loading Payload", level=4),
            "_event_type": "process_creation",
            "_process_name": "rundll32.exe",
            "_command_line": "rundll32.exe C:\\Windows\\Temp\\update.dll,Exploit"
        }
    ]
    for p in payloads:
        send_gelf(p)
        time.sleep(1)

    # 2. Widget: Lateral Movement Tracker
    print("\nPopulating: Lateral Movement Tracker...")
    ips = ["192.168.1.105", "45.33.12.91", "10.0.0.15"]
    for ip in ips:
        for _ in range(3):
            payload = {
                **create_base_gelf(f"SSH Auth Failure from {ip}", level=3),
                "_event_type": "ssh_login",
                "_status": "FAILED",
                "_source_ip": ip
            }
            send_gelf(payload)
            time.sleep(0.5)

    # 3. Widget: Data Exfiltration Radar
    print("\nPopulating: Data Exfiltration Radar...")
    for i in range(10):
        payload = {
            **create_base_gelf(f"Suspicious DNS Request {i+1}", level=3),
            "_event_type": "dns_query",
            "_is_suspicious": "true",
            "_domain": f"exfil-chunk-{i}.attacker.com"
        }
        send_gelf(payload)
        time.sleep(1)

    # 4. Widget: Ransomware Encryption Alarm
    print("\nPopulating: Ransomware Encryption Alarm...")
    for i in range(5):
        payload = {
            **create_base_gelf(f"File modified to .locked", level=1),
            "_event_type": "file_modification",
            "_file_extension": ".locked",
            "_file_path": f"C:\\Users\\Admin\\Documents\\file_{i}.docx.locked"
        }
        send_gelf(payload)
        time.sleep(1)

    # 5. Widget: Business Impact Metric
    print("\nPopulating: Business Impact Metric...")
    amounts = [15000, 25000, 12000]
    for amt in amounts:
        payload = {
            **create_base_gelf(f"High Value Withdrawal: {amt} USD", level=2),
            "_event_type": "WITHDRAWAL_INITIATED",
            "_amount": amt,
            "_username": "whale_user_01"
        }
        send_gelf(payload)
        time.sleep(2)

    print("\n=== Success! Widgets should now be populated in Graylog. ===")

if __name__ == "__main__":
    populate_dashboard()
