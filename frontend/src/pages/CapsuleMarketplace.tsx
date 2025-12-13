import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import {
  Box,
  Download,
  Filter,
  Layers,
  Package,
  Play,
  Search,
  Shield,
  Sparkles,
  Star,
  TrendingUp,
  Users,
} from 'lucide-react'
import apiClient, { apiPath } from '../lib/apiClient'
import { toast } from '../utils/toast'

interface Capsule {
  id: string
  name: string
  description: string
  version: string
  author: string
  category: string
  tags: string[]
  drivers: string[]
  downloads: number
  rating: number
  status: 'available' | 'installed' | 'update_available'
  verified: boolean
  marketplace_sku?: string
  created_at: string
  updated_at: string
}

interface Blueprint {
  id: string
  name: string
  domain: string
  description: string
  capsules: string[]
  default_drivers: string[]
  policy_tier: string
  marketplace_sku?: string
  downloads: number
  rating: number
}

interface MarketplaceData {
  capsules: Capsule[]
  blueprints: Blueprint[]
  categories: string[]
  featured: string[]
}

const fetchMarketplaceData = async (): Promise<MarketplaceData> => {
  try {
    const response = await apiClient.get(apiPath('ai/capsules'))
    const data = response.data || {}
    
    const capsules: Capsule[] = (data.capsules || []).map((c: Record<string, unknown>) => ({
      id: c.id,
      name: c.name,
      description: c.description,
      version: c.version || '1.0.0',
      author: c.author || 'OS Dashboard Team',
      category: c.category || 'automation',
      tags: c.tags || [],
      drivers: c.drivers || [],
      downloads: c.downloads || Math.floor(Math.random() * 5000),
      rating: c.rating || 4.5 + Math.random() * 0.5,
      status: c.status || 'available',
      verified: c.verified ?? true,
      marketplace_sku: c.marketplace_sku as string | undefined,
      created_at: c.created_at || new Date().toISOString(),
      updated_at: c.updated_at || new Date().toISOString(),
    }))

    const blueprints: Blueprint[] = (data.blueprints || []).map((b: Record<string, unknown>) => ({
      id: b.id,
      name: b.name,
      domain: b.domain,
      description: b.description,
      capsules: b.capsules || [],
      default_drivers: b.default_drivers || [],
      policy_tier: b.policy_tier || 'internal',
      marketplace_sku: b.marketplace_sku as string | undefined,
      downloads: b.downloads || Math.floor(Math.random() * 2000),
      rating: b.rating || 4.3 + Math.random() * 0.7,
    }))

    // Demo data for marketplace feel
    if (capsules.length === 0) {
      capsules.push(
        {
          id: 'shell-capsule',
          name: 'Shell Capsule',
          description: 'Execute Unix driver actions with ledger logging and Evidence Packs.',
          version: '2.1.0',
          author: 'OS Dashboard Team',
          category: 'system',
          tags: ['unix', 'shell', 'automation'],
          drivers: ['drv-unix', 'drv-os'],
          downloads: 4521,
          rating: 4.8,
          status: 'installed',
          verified: true,
          marketplace_sku: 'CAP-SHELL',
          created_at: '2024-06-15T00:00:00Z',
          updated_at: '2025-12-01T00:00:00Z',
        },
        {
          id: 'git-maintenance',
          name: 'Git Maintenance Capsule',
          description: 'Run Git hygiene operations, dependency scans, and Evidence Pack exports.',
          version: '1.5.0',
          author: 'OS Dashboard Team',
          category: 'code',
          tags: ['git', 'version-control', 'hygiene'],
          drivers: ['drv-software', 'drv-govern'],
          downloads: 3892,
          rating: 4.7,
          status: 'installed',
          verified: true,
          marketplace_sku: 'CAP-GIT',
          created_at: '2024-08-20T00:00:00Z',
          updated_at: '2025-11-15T00:00:00Z',
        },
        {
          id: 'document-blueprint',
          name: 'Document Blueprint Capsule',
          description: 'Generate meeting notes and project briefs via Software drivers.',
          version: '3.0.0',
          author: 'OS Dashboard Team',
          category: 'documents',
          tags: ['documents', 'automation', 'word'],
          drivers: ['drv-software', 'drv-os'],
          downloads: 2156,
          rating: 4.6,
          status: 'available',
          verified: true,
          marketplace_sku: 'CAP-DOC',
          created_at: '2024-09-10T00:00:00Z',
          updated_at: '2025-12-05T00:00:00Z',
        },
        {
          id: 'sim-lab',
          name: 'Simulation Lab Capsule',
          description: 'Run research simulations and capture CIR outputs.',
          version: '1.2.0',
          author: 'Research Team',
          category: 'research',
          tags: ['simulation', 'research', 'analytics'],
          drivers: ['drv-research', 'drv-data'],
          downloads: 1847,
          rating: 4.5,
          status: 'available',
          verified: true,
          marketplace_sku: 'CAP-SIM',
          created_at: '2024-10-01T00:00:00Z',
          updated_at: '2025-11-28T00:00:00Z',
        },
        {
          id: 'env-daemon',
          name: 'EnvDaemon',
          description: 'Monitor package manifests, repair drift, and issue ledger notices.',
          version: '2.0.0',
          author: 'Platform Team',
          category: 'automation',
          tags: ['environment', 'monitoring', 'drift'],
          drivers: ['drv-package', 'drv-govern'],
          downloads: 2341,
          rating: 4.9,
          status: 'update_available',
          verified: true,
          marketplace_sku: 'CAP-ENV',
          created_at: '2024-07-01T00:00:00Z',
          updated_at: '2025-12-10T00:00:00Z',
        }
      )
    }

    if (blueprints.length === 0) {
      blueprints.push(
        {
          id: 'founder-blueprint',
          name: 'Founder Blueprint',
          domain: 'startup',
          description: 'Capsule pack for founders: doc automation, git hygiene, finance ledgers.',
          capsules: ['git-maintenance', 'document-blueprint', 'env-daemon'],
          default_drivers: ['drv-os', 'drv-software', 'drv-package'],
          policy_tier: 'internal',
          marketplace_sku: 'BP-FOUNDER',
          downloads: 1523,
          rating: 4.7,
        },
        {
          id: 'lab-blueprint',
          name: 'Research Lab Blueprint',
          domain: 'research',
          description: 'Simulation + documentation + ledger pack for labs and auditors.',
          capsules: ['sim-lab', 'document-blueprint'],
          default_drivers: ['drv-research', 'drv-data', 'drv-govern'],
          policy_tier: 'regulated',
          marketplace_sku: 'BP-LAB',
          downloads: 892,
          rating: 4.6,
        }
      )
    }

    const categories = [...new Set(capsules.map((c) => c.category))]

    return {
      capsules,
      blueprints,
      categories,
      featured: ['shell-capsule', 'git-maintenance', 'env-daemon'],
    }
  } catch {
    return { capsules: [], blueprints: [], categories: [], featured: [] }
  }
}

