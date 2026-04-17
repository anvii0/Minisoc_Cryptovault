# CryptoVault SOC Demo

This Flask app writes JSON audit logs to `cryptovault_audit.log`, forwards them to Wazuh over UDP syslog, and can also mirror them to Graylog on another laptop.

## 1. Install and run

```bash
python3 -m pip install flask
python3 cryptovault_app.py
```

Open `http://127.0.0.1:5000`.

Use these actions to generate security events:

- Failed login: any wrong password
- Successful login: `admin` / `secure123`
- Dashboard access: open `/dashboard`
- Withdrawal alert: submit the transfer form
- Recon event: open a fake path like `/admin-test`

## 2. Send logs to Wazuh

By default the app sends syslog UDP events to:

```bash
WAZUH_HOST=127.0.0.1
WAZUH_PORT=2514
```

If your Wazuh manager is mapped somewhere else, run:

```bash
WAZUH_HOST=<your-wazuh-ip> WAZUH_PORT=<your-wazuh-port> python3 cryptovault_app.py
```

## 3. Send logs to your friend's Graylog laptop

Ask your friend to create one of these Graylog inputs:

- Recommended: `GELF UDP` on port `12201`
- Alternate: `Syslog UDP` on a port they choose

Then start the app with their laptop IP.

For `GELF UDP`:

```bash
GRAYLOG_HOST=<friend-laptop-ip> GRAYLOG_PORT=12201 GRAYLOG_PROTOCOL=gelf-udp python3 cryptovault_app.py
```

For `Syslog UDP`:

```bash
GRAYLOG_HOST=<friend-laptop-ip> GRAYLOG_PORT=<their-syslog-port> GRAYLOG_PROTOCOL=syslog-udp python3 cryptovault_app.py
```

You can send to both Wazuh and Graylog at the same time:

```bash
WAZUH_HOST=127.0.0.1 WAZUH_PORT=2514 GRAYLOG_HOST=<friend-laptop-ip> GRAYLOG_PORT=12201 GRAYLOG_PROTOCOL=gelf-udp python3 cryptovault_app.py
```

## 4. What to look for

The app emits structured events with fields like:

- `event_type`
- `severity`
- `username`
- `source_ip`
- `details`

That makes it easy to filter in Wazuh and Graylog for:

- `LOGIN_FAILED`
- `LOGIN_SUCCESS`
- `PAGE_ACCESS`
- `WITHDRAWAL_INITIATED`
- `404_NOT_FOUND`
