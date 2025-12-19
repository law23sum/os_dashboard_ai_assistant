import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useState, useEffect } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import {
  Database,
  Users,
  Activity,
  Server,
  FileText,
  Shield,
  Eye,
  RefreshCw,
  ChevronDown,
  ChevronRight,
  BarChart3,
  FileText
  TrendingUp,
  AlertCircle,
  RefreshCw,
  Eye,
  EyeOff,
  ChevronDown,
  ChevronRight,
  Search,
  Filter,
  Table,
  Lock,
  Key,
  BarChart3,
  Clock,
  Hash,
  Check,
  X,
} from 'lucide-react'
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
interface TableSchema {
  name: string
  columns: Array<{
    name: string
    type: string
    not_null: boolean
    primary_key: boolean
    default_value?: string
  }>
  row_count: number
}

interface UserStats {
  total_users: number
  active_users: number
  admin_users: number
  users_by_role: Record<string, number>
  recent_activity: Array<{
    user_id: number
    username: string
    action: string
    created_at: string
  }>
}

interface SystemOverview {
  database_stats: {
    total_tables: number
    total_rows: number
    database_size_bytes: number
  }
  user_stats: UserStats
  tables: TableSchema[]
  system_health: {
    cpu_percent: number
    memory_percent: number
    disk_percent: number
  }
}

// Sensitive columns that should be masked
const SENSITIVE_COLUMNS = ['password', 'password_hash', 'secret', 'token', 'api_key', 'private_key', 'ssn', 'credit_card']

// Columns that indicate boolean values
const BOOLEAN_COLUMNS = ['is_active', 'is_admin', 'is_verified', 'is_deleted', 'enabled', 'active']

async function fetchAdminOverview(): Promise<SystemOverview> {
  const token = localStorage.getItem('access_token')
  const response = await fetch('/api/admin/overview', {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  })
  if (!response.ok) {
    if (response.status === 401 || response.status === 403) {
      throw new Error('Unauthorized: Admin access required')
    }
    throw new Error('Failed to fetch admin data')
  }
  return response.json()
}

async function fetchTableData(tableName: string, page: number = 1, pageSize: number = 50) {
  const token = localStorage.getItem('access_token')
  const response = await fetch(`/api/admin/tables/${tableName}/data?page=${page}&page_size=${pageSize}`, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  })
  if (!response.ok) throw new Error('Failed to fetch table data')
  return response.json()
}

