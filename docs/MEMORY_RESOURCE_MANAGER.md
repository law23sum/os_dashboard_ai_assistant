# Memory Resource Manager

An intelligent daemon that monitors system memory and automatically reduces resource allocation for processes with exponential (O(2^n)) or quadratic (O(n^2)) memory growth patterns, especially after user inactivity periods.

## Features

- **Real-time Memory Monitoring**: Continuously tracks system memory usage and individual process consumption
- **Complexity Pattern Detection**: Automatically identifies processes with O(2^n), O(n^2), or other high-complexity memory growth patterns
- **User Activity Detection**: Monitors user activity and adjusts resource allocation accordingly
- **Automatic Resource Throttling**: Reduces CPU and I/O resources for problematic processes
- **Process Suspension**: Can suspend processes when memory pressure is high and user is inactive
- **AI-Powered Decisions** (Optional): Uses AI to make intelligent resource allocation decisions
- **Configurable Policies**: Highly configurable thresholds and policies

## Quick Start

### Basic Usage

```bash
# Start the daemon
./scripts/launch_memory_manager.sh start

# Check status
./scripts/launch_memory_manager.sh status

# Stop the daemon
./scripts/launch_memory_manager.sh stop

# Run in foreground (for debugging)
./scripts/launch_memory_manager.sh foreground
```

### Direct Python Execution

```bash
# Run with default settings
python scripts/memory_resource_manager.py

# Run with custom config
python scripts/memory_resource_manager.py --config config/memory_manager_config.json

# Run with custom thresholds
python scripts/memory_resource_manager.py \
    --memory-threshold 90.0 \
    --inactivity-threshold 600 \
    --log-level DEBUG
```

## How It Works

### 1. Process Monitoring

The daemon continuously scans all running processes and tracks:
- Memory usage (RSS, percentage of system memory)
- CPU usage
- Memory growth patterns over time
- Process state (active, throttled, suspended)

### 2. Complexity Analysis

For each process, the system analyzes memory growth patterns to classify complexity:

- **O(n) - Linear**: Constant growth rate
- **O(n^2) - Quadratic**: Growth rate increases linearly
- **O(2^n) - Exponential**: Growth rate increases exponentially
- **O(n!) - Factorial**: Extremely rapid growth (rare)

The analyzer uses statistical methods to detect these patterns from memory history.

### 3. User Activity Detection

The system detects user activity through:
- **macOS**: Quartz event system (keyboard/mouse activity)
- **Fallback**: Active process detection (monitors interactive applications)

When user inactivity exceeds the threshold, the system becomes more aggressive in resource management.

### 4. Resource Management Decisions

The system makes decisions based on:

1. **Memory Pressure**: System memory usage above threshold
2. **User Activity**: Whether user is currently active
3. **Process Complexity**: O(2^n) processes get more aggressive throttling
4. **Memory Score**: Calculated score indicating how problematic a process is

### 5. Throttling Mechanisms

When a process is throttled:
- **CPU Priority**: Nice value is increased (lower priority)
- **CPU Affinity**: Limited to fewer CPU cores
- **I/O Priority**: Reduced I/O bandwidth (where supported)

Throttle levels:
- **0.1 (10%)**: Extreme throttling for O(2^n) processes
- **0.3 (30%)**: Heavy throttling for O(n^2) processes
- **0.5-0.7 (50-70%)**: Moderate throttling for other high-memory processes

## Configuration

Edit `config/memory_manager_config.json`:

```json
{
  "memory_threshold": 85.0,          // Memory usage % to trigger actions
  "inactivity_threshold": 300,        // Seconds of inactivity before aggressive management
  "monitor_interval": 5,              // Seconds between monitoring cycles
  "min_memory_mb": 100,               // Minimum memory (MB) to track a process
  "history_size": 20,                  // Number of memory samples to keep
  "whitelist": [                       // Processes to never throttle
    "kernel_task",
    "WindowServer"
  ],
  "blacklist": [                       // Processes to always throttle when memory high
    "com.apple.WebKit.Networking"
  ]
}
```

## AI-Enhanced Decision Making (Optional)

Enable AI-powered decision making by:

1. Set `OPENAI_API_KEY` environment variable
2. Enable in config:

```json
{
  "ai_decision_making": {
    "enabled": true,
    "model": "gpt-4",
    "temperature": 0.3,
    "max_tokens": 500
  }
}
```

The AI engine analyzes process and system context to make intelligent decisions about resource allocation, considering:
- Process importance
- User impact
- Memory complexity patterns
- System state

## Monitoring and Logs

### Log Files

