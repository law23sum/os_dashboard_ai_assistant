import { ReactNode, useEffect, useState, useRef, useCallback, useMemo } from 'react'
import { createPortal } from 'react-dom'
import { Link, useLocation } from 'react-router-dom'
import {
  LayoutDashboard,
  ChevronDown,
  Sparkles,
  ChevronRight,
  Menu,
  X
} from 'lucide-react'
import { applyTheme, defaultTheme } from '../theme'
import { useAppSettings } from '../hooks/useSettings'
import { UnifiedAIPanel } from './UnifiedAIPanel'
import { throttle } from '../shared/utils'
import PlatformFeatureSidebar from './PlatformFeatureSidebar'
import { navigationConfig, Category, Platform, FeatureOption } from '../config/navigation'
import { navigationManifest, findCategoryByPath, getAllPagesFromCategory, type NavCategory } from '../data/navigationManifest'

interface LayoutProps {
  children: ReactNode
}

interface NavDropdownProps {
  category: Category
  platforms: Platform[]
  category: NavCategory
  active: boolean
  expanded: boolean
  onToggle: () => void
  onClose: () => void
  location: { pathname: string }
}

function NavDropdown({ category, platforms, active, expanded, onToggle, onClose, location }: NavDropdownProps) {
  const buttonRef = useRef<HTMLButtonElement>(null)
  const dropdownRef = useRef<HTMLDivElement>(null)
  const expandedRef = useRef(expanded)
  
  // Use the first platform's icon or a default
  const Icon = platforms[0]?.icon || LayoutDashboard

  useEffect(() => {
    expandedRef.current = expanded
  }, [expanded])

  const updatePosition = useCallback(() => {
    if (buttonRef.current && dropdownRef.current) {
      const buttonRect = buttonRef.current.getBoundingClientRect()
      const viewportWidth = window.innerWidth
      const viewportHeight = window.innerHeight
      const dropdownWidth = 288
function NavDropdown({ category, active, expanded, onToggle, onClose, location }: NavDropdownProps) {
  const buttonRef = useRef<HTMLButtonElement>(null)
  const dropdownRef = useRef<HTMLDivElement>(null)
  const isTogglingRef = useRef(false)
  const Icon = category.icon

  useEffect(() => {
    if (expanded && buttonRef.current && dropdownRef.current) {
      const buttonRect = buttonRef.current.getBoundingClientRect()
      const viewportWidth = window.innerWidth
      const dropdownWidth = 288 // w-72
      
      let left = buttonRect.left
      if (left + dropdownWidth > viewportWidth) {
        left = viewportWidth - dropdownWidth - 16
      }
      if (left < 16) {
        left = 16
      }
      if (left < 16) left = 16

      const top = buttonRect.bottom + 8
      const dropdownHeight = dropdownRef.current.offsetHeight || 400
      
      let finalTop = top
      if (top + dropdownHeight > viewportHeight && buttonRect.top > dropdownHeight) {
        finalTop = buttonRect.top - dropdownHeight - 8
      }

      dropdownRef.current.style.top = `${finalTop}px`
      dropdownRef.current.style.left = `${left}px`
    }
  }, [])

  const throttledUpdatePosition = useMemo(
    () => throttle(updatePosition, 100),
    [updatePosition]
  )

  useEffect(() => {
    if (!expanded) {
      if (dropdownRef.current) {
        dropdownRef.current.style.top = ''
        dropdownRef.current.style.left = ''
      }
      return
    }

    updatePosition()
    window.addEventListener('scroll', throttledUpdatePosition, { passive: true, capture: true })
    window.addEventListener('resize', throttledUpdatePosition, { passive: true })

    return () => {
      window.removeEventListener('scroll', throttledUpdatePosition, { capture: true } as EventListenerOptions)
      window.removeEventListener('resize', throttledUpdatePosition)
    }
  }, [expanded, updatePosition, throttledUpdatePosition])

  const ignoreNextClickRef = useRef(false)
  const isButtonClickRef = useRef(false)

  const handleButtonClick = useCallback(
    (e: React.MouseEvent) => {
      e.stopPropagation()
      e.preventDefault()
      isButtonClickRef.current = true
      
      if (expanded) {
        onClose()
      } else {
        ignoreNextClickRef.current = true
        onToggle()
        setTimeout(() => { ignoreNextClickRef.current = false }, 100)
      }
      
      setTimeout(() => { isButtonClickRef.current = false }, 0)
    },
    [onToggle, onClose, expanded]
  )

  const handleLinkClick = useCallback(
    (e: React.MouseEvent) => {
      e.stopPropagation()
      onClose()
    },
    [onClose]
  )

  useEffect(() => {
    if (!expanded) return

    const handleClickOutside = (event: MouseEvent) => {
      if (ignoreNextClickRef.current || isButtonClickRef.current) return

      const target = event.target as Node
      const button = buttonRef.current
      const dropdown = dropdownRef.current
      
      if (!button || !dropdown) return
      if (button.contains(target) || dropdown.contains(target)) return
      
      onClose()
    }

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onClose()
    }

    document.addEventListener('click', handleClickOutside, true)
    document.addEventListener('keydown', handleEscape, true)
      dropdownRef.current.style.top = `${buttonRect.bottom + 8}px`
      dropdownRef.current.style.left = `${left}px`
    }
  }, [expanded])

  const handleButtonClick = useCallback((e: React.MouseEvent) => {
    e.stopPropagation()
    e.preventDefault()
    
    // Set flag to prevent click outside handler from firing
    isTogglingRef.current = true
    
    // Toggle the dropdown
    onToggle()
    
    // Reset flag after a brief delay to allow click event to complete
    // This prevents the click outside handler from immediately closing it
    requestAnimationFrame(() => {
      setTimeout(() => {
        isTogglingRef.current = false
      }, 50)
    })
  }, [onToggle])

  useEffect(() => {
    if (!expanded) {
      isTogglingRef.current = false
      return
    }

    const handleClickOutside = (event: MouseEvent) => {
      // Ignore if we're currently toggling (button was just clicked)
      if (isTogglingRef.current) {
        return
      }

      const target = event.target as Node
      
      // Don't close if clicking on button or dropdown
      if (
        !buttonRef.current ||
        !dropdownRef.current ||
        buttonRef.current.contains(target) ||
        dropdownRef.current.contains(target)
      ) {
        return
      }
      
      // Close when clicking outside
      onToggle()
    }

    // Use click event with capture phase to catch all clicks
    // Add small delay to ensure button click handler runs first
    const timeoutId = setTimeout(() => {
      document.addEventListener('click', handleClickOutside, true)
    }, 10)

    return () => {
      clearTimeout(timeoutId)
      document.removeEventListener('click', handleClickOutside, true)
    }
  }, [expanded, onClose])
  }, [expanded, onToggle])

  return (
    <>
      <div className="relative group flex items-center">
        <button
          ref={buttonRef}
          type="button"
          onClick={handleButtonClick}
          onMouseDown={(e) => {
            // Prevent mousedown from bubbling to document
            e.stopPropagation()
          }}
          className={`osd-nav-link ${active ? 'osd-nav-link--active' : ''}`}
          style={{ pointerEvents: 'auto', cursor: 'pointer' }}
          aria-haspopup="menu"
          aria-expanded={expanded}
        >
          {/* <Icon className="w-5 h-5 mr-2" /> */}
          <Icon className="w-5 h-5 mr-2" />
          {category.label}
          <ChevronDown
            className={`w-4 h-4 ml-1 transition-transform duration-150 ${
              expanded ? 'transform rotate-180' : ''
            }`}
          />
        </button>
      </div>
      {expanded &&
        createPortal(
          <div 
            ref={dropdownRef} 
            className="osd-dropdown w-72" 
            style={{ 
              position: 'fixed', 
              zIndex: 99999, 
              pointerEvents: 'auto',
            }}
            onClick={(e) => e.stopPropagation()}
            onMouseDown={(e) => e.stopPropagation()}
          >
            <div className="px-4 py-3">
              <div className="mb-2">
                <p className="text-[0.65rem] uppercase tracking-[0.35em] text-[color:var(--osd-muted)]">
                  Platforms
                </p>
            style={{ position: 'fixed', zIndex: 99999, pointerEvents: 'auto' }}
            onClick={(e) => {
              // Prevent clicks inside dropdown from bubbling to document
              e.stopPropagation()
            }}
            onMouseDown={(e) => {
              // Prevent mousedown from bubbling to document
              e.stopPropagation()
            }}
          >
            {category.groups.map((group, groupIndex) => (
              <div
                key={`${category.path}-group-${groupIndex}`}
                className="px-4 py-3 border-b border-white/5 last:border-b-0"
              >
                {group.label && (
                  <div className="mb-2 space-y-1">
                    <p className="text-[0.65rem] uppercase tracking-[0.35em] text-[color:var(--osd-muted)]">
                      {group.label}
                      {group.spec && <span className="ml-1 text-[0.6rem]">· {group.spec}</span>}
                    </p>
                    {group.description && (
                      <p className="text-[0.7rem] text-[color:var(--osd-muted)]">{group.description}</p>
                    )}
                  </div>
                )}
                <div className="space-y-1">
                  {group.items.map((item) => {
                    const ItemIcon = item.icon
                    const itemActive = location.pathname === item.path || location.pathname.startsWith(item.path + '/')
                    return (
                      <Link
                        key={item.path}
                        to={item.path}
                        className={`osd-dropdown-link ${itemActive ? 'osd-dropdown-link--active' : ''}`}
                        onClick={onToggle}
                      >
                        <ItemIcon className="w-4 h-4 mr-2" />
                        {item.label}
                        {item.status === 'new' && (
                          <span className="ml-auto text-[0.6rem] px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-400">
                            NEW
                          </span>
                        )}
                      </Link>
                    )
                  })}
                </div>
              </div>
              <div className="space-y-1">
                {platforms.map((platform) => {
                  const PlatformIcon = platform.icon
                  const platformActive = location.pathname.startsWith(platform.path)
                  return (
                    <Link
                      key={platform.id}
                      to={platform.path}
                      className={`osd-dropdown-link ${platformActive ? 'osd-dropdown-link--active' : ''}`}
                      onClick={handleLinkClick}
                    >
                      <PlatformIcon className="w-4 h-4 mr-2" />
                      {platform.label}
                    </Link>
                  )
                })}
              </div>
            </div>
          </div>,
          document.body
        )}
    </>
  )
}

function FeatureSidebar({ platform, activeFeature }: { platform: Platform, activeFeature?: string }) {
  if (!platform) return null;

  return (
    <div className="hidden lg:block w-64 flex-shrink-0 mr-8">
      <div className="sticky top-24 space-y-6">
        <div>
          <h3 className="text-sm font-semibold text-[color:var(--osd-text)] flex items-center gap-2 mb-4">
            <platform.icon className="w-4 h-4" />
            {platform.label} Features
          </h3>
          <nav className="space-y-1">
            {platform.features.map((feature) => (
              <button
                key={feature.id}
                className={`w-full flex items-center justify-between px-3 py-2 text-sm rounded-lg transition-colors text-left group ${
                  activeFeature === feature.id 
                    ? 'bg-[color:var(--osd-accentSoft)] text-[color:var(--osd-accent)]' 
                    : 'text-[color:var(--osd-muted)] hover:text-[color:var(--osd-text)] hover:bg-[color:var(--osd-surface)]'
                }`}
              >
                <span>{feature.label}</span>
                {feature.complexity && (
                  <span className={`text-[10px] uppercase tracking-wider px-1.5 py-0.5 rounded ${
                    feature.complexity === 'simple' ? 'bg-emerald-500/10 text-emerald-500' :
                    feature.complexity === 'intermediate' ? 'bg-amber-500/10 text-amber-500' :
                    'bg-rose-500/10 text-rose-500'
                  } opacity-0 group-hover:opacity-100 transition-opacity`}>
                    {feature.complexity === 'simple' ? 'Basic' : 
                     feature.complexity === 'intermediate' ? 'Inter' : 'Adv'}
                  </span>
                )}
              </button>
            ))}
          </nav>
        </div>
        
        {platform.description && (
          <div className="p-4 rounded-lg bg-[color:var(--osd-surface)] border border-[color:var(--osd-border)]">
            <p className="text-xs text-[color:var(--osd-muted)] leading-relaxed">
              {platform.description}
            </p>
          </div>
        )}
      </div>
    </div>
interface SidebarProps {
  category: NavCategory
  currentPath: string
}

function Sidebar({ category, currentPath }: SidebarProps) {
  const allPages = getAllPagesFromCategory(category)
  if (allPages.length === 0) return null

  return (
    <aside className="hidden lg:block w-64 flex-shrink-0">
      <div className="sticky top-24 space-y-4">
        {/* Category Header */}
        <div className="bg-[color:var(--osd-surface)]/80 backdrop-blur-md rounded-xl shadow-sm border border-[color:var(--osd-border)] p-4">
          <div className="mb-4 pb-3 border-b border-[color:var(--osd-border)]">
            <div className="flex items-center gap-2 mb-1">
              <category.icon className="w-5 h-5 text-[color:var(--osd-accent)]" />
              <h2 className="font-semibold text-[color:var(--osd-text)]">{category.label}</h2>
            </div>
            {category.spec && (
              <p className="text-[0.65rem] uppercase tracking-[0.35em] text-[color:var(--osd-muted)] mt-1">
                Spec {category.spec}
              </p>
            )}
            {category.description && (
              <p className="text-[0.7rem] text-[color:var(--osd-muted)] mt-2">{category.description}</p>
            )}
          </div>
        </div>

        {/* Groups and Pages */}
        {category.groups.map((group, groupIdx) => (
          <div
            key={`sidebar-group-${groupIdx}`}
            className="bg-[color:var(--osd-surface)]/80 backdrop-blur-md rounded-xl shadow-sm border border-[color:var(--osd-border)]"
          >
            <div className="px-4 pt-3">
              {group.label && (
                <h3 className="text-xs font-bold uppercase tracking-wider text-[color:var(--osd-muted)] mb-2">
                  {group.label}
                  {group.spec && <span className="ml-1 text-[0.6rem] normal-case">· {group.spec}</span>}
                </h3>
              )}
              {group.description && (
                <p className="text-[0.7rem] text-[color:var(--osd-muted)] mb-2">{group.description}</p>
              )}
            </div>
            <nav className="px-2 pb-2">
              <div className="space-y-1">
                {group.items.map((item) => {
                  const ItemIcon = item.icon
                  const isActive = currentPath === item.path || currentPath.startsWith(item.path + '/')
                  return (
                    <Link
                      key={item.path}
                      to={item.path}
                      className={`
                        flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all
                        ${isActive 
                          ? 'bg-[color:var(--osd-accentSoft)] text-[color:var(--osd-text)] border border-[color:var(--osd-accent)]/20 shadow-sm' 
                          : 'text-[color:var(--osd-muted)] hover:text-[color:var(--osd-text)] hover:bg-[color:var(--osd-surface)]'
                        }
                      `}
                      aria-current={isActive ? 'page' : undefined}
                    >
                      <ItemIcon className={`w-4 h-4 shrink-0 ${isActive ? 'text-[color:var(--osd-accent)]' : ''}`} />
                      <span className="truncate flex-1">{item.label}</span>
                      {item.status === 'new' && (
                        <span className="text-[0.6rem] px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-400 shrink-0">
                          NEW
                        </span>
                      )}
                    </Link>
                  )
                })}
              </div>
            </nav>
          </div>
        ))}
      </div>
    </aside>
  )
}

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set())
  // Single-open dropdown model for the top nav.
  // (Portaled menus behave best when only one is open at a time.)
  const [openGroupPath, setOpenGroupPath] = useState<string | null>(null)
  const { data: settings } = useAppSettings()
  const aiButtonRef = useRef<HTMLButtonElement>(null)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  
  const [aiPanelOpen, setAiPanelOpen] = useState<boolean>(() => {
    if (typeof window === 'undefined') return false
    try {
      const stored = window.localStorage?.getItem?.('aiPanelOpen')
    return stored === 'true'
    } catch {
      return false
    }
  })

  // Identify current category and platform
  const currentCategory = navigationConfig.find(cat => 
    location.pathname.startsWith(cat.path) || 
    cat.platforms.some(p => location.pathname.startsWith(p.path))
  )
  
  const currentPlatform = currentCategory?.platforms.find(p => 
    location.pathname.startsWith(p.path)
  )

  useEffect(() => {
    if (typeof window === 'undefined') return
    try {
      window.localStorage?.setItem?.('aiPanelOpen', aiPanelOpen ? 'true' : 'false')
    } catch (error) {
      console.warn('Failed to save aiPanelOpen to localStorage:', error)
    }
  }, [aiPanelOpen])

  useEffect(() => {
    const button = aiButtonRef.current
    if (!button) return
    
    const handleClick = (e: MouseEvent) => {
      e.preventDefault()
      e.stopPropagation()
      setAiPanelOpen((prev) => !prev)
    }

    button.addEventListener('click', handleClick, true)
    return () => {
      if (button && button.parentNode) {
        button.removeEventListener('click', handleClick, true)
      }
    }
  }, [])

  useEffect(() => {
    if (settings?.theme) {
      applyTheme(settings.theme)
    } else {
      applyTheme(defaultTheme)
    }
  }, [settings?.theme])

  const toggleCategory = useCallback((categoryId: string) => {
    setExpandedCategories((prev) => {
      const newExpanded = new Set(prev)
      if (newExpanded.has(categoryId)) {
        newExpanded.delete(categoryId)
      } else {
        newExpanded.clear() // Close others for accordion behavior if desired, or keep open
        newExpanded.add(categoryId)
      }
  const toggleGroup = useCallback((groupPath: string) => {
    setOpenGroupPath((prev) => (prev === groupPath ? null : groupPath))
    setExpandedGroups((prev) => {
      const newExpanded = new Set(prev)
    if (newExpanded.has(groupPath)) {
      newExpanded.delete(groupPath)
    } else {
      newExpanded.add(groupPath)
    }
      return newExpanded
    })
  }, [])

  const closeCategory = useCallback((categoryId: string) => {
    setExpandedCategories((prev) => {
      const newExpanded = new Set(prev)
      newExpanded.delete(categoryId)
      return newExpanded
    })
  }, [])

  const closeGroup = useCallback((groupPath: string) => {
    setOpenGroupPath((prev) => (prev === groupPath ? null : prev))
  }, [])

  useEffect(() => {
    // Close any open dropdown when navigation occurs.
    setOpenGroupPath(null)
  }, [location.pathname])

  const navItems: NavItem[] = [
    {
      path: '/dashboard',
      icon: LayoutDashboard,
      label: 'Mission Control',
      groups: [
        {
          label: 'Core Flight Deck · Spec §1.7',
          description: 'Dashboard, tasks, and projects for the driver-aware loop.',
          items: [
            { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
            { path: '/tasks', icon: CheckSquare, label: 'Tasks' },
            { path: '/projects', icon: FolderKanban, label: 'Projects' },
          ],
        },
        {
          label: 'Engagement & Persona Surfaces · Spec §7.12',
          description: 'Chat, collaboration, and personalization stay one click away.',
          items: [
            { path: '/chat', icon: MessageSquare, label: 'Chat' },
            { path: '/collaboration', icon: Users, label: 'Collaboration' },
            { path: '/personalization', icon: Target, label: 'Personalization' },
            { path: '/search', icon: SearchIcon, label: 'Search & Discovery' },
          ],
        },
      ],
    },
    {
      path: '/work',
      icon: BookOpen,
      label: 'Workspaces',
      groups: [
        {
          label: 'Research & Simulation · Spec §7.4',
          items: [{ path: '/research', icon: FlaskConical, label: 'Research Hub' }],
        },
        {
          label: 'Writer & Templates · Spec §7.5',
          items: [
            { path: '/work/writer', icon: BookOpen, label: 'Writer Workstation' },
            { path: '/work/templates', icon: LayoutTemplate, label: 'Templates' },
          ],
        },
        {
          label: 'Tools & Applied Intelligence',
          description: 'Shared tools and terminal surfaces for workspace operators.',
          items: [
            { path: '/work/tools', icon: Terminal, label: 'Tools & Terminal' },
            { path: '/workspace/health', icon: Activity, label: 'Workspace Health' },
          ],
        },
      ],
    },
    {
      path: '/ai',
      icon: Brain,
      label: 'AI Fabric',
      groups: [
        {
          label: 'Ops & Driver Fabric · Spec §5.1/§5.12',
          items: [
            { path: '/ai/operations', icon: Cpu, label: 'AI Operations' },
            { path: '/ai/os', icon: ServerCog, label: 'AI OS Control' },
            { path: '/ai/mlops', icon: Bot, label: 'MLOps' },
            { path: '/ai/intents', icon: Zap, label: 'Intent Processor' },
          ],
        },
        {
          label: 'Cognitive Engines · Spec §4',
          items: [
            { path: '/ai/copilot', icon: Bot, label: 'AI Copilot' },
            { path: '/ai/advanced', icon: Brain, label: 'Advanced AI Engine' },
            { path: '/ai/systems', icon: Layers, label: 'Systems Map' },
          ],
        },
        {
          label: 'Automation & Capsules · Spec §8',
          items: [
            { path: '/ai/workflows', icon: Workflow, label: 'Workflow Orchestrator' },
            { path: '/ai/capsules', icon: Package, label: 'Capsule Marketplace' },
            { path: '/ai/autofix', icon: Wrench, label: 'Auto-Fix Console' },
          ],
        },
        {
          label: 'Edge & Security · Spec §7.7/§10',
          items: [
            { path: '/ai/security', icon: Shield, label: 'Security Guardian' },
            { path: '/ai/edge', icon: Satellite, label: 'Edge Computing' },
            { path: '/ai/vision', icon: Eye, label: 'Computer Vision' },
          ],
        },
        {
          label: 'NAS & Simulation · Spec §7.4',
          items: [
            { path: '/ai/nas', icon: Dna, label: 'NAS Console' },
            { path: '/ai/nas/experiments', icon: FlaskConical, label: 'Experiment Console' },
            { path: '/ai/nas/simulator', icon: Layers, label: 'NAS Simulator' },
          ],
        },
      ],
    },
    {
      path: '/integrations',
      icon: Plug,
      label: 'Drivers & Integrations',
      groups: [
        {
          label: 'Connectors · Spec §9.18',
          items: [
            { path: '/integrations', icon: Plug, label: 'Overview' },
            { path: '/integrations/api-connectors', icon: Network, label: 'API Connectors' },
            { path: '/integrations/office', icon: Activity, label: 'Office Realtime' },
          ],
        },
        {
          label: 'Execution Surfaces · Spec §5.3',
          description: 'Driver-oriented system surfaces for workflows + security.',
          items: [
            { path: '/systems/security', icon: Shield, label: 'Security Operations' },
            { path: '/systems/network', icon: Network, label: 'Network Monitoring' },
            { path: '/systems/workflows', icon: Workflow, label: 'Workflow Orchestration' },
            { path: '/systems/nas', icon: Layers, label: 'NAS Simulator' },
            { path: '/systems/edge', icon: Satellite, label: 'Edge Systems' },
          ],
        },
      ],
    },
    {
      path: '/analytics',
      icon: BarChart3,
      label: 'Governance & Evidence',
      groups: [
        {
          label: 'Telemetry · Spec §11',
          items: [
            { path: '/analytics', icon: BarChart3, label: 'Analytics' },
            { path: '/monitoring', icon: Activity, label: 'Monitoring' },
            { path: '/observability', icon: Radio, label: 'Observability' },
          ],
        },
        {
          label: 'Finance & Audit · Spec §8.17/§15',
          items: [
            { path: '/billing', icon: CreditCard, label: 'Billing & Usage' },
            { path: '/audit', icon: ClipboardList, label: 'Audit Evidence' },
          ],
        },
      ],
    },
    {
      path: '/vision',
      icon: Sparkles,
      label: 'Vision & Docs',
      groups: [
        {
          label: 'Vision Deck · Spec §17',
          items: [
            { path: '/vision', icon: Compass, label: 'Vision Deck Hub' },
            { path: '/future/core_os', icon: Layers, label: 'Core OS Engines' },
            { path: '/future/advanced', icon: Brain, label: 'Advanced Horizons' },
            { path: '/future/super', icon: Dna, label: 'Super Capabilities' },
            { path: '/future/hyper', icon: Satellite, label: 'Hyper Network' },
            { path: '/future/ultra', icon: Workflow, label: 'Ultra Scale' },
            { path: '/future/supreme', icon: Shield, label: 'Supreme' },
            { path: '/future/ascend', icon: Shield, label: 'Ascend' },
            { path: '/future/meta', icon: Compass, label: 'Meta Envelope' },
          ],
        },
        {
          label: 'Canon & References',
          description: 'Spec + migration docs stay co-located.',
          items: [
            { path: '/docs', icon: FileText, label: 'Docs Hub' },
            { path: '/docs/spec-sheet', icon: Compass, label: 'Technical Spec Sheet' },
            { path: '/docs/migration_continued.md', icon: FileText, label: 'Migration Continued' },
            { path: '/docs/projects.html', icon: ExternalLink, label: 'Legacy Projects HTML' },
          ],
        },
      ],
    },
    { path: '/settings', icon: Settings, label: 'Settings' },
  ]
  // Find active category based on current path
  const activeCategory = useMemo(() => {
    return findCategoryByPath(location.pathname) || navigationManifest[0]
  }, [location.pathname])

  // Check if a category is active
  const isCategoryActive = (category: NavCategory): boolean => {
    if (location.pathname === category.path) return true
    const allPages = getAllPagesFromCategory(category)
    return allPages.some((page) => location.pathname === page.path || location.pathname.startsWith(page.path + '/'))
  }

  // Expanded should be an explicit user toggle. Being "active" should not force open
  // (it makes dropdowns impossible to close when the current route matches).
  const isExpanded = (item: NavItem): boolean => expandedGroups.has(item.path)

  const isExpanded = (item: NavItem): boolean =>
    openGroupPath === item.path
  // Check if category is expanded
  const isCategoryExpanded = (category: NavCategory): boolean => {
    return expandedGroups.has(category.path) || isCategoryActive(category)
  }
  return (
    <div className="osd-shell min-h-screen text-[color:var(--osd-text)] flex flex-col">
      {/* Top Navigation Bar */}
      <nav className="osd-nav border-b border-[color:var(--osd-border)] sticky top-0 z-50 bg-[color:var(--osd-background)]/80 backdrop-blur-md">
        <div className="w-full px-2 sm:px-4 lg:px-6">
          <div className="flex justify-between h-16 items-center">
             {/* Logo & Mobile Menu */}
            <div className="flex items-center gap-4">
              <button 
                className="lg:hidden p-2 text-[color:var(--osd-muted)] hover:text-[color:var(--osd-text)]"
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              >
                {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
              </button>
              
              <div className="flex items-center gap-3">
                <div className="osd-logo w-8 h-8 bg-gradient-to-br from-[color:var(--osd-accent)] to-[color:var(--osd-accentPurple)] rounded-lg shadow-lg" />
                <div className="hidden sm:block">
                  <p className="text-[0.6rem] uppercase tracking-[0.2em] text-[color:var(--osd-muted)] leading-none mb-1">
                    Canonical Control Room
                  </p>
                  <h1 className="text-sm font-semibold tracking-wide">OS DASHBOARD</h1>
      <nav className="osd-nav border-b border-[color:var(--osd-border)]">
        <div className="w-full px-2 sm:px-4 lg:px-6" style={{ overflow: 'visible' }}>
          <div className="flex justify-between h-auto" style={{ overflow: 'visible' }}>
            <div className="flex flex-col w-full" style={{ overflow: 'visible' }}>
              {/* Primary Navigation */}
              <div className="flex h-16" style={{ overflow: 'visible', position: 'relative', zIndex: 1 }}>
                <div className="flex-shrink-0 flex items-center gap-3" style={{ position: 'relative', zIndex: 1 }}>
                  <div className="osd-logo" />
                  <div>
                    <p className="text-xs uppercase tracking-[0.2em] text-[color:var(--osd-muted)]">
                      Canonical Control Room
                    </p>
                    <h1 className="text-lg font-semibold">OS Dashboard · AI Assistant</h1>
                  </div>
                </div>
                <div className="hidden sm:ml-6 sm:flex sm:space-x-2 flex-1 overflow-x-auto overflow-y-visible items-center scrollbar-hide" style={{ position: 'relative', zIndex: 2 }}>
                  {navigationManifest.map((category) => {
                    const active = isCategoryActive(category)
                    const expanded = isCategoryExpanded(category)
                    const allPages = getAllPagesFromCategory(category)

                    if (allPages.length > 0) {
                      return (
                        <NavDropdown
                          key={category.path}
                          category={category}
                          active={active}
                          expanded={expanded}
                          onToggle={() => toggleGroup(category.path)}
                          onClose={() => closeGroup(category.path)}
                          location={location}
                        />
                      )
                    }

                    return (
                      <div key={category.path} className="flex items-center flex-shrink-0">
                        <Link
                          to={category.path}
                          className={`osd-nav-link ${active ? 'osd-nav-link--active' : ''}`}
                          aria-current={active ? 'page' : undefined}
                        >
                          <category.icon className="w-5 h-5 mr-2 flex-shrink-0" />
                          <span className="whitespace-nowrap">{category.label}</span>
                        </Link>
                      </div>
                    )
                  })}
                </div>
              </div>
            </div>

            {/* Desktop Navigation */}
            <div className="hidden lg:flex items-center space-x-1">
              {navigationConfig.map((category) => {
                const isActive = currentCategory?.id === category.id
                const isExpanded = expandedCategories.has(category.id)

                return (
                  <NavDropdown
                    key={category.id}
                    category={category}
                    platforms={category.platforms}
                    active={isActive}
                    expanded={isExpanded}
                    onToggle={() => toggleCategory(category.id)}
                    onClose={() => closeCategory(category.id)}
                    location={location}
                  />
                )
              })}
            </div>
            {/* Right Actions */}
            <div className="flex items-center gap-2">
               {/* Placeholders for search/profile/notifications could go here */}
               <Link to="/settings" className="p-2 text-[color:var(--osd-muted)] hover:text-[color:var(--osd-text)] transition-colors">
                 <Settings className="w-5 h-5" />
               </Link>
              {/* Breadcrumb Navigation */}
              {location.pathname !== '/' && (
                <nav className="flex items-center space-x-1.5 px-4 py-2.5 text-sm border-t border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]/30 backdrop-blur-sm" aria-label="Breadcrumb">
                  <Link 
                    to="/" 
                    className="flex items-center gap-1.5 px-2 py-1 rounded-lg text-[color:var(--osd-muted)] hover:text-[color:var(--osd-text)] hover:bg-[color:var(--osd-surface)] transition-colors"
                    aria-label="Go to Dashboard"
                  >
                    <LayoutDashboard className="w-3.5 h-3.5" />
                    Dashboard
                  </Link>
                  {location.pathname
                    .split('/')
                    .filter(Boolean)
                    .map((segment, index, arr) => {
                      const path = '/' + arr.slice(0, index + 1).join('/')
                      const isLast = index === arr.length - 1
                      const label = segment
                        .split('-')
                        .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
                        .join(' ')

                      return (
                        <span key={path} className="flex items-center" aria-current={isLast ? 'page' : undefined}>
                          <span className="mx-1.5 text-[color:var(--osd-muted)]">/</span>
                          {isLast ? (
                            <span className="px-2.5 py-1 rounded-lg text-[color:var(--osd-text)] font-semibold bg-[color:var(--osd-accentSoft)]">
                              {label}
                            </span>
                          ) : (
                            <Link 
                              to={path} 
                              className="px-2 py-1 rounded-lg text-[color:var(--osd-muted)] hover:text-[color:var(--osd-text)] hover:bg-[color:var(--osd-surface)] transition-colors"
                            >
                              {label}
                            </Link>
                          )}
                        </span>
                      )
                    })}
                </nav>
              )}
            </div>
          </div>
        </div>
        {/* Breadcrumbs */}
        {location.pathname !== '/' && (
           <div className="px-4 py-2 border-t border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]/30 backdrop-blur-sm flex items-center text-xs">
              <Link to="/" className="hover:text-[color:var(--osd-accent)] transition-colors">Mission Control</Link>
              {currentCategory && (
                <>
                  <ChevronRight className="w-3 h-3 mx-2 text-[color:var(--osd-muted)]" />
                  <span className={!currentPlatform ? 'font-semibold text-[color:var(--osd-text)]' : 'text-[color:var(--osd-muted)]'}>
                    {currentCategory.label}
                  </span>
                </>
              )}
              {currentPlatform && (
                <>
                  <ChevronRight className="w-3 h-3 mx-2 text-[color:var(--osd-muted)]" />
                  <span className="font-semibold text-[color:var(--osd-text)]">
                    {currentPlatform.label}
                  </span>
                </>
              )}
           </div>
        )}
      </nav>
      {/* Main Content Area */}
      <div className="flex flex-1 min-h-0 relative">
        {/* Left Sidebar (Desktop) */}
        <aside className="hidden lg:block w-64 border-r border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]/20 overflow-y-auto">
           {currentPlatform ? (
             <div className="p-4">
                <FeatureSidebar platform={currentPlatform} />
             </div>
           ) : (
             <div className="p-4 text-center text-[color:var(--osd-muted)] text-sm italic mt-10">
               Select a platform to view features
             </div>
           )}
        </aside>

        {/* Content */}
        <main className="flex-1 min-w-0 overflow-y-auto py-6 px-4 sm:px-6 lg:px-8 glass-content">
          <div className="max-w-7xl mx-auto">
             {children}
          </div>
        </main>
      </div>

      <UnifiedAIPanel currentPath={location.pathname} open={aiPanelOpen} onToggle={setAiPanelOpen} />

      {/* Main Content with Left Sidebar */}
      <main className="glass-content page-container w-full py-6 sm:py-8 px-3 sm:px-5 lg:px-8 min-h-[calc(100vh-8rem)]">
        <div className="flex flex-col gap-8 lg:flex-row w-full">
          <PlatformFeatureSidebar />
        <div className="flex w-full gap-6">
          {/* Left Sidebar Navigation - Shows pages for active category */}
          {activeCategory && getAllPagesFromCategory(activeCategory).length > 0 && (
            <Sidebar category={activeCategory} currentPath={location.pathname} />
          )}

          {/* Main Content Pane */}
          <div className="flex-1 min-w-0 w-full">{children}</div>
        </div>
      </main>

      <UnifiedAIPanel currentPath={location.pathname} open={aiPanelOpen} onToggle={setAiPanelOpen} />

      {/* AI Assistant Toggle Button */}
      <button
        ref={aiButtonRef}
        type="button"
        id="ai-assistant-toggle-button"
        className={`fixed bottom-6 right-6 flex items-center gap-2.5 rounded-full px-5 py-3 shadow-2xl cursor-pointer transition-all duration-300 z-[9999] backdrop-blur-md ${
          aiPanelOpen
            ? 'bg-[color:var(--osd-surface)]/90 text-[color:var(--osd-text)] hover:bg-[color:var(--osd-surface)] border border-[color:var(--osd-border)]'
            : 'bg-gradient-to-r from-[color:var(--osd-accent)] to-[color:var(--osd-accentPurple)] text-white hover:from-[color:var(--osd-accentHover)] hover:to-purple-600 border border-[color:var(--osd-accent)]/30 hover:shadow-[0_0_20px_rgba(99,102,241,0.4)]'
        }`}
        style={{
          right: aiPanelOpen ? '400px' : '24px',
        }}
        aria-pressed={aiPanelOpen}
      >
        <div className={`transition-transform duration-300 ${aiPanelOpen ? 'rotate-180' : ''}`}>
          <Sparkles className="w-5 h-5" />
        </div>
        <span className="font-medium text-sm whitespace-nowrap">
          {aiPanelOpen ? 'Hide Assistant' : 'AI Assistant'}
        </span>
      </button>
    </div>
  )
}
