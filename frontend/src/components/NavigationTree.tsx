/**
 * NavigationTree Component
 * 
 * Implements the hybrid tree-network topology for navigation:
 * - Tree: Hierarchical category organization (top tabs)
 * - Network: Interconnected platforms and features (dropdowns)
 * 
 * Features are ordered from simple/common to complex/specialized per platform.
 */

import { useState, useMemo } from 'react'
import { Link, useLocation } from 'react-router-dom'
import {
  ChevronDown,
  ChevronRight,
  Layers,
  Brain,
  FlaskConical,
  Server,
  Plug,
  Settings,
  Rocket,
  Circle,
} from 'lucide-react'
import {
  navigationStructure,
  type NavigationCategory,
  type NavigationPlatform,
  type NavigationFeature,
  getPlatformBreadcrumb,
} from '../lib/navigationStructure'

interface NavigationTreeProps {
  collapsed?: boolean
  onNavigate?: () => void
}

const complexityColors = {
  simple: 'text-emerald-400',
  intermediate: 'text-sky-400',
  advanced: 'text-amber-400',
  expert: 'text-rose-400',
}

const tierBadges = {
  core: { label: 'Core', color: 'bg-blue-500/20 text-blue-300 border-blue-500/30' },
  advanced: { label: 'Advanced', color: 'bg-purple-500/20 text-purple-300 border-purple-500/30' },
  super: { label: 'Super', color: 'bg-pink-500/20 text-pink-300 border-pink-500/30' },
  hyper: { label: 'Hyper', color: 'bg-orange-500/20 text-orange-300 border-orange-500/30' },
  ultra: { label: 'Ultra', color: 'bg-red-500/20 text-red-300 border-red-500/30' },
  supreme: { label: 'Supreme', color: 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30' },
  ascend: { label: 'Ascend', color: 'bg-indigo-500/20 text-indigo-300 border-indigo-500/30' },
}

export default function NavigationTree({ collapsed = false, onNavigate }: NavigationTreeProps) {
  const location = useLocation()
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set(['core-workspaces']))
  const [expandedPlatforms, setExpandedPlatforms] = useState<Set<string>>(new Set())

  const currentPath = location.pathname

  const toggleCategory = (categoryId: string) => {
    setExpandedCategories(prev => {
      const next = new Set(prev)
      if (next.has(categoryId)) {
        next.delete(categoryId)
      } else {
        next.add(categoryId)
      }
      return next
    })
  }

  const togglePlatform = (platformId: string) => {
    setExpandedPlatforms(prev => {
      const next = new Set(prev)
      if (next.has(platformId)) {
        next.delete(platformId)
      } else {
        next.add(platformId)
      }
      return next
    })
  }

  const handleNavigate = () => {
    onNavigate?.()
  }

  if (collapsed) {
    return (
      <nav className="flex flex-col gap-2 py-4">
        {navigationStructure.slice(0, 7).map(category => (
          <button
            key={category.id}
            onClick={() => toggleCategory(category.id)}
            className="flex items-center justify-center p-2 rounded-lg hover:bg-[color:var(--osd-surfaceAlt)] transition-colors"
            title={category.label}
          >
            <CategoryIcon category={category} />
          </button>
        ))}
      </nav>
    )
  }

  return (
    <nav className="flex flex-col gap-3 py-4">
      {navigationStructure.map(category => {
        const isExpanded = expandedCategories.has(category.id)
        
        return (
          <div key={category.id} className="space-y-2">
            {/* Category Header */}
            <button
              onClick={() => toggleCategory(category.id)}
              className="w-full flex items-center justify-between px-3 py-2 rounded-lg hover:bg-[color:var(--osd-surfaceAlt)] transition-colors group"
            >
              <div className="flex items-center gap-2">
                <CategoryIcon category={category} className="h-4 w-4" />
                <span className="text-sm font-semibold text-[color:var(--osd-text)]">
                  {category.label}
                </span>
                <span className={`text-xs px-2 py-0.5 rounded-full border ${tierBadges[category.tier].color}`}>
                  {tierBadges[category.tier].label}
                </span>
              </div>
              {isExpanded ? (
                <ChevronDown className="h-4 w-4 text-[color:var(--osd-muted)]" />
              ) : (
                <ChevronRight className="h-4 w-4 text-[color:var(--osd-muted)]" />
              )}
            </button>

            {/* Platforms (Network Nodes) */}
            {isExpanded && (
              <div className="ml-4 space-y-2 border-l border-[color:var(--osd-border)] pl-3">
                {category.platforms.map(platform => {
                  const isPlatformExpanded = expandedPlatforms.has(platform.id)
                  const hasActiveFeature = platform.features.some(f => f.path === currentPath)
                  
                  return (
                    <div key={platform.id} className="space-y-1">
                      {/* Platform Header */}
                      <button
                        onClick={() => togglePlatform(platform.id)}
                        className={`w-full flex items-center justify-between px-2 py-1.5 rounded-lg hover:bg-[color:var(--osd-surfaceAlt)] transition-colors ${
                          hasActiveFeature ? 'bg-[color:var(--osd-surfaceAlt)]' : ''
                        }`}
                      >
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-[color:var(--osd-muted)]">
                            {platform.label}
                          </span>
                          {platform.specRef && (
                            <span className="text-xs text-[color:var(--osd-muted)] opacity-60">
                              {platform.specRef}
                            </span>
                          )}
                        </div>
                        {isPlatformExpanded ? (
                          <ChevronDown className="h-3 w-3 text-[color:var(--osd-muted)]" />
                        ) : (
                          <ChevronRight className="h-3 w-3 text-[color:var(--osd-muted)]" />
                        )}
                      </button>

                      {/* Features (ordered by complexity) */}
                      {isPlatformExpanded && (
                        <div className="ml-4 space-y-0.5">
                          {platform.features.map(feature => {
                            const isActive = feature.path === currentPath
                            
                            return (
                              <Link
                                key={feature.id}
                                to={feature.path}
                                onClick={handleNavigate}
                                className={`flex items-center gap-2 px-2 py-1.5 rounded-lg text-xs transition-colors ${
                                  isActive
                                    ? 'bg-[color:var(--osd-accent)]/20 text-[color:var(--osd-accent)] font-medium'
                                    : 'text-[color:var(--osd-muted)] hover:text-[color:var(--osd-text)] hover:bg-[color:var(--osd-surfaceAlt)]'
                                }`}
                              >
                                <Circle className={`h-2 w-2 ${complexityColors[feature.complexity]}`} />
                                <span>{feature.label}</span>
                                {feature.specRef && (
                                  <span className="text-xs opacity-50">{feature.specRef}</span>
                                )}
                              </Link>
                            )
                          })}
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        )
      })}
    </nav>
  )
}

function CategoryIcon({ category, className = "h-5 w-5" }: { category: NavigationCategory; className?: string }) {
  const iconMap: Record<string, React.ComponentType<{ className?: string }>> = {
    Layers,
    Brain,
    FlaskConical,
    Server,
    Plug,
    Settings,
    Rocket,
  }

  const Icon = category.icon ? iconMap[category.icon] : Layers
  return <Icon className={`${className} text-[color:var(--osd-accent)]`} />
}

/**
 * Breadcrumb Component
 * Shows the current location in the navigation tree
 */
export function NavigationBreadcrumb() {
  const location = useLocation()
  const breadcrumb = useMemo(
    () => getPlatformBreadcrumb(location.pathname),
    [location.pathname]
  )

  if (breadcrumb.length === 0) return null

  return (
    <nav className="flex items-center gap-2 text-sm text-[color:var(--osd-muted)] mb-4">
      {breadcrumb.map((item, index) => (
        <span key={index} className="flex items-center gap-2">
          {index > 0 && <ChevronRight className="h-3 w-3" />}
          {item.path ? (
            <Link
              to={item.path}
              className="hover:text-[color:var(--osd-accent)] transition-colors"
            >
              {item.label}
            </Link>
          ) : (
            <span>{item.label}</span>
          )}
        </span>
      ))}
    </nav>
  )
}
