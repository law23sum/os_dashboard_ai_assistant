import { ReactNode, useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { createPortal } from 'react-dom'
import { Link, Navigate, Outlet, useLocation, useNavigate } from 'react-router-dom'
import {
  Bell,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  HelpCircle,
  LogOut,
  Menu,
  PanelLeft,
  Settings,
  Shield,
  Sparkles,
  UserCog,
  X,
} from 'lucide-react'
import { applyTheme, defaultTheme } from '../theme'
import { useAppSettings } from '../hooks/useSettings'
import { UnifiedAIPanel } from './UnifiedAIPanel'
import GlobalSearch from './GlobalSearch'
import ActorSwitch from './ActorSwitch'
import { useActor } from '../contexts/ActorContext'
import { useAuth } from '../auth/AuthContext'
import { useIARouteContext } from '../navigation/iaContext'
import {
  getCategories,
  getFeatures,
  getPlatforms,
  legacyRedirects,
  type Category,
  type NavItem,
  type Platform,
} from '../data/iaManifest'

type Breadcrumb = {
  label: string
  path: string
}

interface LayoutProps {
  children?: ReactNode
}

function useDropdownPosition(
  open: boolean,
  buttonRef: React.RefObject<HTMLButtonElement>,
  dropdownRef: React.RefObject<HTMLDivElement>,
) {
  const update = useCallback(() => {
    const button = buttonRef.current
    const menu = dropdownRef.current
    if (!button || !menu) return

    const rect = button.getBoundingClientRect()
    const viewportWidth = window.innerWidth
    const viewportHeight = window.innerHeight
    const dropdownWidth = 320
    const margin = 12

    let left = rect.left
    if (left + dropdownWidth > viewportWidth - margin) {
      left = viewportWidth - dropdownWidth - margin
    }
    if (left < margin) left = margin

    const belowTop = rect.bottom + 8
    const menuHeight = menu.offsetHeight || 420
    const aboveTop = rect.top - menuHeight - 8
    const top =
      belowTop + menuHeight > viewportHeight - margin && aboveTop > margin ? aboveTop : belowTop

    menu.style.left = `${left}px`
    menu.style.top = `${top}px`
  }, [buttonRef, dropdownRef])

  useEffect(() => {
    if (!open) return
    update()
    const onScroll = () => update()
    const onResize = () => update()
    window.addEventListener('scroll', onScroll, { capture: true, passive: true })
    window.addEventListener('resize', onResize, { passive: true })
    return () => {
      window.removeEventListener('scroll', onScroll, { capture: true } as EventListenerOptions)
      window.removeEventListener('resize', onResize)
    }
  }, [open, update])
}

function PlatformDropdown({
  platform,
  categories,
  open,
  isActive,
  onOpen,
  onClose,
}: {
  platform: Platform
  categories: Category[]
  open: boolean
  isActive: boolean
  onOpen: () => void
  onClose: () => void
}) {
  const navigate = useNavigate()
  const buttonRef = useRef<HTMLButtonElement>(null)
  const dropdownRef = useRef<HTMLDivElement>(null)

  useDropdownPosition(open, buttonRef, dropdownRef)

  useEffect(() => {
    if (!open) return

    const onDocClick = (e: MouseEvent) => {
      const target = e.target as Node
      if (buttonRef.current?.contains(target)) return
      if (dropdownRef.current?.contains(target)) return
      onClose()
    }

    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key !== 'Escape') return
      event.preventDefault()
      onClose()
    }

    document.addEventListener('click', onDocClick, true)
    document.addEventListener('keydown', onKeyDown)
    return () => {
      document.removeEventListener('click', onDocClick, true)
      document.removeEventListener('keydown', onKeyDown)
    }
  }, [open, onClose])

  return (
    <>
      <button
        ref={buttonRef}
        type="button"
        className={`osd-nav-link ${isActive ? 'osd-nav-link--active' : ''}`}
        aria-haspopup="menu"
        aria-expanded={open}
        onClick={(event) => {
          event.preventDefault()
          event.stopPropagation()
          if (open) onClose()
          else onOpen()
        }}
        onMouseDown={(event) => event.stopPropagation()}
      >
        <span className="whitespace-nowrap">{platform.label}</span>
        <ChevronDown className={`w-4 h-4 ml-1 transition-transform ${open ? 'rotate-180' : ''}`} />
      </button>

      {open
        ? createPortal(
            <div
              ref={dropdownRef}
              className="osd-dropdown w-80"
              style={{ position: 'fixed', zIndex: 99999, pointerEvents: 'auto' }}
              onClick={(event) => event.stopPropagation()}
              onMouseDown={(event) => event.stopPropagation()}
              role="menu"
            >
              <div className="px-4 py-3 border-b border-white/5">
                <p className="text-[0.65rem] uppercase tracking-[0.35em] text-[color:var(--osd-muted)]">
                  Categories
                </p>
                <p className="mt-1 text-sm font-semibold text-[color:var(--osd-text)]">{platform.label}</p>
              </div>
              <div className="py-2">
                {categories.map((category) => {
                  const newCount = category.features.filter((feature) => feature.isNew).length
                  const description = `Overview and quick actions for ${category.label}.`
                  return (
                    <button
                      key={category.id}
                      type="button"
                      role="menuitem"
                      className="w-full text-left px-4 py-2 hover:bg-[color:var(--osd-surface)] transition-colors"
                      onClick={() => {
                        onClose()
                        navigate(category.homeRoute)
                      }}
                    >
                      <div className="flex items-center gap-2">
                        <div className="text-sm font-medium text-[color:var(--osd-text)]">{category.label}</div>
                        {newCount > 0 ? (
                          <span className="text-[0.55rem] uppercase tracking-wider px-2 py-0.5 rounded-full border border-emerald-400/40 text-emerald-300">
                            New
                          </span>
                        ) : null}
                      </div>
                      <div className="text-xs text-[color:var(--osd-muted)] mt-0.5">{description}</div>
                      <div className="text-[0.65rem] text-[color:var(--osd-muted)] mt-1">
                        {category.features.length} features
                      </div>
                    </button>
                  )
                })}
              </div>
            </div>,
            document.body,
          )
        : null}
    </>
  )
}

