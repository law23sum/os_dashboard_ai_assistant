import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import {
  Dna,
  Play,
  Pause,
  BarChart2,
  Settings2,
  RefreshCw,
  Zap,
  Layers,
  Cpu,
  GitBranch,
  TrendingUp,
  Activity,
  Target,
  Clock,
  FlaskConical,
} from 'lucide-react'
import { toast } from '../utils/toast'

interface Architecture {
  id: string
  layers: number
  fitness: number
  params: string
  timestamp: string
}

interface ExperimentMetrics {
  generation: number
  totalGenerations: number
  populationSize: number
  bestFitness: number
  avgFitness: number
  mutationRate: number
  eliteCount: number
}

const strategies = [
  { id: 'genetic', name: 'Genetic Algorithm', icon: Dna, desc: 'Evolutionary optimization using crossover and mutation' },
  { id: 'random', name: 'Random Search', icon: GitBranch, desc: 'Stochastic exploration of architecture space' },
  { id: 'reinforcement', name: 'Reinforcement Learning', icon: Zap, desc: 'Policy-guided architecture generation' },
  { id: 'bayesian', name: 'Bayesian Optimization', icon: TrendingUp, desc: 'Probabilistic model-based optimization' },
]

export default function NAS() {
  const [isRunning, setIsRunning] = useState(false)
  const [selectedStrategy, setSelectedStrategy] = useState('genetic')
  const [configOpen, setConfigOpen] = useState(false)
  const [config, setConfig] = useState({
    populationSize: 50,
    generations: 100,
    mutationRate: 0.1,
    crossoverRate: 0.7,
  })
  const [metrics, setMetrics] = useState<ExperimentMetrics>({
    generation: 0,
    totalGenerations: 100,
    populationSize: 50,
    bestFitness: 0,
    avgFitness: 0,
    mutationRate: 0.1,
    eliteCount: 5,
  })
  const [architectures, setArchitectures] = useState<Architecture[]>([
    { id: 'arch-001', layers: 12, fitness: 0.9234, params: '24.5M', timestamp: '2m ago' },
    { id: 'arch-002', layers: 8, fitness: 0.9189, params: '18.2M', timestamp: '5m ago' },
    { id: 'arch-003', layers: 15, fitness: 0.9156, params: '32.1M', timestamp: '8m ago' },
  ])
  const [bestArchitecture, setBestArchitecture] = useState<string | null>(null)

  // Simulate evolution progress
  useEffect(() => {
    if (!isRunning) return
    
    const interval = setInterval(() => {
      setMetrics(prev => {
        const newGen = prev.generation + 1
        if (newGen >= prev.totalGenerations) {
          setIsRunning(false)
          toast.success('NAS experiment completed!')
          return { ...prev, generation: prev.totalGenerations }
        }
        return {
          ...prev,
          generation: newGen,
          bestFitness: Math.min(0.99, prev.bestFitness + Math.random() * 0.01),
          avgFitness: Math.min(0.95, prev.avgFitness + Math.random() * 0.008),
        }
      })
    }, 500)

    return () => clearInterval(interval)
  }, [isRunning])

  const startExperiment = () => {
    setIsRunning(true)
    setMetrics(prev => ({ ...prev, generation: 0, bestFitness: 0.7, avgFitness: 0.5 }))
    toast.info('Starting Neural Architecture Search experiment...')
  }

  const stopExperiment = () => {
    setIsRunning(false)
    toast.info('Experiment paused')
  }

  const progress = (metrics.generation / metrics.totalGenerations) * 100

  return (
    <div className="px-4 py-6 sm:px-0 space-y-6">
      {/* Header */}
      <div className="glass-panel p-6">
        <div className="flex items-center gap-4 mb-4">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-emerald-500 to-cyan-500 flex items-center justify-center shadow-lg shadow-emerald-500/30">
            <Dna className="w-6 h-6 text-white" />
          </div>
          <div>
            <p className="eyebrow-text">Evolutionary AI</p>
            <h1 className="text-2xl font-bold glass-gradient-text">Neural Architecture Search</h1>
          </div>
        </div>
        <p className="text-[color:var(--osd-muted)] max-w-2xl">
          Automated neural network design using evolutionary algorithms. Discover optimal architectures
          for your datasets and tasks through genetic optimization, random search, reinforcement learning,
          or Bayesian optimization strategies.
        </p>
        <div className="mt-4 flex flex-col gap-2 lg:flex-row lg:items-center lg:justify-between">
          <p className="text-xs uppercase tracking-[0.25em] text-[color:var(--osd-muted)]">
            FastAPI · <code className="rounded bg-black/30 px-2 py-0.5 text-[0.65rem]">/neural-architecture/nas/*</code>
          </p>
          <Link
            to="/ai/nas/experiments"
            className="inline-flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-emerald-500 to-cyan-500 px-4 py-2 text-sm font-semibold text-white shadow-lg shadow-emerald-500/30 hover:opacity-95"
          >
            <FlaskConical className="h-4 w-4" />
            Open Experiment Console
          </Link>
        </div>
      </div>

      {/* Control Panel */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          {isRunning ? (
            <button onClick={stopExperiment} className="cv-btn bg-red-500/20 border-red-500/30 text-red-400 hover:bg-red-500/30">
              <Pause className="w-4 h-4" />
              Stop Experiment
            </button>
          ) : (
            <button onClick={startExperiment} className="cv-btn cv-btn-primary">
              <Play className="w-4 h-4" />
              Start NAS Experiment
            </button>
          )}
          <button className="cv-btn cv-btn-ghost">
            <BarChart2 className="w-4 h-4" />
            View Results
          </button>
        </div>
        <div className="flex items-center gap-3">
          <button onClick={() => setConfigOpen(!configOpen)} className="cv-btn cv-btn-ghost">
            <Settings2 className="w-4 h-4" />
            Configure
          </button>
          <button className="cv-btn cv-btn-ghost">
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
        </div>
      </div>

      {/* Configuration Panel */}
      {configOpen && (
        <div className="glass-panel p-6 animate-in slide-in-from-top-2 duration-200">
          <h3 className="font-semibold text-lg mb-4 flex items-center gap-2">
            <Settings2 className="w-5 h-5" />
            Experiment Configuration
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
            <div>
              <label className="block text-sm text-[color:var(--osd-muted)] mb-2">Population Size</label>
              <input
                type="number"
                value={config.populationSize}
                onChange={(e) => setConfig({ ...config, populationSize: Number(e.target.value) })}
                className="w-full px-4 py-2.5 rounded-xl bg-[color:var(--osd-surfaceAlt)] border border-[color:var(--osd-border)] focus:border-[color:var(--osd-accent)] focus:outline-none transition-colors"
              />
            </div>
            <div>
              <label className="block text-sm text-[color:var(--osd-muted)] mb-2">Generations</label>
              <input
                type="number"
                value={config.generations}
                onChange={(e) => setConfig({ ...config, generations: Number(e.target.value) })}
                className="w-full px-4 py-2.5 rounded-xl bg-[color:var(--osd-surfaceAlt)] border border-[color:var(--osd-border)] focus:border-[color:var(--osd-accent)] focus:outline-none transition-colors"
              />
            </div>
            <div>
              <label className="block text-sm text-[color:var(--osd-muted)] mb-2">Mutation Rate</label>
              <input
                type="number"
                step="0.01"
                min="0"
                max="1"
                value={config.mutationRate}
                onChange={(e) => setConfig({ ...config, mutationRate: Number(e.target.value) })}
                className="w-full px-4 py-2.5 rounded-xl bg-[color:var(--osd-surfaceAlt)] border border-[color:var(--osd-border)] focus:border-[color:var(--osd-accent)] focus:outline-none transition-colors"
              />
            </div>
            <div>
              <label className="block text-sm text-[color:var(--osd-muted)] mb-2">Crossover Rate</label>
              <input
                type="number"
                step="0.01"
                min="0"
                max="1"
                value={config.crossoverRate}
                onChange={(e) => setConfig({ ...config, crossoverRate: Number(e.target.value) })}
                className="w-full px-4 py-2.5 rounded-xl bg-[color:var(--osd-surfaceAlt)] border border-[color:var(--osd-border)] focus:border-[color:var(--osd-accent)] focus:outline-none transition-colors"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm text-[color:var(--osd-muted)] mb-3">Search Strategy</label>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {strategies.map((strategy) => {
                const Icon = strategy.icon
                const isSelected = selectedStrategy === strategy.id
                return (
                  <button
                    key={strategy.id}
                    onClick={() => setSelectedStrategy(strategy.id)}
                    className={`p-4 rounded-xl border transition-all text-left ${
                      isSelected
                        ? 'border-[color:var(--osd-accent)] bg-[color:var(--osd-accent)]/10'
                        : 'border-[color:var(--osd-border)] hover:border-[color:var(--osd-accent)]/50'
                    }`}
                  >
                    <Icon className={`w-5 h-5 mb-2 ${isSelected ? 'text-[color:var(--osd-accent)]' : 'text-[color:var(--osd-muted)]'}`} />
                    <p className="font-medium text-sm">{strategy.name}</p>
                    <p className="text-xs text-[color:var(--osd-muted)] mt-1">{strategy.desc}</p>
                  </button>
                )
              })}
            </div>
          </div>
        </div>
      )}

      {/* Progress & Status */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Evolution Progress */}
        <div className="lg:col-span-2 glass-panel p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-lg flex items-center gap-2">
              <Activity className="w-5 h-5 text-emerald-400" />
              Evolution Progress
            </h3>
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${isRunning ? 'bg-emerald-500 animate-pulse' : 'bg-gray-500'}`} />
              <span className="text-sm text-[color:var(--osd-muted)]">{isRunning ? 'Running' : 'Idle'}</span>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="mb-6">
            <div className="flex justify-between mb-2">
              <span className="text-sm text-[color:var(--osd-muted)]">Generation {metrics.generation} / {metrics.totalGenerations}</span>
              <span className="text-sm font-medium">{progress.toFixed(1)}%</span>
            </div>
            <div className="h-3 rounded-full bg-[color:var(--osd-surfaceAlt)] overflow-hidden">
              <div
                className="h-full rounded-full bg-gradient-to-r from-emerald-500 to-cyan-500 transition-all duration-500"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>

          {/* Metrics Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { label: 'Best Fitness', value: metrics.bestFitness.toFixed(4), icon: Target, color: 'text-emerald-400' },
              { label: 'Avg Fitness', value: metrics.avgFitness.toFixed(4), icon: TrendingUp, color: 'text-blue-400' },
              { label: 'Population', value: metrics.populationSize, icon: Layers, color: 'text-violet-400' },
              { label: 'Elite Count', value: metrics.eliteCount, icon: Zap, color: 'text-yellow-400' },
            ].map((metric) => {
              const Icon = metric.icon
              return (
                <div key={metric.label} className="p-4 rounded-xl bg-[color:var(--osd-surfaceAlt)] border border-[color:var(--osd-border)]">
                  <div className="flex items-center gap-2 mb-2">
                    <Icon className={`w-4 h-4 ${metric.color}`} />
                    <span className="text-xs text-[color:var(--osd-muted)]">{metric.label}</span>
                  </div>
                  <p className={`text-xl font-bold ${metric.color}`}>{metric.value}</p>
                </div>
              )
            })}
          </div>
        </div>

        {/* Best Architecture */}
        <div className="glass-panel p-6">
          <h3 className="font-semibold text-lg mb-4 flex items-center gap-2">
            <Cpu className="w-5 h-5 text-violet-400" />
            Best Architecture
          </h3>
          {metrics.bestFitness > 0 ? (
            <div className="p-4 rounded-xl bg-[color:var(--osd-surfaceAlt)] border border-emerald-500/30 mb-4">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs text-[color:var(--osd-muted)]">Current Best</span>
                <span className="pill bg-emerald-500/20 text-emerald-400">
                  {metrics.bestFitness.toFixed(4)}
                </span>
              </div>
              <div className="font-mono text-sm text-[color:var(--osd-muted)] space-y-1">
                <p>• Conv2D(64) → BatchNorm → ReLU</p>
                <p>• Conv2D(128) → BatchNorm → ReLU</p>
                <p>• MaxPool2D(2×2)</p>
                <p>• Conv2D(256) → BatchNorm → ReLU</p>
                <p>• GlobalAvgPool → Dense(10)</p>
              </div>
            </div>
          ) : (
            <div className="p-8 rounded-xl bg-[color:var(--osd-surfaceAlt)] border border-dashed border-[color:var(--osd-border)] text-center">
              <Layers className="w-12 h-12 mx-auto mb-3 text-[color:var(--osd-muted)] opacity-50" />
              <p className="text-[color:var(--osd-muted)]">No architecture discovered yet</p>
              <p className="text-sm text-[color:var(--osd-muted)] opacity-75 mt-1">
                Start an experiment to begin evolution
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Recent Architectures */}
      <div className="glass-panel p-6">
        <h3 className="font-semibold text-lg mb-4 flex items-center gap-2">
          <GitBranch className="w-5 h-5 text-cyan-400" />
          Discovered Architectures
        </h3>
        <div className="space-y-3">
          {architectures.map((arch, index) => (
            <div
              key={arch.id}
              className="flex items-center justify-between p-4 rounded-xl bg-[color:var(--osd-surfaceAlt)] border border-[color:var(--osd-border)] hover:border-[color:var(--osd-accent)]/50 transition-colors cursor-pointer"
            >
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-xl bg-[color:var(--osd-accent)]/20 flex items-center justify-center">
                  <span className="text-sm font-bold text-[color:var(--osd-accent)]">#{index + 1}</span>
                </div>
                <div>
                  <p className="font-mono text-sm">{arch.id}</p>
                  <p className="text-xs text-[color:var(--osd-muted)]">{arch.layers} layers • {arch.params} parameters</p>
                </div>
              </div>
              <div className="flex items-center gap-6">
                <div className="text-right">
                  <p className="font-bold text-emerald-400">{arch.fitness.toFixed(4)}</p>
                  <p className="text-xs text-[color:var(--osd-muted)]">fitness</p>
                </div>
                <div className="flex items-center gap-1 text-[color:var(--osd-muted)]">
                  <Clock className="w-3 h-3" />
                  <span className="text-xs">{arch.timestamp}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Capabilities Info */}
      <div className="glass-panel p-6">
        <h3 className="font-semibold text-lg mb-4">How It Works</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { icon: Dna, title: 'Genetic Crossover', desc: 'Combine successful architectures to create new variants' },
            { icon: Zap, title: 'Mutation', desc: 'Introduce random beneficial variations to explore new designs' },
            { icon: Target, title: 'Fitness Evaluation', desc: 'Test performance on your data to score architectures' },
            { icon: Layers, title: 'Elite Preservation', desc: 'Preserve top performers across generations' },
          ].map(({ icon: Icon, title, desc }) => (
            <div key={title} className="p-4 rounded-xl bg-[color:var(--osd-surfaceAlt)] border border-[color:var(--osd-border)]">
              <Icon className="w-6 h-6 text-[color:var(--osd-accent)] mb-3" />
              <p className="font-medium mb-1">{title}</p>
              <p className="text-sm text-[color:var(--osd-muted)]">{desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
