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
import { navigationManifest, findCategoryByPath, getAllPagesFromCategory, type NavCategory } from '../data/navigationManifest'

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

  const updatePosition = useCallback(() => {
    if (!buttonRef.current || !dropdownRef.current || !expanded) return
    
    const buttonRect = buttonRef.current.getBoundingClientRect()
    const viewportWidth = window.innerWidth
    const viewportHeight = window.innerHeight
    const dropdownWidth = 288
    
    let left = buttonRect.left
    if (left + dropdownWidth > viewportWidth) {
      left = viewportWidth - dropdownWidth - 16
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
  }, [expanded])

  const throttledUpdatePosition = useMemo(
    () => throttle(() => requestAnimationFrame(updatePosition), 16),
    [updatePosition]
  )

  useEffect(() => {
    if (!expanded) {
      if (dropdownRef.current) {
        dropdownRef.current.style.top = ''
        dropdownRef.current.style.left = ''
      }
      isTogglingRef.current = false
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

  const handleButtonClick = useCallback((e: React.MouseEvent) => {
    e.stopPropagation()
    e.preventDefault()
    
    isTogglingRef.current = true
    
    if (expanded) {
      onClose()
    } else {
      onToggle()
    }
    
    requestAnimationFrame(() => {
      setTimeout(() => {
        isTogglingRef.current = false
      }, 100)
    })
  }, [expanded, onToggle, onClose])

  const handleLinkClick = useCallback(() => {
    onClose()
  }, [onClose])

  useEffect(() => {
    if (!expanded) return

    const handleClickOutside = (event: MouseEvent) => {
      if (isTogglingRef.current) return

      const target = event.target as Node
      
      if (
        !buttonRef.current ||
        !dropdownRef.current ||
        buttonRef.current.contains(target) ||
        dropdownRef.current.contains(target)
      ) {
        return
      }
      
      onClose()
    }

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onClose()
      }
    }

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
            className="osd-dropdown w-72" 
            style={{ 
              position: 'fixed', 
              zIndex: 99999, 
              pointerEvents: 'auto' 
            }}
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
                        onClick={handleLinkClick}
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

function Sidebar({ category, currentPath }: SidebarProps) {
  const allPages = getAllPagesFromCategory(category)
  if (allPages.length === 0) return null

  // Get all features/flows/simulations/etc from the category groups
  // This is the left sidebar showing features, not categories
  const allFeatures = category.groups.flatMap(group => group.items)

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

        {/* Features List - This is what should be in the sidebar */}
        <div className="bg-[color:var(--osd-surface)]/80 backdrop-blur-md rounded-xl shadow-sm border border-[color:var(--osd-border)]">
          <div className="px-4 pt-3 pb-2">
            <h3 className="text-xs font-bold uppercase tracking-wider text-[color:var(--osd-muted)] mb-2">
              Features & Tools
            </h3>
          </div>
          <nav className="px-2 pb-2">
            <div className="space-y-1">
              {allFeatures.map((item) => {
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
      </div>
    </aside>
  )
}

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()
  const [openCategoryPath, setOpenCategoryPath] = useState<string | null>(null)
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

  const toggleCategory = useCallback((categoryPath: string) => {
    setOpenCategoryPath((prev) => (prev === categoryPath ? null : categoryPath))
  }, [])

  const closeCategory = useCallback((categoryPath: string) => {
    setOpenCategoryPath((prev) => (prev === categoryPath ? null : prev))
  }, [])

  useEffect(() => {
    // Close dropdown when navigation occurs
    setOpenCategoryPath(null)
  }, [location.pathname])

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

  // Check if category is expanded
  const isCategoryExpanded = (category: NavCategory): boolean => {
    return openCategoryPath === category.path
  }

  return (
    <div className="osd-shell min-h-screen text-[color:var(--osd-text)] flex flex-col">
      {/* Top Navigation Bar */}
      <nav className="osd-nav border-b border-[color:var(--osd-border)] sticky top-0 z-50 bg-[color:var(--osd-background)]/80 backdrop-blur-md">
        <div className="w-full px-2 sm:px-4 lg:px-6" style={{ overflow: 'visible' }}>
          <div className="flex flex-col w-full" style={{ overflow: 'visible' }}>
            {/* Primary Navigation */}
            <div className="flex h-16" style={{ overflow: 'visible', position: 'relative', zIndex: 1 }}>
              <div className="flex-shrink-0 flex items-center gap-3" style={{ position: 'relative', zIndex: 1 }}>
                <button 
                  className="lg:hidden p-2 text-[color:var(--osd-muted)] hover:text-[color:var(--osd-text)]"
                  onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                >
                  {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
                </button>
                <div className="osd-logo w-8 h-8 bg-gradient-to-br from-[color:var(--osd-accent)] to-[color:var(--osd-accentPurple)] rounded-lg shadow-lg" />
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
                        onToggle={() => toggleCategory(category.path)}
                        onClose={() => closeCategory(category.path)}
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
              {/* Right Actions */}
              <div className="flex items-center gap-2">
                <Link to="/settings" className="p-2 text-[color:var(--osd-muted)] hover:text-[color:var(--osd-text)] transition-colors">
                  <LayoutDashboard className="w-5 h-5" />
                </Link>
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content with Left Sidebar */}
      <main className="glass-content page-container w-full py-6 sm:py-8 px-3 sm:px-5 lg:px-8 min-h-[calc(100vh-8rem)]">
        <div className="flex w-full gap-6">
          {/* Left Sidebar Navigation - Shows features for active category */}
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
