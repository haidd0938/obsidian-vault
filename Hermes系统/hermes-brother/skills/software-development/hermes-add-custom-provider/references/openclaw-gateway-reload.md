# OpenClaw Gateway Reload Pitfalls

## The Critical Discovery

**`openclaw stop` + `openclaw start` does NOT reload dist files.**

When you update OpenClaw's web UI dist files (via the "系统更新" button or by patching JS files), the Gateway process may continue serving from in-memory cached modules. This causes version mismatch errors like:

```
invalid chat.send params: at root: unexpected property 'sessionId'
```

even though the same Gateway version **accepts** `sessionId` in its schema.

## Root Cause

The OpenClaw Gateway process (launchd-managed) loads JavaScript modules into memory at startup. When dist files are replaced on disk:

- `openclaw stop` sends SIGTERM → launchd restarts the process **but with the same cached Node interpreter** (Homebrew node@22 at `/usr/local/Cellar/node@22/22.22.2/bin/node`)
- The new process **does** read the new dist files — BUT only if the dist files were already on disk before the restart
- **Race condition**: if dist files are being written during the restart sequence, the old files load

## The Fix

1. **Wait** for dist file update to fully complete (confirm via `ls -la` timestamps)
2. **Kill the Gateway process directly**:
   ```bash
   # Find the PID
   ps aux | grep openclaw-gateway | grep -v grep
   # Kill it (launchd auto-restarts)
   kill <PID>
   ```
3. **Verify** in gateway logs that the new files loaded:
   ```bash
   cat ~/.openclaw/logs/gateway.log | tail -20
   # Look for clean startup without sessionId/view errors
   ```
4. **Refresh browser** (Cmd+R) to reload Web UI from new server

## Symptom Pattern

| Time | Event |
|------|-------|
| T+0 | User clicks "系统更新" in Web UI |
| T+15s | Web UI reports update completed (may show error) |
| T+16s | dist files on disk are replaced (check timestamps) |
| T+17s | Web UI auto-reloads → connects to OLD Gateway process |
| T+18s | Gateway rejects requests because it has OLD schema loaded |
| T+20s | **Fix**: kill Gateway → launchd spawns new process → new dist files |

## Verification

After kill+restart, gateway logs should show:

```
2026-05-05T18:23:39+08:00 [gateway] loading configuration…
2026-05-05T18:23:43+08:00 [gateway] auto-enabled plugins: nvidia/..., ollama/...
2026-05-05T18:23:44+08:00 [gateway] ready
2026-05-05T18:23:46+08:00 [ws] webchat connected
2026-05-05T18:23:48+08:00 [ws] ⇄ res ✓ models.list ... ✓ chat.history ...
```

No more `invalid ... params` errors.

## Node Version Mismatch

The Gateway runs on Homebrew `node@22` (v22.22.2), **not** the system `node` (v23.11.0):

```bash
# System default
/usr/local/node23/bin/node    # v23.11.0

# Gateway's actual Node
/usr/local/Cellar/node@22/22.22.2/bin/node  # v22.22.2
```

This means Gateway has access to a different set of globally-installed packages. If you install packages for the system Node, they won't be visible to the Gateway process.
