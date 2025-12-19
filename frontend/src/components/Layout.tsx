import { ReactNode, useEffect, useState, useRef, useCallback, useMemo } from 'react'
import { createPortal } from 'react-dom'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard,
  ChevronDown,
  Sparkles,
  ChevronRight,
  Menu,
  X,
  LogOut,
  User,
  Settings,
  Shield,
} from 'lucide-react'
import { applyTheme, defaultTheme } from '../theme'
import { useAppSettings } from '../hooks/useSettings'
import { UnifiedAIPanel } from './UnifiedAIPanel'
import { throttle } from '../shared/utils'
import { navigationManifest, getAllPagesFromCategory, type NavCategory, type NavPage } from '../data/navigationManifest'

interface LayoutProps {
  children: ReactNode
}

interface NavDropdownProps {
  category: NavCategory
  active: boolean
  expanded: boolean
  onToggle: () => void
  onClose: () => void
  location: { pathname: string }
}

function NavDropdown({ category, active, expanded, onToggle, onClose, location }: NavDropdownProps) {
  const buttonRef = useRef<HTMLButtonElement>(null)
  const dropdownRef = useRef<HTMLDivElement>(null)
  const isTogglingRef = useRef(false)
  const Icon = category.icon

  // Position dropdown when expanded
  useEffect(() => {
    if (expanded && buttonRef.current && dropdownRef.current) {
      const buttonRect = buttonRef.current.getBoundingClientRect()
      const viewportWidth = window.innerWidth
      const dropdownWidth = 288

      let left = buttonRect.left
      if (left + dropdownWidth > viewportWidth) {
        left = viewportWidth - dropdownWidth - 16
      }
      if (left < 16) left = 16

      dropdownRef.current.style.top = `${buttonRect.bottom + 8}px`
      dropdownRef.current.style.left = `${left}px`
    }
  }, [expanded])

  const handleButtonClick = useCallback((e: React.MouseEvent) => {
    e.stopPropagation()
    e.preventDefault()

    // Set flag to prevent click outside handler from firing immediately
    isTogglingRef.current = true

    // Toggle the dropdown
    onToggle()

    // Reset flag after a brief delay
    requestAnimationFrame(() => {
      setTimeout(() => {
        isTogglingRef.current = false
      }, 100)
    })
  }, [onToggle])

  // Handle click outside to close dropdown
  useEffect(() => {
    if (!expanded) {
      isTogglingRef.current = false
      return
    }

    const handleClickOutside = (event: MouseEvent) => {
      // Ignore if we're currently toggling
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
      onClose()
    }

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onClose()
      }
    }

    // Add small delay to ensure button click handler runs first
    const timeoutId = setTimeout(() => {
      document.addEventListener('click', handleClickOutside, true)
      document.addEventListener('keydown', handleEscape, true)
    }, 10)

    return () => {
      clearTimeout(timeoutId)
      document.removeEventListener('click', handleClickOutside, true)
      document.removeEventListener('keydown', handleEscape, true)
    }
  }, [expanded, onClose])

  return (
    <>
      <div className="relative group flex items-center">
        <button
          ref={buttonRef}
          type="button"
          onClick={handleButtonClick}
          onMouseDown={(e) => e.stopPropagation()}
          className={`osd-nav-link ${active ? 'osd-nav-link--active' : ''}`}
          style={{ pointerEvents: 'auto', cursor: 'pointer' }}
          aria-haspopup="menu"
          aria-expanded={expanded}
        >
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
            className="osd-dropdown w-72 max-h-[70vh] overflow-y-auto"
            style={{ position: 'fixed', zIndex: 99999, pointerEvents: 'auto' }}
            onClick={(e) => e.stopPropagation()}
            onMouseDown={(e) => e.stopPropagation()}
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
                        onClick={() => onClose()}
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
            ))}
          </div>,
          document.body
        )}
    </>
  )
}

interface SidebarProps {
  category: NavCategory
  currentPath: string
}

