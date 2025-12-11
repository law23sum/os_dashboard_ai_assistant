import { ReactNode, useEffect, useState, useRef } from 'react'
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
} from 'lucide-react'
import { applyTheme, defaultTheme } from '../theme'
import { useAppSettings } from '../hooks/useSettings'

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
  location: { pathname: string }
}

function NavDropdown({ item, childItems, active, expanded, onToggle, location }: NavDropdownProps) {
  const buttonRef = useRef<HTMLButtonElement>(null)
  const dropdownRef = useRef<HTMLDivElement>(null)
  const Icon = item.icon

  useEffect(() => {
    if (expanded && buttonRef.current && dropdownRef.current) {
      const buttonRect = buttonRef.current.getBoundingClientRect()
      dropdownRef.current.style.top = `${buttonRect.bottom + 8}px`
      dropdownRef.current.style.left = `${buttonRect.left}px`
    }
  }, [expanded])

  useEffect(() => {
    if (!expanded) return

    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        buttonRef.current &&
        !dropdownRef.current.contains(event.target as Node) &&
        !buttonRef.current.contains(event.target as Node)
      ) {
        onToggle()
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [expanded, onToggle])

  return (
    <>
      <div className="relative group flex items-center">
        <button
          ref={buttonRef}
          type="button"
          onClick={onToggle}
          className={`osd-nav-link ${active ? 'osd-nav-link--active' : ''}`}
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
          <div ref={dropdownRef} className="osd-dropdown w-72" style={{ position: 'fixed', zIndex: 99999 }}>
            {(item.groups && item.groups.length
              ? item.groups
              : [{ label: undefined, items: childItems }]
            ).map((group, index) => (
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
                        onClick={onToggle}
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

  useEffect(() => {
    if (settings?.theme) {
      applyTheme(settings.theme)
    } else {
      applyTheme(defaultTheme)
    }
  }, [settings?.theme])

  const toggleGroup = (groupPath: string) => {
    const newExpanded = new Set(expandedGroups)
    if (newExpanded.has(groupPath)) {
      newExpanded.delete(groupPath)
    } else {
      newExpanded.add(groupPath)
    }
    setExpandedGroups(newExpanded)
  }

  const navItems: NavItem[] = [
    { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
    { path: '/research', icon: FlaskConical, label: 'Research' },
    { path: '/tasks', icon: CheckSquare, label: 'Tasks' },
    { path: '/projects', icon: FolderKanban, label: 'Projects' },
    { path: '/chat', icon: MessageSquare, label: 'Chat' },
    {
      path: '/work',
      icon: BookOpen,
      label: 'Work',
      groups: [
        {
          label: 'Content Systems',
          description: 'Templates + Writer workspace (Canon Spec §2.1)',
          items: [
            { path: '/work/templates', icon: LayoutTemplate, label: 'Templates' },
            { path: '/work/writer', icon: BookOpen, label: 'Writer' },
          ],
        },
        {
          label: 'Automation & Tools',
          description: 'Shared tooling and terminal',
          items: [{ path: '/work/tools', icon: Terminal, label: 'Tools & Terminal' }],
        },
      ],
    },
    {
      path: '/integrations',
      icon: Plug,
      label: 'Integrations',
      children: [
        { path: '/integrations', icon: Plug, label: 'Overview' },
        { path: '/integrations/api-connectors', icon: Network, label: 'API Connectors' },
      ],
    },
    {
      path: '/analytics',
      icon: BarChart3,
      label: 'Insights',
      children: [
        { path: '/analytics', icon: BarChart3, label: 'Analytics' },
        { path: '/monitoring', icon: Activity, label: 'Monitoring' },
        { path: '/billing', icon: CreditCard, label: 'Billing' },
        { path: '/audit', icon: ClipboardList, label: 'Audit' },
      ],
    },
    {
      path: '/collaboration',
      icon: Users,
      label: 'Engagement',
      children: [
        { path: '/collaboration', icon: Users, label: 'Collaboration' },
        { path: '/personalization', icon: Target, label: 'Personalization' },
        { path: '/search', icon: SearchIcon, label: 'Search' },
        { path: '/computer-vision', icon: Eye, label: 'Computer Vision' },
      ],
    },
    {
      path: '/ai',
      icon: Brain,
      label: 'AI Stack',
      groups: [
        {
          label: 'Ops & Control',
          description: 'AI Ops feed, AI OS cockpit, and MLOps',
          items: [
            { path: '/ai/operations', icon: Cpu, label: 'Operations Feed' },
            { path: '/ai/os', icon: ServerCog, label: 'AI OS Control' },
            { path: '/ai/mlops', icon: Bot, label: 'MLOps' },
          ],
        },
        {
          label: 'Intelligence & Systems',
          description: 'Advanced engines + Canon system map',
          items: [
            { path: '/ai/advanced', icon: Brain, label: 'Advanced AI Engine' },
            { path: '/ai/systems', icon: Layers, label: 'Systems Map' },
          ],
        },
        {
          label: 'Research & NAS',
          description: 'Tkinter NAS dashboards mirrored in React',
          items: [
            { path: '/ai/nas', icon: Dna, label: 'NAS Dashboard' },
            { path: '/ai/nas/experiments', icon: FlaskConical, label: 'Experiment Console' },
          ],
        },
        {
          label: 'Edge & Security',
          description: 'Edge orchestration, workflows, and security operations',
          items: [
            { path: '/ai/security', icon: Shield, label: 'Security' },
            { path: '/ai/edge', icon: Satellite, label: 'Edge Computing' },
            { path: '/ai/workflows', icon: Workflow, label: 'Workflows' },
            { path: '/ai/vision', icon: Eye, label: 'Computer Vision' },
          ],
        },
      ],
    },
    {
      path: '/systems',
      icon: Layers,
      label: 'Systems',
      groups: [
        {
          label: 'Research & Simulation',
          description: 'Backend NAS experiments + simulator surfaces',
          items: [
            { path: '/ai/nas', icon: Dna, label: 'NAS Experiments' },
            { path: '/systems/nas', icon: Layers, label: 'NAS Simulator' },
            { path: '/systems/edge', icon: Satellite, label: 'Edge Computing' },
          ],
        },
        {
          label: 'Security & Workflows',
          items: [
            { path: '/systems/security', icon: Shield, label: 'Security Operations' },
            { path: '/systems/workflows', icon: Workflow, label: 'Workflow Orchestration' },
          ],
        },
      ],
    },
    {
      path: '/vision',
      icon: Sparkles,
      label: 'Vision',
      children: [
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
      path: '/docs',
      icon: FileText,
      label: 'Docs',
      groups: [
        {
          label: 'Core References',
          items: [
            { path: '/docs', icon: FileText, label: 'Docs Hub' },
            { path: '/docs/spec-sheet', icon: Compass, label: 'Technical Spec Sheet' },
          ],
        },
        {
          label: 'Vision & Futures',
          items: [
            { path: '/vision', icon: Sparkles, label: 'Vision Deck' },
            { path: '/future/core_os', icon: Layers, label: 'Core OS Envelope' },
          ],
        },
        {
          label: 'Legacy HTML',
          items: [{ path: '/docs/projects.html', icon: ExternalLink, label: 'Legacy Pages' }],
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

  const isExpanded = (item: NavItem): boolean =>
    expandedGroups.has(item.path) || isActive(item.path, extractChildren(item))

  return (
    <div className="osd-shell min-h-screen text-[color:var(--osd-text)]">
      {/* Top Navigation Bar */}
      <nav className="osd-nav border-b border-[color:var(--osd-border)]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8" style={{ overflow: 'visible' }}>
          <div className="flex justify-between h-auto" style={{ overflow: 'visible' }}>
            <div className="flex flex-col w-full" style={{ overflow: 'visible' }}>
              {/* Primary Navigation */}
              <div className="flex h-16" style={{ overflow: 'visible' }}>
                <div className="flex-shrink-0 flex items-center gap-3">
                  <div className="osd-logo" />
                  <div>
                    <p className="text-xs uppercase tracking-[0.2em] text-[color:var(--osd-muted)]">
                      Canonical Control Room
                    </p>
                    <h1 className="text-lg font-semibold">OS Dashboard · AI Assistant</h1>
                  </div>
                </div>
                <div className="hidden sm:ml-6 sm:flex sm:space-x-4 flex-1 overflow-x-auto overflow-y-visible items-center">
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
                          location={location}
                        />
                      )
                    }

                    return (
                      <div key={item.path} className="flex items-center">
                        <Link
                          to={item.path}
                          className={`osd-nav-link ${active ? 'osd-nav-link--active' : ''}`}
                        >
                          <Icon className="w-5 h-5 mr-2" />
                          {item.label}
                        </Link>
                      </div>
                    )
                  })}
                </div>
              </div>

              {/* Breadcrumb Navigation */}
              {location.pathname !== '/' && (
                <div className="flex items-center space-x-2 px-4 py-2 text-sm text-gray-500 dark:text-gray-400 border-t border-gray-200 dark:border-gray-700">
                  <Link to="/" className="hover:text-gray-700 dark:hover:text-gray-300">
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
                        <span key={path} className="flex items-center">
                          <span className="mx-2">/</span>
                          {isLast ? (
                            <span className="text-gray-900 dark:text-white font-medium">{label}</span>
                          ) : (
                            <Link to={path} className="hover:text-gray-700 dark:hover:text-gray-300">
                              {label}
                            </Link>
                          )}
                        </span>
                      )
                    })}
                </div>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="glass-content max-w-7xl mx-auto py-8 sm:px-6 lg:px-8">
        {children}
      </main>
    </div>
  )
}
