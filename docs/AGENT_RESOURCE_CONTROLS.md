# Agent Resource Controls (OS-Specific)

Updated: 2025-01-05

## Goals
- Provide per-agent resource isolation, prioritization, and throttling across Linux, Windows, and macOS.
- Ensure resource actions are policy-driven and fully logged via the unified event journal.
- Detect freezes and apply automatic throttling without violating host stability.

## Common Invariants
- Every resource policy change emits RESOURCE_POLICY_APPLIED.
- Freeze detection emits FREEZE_DETECTED, then THROTTLE_APPLIED, then a recovery outcome.
- All actions include correlation_id and causation_id linking to the triggering intent.
- No kernel memory access or privileged writes outside agent partitions.

## Linux (Ubuntu/Debian)
Primary mechanism: systemd + cgroups v2.

Recommended approach:
- Run each agent under a dedicated systemd service or slice.
- Enforce memory and CPU policies via cgroups v2.
- Use IO limits where supported.

Example systemd unit snippet:
```
[Service]
ExecStart=/usr/local/bin/osdash-agent --agent-id=aic
Restart=always
MemoryMax=4G
CPUWeight=200
IOWeight=200
```

Notes:
- Use systemd-run for ad-hoc tasks if services are not yet defined.
- Prefer MemoryMax and MemoryHigh for hard and soft caps.
- IOReadBandwidthMax/IOWriteBandwidthMax can enforce disk limits on supported kernels.

## Windows 11
Primary mechanism: Job Objects + priority classes.

Recommended approach:
- Launch each agent inside a Job Object (via a small host/service).
- Set process priority class and memory limits per job.

Common controls:
- JOB_OBJECT_LIMIT_PROCESS_MEMORY
- JOB_OBJECT_LIMIT_JOB_MEMORY
- JOB_OBJECT_LIMIT_PRIORITY_CLASS
- JOB_OBJECT_LIMIT_ACTIVE_PROCESS

Notes:
- Memory limits require Win32 Job Object APIs; PowerShell alone is insufficient.
- Use a thin wrapper service to create and manage the job, then spawn the agent.

## macOS
Primary mechanism: launchd + taskpolicy/nice adjustments.

Recommended approach:
- Run each agent as a launchd service.
- Apply priority changes with nice/renice and taskpolicy.

Example launchd hints:
- Use Nice to set CPU scheduling priority.
- Use taskpolicy -b to background when throttled.
- Use HardResourceLimits where applicable (CPU and file limits).

Notes:
- macOS has limited enforcement for hard memory caps without a VM boundary.
- Prefer VM isolation if strict memory partitioning is required.

## Freeze Detection and Throttling
- Watchdog monitors heartbeat, CPU usage, and event loop liveness.
- On stall:
  - Emit FREEZE_DETECTED with process metadata and last action.
  - Apply throttle policy and emit THROTTLE_APPLIED.
  - Attempt recovery and emit RECOVERY_SUCCESS or RECOVERY_FAIL.
- On recovery, emit THROTTLE_RELEASED and restore baseline limits.

## Integration with Existing Components
- The memory daemon in `scripts/memory_resource_manager.py` can be used as a local-only watcher for macOS and Linux.
- All resource changes MUST use the unified EventEmitter and HubSink.

## Implementation Phases
1. Add per-OS service templates (systemd units, launchd plists, Windows job host).
2. Wire resource controls into AI OS policy engine.
3. Enable watchdog-based throttling with full event logging.
4. Add UI controls for policy overrides and audit history.

Service templates live in `scripts/services/`.
