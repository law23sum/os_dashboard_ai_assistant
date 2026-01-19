# Agent Service Templates

These templates wire AI OS agents into the host service manager so they stay running with defined resource policies.

## systemd (Linux)
- Template: `systemd/osdash-agent@.service`
- Example:
  - Copy to `/etc/systemd/system/osdash-agent@.service`
  - `sudo systemctl daemon-reload`
  - `sudo systemctl enable --now osdash-agent@AIC`

## launchd (macOS)
- Template: `launchd/com.osdashboard.agent.plist`
- Example:
  - Copy to `~/Library/LaunchAgents/com.osdashboard.agent.plist`
  - `launchctl load ~/Library/LaunchAgents/com.osdashboard.agent.plist`

## Windows Job Object wrapper
- Script: `windows/osdash_agent_job.ps1`
- Example:
  - `powershell -ExecutionPolicy Bypass -File .\osdash_agent_job.ps1 -AgentId AIC -RepoRoot C:\OSDashboardAI`

Notes
- Update `RepoRoot`, agent id, and log paths before use.
- Resource limits are defaults; tune them per host and workload.
