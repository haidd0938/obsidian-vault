---
name: hermes-web-ui-setup
description: Install, build, and launch Hermes Agent's built-in Web Dashboard (FastAPI + Vite/React frontend on port 9119).
category: software-development
---

# Hermes Web UI Setup

Install dependencies and launch the Hermes Web Dashboard at `http://127.0.0.1:9119`.

## Steps

### 1. Install Python deps

```bash
cd ~/.hermes  # or your HERMES_HOME
source hermes-agent/venv/bin/activate
pip install 'fastapi' 'uvicorn[standard]'
```

### 2. Build the frontend (Vite/React)

```bash
cd hermes-agent/web
npm install            # skip --ignore-scripts, need full install for @nous-research/ui dist
npm run build          # outputs to ../hermes_cli/web_dist/
```

**Known issues:**
- First `npm run build` may fail with `cp: node_modules/@nous-research/ui/dist/fonts: No such file or directory`. Run `npm install` (without `--ignore-scripts`) to ensure the `dist/` directory exists.
- The `web/node_modules/` directory may sometimes vanish after a failed build — just re-run `npm install`.

### 3. Launch

```bash
# Option A: let cmd_dashboard auto-build (use HERMES_WEB_DIST to skip rebuild)
HERMES_WEB_DIST=~/hermes-agent/hermes_cli/web_dist hermes dashboard --no-open

# Option B: if web_dist already exists, skip the build entirely
cd ~/.hermes && source hermes-agent/venv/bin/activate && \
  HERMES_WEB_DIST=$PWD/hermes-agent/hermes_cli/web_dist hermes dashboard --no-open
```

The server starts on `http://127.0.0.1:9119`.

### 4. Verify

```bash
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:9119/
# Should return 200
```

### 5. Background it (for long-running)

```bash
cd ~/.hermes
source hermes-agent/venv/bin/activate
HERMES_WEB_DIST=$PWD/hermes-agent/hermes_cli/web_dist nohup hermes dashboard --no-open > web-ui.log 2>&1 &
```

## Pitfalls

- `hermes web` is **not a valid command**. The correct command is `hermes dashboard`.
- The dashboard runs on port **9119**, not 8648 (the API server port).
- `hermes dashboard --no-open` may seem to hang or produce no output — it's running uvicorn, check with `curl http://127.0.0.1:9119/`.
- The frontend has a Chinese language toggle in the top-right corner of the UI.
- If you see "Web UI dependencies not installed", it means fastapi/uvicorn are missing — pip install them.
- Web UI shows gateway status, sessions, logs, cron, skills, config, and API keys. It's a management dashboard, not a chat interface per se — but it pairs with the API server on port 8642.