- **Main Log**: `logs/memory_manager.log`
- **State File**: `logs/memory_manager_state.json`
- **Output**: `logs/memory_manager.out` (when run as daemon)

### State File

The state file contains:
- Current system metrics
- All tracked processes with their metrics
- Statistics (processes throttled, suspended, etc.)

View current state:
```bash
cat logs/memory_manager_state.json | jq '.'
```

### Real-time Monitoring

Watch the log file:
```bash
tail -f logs/memory_manager.log
```

## Process States

- **ACTIVE**: Process running with full resources
- **THROTTLED**: Process running with reduced resources
- **SUSPENDED**: Process paused (not executing)
- **TERMINATED**: Process has been killed (last resort)

## Throttling Policies

The system applies different throttling levels based on:

1. **Complexity Level**:
   - O(2^n): 10% resources
   - O(n^2): 30% resources
   - O(n): 50-70% resources

2. **Memory Pressure**:
   - High pressure (>85%): More aggressive throttling
   - Normal pressure: Light throttling only for high-complexity processes

3. **User Activity**:
   - User active: Conservative throttling
   - User inactive: Aggressive throttling

## Suspension Policy

Processes can be suspended when:
- User inactive for > 10 minutes
- System memory > 90%
- Process has high memory score
- Process has been throttled for extended period

Suspended processes are automatically resumed when:
- User becomes active
- System memory pressure decreases
- Process is needed

## Troubleshooting

### Daemon Won't Start

1. Check Python version: `python3 --version` (requires 3.8+)
2. Install dependencies: `pip install psutil`
3. Check logs: `cat logs/memory_manager.out`
4. Try foreground mode: `./scripts/launch_memory_manager.sh foreground`

### Processes Not Being Throttled

1. Check if process is whitelisted in config
2. Verify process memory exceeds `min_memory_mb` threshold
3. Check if system memory is above `memory_threshold`
4. Review logs for access denied errors (may need sudo)

### High CPU Usage from Daemon

1. Increase `monitor_interval` in config (default: 5 seconds)
2. Increase `min_memory_mb` to track fewer processes
3. Reduce `history_size` to use less memory

### Permission Errors

Some operations require elevated privileges:
- Setting CPU affinity
- Suspending/resuming processes
- Terminating processes

The daemon will log warnings but continue operating with reduced capabilities.

## Integration

### With Existing Monitoring

The Memory Resource Manager can integrate with existing monitoring systems:

```python
from scripts.memory_resource_manager import MemoryResourceManager, load_config

config = load_config('config/memory_manager_config.json')
manager = MemoryResourceManager(config)

# Get current system metrics
system_metrics = manager.get_system_metrics()
print(f"Memory usage: {system_metrics.memory_percent:.1f}%")

# Get process metrics
manager.scan_processes()
for pid, metrics in manager.processes.items():
    if metrics.complexity.value in ['O(2^n)', 'O(n^2)']:
        print(f"{metrics.name}: {metrics.complexity.value}")
```

### With AI Decision Engine

```python
from scripts.ai_memory_decision_engine import AIMemoryDecisionEngine, ProcessContext, SystemContext

engine = AIMemoryDecisionEngine(config)
decision = engine.analyze_with_ai(process_context, system_context)
print(decision)
```

## Performance Considerations

- **Monitoring Overhead**: ~1-2% CPU usage for monitoring
- **Memory Overhead**: ~50-100 MB for daemon and state
- **I/O Impact**: Minimal (writes state file every 5 seconds)
- **Network**: None (unless AI features enabled)

## Security Considerations

- The daemon requires access to process information (psutil)
- Some operations may require elevated privileges
- State files contain process information (keep secure)
- AI features require API key (store securely)

## Best Practices

1. **Whitelist Critical Processes**: Add system-critical processes to whitelist
2. **Monitor Logs**: Regularly check logs for issues
3. **Adjust Thresholds**: Tune thresholds based on your system
4. **Test First**: Run in foreground mode before deploying as daemon
5. **Backup State**: Keep backups of state files for analysis

## Limitations

- Cannot throttle processes that require root privileges (without sudo)
- Some processes may not respond to throttling (system processes)
- Suspension may cause data loss in unsaved applications
- Complexity detection requires sufficient history (5+ samples)

## Future Enhancements

- Machine learning for better complexity detection
- Predictive memory management
- Integration with system monitoring tools
- Web dashboard for visualization
- Process grouping and coordinated management
- Custom policies per application

## License

Part of the OS Dashboard AI Assistant project.

## Support

For issues or questions:
1. Check logs in `logs/memory_manager.log`
2. Review this documentation
3. Run in foreground mode with DEBUG logging
4. Open an issue in the repository


