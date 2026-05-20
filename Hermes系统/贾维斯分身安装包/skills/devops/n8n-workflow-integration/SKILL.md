---
name: n8n-workflow-integration
title: Trigger and Manage n8n Workflows from Hermes
description: Integration skill for triggering n8n workflows via webhooks, creating new workflows, and managing n8n from Hermes CLI
tags: [n8n, automation, webhook, integration, hermesskill]
version: 1.0
author: Jarvis
created: 2026-04-19
last_modified: 2026-04-19
---

# n8n Workflow Integration

Trigger n8n workflows from Hermes via webhooks, creating a seamless integration between your AI assistant and automation platform.

## Prerequisites

- n8n running locally at `http://localhost:5678`
- Basic understanding of n8n workflows
- Hermes with terminal tool access

## Core Concepts

n8n exposes webhook nodes that can be triggered via HTTP POST requests. This skill enables Hermes to:
1. Trigger existing n8n workflows
2. Create simple workflows programmatically
3. Monitor workflow execution
4. Integrate n8n automation into Hermes skills

## Basic Usage

### 1. Trigger an Existing n8n Webhook

```bash
# Get webhook URL from n8n workflow
WEBHOOK_URL="http://localhost:5678/webhook/workflow-id"

# Trigger via curl
curl -X POST "$WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{"task": "process document", "priority": "high"}'
```

### 2. Create a Simple Hermes Wrapper Function

Add to your shell configuration (`~/.bashrc` or `~/.zshrc`):

```bash
# Trigger n8n workflow
n8n-trigger() {
  local workflow_id="$1"
  local data="${2:-'{}'}"
  local url="http://localhost:5678/webhook/$workflow_id"
  
  curl -X POST "$url" \
    -H "Content-Type: application/json" \
    -d "$data"
  
  echo ""
}
```

### 3. Hermes Skill Implementation

When building Hermes skills that integrate with n8n:

```python
# Example from hermes_tools import
from hermes_tools import terminal

def trigger_n8n_workflow(workflow_id, payload):
    cmd = f'''curl -X POST "http://localhost:5678/webhook/{workflow_id}" \
      -H "Content-Type: application/json" \
      -d '{payload}' 2>/dev/null'''
    
    result = terminal(cmd)
    return result.get("output", "")
```

## Example Workflows

### 1. Notification Workflow

Create an n8n workflow that:
- Webhook node (HTTP trigger)
- Email/SMS/Telegram node for notification
- Responds with confirmation

**Hermes trigger:**
```bash
n8n-trigger "notify" '{"message": "Task completed", "channel": "telegram"}'
```

### 2. Document Processing Workflow

Create an n8n workflow that:
- Webhook node receives document path
- Python node processes document
- Stores result in database
- Returns processing status

**Hermes trigger:**
```bash
n8n-trigger "process-doc" '{"path": "/path/to/document.pdf", "action": "extract"}'
```

### 3. Data Collection Workflow

Create an n8n workflow that:
- Webhook node triggers data collection
- HTTP Request nodes fetch from APIs
- Transform and store data
- Return summary

**Hermes trigger:**
```bash
n8n-trigger "collect-data" '{"sources": ["weather", "news"], "format": "json"}'
```

## Advanced Integration

### 1. Dynamic Workflow Creation

Create workflows programmatically using n8n's REST API:

```bash
# Get n8n API key from settings
API_KEY="your-n8n-api-key"

# Create a simple workflow
curl -X POST "http://localhost:5678/api/v1/workflows" \
  -H "X-N8N-API-KEY: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Hermes Automation",
    "nodes": [
      {
        "name": "Webhook",
        "type": "n8n-nodes-base.webhook",
        "position": [250, 300],
        "parameters": {"path": "hermes-webhook"}
      }
    ]
  }'
```

### 2. Workflow Status Monitoring

```bash
# Check active workflows
curl -s "http://localhost:5678/api/v1/workflows" \
  -H "X-N8N-API-KEY: $API_KEY" | jq '.data[] | .name'
```

### 3. Hermes ↔ n8n Bidirectional Communication

1. **Hermes → n8n**: Webhook triggers
2. **n8n → Hermes**: Use Hermes API server (port 8648) or Telegram bot

## Troubleshooting

### Common Issues

1. **Webhook not found**: Ensure workflow is active in n8n
2. **Connection refused**: Check if n8n is running (`n8n-start`)
3. **Authentication errors**: Set up n8n API key in settings
4. **CORS issues**: Configure n8n CORS settings if accessing from different domain

### Debug Steps

```bash
# 1. Check n8n status
docker ps | grep n8n

# 2. Test connectivity
curl -I http://localhost:5678

# 3. List active webhooks
# Visit http://localhost:5678 and check workflow activation
```

## Best Practices

1. **Idempotent operations**: Design workflows to handle duplicate triggers
2. **Error handling**: Include error nodes in n8n workflows
3. **Logging**: Log all Hermes → n8n interactions
4. **Security**: Use n8n API keys for production workflows
5. **Backup**: Export n8n workflows regularly

## Related Skills

- `n8n-standalone-docker-deployment` - Deploy n8n
- `webhook-subscriptions` - Manage webhook triggers
- `telegram-integration-configuration` - Notify via Telegram

## References

- [n8n Documentation](https://docs.n8n.io/)
- [n8n REST API](https://docs.n8n.io/api/api-reference/)
- [Hermes API Server](/api/v1)