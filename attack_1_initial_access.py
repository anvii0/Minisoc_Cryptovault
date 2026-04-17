from siem_logger import log_event
import time

def run_simulation():
    print("--- STAGE 1: INITIAL ACCESS ---")
    
    # PowerShell Execution
    log_event(
        event_type="process_creation",
        severity="WARNING",
        user="john_doe",
        ip="192.168.1.50",
        details="powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -EncodedCommand SUVYIChOZXctT2JqZWN0IE5ldC5XZWJDbGllbnQpLkRv...",
        process_name="powershell.exe",
        command_line="powershell.exe -ep bypass -Enc SUVYIChOZXctT2JqZWN0IE5ldC5XZWJDbGllbnQpLkRv..."
    )
    time.sleep(2)
    
    # Rundll32 Execution
    log_event(
        event_type="process_creation",
        severity="WARNING",
        user="admin",
        ip="192.168.1.50",
        details="rundll32.exe C:\\Windows\\Temp\\update.dll,Exploit",
        process_name="rundll32.exe",
        command_line="rundll32.exe C:\\Windows\\Temp\\update.dll,Exploit"
    )

if __name__ == "__main__":
    run_simulation()
    print("Simulation Complete.")
