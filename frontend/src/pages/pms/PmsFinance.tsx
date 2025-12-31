import { useQuery } from '@tanstack/react-query'
import { Plus } from 'lucide-react'
import PageHeader from '../../components/PageHeader'
import { pmsApi } from '../../api/pms'
import { useActor } from '../../contexts/ActorContext'
import { formatCurrency } from './pmsUtils'

export default function PmsFinance() {
  const { currentActor } = useActor()

  const { data: expenses = [] } = useQuery({
    queryKey: ['pms-expenses-global', currentActor],
    queryFn: () => pmsApi.listExpenses(undefined, currentActor),
  })

  const { data: timeEntries = [] } = useQuery({
    queryKey: ['pms-time-entries-global', currentActor],
    queryFn: () => pmsApi.listTimeEntries(undefined, currentActor),
  })

  const expenseTotal = expenses.reduce((sum, entry) => sum + entry.amount, 0)
  const laborTotal = timeEntries.reduce((sum, entry) => sum + (entry.labor_cost ?? 0), 0)

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="PMS"
        title="Finance"
        description="Track spend and labor across all projects."
        actions={
          <div className="flex gap-2">
            <button type="button" className="btn btn-secondary">
              <Plus className="w-4 h-4" />
              Add Expense
            </button>
            <button type="button" className="btn btn-secondary">
              <Plus className="w-4 h-4" />
              Add Time Entry
            </button>
          </div>
        }
      />

      <div className="grid gap-4 md:grid-cols-3">
        <div className="glass-card p-4">
          <p className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Total expenses</p>
          <p className="text-2xl font-semibold">{formatCurrency(expenseTotal)}</p>
        </div>
        <div className="glass-card p-4">
          <p className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Total labor</p>
          <p className="text-2xl font-semibold">{formatCurrency(laborTotal)}</p>
        </div>
        <div className="glass-card p-4">
          <p className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Combined</p>
          <p className="text-2xl font-semibold">{formatCurrency(expenseTotal + laborTotal)}</p>
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <div className="glass-card p-5 space-y-3">
          <h2 className="text-sm font-semibold">Expenses</h2>
          <div className="space-y-2 text-sm">
            {expenses.map((expense) => (
              <div key={expense.expense_id} className="flex items-center justify-between">
                <span>{expense.vendor}</span>
                <span>{formatCurrency(expense.amount, expense.currency)}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="glass-card p-5 space-y-3">
          <h2 className="text-sm font-semibold">Time Entries</h2>
          <div className="space-y-2 text-sm">
            {timeEntries.map((entry) => (
              <div key={entry.time_entry_id} className="flex items-center justify-between">
                <span>{entry.role}</span>
                <span>{formatCurrency(entry.labor_cost ?? 0)}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
