import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import apiClient, { apiPath } from '../lib/apiClient'

type ColumnInfo = {
  name: string
  type: string
  notnull: boolean
  pk: boolean
  default?: string | null
}

type TableInfo = {
  name: string
  columns: ColumnInfo[]
  row_count: number
}

type SchemaResponse = {
  tables: TableInfo[]
}

type TableRowsResponse = {
  table: string
  columns: string[]
  rows: Record<string, any>[]
  limit: number
  offset: number
  total: number
}

const fetchSchema = async (): Promise<SchemaResponse> => {
  const { data } = await apiClient.get<SchemaResponse>(apiPath('admin/schema'))
  return data
}

const fetchRows = async (table: string, offset: number): Promise<TableRowsResponse> => {
  const { data } = await apiClient.get<TableRowsResponse>(
    apiPath(`admin/table/${encodeURIComponent(table)}?limit=50&offset=${offset}`),
  )
  return data
}

export default function Admin() {
  const [selectedTable, setSelectedTable] = useState<string | null>(null)
  const [offset, setOffset] = useState(0)

  const { data: schema } = useQuery({ queryKey: ['admin-schema'], queryFn: fetchSchema })

  const { data: rows } = useQuery({
    queryKey: ['admin-table', selectedTable, offset],
    queryFn: () => fetchRows(selectedTable!, offset),
    enabled: !!selectedTable,
  })

  const tables = schema?.tables ?? []
  const active = tables.find((t) => t.name === selectedTable) ?? null

  const pages = useMemo(() => {
    if (!rows) return { page: 1, totalPages: 1 }
    const page = Math.floor(rows.offset / rows.limit) + 1
    const totalPages = Math.max(1, Math.ceil(rows.total / rows.limit))
    return { page, totalPages }
  }, [rows])

  return (
    <div className="px-4 py-6 sm:px-0 space-y-6 text-slate-100">
      <section className="glass-card">
        <p className="eyebrow-text">Admin Console</p>
        <h1 className="mt-2 text-2xl font-semibold text-white">Database Schema Explorer</h1>
        <p className="mt-2 text-sm text-slate-300">
          Django-admin-style visibility into tables, schemas, and live rows.
        </p>
      </section>

      <div className="grid gap-6 lg:grid-cols-3">
        <section className="glass-card lg:col-span-1">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold text-white">Tables</h2>
            <span className="pill-muted">{tables.length}</span>
          </div>
          <div className="mt-4 space-y-2 max-h-[65vh] overflow-y-auto">
            {tables.map((t) => (
              <button
                key={t.name}
                onClick={() => {
                  setSelectedTable(t.name)
                  setOffset(0)
                }}
                className={`w-full text-left rounded-xl border px-4 py-3 transition ${
                  selectedTable === t.name
                    ? 'border-primary-500/60 bg-primary-500/10'
                    : 'border-white/10 bg-white/5 hover:border-white/25'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono text-sm text-white">{t.name}</span>
                  <span className="text-xs text-slate-300">{t.row_count} rows</span>
                </div>
                <p className="mt-1 text-xs text-slate-400">{t.columns.length} columns</p>
              </button>
            ))}
          </div>
        </section>

        <section className="glass-card lg:col-span-2">
          {!active ? (
            <div className="text-sm text-slate-300">Select a table to inspect columns and rows.</div>
          ) : (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-lg font-semibold text-white font-mono">{active.name}</h2>
                  <p className="text-xs text-slate-400">
                    Columns: {active.columns.length} · Rows: {active.row_count}
                  </p>
                </div>
                {rows && (
                  <div className="flex items-center gap-2">
                    <button
                      className="rounded-lg border border-white/10 bg-white/5 px-3 py-1.5 text-xs hover:border-white/25 disabled:opacity-50"
                      disabled={offset === 0}
                      onClick={() => setOffset((v) => Math.max(0, v - (rows?.limit ?? 50)))}
                    >
                      Prev
                    </button>
                    <span className="text-xs text-slate-300">
                      {pages.page}/{pages.totalPages}
                    </span>
                    <button
                      className="rounded-lg border border-white/10 bg-white/5 px-3 py-1.5 text-xs hover:border-white/25 disabled:opacity-50"
                      disabled={pages.page >= pages.totalPages}
                      onClick={() => setOffset((v) => v + (rows?.limit ?? 50))}
                    >
                      Next
                    </button>
                  </div>
                )}
              </div>

              <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                <h3 className="text-xs uppercase tracking-[0.2em] text-slate-400">Columns</h3>
                <div className="mt-3 grid gap-2 sm:grid-cols-2">
                  {active.columns.map((c) => (
                    <div key={c.name} className="rounded-xl border border-white/10 bg-black/20 p-3">
                      <div className="flex items-center justify-between">
                        <span className="font-mono text-sm text-white">{c.name}</span>
                        <span className="text-[10px] text-slate-400">{c.type}</span>
                      </div>
                      <p className="mt-1 text-[11px] text-slate-400">
                        {c.pk ? 'PK · ' : ''}
                        {c.notnull ? 'NOT NULL · ' : ''}
                        {c.default ? `DEFAULT ${c.default}` : '—'}
                      </p>
                    </div>
                  ))}
                </div>
              </div>

              <div className="rounded-2xl border border-white/10 bg-white/5 p-4 overflow-x-auto">
                <h3 className="text-xs uppercase tracking-[0.2em] text-slate-400">Rows</h3>
                {!rows ? (
                  <div className="mt-3 text-sm text-slate-300">Loading rows…</div>
                ) : rows.rows.length === 0 ? (
                  <div className="mt-3 text-sm text-slate-300">No rows.</div>
                ) : (
                  <table className="mt-3 w-full text-xs">
                    <thead>
                      <tr className="text-slate-300">
                        {rows.columns.map((c) => (
                          <th key={c} className="text-left font-semibold pb-2 pr-3 whitespace-nowrap">
                            {c}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="text-slate-200">
                      {rows.rows.map((r, idx) => (
                        <tr key={idx} className="border-t border-white/5">
                          {rows.columns.map((c) => (
                            <td key={c} className="py-2 pr-3 align-top whitespace-pre-wrap">
                              {typeof r[c] === 'object' && r[c] !== null ? JSON.stringify(r[c]) : String(r[c] ?? '')}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            </div>
          )}
        </section>
      </div>
    </div>
  )
}

