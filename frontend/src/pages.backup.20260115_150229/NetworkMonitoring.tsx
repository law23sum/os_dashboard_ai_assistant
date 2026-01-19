import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { 
  Network, 
  RefreshCw, 
  Shield, 
  AlertTriangle, 
  Wifi, 
  Activity, 
  Users, 
  Server,
  CheckCircle,
  XCircle,
  Clock,
  HardDrive,
  Settings,
  Plus,
  Ban,
  Check,
  X,
  Save,
  Edit,
  Lightbulb,
  ChevronDown,
  ChevronUp,
  Info
} from 'lucide-react'
import apiClient, { apiPath } from '../lib/apiClient'
import { toast } from '../utils/toast'

interface NetworkDevice {
  ip: string
  mac: string
  hostname?: string
  interface: string
  is_suspicious: boolean
  suspicious_reasons: string[]
  is_known: boolean
}

interface NetworkInterface {
  interface: string
  tx_bytes_per_sec: number
  rx_bytes_per_sec: number
  tx_mbps: number
  rx_mbps: number
  tx_packets_per_sec: number
  rx_packets_per_sec: number
}

interface NetworkMonitoringReport {
  generated_at: string
  auth: {
    window_minutes: number
    count: number
    recent_events: string[]
  }
  listening: Array<{
    port: number
    is_allowed: boolean
    process: string
    exe: string
  }>
  suspicious: Array<{
    local_port: number
    remote: string
    status: string
    process: string
    exe: string
    is_private_remote: boolean
  }>
  devices: NetworkDevice[]
  suspicious_devices: NetworkDevice[]
  suspicious_device_count: number
  interfaces: NetworkInterface[]
  wifi: {
    status: string
    ssid?: string
    bssid?: string
    rssi?: number
    channel?: string
  }
  latency: Array<{
    host: string
    status: string
    latency?: string
  }>
}

interface NetworkConfig {
  scan_interval_seconds: number
  auto_refresh_enabled: boolean
  alert_on_suspicious: boolean
  alert_threshold: {
    suspicious_devices: number
    auth_failures: number
  }
  monitoring_settings: {
    window_minutes: number
    enable_device_detection: boolean
    enable_interface_monitoring: boolean
    enable_wifi_monitoring: boolean
  }
}

