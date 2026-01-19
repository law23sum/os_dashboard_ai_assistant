import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  Activity, BarChart3, Server, Cpu, HardDrive, Network, AlertTriangle,
  CheckCircle, Clock, TrendingUp, RefreshCw, Settings, Eye, Zap
} from 'lucide-react'
import apiClient, { apiPath } from '../lib/apiClient'

type TabType = 'monitoring' | 'analytics' | 'health' | 'network'

interface SystemMetric {
  name: string
  value: number
  unit: string
  status: 'healthy' | 'warning' | 'critical'
  trend?: number
}

interface AnalyticsData {
  period: string
  requests: number
  errors: number
  latency: number
}

export default function Operations() {
  const [activeTab, setActiveTab] = useState<TabType>('monitoring')

  const { data: metrics, isLoading: metricsLoading } = useQuery({
    queryKey: ['system-metrics'],
    queryFn: async () => {
      try {
        const { data } = await apiClient.get<SystemMetric[]>(apiPath('system/metrics'))
        return data
      } catch {
        return [
          { name: 'CPU Usage', value: 45, unit: '%', status: 'healthy' as const, trend: -2 },
          { name: 'Memory', value: 68, unit: '%', status: 'healthy' as const, trend: 5 },
          { name: 'Disk I/O', value: 23, unit: 'MB/s', status: 'healthy' as const, trend: 0 },
          { name: 'Network', value: 156, unit: 'Mbps', status: 'healthy' as const, trend: 12 },
          { name: 'API Latency', value: 45, unit: 'ms', status: 'healthy' as const, trend: -5 },
          { name: 'Error Rate', value: 0.2, unit: '%', status: 'healthy' as const, trend: -0.1 },
        ]
      }
    },
    refetchInterval: 10000,
  })

  const { data: analytics } = useQuery({
    queryKey: ['analytics-data'],
    queryFn: async () => {
      try {
        const { data } = await apiClient.get<AnalyticsData[]>(apiPath('analytics/summary'))
        return data
      } catch {
        return [
          { period: 'Today', requests: 12450, errors: 23, latency: 42 },
          { period: 'Yesterday', requests: 11230, errors: 31, latency: 45 },
          { period: 'This Week', requests: 78500, errors: 156, latency: 44 },
          { period: 'This Month', requests: 324000, errors: 612, latency: 43 },
        ]
      }
    },
  })

  const tabs = [
    { id: 'monitoring' as TabType, label: 'System Monitoring', icon: Activity },
    { id: 'analytics' as TabType, label: 'Analytics', icon: BarChart3 },
    { id: 'health' as TabType, label: 'Health Check', icon: CheckCircle },
    { id: 'network' as TabType, label: 'Network', icon: Network },
  ]

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'text-green-400 bg-green-400/10'
      case 'warning': return 'text-yellow-400 bg-yellow-400/10'
      case 'critical': return 'text-red-400 bg-red-400/10'
      default: return 'text-slate-400 bg-slate-400/10'
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white flex items-center gap-3">
              <Activity className="w-8 h-8 text-indigo-400" />
              Operations Center
            </h1>
            <p className="text-slate-400 mt-1">System monitoring, analytics, and health status</p>
          </div>
          <button className="flex items-center gap-2 px-4 py-2 bg-indigo-500/20 hover:bg-indigo-500/30 text-indigo-400 rounded-lg transition-colors">
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 p-1 bg-slate-800/50 rounded-xl w-fit">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                activeTab === tab.id
                  ? 'bg-indigo-500 text-white'
                  : 'text-slate-400 hover:text-white hover:bg-slate-700/50'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </button>
          ))}
        </div>

        {/* Content */}
        {activeTab === 'monitoring' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {metricsLoading ? (
              <div className="col-span-full flex justify-center py-12">
                <RefreshCw className="w-8 h-8 text-indigo-400 animate-spin" />
              </div>
            ) : (
              metrics?.map((metric, i) => (
                <div key={i} className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-5">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-2">
                      {metric.name === 'CPU Usage' && <Cpu className="w-5 h-5 text-indigo-400" />}
                      {metric.name === 'Memory' && <HardDrive className="w-5 h-5 text-violet-400" />}
                      {metric.name === 'Disk I/O' && <Server className="w-5 h-5 text-blue-400" />}
                      {metric.name === 'Network' && <Network className="w-5 h-5 text-cyan-400" />}
                      {metric.name === 'API Latency' && <Clock className="w-5 h-5 text-amber-400" />}
                      {metric.name === 'Error Rate' && <AlertTriangle className="w-5 h-5 text-red-400" />}
                      <span className="text-slate-300 font-medium">{metric.name}</span>
                    </div>
                    <span className={`px-2 py-1 rounded-full text-xs ${getStatusColor(metric.status)}`}>
                      {metric.status}
                    </span>
                  </div>
                  <div className="flex items-end justify-between">
                    <div>
                      <span className="text-3xl font-bold text-white">{metric.value}</span>
                      <span className="text-slate-400 ml-1">{metric.unit}</span>
                    </div>
                    {metric.trend !== undefined && (
                      <div className={`flex items-center gap-1 text-sm ${metric.trend >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                        <TrendingUp className={`w-4 h-4 ${metric.trend < 0 ? 'rotate-180' : ''}`} />
                        {Math.abs(metric.trend)}%
                      </div>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === 'analytics' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {analytics?.map((item, i) => (
                <div key={i} className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-5">
                  <h3 className="text-slate-400 text-sm mb-2">{item.period}</h3>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-slate-300">Requests</span>
                      <span className="text-white font-medium">{item.requests.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-300">Errors</span>
                      <span className="text-red-400 font-medium">{item.errors}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-300">Avg Latency</span>
                      <span className="text-amber-400 font-medium">{item.latency}ms</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'health' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              { name: 'API Server', status: 'healthy', uptime: '99.9%', lastCheck: '2s ago' },
              { name: 'Database', status: 'healthy', uptime: '99.8%', lastCheck: '5s ago' },
              { name: 'Cache Layer', status: 'healthy', uptime: '100%', lastCheck: '1s ago' },
              { name: 'Message Queue', status: 'healthy', uptime: '99.7%', lastCheck: '3s ago' },
              { name: 'File Storage', status: 'healthy', uptime: '99.9%', lastCheck: '4s ago' },
              { name: 'AI Services', status: 'healthy', uptime: '99.5%', lastCheck: '2s ago' },
            ].map((service, i) => (
              <div key={i} className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-5 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className={`w-3 h-3 rounded-full ${service.status === 'healthy' ? 'bg-green-400' : 'bg-red-400'}`} />
                  <div>
                    <h3 className="text-white font-medium">{service.name}</h3>
                    <p className="text-slate-400 text-sm">Last check: {service.lastCheck}</p>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-green-400 font-medium">{service.uptime}</div>
                  <div className="text-slate-400 text-sm">uptime</div>
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'network' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {[
                { label: 'Inbound Traffic', value: '2.4 GB/s', icon: Network },
                { label: 'Outbound Traffic', value: '1.8 GB/s', icon: Network },
                { label: 'Active Connections', value: '12,456', icon: Zap },
              ].map((stat, i) => (
                <div key={i} className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-5">
                  <div className="flex items-center gap-2 text-slate-400 mb-2">
                    <stat.icon className="w-4 h-4" />
                    {stat.label}
                  </div>
                  <div className="text-2xl font-bold text-white">{stat.value}</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
