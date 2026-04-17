#!/usr/bin/env python3

import sys
import json
import socket

# Configuration
GRAYLOG_HOST = '192.168.0.103'
GRAYLOG_PORT = 1514

# Read input (from Wazuh)
try:
    with open(sys.argv[1], 'r') as f:
        alert = json.load(f)
except Exception:
    sys.exit(0)

# Create Syslog message
message = f"WAZUH_ALERT: {json.dumps(alert)}\n"

# Send via UDP
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(message.encode(), (GRAYLOG_HOST, GRAYLOG_PORT))
    sock.close()
except Exception:
    pass