function StatCard({ icon: Icon, label, value, detail, color = 'indigo' }: {
  icon: any
  label: string
  value: string | number
  detail?: string
  color?: 'indigo' | 'green' | 'amber' | 'red'
}) {
  const colorClasses = {
    indigo: 'bg-indigo-500/20 border-indigo-500/30 text-indigo-400',
    green: 'bg-emerald-500/20 border-emerald-500/30 text-emerald-400',
    amber: 'bg-amber-500/20 border-amber-500/30 text-amber-400',
    red: 'bg-red-500/20 border-red-500/30 text-red-400',
  }

  return (
    <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs uppercase tracking-wider text-slate-400">{label}</p>
          <p className="text-3xl font-semibold text-white mt-2">{value}</p>
          {detail && <p className="text-sm text-slate-400 mt-1">{detail}</p>}
        </div>
        <div className={`p-3 rounded-xl border ${colorClasses[color]}`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
    </div>
  )
}

function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`
}

function isSensitiveColumn(columnName: string): boolean {
  return SENSITIVE_COLUMNS.some(s => columnName.toLowerCase().includes(s))
}

function formatCellValue(value: any, columnName: string, showSensitive: boolean): React.ReactNode {
  if (value === null || value === undefined) {
    return <span className="text-slate-500 italic">null</span>
  }

  // Mask sensitive data
  if (isSensitiveColumn(columnName) && !showSensitive) {
    return <span className="text-slate-500 font-mono">••••••••</span>
  }

  // Boolean columns
  if (BOOLEAN_COLUMNS.includes(columnName.toLowerCase()) || typeof value === 'boolean') {
    return value ? (
      <span className="inline-flex items-center gap-1 text-emerald-400">
        <Check className="w-4 h-4" /> Yes
      </span>
    ) : (
      <span className="inline-flex items-center gap-1 text-slate-500">
        <X className="w-4 h-4" /> No
      </span>
    )
  }

  // Timestamps
  if (columnName.includes('_at') || columnName.includes('date') || columnName.includes('time')) {
    try {
      const date = new Date(value)
      if (!isNaN(date.getTime())) {
        return (
          <span className="text-slate-300 tabular-nums">
            {date.toLocaleDateString()} {date.toLocaleTimeString()}
          </span>
        )
      }
    } catch {}
  }

  // JSON objects
  if (typeof value === 'object') {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="w-12 h-12 border-2 border-white/30 border-t-white rounded-full animate-spin mx-auto mb-4" />
          <p className="text-slate-400">Loading admin dashboard...</p>
        </div>
      <span className="font-mono text-xs text-slate-400">
        {JSON.stringify(value).substring(0, 50)}...
      </span>
    )
  }

  // Long strings
  if (typeof value === 'string' && value.length > 100) {
    return <span className="text-slate-300">{value.substring(0, 100)}...</span>
  }

  return <span className="text-slate-300">{String(value)}</span>
}

export default function Admin() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [selectedTable, setSelectedTable] = useState<string | null>(null)
  const [tableData, setTableData] = useState<any[]>([])
  const [tablePage, setTablePage] = useState(1)
  const [loadingTable, setLoadingTable] = useState(false)
  const [expandedTables, setExpandedTables] = useState<Set<string>>(new Set())
  const [showSensitive, setShowSensitive] = useState(false)
  const [searchFilter, setSearchFilter] = useState('')

  // Check if user is admin
  useEffect(() => {
    const user = localStorage.getItem('user')
    if (user) {
      const userData = JSON.parse(user)
      if (userData.role !== 'admin') {
        navigate('/login')
      }
    } else {
      navigate('/login')
    }
  }, [navigate])

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['admin-overview'],
    queryFn: fetchAdminOverview,
    refetchInterval: 30000, // Refresh every 30 seconds
    retry: 1,
  })

  const loadTableData = async (tableName: string, page: number = 1) => {
    setLoadingTable(true)
    try {
      const result = await fetchTableData(tableName, page)
      setTableData(result.data || result.rows || [])
      setTablePage(page)
    } catch (error) {
      console.error('Failed to load table data:', error)
      setTableData([])
    } finally {
      setLoadingTable(false)
    }
  }

  useEffect(() => {
    if (selectedTable) {
      loadTableData(selectedTable, 1)
    }
  }, [selectedTable])

  const toggleTableExpand = (tableName: string) => {
    const newExpanded = new Set(expandedTables)
    if (newExpanded.has(tableName)) {
      newExpanded.delete(tableName)
    } else {
      newExpanded.add(tableName)
    }
    setExpandedTables(newExpanded)
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="w-12 h-12 border-2 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin mx-auto mb-4" />
          <p className="text-slate-400">Loading admin dashboard...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
          <p className="text-red-400 font-semibold">Access Denied</p>
          <p className="text-slate-400 mt-2">You don't have permission to access this page.</p>
          <button
            onClick={() => navigate('/login')}
            className="mt-4 px-4 py-2 bg-indigo-500 text-white rounded-lg hover:bg-indigo-600 transition-colors"
          >
            Go to Login
          </button>
        </div>
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

  const filteredTables = data.tables.filter(table =>
    table.name.toLowerCase().includes(searchFilter.toLowerCase())
  )
import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Eye, RefreshCw, Shield, Table } from 'lucide-react'
import PageHeader from '../components/PageHeader'

type AdminDashboard = {
  dashboard: {
    total_users: number
    active_users: number
    admin_users: number
    total_activities: number
    total_tasks: number
    total_projects: number
    total_chat_messages: number
    total_documents: number
  }
  timestamp: string
  admin_user: string
}

type TableColumn = {
  name: string
  type: string
  not_null: boolean
  primary_key: boolean
  sensitive?: boolean
}

type TableInfo = {
  name: string
  row_count: number
  columns: TableColumn[]
}

type TablesResponse = {
  database: 'main' | 'users'
  tables: TableInfo[]
}

type TableDataResponse = {
  table: string
  database: 'main' | 'users'
  page: number
  page_size: number
  total_rows: number
  total_pages: number
  rows: Array<Record<string, unknown>>
}

const authHeaders = (): HeadersInit => {
  const token = localStorage.getItem('access_token')
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  }
}

const fetchJson = async <T,>(url: string): Promise<T> => {
  const res = await fetch(url, { headers: authHeaders() })
  const data = await res.json().catch(() => ({}))
  if (!res.ok) throw new Error((data as any).detail || `Request failed (${res.status})`)
  return data as T
}

export default function Admin() {
  const [database, setDatabase] = useState<'main' | 'users'>('main')
  const [selectedTable, setSelectedTable] = useState<string | null>(null)
  const [page, setPage] = useState(1)
  const [revealSensitive, setRevealSensitive] = useState(false)

  const { data: dashboard, refetch: refetchDashboard, isFetching: fetchingDashboard } = useQuery({
    queryKey: ['admin-dashboard'],
    queryFn: () => fetchJson<AdminDashboard>('/api/admin/dashboard'),
    refetchInterval: 30000,
  })

  const { data: tables, refetch: refetchTables, isFetching: fetchingTables } = useQuery({
    queryKey: ['admin-tables', database],
    queryFn: () => fetchJson<TablesResponse>(`/api/admin/tables?database=${database}`),
  })

  const { data: tableData, isFetching: fetchingTableData } = useQuery({
    queryKey: ['admin-table-data', database, selectedTable, page, revealSensitive],
    queryFn: () =>
      fetchJson<TableDataResponse>(
        `/api/admin/tables/${encodeURIComponent(selectedTable || '')}/data?database=${database}&page=${page}&page_size=50&reveal_sensitive=${revealSensitive ? 'true' : 'false'}`
      ),
    enabled: !!selectedTable,
    keepPreviousData: true,
  })

  const stats = dashboard?.dashboard

  const selected = useMemo(() => {
    if (!tables || !selectedTable) return null
    return tables.tables.find((t) => t.name === selectedTable) || null
  }, [tables, selectedTable])

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Administration"
        title="Admin Panel"
        description="Django-style admin interface with full system visibility. Monitor users, database schemas, and system health."
        icon={Shield}
        actions={
          <div className="flex items-center gap-3">
            <button
              onClick={() => setShowSensitive(!showSensitive)}
              className={`px-3 py-2 rounded-lg flex items-center gap-2 text-sm transition-colors ${
                showSensitive
                  ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                  : 'bg-slate-800/50 text-slate-400 border border-slate-700/50 hover:text-white'
              }`}
            >
              {showSensitive ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              {showSensitive ? 'Hide Sensitive' : 'Show Sensitive'}
            </button>
            <button
              onClick={() => {
                queryClient.invalidateQueries({ queryKey: ['admin-dashboard'] })
                queryClient.invalidateQueries({ queryKey: ['admin-tables'] })
                queryClient.invalidateQueries({ queryKey: ['admin-user-stats'] })
                queryClient.invalidateQueries({ queryKey: ['admin-system-info'] })
                toast.success('Dashboard refreshed')
                queryClient.invalidateQueries({ queryKey: ['admin-overview'] })
                refetch()
              }}
              className="px-4 py-2 bg-slate-800/50 border border-slate-700/50 rounded-lg flex items-center gap-2 text-sm hover:bg-slate-700/50 transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
              Refresh
            </button>
          </div>
        eyebrow="Admin"
        title="System Administration"
        description="Django-style visibility over schemas, tables, and system state. Sensitive fields are masked by default."
        icon={Shield}
        actions={
          <button
            onClick={() => {
              refetchDashboard()
              refetchTables()
            }}
            className="btn-secondary"
            disabled={fetchingDashboard || fetchingTables}
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
        }
      />

      {/* Overview */}
      <section className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          icon={Database}
          label="Database Tables"
          value={data.database_stats.total_tables}
          detail={formatBytes(data.database_stats.database_size_bytes)}
          color="indigo"
        />
        <StatCard
          icon={Users}
          label="Total Users"
          value={data.user_stats.total_users}
          detail={`${data.user_stats.active_users} active`}
          color="green"
        />
        <StatCard
          icon={Shield}
          label="Admin Users"
          value={data.user_stats.admin_users}
          detail="With full access"
          color="amber"
        />
        <StatCard
          icon={Hash}
          label="Total Rows"
          value={data.database_stats.total_rows.toLocaleString()}
          detail="Across all tables"
          color="indigo"
        />
      </section>

      {/* System Health */}
      {data.system_health && (
        <section className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6">
          <div className="flex items-center gap-3 mb-6">
            <Server className="w-6 h-6 text-indigo-400" />
            <div>
              <h3 className="text-xl font-semibold text-white">System Health</h3>
              <p className="text-sm text-slate-400">Real-time system metrics</p>
            </div>
          </div>

          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            <MetricCard label="CPU Usage" value={`${systemInfo.system?.cpu_percent?.toFixed(1)}%`} />
            <MetricCard label="Memory" value={`${systemInfo.system?.memory?.percent?.toFixed(1)}%`} />
            <MetricCard label="Disk Usage" value={`${systemInfo.system?.disk?.percent?.toFixed(1)}%`} />
            <MetricCard label="CPU Cores" value={systemInfo.system?.cpu_count} />
            <MetricCard label="Main DB Size" value={systemInfo.databases?.main_db_size ? `${(systemInfo.databases.main_db_size / 1024 / 1024).toFixed(2)} MB` : 'N/A'} />
            <MetricCard label="Users DB Size" value={systemInfo.databases?.users_db_size ? `${(systemInfo.databases.users_db_size / 1024 / 1024).toFixed(2)} MB` : 'N/A'} />
          </div>
        </section>
      )}
          <div className="grid gap-4 md:grid-cols-3">
            <HealthMetric label="CPU Usage" value={data.system_health.cpu_percent} />
            <HealthMetric label="Memory" value={data.system_health.memory_percent} />
            <HealthMetric label="Disk" value={data.system_health.disk_percent} />
        <StatCard label="Users" value={stats?.total_users ?? 0} detail={`${stats?.active_users ?? 0} active`} />
        <StatCard label="Admins" value={stats?.admin_users ?? 0} detail="Role-based access" />
        <StatCard label="Tasks" value={stats?.total_tasks ?? 0} detail="Scoped by owner" />
        <StatCard label="Documents" value={stats?.total_documents ?? 0} detail="Stored artifacts" />
      </section>

      {/* Tables */}
      <section className="glass-card p-6">
        <div className="flex items-center justify-between gap-3 mb-4">
          <div className="flex items-center gap-2">
            <Table className="w-5 h-5 text-[color:var(--osd-muted)]" />
            <h2 className="text-sm font-semibold">Schema browser</h2>
          </div>
          <div className="flex items-center gap-2">
            <select
              className="px-3 py-2 rounded-lg bg-[color:var(--osd-surface)] border border-[color:var(--osd-border)] text-sm"
              value={database}
              onChange={(e) => {
                setDatabase(e.target.value as 'main' | 'users')
                setSelectedTable(null)
                setPage(1)
              }}
            >
              <option value="main">Main DB</option>
              <option value="users">Users DB</option>
            </select>

            <label className="flex items-center gap-2 text-sm text-[color:var(--osd-muted)]">
              <input
                type="checkbox"
                checked={revealSensitive}
                onChange={(e) => setRevealSensitive(e.target.checked)}
              />
              Reveal sensitive
            </label>
          </div>
        </div>

        <div className="grid gap-4 lg:grid-cols-2">
          <div className="rounded-xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]/30 overflow-hidden">
            <div className="p-3 border-b border-[color:var(--osd-border)] text-sm font-semibold">Tables</div>
            <div className="max-h-[28rem] overflow-y-auto">
              {tables?.tables.map((t) => (
                <button
                  key={t.name}
                  type="button"
                  onClick={() => {
                    setSelectedTable(t.name)
                    setPage(1)
                  }}
                  className={`w-full text-left px-4 py-3 border-b border-[color:var(--osd-border)]/60 hover:bg-[color:var(--osd-surface)] transition-colors ${
                    selectedTable === t.name ? 'bg-[color:var(--osd-accentSoft)]' : ''
                  }`}
                >
                  <div className="flex items-center justify-between gap-3">
                    <span className="font-mono text-sm">{t.name}</span>
                    <span className="text-xs text-[color:var(--osd-muted)]">{t.row_count} rows</span>
                  </div>
                  <div className="mt-1 text-xs text-[color:var(--osd-muted)]">{t.columns.length} columns</div>
                </button>
              ))}
              {!tables?.tables.length ? (
                <div className="p-4 text-sm text-[color:var(--osd-muted)]">No tables found.</div>
              ) : null}
            </div>
          </div>

      {/* Database Tables - Django Style */}
      <section className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <Table className="w-6 h-6 text-indigo-400" />
            <div>
              <h3 className="text-xl font-semibold text-white">Database Tables</h3>
              <p className="text-sm text-slate-400">Browse and inspect database schemas</p>
          <div className="rounded-xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]/30 overflow-hidden">
            <div className="p-3 border-b border-[color:var(--osd-border)] flex items-center justify-between">
              <div className="text-sm font-semibold">{selectedTable ? `Data: ${selectedTable}` : 'Select a table'}</div>
              {selectedTable ? (
                <span className="text-xs text-[color:var(--osd-muted)]">
                  {fetchingTableData ? 'Loading…' : `${tableData?.total_rows ?? 0} rows`}
                </span>
              ) : null}
            </div>

          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              placeholder="Filter tables..."
              value={searchFilter}
              onChange={(e) => setSearchFilter(e.target.value)}
              className="pl-10 pr-4 py-2 bg-slate-900/50 border border-slate-700/50 rounded-lg text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
            />
          </div>
        </div>

        <div className="space-y-2">
          {filteredTables.map((table) => (
            <div key={table.name} className="border border-slate-700/50 rounded-xl overflow-hidden">
              <button
                onClick={() => toggleTableExpand(table.name)}
                className="w-full flex items-center justify-between p-4 bg-slate-900/30 hover:bg-slate-900/50 transition-colors"
              >
                <div className="flex items-center gap-3">
                  {expandedTables.has(table.name) ? (
                    <ChevronDown className="w-4 h-4 text-slate-400" />
                  ) : (
                    <ChevronRight className="w-4 h-4 text-slate-400" />
                  )}
                  <Database className="w-4 h-4 text-indigo-400" />
                  <span className="font-mono text-sm text-white">{table.name}</span>
                  <span className="text-xs text-slate-400">({table.row_count} rows)</span>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    setSelectedTable(table.name)
                  }}
                  className="px-3 py-1.5 bg-indigo-500/20 text-indigo-400 border border-indigo-500/30 rounded-lg text-xs hover:bg-indigo-500/30 transition-colors"
                >
                  <Eye className="w-3 h-3 inline mr-1" />
                  View Data
                </button>
              </button>

              {expandedTables.has(table.name) && (
                <div className="p-4 bg-slate-900/20 border-t border-slate-700/50">
                  <p className="text-xs font-semibold text-slate-300 mb-3">Schema Columns:</p>
                  <div className="grid gap-2 md:grid-cols-2 lg:grid-cols-3">
                    {table.columns.map((col) => (
                      <div
                        key={col.name}
                        className="flex items-center gap-2 p-2 bg-slate-800/50 rounded-lg text-xs"
                      >
                        {isSensitiveColumn(col.name) ? (
                          <Lock className="w-3 h-3 text-amber-400" />
                        ) : col.primary_key ? (
                          <Key className="w-3 h-3 text-indigo-400" />
                        ) : (
                          <Hash className="w-3 h-3 text-slate-500" />
                        )}
                        <span className="font-mono text-indigo-400">{col.name}</span>
                        <span className="text-slate-500">{col.type}</span>
                        {col.primary_key && (
                          <span className="px-1.5 py-0.5 bg-indigo-500/20 text-indigo-400 rounded text-[10px]">
                            PK
                          </span>
                        )}
                        {col.not_null && (
                          <span className="px-1.5 py-0.5 bg-red-500/20 text-red-400 rounded text-[10px]">
                            NOT NULL
                          </span>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* Table Data Viewer - Django Style */}
      {selectedTable && (
        <section className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-xl font-semibold text-white">
                Table: <span className="font-mono text-indigo-400">{selectedTable}</span>
              </h3>
              <p className="text-sm text-slate-400">
                Showing {tableData.length} records
              </p>
            </div>
            <button
              onClick={() => {
                setSelectedTable(null)
                setTableData([])
              }}
              className="px-4 py-2 bg-slate-700/50 text-slate-300 rounded-lg text-sm hover:bg-slate-600/50 transition-colors"
            >
              Close
            </button>
          </div>

          {loadingTable ? (
            <div className="flex items-center justify-center py-12">
              <div className="w-8 h-8 border-2 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin" />
            </div>
          ) : tableData.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-700/50">
                    {Object.keys(tableData[0]).map((key) => (
                      <th
                        key={key}
                        className="text-left p-3 font-semibold text-slate-300 bg-slate-900/30 first:rounded-tl-lg last:rounded-tr-lg"
                      >
                        <div className="flex items-center gap-2">
                          {isSensitiveColumn(key) && <Lock className="w-3 h-3 text-amber-400" />}
                          {key}
                        </div>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {tableData.map((row: any, idx: number) => (
                    <tr
                      key={idx}
                      className="border-b border-slate-700/30 hover:bg-slate-800/30 transition-colors"
                    >
                      {Object.entries(row).map(([key, value]: [string, any], colIdx: number) => (
                        <td key={colIdx} className="p-3 font-mono text-xs">
                          {formatCellValue(value, key, showSensitive)}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-8 text-slate-400">No data in this table</div>
          )}
        </section>
      )}

function MetricCard({ label, value }: { label: string; value: any }) {
  return (
    <div className="p-4 bg-slate-800/50 border border-slate-700/50 rounded-xl">
      <p className="text-xs text-slate-400 uppercase">{label}</p>
      <p className="text-2xl font-semibold text-white mt-1">{value}</p>
      {/* Recent Activity */}
      {data.user_stats.recent_activity && data.user_stats.recent_activity.length > 0 && (
        <section className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-6">
          <div className="flex items-center gap-3 mb-6">
            <Activity className="w-6 h-6 text-indigo-400" />
            <div>
              <h3 className="text-xl font-semibold text-white">Recent Activity</h3>
              <p className="text-sm text-slate-400">Latest user actions</p>
            </div>
          </div>

          <div className="space-y-2">
            {data.user_stats.recent_activity.slice(0, 10).map((activity, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between p-3 bg-slate-900/30 rounded-lg"
              >
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-indigo-500/20 flex items-center justify-center">
                    <span className="text-sm text-indigo-400">
                      {activity.username?.charAt(0).toUpperCase() || '?'}
                    </span>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-white">{activity.username}</p>
                    <p className="text-xs text-slate-400">{activity.action}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2 text-xs text-slate-400">
                  <Clock className="w-3 h-3" />
                  {new Date(activity.created_at).toLocaleString()}
                </div>
              </div>
            ))}
          </div>
        </section>
      )}
            {selectedTable && selected ? (
              <div className="p-3 border-b border-[color:var(--osd-border)]">
                <div className="text-xs text-[color:var(--osd-muted)] mb-2">Columns</div>
                <div className="flex flex-wrap gap-2">
                  {selected.columns.map((c) => (
                    <span
                      key={c.name}
                      className={`px-2 py-1 rounded-lg text-xs border ${
                        c.sensitive ? 'border-red-500/30 bg-red-500/10 text-red-200' : 'border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]/40'
                      }`}
                      title={c.type}
                    >
                      {c.name}
                    </span>
                  ))}
                </div>
              </div>
            ) : null}

            {selectedTable ? (
              <div className="max-h-[22rem] overflow-auto">
                {tableData?.rows?.length ? (
                  <table className="w-full text-xs">
                    <thead className="sticky top-0 bg-[color:var(--osd-surface)]">
                      <tr>
                        {Object.keys(tableData.rows[0]).map((key) => (
                          <th key={key} className="text-left px-3 py-2 border-b border-[color:var(--osd-border)] font-semibold">
                            {key}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {tableData.rows.map((row, idx) => (
                        <tr key={idx} className="border-b border-[color:var(--osd-border)]/60 hover:bg-[color:var(--osd-surface)]/40">
                          {Object.values(row).map((val, colIdx) => (
                            <td key={colIdx} className="px-3 py-2 font-mono">
                              {val === null ? 'null' : typeof val === 'object' ? JSON.stringify(val) : String(val)}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                ) : (
                  <div className="p-4 text-sm text-[color:var(--osd-muted)]">No data (or table empty).</div>
                )}
              </div>
            ) : (
              <div className="p-4 text-sm text-[color:var(--osd-muted)]">Choose a table on the left.</div>
            )}

            {selectedTable && tableData ? (
              <div className="p-3 border-t border-[color:var(--osd-border)] flex items-center justify-between">
                <button
                  className="btn-secondary text-xs"
                  disabled={page <= 1}
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                >
                  Previous
                </button>
                <span className="text-xs text-[color:var(--osd-muted)]">
                  Page {tableData.page} / {tableData.total_pages}
                </span>
                <button
                  className="btn-secondary text-xs"
                  disabled={page >= tableData.total_pages}
                  onClick={() => setPage((p) => Math.min(tableData.total_pages, p + 1))}
                >
                  Next
                </button>
              </div>
            ) : null}
          </div>
        </div>

        <div className="mt-4 text-xs text-[color:var(--osd-muted)] flex items-center gap-2">
          <Eye className="w-3.5 h-3.5" />
          Sensitive fields are masked unless “Reveal sensitive” is enabled.
        </div>
      </section>
    </div>
  )
}

function HealthMetric({ label, value }: { label: string; value: number }) {
  const color = value > 80 ? 'red' : value > 60 ? 'amber' : 'emerald'
  const colorClasses = {
    red: 'bg-red-500',
    amber: 'bg-amber-500',
    emerald: 'bg-emerald-500',
  }

  return (
    <div className="p-4 bg-slate-900/30 rounded-xl">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-slate-400">{label}</span>
        <span className="text-lg font-semibold text-white">{value?.toFixed(1) || 0}%</span>
      </div>
      <div className="h-2 bg-slate-700/50 rounded-full overflow-hidden">
        <div
          className={`h-full ${colorClasses[color]} transition-all duration-500`}
          style={{ width: `${Math.min(value || 0, 100)}%` }}
        />
function StatCard({ label, value, detail }: { label: string; value: number; detail: string }) {
  return (
    <div className="glass-card p-5">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">{label}</p>
          <p className="text-3xl font-semibold text-[color:var(--osd-text)] mt-2">{value}</p>
          <p className="text-sm text-[color:var(--osd-muted)] mt-1">{detail}</p>
        </div>
      </div>
    </div>
  )
}