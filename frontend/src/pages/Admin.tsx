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