export default function NetworkMonitoring() {
  const [autoRefresh, setAutoRefresh] = useState(false)
  const [selectedNetwork, setSelectedNetwork] = useState<'local' | 'wan' | 'all'>('local')
  const [showConfig, setShowConfig] = useState(false)
  const [showRecommended, setShowRecommended] = useState(true)
  const [selectedDevice, setSelectedDevice] = useState<NetworkDevice | null>(null)
  const [editingDevice, setEditingDevice] = useState<NetworkDevice | null>(null)
  const [deviceEditForm, setDeviceEditForm] = useState({
    hostname: '',
    category: '',
    notes: '',
    ip: '',
  })

  const networkQuery = useQuery({
    queryKey: ['network-status', selectedNetwork],
    queryFn: async () => {
      const response = await apiClient.get<NetworkMonitoringReport>(
        apiPath('network/status'),
        { params: { refresh: false } }
      )
      return response.data
    },
    refetchInterval: autoRefresh ? 10000 : false,
  })

  const configQuery = useQuery({
    queryKey: ['network-config'],
    queryFn: async () => {
      const response = await apiClient.get<NetworkConfig>(apiPath('network/config'))
      return response.data
    },
  })

  const knownDevicesQuery = useQuery({
    queryKey: ['known-devices'],
    queryFn: async () => {
      const response = await apiClient.get(apiPath('network/known-devices'))
      return response.data
    },
  })

  const refreshMutation = useMutation({
    mutationFn: async () => {
      await apiClient.post(apiPath('network/refresh'))
      return networkQuery.refetch()
    },
    onSuccess: () => {
      toast.success('Network data refreshed')
      networkQuery.refetch()
    },
    onError: () => toast.error('Failed to refresh network data'),
  })

  const addKnownDeviceMutation = useMutation({
    mutationFn: async (device: { hostname?: string; mac?: string; ip?: string }) => {
      return apiClient.post(apiPath('network/known-devices/add'), device)
    },
    onSuccess: () => {
      toast.success('Device added to known devices')
      knownDevicesQuery.refetch()
      networkQuery.refetch()
      setShowDeviceActions(false)
    },
    onError: () => toast.error('Failed to add device'),
  })

  const blockDeviceMutation = useMutation({
    mutationFn: async (device: { hostname?: string; mac?: string; ip?: string; reason?: string }) => {
      return apiClient.post(apiPath('network/devices/block'), device)
    },
    onSuccess: () => {
      toast.success('Device blocked')
      knownDevicesQuery.refetch()
      networkQuery.refetch()
      setShowDeviceActions(false)
    },
    onError: () => toast.error('Failed to block device'),
  })

  const unblockDeviceMutation = useMutation({
    mutationFn: async (device: { hostname?: string; mac?: string; ip?: string }) => {
      return apiClient.post(apiPath('network/devices/unblock'), device)
    },
    onSuccess: () => {
      toast.success('Device unblocked')
      knownDevicesQuery.refetch()
      networkQuery.refetch()
    },
    onError: () => toast.error('Failed to unblock device'),
  })

  const updateConfigMutation = useMutation({
    mutationFn: async (config: Partial<NetworkConfig>) => {
      return apiClient.post(apiPath('network/config'), config)
    },
    onSuccess: () => {
      toast.success('Configuration updated')
      configQuery.refetch()
      setShowConfig(false)
    },
    onError: () => toast.error('Failed to update configuration'),
  })

  const recommendedSettingsQuery = useQuery({
    queryKey: ['recommended-settings'],
    queryFn: async () => {
      const response = await apiClient.get(apiPath('network/recommended-settings'))
      return response.data
    },
  })

  const updateDeviceMutation = useMutation({
    mutationFn: async (deviceUpdate: { mac?: string; ip?: string; hostname?: string; category?: string; notes?: string }) => {
      return apiClient.post(apiPath('network/devices/update'), deviceUpdate)
    },
    onSuccess: () => {
      toast.success('Device updated')
      networkQuery.refetch()
      setEditingDevice(null)
      setDeviceEditForm({ hostname: '', category: '', notes: '', ip: '' })
    },
    onError: () => toast.error('Failed to update device'),
  })

  const handleEditDevice = (device: NetworkDevice) => {
    setEditingDevice(device)
    setDeviceEditForm({
      hostname: device.hostname || '',
      category: '',
      notes: '',
      ip: device.ip || '',
    })
  }

  const handleSaveDeviceEdit = () => {
    if (!editingDevice) return
    
    updateDeviceMutation.mutate({
      mac: editingDevice.mac,
      ip: editingDevice.ip,
      hostname: deviceEditForm.hostname || undefined,
      category: deviceEditForm.category || undefined,
      notes: deviceEditForm.notes || undefined,
    })
  }

  const handleApplyRecommended = (recommendation: any) => {
    if (recommendation.action === 'router_config') {
      toast.info(`Apply this setting in your router admin panel: ${recommendation.title}`)
      return
    }
    
    // Apply monitoring-related recommendations
    if (recommendation.category === 'monitoring') {
      const updates: Partial<NetworkConfig> = {}
      if (recommendation.key === 'scan_interval_seconds') {
        updates.scan_interval_seconds = recommendation.value
      } else if (recommendation.key === 'alert_on_suspicious') {
        updates.alert_on_suspicious = recommendation.value
      }
      if (Object.keys(updates).length > 0) {
        updateConfigMutation.mutate(updates)
      }
    }
  }

  const report = networkQuery.data
  const config = configQuery.data

  const getSuspiciousSeverity = (device: NetworkDevice): 'low' | 'medium' | 'high' => {
    if (device.suspicious_reasons.includes('suspicious_hostname_pattern')) return 'high'
    if (device.suspicious_reasons.includes('unknown_hostname') && !device.is_known) return 'medium'
    return 'low'
  }

  const severityColors = {
    low: 'bg-yellow-500/10 text-yellow-300 border-yellow-500/20',
    medium: 'bg-orange-500/10 text-orange-300 border-orange-500/20',
    high: 'bg-red-500/10 text-red-300 border-red-500/20',
  }

  const handleAddKnownDevice = (device: NetworkDevice) => {
    addKnownDeviceMutation.mutate({
      hostname: device.hostname,
      mac: device.mac,
      ip: device.ip,
    })
  }

  const handleBlockDevice = (device: NetworkDevice) => {
    blockDeviceMutation.mutate({
      hostname: device.hostname,
      mac: device.mac,
      ip: device.ip,
      reason: 'Manually blocked via UI',
    })
  }

  return (
    <div className="px-4 py-6 sm:px-0 space-y-6">
      {/* Header */}
      <header className="glass-panel p-6 border border-[color:var(--osd-border)]">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.5em] text-[color:var(--osd-muted)]">
              Network Security & Monitoring
            </p>
            <h1 className="text-3xl font-semibold flex items-center gap-3 text-[color:var(--osd-text)]">
              <Network className="w-8 h-8 text-[color:var(--osd-accent)]" />
              Network Device Monitor
            </h1>
            <p className="mt-2 text-sm text-[color:var(--osd-muted)] max-w-3xl">
              Monitor network devices, detect suspicious activity, and configure network security settings.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <select
              value={selectedNetwork}
              onChange={(e) => setSelectedNetwork(e.target.value as 'local' | 'wan' | 'all')}
              className="btn-tonal border border-[color:var(--osd-border)] text-[color:var(--osd-text)] bg-[color:var(--osd-surfaceAlt)]"
            >
              <option value="local">Local Network</option>
              <option value="wan">Wide Area</option>
              <option value="all">All Networks</option>
            </select>
            <button
              onClick={() => refreshMutation.mutate()}
              disabled={refreshMutation.isPending}
              className="btn-tonal border border-[color:var(--osd-border)] text-[color:var(--osd-text)]"
            >
              <RefreshCw className={`w-4 h-4 ${refreshMutation.isPending ? 'animate-spin' : ''}`} />
              Refresh
            </button>
            <button
              onClick={() => setAutoRefresh(!autoRefresh)}
              className={`btn-tonal ${
                autoRefresh
                  ? 'bg-[color:var(--osd-accent)] text-white'
                  : 'border border-[color:var(--osd-border)] text-[color:var(--osd-text)]'
              }`}
            >
              <Activity className="w-4 h-4" />
              Auto
            </button>
            <button
              onClick={() => setShowConfig(!showConfig)}
              className={`btn-tonal ${
                showConfig
                  ? 'bg-[color:var(--osd-accent)] text-white'
                  : 'border border-[color:var(--osd-border)] text-[color:var(--osd-text)]'
              }`}
            >
              <Settings className="w-4 h-4" />
              Config
            </button>
          </div>
        </div>
      </header>

      {/* Configuration Panel */}
      {showConfig && config && (
        <section className="glass-panel p-6 border border-[color:var(--osd-border)]">
          <h2 className="text-lg font-semibold text-[color:var(--osd-text)] flex items-center gap-2 mb-4">
            <Settings className="w-5 h-5" />
            Network Monitoring Configuration
          </h2>
          <div className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label className="block text-sm font-medium text-[color:var(--osd-text)] mb-2">
                  Scan Interval (seconds)
                </label>
                <input
                  type="number"
                  defaultValue={config.scan_interval_seconds}
                  min={10}
                  max={3600}
                  className="w-full px-3 py-2 rounded-xl bg-[color:var(--osd-surfaceAlt)] border border-[color:var(--osd-border)] text-[color:var(--osd-text)]"
                  onChange={(e) => {
                    updateConfigMutation.mutate({
                      scan_interval_seconds: parseInt(e.target.value) || 60,
                    })
                  }}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-[color:var(--osd-text)] mb-2">
                  Monitoring Window (minutes)
                </label>
                <input
                  type="number"
                  defaultValue={config.monitoring_settings.window_minutes}
                  min={1}
                  max={1440}
                  className="w-full px-3 py-2 rounded-xl bg-[color:var(--osd-surfaceAlt)] border border-[color:var(--osd-border)] text-[color:var(--osd-text)]"
                  onChange={(e) => {
                    updateConfigMutation.mutate({
                      monitoring_settings: {
                        ...config.monitoring_settings,
                        window_minutes: parseInt(e.target.value) || 10,
                      },
                    })
                  }}
                />
              </div>
            </div>
            <div className="flex flex-wrap gap-4">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  defaultChecked={config.auto_refresh_enabled}
                  onChange={(e) => {
                    updateConfigMutation.mutate({ auto_refresh_enabled: e.target.checked })
                  }}
                  className="w-4 h-4"
                />
                <span className="text-sm text-[color:var(--osd-text)]">Auto Refresh Enabled</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  defaultChecked={config.alert_on_suspicious}
                  onChange={(e) => {
                    updateConfigMutation.mutate({ alert_on_suspicious: e.target.checked })
                  }}
                  className="w-4 h-4"
                />
                <span className="text-sm text-[color:var(--osd-text)]">Alert on Suspicious Devices</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  defaultChecked={config.monitoring_settings.enable_device_detection}
                  onChange={(e) => {
                    updateConfigMutation.mutate({
                      monitoring_settings: {
                        ...config.monitoring_settings,
                        enable_device_detection: e.target.checked,
                      },
                    })
                  }}
                  className="w-4 h-4"
                />
                <span className="text-sm text-[color:var(--osd-text)]">Enable Device Detection</span>
              </label>
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label className="block text-sm font-medium text-[color:var(--osd-text)] mb-2">
                  Suspicious Device Alert Threshold
                </label>
                <input
                  type="number"
                  defaultValue={config.alert_threshold.suspicious_devices}
                  min={0}
                  className="w-full px-3 py-2 rounded-xl bg-[color:var(--osd-surfaceAlt)] border border-[color:var(--osd-border)] text-[color:var(--osd-text)]"
                  onChange={(e) => {
                    updateConfigMutation.mutate({
                      alert_threshold: {
                        ...config.alert_threshold,
                        suspicious_devices: parseInt(e.target.value) || 1,
                      },
                    })
                  }}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-[color:var(--osd-text)] mb-2">
                  Auth Failure Alert Threshold
                </label>
                <input
                  type="number"
                  defaultValue={config.alert_threshold.auth_failures}
                  min={0}
                  className="w-full px-3 py-2 rounded-xl bg-[color:var(--osd-surfaceAlt)] border border-[color:var(--osd-border)] text-[color:var(--osd-text)]"
                  onChange={(e) => {
                    updateConfigMutation.mutate({
                      alert_threshold: {
                        ...config.alert_threshold,
                        auth_failures: parseInt(e.target.value) || 10,
                      },
                    })
                  }}
                />
              </div>
            </div>
          </div>
        </section>
      )}

      {networkQuery.isLoading && (
        <div className="glass-panel p-6 border border-[color:var(--osd-border)] text-center">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto text-[color:var(--osd-muted)]" />
          <p className="mt-2 text-[color:var(--osd-muted)]">Loading network data...</p>
        </div>
      )}

      {networkQuery.isError && (
        <div className="glass-panel p-6 border border-red-500/20 bg-red-500/10">
          <div className="flex items-center gap-2 text-red-300">
            <AlertTriangle className="w-5 h-5" />
            <p>Failed to load network data. Make sure network monitoring script is configured.</p>
          </div>
        </div>
      )}

      {report && (
        <>
          {/* Summary Cards */}
          <section className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <MetricCard
              icon={Users}
              label="Total Devices"
              value={report.devices.length.toString()}
              color="text-blue-400"
            />
            <MetricCard
              icon={Shield}
              label="Suspicious Devices"
              value={report.suspicious_device_count.toString()}
              color={report.suspicious_device_count > 0 ? 'text-red-400' : 'text-green-400'}
            />
            <MetricCard
              icon={Activity}
              label="Auth Failures"
              value={report.auth.count.toString()}
              color={report.auth.count > 0 ? 'text-yellow-400' : 'text-green-400'}
            />
            <MetricCard
              icon={Server}
              label="Listening Ports"
              value={report.listening.length.toString()}
              color="text-purple-400"
            />
          </section>

          {/* Suspicious Devices Alert */}
          {report.suspicious_device_count > 0 && (
            <section className="glass-panel p-6 border border-red-500/40 bg-red-500/10">
              <div className="flex items-start gap-3">
                <AlertTriangle className="w-6 h-6 text-red-400 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <h2 className="text-lg font-semibold text-red-300 mb-2">
                    ⚠️ {report.suspicious_device_count} Suspicious Device{report.suspicious_device_count !== 1 ? 's' : ''} Detected
                  </h2>
                  <div className="space-y-2">
                    {report.suspicious_devices.map((device, idx) => (
                      <div
                        key={idx}
                        className={`rounded-lg border p-3 ${severityColors[getSuspiciousSeverity(device)]}`}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <p className="font-semibold">
                              {device.hostname || 'Unknown Device'} ({device.ip})
                            </p>
                            <p className="text-xs opacity-80 mt-1">MAC: {device.mac}</p>
                            <div className="flex flex-wrap gap-2 mt-2">
                              {device.suspicious_reasons.map((reason, rIdx) => (
                                <span
                                  key={rIdx}
                                  className="text-xs px-2 py-1 rounded bg-black/20"
                                >
                                  {reason.replace(/_/g, ' ')}
                                </span>
                              ))}
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            {!device.is_known && (
                              <>
                                <button
                                  onClick={() => handleAddKnownDevice(device)}
                                  className="px-3 py-1 text-xs rounded bg-green-500/20 text-green-300 border border-green-500/40 hover:bg-green-500/30"
                                  title="Add to known devices"
                                >
                                  <Check className="w-3 h-3 inline mr-1" />
                                  Trust
                                </button>
                                <button
                                  onClick={() => handleBlockDevice(device)}
                                  className="px-3 py-1 text-xs rounded bg-red-500/20 text-red-300 border border-red-500/40 hover:bg-red-500/30"
                                  title="Block device"
                                >
                                  <Ban className="w-3 h-3 inline mr-1" />
                                  Block
                                </button>
                              </>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </section>
          )}

          {/* Recommended Settings Panel */}
          {showRecommended && recommendedSettingsQuery.data && (
            <section className="glass-panel p-6 border border-[color:var(--osd-border)] bg-blue-500/5">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-[color:var(--osd-text)] flex items-center gap-2">
                  <Lightbulb className="w-5 h-5 text-yellow-400" />
                  Recommended Security & Performance Settings
                </h2>
                <button
                  onClick={() => setShowRecommended(false)}
                  className="text-sm text-[color:var(--osd-muted)] hover:text-[color:var(--osd-text)]"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
              <div className="space-y-3">
                {recommendedSettingsQuery.data.security?.recommendations?.slice(0, 5).map((rec: any, idx: number) => (
                  <div
                    key={idx}
                    className={`rounded-lg border p-3 ${
                      rec.priority === 'critical'
                        ? 'bg-red-500/10 border-red-500/30'
                        : rec.priority === 'high'
                        ? 'bg-orange-500/10 border-orange-500/30'
                        : 'bg-blue-500/10 border-blue-500/30'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-semibold text-[color:var(--osd-text)]">{rec.title}</span>
                          <span
                            className={`text-xs px-2 py-0.5 rounded ${
                              rec.priority === 'critical'
                                ? 'bg-red-500/20 text-red-300'
                                : rec.priority === 'high'
                                ? 'bg-orange-500/20 text-orange-300'
                                : 'bg-blue-500/20 text-blue-300'
                            }`}
                          >
                            {rec.priority}
                          </span>
                        </div>
                        <p className="text-sm text-[color:var(--osd-muted)]">{rec.description}</p>
                        {rec.action === 'router_config' && (
                          <p className="text-xs text-[color:var(--osd-muted)] mt-1 italic">
                            Configure in router admin panel
                          </p>
                        )}
                      </div>
                      <button
                        onClick={() => handleApplyRecommended(rec)}
                        className="px-3 py-1 text-xs rounded bg-[color:var(--osd-accent)]/20 text-[color:var(--osd-accent)] border border-[color:var(--osd-accent)]/40 hover:bg-[color:var(--osd-accent)]/30"
                      >
                        {rec.action === 'router_config' ? 'View Guide' : 'Apply'}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Network Devices Table */}
          <section className="glass-panel p-6 border border-[color:var(--osd-border)]">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-[color:var(--osd-text)] flex items-center gap-2">
                <Users className="w-5 h-5" />
                Network Devices ({report.devices.length})
              </h2>
              <div className="flex items-center gap-3">
                {!showRecommended && (
                  <button
                    onClick={() => setShowRecommended(true)}
                    className="text-xs text-[color:var(--osd-muted)] hover:text-[color:var(--osd-text)] flex items-center gap-1"
                  >
                    <Lightbulb className="w-3 h-3" />
                    Show Recommendations
                  </button>
                )}
                <span className="text-xs text-[color:var(--osd-muted)]">
                  Last updated: {new Date(report.generated_at).toLocaleString()}
                </span>
              </div>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-[color:var(--osd-border)]">
                    <th className="text-left py-2 px-3 text-sm font-semibold text-[color:var(--osd-muted)]">
                      Device
                    </th>
                    <th className="text-left py-2 px-3 text-sm font-semibold text-[color:var(--osd-muted)]">
                      IP Address
                    </th>
                    <th className="text-left py-2 px-3 text-sm font-semibold text-[color:var(--osd-muted)]">
                      MAC Address
                    </th>
                    <th className="text-left py-2 px-3 text-sm font-semibold text-[color:var(--osd-muted)]">
                      Interface
                    </th>
                    <th className="text-left py-2 px-3 text-sm font-semibold text-[color:var(--osd-muted)]">
                      Status
                    </th>
                    <th className="text-left py-2 px-3 text-sm font-semibold text-[color:var(--osd-muted)]">
                      Actions
                    </th>
                    <th className="text-left py-2 px-3 text-sm font-semibold text-[color:var(--osd-muted)]">
                      Edit
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {report.devices.length === 0 ? (
                    <tr>
                      <td colSpan={7} className="py-8 text-center text-[color:var(--osd-muted)]">
                        No devices detected
                      </td>
                    </tr>
                  ) : (
                    report.devices.map((device, idx) => (
                      <tr
                        key={idx}
                        className="border-b border-[color:var(--osd-border)] hover:bg-[color:var(--osd-surfaceAlt)]"
                      >
                        <td className="py-3 px-3">
                          <div className="flex items-center gap-2">
                            {device.is_suspicious ? (
                              <AlertTriangle className="w-4 h-4 text-red-400" />
                            ) : device.is_known ? (
                              <CheckCircle className="w-4 h-4 text-green-400" />
                            ) : (
                              <Clock className="w-4 h-4 text-yellow-400" />
                            )}
                            <span className="font-medium text-[color:var(--osd-text)]">
                              {device.hostname || 'Unknown'}
                            </span>
                          </div>
                        </td>
                        <td className="py-3 px-3 text-sm text-[color:var(--osd-text)] font-mono">
                          {device.ip}
                        </td>
                        <td className="py-3 px-3 text-sm text-[color:var(--osd-muted)] font-mono">
                          {device.mac}
                        </td>
                        <td className="py-3 px-3 text-sm text-[color:var(--osd-muted)]">
                          {device.interface}
                        </td>
                        <td className="py-3 px-3">
                          {device.is_suspicious ? (
                            <span className="px-2 py-1 rounded text-xs bg-red-500/20 text-red-300 border border-red-500/40">
                              Suspicious
                            </span>
                          ) : device.is_known ? (
                            <span className="px-2 py-1 rounded text-xs bg-green-500/20 text-green-300 border border-green-500/40">
                              Known
                            </span>
                          ) : (
                            <span className="px-2 py-1 rounded text-xs bg-yellow-500/20 text-yellow-300 border border-yellow-500/40">
                              Unknown
                            </span>
                          )}
                        </td>
                        <td className="py-3 px-3">
                          <div className="flex items-center gap-2">
                            {!device.is_known && (
                              <button
                                onClick={() => handleAddKnownDevice(device)}
                                className="px-2 py-1 text-xs rounded bg-green-500/20 text-green-300 border border-green-500/40 hover:bg-green-500/30"
                                title="Add to known devices"
                              >
                                <Check className="w-3 h-3" />
                              </button>
                            )}
                            <button
                              onClick={() => handleBlockDevice(device)}
                              className="px-2 py-1 text-xs rounded bg-red-500/20 text-red-300 border border-red-500/40 hover:bg-red-500/30"
                              title="Block device"
                            >
                              <Ban className="w-3 h-3" />
                            </button>
                          </div>
                        </td>
                        <td className="py-3 px-3">
                          <button
                            onClick={() => handleEditDevice(device)}
                            className="px-2 py-1 text-xs rounded bg-blue-500/20 text-blue-300 border border-blue-500/40 hover:bg-blue-500/30"
                            title="Edit device"
                          >
                            <Edit className="w-3 h-3" />
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </section>

          {/* Network Interfaces */}
          {report.interfaces.length > 0 && (
            <section className="glass-panel p-6 border border-[color:var(--osd-border)]">
              <h2 className="text-lg font-semibold text-[color:var(--osd-text)] flex items-center gap-2 mb-4">
                <HardDrive className="w-5 h-5" />
                Network Interfaces
              </h2>
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {report.interfaces.map((iface, idx) => (
                  <div
                    key={idx}
                    className="rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surfaceAlt)] p-4"
                  >
                    <div className="flex items-center justify-between mb-3">
                      <span className="font-semibold text-[color:var(--osd-text)]">{iface.interface}</span>
                      <Activity className="w-4 h-4 text-[color:var(--osd-muted)]" />
                    </div>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-[color:var(--osd-muted)]">TX:</span>
                        <span className="text-[color:var(--osd-text)] font-mono">
                          {iface.tx_mbps.toFixed(2)} Mbps
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-[color:var(--osd-muted)]">RX:</span>
                        <span className="text-[color:var(--osd-text)] font-mono">
                          {iface.rx_mbps.toFixed(2)} Mbps
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-[color:var(--osd-muted)]">Packets/s:</span>
                        <span className="text-[color:var(--osd-text)] font-mono">
                          {(iface.tx_packets_per_sec + iface.rx_packets_per_sec).toFixed(0)}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* WiFi Status */}
          {report.wifi.status === 'ok' && report.wifi.ssid && (
            <section className="glass-panel p-6 border border-[color:var(--osd-border)]">
              <h2 className="text-lg font-semibold text-[color:var(--osd-text)] flex items-center gap-2 mb-4">
                <Wifi className="w-5 h-5" />
                WiFi Connection
              </h2>
              <div className="grid gap-4 md:grid-cols-3">
                <div>
                  <p className="text-sm text-[color:var(--osd-muted)]">SSID</p>
                  <p className="text-lg font-semibold text-[color:var(--osd-text)]">{report.wifi.ssid}</p>
                </div>
                {report.wifi.channel && (
                  <div>
                    <p className="text-sm text-[color:var(--osd-muted)]">Channel</p>
                    <p className="text-lg font-semibold text-[color:var(--osd-text)]">{report.wifi.channel}</p>
                  </div>
                )}
                {report.wifi.rssi !== null && report.wifi.rssi !== undefined && (
                  <div>
                    <p className="text-sm text-[color:var(--osd-muted)]">Signal Strength</p>
                    <p className="text-lg font-semibold text-[color:var(--osd-text)]">
                      {report.wifi.rssi} dBm
                    </p>
                  </div>
                )}
              </div>
            </section>
          )}

          {/* Device Edit Modal */}
          {editingDevice && (
            <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={() => setEditingDevice(null)}>
              <div className="glass-panel p-6 border border-[color:var(--osd-border)] w-full max-w-md m-4" onClick={(e) => e.stopPropagation()}>
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-[color:var(--osd-text)] flex items-center gap-2">
                    <Edit className="w-5 h-5" />
                    Edit Device
                  </h3>
                  <button
                    onClick={() => setEditingDevice(null)}
                    className="text-[color:var(--osd-muted)] hover:text-[color:var(--osd-text)]"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-[color:var(--osd-text)] mb-2">
                      Hostname
                    </label>
                    <input
                      type="text"
                      value={deviceEditForm.hostname}
                      onChange={(e) => setDeviceEditForm({ ...deviceEditForm, hostname: e.target.value })}
                      placeholder={editingDevice.hostname || 'Enter hostname'}
                      className="w-full px-3 py-2 rounded-xl bg-[color:var(--osd-surfaceAlt)] border border-[color:var(--osd-border)] text-[color:var(--osd-text)]"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-[color:var(--osd-text)] mb-2">
                      IP Address (if different)
                    </label>
                    <input
                      type="text"
                      value={deviceEditForm.ip}
                      onChange={(e) => setDeviceEditForm({ ...deviceEditForm, ip: e.target.value })}
                      placeholder={editingDevice.ip || 'Enter IP address'}
                      className="w-full px-3 py-2 rounded-xl bg-[color:var(--osd-surfaceAlt)] border border-[color:var(--osd-border)] text-[color:var(--osd-text)] font-mono"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-[color:var(--osd-text)] mb-2">
                      Category
                    </label>
                    <select
                      value={deviceEditForm.category}
                      onChange={(e) => setDeviceEditForm({ ...deviceEditForm, category: e.target.value })}
                      className="w-full px-3 py-2 rounded-xl bg-[color:var(--osd-surfaceAlt)] border border-[color:var(--osd-border)] text-[color:var(--osd-text)]"
                    >
                      <option value="">No category</option>
                      <option value="laptop">Laptop</option>
                      <option value="desktop">Desktop</option>
                      <option value="mobile">Mobile Device</option>
                      <option value="server">Server</option>
                      <option value="iot">IoT Device</option>
                      <option value="printer">Printer</option>
                      <option value="router">Router/Gateway</option>
                      <option value="other">Other</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-[color:var(--osd-text)] mb-2">
                      Notes
                    </label>
                    <textarea
                      value={deviceEditForm.notes}
                      onChange={(e) => setDeviceEditForm({ ...deviceEditForm, notes: e.target.value })}
                      placeholder="Add notes about this device..."
                      rows={3}
                      className="w-full px-3 py-2 rounded-xl bg-[color:var(--osd-surfaceAlt)] border border-[color:var(--osd-border)] text-[color:var(--osd-text)]"
                    />
                  </div>
                  <div className="text-xs text-[color:var(--osd-muted)] space-y-1">
                    <p><strong>MAC:</strong> {editingDevice.mac}</p>
                    <p><strong>Interface:</strong> {editingDevice.interface}</p>
                  </div>
                  <div className="flex gap-2 justify-end">
                    <button
                      onClick={() => setEditingDevice(null)}
                      className="px-4 py-2 rounded-xl border border-[color:var(--osd-border)] text-[color:var(--osd-text)] hover:bg-[color:var(--osd-surfaceAlt)]"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleSaveDeviceEdit}
                      disabled={updateDeviceMutation.isPending}
                      className="px-4 py-2 rounded-xl bg-[color:var(--osd-accent)] text-white hover:bg-[color:var(--osd-accentHover)] disabled:opacity-50"
                    >
                      <Save className="w-4 h-4 inline mr-2" />
                      Save Changes
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}

function MetricCard({
  icon: Icon,
  label,
  value,
  color,
}: {
  icon: React.ElementType
  label: string
  value: string
  color: string
}) {
  return (
    <div className="glass-panel p-4 border border-[color:var(--osd-border)]">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs text-[color:var(--osd-muted)] mb-1">{label}</p>
          <p className={`text-2xl font-semibold ${color}`}>{value}</p>
        </div>
        <Icon className={`w-8 h-8 ${color} opacity-50`} />
      </div>
    </div>
  )
}







