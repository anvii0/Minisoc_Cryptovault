from siem_logger import log_event
import time

def run_simulation():
    print("--- PHASE 4: INCIDENT RESPONSE & CONTAINMENT ---")
    
    # 1. SIEM Alert Correlation
    print("Simulating SIEM Alert Correlation...")
    log_event(
        event_type="INCIDENT_CORRELATION",
        severity="CRITICAL",
        user="SOAR_AUTOMATION",
        ip="127.0.0.1",
        details="High-confidence Ransomware behavior detected. Triggering Playbook ID: CRYPTO-LOCK-V4.",
        log_source="SOAR Engine",
        incident_id="INC-2026-0042"
    )
    time.sleep(2)
    
    # 2. Containment: Freeze Wallet
    print("Simulating Wallet Freeze...")
    log_event(
        event_type="WALLET_FREEZE",
        severity="ALERT",
        user="SOAR_AUTOMATION",
        ip="10.0.0.5",
        details="Access to Ledger 'Main_Hot_Wallet' has been FROZEN. No further withdrawals permitted.",
        log_source="Vault Security Manager",
        action_status="SUCCESSFUL",
        target_wallet="Main_Hot_Wallet"
    )
    time.sleep(2)
    
    # 3. Containment: Host Isolation
    print("Simulating Host Isolation...")
    log_event(
        event_type="HOST_ISOLATION",
        severity="CRITICAL",
        user="EDR_SYSTEM",
        ip="10.0.0.5",
        details="Endpoint 10.0.0.5 has been isolated from the network. Only SIEM communication permitted.",
        log_source="CrowdStrike EDR",
        action_taken="NETWORK_QUARANTINE"
    )

if __name__ == "__main__":
    run_simulation()
    print("\nPhase 4 Simulation Complete. You can now build your IR Dashboard in Graylog!")
