#!/bin/bash
# Apply custom rules
docker cp wazuh_custom_rules.xml single-node-wazuh.manager-1:/var/ossec/etc/rules/local_rules.xml
docker exec -u 0 single-node-wazuh.manager-1 chown wazuh:wazuh /var/ossec/etc/rules/local_rules.xml
docker exec -u 0 single-node-wazuh.manager-1 chmod 660 /var/ossec/etc/rules/local_rules.xml

# Check if syslog remote already exists
if ! docker exec -u 0 single-node-wazuh.manager-1 grep -q "<connection>syslog</connection>" /var/ossec/etc/ossec.conf; then
  # Inject before the first <remote>
  docker exec -u 0 single-node-wazuh.manager-1 sed -i.bak '0,/<remote>/{s|<remote>|  <remote>\n    <connection>syslog</connection>\n    <port>514</port>\n    <protocol>udp</protocol>\n    <allowed-ips>172.16.0.0/12</allowed-ips>\n    <allowed-ips>192.168.0.0/16</allowed-ips>\n    <allowed-ips>10.0.0.0/8</allowed-ips>\n    <allowed-ips>127.0.0.0/8</allowed-ips>\n  </remote>\n\n  <remote>|}' /var/ossec/etc/ossec.conf
fi

# Restart Wazuh
echo "Restarting Wazuh Manager..."
docker exec -u 0 single-node-wazuh.manager-1 /var/ossec/bin/wazuh-control restart
