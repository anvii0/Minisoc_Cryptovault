import socket
import json
import time
from datetime import datetime

def run_ransomware_simulation(wazuh_ip='127.0.0.1', wazuh_port=1514):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send_log(log_data):
        """Formats and sends the log to Wazuh/Graylog"""
        log_data["timestamp"] = datetime.utcnow().isoformat() + "Z"
        message = json.dumps(log_data).encode('utf-8')
        sock.sendto(message, (wazuh_ip, wazuh_port))
        print(f"[+] Sent Log: {log_data['event_type']}")
        time.sleep(1.5) # Pause for dramatic effect during the demo

    print("=========================================")
    print("☠️ INITIATING PHASE 4 RANSOMWARE SIMULATION")
    print("=========================================\n")

    # Step 0: Initial Phishing Hook
    print(">>> STAGE 0: Phishing Link Clicked (MITRE T1566.002)")
    send_log({
        "event_type": "web_proxy_log", 
        "action": "allowed", 
        "url": "http://secure-cryptovault-update.net/login", 
        "source_ip": "10.0.3.15", 
        "user_agent": "Internal-Admin-Browser",
        "severity": "MEDIUM",
        "description": "User clicked link in email from unknown external sender"
    })

    # Step 1: Initial Access & Execution
    print(">>> STAGE 1: Execution (MITRE T1059.001)")
    send_log({
        "event_type": "process_creation", "process_name": "powershell.exe",
        "command_line": "powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -EncodedCommand JABz...",
        "user": "admin", "host": "jump-server-01", "severity": "HIGH"
    })

    send_log({
        "event_type": "process_creation", "process_name": "rundll32.exe",
        "command_line": "rundll32.exe C:\\Users\\admin\\AppData\\Local\\Temp\\payload.dll, Start",
        "user": "admin", "host": "jump-server-01", "severity": "CRITICAL"
    })

    # Step 2: Lateral Movement
    print("\n>>> STAGE 2: Lateral Movement (MITRE T1021.004)")
    for i in range(3):
        send_log({
            "event_type": "ssh_login", "status": "FAILED", "user": "root",
            "source_ip": "10.0.4.55", "destination_ip": "10.0.4.10", "host": "hot-wallet-server"
        })

    # Phase 3 Hunting Hypothesis: Clipboard Poisoning
    print("\n>>> PHASE 3: Clipboard Manipulation (MITRE T1115)")
    send_log({
        "event_type": "clipboard_access", 
        "process_name": "unknown_utility.exe", 
        "action": "read_and_replace", 
        "description": "Non-browser process accessed clipboard during withdrawal",
        "severity": "HIGH",
        "host": "admin-workstation"
    })

    # Step 3: Exfiltration
    print("\n>>> STAGE 3: DNS Exfiltration (MITRE T1048.003)")
    send_log({
        "event_type": "dns_query", "query_domain": "9a8b7c6d5e4f.evil-crypto-hacker.com",
        "query_length": 256, "is_suspicious": "true", "host": "hot-wallet-server"
    })

    # Step 4: Encryption
    print("\n>>> STAGE 4: Data Encrypted for Impact (MITRE T1486)")
    send_log({
        "event_type": "file_modification", "file_name": "wallet_keys.dat",
        "file_extension": ".locked", "action": "renamed", "host": "hot-wallet-server", "severity": "CRITICAL"
    })

    print("\n=========================================")
    print("✅ ATTACK SEQUENCE COMPLETE. CHECK GRAYLOG DASHBOARD.")
    print("=========================================")

if __name__ == "__main__":
    run_ransomware_simulation()