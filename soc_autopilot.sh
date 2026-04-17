#!/bin/bash
echo "================================================="
echo "🚀 INITIATING CRYPTOVAULT SOC INFRASTRUCTURE"
echo "================================================="

echo "[1/4] 🧠 Applying Mac Memory Patch for OpenSearch..."
docker run --rm --privileged alpine sysctl -w vm.max_map_count=262144

echo "[2/4] 🛡️ Booting Wazuh Manager..."
cd ~/wazuh-docker/single-node
docker compose up -d

echo "[3/4] 🪚 Optimizing RAM (Killing Wazuh Indexer & Dashboard)..."
docker stop single-node-wazuh.indexer-1 single-node-wazuh.dashboard-1

echo "[4/4] 👁️ Booting Graylog SIEM..."
cd ~/graylog-docker
docker compose up -d

echo "================================================="
echo "✅ INFRASTRUCTURE ONLINE!"
echo "⚠️ Please wait exactly 2 minutes for OpenSearch to warm up."
echo "Access Graylog at: http://localhost:9000"
echo "================================================="
