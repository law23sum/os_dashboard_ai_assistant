# Memory Resource Manager - Quick Start Guide

## 🚀 30-Second Setup

```bash
# 1. Start the daemon
./scripts/launch_memory_manager.sh start

# 2. Check it's running
./scripts/launch_memory_manager.sh status

# 3. View logs
tail -f logs/memory_manager.log
```

## 📋 Common Commands

```bash
# Start daemon
./scripts/launch_memory_manager.sh start

# Stop daemon
./scripts/launch_memory_manager.sh stop

# Restart daemon
./scripts/launch_memory_manager.sh restart

# Check status
./scripts/launch_memory_manager.sh status

# Run in foreground (for debugging)
./scripts/launch_memory_manager.sh foreground
```

## ⚙️ Quick Configuration

Edit `config/memory_manager_config.json`:

```json
{
  "memory_threshold": 85.0,        // When to start throttling (%)
  "inactivity_threshold": 300,      // Seconds before aggressive throttling
  "min_memory_mb": 100              // Only track processes using >100MB
}
```

## 🔍 Monitoring

```bash
# View current state
cat logs/memory_manager_state.json | jq '.'

# Watch logs in real-time
tail -f logs/memory_manager.log

# Check which processes are throttled
cat logs/memory_manager_state.json | jq '.processes | to_entries | map(select(.value.state == "throttled"))'
```

## 🎯 What It Does

1. **Monitors** all processes using >100MB RAM
2. **Detects** O(2^n) and O(n^2) memory growth patterns
3. **Throttles** heavy processes when:
   - Memory usage > 85%
   - User inactive > 5 minutes
   - Process has exponential/quadratic complexity
4. **Suspends** processes when memory > 90% and user inactive

## 🛡️ Whitelist/Blacklist

Add processes to never throttle (whitelist) or always throttle (blacklist):

```json
{
  "whitelist": ["kernel_task", "WindowServer"],
  "blacklist": ["com.apple.WebKit.Networking"]
}
```

## 🐛 Troubleshooting

**Daemon won't start?**
```bash
# Check dependencies
python3 -c "import psutil" || pip install psutil

# Run in foreground to see errors
./scripts/launch_memory_manager.sh foreground
```

**Processes not being throttled?**
- Check if whitelisted
- Verify memory > min_memory_mb (100MB default)
- Check system memory > memory_threshold (85% default)

**Need more aggressive throttling?**
- Lower `memory_threshold` (e.g., 80.0)
- Lower `inactivity_threshold` (e.g., 180 seconds)

## 📊 Understanding Output

When a process is throttled, you'll see:
```
INFO - Throttled Chrome (PID 12345) to 30% - Score: 75.2, Complexity: O(n^2)
```

- **Score**: 0-100, higher = more problematic
- **Complexity**: O(n), O(n^2), O(2^n), etc.
- **Throttle Level**: % of resources allocated

## 🔗 Full Documentation

See `docs/MEMORY_RESOURCE_MANAGER.md` for complete documentation.


