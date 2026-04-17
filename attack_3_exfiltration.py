from siem_logger import log_event
import time

def run_simulation():
    print("--- STAGE 3: DATA EXFILTRATION ---")
    
    for i in range(5):
        domain = f"keys-chunk-{i}.attacker-controlled-dns.xyz"
        log_event(
            event_type="dns_query",
            severity="HIGH LEVEL",
            user="system",
            ip="10.0.0.5",
            details=f"Query type A for domain: {domain}",
            is_suspicious="true",
            domain=domain
        )
        time.sleep(1)

if __name__ == "__main__":
    run_simulation()
    print("Simulation Complete.")