// Feature Sidebar - Shows features for the current category (distinct from dropdown categories)
function FeatureSidebar({ category, currentPath }: SidebarProps) {
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

// User menu component
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

  const isAdmin = user?.role === 'admin'
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
        {isAdmin && (
          <Shield className="w-4 h-4 text-amber-400" />
        )}
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

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()
  // Single-open dropdown model for top nav
  const [openDropdownPath, setOpenDropdownPath] = useState<string | null>(null)
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

  // Toggle dropdown - only one open at a time
  const toggleDropdown = useCallback((path: string) => {
    setOpenDropdownPath((prev) => (prev === path ? null : path))
  }, [])

  // Close dropdown
  const closeDropdown = useCallback(() => {
    setOpenDropdownPath(null)
  }, [])

  // Close dropdown on navigation
  useEffect(() => {
    setOpenDropdownPath(null)
    setMobileMenuOpen(false)
  }, [location.pathname])

  // Find active category based on current path
  const activeCategory = useMemo(() => {
    for (const category of navigationManifest) {
      if (location.pathname === category.path) return category
      const allPages = getAllPagesFromCategory(category)
      if (allPages.some((page) => location.pathname === page.path || location.pathname.startsWith(page.path + '/'))) {
        return category
      }
    }
    return navigationManifest[0]
  }, [location.pathname])

  // Check if a category is active
  const isCategoryActive = (category: NavCategory): boolean => {
    if (location.pathname === category.path) return true
    const allPages = getAllPagesFromCategory(category)
    return allPages.some((page) => location.pathname === page.path || location.pathname.startsWith(page.path + '/'))
  }

  return (
    <div className="osd-shell min-h-screen text-[color:var(--osd-text)] flex flex-col">
      {/* Top Navigation Bar */}
      <nav className="osd-nav border-b border-[color:var(--osd-border)] sticky top-0 z-50 bg-[color:var(--osd-background)]/95 backdrop-blur-md">
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

              <Link to="/" className="flex items-center gap-3">
                <div className="osd-logo w-8 h-8 bg-gradient-to-br from-[color:var(--osd-accent)] to-[color:var(--osd-accentPurple)] rounded-lg shadow-lg" />
                <div className="hidden sm:block">
                  <p className="text-[0.6rem] uppercase tracking-[0.2em] text-[color:var(--osd-muted)] leading-none mb-1">
                    Canonical Control Room
                  </p>
                  <h1 className="text-sm font-semibold tracking-wide">OS Dashboard · AI Assistant</h1>
                </div>
              </Link>
            </div>

            {/* Desktop Navigation - Platform Level Dropdowns */}
            <div className="hidden lg:flex items-center space-x-1 flex-1 justify-center">
              {navigationManifest.map((category) => {
                const active = isCategoryActive(category)
                const expanded = openDropdownPath === category.path
                const allPages = getAllPagesFromCategory(category)

                if (allPages.length > 0) {
                  return (
                    <NavDropdown
                      key={category.path}
                      category={category}
                      active={active}
                      expanded={expanded}
                      onToggle={() => toggleDropdown(category.path)}
                      onClose={closeDropdown}
                      location={location}
                    />
                  )
                }

                return (
                  <Link
                    key={category.path}
                    to={category.path}
                    className={`osd-nav-link ${active ? 'osd-nav-link--active' : ''}`}
                  >
                    <category.icon className="w-5 h-5 mr-2" />
                    {category.label}
                  </Link>
                )
              })}
            </div>

            {/* Right Actions */}
            <div className="flex items-center gap-2">
              <UserMenu />
            </div>
          </div>
        </div>

        {/* Breadcrumbs */}
        {location.pathname !== '/' && (
          <div className="px-4 py-2 border-t border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]/30 backdrop-blur-sm flex items-center text-xs">
            <Link to="/" className="hover:text-[color:var(--osd-accent)] transition-colors flex items-center gap-1">
              <LayoutDashboard className="w-3.5 h-3.5" />
              Dashboard
            </Link>
            {activeCategory && (
              <>
                <ChevronRight className="w-3 h-3 mx-2 text-[color:var(--osd-muted)]" />
                <span className="font-semibold text-[color:var(--osd-text)]">
                  {activeCategory.label}
                </span>
              </>
            )}
            {/* Current page from path */}
            {location.pathname.split('/').filter(Boolean).length > 1 && (
              <>
                <ChevronRight className="w-3 h-3 mx-2 text-[color:var(--osd-muted)]" />
                <span className="text-[color:var(--osd-muted)]">
                  {location.pathname
                    .split('/')
                    .filter(Boolean)
                    .pop()
                    ?.split('-')
                    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
                    .join(' ')}
                </span>
              </>
            )}
          </div>
        )}

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="lg:hidden border-t border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]">
            <div className="px-4 py-4 space-y-2 max-h-[70vh] overflow-y-auto">
              {navigationManifest.map((category) => {
                const allPages = getAllPagesFromCategory(category)
                return (
                  <div key={category.path} className="space-y-1">
                    <p className="text-xs uppercase tracking-wider text-[color:var(--osd-muted)] font-semibold px-3 py-2">
                      {category.label}
                    </p>
                    {allPages.slice(0, 5).map((page) => (
                      <Link
                        key={page.path}
                        to={page.path}
                        className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm hover:bg-[color:var(--osd-accentSoft)]"
                        onClick={() => setMobileMenuOpen(false)}
                      >
                        <page.icon className="w-4 h-4" />
                        {page.label}
                      </Link>
                    ))}
                  </div>
                )
              })}
            </div>
          </div>
        )}
      </nav>

      {/* Main Content with Left Sidebar */}
      <main className="glass-content page-container w-full py-6 sm:py-8 px-3 sm:px-5 lg:px-8 min-h-[calc(100vh-8rem)] flex-1">
        <div className="flex w-full gap-6">
          {/* Left Sidebar Navigation - Shows features for active category */}
          {activeCategory && getAllPagesFromCategory(activeCategory).length > 0 && (
            <FeatureSidebar category={activeCategory} currentPath={location.pathname} />
          )}

          {/* Main Content Pane */}
          <div className="flex-1 min-w-0 w-full">{children}</div>
        </div>
      </main>

      {/* AI Assistant Panel */}
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
