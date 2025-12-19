import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Shield,
  Users,
  Database,
  Activity,
  Settings,
  Table,
  FileText,
  AlertTriangle,
  CheckCircle,
  XCircle,
  RefreshCw,
  Download,
  Trash2,
  Eye,
  Edit,
  ChevronRight,
  ChevronDown,
  Search,
  Filter,
  Clock,
  Server,
  Layers,
} from 'lucide-react'
import { adminAPI, logsAPI } from '../lib/apiClient'
import { toast } from '../utils/toast'

type AdminTab = 'overview' | 'users' | 'database' | 'logs' | 'services'

interface TableColumn {
  name: string
  type: string
  notnull: boolean
  pk: boolean
}

interface TableSchema {
  name: string
  columns: TableColumn[]
  row_count: number
  indexes: any[]
}

export default function Admin() {
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState<AdminTab>('overview')
  const [selectedTable, setSelectedTable] = useState<string | null>(null)
  const [expandedTables, setExpandedTables] = useState<Set<string>>(new Set())
  const [logFilters, setLogFilters] = useState({
    level: '',
    source: '',
    search: '',
  })
  const [userFilter, setUserFilter] = useState({
    includeDemo: true,
    includeProduction: true,
    activeOnly: false,
  })

  // Queries
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['admin-stats'],
    queryFn: adminAPI.getStats,
  })

  const { data: users = [], isLoading: usersLoading } = useQuery({
    queryKey: ['admin-users', userFilter],
    queryFn: () => adminAPI.listUsers(userFilter),
    enabled: activeTab === 'users',
  })

  const { data: tables = [], isLoading: tablesLoading } = useQuery({
    queryKey: ['admin-tables'],
    queryFn: adminAPI.getTables,
    enabled: activeTab === 'database',
  })

  const { data: tableData, isLoading: tableDataLoading } = useQuery({
    queryKey: ['admin-table-data', selectedTable],
    queryFn: () => adminAPI.getTableData(selectedTable!, { limit: 50 }),
    enabled: !!selectedTable,
  })

  const { data: logs = [], isLoading: logsLoading } = useQuery({
    queryKey: ['admin-logs', logFilters],
    queryFn: () => logsAPI.getLogs({
      level: logFilters.level || undefined,
      source: logFilters.source || undefined,
      search: logFilters.search || undefined,
      limit: 100,
    }),
    enabled: activeTab === 'logs',
    refetchInterval: 5000,
  })

  const { data: logSources = [] } = useQuery({
    queryKey: ['log-sources'],
    queryFn: logsAPI.getSources,
    enabled: activeTab === 'logs',
  })

  const { data: serviceMetrics = [] } = useQuery({
    queryKey: ['service-metrics'],
    queryFn: () => logsAPI.getServiceMetrics(24),
    enabled: activeTab === 'services',
  })

  // Mutations
  const seedDemoMutation = useMutation({
    mutationFn: adminAPI.seedDemoData,
    onSuccess: () => {
      toast.success('Demo data seeded successfully')
      queryClient.invalidateQueries({ queryKey: ['admin-stats'] })
      queryClient.invalidateQueries({ queryKey: ['admin-users'] })
    },
    onError: () => toast.error('Failed to seed demo data'),
  })

  const cleanupDemoMutation = useMutation({
    mutationFn: adminAPI.cleanupDemoData,
    onSuccess: () => {
      toast.success('Demo data cleaned up')
      queryClient.invalidateQueries({ queryKey: ['admin-stats'] })
      queryClient.invalidateQueries({ queryKey: ['admin-users'] })
    },
    onError: () => toast.error('Failed to cleanup demo data'),
  })

  const updateUserMutation = useMutation({
    mutationFn: ({ userId, updates }: { userId: string; updates: any }) =>
      adminAPI.updateUser(userId, updates),
    onSuccess: () => {
      toast.success('User updated')
      queryClient.invalidateQueries({ queryKey: ['admin-users'] })
    },
    onError: () => toast.error('Failed to update user'),
  })

  const toggleTableExpanded = (tableName: string) => {
    setExpandedTables((prev) => {
      const next = new Set(prev)
      if (next.has(tableName)) {
        next.delete(tableName)
      } else {
        next.add(tableName)
      }
      return next
    })
  }

  const tabs = [
    { id: 'overview' as AdminTab, label: 'Overview', icon: Activity },
    { id: 'users' as AdminTab, label: 'Users', icon: Users },
    { id: 'database' as AdminTab, label: 'Database', icon: Database },
    { id: 'logs' as AdminTab, label: 'Logs', icon: FileText },
    { id: 'services' as AdminTab, label: 'Services', icon: Server },
  ]

  const getSeverityColor = (level: string) => {
    switch (level?.toUpperCase()) {
      case 'ERROR':
      case 'CRITICAL':
        return 'text-rose-400 bg-rose-500/10'
      case 'WARNING':
        return 'text-amber-400 bg-amber-500/10'
      case 'INFO':
        return 'text-primary-400 bg-primary-500/10'
      case 'DEBUG':
        return 'text-slate-400 bg-slate-500/10'
      default:
        return 'text-slate-400 bg-slate-500/10'
    }
  }

  return (
    <div className="min-h-screen bg-slate-900">
      {/* Header */}
      <div className="px-6 py-4 border-b border-slate-700/50 bg-gradient-to-r from-slate-900 to-slate-800">
        <div className="flex items-center gap-4">
          <div className="p-2.5 rounded-xl bg-gradient-to-br from-amber-500/20 to-orange-500/20 border border-amber-500/30">
            <Shield className="w-6 h-6 text-amber-400" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">Admin Panel</h1>
            <p className="text-sm text-slate-400">Manage users, view database, and monitor system</p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="px-6 py-3 border-b border-slate-700/50 bg-slate-800/30">
        <div className="flex items-center gap-1">
          {tabs.map((tab) => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  activeTab === tab.id
                    ? 'bg-primary-500/20 text-primary-400 border border-primary-500/30'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-700/50'
                }`}
              >
                <Icon className="w-4 h-4" />
                {tab.label}
              </button>
            )
          })}
        </div>
      </div>

      {/* Content */}
      <div className="p-6">
        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="p-5 bg-slate-800/50 border border-slate-700/50 rounded-xl">
                <div className="flex items-center justify-between mb-3">
                  <Users className="w-5 h-5 text-primary-400" />
                  <span className="text-xs text-slate-500">Users</span>
                </div>
                <p className="text-2xl font-bold text-white">{stats?.total_users || 0}</p>
                <div className="flex items-center gap-4 mt-2 text-xs">
                  <span className="text-emerald-400">{stats?.active_users || 0} active</span>
                  <span className="text-slate-500">{stats?.demo_users || 0} demo</span>
                </div>
              </div>

              <div className="p-5 bg-slate-800/50 border border-slate-700/50 rounded-xl">
                <div className="flex items-center justify-between mb-3">
                  <Activity className="w-5 h-5 text-emerald-400" />
                  <span className="text-xs text-slate-500">Sessions</span>
                </div>
                <p className="text-2xl font-bold text-white">{stats?.active_sessions || 0}</p>
                <div className="flex items-center gap-4 mt-2 text-xs">
                  <span className="text-slate-500">{stats?.total_sessions || 0} total</span>
                </div>
              </div>

              <div className="p-5 bg-slate-800/50 border border-slate-700/50 rounded-xl">
                <div className="flex items-center justify-between mb-3">
                  <Database className="w-5 h-5 text-violet-400" />
                  <span className="text-xs text-slate-500">Data</span>
                </div>
                <p className="text-2xl font-bold text-white">{stats?.total_tasks || 0}</p>
                <div className="flex items-center gap-4 mt-2 text-xs">
                  <span className="text-slate-500">{stats?.total_projects || 0} projects</span>
                  <span className="text-slate-500">{stats?.total_documents || 0} docs</span>
                </div>
              </div>

              <div className="p-5 bg-slate-800/50 border border-slate-700/50 rounded-xl">
                <div className="flex items-center justify-between mb-3">
                  {stats?.system_health === 'healthy' ? (
                    <CheckCircle className="w-5 h-5 text-emerald-400" />
                  ) : (
                    <AlertTriangle className="w-5 h-5 text-amber-400" />
                  )}
                  <span className="text-xs text-slate-500">Health</span>
                </div>
                <p className="text-2xl font-bold text-white capitalize">{stats?.system_health || 'Unknown'}</p>
                <div className="flex items-center gap-4 mt-2 text-xs">
                  <span className="text-emerald-400">All systems operational</span>
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="p-5 bg-slate-800/50 border border-slate-700/50 rounded-xl">
              <h3 className="text-sm font-semibold text-slate-200 mb-4">Quick Actions</h3>
              <div className="flex flex-wrap gap-3">
                <button
                  onClick={() => seedDemoMutation.mutate()}
                  disabled={seedDemoMutation.isPending}
                  className="px-4 py-2 bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 rounded-lg text-sm font-medium hover:bg-emerald-500/30 disabled:opacity-50 transition-all"
                >
                  Seed Demo Data
                </button>
                <button
                  onClick={() => cleanupDemoMutation.mutate()}
                  disabled={cleanupDemoMutation.isPending}
                  className="px-4 py-2 bg-rose-500/20 text-rose-400 border border-rose-500/30 rounded-lg text-sm font-medium hover:bg-rose-500/30 disabled:opacity-50 transition-all"
                >
                  Cleanup Demo Data
                </button>
                <button
                  onClick={() => queryClient.invalidateQueries()}
                  className="px-4 py-2 bg-slate-700/50 text-slate-300 border border-slate-600/50 rounded-lg text-sm font-medium hover:bg-slate-700 transition-all flex items-center gap-2"
                >
                  <RefreshCw className="w-4 h-4" />
                  Refresh All
                </button>
              </div>
            </div>

            {/* Production vs Demo Stats */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-5 bg-slate-800/50 border border-slate-700/50 rounded-xl">
                <h3 className="text-sm font-semibold text-slate-200 mb-4 flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-emerald-400" />
                  Production Users
                </h3>
                <p className="text-3xl font-bold text-white mb-2">{stats?.production_users || 0}</p>
                <p className="text-xs text-slate-500">Real users with live data</p>
              </div>
              <div className="p-5 bg-slate-800/50 border border-slate-700/50 rounded-xl">
                <h3 className="text-sm font-semibold text-slate-200 mb-4 flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-amber-400" />
                  Demo Users
                </h3>
                <p className="text-3xl font-bold text-white mb-2">{stats?.demo_users || 0}</p>
                <p className="text-xs text-slate-500">Test accounts for development</p>
              </div>
            </div>
          </div>
        )}

        {/* Users Tab */}
        {activeTab === 'users' && (
          <div className="space-y-4">
            {/* Filters */}
            <div className="flex items-center gap-4 p-4 bg-slate-800/30 border border-slate-700/30 rounded-xl">
              <Filter className="w-4 h-4 text-slate-400" />
              <label className="flex items-center gap-2 text-sm text-slate-300">
                <input
                  type="checkbox"
                  checked={userFilter.includeDemo}
                  onChange={(e) => setUserFilter((f) => ({ ...f, includeDemo: e.target.checked }))}
                  className="rounded border-slate-600 bg-slate-800 text-primary-500"
                />
                Demo
              </label>
              <label className="flex items-center gap-2 text-sm text-slate-300">
                <input
                  type="checkbox"
                  checked={userFilter.includeProduction}
                  onChange={(e) => setUserFilter((f) => ({ ...f, includeProduction: e.target.checked }))}
                  className="rounded border-slate-600 bg-slate-800 text-primary-500"
                />
                Production
              </label>
              <label className="flex items-center gap-2 text-sm text-slate-300">
                <input
                  type="checkbox"
                  checked={userFilter.activeOnly}
                  onChange={(e) => setUserFilter((f) => ({ ...f, activeOnly: e.target.checked }))}
                  className="rounded border-slate-600 bg-slate-800 text-primary-500"
                />
                Active Only
              </label>
            </div>

            {/* Users Table */}
            <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl overflow-hidden">
              <table className="w-full">
                <thead className="bg-slate-800/80">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-slate-400">User</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-slate-400">Email</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-slate-400">Status</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-slate-400">Type</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-slate-400">Last Login</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-slate-400">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-700/50">
                  {users.map((user: any) => (
                    <tr key={user.id} className="hover:bg-slate-700/20">
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary-500/30 to-violet-500/30 flex items-center justify-center text-xs font-bold text-white">
                            {user.username[0].toUpperCase()}
                          </div>
                          <div>
                            <p className="text-sm font-medium text-white">{user.username}</p>
                            {user.display_name && (
                              <p className="text-xs text-slate-500">{user.display_name}</p>
                            )}
                          </div>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-sm text-slate-300">{user.email}</td>
                      <td className="px-4 py-3">
                        <span
                          className={`px-2 py-1 rounded-md text-xs font-medium ${
                            user.is_active
                              ? 'bg-emerald-500/20 text-emerald-400'
                              : 'bg-slate-700/50 text-slate-400'
                          }`}
                        >
                          {user.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <span
                          className={`px-2 py-1 rounded-md text-xs font-medium ${
                            user.is_admin
                              ? 'bg-amber-500/20 text-amber-400'
                              : user.is_demo_user
                              ? 'bg-violet-500/20 text-violet-400'
                              : 'bg-primary-500/20 text-primary-400'
                          }`}
                        >
                          {user.is_admin ? 'Admin' : user.is_demo_user ? 'Demo' : 'User'}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm text-slate-400">
                        {user.last_login
                          ? new Date(user.last_login).toLocaleDateString()
                          : 'Never'}
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          <button className="p-1.5 text-slate-400 hover:text-slate-200 hover:bg-slate-700/50 rounded-md transition-colors">
                            <Eye className="w-4 h-4" />
                          </button>
                          <button className="p-1.5 text-slate-400 hover:text-slate-200 hover:bg-slate-700/50 rounded-md transition-colors">
                            <Edit className="w-4 h-4" />
                          </button>
                          <button className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 rounded-md transition-colors">
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {usersLoading && (
                <div className="p-8 text-center text-slate-400">Loading users...</div>
              )}
              {!usersLoading && users.length === 0 && (
                <div className="p-8 text-center text-slate-500">No users found</div>
              )}
            </div>
          </div>
        )}

        {/* Database Tab */}
        {activeTab === 'database' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Tables List */}
            <div className="lg:col-span-1 bg-slate-800/50 border border-slate-700/50 rounded-xl overflow-hidden">
              <div className="p-4 border-b border-slate-700/50">
                <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
                  <Layers className="w-4 h-4 text-primary-400" />
                  Database Tables
                </h3>
              </div>
              <div className="divide-y divide-slate-700/30 max-h-[600px] overflow-y-auto">
                {tables.map((table: TableSchema) => (
                  <div key={table.name} className="border-b border-slate-700/30 last:border-0">
                    <button
                      onClick={() => {
                        toggleTableExpanded(table.name)
                        setSelectedTable(table.name)
                      }}
                      className={`w-full px-4 py-3 flex items-center justify-between hover:bg-slate-700/30 transition-colors ${
                        selectedTable === table.name ? 'bg-primary-500/10' : ''
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <Table className="w-4 h-4 text-slate-400" />
                        <span className="text-sm font-medium text-slate-200">{table.name}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-slate-500">{table.row_count} rows</span>
                        {expandedTables.has(table.name) ? (
                          <ChevronDown className="w-4 h-4 text-slate-500" />
                        ) : (
                          <ChevronRight className="w-4 h-4 text-slate-500" />
                        )}
                      </div>
                    </button>
                    {expandedTables.has(table.name) && (
                      <div className="px-4 py-2 bg-slate-900/30 text-xs">
                        <p className="text-slate-500 mb-2">Columns:</p>
                        <div className="space-y-1">
                          {table.columns.map((col) => (
                            <div key={col.name} className="flex items-center gap-2">
                              <span className={`${col.pk ? 'text-amber-400' : 'text-slate-300'}`}>
                                {col.name}
                              </span>
                              <span className="text-slate-600">{col.type}</span>
                              {col.pk && <span className="text-amber-500">PK</span>}
                              {col.notnull && <span className="text-rose-500">NOT NULL</span>}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Table Data */}
            <div className="lg:col-span-2 bg-slate-800/50 border border-slate-700/50 rounded-xl overflow-hidden">
              <div className="p-4 border-b border-slate-700/50 flex items-center justify-between">
                <h3 className="text-sm font-semibold text-slate-200">
                  {selectedTable ? `Table: ${selectedTable}` : 'Select a table'}
                </h3>
                {selectedTable && (
                  <span className="text-xs text-slate-500">
                    Showing up to 50 rows
                  </span>
                )}
              </div>
              <div className="overflow-x-auto max-h-[600px] overflow-y-auto">
                {tableDataLoading && (
                  <div className="p-8 text-center text-slate-400">Loading data...</div>
                )}
                {!tableDataLoading && tableData && tableData.rows?.length > 0 ? (
                  <table className="w-full text-xs">
                    <thead className="bg-slate-800/80 sticky top-0">
                      <tr>
                        {Object.keys(tableData.rows[0]).map((key) => (
                          <th key={key} className="px-3 py-2 text-left font-semibold text-slate-400 whitespace-nowrap">
                            {key}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-700/30">
                      {tableData.rows.map((row: any, idx: number) => (
                        <tr key={idx} className="hover:bg-slate-700/20">
                          {Object.values(row).map((val: any, colIdx) => (
                            <td key={colIdx} className="px-3 py-2 text-slate-300 max-w-[200px] truncate">
                              {val === null ? (
                                <span className="text-slate-600 italic">null</span>
                              ) : typeof val === 'object' ? (
                                JSON.stringify(val).slice(0, 50)
                              ) : (
                                String(val).slice(0, 100)
                              )}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                ) : (
                  !tableDataLoading && (
                    <div className="p-8 text-center text-slate-500">
                      {selectedTable ? 'No data in this table' : 'Select a table to view data'}
                    </div>
                  )
                )}
              </div>
            </div>
          </div>
        )}

        {/* Logs Tab */}
        {activeTab === 'logs' && (
          <div className="space-y-4">
            {/* Filters */}
            <div className="flex items-center gap-4 p-4 bg-slate-800/30 border border-slate-700/30 rounded-xl">
              <select
                value={logFilters.level}
                onChange={(e) => setLogFilters((f) => ({ ...f, level: e.target.value }))}
                className="px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-sm text-slate-300"
              >
                <option value="">All Levels</option>
                <option value="DEBUG">Debug</option>
                <option value="INFO">Info</option>
                <option value="WARNING">Warning</option>
                <option value="ERROR">Error</option>
                <option value="CRITICAL">Critical</option>
              </select>
              <select
                value={logFilters.source}
                onChange={(e) => setLogFilters((f) => ({ ...f, source: e.target.value }))}
                className="px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-sm text-slate-300"
              >
                <option value="">All Sources</option>
                {logSources.map((src: string) => (
                  <option key={src} value={src}>{src}</option>
                ))}
              </select>
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                <input
                  type="text"
                  value={logFilters.search}
                  onChange={(e) => setLogFilters((f) => ({ ...f, search: e.target.value }))}
                  placeholder="Search logs..."
                  className="w-full pl-10 pr-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-sm text-slate-300 placeholder-slate-500"
                />
              </div>
            </div>

            {/* Logs List */}
            <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl overflow-hidden">
              <div className="divide-y divide-slate-700/30 max-h-[600px] overflow-y-auto font-mono text-xs">
                {logs.map((log: any) => (
                  <div key={log.id} className="px-4 py-2 hover:bg-slate-700/20">
                    <div className="flex items-start gap-3">
                      <span className="text-slate-600 whitespace-nowrap">
                        {new Date(log.timestamp).toLocaleTimeString()}
                      </span>
                      <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${getSeverityColor(log.level)}`}>
                        {log.level}
                      </span>
                      <span className="text-violet-400">[{log.source}]</span>
                      <span className="text-slate-300">{log.action}:</span>
                      <span className="text-slate-400 flex-1">{log.message}</span>
                      {log.duration_ms && (
                        <span className="text-slate-600">{log.duration_ms}ms</span>
                      )}
                    </div>
                  </div>
                ))}
                {logsLoading && (
                  <div className="p-8 text-center text-slate-400">Loading logs...</div>
                )}
                {!logsLoading && logs.length === 0 && (
                  <div className="p-8 text-center text-slate-500">No logs found</div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Services Tab */}
        {activeTab === 'services' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {serviceMetrics.map((service: any) => (
              <div key={service.service_name} className="p-5 bg-slate-800/50 border border-slate-700/50 rounded-xl">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <Server className="w-5 h-5 text-primary-400" />
                    <h3 className="text-sm font-semibold text-white">{service.service_name}</h3>
                  </div>
                  <span
                    className={`px-2 py-1 rounded-md text-xs font-medium ${
                      service.error_count > 0
                        ? 'bg-rose-500/20 text-rose-400'
                        : 'bg-emerald-500/20 text-emerald-400'
                    }`}
                  >
                    {service.error_count > 0 ? `${service.error_count} errors` : 'Healthy'}
                  </span>
                </div>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Total Requests</span>
                    <span className="text-slate-200">{service.total_requests}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Success Rate</span>
                    <span className="text-emerald-400">
                      {((service.success_count / service.total_requests) * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Avg Duration</span>
                    <span className="text-slate-200">{service.avg_duration_ms?.toFixed(0) || 0}ms</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">P95 Duration</span>
                    <span className="text-slate-200">{service.p95_duration_ms || 0}ms</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-slate-400">Last Activity</span>
                    <span className="text-xs text-slate-500">
                      {new Date(service.last_activity).toLocaleTimeString()}
                    </span>
                  </div>
                </div>
              </div>
            ))}
            {serviceMetrics.length === 0 && (
              <div className="col-span-full p-8 text-center text-slate-500">
                No service metrics available
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
