import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { Activity, AlertTriangle, Heart, Zap } from 'lucide-react'
import apiClient, { apiPath } from '../lib/apiClient'
import { toast } from '../utils/toast'

interface MonitoringRequest {
  action: string
  system_metrics: Record<string, number>
  monitoring_window: number
  alert_thresholds: Record<string, number>
}

export default function Monitoring() {
  const [action, setAction] = useState('check_health')
  const [metrics, setMetrics] = useState('{"cpu": 65, "memory": 78, "disk": 45}')
  const [window, setWindow] = useState(24)
  const [thresholds, setThresholds] = useState('{"cpu": 80, "memory": 85, "disk": 90}')
  const [results, setResults] = useState<string>('')

  const monitoringMutation = useMutation({
    mutationFn: async (data: MonitoringRequest) => {
      const response = await apiClient.post(apiPath('intelligence/monitoring'), data)
      return response.data
    },
    onSuccess: (data) => {
      setResults(JSON.stringify(data, null, 2))
      toast.success('System monitoring completed successfully')
    },
    onError: (error: any) => {
      toast.error(`Monitoring failed: ${error.message || 'Unknown error'}`)
      setResults(`Error: ${error.message || 'Unknown error'}`)
    },
  })

  const parseJsonInput = (input: string, label: string) => {
    try {
      const parsed = JSON.parse(input)
      if (typeof parsed !== 'object' || parsed === null) {
        throw new Error('must be an object')
      }
      return parsed as Record<string, number>
    } catch (error) {
      toast.error(`Invalid ${label} JSON`)
      throw error
    }
  }

  const handleMonitor = () => {
    let metricsObj: Record<string, number>
    let thresholdsObj: Record<string, number>
    try {
      metricsObj = parseJsonInput(metrics, 'system metrics')
      thresholdsObj = parseJsonInput(thresholds, 'alert thresholds')
    } catch {
      return
    }

    monitoringMutation.mutate({
      action,
      system_metrics: metricsObj,
      monitoring_window: window,
      alert_thresholds: thresholdsObj,
    })
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="mb-8">
        <div className="flex items-center mb-2">
          <Activity className="h-8 w-8 mr-3 text-primary-500" />
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Intelligent Monitoring & Self-Healing
          </h2>
        </div>
        <p className="text-gray-600 dark:text-gray-400">
          Monitor system health, detect anomalies, and enable self-healing
        </p>
      </div>

      {/* Status Indicator */}
      <div className="mb-6 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
        <div className="flex items-center">
          <Heart className="h-5 w-5 text-green-500 mr-2" />
          <span className="text-green-800 dark:text-green-200 font-semibold">
            ✅ Intelligent Monitoring Available
          </span>
        </div>
      </div>

      {/* Monitoring Settings */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6 mb-6">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
          Monitoring Settings
        </h3>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Action
            </label>
            <select
              value={action}
              onChange={(e) => setAction(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white"
            >
              <option value="check_health">Check Health</option>
              <option value="detect_anomalies">Detect Anomalies</option>
              <option value="predictive_maintenance">Predictive Maintenance</option>
              <option value="self_heal">Self-Heal</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              System Metrics (JSON)
            </label>
            <textarea
              value={metrics}
              onChange={(e) => setMetrics(e.target.value)}
              rows={2}
              placeholder='{"cpu": 65, "memory": 78, "disk": 45}'
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white font-mono text-sm"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Monitoring Window (hours)
            </label>
            <input
              type="number"
              value={window}
              onChange={(e) => setWindow(parseInt(e.target.value) || 24)}
              min={1}
              max={168}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Alert Thresholds (JSON)
            </label>
            <textarea
              value={thresholds}
              onChange={(e) => setThresholds(e.target.value)}
              rows={2}
              placeholder='{"cpu": 80, "memory": 85, "disk": 90}'
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white font-mono text-sm"
            />
          </div>

          <button
            onClick={handleMonitor}
            disabled={monitoringMutation.isPending}
            className="w-full flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {monitoringMutation.isPending ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Monitoring...
              </>
            ) : (
              <>
                <Zap className="h-4 w-4 mr-2" />
                Monitor System
              </>
            )}
          </button>
        </div>
      </div>

      {/* Results Area */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <div className="flex items-center mb-4">
          <AlertTriangle className="h-5 w-5 mr-2 text-gray-500" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-white">Monitoring Results</h3>
        </div>
        <div className="bg-gray-50 dark:bg-gray-900 rounded-md p-4">
          <pre className="text-sm text-gray-800 dark:text-gray-200 whitespace-pre-wrap font-mono overflow-auto max-h-96">
            {results || 'Monitoring results will appear here...'}
          </pre>
        </div>
      </div>
    </div>
  )
}
