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
import { navigationConfig, Category, Platform, FeatureOption } from '../config/navigation'

interface LayoutProps {
  children: ReactNode
}

interface NavDropdownProps {
  category: Category
  platforms: Platform[]
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

    return () => {
      document.removeEventListener('click', handleClickOutside, true)
      document.removeEventListener('keydown', handleEscape, true)
    }
  }, [expanded, onClose])

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
          {/* <Icon className="w-5 h-5 mr-2" /> */}
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
  )
}

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set())
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