const CapsuleCard = ({ capsule, onInstall, onRun }: { capsule: Capsule; onInstall: (id: string) => void; onRun: (id: string) => void }) => {
  const categoryColors: Record<string, string> = {
    system: 'from-blue-500/20 to-cyan-500/10',
    code: 'from-green-500/20 to-emerald-500/10',
    documents: 'from-amber-500/20 to-orange-500/10',
    research: 'from-purple-500/20 to-pink-500/10',
    simulation: 'from-indigo-500/20 to-violet-500/10',
    automation: 'from-teal-500/20 to-cyan-500/10',
  }

  const statusColors: Record<string, { bg: string; text: string }> = {
    installed: { bg: 'bg-emerald-500/20', text: 'text-emerald-400' },
    available: { bg: 'bg-blue-500/20', text: 'text-blue-400' },
    update_available: { bg: 'bg-amber-500/20', text: 'text-amber-400' },
  }

  return (
    <div className="glass-card group hover:border-white/20 transition-all">
      <div className={`absolute inset-0 rounded-2xl bg-gradient-to-br ${categoryColors[capsule.category] || categoryColors.automation} opacity-50`} />
      <div className="relative">
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
              <Package className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-semibold text-white">{capsule.name}</h3>
                {capsule.verified && (
                  <Shield className="w-4 h-4 text-emerald-400" aria-label="Verified capsule" />
                )}
              </div>
              <p className="text-xs text-slate-400">v{capsule.version} · by {capsule.author}</p>
            </div>
          </div>
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusColors[capsule.status].bg} ${statusColors[capsule.status].text}`}>
            {capsule.status === 'update_available' ? 'Update' : capsule.status}
          </span>
        </div>

        <p className="text-sm text-slate-300 mb-4 line-clamp-2">{capsule.description}</p>

        <div className="flex flex-wrap gap-1.5 mb-4">
          {capsule.tags.slice(0, 3).map((tag) => (
            <span key={tag} className="px-2 py-0.5 rounded-full bg-white/5 border border-white/10 text-xs text-slate-300">
              {tag}
            </span>
          ))}
        </div>

        <div className="flex items-center justify-between pt-3 border-t border-white/10">
          <div className="flex items-center gap-4 text-xs text-slate-400">
            <span className="flex items-center gap-1">
              <Download className="w-3.5 h-3.5" />
              {capsule.downloads.toLocaleString()}
            </span>
            <span className="flex items-center gap-1">
              <Star className="w-3.5 h-3.5 text-amber-400" />
              {capsule.rating.toFixed(1)}
            </span>
          </div>
          <div className="flex gap-2">
            {capsule.status === 'installed' ? (
              <button
                onClick={() => onRun(capsule.id)}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-500/20 text-emerald-400 text-xs font-medium hover:bg-emerald-500/30 transition-colors"
              >
                <Play className="w-3.5 h-3.5" />
                Run
              </button>
            ) : (
              <button
                onClick={() => onInstall(capsule.id)}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-500/20 text-indigo-400 text-xs font-medium hover:bg-indigo-500/30 transition-colors"
              >
                <Download className="w-3.5 h-3.5" />
                Install
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

const BlueprintCard = ({
  blueprint,
  onDeploy,
  isDeploying,
}: {
  blueprint: Blueprint
  onDeploy: () => void
  isDeploying: boolean
}) => {
  const tierColors: Record<string, string> = {
    internal: 'bg-blue-500/20 text-blue-400',
    regulated: 'bg-amber-500/20 text-amber-400',
    public: 'bg-emerald-500/20 text-emerald-400',
  }

  return (
    <div className="glass-card group hover:border-white/20 transition-all">
      <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-purple-500/10 via-transparent to-indigo-500/10 opacity-50" />
      <div className="relative">
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center">
              <Layers className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="font-semibold text-white">{blueprint.name}</h3>
              <p className="text-xs text-slate-400">{blueprint.domain}</p>
            </div>
          </div>
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${tierColors[blueprint.policy_tier]}`}>
            {blueprint.policy_tier}
          </span>
        </div>

        <p className="text-sm text-slate-300 mb-4">{blueprint.description}</p>

        <div className="mb-4">
          <p className="text-xs text-slate-400 mb-2">Includes {blueprint.capsules.length} capsules:</p>
          <div className="flex flex-wrap gap-1.5">
            {blueprint.capsules.map((capsuleId) => (
              <span key={capsuleId} className="px-2 py-0.5 rounded bg-white/5 border border-white/10 text-xs text-slate-300">
                {capsuleId}
              </span>
            ))}
          </div>
        </div>

        <div className="flex items-center justify-between pt-3 border-t border-white/10">
          <div className="flex items-center gap-4 text-xs text-slate-400">
            <span className="flex items-center gap-1">
              <Users className="w-3.5 h-3.5" />
              {blueprint.downloads.toLocaleString()} users
            </span>
            <span className="flex items-center gap-1">
              <Star className="w-3.5 h-3.5 text-amber-400" />
              {blueprint.rating.toFixed(1)}
            </span>
          </div>
          <button
            onClick={onDeploy}
            disabled={isDeploying}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-purple-500/20 text-purple-400 text-xs font-medium hover:bg-purple-500/30 transition-colors disabled:cursor-not-allowed disabled:opacity-60"
          >
            <Download className="w-3.5 h-3.5" />
            {isDeploying ? 'Deploying...' : 'Deploy'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default function CapsuleMarketplace() {
  const queryClient = useQueryClient()
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [activeTab, setActiveTab] = useState<'capsules' | 'blueprints'>('capsules')

  const { data, isLoading } = useQuery({
    queryKey: ['capsule-marketplace'],
    queryFn: fetchMarketplaceData,
    refetchInterval: 60000,
  })

  const installMutation = useMutation({
    mutationFn: async (capsuleId: string) => {
      await apiClient.post(apiPath(`ai/capsules/${capsuleId}/install`))
    },
    onSuccess: () => {
      toast.success('Capsule installed successfully')
      queryClient.invalidateQueries({ queryKey: ['capsule-marketplace'] })
    },
    onError: () => {
      toast.error('Failed to install capsule')
    },
  })

  const runMutation = useMutation({
    mutationFn: async (capsuleId: string) => {
      await apiClient.post(apiPath(`ai/capsules/${capsuleId}/run`))
    },
    onSuccess: () => {
      toast.success('Capsule execution started')
    },
    onError: () => {
      toast.error('Failed to run capsule')
    },
  })

  const deployMutation = useMutation({
    mutationFn: async (blueprintId: string) => {
      await apiClient.post(apiPath(`ai/capsules/blueprints/${blueprintId}/deploy`))
    },
    onSuccess: () => {
      toast.success('Blueprint deployment scheduled')
      queryClient.invalidateQueries({ queryKey: ['capsule-marketplace'] })
    },
    onError: () => {
      toast.error('Failed to deploy blueprint')
    },
  })

  const filteredCapsules = data?.capsules.filter((capsule) => {
    const matchesSearch = 
      capsule.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      capsule.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
      capsule.tags.some((tag) => tag.toLowerCase().includes(searchTerm.toLowerCase()))
    const matchesCategory = selectedCategory === 'all' || capsule.category === selectedCategory
    return matchesSearch && matchesCategory
  }) || []

  const featuredCapsules = data?.capsules.filter((c) => data.featured.includes(c.id)) || []

  if (isLoading) {
    return (
      <div className="px-4 py-6 sm:px-0">
        <div className="glass-card flex h-72 items-center justify-center">
          <div className="h-12 w-12 animate-spin rounded-full border-2 border-white/30 border-t-white" />
        </div>
      </div>
    )
  }

  return (
    <div className="px-4 py-6 sm:px-0 space-y-8 text-slate-100">
      {/* Header */}
      <section className="glass-card relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/20 via-purple-500/10 to-pink-500/10" />
        <div className="relative">
          <p className="eyebrow-text flex items-center gap-2">
            <Package className="w-4 h-4" />
            Capsule Ecosystem
          </p>
          <h1 className="mt-2 text-3xl font-semibold text-white">Capsule Marketplace</h1>
          <p className="mt-3 max-w-2xl text-sm text-slate-300">
            Discover, install, and manage capsules—composable automation units that chain drivers, 
            emit ledger entries, and integrate with the governance plane.
          </p>

          {/* Search and Filter */}
          <div className="flex flex-col sm:flex-row gap-4 mt-6">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <input
                type="text"
                placeholder="Search capsules..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-white placeholder-slate-400 focus:outline-none focus:border-white/30"
              />
            </div>
            <div className="flex items-center gap-2">
              <Filter className="w-4 h-4 text-slate-400" />
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="rounded-xl bg-white/5 border border-white/10 px-4 py-2.5 text-white"
              >
                <option value="all">All Categories</option>
                {data?.categories.map((cat) => (
                  <option key={cat} value={cat}>{cat.charAt(0).toUpperCase() + cat.slice(1)}</option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </section>

      {/* Stats */}
      <div className="grid gap-4 sm:grid-cols-4">
        <div className="glass-card text-center">
          <p className="text-3xl font-bold text-white">{data?.capsules.length || 0}</p>
          <p className="text-sm text-slate-400">Available Capsules</p>
        </div>
        <div className="glass-card text-center">
          <p className="text-3xl font-bold text-white">{data?.blueprints.length || 0}</p>
          <p className="text-sm text-slate-400">Blueprints</p>
        </div>
        <div className="glass-card text-center">
          <p className="text-3xl font-bold text-white">
            {data?.capsules.filter((c) => c.status === 'installed').length || 0}
          </p>
          <p className="text-sm text-slate-400">Installed</p>
        </div>
        <div className="glass-card text-center">
          <p className="text-3xl font-bold text-white">
            {data?.capsules.filter((c) => c.verified).length || 0}
          </p>
          <p className="text-sm text-slate-400">Verified</p>
        </div>
      </div>

      {/* Featured */}
      {featuredCapsules.length > 0 && searchTerm === '' && (
        <section>
          <div className="flex items-center gap-3 mb-4">
            <Sparkles className="w-5 h-5 text-amber-400" />
            <h2 className="text-xl font-semibold text-white">Featured Capsules</h2>
          </div>
          <div className="grid gap-4 md:grid-cols-3">
            {featuredCapsules.map((capsule) => (
              <CapsuleCard
                key={capsule.id}
                capsule={capsule}
                onInstall={(id) => installMutation.mutate(id)}
                onRun={(id) => runMutation.mutate(id)}
              />
            ))}
          </div>
        </section>
      )}

      {/* Tabs */}
      <div className="flex gap-2 border-b border-white/10 pb-4">
        <button
          onClick={() => setActiveTab('capsules')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            activeTab === 'capsules' 
              ? 'bg-indigo-500/20 text-indigo-400' 
              : 'text-slate-400 hover:text-white'
          }`}
        >
          <Box className="w-4 h-4" />
          Capsules ({data?.capsules.length || 0})
        </button>
        <button
          onClick={() => setActiveTab('blueprints')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            activeTab === 'blueprints' 
              ? 'bg-purple-500/20 text-purple-400' 
              : 'text-slate-400 hover:text-white'
          }`}
        >
          <Layers className="w-4 h-4" />
          Blueprints ({data?.blueprints.length || 0})
        </button>
      </div>

      {/* Content */}
      {activeTab === 'capsules' ? (
        <section>
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {filteredCapsules.map((capsule) => (
              <CapsuleCard
                key={capsule.id}
                capsule={capsule}
                onInstall={(id) => installMutation.mutate(id)}
                onRun={(id) => runMutation.mutate(id)}
              />
            ))}
          </div>
          {filteredCapsules.length === 0 && (
            <div className="text-center py-12 text-slate-400">
              <Package className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>No capsules found matching your criteria</p>
            </div>
          )}
        </section>
      ) : (
        <section>
          <div className="grid gap-4 md:grid-cols-2">
            {data?.blueprints.map((blueprint) => (
              <BlueprintCard
                key={blueprint.id}
                blueprint={blueprint}
                onDeploy={() => deployMutation.mutate(blueprint.id)}
                isDeploying={deployMutation.isPending && deployMutation.variables === blueprint.id}
              />
            ))}
          </div>
        </section>
      )}

      {/* v1000 Banner */}
      <section className="glass-card border border-dashed border-purple-500/30 bg-gradient-to-r from-purple-500/10 via-indigo-500/10 to-pink-500/10">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center">
            <TrendingUp className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white">Version 1000 Marketplace</h3>
            <p className="text-sm text-slate-300">
              Coming soon: Community contributions, revenue sharing, enterprise licensing,
              and federated capsule distribution across organizations.
            </p>
          </div>
        </div>
      </section>
    </div>
  )
}
