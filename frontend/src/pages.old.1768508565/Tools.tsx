import { useEffect, useMemo, useRef, useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import {
  Terminal as TerminalIcon,
  Play,
  Loader2,
  RefreshCcw,
  History,
  Copy,
  Trash2,
  Folder,
  RotateCcw,
  ArrowUp,
} from 'lucide-react'
import apiClient, { apiPath } from '../lib/apiClient'
import { toast } from '../utils/toast'
import {
  TerminalResult,
  TerminalHistoryEntry,
  TerminalCommandCatalog,
  TerminalCommandEntry,
} from '../types'

interface TerminalPayload {
  command: string
  cwd?: string
}

const STORAGE_KEY = 'osdash-terminal-history'

const workspaces = ['.', 'assistant_hub_gui', 'assistant_hub', 'backend_api', 'frontend', 'ui']

const workspaceShortcuts: TerminalCommandEntry[] = [
  {
    label: 'List files',
    command: 'ls -la',
    description: 'Inspect the active working directory.',
  },
  {
    label: 'Git status',
    command: 'git status -sb',
    description: 'Check repository status with short branch info.',
  },
  {
    label: 'Run pytest',
    command: 'pytest -q',
    description: 'Execute the Python unit tests quietly.',
  },
  {
    label: 'Install Python deps',
    command: 'pip install -r requirements.txt',
    description: 'Install backend dependencies.',
  },
  {
    label: 'Install frontend deps',
    command: 'cd frontend && npm install',
    description: 'Install React/Electron dependencies.',
  },
  {
    label: 'Build web bundle',
    command: 'cd frontend && npm run build:web',
    description: 'Produce the Vite static build in frontend/dist.',
  },
]

const generateId = () =>
  typeof crypto !== 'undefined' && crypto.randomUUID ? crypto.randomUUID() : String(Date.now())

const loadHistoryFromStorage = (): TerminalHistoryEntry[] => {
  if (typeof window === 'undefined') return []
  try {
    const cached = window.localStorage.getItem(STORAGE_KEY)
    if (!cached) return []
    const parsed = JSON.parse(cached)
    if (!Array.isArray(parsed)) return []
    return parsed.map((entry: Partial<TerminalHistoryEntry>) => ({
      id: entry.id ?? generateId(),
      command: entry.command ?? '',
      stdout: entry.stdout ?? '',
      stderr: entry.stderr ?? '',
      exit_code: typeof entry.exit_code === 'number' ? entry.exit_code : -1,
      shell: entry.shell ?? 'shell',
      cwd: entry.cwd ?? '.',
      ok: typeof entry.ok === 'boolean' ? entry.ok : (entry.exit_code ?? -1) === 0,
      timestamp: entry.timestamp ?? new Date().toISOString(),
    }))
  } catch {
    return []
  }
}

const runTerminalCommand = async ({ command, cwd }: TerminalPayload): Promise<TerminalResult> => {
  const { data } = await apiClient.post<TerminalResult>(apiPath('terminal'), {
    command,
    cwd,
  })
  return data
}

const fetchCommandCatalog = async (): Promise<TerminalCommandCatalog> => {
  const { data } = await apiClient.get<TerminalCommandCatalog>(apiPath('terminal/commands'))
  return data
}

export default function Tools() {
  const [command, setCommand] = useState('python main.py')
  const [cwd, setCwd] = useState('.')
  const [history, setHistory] = useState<TerminalHistoryEntry[]>(() => loadHistoryFromStorage())
  const [autoScroll, setAutoScroll] = useState(true)
  const outputRef = useRef<HTMLDivElement>(null)
  const cwdRef = useRef<HTMLInputElement>(null)
  const commandRef = useRef<HTMLTextAreaElement>(null)

  const commandCatalogQuery = useQuery({
    queryKey: ['terminal', 'catalog'],
    queryFn: fetchCommandCatalog,
    staleTime: 1000 * 60 * 5,
    refetchOnWindowFocus: false,
  })

  const mutation = useMutation({
    mutationFn: runTerminalCommand,
    onSuccess: (result) => {
      const entry: TerminalHistoryEntry = {
        id: generateId(),
        ...result,
        cwd: result.cwd || cwd || '.',
        shell: result.shell || 'shell',
        ok: typeof result.ok === 'boolean' ? result.ok : result.exit_code === 0,
        timestamp: new Date().toISOString(),
      }
      setHistory((current) => [entry, ...current].slice(0, 20))
      if (entry.ok) {
        toast.success(`Command finished (exit ${entry.exit_code})`)
      } else {
        toast.error(`Command exited with code ${entry.exit_code}`)
      }
    },
    onError: (error) => {
      toast.error(
        `Command failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
      )
    },
  })

  useEffect(() => {
    if (typeof window !== 'undefined') {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(history))
    }
  }, [history])

  useEffect(() => {
    if (autoScroll && outputRef.current) {
      outputRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [history, autoScroll])

  const latest = history[0]
  const hasError = latest ? !latest.ok : false

  const combinedOutput = useMemo(() => {
    if (!latest) return ''
    const segments: string[] = []
    if (latest.stdout?.trim()) {
      segments.push(`STDOUT:\n${latest.stdout.trim()}`)
    }
    if (latest.stderr?.trim()) {
      segments.push(`STDERR:\n${latest.stderr.trim()}`)
    }
    return segments.join('\n\n')
  }, [latest])

  const handleRun = (payload?: Partial<TerminalPayload>) => {
    const trimmed = (payload?.command ?? command).trim()
    if (!trimmed) {
      toast.error('Enter a command to run')
      return
    }
    const rawCwd = payload?.cwd ?? cwd ?? '.'
    const sanitizedCwd =
      typeof rawCwd === 'string' && rawCwd.trim().length > 0 ? rawCwd.trim() : '.'
    const targetCwd = sanitizedCwd
    setCwd(targetCwd)
    if (payload?.command) {
      setCommand(trimmed)
    }
    mutation.mutate({
      command: trimmed,
      cwd: targetCwd,
    })
  }

  const handleClearHistory = () => {
    setHistory([])
    toast.success('Cleared terminal history')
  }

  const handleCopy = (text: string) => {
    if (!text) {
      toast.error('Nothing to copy yet')
      return
    }
    navigator.clipboard
      .writeText(text)
      .then(() => toast.success('Copied output to clipboard'))
      .catch(() => toast.error('Unable to copy to clipboard'))
  }

  const handleUseEntry = (entry: TerminalHistoryEntry) => {
    setCommand(entry.command)
    setCwd(entry.cwd)
    commandRef.current?.focus()
  }

  const handleRunCatalogCommand = (entry: TerminalCommandEntry) => {
    setCommand(entry.command)
    handleRun({ command: entry.command })
  }

  const handleInsertTemplate = (entry: TerminalCommandEntry) => {
    setCommand(entry.command)
    toast.success('Template inserted. Update placeholders before running.')
    commandRef.current?.focus()
  }

  const handleRunShortcut = (entry: TerminalCommandEntry) => {
    setCommand(entry.command)
    handleRun({ command: entry.command })
  }

  const catalogErrorMessage = commandCatalogQuery.isError
    ? 'Command catalog unavailable. Start the FastAPI backend to load shared entries.'
    : 'No commands published yet.'

  return (
    <div className="px-4 py-6 sm:px-0 space-y-6">
      <header className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <TerminalIcon className="w-6 h-6 text-primary-500" />
            Tools & Terminal
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            Shared command runner backed by the FastAPI terminal endpoint. Desktop and browser
            clients now use the exact same command catalog as the Tkinter Tools tab.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <label className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-300">
            <input
              type="checkbox"
              checked={autoScroll}
              onChange={(e) => setAutoScroll(e.target.checked)}
              className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            />
            Auto-scroll output
          </label>
          <button
            onClick={handleClearHistory}
            className="inline-flex items-center gap-2 px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-md text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700"
          >
            <Trash2 className="w-4 h-4" />
            Clear History
          </button>
        </div>
      </header>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <section className="glass-panel bg-white dark:bg-gray-800 shadow rounded-xl p-6 space-y-4 xl:col-span-2">
          <div className="space-y-3">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300 flex items-center gap-2">
              <TerminalIcon className="w-4 h-4 text-primary-500" />
              Command
            </label>
            <textarea
              ref={commandRef}
              value={command}
              onChange={(e) => setCommand(e.target.value)}
              rows={3}
              className="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-transparent px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500"
              placeholder="Enter a shell command (e.g., ls -la)"
            />
          </div>

          <div className="space-y-3">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300 flex items-center gap-2">
              <Folder className="w-4 h-4 text-primary-500" />
              Working Directory
            </label>
            <div className="flex flex-col gap-2 md:flex-row">
              <input
                ref={cwdRef}
                value={cwd}
                onChange={(e) => setCwd(e.target.value)}
                className="flex-1 rounded-lg border border-gray-300 dark:border-gray-600 bg-transparent px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500"
                placeholder="."
              />
              <div className="flex gap-2 flex-wrap">
                {workspaces.map((dir) => (
                  <button
                    key={dir}
                    type="button"
                    onClick={() => setCwd(dir)}
                    className={`px-3 py-1 text-xs rounded-full border ${
                      cwd === dir
                        ? 'border-primary-500 text-primary-600'
                        : 'border-gray-300 text-gray-600 dark:text-gray-300'
                    }`}
                  >
                    {dir}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="flex flex-wrap gap-3">
            <button
              onClick={() => handleRun()}
              disabled={mutation.isPending}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-md bg-primary-600 text-white text-sm font-medium hover:bg-primary-700 disabled:opacity-60"
            >
              {mutation.isPending ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Play className="w-4 h-4" />
              )}
              Run Command
            </button>
            <button
              onClick={() => latest && handleRun({ command: latest.command, cwd: latest.cwd })}
              disabled={mutation.isPending || !latest}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-md border border-gray-300 dark:border-gray-600 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50"
            >
              <RotateCcw className="w-4 h-4" />
              Re-run Last
            </button>
            <button
              onClick={() => handleRun({ command: 'pwd', cwd })}
              disabled={mutation.isPending}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-md border border-gray-300 dark:border-gray-600 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700"
            >
              <RefreshCcw className="w-4 h-4" />
              Verify Path
            </button>
          </div>

          <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
            <div className="flex items-center justify-between mb-3">
              <div>
                <p className="text-sm font-semibold text-gray-800 dark:text-gray-100">
                  Output
                </p>
                {latest ? (
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    Ran "{latest.command}" via {latest.shell} · {latest.cwd} ·{' '}
                    {new Date(latest.timestamp).toLocaleTimeString()}
                  </p>
                ) : (
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    No commands have been executed yet.
                  </p>
                )}
              </div>
              {latest && (
                <div className="flex items-center gap-2">
                  <span
                    className={`text-xs font-semibold px-2 py-1 rounded-full ${
                      hasError
                        ? 'bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-100'
                        : 'bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-100'
                    }`}
                  >
                    Exit {latest.exit_code}
                  </span>
                  <button
                    onClick={() => handleCopy(combinedOutput)}
                    className="inline-flex items-center gap-1 text-xs text-gray-600 dark:text-gray-300 hover:text-primary-600"
                  >
                    <Copy className="w-4 h-4" />
                    Copy
                  </button>
                </div>
              )}
            </div>
            {latest && (
              <dl className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs text-gray-600 dark:text-gray-400 mb-4">
                <div>
                  <dt className="uppercase tracking-wide text-[0.65rem] text-gray-500 dark:text-gray-500">
                    Shell
                  </dt>
                  <dd className="text-sm text-gray-900 dark:text-gray-100">{latest.shell}</dd>
                </div>
                <div>
                  <dt className="uppercase tracking-wide text-[0.65rem] text-gray-500 dark:text-gray-500">
                    Directory
                  </dt>
                  <dd className="text-sm text-gray-900 dark:text-gray-100">{latest.cwd}</dd>
                </div>
                <div>
                  <dt className="uppercase tracking-wide text-[0.65rem] text-gray-500 dark:text-gray-500">
                    Exit Code
                  </dt>
                  <dd className="text-sm text-gray-900 dark:text-gray-100">{latest.exit_code}</dd>
                </div>
              </dl>
            )}
            <div className="bg-gray-50 dark:bg-gray-900 rounded-md p-4 h-64 overflow-y-auto">
              {latest ? (
                <>
                  {latest.stdout && (
                    <div className="mb-4">
                      <p className="text-xs uppercase tracking-wide text-gray-500 dark:text-gray-400 mb-1">
                        Stdout
                      </p>
                      <pre className="text-sm text-gray-900 dark:text-gray-100 whitespace-pre-wrap">
                        {latest.stdout}
                      </pre>
                    </div>
                  )}
                  {latest.stderr && (
                    <div>
                      <p className="text-xs uppercase tracking-wide text-red-600 dark:text-red-400 mb-1">
                        Stderr
                      </p>
                      <pre className="text-sm text-red-600 dark:text-red-400 whitespace-pre-wrap">
                        {latest.stderr}
                      </pre>
                    </div>
                  )}
                  {!latest.stdout && !latest.stderr && (
                    <p className="text-sm text-gray-400">No output</p>
                  )}
                </>
              ) : (
                <div className="h-full flex items-center justify-center text-sm text-gray-500">
                  Outputs will appear here.
                </div>
              )}
              <div ref={outputRef} />
            </div>
          </div>

          <div>
            <div className="flex items-center gap-2 mb-3">
              <History className="w-5 h-5 text-primary-500" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                Recent Commands
              </h3>
            </div>
            {history.length === 0 ? (
              <p className="text-sm text-gray-500 dark:text-gray-400">
                No commands run yet.
              </p>
            ) : (
              <div className="space-y-3">
                {history.map((entry) => (
                  <div
                    key={entry.id}
                    className="border border-gray-200 dark:border-gray-700 rounded-md p-3"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                          {entry.command}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          {entry.shell} · {entry.cwd} ·{' '}
                          {new Date(entry.timestamp).toLocaleTimeString()}
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        <span
                          className={`text-xs px-2 py-0.5 rounded-full ${
                            entry.exit_code === 0
                              ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-200'
                              : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-200'
                          }`}
                        >
                          {entry.exit_code === 0 ? 'Success' : `Exit ${entry.exit_code}`}
                        </span>
                        <button
                          onClick={() => handleUseEntry(entry)}
                          className="inline-flex items-center gap-1 text-xs text-primary-600 hover:text-primary-700"
                        >
                          <ArrowUp className="w-4 h-4" />
                          Use
                        </button>
                      </div>
                    </div>
                    {(entry.stderr || entry.stdout) && (
                      <pre className="mt-2 text-xs text-gray-600 dark:text-gray-300 whitespace-pre-wrap">
                        {(entry.stdout || '') + (entry.stderr ? `\n${entry.stderr}` : '')}
                      </pre>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </section>

        <aside className="space-y-6">
          <CommandCard
            title="Spec Sheet Commands"
            subtitle="Mirrors the Tkinter quick actions."
            commands={commandCatalogQuery.data?.spec_sheet ?? []}
            isLoading={commandCatalogQuery.isPending}
            emptyMessage={catalogErrorMessage}
            onCommand={handleRunCatalogCommand}
          />

          <CommandCard
            title="Backend CLI Routines"
            subtitle="assistant_hub CLI entrypoints (projects, OneNote, Excel)."
            commands={commandCatalogQuery.data?.backend_cli ?? []}
            isLoading={commandCatalogQuery.isPending}
            emptyMessage={catalogErrorMessage}
            onCommand={handleRunCatalogCommand}
          />

          <CommandCard
            title="CLI Templates"
            subtitle="Prefill commands that need manual IDs or file paths."
            commands={commandCatalogQuery.data?.templates ?? []}
            isLoading={commandCatalogQuery.isPending}
            emptyMessage={catalogErrorMessage}
            action="insert"
            onCommand={handleInsertTemplate}
          />

          <CommandCard
            title="Workspace Shortcuts"
            subtitle="Local helpers for repo maintenance."
            commands={workspaceShortcuts}
            isLoading={false}
            onCommand={handleRunShortcut}
          />

          <div className="glass-panel bg-white dark:bg-gray-800 shadow rounded-xl p-5 space-y-3">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
              External Tools
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-300 mb-2">
              Access integrated utilities directly from the dashboard.
            </p>
            <a
              href="/tools/cyberchef/CyberChef_v10.19.4.html"
              target="_blank"
              rel="noopener noreferrer"
              className="w-full flex items-center justify-between gap-3 px-3 py-2 border border-gray-200 dark:border-gray-700 rounded-lg text-left hover:bg-gray-50 dark:hover:bg-gray-700 group"
            >
              <div>
                <p className="text-sm font-medium text-gray-900 dark:text-gray-100 group-hover:text-primary-600">
                  CyberChef
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">The Cyber Swiss Army Knife.</p>
              </div>
              <ArrowUp className="w-4 h-4 rotate-45 text-gray-400 group-hover:text-primary-600" />
            </a>
          </div>

          <div className="glass-panel bg-white dark:bg-gray-800 shadow rounded-xl p-5 space-y-3">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
              Execution Notes
            </h3>
            <ul className="text-sm text-gray-600 dark:text-gray-300 space-y-2">
              <li>Commands execute on the FastAPI host (desktop shell or remote server).</li>
              <li>History is stored locally only—clear it anytime.</li>
              <li>
                Catalog definitions live in <code className="font-mono">assistant_hub/command_catalog.py</code>.
              </li>
              <li className="font-medium">
                React desktop + browser experiences stay in lockstep with this shared catalog.
              </li>
            </ul>
          </div>

          <div className="bg-white dark:bg-gray-800 shadow rounded-xl p-5 space-y-3">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
              Deployment Targets
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-300">
              Build once, deploy everywhere. Use <code className="font-mono">npm run build:web</code>{' '}
              for static hosting and <code className="font-mono">npm run build:desktop:&lt;os&gt;</code>{' '}
              to package Electron apps for Linux, Windows, and macOS. The same React bundle and
              command catalog ship with both surfaces.
            </p>
          </div>
        </aside>
      </div>
    </div>
  )
}

interface CommandCardProps {
  title: string
  subtitle?: string
  commands: TerminalCommandEntry[]
  isLoading: boolean
  emptyMessage?: string
  action?: 'run' | 'insert'
  onCommand: (entry: TerminalCommandEntry) => void
}

function CommandCard({
  title,
  subtitle,
  commands,
  isLoading,
  emptyMessage,
  action = 'run',
  onCommand,
}: CommandCardProps) {
  const actionLabel = action === 'run' ? 'Run' : 'Insert'

  return (
    <div className="glass-panel bg-white dark:bg-gray-800 shadow rounded-xl p-5 space-y-3">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">{title}</h3>
        {subtitle && <p className="text-sm text-gray-600 dark:text-gray-400">{subtitle}</p>}
      </div>
      {isLoading ? (
        <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
          <Loader2 className="w-4 h-4 animate-spin" />
          Loading command catalog…
        </div>
      ) : commands.length === 0 ? (
        <p className="text-sm text-gray-500 dark:text-gray-400">{emptyMessage}</p>
      ) : (
        <div className="space-y-2 max-h-80 overflow-y-auto pr-1">
          {commands.map((cmd) => (
            <button
              key={`${cmd.label}-${cmd.command}`}
              type="button"
              onClick={() => onCommand(cmd)}
              className="w-full flex items-center justify-between gap-3 px-3 py-2 border border-gray-200 dark:border-gray-700 rounded-lg text-left hover:bg-gray-50 dark:hover:bg-gray-700"
            >
              <div>
                <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                  {cmd.label}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">{cmd.description}</p>
              </div>
              <span className="text-xs font-semibold text-primary-600">{actionLabel}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
