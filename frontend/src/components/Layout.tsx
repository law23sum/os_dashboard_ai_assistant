import { ReactNode, useEffect, useState, useRef, useCallback, useMemo } from 'react'
import { createPortal } from 'react-dom'
import { Link, useLocation } from 'react-router-dom'
import {
  LayoutDashboard,
  CheckSquare,
  FolderKanban,
  MessageSquare,
  Plug,
  Settings,
  Cpu,
  BarChart3,
  Bot,
  Target,
  Users,
  Activity,
  FileText,
  FlaskConical,
  BookOpen,
  LayoutTemplate,
  Network,
  ServerCog,
  Brain,
  Terminal,
  ClipboardList,
  Search as SearchIcon,
  ChevronDown,
  Eye,
  Shield,
  Dna,
  Layers,
  Satellite,
  Workflow,
  CreditCard,
  Compass,
  ExternalLink,
  Sparkles,
  Radio,
  Package,
  Wrench,
  Zap,
} from 'lucide-react'
import { applyTheme, defaultTheme } from '../theme'
import { useAppSettings } from '../hooks/useSettings'
import { UnifiedAIPanel } from './UnifiedAIPanel'
import { throttle } from '../shared/utils'
import PlatformFeatureSidebar from './PlatformFeatureSidebar'

interface LayoutProps {
  children: ReactNode
}

interface NavItem {
  path: string
  icon: React.ComponentType<{ className?: string }>
  label: string
  children?: NavItem[]
  groups?: NavGroup[]
}

interface NavGroup {
  label: string
  description?: string
  items: NavItem[]
}

const extractChildren = (item: NavItem): NavItem[] => {
  if (item.groups && item.groups.length) {
    return item.groups.flatMap((group) => group.items)
  }
  return item.children ?? []
}

interface NavDropdownProps {
  item: NavItem
  childItems: NavItem[]
  active: boolean
  expanded: boolean
  onToggle: () => void
  onClose: () => void
  location: { pathname: string }
}

