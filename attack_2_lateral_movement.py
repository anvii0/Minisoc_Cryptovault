from siem_logger import log_event
import time

def run_simulation():
    print("--- STAGE 2: LATERAL MOVEMENT ---")
    
    ips = ["192.168.1.105", "45.33.12.91", "10.0.0.15"]
    for ip in ips:
        print(f"Brute forcing from {ip}...")
        for i in range(3):
            log_event(
                event_type="ssh_login",
                severity="ERROR",
                user="root",
                ip=ip,
                details=f"Failed SSH login attempt for user root from {ip}",
                status="FAILED"
            )
            time.sleep(0.5)
    
    # Success event
    log_event(
        event_type="ssh_login",
        severity="CRITICAL",
        user="root",
        ip="192.168.1.105",
        details="Accepted password for root from 192.168.1.105 port 22 ssh2",
        status="SUCCESSFUL"
    )

if __name__ == "__main__":
    run_simulation()
    print("Simulation Complete.")
