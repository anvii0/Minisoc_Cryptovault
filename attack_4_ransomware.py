from siem_logger import log_event
import time

def run_simulation():
    print("--- STAGE 4: RANSOMWARE ---")
    
    files = ["financials.xlsx", "client_database.db", "legal_docs.pdf", "backup_config.xml"]
    for file_name in files:
        log_event(
            event_type="file_modification",
            severity="CRITICAL",
            user="admin_svc",
            ip="10.0.0.5",
            details=f"Process encryptor.exe modified {file_name} -> {file_name}.locked",
            file_extension=".locked",
            file_path=f"C:\\Users\\Admin\\Documents\\{file_name}.locked"
        )
        time.sleep(1)

if __name__ == "__main__":
    run_simulation()
    print("Simulation Complete.")
