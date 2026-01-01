import { useEffect, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Plus } from 'lucide-react'
import PageHeader from '@/components/PageHeader'
import { pmsApi } from '../../api/pms'
import { useActor } from '../../contexts/ActorContext'
import { formatCurrency } from './pmsUtils'

export default function PmsFinance() {
  const { currentActor } = useActor()
  const queryClient = useQueryClient()
  const [showExpenseForm, setShowExpenseForm] = useState(false)
  const [showTimeForm, setShowTimeForm] = useState(false)
  const [expenseProjectId, setExpenseProjectId] = useState('')
  const [expenseAmount, setExpenseAmount] = useState('')
  const [expenseCurrency, setExpenseCurrency] = useState('USD')
  const [expenseCategory, setExpenseCategory] = useState('')
  const [expenseVendor, setExpenseVendor] = useState('')
  const [expenseDescription, setExpenseDescription] = useState('')
  const [timeProjectId, setTimeProjectId] = useState('')
  const [timeRole, setTimeRole] = useState('')
  const [timeActor, setTimeActor] = useState('')
  const [timeDuration, setTimeDuration] = useState('')
  const [timeRate, setTimeRate] = useState('')

  const { data: projects = [] } = useQuery({
    queryKey: ['pms-projects', currentActor],
    queryFn: () => pmsApi.listProjects(currentActor),
  })

  useEffect(() => {
    if (!expenseProjectId && projects.length > 0) {
      setExpenseProjectId(projects[0].project_id)
    }
    if (!timeProjectId && projects.length > 0) {
      setTimeProjectId(projects[0].project_id)
    }
  }, [expenseProjectId, timeProjectId, projects])

  const { data: expenses = [] } = useQuery({
    queryKey: ['pms-expenses-global', currentActor],
    queryFn: () => pmsApi.listExpenses(undefined, currentActor),
  })

  const { data: timeEntries = [] } = useQuery({
    queryKey: ['pms-time-entries-global', currentActor],
    queryFn: () => pmsApi.listTimeEntries(undefined, currentActor),
  })

  const addExpense = useMutation({
    mutationFn: () =>
      pmsApi.addExpense(
        {
          project_id: expenseProjectId,
          amount: Number(expenseAmount),
          currency: expenseCurrency || 'USD',
          category: expenseCategory || undefined,
          vendor: expenseVendor || undefined,
          description: expenseDescription || undefined,
        },
        currentActor,
      ),
    onSuccess: () => {
      setExpenseAmount('')
      setExpenseCategory('')
      setExpenseVendor('')
      setExpenseDescription('')
      queryClient.invalidateQueries({ queryKey: ['pms-expenses-global'] })
    },
  })

  const addTimeEntry = useMutation({
    mutationFn: () =>
      pmsApi.addTimeEntry(
        {
          project_id: timeProjectId,
          actor_id: timeActor || undefined,
          role: timeRole || undefined,
          duration_minutes: Number(timeDuration),
          hourly_rate: Number(timeRate),
        },
        currentActor,
      ),
    onSuccess: () => {
      setTimeActor('')
      setTimeRole('')
      setTimeDuration('')
      setTimeRate('')
      queryClient.invalidateQueries({ queryKey: ['pms-time-entries-global'] })
    },
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
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => setShowExpenseForm((prev) => !prev)}
            >
              <Plus className="w-4 h-4" />
              Add Expense
            </button>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => setShowTimeForm((prev) => !prev)}
            >
              <Plus className="w-4 h-4" />
              Add Time Entry
            </button>
          </div>
        }
      />

      {showExpenseForm && (
        <div className="glass-card p-4 grid gap-3 md:grid-cols-[1fr_1fr_1fr]">
          <select
            className="rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2 text-sm"
            value={expenseProjectId}
            onChange={(event) => setExpenseProjectId(event.target.value)}
          >
            {projects.map((project) => (
              <option key={project.project_id} value={project.project_id}>
                {project.name}
              </option>
            ))}
          </select>
          <input
            className="rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2 text-sm"
            placeholder="Amount"
            value={expenseAmount}
            onChange={(event) => setExpenseAmount(event.target.value)}
          />
          <input
            className="rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2 text-sm"
            placeholder="Currency (USD)"
            value={expenseCurrency}
            onChange={(event) => setExpenseCurrency(event.target.value.toUpperCase())}
          />
          <input
            className="rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2 text-sm"
            placeholder="Category"
            value={expenseCategory}
            onChange={(event) => setExpenseCategory(event.target.value)}
          />
          <input
            className="rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2 text-sm"
            placeholder="Vendor"
            value={expenseVendor}
            onChange={(event) => setExpenseVendor(event.target.value)}
          />
          <input
            className="rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2 text-sm"
            placeholder="Description"
            value={expenseDescription}
            onChange={(event) => setExpenseDescription(event.target.value)}
          />
          <button
            type="button"
            className="btn btn-secondary md:col-span-3"
            disabled={!expenseProjectId || !expenseAmount || addExpense.isPending}
            onClick={() => addExpense.mutate()}
          >
            Save Expense
          </button>
        </div>
      )}

      {showTimeForm && (
        <div className="glass-card p-4 grid gap-3 md:grid-cols-[1fr_1fr_1fr]">
          <select
            className="rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2 text-sm"
            value={timeProjectId}
            onChange={(event) => setTimeProjectId(event.target.value)}
          >
            {projects.map((project) => (
              <option key={project.project_id} value={project.project_id}>
                {project.name}
              </option>
            ))}
          </select>
          <input
            className="rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2 text-sm"
            placeholder="Actor"
            value={timeActor}
            onChange={(event) => setTimeActor(event.target.value)}
          />
          <input
            className="rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2 text-sm"
            placeholder="Role"
            value={timeRole}
            onChange={(event) => setTimeRole(event.target.value)}
          />
          <input
            className="rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2 text-sm"
            placeholder="Duration (minutes)"
            value={timeDuration}
            onChange={(event) => setTimeDuration(event.target.value)}
          />
          <input
            className="rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-2 text-sm"
            placeholder="Hourly rate"
            value={timeRate}
            onChange={(event) => setTimeRate(event.target.value)}
          />
          <button
            type="button"
            className="btn btn-secondary md:col-span-3"
            disabled={!timeProjectId || !timeDuration || !timeRate || addTimeEntry.isPending}
            onClick={() => addTimeEntry.mutate()}
          >
            Save Time Entry
          </button>
        </div>
      )}

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
                <span>{expense.vendor || expense.category || 'Expense'}</span>
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
                <span>{entry.role || entry.actor_id || 'Time entry'}</span>
                <span>{formatCurrency(entry.labor_cost ?? 0)}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
