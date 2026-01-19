import React, { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { BarChart3, Brain, Play, Settings, StopCircle, RefreshCw } from 'lucide-react'
import apiClient, { apiPath } from '../lib/apiClient'
import { toast } from '../utils/toast'
import { NeuralArchitectureStatus } from '../types'

const defaultStrategies = [
  'Genetic Algorithm',
  'Random Search',
  'Reinforcement Learning',
  'Bayesian Optimization',
]

export default function NeuralArchitectureSearch() {
  const [results, setResults] = useState<string>('')
  const [searchSpace, setSearchSpace] = useState('universal')
  const [strategy, setStrategy] = useState('genetic_algorithm')
  const [maxGenerations, setMaxGenerations] = useState(80)

  const fetchStatus = async (): Promise<NeuralArchitectureStatus> => {
    const response = await apiClient.get<NeuralArchitectureStatus>(apiPath('neural-architecture/nas/status'))
    return response.data
  }

  const statusQuery = useQuery({
    queryKey: ['nas-status'],
    queryFn: fetchStatus,
    refetchInterval: 6000,
  })

  const startExperiment = useMutation({
    mutationFn: () =>
      apiClient.post(apiPath('neural-architecture/nas/experiment/start'), {
        name: `NAS ${new Date().toISOString()}`,
        search_space: searchSpace,
        strategy,
        max_generations: maxGenerations,
      }),
    onSuccess: (payload) => {
      toast.success('NAS experiment launched')
      statusQuery.refetch()
      setResults(JSON.stringify(payload.data || payload, null, 2))
    },
    onError: () => toast.error('Failed to start NAS experiment'),
  })

  const stopExperiment = useMutation({
    mutationFn: () => apiClient.post(apiPath('neural-architecture/nas/experiment/stop'), {}),
    onSuccess: () => {
      toast.info('NAS experiment stopped')
      statusQuery.refetch()
    },
    onError: () => toast.error('Could not stop experiment'),
  })

  const viewResults = useMutation({
    mutationFn: () => apiClient.post(apiPath('neural-architecture/nas/results/view')),
    onSuccess: (payload) => {
      toast.success('Results refreshed')
      setResults(JSON.stringify(payload.data || payload, null, 2))
    },
    onError: () => toast.error('Unable to fetch experiment results'),
  })

  const configureMutation = useMutation({
    mutationFn: () =>
      apiClient.post(apiPath('neural-architecture/nas/configure'), {
        strategy,
        population_size: 60,
        max_generations: maxGenerations,
      }),
    onSuccess: () => {
      toast.success('NAS configuration saved')
      statusQuery.refetch()
    },
    onError: () => toast.error('Failed to configure NAS'),
  })

  const status = statusQuery.data
  const experiment = status?.current_experiment
  const metrics = status?.evolution_metrics

  return (
    <div className="px-4 py-6 sm:px-0 space-y-6">
      <header className="glass-panel p-6 border border-[color:var(--osd-border)]">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.5em] text-[color:var(--osd-muted)]">Advanced Systems</p>
            <h1 className="text-3xl font-semibold flex items-center gap-3 text-[color:var(--osd-text)]">
              <Brain className="w-8 h-8 text-[color:var(--osd-accent)]" />
              Neural Architecture Search
            </h1>
            <p className="mt-2 text-sm text-[color:var(--osd-muted)] max-w-3xl">
              Evolutionary AI that iterates on topology, layer widths, and activations to discover optimal networks
              for your latency and accuracy targets.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => startExperiment.mutate()}
              disabled={startExperiment.isPending}
              className="btn-tonal bg-[color:var(--osd-accent)] text-white hover:bg-[color:var(--osd-accentHover)]"
            >
              <Play className="w-4 h-4" />
              Start Experiment
            </button>
            <button
              onClick={() => stopExperiment.mutate()}
              disabled={!experiment || stopExperiment.isPending}
              className="btn-tonal border border-[color:var(--osd-border)] text-[color:var(--osd-text)]"
            >
              <StopCircle className="w-4 h-4" />
              Stop
            </button>
            <button
              onClick={() => viewResults.mutate()}
              className="btn-tonal border border-[color:var(--osd-border)] text-[color:var(--osd-text)]"
            >
              <BarChart3 className="w-4 h-4" />
              View Results
            </button>
            <button
              onClick={() => configureMutation.mutate()}
              className="btn-tonal border border-[color:var(--osd-border)] text-[color:var(--osd-text)]"
            >
              <Settings className="w-4 h-4" />
              Configure
            </button>
            <button onClick={() => statusQuery.refetch()} className="btn-tonal border border-[color:var(--osd-border)] text-[color:var(--osd-text)]">
              <RefreshCw className="w-4 h-4" />
              Refresh
            </button>
          </div>
        </div>
      </header>

      <section className="grid gap-6 md:grid-cols-3">
        <Card title="Experiments">
          <p className="text-4xl font-bold text-[color:var(--osd-text)]">{status?.total_experiments ?? 0}</p>
          <p className="text-xs text-[color:var(--osd-muted)] mt-1">Total experiments</p>
          <div className="mt-4 flex items-center gap-2">
            <span className="rounded-full bg-[color:var(--osd-pill)] px-3 py-1 text-xs uppercase tracking-[0.3em] text-[color:var(--osd-text)]">
              Active {status?.active_experiments ?? 0}
            </span>
          </div>
        </Card>
        <Card title="Strategy">
          <p className="text-lg text-[color:var(--osd-muted)]">Active strategy</p>
          <p className="text-xl font-semibold text-[color:var(--osd-text)]">{experiment ? experiment.name : 'Idle'}</p>
          <div className="mt-3 flex flex-wrap gap-2">
            {status?.available_strategies?.map((entry) => (
              <span key={entry} className="glass-pill border border-[color:var(--osd-border)] text-[color:var(--osd-text)]">
                {entry}
              </span>
            ))}
          </div>
        </Card>
        <Card title="Evolution">
          <p className="text-sm text-[color:var(--osd-muted)]">Current generation</p>
          <p className="text-2xl font-semibold text-[color:var(--osd-text)]">
            {metrics?.generation ?? experiment?.generation ?? 0}
          </p>
          <p className="mt-3 text-xs text-[color:var(--osd-muted)]">
            Population {metrics?.population_size ?? experiment?.population_size ?? 0}
          </p>
        </Card>
      </section>

      <section className="glass-panel p-6 border border-[color:var(--osd-border)] space-y-4">
        <h2 className="text-xl font-semibold text-[color:var(--osd-text)]">Current Experiment</h2>
        {experiment ? (
          <div className="grid gap-6 md:grid-cols-2">
            <div className="space-y-2">
              <p className="text-xs text-[color:var(--osd-muted)]">Name</p>
              <p className="text-lg font-semibold text-[color:var(--osd-text)]">{experiment.name}</p>
            </div>
            <div className="space-y-2">
              <p className="text-xs text-[color:var(--osd-muted)]">Status</p>
              <p className="text-lg text-[color:var(--osd-text)] capitalize">{experiment.status}</p>
            </div>
            <div className="space-y-2">
              <p className="text-xs text-[color:var(--osd-muted)]">Fitness</p>
              <p className="text-lg font-semibold text-[color:var(--osd-text)]">
                {experiment.best_fitness.toFixed(3)}
              </p>
            </div>
            <div className="space-y-2">
              <p className="text-xs text-[color:var(--osd-muted)]">Generation</p>
              <p className="text-lg text-[color:var(--osd-text)]">{experiment.generation}</p>
            </div>
          </div>
        ) : (
          <p className="text-sm text-[color:var(--osd-muted)]">No experiment is currently running.</p>
        )}
      </section>

      {status?.best_architecture && (
        <section className="glass-panel p-6 border border-[color:var(--osd-border)] space-y-3">
          <h2 className="text-lg font-semibold text-[color:var(--osd-text)]">Best Architecture</h2>
          <pre className="rounded-xl bg-[color:var(--osd-surfaceAlt)] border border-[color:var(--osd-border)] p-4 text-sm text-[color:var(--osd-muted)] font-mono max-h-64 overflow-auto">
            {JSON.stringify(status.best_architecture, null, 2)}
          </pre>
        </section>
      )}

      {results && (
        <section className="glass-panel p-6 border border-[color:var(--osd-border)]">
          <h3 className="text-lg font-semibold text-[color:var(--osd-text)]">Recent Activity</h3>
          <pre className="mt-3 rounded-xl bg-[color:var(--osd-surfaceAlt)] border border-[color:var(--osd-border)] p-3 text-xs text-[color:var(--osd-muted)] font-mono overflow-auto max-h-56">
            {results}
          </pre>
        </section>
      )}

      <section className="glass-panel p-6 border border-[color:var(--osd-border)] space-y-4">
        <h2 className="text-lg font-semibold text-[color:var(--osd-text)]">Plan Configuration</h2>
        <div className="grid gap-4 md:grid-cols-3">
          <label className="space-y-1 text-sm text-[color:var(--osd-muted)]">
            Search Space
            <select
              value={searchSpace}
              onChange={(e) => setSearchSpace(e.target.value)}
              className="w-full rounded-xl bg-[color:var(--osd-surfaceAlt)] border border-[color:var(--osd-border)] px-3 py-2 text-[color:var(--osd-text)] focus:border-[color:var(--osd-accent)] focus:outline-none"
            >
              <option value="universal">Universal</option>
              <option value="vision">Vision</option>
              <option value="nlp">Transformer</option>
              <option value="edge">Edge-optimized</option>
            </select>
          </label>
          <label className="space-y-1 text-sm text-[color:var(--osd-muted)]">
            Strategy
            <select
              value={strategy}
              onChange={(e) => setStrategy(e.target.value)}
              className="w-full rounded-xl bg-[color:var(--osd-surfaceAlt)] border border-[color:var(--osd-border)] px-3 py-2 text-[color:var(--osd-text)] focus:border-[color:var(--osd-accent)] focus:outline-none"
            >
              {defaultStrategies.map((item) => (
                <option key={item} value={item.toLowerCase().replace(/\s/g, '_')}>
                  {item}
                </option>
              ))}
            </select>
          </label>
          <label className="space-y-1 text-sm text-[color:var(--osd-muted)]">
            Max Generations ({maxGenerations})
            <input
              type="range"
              min={20}
              max={200}
              value={maxGenerations}
              onChange={(e) => setMaxGenerations(Number(e.target.value))}
              className="w-full"
            />
          </label>
        </div>
      </section>
    </div>
  )
}

function Card({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="glass-card border border-[color:var(--osd-border)] p-5 space-y-2 bg-[color:var(--osd-surfaceAlt)]">
      <p className="text-xs uppercase tracking-[0.4em] text-[color:var(--osd-muted)]">{title}</p>
      {children}
    </div>
  )
}

