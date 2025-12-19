import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { createPortal } from 'react-dom'
import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom'
import { ChevronDown, Menu, Settings, X } from 'lucide-react'
import { UnifiedAIPanel } from './UnifiedAIPanel'
import PlatformFeatureSidebar from './PlatformFeatureSidebar'
import { navigationManifest, type NavCategory, type NavGroup, type NavPage } from '../data/navigationManifest'

type ActiveNav = {
  platform: NavCategory | null
  group: NavGroup | null
  page: NavPage | null
}

function matchPage(currentPath: string, pagePath: string): boolean {
  return currentPath === pagePath || currentPath.startsWith(pagePath + '/')
}

function getActiveNav(pathname: string): ActiveNav {
  const platform =
    navigationManifest.find((p) => pathname.startsWith(p.path)) ??
    // Dashboard is special: root routes live under Mission Control.
    navigationManifest.find((p) => p.path === '/dashboard') ??
    null

  if (!platform) return { platform: null, group: null, page: null }

  let group: NavGroup | null = null
  let page: NavPage | null = null

  for (const g of platform.groups) {
    const found = g.items.find((item) => matchPage(pathname, item.path))
    if (found) {
      group = g
      page = found
      break
    }
  }

  if (!group && platform.groups.length > 0) {
    group = platform.groups[0]
  }

  return { platform, group, page }
}

function useDropdownPosition(
  open: boolean,
  buttonRef: React.RefObject<HTMLButtonElement>,
  dropdownRef: React.RefObject<HTMLDivElement>
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
  open,
  onOpen,
  onClose,
}: {
  platform: NavCategory
  open: boolean
  onOpen: () => void
  onClose: () => void
}) {
  const location = useLocation()
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

    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }

    document.addEventListener('click', onDocClick, true)
    document.addEventListener('keydown', onKeyDown, true)
    return () => {
      document.removeEventListener('click', onDocClick, true)
      document.removeEventListener('keydown', onKeyDown, true)
    }
  }, [open, onClose])

  const isActive = useMemo(() => {
    if (platform.path === '/dashboard') {
      return (
        location.pathname === '/' ||
        location.pathname === '/dashboard' ||
        location.pathname.startsWith('/tasks') ||
        location.pathname.startsWith('/projects') ||
        location.pathname.startsWith('/chat') ||
        location.pathname.startsWith('/collaboration') ||
        location.pathname.startsWith('/personalization') ||
        location.pathname.startsWith('/search')
      )
    }
    return location.pathname.startsWith(platform.path)
  }, [location.pathname, platform.path])

  const handleCategorySelect = (group: NavGroup) => {
    const target = group.items[0]?.path ?? (platform.path === '/dashboard' ? '/' : platform.path)
    onClose()
    navigate(target)
  }

  return (
    <>
      <button
        ref={buttonRef}
        type="button"
        className={`osd-nav-link ${isActive ? 'osd-nav-link--active' : ''}`}
        aria-haspopup="menu"
        aria-expanded={open}
        onClick={(e) => {
          e.preventDefault()
          e.stopPropagation()
          if (open) onClose()
          else onOpen()
        }}
        onMouseDown={(e) => e.stopPropagation()}
      >
        <platform.icon className="w-5 h-5 mr-2" />
        <span className="whitespace-nowrap">{platform.label}</span>
        <ChevronDown className={`w-4 h-4 ml-1 transition-transform ${open ? 'rotate-180' : ''}`} />
      </button>

      {open
        ? createPortal(
            <div
              ref={dropdownRef}
              className="osd-dropdown w-80"
              style={{ position: 'fixed', zIndex: 99999, pointerEvents: 'auto' }}
              onClick={(e) => e.stopPropagation()}
              onMouseDown={(e) => e.stopPropagation()}
              role="menu"
            >
              <div className="px-4 py-3 border-b border-white/5">
                <p className="text-[0.65rem] uppercase tracking-[0.35em] text-[color:var(--osd-muted)]">
                  Categories
                </p>
                <p className="mt-1 text-sm font-semibold text-[color:var(--osd-text)]">{platform.label}</p>
                <p className="mt-1 text-xs text-[color:var(--osd-muted)]">{platform.description}</p>
              </div>
              <div className="py-2">
                {platform.groups.map((group) => (
                  <button
                    key={group.label}
                    type="button"
                    className="w-full text-left px-4 py-2 hover:bg-[color:var(--osd-surface)] transition-colors"
                    onClick={() => handleCategorySelect(group)}
                  >
                    <div className="text-sm font-medium text-[color:var(--osd-text)]">{group.label}</div>
                    {group.description ? (
                      <div className="text-xs text-[color:var(--osd-muted)] mt-0.5">{group.description}</div>
                    ) : null}
                  </button>
                ))}
              </div>
            </div>,
            document.body
          )
        : null}
    </>
  )
}

