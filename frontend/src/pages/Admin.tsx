import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Database,
  Users,
  Activity,
  Server,
  Table,
  FileJson,
  Shield,
  TrendingUp,
  AlertCircle,
  Settings,
  Download,
  Eye,
  Edit,
  Trash2,
  RefreshCw,
  Search,
  Filter,
  ChevronDown,
  ChevronRight,
} from 'lucide-react'
import { useState } from 'react'
import apiClient, { apiPath } from '../lib/apiClient'
import { toast } from '../utils/toast'
import PageHeader from '../components/PageHeader'

interface AdminDashboard {
  dashboard: {
    total_users: number
    active_users: number
    admin_users: number
    active_24h: number
    total_activities: number
    activities_24h: number
    total_tasks: number
    total_projects: number
    total_chat_messages: number
    total_documents: number
  }
  timestamp: string
  admin_user: string
}

interface TableInfo {
  name: string
  row_count: number
import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Database, Users, Activity, FileText, Shield, BarChart3, Eye, RefreshCw } from 'lucide-react'

interface TableSchema {
  name: string
  columns: Array<{
    name: string
    type: string
    not_null: boolean
    primary_key: boolean
  }>
  schema: string
}

interface UserStats {
  users_by_role: Record<string, number>
  users_by_status: Record<string, number>
  recent_signups: Array<{ date: string; count: number }>
  most_active_users: Array<{ username: string; email: string; activity_count: number }>
  activity_breakdown: Record<string, number>
}

const fetchAdminDashboard = async (): Promise<AdminDashboard> => {
  const token = localStorage.getItem('access_token')
  const { data } = await apiClient.get(apiPath('admin/dashboard'), {
    headers: { Authorization: `Bearer ${token}` },
  })
  return data
}

const fetchTables = async (database: string) => {
  const token = localStorage.getItem('access_token')
  const { data } = await apiClient.get(apiPath('admin/tables'), {
    params: { database },
    headers: { Authorization: `Bearer ${token}` },
  })
  return data
}

const fetchTableData = async (tableName: string, database: string, page: number) => {
  const token = localStorage.getItem('access_token')
  const { data } = await apiClient.get(apiPath(`admin/tables/${tableName}/data`), {
    params: { database, page, page_size: 50 },
    headers: { Authorization: `Bearer ${token}` },
  })
  return data
}

const fetchUserStats = async (): Promise<UserStats> => {
  const token = localStorage.getItem('access_token')
  const { data } = await apiClient.get(apiPath('admin/users/stats'), {
    headers: { Authorization: `Bearer ${token}` },
  })
  return data
}

const fetchSystemInfo = async () => {
  const token = localStorage.getItem('access_token')
  const { data } = await apiClient.get(apiPath('admin/system/info'), {
    headers: { Authorization: `Bearer ${token}` },
  })
  return data
}