function NavDropdown({ item, childItems, active, expanded, onToggle, onClose, location }: NavDropdownProps) {
  const buttonRef = useRef<HTMLButtonElement>(null)
  const dropdownRef = useRef<HTMLDivElement>(null)
  const expandedRef = useRef(expanded)
  const Icon = item.icon

  // Keep ref in sync with prop
  useEffect(() => {
    expandedRef.current = expanded
  }, [expanded])

  // Memoize the position update function
  const updatePosition = useCallback(() => {
    if (buttonRef.current && dropdownRef.current) {
      const buttonRect = buttonRef.current.getBoundingClientRect()
      const viewportWidth = window.innerWidth
      const viewportHeight = window.innerHeight
      const dropdownWidth = 288 // w-72 = 18rem = 288px
      
      // Calculate horizontal position (prevent overflow)
      let left = buttonRect.left
      if (left + dropdownWidth > viewportWidth) {
        left = viewportWidth - dropdownWidth - 16 // 16px padding from edge
      }
      if (left < 16) {
        left = 16
      }

      // Calculate vertical position
      const top = buttonRect.bottom + 8
      const dropdownHeight = dropdownRef.current.offsetHeight || 400 // estimate if not rendered yet
      
      // If dropdown would overflow bottom, position above button
      let finalTop = top
      if (top + dropdownHeight > viewportHeight && buttonRect.top > dropdownHeight) {
        finalTop = buttonRect.top - dropdownHeight - 8
      }

      dropdownRef.current.style.top = `${finalTop}px`
      dropdownRef.current.style.left = `${left}px`
    }
  }, [])

  // Throttle position updates for scroll/resize (100ms is sufficient for these events)
  const throttledUpdatePosition = useMemo(
    () => throttle(updatePosition, 100),
    [updatePosition]
  )

  useEffect(() => {
    if (!expanded) {
      // Reset position when closed
      if (dropdownRef.current) {
        dropdownRef.current.style.top = ''
        dropdownRef.current.style.left = ''
      }
      return
    }

    // Immediate position calculation - no delay for instant response
    updatePosition()

    // Update position on scroll and resize with throttling
    window.addEventListener('scroll', throttledUpdatePosition, { passive: true, capture: true })
    window.addEventListener('resize', throttledUpdatePosition, { passive: true })

    return () => {
      window.removeEventListener('scroll', throttledUpdatePosition, { capture: true } as EventListenerOptions)
      window.removeEventListener('resize', throttledUpdatePosition)
    }
  }, [expanded, updatePosition, throttledUpdatePosition])

  // Track if we should ignore the next click (to prevent immediate closure)
  const ignoreNextClickRef = useRef(false)
  const isButtonClickRef = useRef(false)

  // Simplified handlers - instant response
  const handleButtonClick = useCallback(
    (e: React.MouseEvent) => {
      e.stopPropagation()
      e.preventDefault()
      
      // Mark that this is a button click
      isButtonClickRef.current = true
      
      // If already expanded, close it
      if (expanded) {
        onClose()
      } else {
        // Mark to ignore the next click to prevent immediate closure
        ignoreNextClickRef.current = true
        onToggle()
        // Reset after a brief moment
        setTimeout(() => {
          ignoreNextClickRef.current = false
        }, 100)
      }
      
      // Reset button click flag after event completes
      setTimeout(() => {
        isButtonClickRef.current = false
      }, 0)
    },
    [onToggle, onClose, expanded]
  )

  const handleLinkClick = useCallback(
    (e: React.MouseEvent) => {
      e.stopPropagation()
      // Don't prevent default - allow navigation
      onClose()
    },
    [onClose]
  )

  // Click outside handler and Escape key - responsive and reliable
  useEffect(() => {
    if (!expanded) {
      return
    }

    const handleClickOutside = (event: MouseEvent) => {
      // Ignore if we just opened the dropdown or if this is a button click
      if (ignoreNextClickRef.current || isButtonClickRef.current) {
        return
      }

      const target = event.target as Node
      const button = buttonRef.current
      const dropdown = dropdownRef.current
      
      if (!button || !dropdown) return
      
      // Don't close if clicking on button or dropdown
      if (button.contains(target) || dropdown.contains(target)) {
        return
      }
      
      // Close when clicking outside
      onClose()
    }

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onClose()
      }
    }

    // Use click event instead of mousedown for better compatibility
    // Add listener immediately - ignoreNextClickRef prevents immediate closure
    document.addEventListener('click', handleClickOutside, true)
    document.addEventListener('keydown', handleEscape, true)

    return () => {
      document.removeEventListener('click', handleClickOutside, true)
      document.removeEventListener('keydown', handleEscape, true)
    }
  }, [expanded, onClose])

  // Memoize groups to avoid unnecessary re-renders
  const groups = useMemo(
    () => (item.groups && item.groups.length ? item.groups : [{ label: undefined, items: childItems }]),
    [item.groups, childItems]
  )

  return (
    <>
      <div className="relative group flex items-center" style={{ zIndex: expanded ? 10001 : 'auto', position: 'relative' }}>
        <button
          ref={buttonRef}
          type="button"
          onClick={handleButtonClick}
          className={`osd-nav-link ${active ? 'osd-nav-link--active' : ''}`}
          style={{ 
            pointerEvents: 'auto', 
            position: 'relative', 
            zIndex: expanded ? 10002 : 'auto',
            cursor: 'pointer',
            userSelect: 'none',
          }}
          aria-haspopup="menu"
          aria-expanded={expanded}
        >
          <Icon className="w-5 h-5 mr-2" />
          {item.label}
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
            onClick={(e) => {
              e.stopPropagation()
            }}
            onMouseDown={(e) => {
              e.stopPropagation()
            }}
          >
            {groups.map((group, index) => (
              <div
                key={`${item.path}-group-${group.label ?? index}`}
                className="px-4 py-3 border-b border-white/5 last:border-b-0"
              >
                {group.label && (
                  <div className="mb-2 space-y-1">
                    <p className="text-[0.65rem] uppercase tracking-[0.35em] text-[color:var(--osd-muted)]">
                      {group.label}
                    </p>
                    {group.description && (
                      <p className="text-[0.7rem] text-[color:var(--osd-muted)]">{group.description}</p>
                    )}
                  </div>
                )}
                <div className="space-y-1">
                  {group.items.map((child) => {
                    const ChildIcon = child.icon
                    const childActive = location.pathname === child.path
                    return (
                      <Link
                        key={child.path}
                        to={child.path}
                        className={`osd-dropdown-link ${childActive ? 'osd-dropdown-link--active' : ''}`}
                        onClick={handleLinkClick}
                        onMouseDown={(e) => {
                          e.stopPropagation()
                        }}
                        onMouseUp={(e) => {
                          e.stopPropagation()
                        }}
                      >
                        <ChildIcon className="w-4 h-4 mr-2" />
                        {child.label}
                      </Link>
                    )
                  })}
                </div>
              </div>
            ))}
          </div>,
          document.body
        )}
    </>
  )
}

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()
  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(new Set())
  const { data: settings } = useAppSettings()
  const aiButtonRef = useRef<HTMLButtonElement>(null)
  const [aiPanelOpen, setAiPanelOpen] = useState<boolean>(() => {
    if (typeof window === 'undefined') return false
    try {
      const stored = window.localStorage?.getItem?.('aiPanelOpen')
      return stored === 'true'
    } catch {
      return false
    }
  })

  useEffect(() => {
    if (typeof window === 'undefined') return
    try {
      window.localStorage?.setItem?.('aiPanelOpen', aiPanelOpen ? 'true' : 'false')
      console.log('✅ aiPanelOpen state changed to:', aiPanelOpen)
    } catch (error) {
      console.warn('Failed to save aiPanelOpen to localStorage:', error)
    }
  }, [aiPanelOpen])

  // Attach click handler directly via ref
  useEffect(() => {
    const button = aiButtonRef.current
    if (!button) {
      return
    }
    
    const handleClick = (e: MouseEvent) => {
      e.preventDefault()
      e.stopPropagation()
      setAiPanelOpen((prev) => !prev)
    }

    button.addEventListener('click', handleClick, true)
    
    return () => {
      // Check if button still exists before removing listener
      if (button && button.parentNode) {
        button.removeEventListener('click', handleClick, true)
      }
    }
  }, []) // Empty deps - handler uses functional setState


  useEffect(() => {
    if (settings?.theme) {
      applyTheme(settings.theme)
    } else {
      applyTheme(defaultTheme)
    }
  }, [settings?.theme])

  const toggleGroup = useCallback((groupPath: string) => {
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

  const closeGroup = useCallback((groupPath: string) => {
    setExpandedGroups((prev) => {
      const newExpanded = new Set(prev)
      newExpanded.delete(groupPath)
      return newExpanded
    })
  }, [])

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

  const isActive = (path: string, children?: NavItem[]): boolean => {
    if (path === '/') {
      return location.pathname === '/'
    }
    if (location.pathname === path) return true
    if (children && children.length) {
      return children.some((child) => location.pathname.startsWith(child.path))
    }
    return location.pathname.startsWith(`${path}/`)
  }

  // Expanded should be an explicit user toggle. Being "active" should not force open
  // (it makes dropdowns impossible to close when the current route matches).
  const isExpanded = (item: NavItem): boolean => expandedGroups.has(item.path)

  return (
    <div className="osd-shell min-h-screen text-[color:var(--osd-text)]">
      {/* Top Navigation Bar */}
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
                  {navItems.map((item) => {
                    const Icon = item.icon
                    const childItems = extractChildren(item)
                    const hasChildren = childItems.length > 0
                    const active = isActive(item.path, childItems)
                    const expanded = isExpanded(item)

                    if (hasChildren) {
                      return (
                        <NavDropdown
                          key={item.path}
                          item={item}
                          childItems={childItems}
                          active={active}
                          expanded={expanded}
                          onToggle={() => toggleGroup(item.path)}
                          onClose={() => closeGroup(item.path)}
                          location={location}
                        />
                      )
                    }

                    return (
                      <div key={item.path} className="flex items-center flex-shrink-0">
                        <Link
                          to={item.path}
                          className={`osd-nav-link ${active ? 'osd-nav-link--active' : ''}`}
                          aria-current={active ? 'page' : undefined}
                        >
                          <Icon className="w-5 h-5 mr-2 flex-shrink-0" />
                          <span className="whitespace-nowrap">{item.label}</span>
                        </Link>
                      </div>
                    )
                  })}
                </div>
              </div>

              {/* Enhanced Breadcrumb Navigation */}
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
      </nav>

      {/* Main Content */}
      <main className="glass-content page-container w-full py-6 sm:py-8 px-3 sm:px-5 lg:px-8 min-h-[calc(100vh-8rem)]">
        <div className="flex flex-col gap-8 lg:flex-row w-full">
          <PlatformFeatureSidebar />
          <div className="flex-1 min-w-0 w-full">{children}</div>
        </div>
      </main>

      <UnifiedAIPanel currentPath={location.pathname} open={aiPanelOpen} onToggle={setAiPanelOpen} />

      {/* Enhanced AI Assistant Toggle Button - Floating Action Button */}
      <button
        ref={aiButtonRef}
        type="button"
        id="ai-assistant-toggle-button"
        className={`fixed bottom-6 flex items-center gap-2.5 rounded-full px-5 py-3 shadow-2xl cursor-pointer transition-all duration-300 z-[9999] backdrop-blur-md ${
          aiPanelOpen
            ? 'bg-[color:var(--osd-surface)]/90 text-[color:var(--osd-text)] hover:bg-[color:var(--osd-surface)] border border-[color:var(--osd-border)]'
            : 'bg-gradient-to-r from-[color:var(--osd-accent)] to-[color:var(--osd-accentPurple)] text-white hover:from-[color:var(--osd-accentHover)] hover:to-purple-600 border border-[color:var(--osd-accent)]/30 hover:shadow-[0_0_20px_rgba(99,102,241,0.4)]'
        }`}
        style={{
          right: aiPanelOpen ? '400px' : '24px',
          pointerEvents: 'auto',
          transform: aiPanelOpen ? 'scale(0.95)' : 'scale(1)',
        }}
        aria-pressed={aiPanelOpen}
        aria-label={aiPanelOpen ? 'Hide AI Assistant panel' : 'Show AI Assistant panel'}
      >
        <div className={`transition-transform duration-300 ${aiPanelOpen ? 'rotate-180' : ''}`}>
          <Sparkles className="w-5 h-5" />
        </div>
        <span className="font-medium text-sm whitespace-nowrap">
          {aiPanelOpen ? 'Hide Assistant' : 'AI Assistant'}
        </span>
        {!aiPanelOpen && (
          <div className="absolute -top-1 -right-1 w-3 h-3 bg-emerald-400 rounded-full border-2 border-[color:var(--osd-background)] animate-pulse" />
        )}
      </button>
    </div>
  )
}
