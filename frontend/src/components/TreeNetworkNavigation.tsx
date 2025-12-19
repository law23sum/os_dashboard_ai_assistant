/**
 * Tree-Network Map Topology Navigation Component
 * 
 * Tree: Top-level categories (tabs)
 * Network: Platforms/workspaces within each category (dropdowns)
 * Features: Left sidebar options per platform (ordered simple → complex)
 */

import { useState, useMemo } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { ChevronDown, ChevronRight, FileText } from 'lucide-react'
import { navigationStructure, NavigationCategory, NavigationPlatform, getFeaturesSortedByComplexity } from '../data/navigationStructure'

interface TreeNetworkNavigationProps {
  onFeatureSelect?: (featurePath: string) => void
}

export function TreeNetworkNavigation({ onFeatureSelect }: TreeNetworkNavigationProps) {
  const location = useLocation()
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set())
  const [selectedPlatform, setSelectedPlatform] = useState<string | null>(null)

  const toggleCategory = (categoryId: string) => {
    const newExpanded = new Set(expandedCategories)
    if (newExpanded.has(categoryId)) {
      newExpanded.delete(categoryId)
    } else {
      newExpanded.add(categoryId)
    }
    setExpandedCategories(newExpanded)
  }

  const handlePlatformSelect = (platform: NavigationPlatform) => {
    setSelectedPlatform(platform.id)
    if (onFeatureSelect && platform.features.length > 0) {
      // Select first feature by default
      const sortedFeatures = getFeaturesSortedByComplexity(platform)
      onFeatureSelect(sortedFeatures[0].path)
    }
  }

  return (
    <div className="tree-network-navigation flex h-full">
      {/* Tree: Top-level categories */}
      <div className="tree-categories w-64 border-r border-[color:var(--osd-border)] bg-[color:var(--osd-surfaceAlt)] overflow-y-auto">
        <div className="p-4 border-b border-[color:var(--osd-border)]">
          <h2 className="text-sm font-semibold text-[color:var(--osd-text)] uppercase tracking-wider">
            Categories
          </h2>
          <p className="text-xs text-[color:var(--osd-muted)] mt-1">
            Tree structure organized by spec sections
          </p>
        </div>
        <nav className="p-2">
          {navigationStructure.map((category) => {
            const CategoryIcon = category.icon
            const isExpanded = expandedCategories.has(category.id)
            const hasActivePlatform = category.platforms.some(
              (p) => location.pathname.startsWith(p.path)
            )

            return (
              <div key={category.id} className="mb-1">
                <button
                  onClick={() => toggleCategory(category.id)}
                  className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    hasActivePlatform
                      ? 'bg-[color:var(--osd-accent)]/20 text-[color:var(--osd-accent)]'
                      : 'text-[color:var(--osd-text)] hover:bg-[color:var(--osd-surface)]'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <CategoryIcon className="w-4 h-4" />
                    <span>{category.label}</span>
                  </div>
                  {isExpanded ? (
                    <ChevronDown className="w-4 h-4" />
                  ) : (
                    <ChevronRight className="w-4 h-4" />
                  )}
                </button>

                {/* Network: Platforms dropdown */}
                {isExpanded && (
                  <div className="ml-4 mt-1 space-y-1">
                    {category.platforms.map((platform) => {
                      const PlatformIcon = platform.icon
                      const isActive = location.pathname.startsWith(platform.path)
                      const isSelected = selectedPlatform === platform.id

                      return (
                        <div key={platform.id}>
                          <Link
                            to={platform.path}
                            onClick={() => handlePlatformSelect(platform)}
                            className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors ${
                              isActive || isSelected
                                ? 'bg-[color:var(--osd-accent)]/10 text-[color:var(--osd-accent)] border border-[color:var(--osd-accent)]/30'
                                : 'text-[color:var(--osd-muted)] hover:bg-[color:var(--osd-surface)] hover:text-[color:var(--osd-text)]'
                            }`}
                          >
                            <PlatformIcon className="w-4 h-4" />
                            <span className="flex-1">{platform.label}</span>
                          </Link>
                        </div>
                      )
                    })}
                  </div>
                )}
              </div>
            )
          })}
        </nav>
      </div>

      {/* Features: Left sidebar options list */}
      {selectedPlatform && (
        <FeatureSidebar
          platformId={selectedPlatform}
          onFeatureSelect={onFeatureSelect}
        />
      )}
    </div>
  )
}

interface FeatureSidebarProps {
  platformId: string
  onFeatureSelect?: (featurePath: string) => void
}

function FeatureSidebar({ platformId, onFeatureSelect }: FeatureSidebarProps) {
  const location = useLocation()
  
  const platform = useMemo(() => {
    for (const category of navigationStructure) {
      const found = category.platforms.find((p) => p.id === platformId)
      if (found) return found
    }
    return null
  }, [platformId])

  if (!platform) return null

  const sortedFeatures = getFeaturesSortedByComplexity(platform)

  return (
    <div className="feature-sidebar w-72 border-r border-[color:var(--osd-border)] bg-[color:var(--osd-background)] overflow-y-auto">
      <div className="p-4 border-b border-[color:var(--osd-border)] sticky top-0 bg-[color:var(--osd-background)] z-10">
        <div className="flex items-center gap-2 mb-2">
          {platform.icon && <platform.icon className="w-5 h-5 text-[color:var(--osd-accent)]" />}
          <h3 className="text-sm font-semibold text-[color:var(--osd-text)]">
            {platform.label}
          </h3>
        </div>
        {platform.description && (
          <p className="text-xs text-[color:var(--osd-muted)]">{platform.description}</p>
        )}
        {platform.specRef && (
          <p className="text-xs text-[color:var(--osd-muted)] mt-1">
            Spec: {platform.specRef}
          </p>
        )}
      </div>

      <div className="p-2">
        <div className="mb-2 px-2">
          <p className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">
            Features (Simple → Complex)
          </p>
        </div>
        <nav className="space-y-1">
          {sortedFeatures.map((feature) => {
            const FeatureIcon = feature.icon || FileText
            const isActive = location.pathname === feature.path

            return (
              <Link
                key={feature.id}
                to={feature.path}
                onClick={() => onFeatureSelect?.(feature.path)}
                className={`flex items-start gap-2 px-3 py-2 rounded-lg text-sm transition-colors group ${
                  isActive
                    ? 'bg-[color:var(--osd-accent)]/20 text-[color:var(--osd-accent)] border border-[color:var(--osd-accent)]/30'
                    : 'text-[color:var(--osd-text)] hover:bg-[color:var(--osd-surface)]'
                }`}
              >
                <FeatureIcon className={`w-4 h-4 mt-0.5 flex-shrink-0 ${
                  isActive ? 'text-[color:var(--osd-accent)]' : 'text-[color:var(--osd-muted)] group-hover:text-[color:var(--osd-text)]'
                }`} />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="font-medium">{feature.label}</span>
                    <span className={`text-xs px-1.5 py-0.5 rounded ${
                      feature.complexity === 'simple'
                        ? 'bg-emerald-500/20 text-emerald-300'
                        : feature.complexity === 'intermediate'
                        ? 'bg-blue-500/20 text-blue-300'
                        : feature.complexity === 'complex'
                        ? 'bg-amber-500/20 text-amber-300'
                        : 'bg-purple-500/20 text-purple-300'
                    }`}>
                      {feature.complexity}
                    </span>
                  </div>
                  {feature.description && (
                    <p className="text-xs text-[color:var(--osd-muted)] mt-1 line-clamp-2">
                      {feature.description}
                    </p>
                  )}
                  {feature.specRef && (
                    <p className="text-xs text-[color:var(--osd-muted)] mt-1">
                      {feature.specRef}
                    </p>
                  )}
                </div>
              </Link>
            )
          })}
        </nav>
      </div>
    </div>
  )
}
