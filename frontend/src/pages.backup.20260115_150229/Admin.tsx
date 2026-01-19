import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Eye, RefreshCw, Shield, Table } from 'lucide-react'
import { useAuth } from '../auth/AuthContext'
import PageHeader from '../components/PageHeader'
import apiClient, { apiPath } from '../lib/apiClient'

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

const fetchJson = async <T,>(url: string): Promise<T> => {
  const { data } = await apiClient.get<T>(apiPath(url.replace(/^\/api\//, '')))
  return data
}

function StatCard({ label, value, detail }: { label: string; value: number; detail?: string }) {
  return (
    <div className="glass-card p-5">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">{label}</p>
          <p className="text-3xl font-semibold text-[color:var(--osd-text)] mt-2">{value}</p>
          {detail && <p className="text-sm text-[color:var(--osd-muted)] mt-1">{detail}</p>}
        </div>
      </div>
    </div>
  )
}

export default function Admin() {
  const { state } = useAuth()
  const [database, setDatabase] = useState<'main' | 'users'>('main')
  const [selectedTable, setSelectedTable] = useState<string | null>(null)
  const [page, setPage] = useState(1)
  const [revealSensitive, setRevealSensitive] = useState(false)

  // Check admin status - RequireAdmin wrapper should handle this, but double-check
  if (state.status !== 'authenticated' || !state.user.is_admin) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <Shield className="w-12 h-12 text-red-400 mx-auto mb-4" />
          <p className="text-red-400 font-semibold">Access Denied</p>
          <p className="text-[color:var(--osd-muted)] mt-2">Admin privileges required.</p>
        </div>
      </div>
    )
  }

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
  })

  const stats = dashboard?.dashboard

  const selected = useMemo(() => {
    if (!tables || !selectedTable) return null
    return tables.tables.find((t) => t.name === selectedTable) || null
  }, [tables, selectedTable])

  return (
    <div className="space-y-6">
      <PageHeader
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

      {/* Overview Stats */}
      <section className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
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

          <div className="rounded-xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]/30 overflow-hidden">
            <div className="p-3 border-b border-[color:var(--osd-border)] flex items-center justify-between">
              <div className="text-sm font-semibold">{selectedTable ? `Data: ${selectedTable}` : 'Select a table'}</div>
              {selectedTable ? (
                <span className="text-xs text-[color:var(--osd-muted)]">
                  {fetchingTableData ? 'Loading…' : `${tableData?.total_rows ?? 0} rows`}
                </span>
              ) : null}
            </div>

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
                          {Object.values(row).map((val, colIdx) => {
                            // Mask sensitive data if column is sensitive and revealSensitive is false
                            const columnName = Object.keys(row)[colIdx]
                            const isSensitive = selected?.columns.find(c => c.name === columnName)?.sensitive
                            const displayValue = isSensitive && !revealSensitive ? '••••••••' : val
                            
                            return (
                              <td key={colIdx} className="px-3 py-2 font-mono">
                                {displayValue === null ? 'null' : typeof displayValue === 'object' ? JSON.stringify(displayValue) : String(displayValue)}
                              </td>
                            )
                          })}
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
          Sensitive fields are masked unless "Reveal sensitive" is enabled.
        </div>
      </section>
    </div>
  )
}