function FeatureSidebar({
  category,
  features,
  currentPath,
}: {
  category: Category
  features: NavItem[]
  currentPath: string
}) {
  const [collapsed, setCollapsed] = useState(false)
  const expanded = !collapsed
  const itemRefs = useRef<Array<HTMLAnchorElement | null>>([])

  const focusItem = useCallback(
    (index: number) => {
      if (!features.length) return
      const total = features.length
      const nextIndex = (index + total) % total
      itemRefs.current[nextIndex]?.focus()
    },
    [features.length],
  )

  const handleKeyDown = useCallback(
    (event: React.KeyboardEvent, index: number) => {
      switch (event.key) {
        case 'ArrowDown':
          event.preventDefault()
          focusItem(index + 1)
          break
        case 'ArrowUp':
          event.preventDefault()
          focusItem(index - 1)
          break
        case 'Home':
          event.preventDefault()
          focusItem(0)
          break
        case 'End':
          event.preventDefault()
          focusItem(features.length - 1)
          break
        case 'Escape':
          event.preventDefault()
          setCollapsed(true)
          break
        default:
          break
      }
    },
    [features.length, focusItem],
  )

  return (
    <aside
      className={`hidden lg:flex flex-col shrink-0 border-r border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]/20 transition-all duration-200 ${
        expanded ? 'w-72' : 'w-16'
      }`}
      aria-expanded={expanded}
    >
      <div className="flex items-center justify-between gap-2 px-3 py-3 border-b border-[color:var(--osd-border)]">
        <div className={`min-w-0 ${expanded ? 'opacity-100' : 'opacity-0'} transition-opacity duration-150`}>
          <p className="text-[0.6rem] uppercase tracking-[0.35em] text-[color:var(--osd-muted)]">Category</p>
          <p className="text-sm font-semibold text-[color:var(--osd-text)] truncate">{category.label}</p>
        </div>
        <button
          type="button"
          className="text-[color:var(--osd-muted)] hover:text-[color:var(--osd-text)]"
          onClick={() => setCollapsed((prev) => !prev)}
          aria-label={expanded ? 'Collapse sidebar' : 'Expand sidebar'}
        >
          {expanded ? <ChevronLeft className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
        </button>
      </div>

      <nav
        className={`flex-1 overflow-y-auto ${expanded ? 'px-2 pb-3' : 'px-1 pb-2'}`}
        role="menu"
        aria-label={`${category.label} features`}
      >
        <div className="space-y-1">
          {features.map((item, index) => {
            const isActive = currentPath === item.route || currentPath.startsWith(item.route + '/')
            const tooltipId = `feature-tooltip-${item.id || item.route.replace(/[^a-z0-9]/gi, '-')}`
            return (
              <Link
                key={item.route}
                to={item.route}
                ref={(el) => {
                  itemRefs.current[index] = el
                }}
                onKeyDown={(event) => handleKeyDown(event, index)}
                className={`group relative flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-[color:var(--osd-accentSoft)] text-[color:var(--osd-text)] border border-[color:var(--osd-accent)]/20 shadow-sm'
                    : 'text-[color:var(--osd-muted)] hover:text-[color:var(--osd-text)] hover:bg-[color:var(--osd-surface)]'
                }`}
                title={item.label}
                aria-label={expanded ? undefined : item.label}
                aria-describedby={expanded ? undefined : tooltipId}
                aria-current={isActive ? 'page' : undefined}
                role="menuitem"
              >
                <Sparkles className={`w-4 h-4 shrink-0 ${isActive ? 'text-[color:var(--osd-accent)]' : ''}`} />
                <span className={expanded ? 'truncate' : 'sr-only'}>{item.label}</span>
                {!expanded && (
                  <span
                    id={tooltipId}
                    role="tooltip"
                    className="pointer-events-none absolute left-full top-1/2 z-50 ml-2 -translate-y-1/2 whitespace-nowrap rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] px-3 py-1 text-xs text-[color:var(--osd-text)] opacity-0 shadow-lg transition-opacity group-hover:opacity-100 group-focus-visible:opacity-100"
                  >
                    {item.label}
                  </span>
                )}
              </Link>
            )
          })}
        </div>
      </nav>
    </aside>
  )
}

function UserMenu() {
  const [isOpen, setIsOpen] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)
  const navigate = useNavigate()

  const user = useMemo(() => {
    try {
      const userData = localStorage.getItem('user')
      return userData ? JSON.parse(userData) : null
    } catch {
      return null
    }
  }, [])

  const isAdmin = Boolean(user?.is_admin)
  const isLoggedIn = !!localStorage.getItem('access_token')

  useEffect(() => {
    if (!isOpen) return

    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    document.addEventListener('click', handleClickOutside, true)
    return () => document.removeEventListener('click', handleClickOutside, true)
  }, [isOpen])

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
    navigate('/login')
  }

  if (!isLoggedIn) {
    return (
      <div className="flex items-center gap-2">
        <Link
          to="/login"
          className="px-3 py-2 text-sm text-[color:var(--osd-muted)] hover:text-[color:var(--osd-text)] transition-colors"
        >
          Sign In
        </Link>
        <Link
          to="/signup"
          className="px-3 py-2 text-sm bg-[color:var(--osd-accent)] text-white rounded-lg hover:opacity-90 transition-opacity"
        >
          Sign Up
        </Link>
      </div>
    )
  }

  return (
    <div className="relative" ref={menuRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-[color:var(--osd-surface)] transition-colors"
      >
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[color:var(--osd-accent)] to-[color:var(--osd-accentPurple)] flex items-center justify-center">
          <span className="text-sm font-medium text-white">
            {user?.username?.charAt(0).toUpperCase() || 'U'}
          </span>
        </div>
        <span className="text-sm font-medium hidden sm:block">{user?.username || 'User'}</span>
        {isAdmin && <Shield className="w-4 h-4 text-amber-400" />}
        <ChevronDown className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <div className="absolute right-0 top-full mt-2 w-48 bg-[color:var(--osd-surface)] border border-[color:var(--osd-border)] rounded-xl shadow-xl overflow-hidden z-50">
          <div className="px-4 py-3 border-b border-[color:var(--osd-border)]">
            <p className="text-sm font-medium">{user?.full_name || user?.username}</p>
            <p className="text-xs text-[color:var(--osd-muted)]">{user?.email}</p>
            {isAdmin && (
              <span className="inline-flex items-center gap-1 mt-1 text-xs text-amber-400">
                <Shield className="w-3 h-3" />
                Administrator
              </span>
            )}
          </div>
          <div className="py-1">
            <Link
              to="/settings"
              onClick={() => setIsOpen(false)}
              className="flex items-center gap-2 px-4 py-2 text-sm hover:bg-[color:var(--osd-accentSoft)] transition-colors"
            >
              <Settings className="w-4 h-4" />
              Settings
            </Link>
            {isAdmin && (
              <Link
                to="/admin"
                onClick={() => setIsOpen(false)}
                className="flex items-center gap-2 px-4 py-2 text-sm hover:bg-[color:var(--osd-accentSoft)] transition-colors text-amber-400"
              >
                <Shield className="w-4 h-4" />
                Admin Panel
              </Link>
            )}
            <button
              onClick={handleLogout}
              className="w-full flex items-center gap-2 px-4 py-2 text-sm hover:bg-red-500/10 text-red-400 transition-colors"
            >
              <LogOut className="w-4 h-4" />
              Sign Out
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

function TenantMenu() {
  const [isOpen, setIsOpen] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!isOpen) return

    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    document.addEventListener('click', handleClickOutside, true)
    return () => document.removeEventListener('click', handleClickOutside, true)
  }, [isOpen])

  return (
    <div className="relative" ref={menuRef}>
      <button
        onClick={() => setIsOpen((prev) => !prev)}
        className="p-2 rounded-lg text-[color:var(--osd-muted)] hover:text-[color:var(--osd-text)] hover:bg-[color:var(--osd-surface)] transition-colors"
        aria-label="Tenant controls"
      >
        <UserCog className="w-5 h-5" />
      </button>

      {isOpen && (
        <div className="absolute right-0 top-full mt-2 w-56 bg-[color:var(--osd-surface)] border border-[color:var(--osd-border)] rounded-xl shadow-xl overflow-hidden z-50">
          <div className="px-4 py-3 border-b border-[color:var(--osd-border)]">
            <p className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Tenant & Admin</p>
            <p className="text-sm font-semibold text-[color:var(--osd-text)]">Enterprise controls</p>
          </div>
          <div className="py-1">
            <Link
              to="/admin"
              onClick={() => setIsOpen(false)}
              className="flex items-center gap-2 px-4 py-2 text-sm hover:bg-[color:var(--osd-accentSoft)] transition-colors"
            >
              <Shield className="w-4 h-4" />
              Admin Console
            </Link>
            <Link
              to="/settings/enterprise/user-tenant"
              onClick={() => setIsOpen(false)}
              className="flex items-center gap-2 px-4 py-2 text-sm hover:bg-[color:var(--osd-accentSoft)] transition-colors"
            >
              <Settings className="w-4 h-4" />
              User & Tenant Settings
            </Link>
            <Link
              to="/settings/team"
              onClick={() => setIsOpen(false)}
              className="flex items-center gap-2 px-4 py-2 text-sm hover:bg-[color:var(--osd-accentSoft)] transition-colors"
            >
              <Settings className="w-4 h-4" />
              Team & Members
            </Link>
            <Link
              to="/settings/tenant"
              onClick={() => setIsOpen(false)}
              className="flex items-center gap-2 px-4 py-2 text-sm hover:bg-[color:var(--osd-accentSoft)] transition-colors"
            >
              <Settings className="w-4 h-4" />
              Tenancy & Org Settings
            </Link>
            <Link
              to="/settings/audit"
              onClick={() => setIsOpen(false)}
              className="flex items-center gap-2 px-4 py-2 text-sm hover:bg-[color:var(--osd-accentSoft)] transition-colors"
            >
              <Settings className="w-4 h-4" />
              Audit Settings
            </Link>
          </div>
        </div>
      )}
    </div>
  )
}

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()
  const { currentActor } = useActor()
  const { state: authState } = useAuth()
  const [openPlatformId, setOpenPlatformId] = useState<string | null>(null)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false)
  const aiButtonRef = useRef<HTMLButtonElement>(null)
  const { data: settings } = useAppSettings()

  const [aiPanelOpen, setAiPanelOpen] = useState<boolean>(() => {
    if (typeof window === 'undefined') return false
    try {
      const stored = window.localStorage?.getItem?.('aiPanelOpen')
      return stored === 'true'
    } catch {
      return false
    }
  })

  const platforms = useMemo(() => getPlatforms(currentActor), [currentActor])
  const homePath = useMemo(() => {
    const mission = platforms.find((platform) => platform.id === 'mission-control')
    return mission?.path ?? platforms[0]?.path ?? '/'
  }, [platforms])
  const routeContext = useIARouteContext()
  const normalizedPath = location.pathname === '/' ? '/' : location.pathname.replace(/\/+$/, '')
  const legacyTarget = legacyRedirects[normalizedPath]

  if (legacyTarget && legacyTarget !== normalizedPath) {
    return (
      <Navigate
        to={{ pathname: legacyTarget, search: location.search, hash: location.hash }}
        replace
      />
    )
  }

  const activePlatform = useMemo(() => {
    if (routeContext.platform) {
      return routeContext.platform
    }
    return platforms[0]
  }, [routeContext.platform, platforms])

  const categories = useMemo(() => {
    if (!activePlatform) return []
    return getCategories(activePlatform.id, currentActor)
  }, [activePlatform, currentActor])

  const activeCategory = useMemo(() => {
    if (routeContext.category) {
      return routeContext.category
    }
    return undefined
  }, [routeContext.category])

  const features = useMemo(() => {
    if (!activePlatform || !activeCategory) return []
    return getFeatures(activePlatform.id, activeCategory.id, currentActor)
  }, [activePlatform, activeCategory, currentActor])

  const isAdmin = authState.status === 'authenticated' && authState.user.is_admin
  const showTenantMenu = isAdmin && currentActor === 'enterprise'
  const showFeatureSidebar = Boolean(
    routeContext.category && (routeContext.isCategoryHome || routeContext.feature),
  )

  const breadcrumbs = useMemo((): Breadcrumb[] => {
    const items: Breadcrumb[] = [{ label: 'Home', path: homePath }]

    if (routeContext.platform) {
      items.push({ label: routeContext.platform.label, path: routeContext.platform.path })
    }
    if (routeContext.category) {
      items.push({ label: routeContext.category.label, path: routeContext.category.homeRoute })
    }
    if (routeContext.feature) {
      items.push({ label: routeContext.feature.label, path: routeContext.feature.route })
    }

    const pmsMatch = location.pathname.match(/^\/pms\/projects\/([^/]+)/)
    if (pmsMatch) {
      const projectId = pmsMatch[1]
      items.push({
        label: `Project ${projectId.slice(0, 6)}`,
        path: `/pms/projects/${projectId}`,
      })
      const params = new URLSearchParams(location.search)
      const tab = params.get('tab')
      if (tab) {
        const tabLabels: Record<string, string> = {
          overview: 'Overview',
          epics: 'Epics',
          tasks: 'Tasks',
          schedule: 'Schedule',
          runs: 'Runs & Artifacts',
          documents: 'Documents',
          journal: 'Journal',
          finance: 'Finance',
          audit: 'Audit',
          settings: 'Settings',
        }
        items.push({ label: tabLabels[tab] ?? tab, path: location.pathname + location.search })
      }
    }

    return items
  }, [
    homePath,
    routeContext.platform,
    routeContext.category,
    routeContext.feature,
    location.pathname,
    location.search,
  ])

  useEffect(() => {
    if (typeof window === 'undefined') return
    try {
      window.localStorage?.setItem?.('aiPanelOpen', aiPanelOpen ? 'true' : 'false')
    } catch {
      // ignore
    }
  }, [aiPanelOpen])

  useEffect(() => {
    const btn = aiButtonRef.current
    if (!btn) return
    const onClick = (event: MouseEvent) => {
      event.preventDefault()
      event.stopPropagation()
      setAiPanelOpen((prev) => !prev)
    }
    btn.addEventListener('click', onClick, true)
    return () => btn.removeEventListener('click', onClick, true)
  }, [])

  useEffect(() => {
    if (settings?.theme) {
      applyTheme(settings.theme)
    } else {
      applyTheme(defaultTheme)
    }
  }, [settings?.theme])

  const toggleDropdown = useCallback((id: string) => {
    setOpenPlatformId((prev) => (prev === id ? null : id))
  }, [])

  const closeDropdown = useCallback(() => {
    setOpenPlatformId(null)
  }, [])

  useEffect(() => {
    setOpenPlatformId(null)
    setMobileMenuOpen(false)
    setMobileSidebarOpen(false)
  }, [location.pathname])

  return (
    <div className="osd-shell min-h-screen text-[color:var(--osd-text)] flex flex-col">
      <nav className="osd-nav border-b border-[color:var(--osd-border)] sticky top-0 z-50 bg-[color:var(--osd-background)]/80 backdrop-blur-md">
        <div className="w-full px-2 sm:px-4 lg:px-6">
          <div className="flex h-16 items-center gap-3">
            <div className="flex items-center gap-3">
              <button
                className="lg:hidden p-2 text-[color:var(--osd-muted)] hover:text-[color:var(--osd-text)]"
                onClick={() => setMobileMenuOpen((v) => !v)}
                aria-label="Toggle platform menu"
              >
                {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
              </button>

              {showFeatureSidebar && (
                <button
                  className="lg:hidden p-2 text-[color:var(--osd-muted)] hover:text-[color:var(--osd-text)]"
                  onClick={() => setMobileSidebarOpen((v) => !v)}
                  aria-label="Toggle feature drawer"
                >
                  <PanelLeft className="w-5 h-5" />
                </button>
              )}

                  <Link to={homePath} className="flex items-center gap-3">
                <div className="osd-logo w-8 h-8 bg-gradient-to-br from-[color:var(--osd-accent)] to-[color:var(--osd-accentPurple)] rounded-lg shadow-lg" />
                <div className="hidden sm:block">
                  <p className="text-[0.6rem] uppercase tracking-[0.2em] text-[color:var(--osd-muted)] leading-none mb-1">
                    Canonical Control Room
                  </p>
                  <h1 className="text-sm font-semibold tracking-wide">OS Dashboard · AI Assistant</h1>
                </div>
              </Link>

              <div className="flex">
                <ActorSwitch compact />
              </div>

              <div className="hidden lg:flex items-center space-x-1">
                {platforms.map((platform) => {
                  const platformCategories = getCategories(platform.id, currentActor)
                  return (
                    <PlatformDropdown
                      key={platform.id}
                      platform={platform}
                      categories={platformCategories}
                      open={openPlatformId === platform.id}
                      isActive={routeContext.platform?.id === platform.id}
                      onOpen={() => toggleDropdown(platform.id)}
                      onClose={closeDropdown}
                    />
                  )
                })}
              </div>
            </div>

            <div className="hidden lg:flex flex-1 justify-center px-4">
              <GlobalSearch />
            </div>

            <div className="flex items-center gap-2 ml-auto">
              <Link
                to="/activity"
                className="p-2 text-[color:var(--osd-muted)] hover:text-[color:var(--osd-text)] transition-colors"
                aria-label="Notifications and activity"
              >
                <Bell className="w-5 h-5" />
              </Link>
              <Link
                to="/docs"
                className="p-2 text-[color:var(--osd-muted)] hover:text-[color:var(--osd-text)] transition-colors"
                aria-label="Help and documentation"
              >
                <HelpCircle className="w-5 h-5" />
              </Link>
              {showTenantMenu ? <TenantMenu /> : null}
              <UserMenu />
            </div>
          </div>
        </div>

        <div className="lg:hidden pb-3 px-2 sm:px-4">
          <div className="flex justify-center">
            <GlobalSearch />
          </div>
        </div>

        {mobileMenuOpen && (
          <div className="lg:hidden border-t border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]">
            <div className="px-4 py-4 space-y-4 max-h-[70vh] overflow-y-auto">
              <div className="flex items-center justify-between">
                <ActorSwitch />
              </div>
              {platforms.map((platform) => (
                <div key={platform.id} className="space-y-1">
                  <p className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)] font-semibold px-3 py-2">
                    {platform.label}
                  </p>
                  {getCategories(platform.id, currentActor).map((category) => (
                    <Link
                      key={category.id}
                      to={category.homeRoute}
                      className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm hover:bg-[color:var(--osd-accentSoft)]"
                      onClick={() => setMobileMenuOpen(false)}
                    >
                      <Sparkles className="w-4 h-4" />
                      {category.label}
                    </Link>
                  ))}
                </div>
              ))}
            </div>
          </div>
        )}

        {mobileSidebarOpen && showFeatureSidebar && activeCategory && (
          <div className="lg:hidden fixed inset-0 z-[9998]">
            <button
              type="button"
              className="absolute inset-0 bg-black/40"
              onClick={() => setMobileSidebarOpen(false)}
              aria-label="Close feature drawer"
            />
            <div className="absolute left-0 top-0 h-full w-72 bg-[color:var(--osd-surface)] border-r border-[color:var(--osd-border)] shadow-xl">
              <div className="flex items-center justify-between px-4 py-4 border-b border-[color:var(--osd-border)]">
                <div>
                  <p className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)]">Category</p>
                  <p className="text-sm font-semibold text-[color:var(--osd-text)]">{activeCategory.label}</p>
                </div>
                <button
                  type="button"
                  className="text-[color:var(--osd-muted)] hover:text-[color:var(--osd-text)]"
                  onClick={() => setMobileSidebarOpen(false)}
                  aria-label="Close drawer"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
              <nav className="px-3 py-3 space-y-1 overflow-y-auto h-[calc(100%-4.5rem)]">
                {features.map((item) => {
                  const isActive = location.pathname === item.route || location.pathname.startsWith(item.route + '/')
                  return (
                    <Link
                      key={item.route}
                      to={item.route}
                      onClick={() => setMobileSidebarOpen(false)}
                      className={`flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                        isActive
                          ? 'bg-[color:var(--osd-accentSoft)] text-[color:var(--osd-text)] border border-[color:var(--osd-accent)]/20'
                          : 'text-[color:var(--osd-muted)] hover:text-[color:var(--osd-text)] hover:bg-[color:var(--osd-surface)]'
                      }`}
                    >
                      <Sparkles className={`w-4 h-4 shrink-0 ${isActive ? 'text-[color:var(--osd-accent)]' : ''}`} />
                      <span className="truncate">{item.label}</span>
                    </Link>
                  )
                })}
              </nav>
            </div>
          </div>
        )}
      </nav>

      <main className="glass-content page-container w-full py-6 sm:py-8 px-3 sm:px-5 lg:px-8 min-h-[calc(100vh-8rem)] flex-1">
        <div className="mb-6 flex flex-col gap-4">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <nav className="flex flex-wrap items-center gap-2 text-xs text-[color:var(--osd-muted)]">
              {breadcrumbs.map((crumb, idx) => (
                <div key={`${crumb.path}-${idx}`} className="flex items-center gap-2">
                  <Link to={crumb.path} className="hover:text-[color:var(--osd-text)]">
                    {crumb.label}
                  </Link>
                  {idx < breadcrumbs.length - 1 && <span className="text-[color:var(--osd-border)]">/</span>}
                </div>
              ))}
            </nav>
          </div>
        </div>

        <div className="flex w-full gap-6">
          {showFeatureSidebar && activeCategory && features.length > 0 && (
            <FeatureSidebar
              category={activeCategory}
              features={features}
              currentPath={location.pathname}
            />
          )}

          <div className="flex-1 min-w-0 w-full">{children ?? <Outlet />}</div>
        </div>
      </main>

      <UnifiedAIPanel currentPath={location.pathname} open={aiPanelOpen} onToggle={setAiPanelOpen} />

      <button
        ref={aiButtonRef}
        type="button"
        id="ai-assistant-toggle-button"
        className={`fixed bottom-6 right-6 flex items-center gap-2.5 rounded-full px-5 py-3 shadow-2xl cursor-pointer transition-all duration-300 z-[9999] backdrop-blur-md ${
          aiPanelOpen
            ? 'bg-[color:var(--osd-surface)]/90 text-[color:var(--osd-text)] hover:bg-[color:var(--osd-surface)] border border-[color:var(--osd-border)]'
            : 'bg-gradient-to-r from-[color:var(--osd-accent)] to-[color:var(--osd-accentPurple)] text-white hover:opacity-95 border border-[color:var(--osd-accent)]/30'
        }`}
        style={{ right: aiPanelOpen ? '400px' : '24px' }}
        aria-pressed={aiPanelOpen}
      >
        <span className="font-medium text-sm whitespace-nowrap">
          {aiPanelOpen ? 'Hide Assistant' : 'AI Assistant'}
        </span>
      </button>
    </div>
  )
}
