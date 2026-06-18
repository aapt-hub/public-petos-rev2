---
title: "Ops-Agent-v1 Operational Guide"
description: "The primary operational and configuration guide for the Ops-Agent-v1, our core infrastructure monitoring and telemetry agent."
tags:
  - agent
  - monitoring
  - observability
  - operations
---

# Ops-Agent-v1 Operational & Configuration Guide

This document is the single source of truth for deploying, configuring, and troubleshooting the `Ops-Agent-v1` monitoring agent.

## 1. Executive Summary & Ownership

The `Ops-Agent-v1` is a lightweight agent responsible for collecting system metrics, logs, and application traces from all production and non-production hosts. It securely forwards this telemetry to our central observability platform.

*   **Business Impact:** Provides the critical data required for incident response, performance analysis, and capacity planning. Downtime or misconfiguration of this agent directly impacts our ability to monitor system health.
*   **Tech Stack Owners:** `@your-org/operations-team`
*   **Support Channels:** `#ops-monitoring` (Slack), `ops-team@example.com` (Email)

## 2. Data Flow & Security Architecture

The agent initiates all connections outbound. No ingress ports are required on the host server. All communication occurs over HTTPS (TLS 1.2+).

!!! danger "Firewall & Network Rules"
    The agent requires outbound access to the following endpoints. Ensure firewall rules permit this traffic.

    *   **Metrics Endpoint:** `https://{{ env.METRICS_INGEST_HOSTNAME }}:443`
    *   **Logs Endpoint:** `https://{{ env.LOGS_INGEST_HOSTNAME }}:443`
    *   **Traces Endpoint:** `https://{{ env.TRACES_INGEST_HOSTNAME }}:443`

The agent authenticates using a unique API key provided during installation. See the configuration matrix for details.

## 3. Configuration Matrix & Variable Map

Configuration is managed via environment variables. Our validation scripts parse these variables to ensure compliance.

| Variable / Secret            | Type   | Scope       | Description & Validation Rule                                  |
| ---------------------------- | ------ | ----------- | -------------------------------------------------------------- |
| `{{ env.AGENT_API_KEY }}`    | Secret | Environment | **Required.** 32-character alphanumeric key for authentication.  |
| `{{ env.AGENT_LOG_LEVEL }}`  | Var    | Environment | **Optional.** Log verbosity. Must be one of: `INFO`, `WARN`, `ERROR`. Default: `INFO`. |
| `{{ env.AGENT_HOSTNAME }}`   | Var    | Environment | **Optional.** Overrides the system hostname. Must be a valid FQDN. |
| `{{ env.METRICS_INGEST_HOSTNAME }}` | Var | Environment | **Required.** The hostname for the metrics ingest endpoint. |
| `{{ env.LOGS_INGEST_HOSTNAME }}` | Var | Environment | **Required.** The hostname for the logs ingest endpoint. |
| `{{ env.TRACES_INGEST_HOSTNAME }}` | Var | Environment | **Required.** The hostname for the traces ingest endpoint. |

## 4. Deployment Runbook

These steps are idempotent and can be re-run safely. The script will download the latest binary, configure the service, and start it.

```bash
#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status.

echo ">>> [1/4] Configuring environment variables..."

# Create the environment file for the systemd service
cat << EOF > /etc/ops-agent/config.env
AGENT_API_KEY={{ env.AGENT_API_KEY }}
AGENT_LOG_LEVEL=INFO
METRICS_INGEST_HOSTNAME={{ env.METRICS_INGEST_HOSTNAME }}
LOGS_INGEST_HOSTNAME={{ env.LOGS_INGEST_HOSTNAME }}
TRACES_INGEST_HOSTNAME={{ env.TRACES_INGEST_HOSTNAME }}
EOF

echo ">>> [2/4] Downloading agent binary..."
curl -sSL "https://{{ env.ARTIFACT_REPO_URL }}/ops-agent-v1/latest/ops-agent" -o /usr/local/bin/ops-agent || { echo "ERROR: Failed to download agent binary."; exit 1; }
chmod +x /usr/local/bin/ops-agent

echo ">>> [3/4] Creating systemd service..."
cat << EOF > /etc/systemd/system/ops-agent.service
[Unit]
Description=Ops-Agent-v1 Monitoring Service
After=network-online.target

[Service]
Type=simple
User=root
Group=root
EnvironmentFile=/etc/ops-agent/config.env
ExecStart=/usr/local/bin/ops-agent
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

echo ">>> [4/4] Enabling and starting the service..."
systemctl daemon-reload
systemctl enable ops-agent.service
systemctl start ops-agent.service

echo ">>> Deployment complete. Verifying status..."
systemctl status ops-agent.service --no-pager
```

## 5. Runtime Sanity & Health Checks

Use these commands to verify the agent is running correctly on the host.

**Check the service status:**
```bash
# The service should be 'active (running)'
systemctl status ops-agent.service
```

**Inspect the latest logs for errors:**
```bash
# Look for any lines containing 'ERROR' or 'WARN'
journalctl -u ops-agent.service -n 50 --no-pager
```

**Query the local health check endpoint:**

!!! info
    The agent exposes a local-only HTTP endpoint for health checks. It is not exposed to the network.

```bash
# This command should return an HTTP 200 OK with a JSON body
curl -s http://127.0.0.1:9090/health
```

**Expected Output:**
```json
{
  "status": "ok",
  "version": "1.0.0",
  "checks": {
    "telemetry_connection": "connected"
  }
}
```

## 6. Troubleshooting & Incident Resolution

??? failure "Failure Mode: Agent service is not running"

    **Symptom:** `systemctl status ops-agent.service` shows `inactive (dead)` or `failed`.

    1.  **Check Logs:** Run `journalctl -u ops-agent.service` to find the specific error message.
    2.  **Validate Config:** Run `cat /etc/ops-agent/config.env` to ensure all required variables are present and correctly formatted.
    3.  **Check Binary:** Run `ls -l /usr/local/bin/ops-agent` to ensure the binary exists and is executable.

??? danger "Failure Mode: HTTP 401 Unauthorized"

    **Symptom:** Logs contain messages like `Failed to send telemetry: server responded with status 401`.

    1.  **Verify API Key:** The `{{ env.AGENT_API_KEY }}` is incorrect, expired, or has been revoked.
    2.  **Action:** Obtain a new, valid API key from the observability platform and update it in `/etc/ops-agent/config.env`.
    3.  **Restart:** Run `systemctl restart ops-agent.service`.

??? warning "Failure Mode: High CPU Utilization"

    **Symptom:** The `ops-agent` process is consuming an unexpectedly high amount of CPU.

    1.  **Enable Debug Logging:** Edit `/etc/ops-agent/config.env`, set `AGENT_LOG_LEVEL=DEBUG`, and restart the service.
    2.  **Inspect Logs:** Check the debug logs for indications of rapid event processing or tight loops.
    3.  **Contact Support:** If the cause is not obvious, open a ticket in `#ops-monitoring` with the debug logs attached.