export default function Admin() {
  const [selectedDatabase, setSelectedDatabase] = useState('main')
  const [selectedTable, setSelectedTable] = useState<string | null>(null)
  const [tablePage, setTablePage] = useState(1)
  const [expandedTables, setExpandedTables] = useState<Set<string>>(new Set())

  const queryClient = useQueryClient()

  const { data: dashboard, isLoading: dashboardLoading } = useQuery({
    queryKey: ['admin-dashboard'],
    queryFn: fetchAdminDashboard,
    refetchInterval: 30000,
  })

  const { data: tables } = useQuery({
    queryKey: ['admin-tables', selectedDatabase],
    queryFn: () => fetchTables(selectedDatabase),
  })

  const { data: tableData } = useQuery({
    queryKey: ['admin-table-data', selectedTable, selectedDatabase, tablePage],
    queryFn: () => fetchTableData(selectedTable!, selectedDatabase, tablePage),
    enabled: !!selectedTable,
  })

  const { data: userStats } = useQuery({
    queryKey: ['admin-user-stats'],
    queryFn: fetchUserStats,
  })

  const { data: systemInfo } = useQuery({
    queryKey: ['admin-system-info'],
    queryFn: fetchSystemInfo,
    refetchInterval: 10000,
  })

  const toggleTableExpand = (tableName: string) => {
    const newExpanded = new Set(expandedTables)
    if (newExpanded.has(tableName)) {
      newExpanded.delete(tableName)
    } else {
      newExpanded.add(tableName)
    }
    setExpandedTables(newExpanded)
  }

  if (dashboardLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="w-12 h-12 border-2 border-white/30 border-t-white rounded-full animate-spin mx-auto mb-4" />
          <p className="text-slate-400">Loading admin dashboard...</p>
        </div>
  row_count: number
}

interface SystemOverview {
  database_stats: {
    total_tables: number
    total_rows: number
    database_size_bytes: number
  }
  user_stats: {
    total_users: number
    active_users: number
    admin_users: number
    dummy_data_users: number
    production_users: number
  }
  tables: TableSchema[]
  recent_audit_logs: Array<{
    id: number
    user_id: number
    action: string
    created_at: string
  }>
}

async function fetchAdminData() {
  const token = localStorage.getItem('access_token')
  const response = await fetch('/api/admin/overview', {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  })
  if (!response.ok) throw new Error('Failed to fetch admin data')
  return response.json() as Promise<SystemOverview>
}

export default function Admin() {
  const [selectedTable, setSelectedTable] = useState<string | null>(null)
  const [tableData, setTableData] = useState<any[]>([])
  const [loadingTable, setLoadingTable] = useState(false)

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['admin-overview'],
    queryFn: fetchAdminData,
  })

  const loadTableData = async (tableName: string) => {
    setLoadingTable(true)
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(`/api/admin/tables/${tableName}/data?limit=100`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })
      if (response.ok) {
        const result = await response.json()
        setTableData(result.data)
      }
    } catch (error) {
      console.error('Failed to load table data:', error)
    } finally {
      setLoadingTable(false)
    }
  }

  useEffect(() => {
    if (selectedTable) {
      loadTableData(selectedTable)
    }
  }, [selectedTable])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-[color:var(--osd-muted)]">Loading admin dashboard...</div>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="text-center py-12">
        <p className="text-red-400">Failed to load admin data</p>
      </div>
    )
  }

  const stats = dashboard?.dashboard

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Admin Panel"
        title="System Administration"
        description="Django-style admin interface with full system visibility. Monitor users, tables, schemas, and system health."
        icon={Shield}
        actions={
          <>
            <span className="pill-muted">
              Admin: {dashboard?.admin_user}
            </span>
            <button
              onClick={() => {
                queryClient.invalidateQueries({ queryKey: ['admin-dashboard'] })
                queryClient.invalidateQueries({ queryKey: ['admin-tables'] })
                toast.success('Dashboard refreshed')
              }}
              className="btn-secondary"
            >
              <RefreshCw className="w-4 h-4" />
              Refresh
            </button>
          </>
        }
      />

      {/* Overview Stats */}
      <section className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard icon={Users} label="Total Users" value={stats?.total_users || 0} detail={`${stats?.active_users || 0} active`} />
        <StatCard icon={Activity} label="Activities (24h)" value={stats?.activities_24h || 0} detail={`${stats?.total_activities || 0} total`} />
        <StatCard icon={Database} label="Tasks" value={stats?.total_tasks || 0} detail="Tracked items" />
        <StatCard icon={FileJson} label="Documents" value={stats?.total_documents || 0} detail="Stored files" />
      </section>

      {/* System Info */}
      {systemInfo && (
        <section className="glass-card p-6">
          <div className="flex items-center gap-3 mb-6">
            <Server className="w-6 h-6 text-primary-400" />
            <div>
              <h3 className="text-xl font-semibold text-white">System Information</h3>
              <p className="text-sm text-slate-400">Real-time system metrics</p>
            </div>
          </div>

          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            <MetricCard label="CPU Usage" value={`${systemInfo.system?.cpu_percent?.toFixed(1)}%`} />
            <MetricCard label="Memory" value={`${systemInfo.system?.memory?.percent?.toFixed(1)}%`} />
            <MetricCard label="Disk Usage" value={`${systemInfo.system?.disk?.percent?.toFixed(1)}%`} />
            <MetricCard label="CPU Cores" value={systemInfo.system?.cpu_count} />
            <MetricCard label="Main DB Size" value={`${(systemInfo.databases?.main_db_size / 1024 / 1024).toFixed(2)} MB`} />
            <MetricCard label="Users DB Size" value={`${(systemInfo.databases?.users_db_size / 1024 / 1024).toFixed(2)} MB`} />
          </div>
        </section>
      )}

      {/* User Statistics */}
      {userStats && (
        <section className="glass-card p-6">
          <div className="flex items-center gap-3 mb-6">
            <Users className="w-6 h-6 text-primary-400" />
            <div>
              <h3 className="text-xl font-semibold text-white">User Analytics</h3>
              <p className="text-sm text-slate-400">User activity and engagement</p>
            </div>
          </div>

          <div className="space-y-6">
            {/* Users by Role */}
            <div>
              <h4 className="text-sm font-semibold text-slate-300 mb-3">Users by Role</h4>
              <div className="grid gap-3 md:grid-cols-3">
                {Object.entries(userStats.users_by_role).map(([role, count]) => (
                  <div key={role} className="p-4 bg-slate-800/50 border border-slate-700/50 rounded-xl">
                    <p className="text-xs text-slate-400 uppercase">{role}</p>
                    <p className="text-2xl font-semibold text-white mt-1">{count}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Most Active Users */}
            <div>
              <h4 className="text-sm font-semibold text-slate-300 mb-3">Most Active Users</h4>
              <div className="space-y-2">
                {userStats.most_active_users.slice(0, 5).map((user) => (
                  <div key={user.username} className="flex items-center justify-between p-3 bg-slate-800/50 border border-slate-700/50 rounded-xl">
                    <div>
                      <p className="text-sm font-medium text-white">{user.username}</p>
                      <p className="text-xs text-slate-400">{user.email}</p>
                    </div>
                    <span className="text-sm font-semibold text-primary-400">{user.activity_count} actions</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>
      )}

      {/* Database Tables */}
      <section className="glass-card p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <Table className="w-6 h-6 text-primary-400" />
            <div>
              <h3 className="text-xl font-semibold text-white">Database Tables</h3>
              <p className="text-sm text-slate-400">Browse and inspect database schemas</p>
            </div>
          </div>

          <select
            value={selectedDatabase}
            onChange={(e) => {
              setSelectedDatabase(e.target.value)
              setSelectedTable(null)
            }}
            className="px-4 py-2 bg-slate-800/80 border border-slate-700/60 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-primary-500/50"
          >
            <option value="main">Main Database</option>
            <option value="users">Users Database</option>
          </select>
        </div>

        {tables && (
          <div className="space-y-2">
            {tables.tables.map((table: TableInfo) => (
              <div key={table.name} className="border border-slate-700/50 rounded-xl overflow-hidden">
                <button
                  onClick={() => toggleTableExpand(table.name)}
                  className="w-full flex items-center justify-between p-4 bg-slate-800/30 hover:bg-slate-800/50 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    {expandedTables.has(table.name) ? (
                      <ChevronDown className="w-4 h-4 text-slate-400" />
                    ) : (
                      <ChevronRight className="w-4 h-4 text-slate-400" />
                    )}
                    <Table className="w-4 h-4 text-primary-400" />
                    <span className="font-mono text-sm text-white">{table.name}</span>
                    <span className="text-xs text-slate-400">({table.row_count} rows)</span>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      setSelectedTable(table.name)
                      setTablePage(1)
                    }}
                    className="btn-tonal text-xs"
                  >
                    <Eye className="w-3 h-3" />
                    View Data
                  </button>
                </button>

                {expandedTables.has(table.name) && (
                  <div className="p-4 bg-slate-800/20 border-t border-slate-700/50">
                    <p className="text-xs font-semibold text-slate-300 mb-2">Columns:</p>
                    <div className="space-y-1">
                      {table.columns.map((col) => (
                        <div key={col.name} className="flex items-center gap-2 text-xs">
                          <span className="font-mono text-primary-400">{col.name}</span>
                          <span className="text-slate-500">{col.type}</span>
                          {col.primary_key && <span className="px-2 py-0.5 bg-amber-500/20 text-amber-300 rounded">PK</span>}
                          {col.not_null && <span className="px-2 py-0.5 bg-red-500/20 text-red-300 rounded">NOT NULL</span>}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Table Data Viewer */}
      {selectedTable && tableData && (
        <section className="glass-card p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-xl font-semibold text-white">Table: {selectedTable}</h3>
              <p className="text-sm text-slate-400">
                Page {tableData.page} of {tableData.total_pages} ({tableData.total_rows} total rows)
              </p>
            </div>
            <button
              onClick={() => setSelectedTable(null)}
              className="btn-secondary text-sm"
            >
              Close
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-700/50">
                  {tableData.rows[0] &&
                    Object.keys(tableData.rows[0]).map((key) => (
                      <th key={key} className="text-left p-3 font-semibold text-slate-300">
                        {key}
                      </th>
                    ))}
                </tr>
              </thead>
              <tbody>
                {tableData.rows.map((row: any, idx: number) => (
                  <tr key={idx} className="border-b border-slate-700/30 hover:bg-slate-800/30">
                    {Object.values(row).map((value: any, colIdx: number) => (
                      <td key={colIdx} className="p-3 text-slate-300 font-mono text-xs">
                        {value === null ? (
                          <span className="text-slate-500 italic">null</span>
                        ) : typeof value === 'object' ? (
                          JSON.stringify(value)
                        ) : (
                          String(value)
                        )}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="flex items-center justify-between mt-6">
            <button
              onClick={() => setTablePage((p) => Math.max(1, p - 1))}
              disabled={tablePage === 1}
              className="btn-secondary text-sm disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            <span className="text-sm text-slate-400">
              Page {tablePage} of {tableData.total_pages}
            </span>
            <button
              onClick={() => setTablePage((p) => Math.min(tableData.total_pages, p + 1))}
              disabled={tablePage === tableData.total_pages}
              className="btn-secondary text-sm disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        </section>
      )}
    </div>
  )
}

function StatCard({ icon: Icon, label, value, detail }: any) {
  return (
    <div className="glass-card p-6">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs uppercase tracking-wider text-slate-400">{label}</p>
          <p className="text-3xl font-semibold text-white mt-2">{value}</p>
          <p className="text-sm text-slate-400 mt-1">{detail}</p>
        </div>
        <div className="p-3 bg-primary-500/20 border border-primary-500/30 rounded-xl">
          <Icon className="w-5 h-5 text-primary-400" />
        </div>
      </div>
    </div>
  )
}

function MetricCard({ label, value }: { label: string; value: any }) {
  return (
    <div className="p-4 bg-slate-800/50 border border-slate-700/50 rounded-xl">
      <p className="text-xs text-slate-400 uppercase">{label}</p>
      <p className="text-2xl font-semibold text-white mt-1">{value}</p>
  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold mb-2">Admin Dashboard</h1>
          <p className="text-[color:var(--osd-muted)]">Holistic system overview and management</p>
        </div>
        <button
          onClick={() => refetch()}
          className="px-4 py-2 bg-[color:var(--osd-surface)] border border-[color:var(--osd-border)] rounded-lg hover:bg-[color:var(--osd-accentSoft)] flex items-center gap-2"
        >
          <RefreshCw className="w-4 h-4" />
          Refresh
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass-content p-6 rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <Database className="w-8 h-8 text-[color:var(--osd-accent)]" />
            <span className="text-2xl font-bold">{data.database_stats.total_tables}</span>
          </div>
          <p className="text-sm text-[color:var(--osd-muted)]">Database Tables</p>
          <p className="text-xs text-[color:var(--osd-muted)] mt-1">
            {formatBytes(data.database_stats.database_size_bytes)}
          </p>
        </div>

        <div className="glass-content p-6 rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <Users className="w-8 h-8 text-[color:var(--osd-accentPurple)]" />
            <span className="text-2xl font-bold">{data.user_stats.total_users}</span>
          </div>
          <p className="text-sm text-[color:var(--osd-muted)]">Total Users</p>
          <p className="text-xs text-[color:var(--osd-muted)] mt-1">
            {data.user_stats.active_users} active
          </p>
        </div>

        <div className="glass-content p-6 rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <Shield className="w-8 h-8 text-green-500" />
            <span className="text-2xl font-bold">{data.user_stats.admin_users}</span>
          </div>
          <p className="text-sm text-[color:var(--osd-muted)]">Admin Users</p>
          <p className="text-xs text-[color:var(--osd-muted)] mt-1">
            {data.user_stats.production_users} production
          </p>
        </div>

        <div className="glass-content p-6 rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <Activity className="w-8 h-8 text-yellow-500" />
            <span className="text-2xl font-bold">{data.user_stats.dummy_data_users}</span>
          </div>
          <p className="text-sm text-[color:var(--osd-muted)]">Test Users</p>
          <p className="text-xs text-[color:var(--osd-muted)] mt-1">
            Dummy data environment
          </p>
        </div>
      </div>

      {/* Tables Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="glass-content p-6 rounded-lg">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <FileText className="w-5 h-5" />
            Database Tables
          </h2>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {data.tables.map((table) => (
              <div
                key={table.name}
                onClick={() => setSelectedTable(table.name)}
                className={`p-3 rounded-lg cursor-pointer transition-colors ${
                  selectedTable === table.name
                    ? 'bg-[color:var(--osd-accentSoft)] border border-[color:var(--osd-accent)]'
                    : 'bg-[color:var(--osd-surface)] hover:bg-[color:var(--osd-accentSoft)]'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium">{table.name}</span>
                  <span className="text-sm text-[color:var(--osd-muted)]">
                    {table.row_count} rows
                  </span>
                </div>
                <div className="text-xs text-[color:var(--osd-muted)] mt-1">
                  {table.columns.length} columns
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Table Data Viewer */}
        <div className="glass-content p-6 rounded-lg">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <Eye className="w-5 h-5" />
            {selectedTable ? `Table: ${selectedTable}` : 'Select a table'}
          </h2>
          {selectedTable ? (
            loadingTable ? (
              <div className="text-center py-8 text-[color:var(--osd-muted)]">Loading...</div>
            ) : tableData.length > 0 ? (
              <div className="overflow-x-auto max-h-96">
                <table className="w-full text-sm">
                  <thead className="sticky top-0 bg-[color:var(--osd-surface)]">
                    <tr>
                      {Object.keys(tableData[0]).map((key) => (
                        <th key={key} className="px-2 py-2 text-left border-b border-[color:var(--osd-border)]">
                          {key}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {tableData.map((row, idx) => (
                      <tr key={idx} className="border-b border-[color:var(--osd-border)]">
                        {Object.values(row).map((val: any, colIdx) => (
                          <td key={colIdx} className="px-2 py-2">
                            {typeof val === 'object' ? JSON.stringify(val).substring(0, 50) : String(val).substring(0, 50)}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-center py-8 text-[color:var(--osd-muted)]">No data</div>
            )
          ) : (
            <div className="text-center py-8 text-[color:var(--osd-muted)]">
              Click on a table to view its data
            </div>
          )}
        </div>
      </div>

      {/* Recent Audit Logs */}
      <div className="glass-content p-6 rounded-lg">
        <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
          <BarChart3 className="w-5 h-5" />
          Recent Audit Logs
        </h2>
        <div className="space-y-2 max-h-64 overflow-y-auto">
          {data.recent_audit_logs.length > 0 ? (
            data.recent_audit_logs.map((log) => (
              <div
                key={log.id}
                className="p-3 bg-[color:var(--osd-surface)] rounded-lg flex items-center justify-between"
              >
                <div>
                  <span className="font-medium">{log.action}</span>
                  <span className="text-sm text-[color:var(--osd-muted)] ml-2">
                    User ID: {log.user_id}
                  </span>
                </div>
                <span className="text-xs text-[color:var(--osd-muted)]">
                  {new Date(log.created_at).toLocaleString()}
                </span>
              </div>
            ))
          ) : (
            <div className="text-center py-4 text-[color:var(--osd-muted)]">No audit logs</div>
          )}
        </div>
      </div>
    </div>
  )
}