function FeatureRail({
  platform,
  group,
  currentPath,
}: {
  platform: NavCategory
  group: NavGroup
  currentPath: string
}) {
  return (
    <aside className="hidden lg:block w-72 shrink-0 border-r border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]/20 overflow-y-auto">
      <div className="p-4">
        <div className="mb-4 pb-3 border-b border-[color:var(--osd-border)]">
          <div className="flex items-center gap-2">
            <platform.icon className="w-5 h-5 text-[color:var(--osd-accent)]" />
            <h2 className="font-semibold text-[color:var(--osd-text)]">{platform.label}</h2>
          </div>
          <p className="mt-2 text-xs uppercase tracking-[0.25em] text-[color:var(--osd-muted)]">Category</p>
          <p className="mt-1 text-sm font-semibold text-[color:var(--osd-text)]">{group.label}</p>
          {group.description ? <p className="mt-1 text-xs text-[color:var(--osd-muted)]">{group.description}</p> : null}
        </div>

        <nav className="space-y-1">
          {group.items.map((item) => {
            const active = matchPage(currentPath, item.path)
            const ItemIcon = item.icon
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                  active
                    ? 'bg-[color:var(--osd-accentSoft)] text-[color:var(--osd-text)] border border-[color:var(--osd-accent)]/20 shadow-sm'
                    : 'text-[color:var(--osd-muted)] hover:text-[color:var(--osd-text)] hover:bg-[color:var(--osd-surface)]'
                }`}
                aria-current={active ? 'page' : undefined}
              >
                <ItemIcon className={`w-4 h-4 shrink-0 ${active ? 'text-[color:var(--osd-accent)]' : ''}`} />
                <span className="truncate flex-1">{item.label}</span>
                {item.status === 'new' ? (
                  <span className="text-[0.6rem] px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-400 shrink-0">
                    NEW
                  </span>
                ) : null}
              </Link>
            )
          })}
        </nav>
      </div>
    </aside>
  )
}

export default function Layout() {
  const location = useLocation()
  const [openPlatformPath, setOpenPlatformPath] = useState<string | null>(null)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const aiButtonRef = useRef<HTMLButtonElement>(null)
  const [aiPanelOpen, setAiPanelOpen] = useState<boolean>(() => {
    if (typeof window === 'undefined') return false
    try {
      return window.localStorage?.getItem?.('aiPanelOpen') === 'true'
    } catch {
      return false
    }
  })

  const active = useMemo(() => getActiveNav(location.pathname), [location.pathname])

  useEffect(() => {
    // Close any open platform dropdown on route change.
    setOpenPlatformPath(null)
  }, [location.pathname])

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
    const onClick = (e: MouseEvent) => {
      e.preventDefault()
      e.stopPropagation()
      setAiPanelOpen((prev) => !prev)
    }
    btn.addEventListener('click', onClick, true)
    return () => btn.removeEventListener('click', onClick, true)
  }, [])

  const currentPlatform = active.platform
  const currentGroup = active.group

  return (
    <div className="osd-shell min-h-screen text-[color:var(--osd-text)] flex flex-col">
      <nav className="osd-nav border-b border-[color:var(--osd-border)] sticky top-0 z-50 bg-[color:var(--osd-background)]/80 backdrop-blur-md">
        <div className="w-full px-2 sm:px-4 lg:px-6">
          <div className="flex justify-between h-16 items-center">
            <div className="flex items-center gap-4">
              <button
                className="lg:hidden p-2 text-[color:var(--osd-muted)] hover:text-[color:var(--osd-text)]"
                onClick={() => setMobileMenuOpen((v) => !v)}
                aria-label="Toggle menu"
              >
                {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
              </button>

              <div className="flex items-center gap-3">
                <div className="osd-logo w-8 h-8 bg-gradient-to-br from-[color:var(--osd-accent)] to-[color:var(--osd-accentPurple)] rounded-lg shadow-lg" />
                <div className="hidden sm:block">
                  <p className="text-[0.6rem] uppercase tracking-[0.2em] text-[color:var(--osd-muted)] leading-none mb-1">
                    Canonical Control Room
                  </p>
                  <h1 className="text-sm font-semibold tracking-wide">OS DASHBOARD · AI Assistant</h1>
                </div>
              </div>
            </div>

            <div className="hidden lg:flex items-center space-x-1 overflow-x-auto overflow-y-visible">
              {navigationManifest.map((platform) => (
                <PlatformDropdown
                  key={platform.path}
                  platform={platform}
                  open={openPlatformPath === platform.path}
                  onOpen={() => setOpenPlatformPath(platform.path)}
                  onClose={() => setOpenPlatformPath((prev) => (prev === platform.path ? null : prev))}
                />
              ))}
            </div>

            <div className="flex items-center gap-2">
              <Link
                to="/settings"
                className="p-2 text-[color:var(--osd-muted)] hover:text-[color:var(--osd-text)] transition-colors"
                aria-label="Settings"
              >
                <Settings className="w-5 h-5" />
              </Link>
            </div>
          </div>

          {mobileMenuOpen ? (
            <div className="lg:hidden pb-3">
              <div className="flex flex-wrap gap-2">
                {navigationManifest.map((platform) => (
                  <Link
                    key={platform.path}
                    to={platform.path === '/dashboard' ? '/' : platform.path}
                    className="px-3 py-2 rounded-lg bg-[color:var(--osd-surface)]/60 border border-[color:var(--osd-border)] text-sm"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    {platform.label}
                  </Link>
                ))}
              </div>
            </div>
          ) : null}
        </div>
      </nav>

      <div className="flex flex-1 min-h-0 relative">
        {currentPlatform && currentGroup ? (
          <FeatureRail platform={currentPlatform} group={currentGroup} currentPath={location.pathname} />
        ) : null}

        <main className="flex-1 min-w-0 overflow-y-auto py-6 px-4 sm:px-6 lg:px-8 glass-content">
          <div className="max-w-7xl mx-auto">
            <Outlet />
          </div>
        </main>

        {/* Per-page anchor sidebar (not redundant with platform/category nav) */}
        <PlatformFeatureSidebar />
      </div>

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
        <span className="font-medium text-sm whitespace-nowrap">{aiPanelOpen ? 'Hide Assistant' : 'AI Assistant'}</span>
      </button>
    </div>
  )
}
