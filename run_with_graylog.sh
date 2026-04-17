#!/bin/bash
# run_with_graylog.sh — Start CryptoVault with Graylog + Wazuh forwarding
# Graylog UI: http://127.0.0.1:9000  (admin / admin)
# GELF UDP input on port 12201 (already created automatically)

cd "$(dirname "$0")"

echo "Starting Graylog stack (if not already running)..."
docker compose -f docker-compose-graylog.yml up -d

echo "Waiting for Graylog to be ready..."
for i in $(seq 1 20); do
  CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:9000/api/)
  [ "$CODE" = "200" ] && break
  echo "  ($i/20) Graylog not ready yet..."
  sleep 5
done

echo ""
echo "============================================"
echo "  Graylog UI: http://127.0.0.1:9000"
echo "  Login: admin / admin"
echo "  Go to: Search (top menu) to see live logs"
echo "============================================"
echo ""

# Start CryptoVault forwarding to both Wazuh and Graylog (local)
source .venv/bin/activate 2>/dev/null || true
GRAYLOG_HOST=127.0.0.1 \
GRAYLOG_PORT=12201 \
GRAYLOG_PROTOCOL=gelf-udp \
WAZUH_HOST=127.0.0.1 \
WAZUH_PORT=514 \
CRYPTOVAULT_PORT=5001 \
python3 cryptovault_app.py
