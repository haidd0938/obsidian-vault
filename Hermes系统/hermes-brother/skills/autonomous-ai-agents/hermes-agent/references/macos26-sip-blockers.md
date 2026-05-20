# macOS 26 SIP Blockers — Debugging Notes

macOS 26 (Sequoia) introduced significantly stricter System Integrity Protection (SIP). Several common debugging and system-access techniques no longer work.

## Observed Failures (macOS 26.4.1)

| Technique | Error | Root Cause |
|-----------|-------|------------|
| `codesign --force --deep --sign -` | `Operation not permitted in subcomponent: WeChatAppEx.app` | macOS 26 blocks re-signing Application Extensions without developer ID |
| `codesign --remove-signature` on subcomponent | `internal error in Code Signing subsystem` | System-protected component, removal denied |
| `sudo wx init` (task_for_pid) | `task_for_pid failed (kr=5)` | SIP blocks cross-process memory access even as root |
| `lldb -n WeChat attach` | `attach failed (Not allowed to attach to process)` | lldb debugserver denied by SIP |
| `pip3 install pysqlcipher3` | Build failure — no wheel | New macOS lacks precompiled wheels for sqlcipher bindings |
| `pip3 install sqlcipher3-binary` | `No matching distribution found` | No binary wheels for macOS 26 |

## What Still Works

- **brew install sqlcipher** ✅ — Bottle available for macOS 26
- Direct `sqlcipher` CLI tool ✅ — Can decrypt SQLCipher databases IF you have the key
- **MMKV inspection** ✅ — `strings *.mmkv` works on MMKV cache files
- **Manual Python memory scanning (via mmap)** ❌ — `task_for_pid` blocked

## Workaround Chain for wx-cli / WeChat DB Access

1. **First try**: `codesign --force --deep --sign - /Applications/WeChat.app` + `sudo wx init`
   - Fails on macOS 26 due to WeChatAppEx.app subcomponent

2. **Second try**: `sudo wx init --key <db_storage_path>` (if supported by version)
   - Not supported in v0.1.10

3. **Third try**: Extract key from MMKV files in data directory
   - `strings f2641700tinfo.mmkv | grep -E "^[0-9a-f]{64}$"` — unlikely to work

4. **Fourth try**: Install sqlcipher via brew, use interactive CLI to open DB with password
   - `brew install sqlcipher` ✅ works on macOS 26
   - WeChat encryption uses PBKDF2-HMAC-SHA1 with specific salt + iteration count
   - Password alone is NOT the key — needs proper derivation

5. **Ultimate**: Disable SIP temporarily
   - Restart → Cmd+R → Terminal → `csrutil disable` → Restart
   - Then everything (codesign, task_for_pid, lldb) works
   - Re-enable after init: `csrutil enable`

## Summary

macOS 26 significantly hardened userland process isolation. Tools that rely on `task_for_pid` (memory scanning of other processes) or `codesign --deep` (re-signing apps with subcomponents) will fail. The only reliable workaround is disabling SIP temporarily or waiting for tool authors to adapt.
