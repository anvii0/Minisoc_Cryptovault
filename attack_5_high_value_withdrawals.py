from siem_logger import log_event
import time
import random

def run_simulation():
    print("--- STAGE 5: HIGH VALUE WITHDRAWALS ---")
    
    users = ["kaveri", "anvita", "pes", "bellyhop"]
    ips = ["192.168.1.50", "192.168.1.51", "192.168.1.52", "192.168.1.53"]
    
    for user, ip in zip(users, ips):
        amount = random.randint(15000, 50000)
        print(f"Simulating withdrawal for {user}...")
        log_event(
            event_type="WITHDRAWAL_INITIATED",
            severity="CRITICAL",
            user=user,
            ip=ip,
            details=f"High-value transfer of {amount} BTC initiated by {user}.",
            amount=amount,
            log_source="Application Logs"
        )
        time.sleep(1.5)

if __name__ == "__main__":
    run_simulation()
    print("Simulation Complete. Check Graylog for the new bars!")
