#!/usr/bin/env python3
"""
Comprehensive GUI Restoration Script
Restores all navigation elements, pages, and components from best commits
"""

import os
import subprocess
import json
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict

# Commits to analyze (most recent with best page versions)
COMMITS_TO_ANALYZE = [
    "0922b926",  # Restore comprehensive GUI structure
    "4816a3a9",  # Add missing page components
    "37000f79",  # Enforce hierarchy and restore pages
    "3a154a6e",  # Latest stable alpha version
    "58cfc34",   # In style
    "4acea80",   # Backup before emergency restore
]

BASE_DIR = Path(__file__).parent.parent
FRONTEND_PAGES = BASE_DIR / "frontend/src/pages"
IA_MANIFEST = BASE_DIR / "frontend/src/data/iaManifest.ts"

@dataclass
class PageInfo:
    """Information about a page file"""
    path: str
    commit: str
    size: int
    has_components: bool
    has_elements: bool
    score: int = 0

def run_git_command(cmd: List[str], cwd: str = None) -> Tuple[str, int]:
    """Run a git command and return output"""
    try:
        result = subprocess.run(
            ["git"] + cmd,
            cwd=cwd or str(BASE_DIR),
            capture_output=True,
            text=True,
            check=False
        )
        return result.stdout.strip(), result.returncode
    except Exception as e:
        print(f"Error running git command: {e}")
        return "", 1

def list_pages_in_commit(commit: str) -> Set[str]:
    """List all page files in a commit"""
    output, code = run_git_command(["ls-tree", "-r", "--name-only", commit, "--", "frontend/src/pages"])
    if code != 0:
        return set()
    
    pages = set()
    for line in output.split("\n"):
        if line and (line.endswith(".tsx") or line.endswith(".ts") or line.endswith(".jsx") or line.endswith(".js")):
            pages.add(line)
    return pages

def analyze_page_content(commit: str, page_path: str) -> PageInfo:
    """Analyze page content to determine quality"""
    output, code = run_git_command(["show", f"{commit}:{page_path}"])
    if code != 0:
        return PageInfo(path=page_path, commit=commit, size=0, has_components=False, has_elements=False, score=0)
    
    content = output
    size = len(content)
    
    # Check for React components
    has_components = bool(re.search(r'(export\s+(default\s+)?function|const\s+\w+\s*=\s*\(|export\s+const\s+\w+\s*=\s*\()', content))
    
    # Check for UI elements
    has_elements = bool(re.search(r'(<div|<button|<input|<select|<form|className|useState|useEffect)', content))
    
    # Calculate score
    score = 0
    if size > 1000:
        score += 10
    if size > 5000:
        score += 10
    if has_components:
        score += 20
    if has_elements:
        score += 20
    if "import" in content:
        score += 10
    if "export" in content:
        score += 10
    if "return" in content and ("<" in content or "JSX" in content):
        score += 20
    
    return PageInfo(
        path=page_path,
        commit=commit,
        size=size,
        has_components=has_components,
        has_elements=has_elements,
        score=score
    )

def find_best_commit_for_page(page_path: str) -> Optional[Tuple[str, PageInfo]]:
    """Find the best commit version for a page"""
    best_info = None
    best_commit = None
    
    for commit in COMMITS_TO_ANALYZE:
        pages = list_pages_in_commit(commit)
        if page_path in pages:
            info = analyze_page_content(commit, page_path)
            if best_info is None or info.score > best_info.score:
                best_info = info
                best_commit = commit
    
    if best_commit and best_info:
        return (best_commit, best_info)
    return None

def extract_routes_from_ia_manifest() -> Dict[str, List[str]]:
    """Extract all routes from IA manifest"""
    routes = {
        "platforms": [],
        "categories": [],
        "features": []
    }
    
    if not IA_MANIFEST.exists():
        print(f"Warning: IA manifest not found at {IA_MANIFEST}")
        return routes
    
    content = IA_MANIFEST.read_text()
    
    # Extract platform routes
    platform_matches = re.findall(r"id:\s*['\"]([^'\"]+)['\"]", content)
    routes["platforms"] = list(set(platform_matches))
    
    # Extract category routes (homeRoute)
    category_matches = re.findall(r"homeRoute:\s*['\"]([^'\"]+)['\"]", content)
    routes["categories"] = list(set(category_matches))
    
    # Extract feature routes
    feature_matches = re.findall(r"route:\s*['\"]([^'\"]+)['\"]", content)
    routes["features"] = list(set(feature_matches))
    
    return routes

def route_to_file_path(route: str) -> str:
    """Convert route to file path"""
    # Remove leading slash
    route = route.lstrip("/")
    
    # Convert route segments to path
    parts = route.split("/")
    
    # Handle special cases
    if len(parts) == 1:
        # Top level route
        name = parts[0].replace("-", "").title()
        return f"frontend/src/pages/{name}.tsx"
    elif len(parts) == 2:
        # Platform/category or category/feature
        platform = parts[0].replace("-", "").title()
        feature = parts[1].replace("-", "").title()
        return f"frontend/src/pages/{platform}/{feature}.tsx"
    elif len(parts) == 3:
        # Platform/category/feature
        platform = parts[0].replace("-", "").title()
        category = parts[1].replace("-", "").title()
        feature = parts[2].replace("-", "").title()
        return f"frontend/src/pages/{platform}/{category}/{feature}.tsx"
    else:
        # Deep nesting
        platform = parts[0].replace("-", "").title()
        category = parts[1].replace("-", "").title()
        feature = "/".join(parts[2:]).replace("-", "").title()
        return f"frontend/src/pages/{platform}/{category}/{feature}.tsx"

def restore_page_from_commit(commit: str, page_path: str, target_path: Path) -> bool:
    """Restore a page from a specific commit"""
    try:
        # Get file content from commit
        output, code = run_git_command(["show", f"{commit}:{page_path}"])
        if code != 0:
            print(f"  ❌ Could not get content from {commit}:{page_path}")
            return False
        
        # Ensure target directory exists
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write file
        target_path.write_text(output)
        print(f"  ✅ Restored {page_path} from {commit}")
        return True
    except Exception as e:
        print(f"  ❌ Error restoring {page_path}: {e}")
        return False

def create_category_home_page(category_route: str, category_label: str) -> str:
    """Create a category home/dashboard page"""
    route_parts = category_route.strip("/").split("/")
    category_id = route_parts[-1] if route_parts else "category"
    
    # Convert to PascalCase
    category_name = "".join(word.capitalize() for word in category_id.split("-"))
    
    # Use triple quotes and escape braces properly
    template = '''import { useState, useEffect } from 'react'
import { useLocation, Link } from 'react-router-dom'
import { LayoutDashboard, ChevronRight } from 'lucide-react'
import { useCurrentCategory, useCategoryFeatures } from '../navigation/context'

export default function ''' + category_name + '''Home() {
  const location = useLocation()
  const category = useCurrentCategory()
  const features = useCategoryFeatures()

  return (
    <div className="category-home-page min-h-screen bg-[color:var(--osd-background)]">
      {/* Header */}
      <div className="border-b border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]">
        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="flex items-center gap-3 mb-4">
            <LayoutDashboard className="w-8 h-8 text-[color:var(--osd-accent)]" />
            <h1 className="text-3xl font-bold text-[color:var(--osd-text)]">
              ''' + category_label + '''
            </h1>
          </div>
          {category?.description && (
            <p className="text-[color:var(--osd-muted)] text-lg">
              {category.description}
            </p>
          )}
        </div>
      </div>

      {/* Dashboard Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {features.map((feature) => (
            <Link
              key={feature.id}
              to={feature.path}
              className="group p-6 rounded-xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] hover:border-[color:var(--osd-accent)] hover:shadow-lg transition-all"
            >
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-lg font-semibold text-[color:var(--osd-text)] group-hover:text-[color:var(--osd-accent)]">
                  {feature.title}
                </h3>
                <ChevronRight className="w-5 h-5 text-[color:var(--osd-muted)] group-hover:text-[color:var(--osd-accent)]" />
              </div>
              <p className="text-sm text-[color:var(--osd-muted)]">
                Access {feature.title.toLowerCase()} tools and features
              </p>
            </Link>
          ))}
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="p-6 rounded-xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]">
            <div className="text-2xl font-bold text-[color:var(--osd-text)] mb-2">
              {features.length}
            </div>
            <div className="text-sm text-[color:var(--osd-muted)]">
              Available Features
            </div>
          </div>
          <div className="p-6 rounded-xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]">
            <div className="text-2xl font-bold text-[color:var(--osd-text)] mb-2">
              Active
            </div>
            <div className="text-sm text-[color:var(--osd-muted)]">
              System Status
            </div>
          </div>
          <div className="p-6 rounded-xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]">
            <div className="text-2xl font-bold text-[color:var(--osd-text)] mb-2">
              Ready
            </div>
            <div className="text-sm text-[color:var(--osd-muted)]">
              All Systems
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
'''
    return template

def create_feature_page(route: str, feature_name: str, feature_type: str = "general") -> str:
    """Create a feature page with implied functionality"""
    route_parts = route.strip("/").split("/")
    feature_id = route_parts[-1] if route_parts else "feature"
    
    # Convert to PascalCase
    component_name = "".join(word.capitalize() for word in feature_id.split("-"))
    
    # Determine page type based on feature name
    is_calculator = any(word in feature_name.lower() for word in ["calc", "compute", "calculate", "simulate"])
    is_explorer = any(word in feature_name.lower() for word in ["explore", "browse", "view", "search", "query"])
    is_editor = any(word in feature_name.lower() for word in ["edit", "create", "build", "design", "write"])
    is_dashboard = any(word in feature_name.lower() for word in ["dashboard", "overview", "home", "summary"])
    is_config = any(word in feature_name.lower() for word in ["config", "settings", "preferences", "options"])
    
    if is_calculator:
        return create_calculator_page(component_name, feature_name)
    elif is_explorer:
        return create_explorer_page(component_name, feature_name)
    elif is_editor:
        return create_editor_page(component_name, feature_name)
    elif is_dashboard:
        return create_dashboard_page(component_name, feature_name)
    elif is_config:
        return create_config_page(component_name, feature_name)
    else:
        return create_general_page(component_name, feature_name)

def create_calculator_page(name: str, label: str) -> str:
    """Create a calculator/simulation page"""
    return '''import { useState } from 'react'
import { Calculator, Play, Download } from 'lucide-react'

export default function ''' + name + '''() {
  const [inputText, setInputText] = useState("")
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleCalculate = async () => {
    setLoading(true)
    setTimeout(() => {
      let payload: any = inputText.trim()
      if (payload.length === 0) {
        payload = "No input provided"
      } else {
        try {
          payload = JSON.parse(payload)
        } catch {
          // keep raw text
        }
      }
      setResults({
        input: payload,
        status: "ok",
        calculated_at: new Date().toISOString(),
      })
      setLoading(false)
    }, 500)
  }

  return (
    <div className="min-h-screen bg-[color:var(--osd-background)] p-6">
      <div className="max-w-4xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-[color:var(--osd-text)] mb-2">
            ''' + label + '''
          </h1>
          <p className="text-[color:var(--osd-muted)]">
            Calculate and simulate ''' + label.lower() + ''' scenarios
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="p-6 rounded-xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]">
            <h2 className="text-lg font-semibold mb-4 text-[color:var(--osd-text)]">
              Parameters
            </h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-[color:var(--osd-text)] mb-2">
                  Input Parameters
                </label>
                <textarea
                  value={inputText}
                  onChange={(event) => setInputText(event.target.value)}
                  className="w-full p-3 rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-background)] text-[color:var(--osd-text)]"
                  rows={4}
                  placeholder="Enter parameters..."
                />
              </div>
              <button
                onClick={handleCalculate}
                disabled={loading}
                className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-[color:var(--osd-accent)] text-white rounded-lg hover:bg-[color:var(--osd-accent)]/90 disabled:opacity-50"
              >
                <Play className="w-4 h-4" />
                {loading ? "Calculating..." : "Calculate"}
              </button>
            </div>
          </div>

          <div className="p-6 rounded-xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]">
            <h2 className="text-lg font-semibold mb-4 text-[color:var(--osd-text)]">
              Results
            </h2>
            {results ? (
              <div className="space-y-4">
                <pre className="p-4 rounded-lg bg-[color:var(--osd-background)] text-[color:var(--osd-text)]">
                  {JSON.stringify(results, null, 2)}
                </pre>
                <button className="w-full flex items-center justify-center gap-2 px-4 py-3 border border-[color:var(--osd-border)] rounded-lg hover:bg-[color:var(--osd-surface)]">
                  <Download className="w-4 h-4" />
                  Export Results
                </button>
              </div>
            ) : (
              <div className="text-center py-12 text-[color:var(--osd-muted)]">
                <Calculator className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>No results yet. Run a calculation to see results.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
'''

def create_explorer_page(name: str, label: str) -> str:
    """Create an explorer/browser page"""
    return f'''import {{ useState }} from 'react'
import {{ Search, Filter, List, Grid }} from 'lucide-react'

export default function {name}() {{
  const [searchQuery, setSearchQuery] = useState("")
  const [viewMode, setViewMode] = useState<"list" | "grid">("list")

  return (
    <div className="min-h-screen bg-[color:var(--osd-background)] p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-[color:var(--osd-text)] mb-2">
            {label}
          </h1>
          <p className="text-[color:var(--osd-muted)]">
            Explore and browse {label.toLowerCase()} resources
          </p>
        </div>

        <div className="mb-6 flex gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-[color:var(--osd-muted)]" />
            <input
              type="text"
              value={{searchQuery}}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search..."
              className="w-full pl-10 pr-4 py-2 rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] text-[color:var(--osd-text)]"
            />
          </div>
          <button className="px-4 py-2 rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] hover:bg-[color:var(--osd-surface)]/80">
            <Filter className="w-5 h-5 text-[color:var(--osd-muted)]" />
          </button>
          <button
            onClick={{() => setViewMode(viewMode === "list" ? "grid" : "list")}}
            className="px-4 py-2 rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] hover:bg-[color:var(--osd-surface)]/80"
          >
            {{viewMode === "list" ? <Grid className="w-5 h-5" /> : <List className="w-5 h-5" />}}
          </button>
        </div>

        <div className="p-6 rounded-xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]">
          <div className="text-center py-12 text-[color:var(--osd-muted)]">
            <Search className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>Start exploring by entering a search query</p>
          </div>
        </div>
      </div>
    </div>
  )
}}
'''

def create_editor_page(name: str, label: str) -> str:
    """Create an editor/builder page"""
    return f'''import {{ useState }} from 'react'
import {{ Save, Plus, Trash2 }} from 'lucide-react'

export default function {name}() {{
  const [content, setContent] = useState("")

  return (
    <div className="min-h-screen bg-[color:var(--osd-background)] p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-[color:var(--osd-text)] mb-2">
              {label}
            </h1>
            <p className="text-[color:var(--osd-muted)]">
              Create and edit {label.toLowerCase()} content
            </p>
          </div>
          <div className="flex gap-2">
            <button className="px-4 py-2 rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)] hover:bg-[color:var(--osd-surface)]/80 flex items-center gap-2">
              <Plus className="w-4 h-4" />
              New
            </button>
            <button className="px-4 py-2 rounded-lg bg-[color:var(--osd-accent)] text-white hover:bg-[color:var(--osd-accent)]/90 flex items-center gap-2">
              <Save className="w-4 h-4" />
              Save
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <div className="p-6 rounded-xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]">
              <textarea
                value={{content}}
                onChange={(e) => setContent(e.target.value)}
                placeholder="Start editing..."
                className="w-full h-96 p-4 rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-background)] text-[color:var(--osd-text)] font-mono"
              />
            </div>
          </div>
          <div className="space-y-4">
            <div className="p-6 rounded-xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]">
              <h3 className="font-semibold mb-4 text-[color:var(--osd-text)]">Properties</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-[color:var(--osd-text)] mb-2">
                    Name
                  </label>
                  <input
                    type="text"
                    className="w-full p-2 rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-background)] text-[color:var(--osd-text)]"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}}
'''

def create_dashboard_page(name: str, label: str) -> str:
    """Create a dashboard/overview page"""
    return f'''import {{ useState, useEffect }} from 'react'
import {{ BarChart3, TrendingUp, Activity }} from 'lucide-react'

export default function {name}() {{
  const [stats, setStats] = useState({{
    total: 0,
    active: 0,
    pending: 0
  }})

  useEffect(() => {{
    const total = 100
    const active = 75
    const pending = total - active
    setStats({{ total, active, pending }})
  }}, [])

  return (
    <div className="min-h-screen bg-[color:var(--osd-background)] p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-[color:var(--osd-text)] mb-2">
            {label}
          </h1>
          <p className="text-[color:var(--osd-muted)]">
            Overview and insights for {label.toLowerCase()}
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <div className="p-6 rounded-xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-[color:var(--osd-muted)]">Total</span>
              <BarChart3 className="w-5 h-5 text-[color:var(--osd-accent)]" />
            </div>
            <div className="text-3xl font-bold text-[color:var(--osd-text)]">
              {{stats.total}}
            </div>
          </div>
          <div className="p-6 rounded-xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-[color:var(--osd-muted)]">Active</span>
              <Activity className="w-5 h-5 text-[color:var(--osd-accent)]" />
            </div>
            <div className="text-3xl font-bold text-[color:var(--osd-text)]">
              {{stats.active}}
            </div>
          </div>
          <div className="p-6 rounded-xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-[color:var(--osd-muted)]">Pending</span>
              <TrendingUp className="w-5 h-5 text-[color:var(--osd-accent)]" />
            </div>
            <div className="text-3xl font-bold text-[color:var(--osd-text)]">
              {{stats.pending}}
            </div>
          </div>
        </div>

        <div className="p-6 rounded-xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]">
          <h2 className="text-lg font-semibold mb-4 text-[color:var(--osd-text)]">
            Recent Activity
          </h2>
          <div className="text-center py-12 text-[color:var(--osd-muted)]">
            <Activity className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>No recent activity to display</p>
          </div>
        </div>
      </div>
    </div>
  )
}}
'''

def create_config_page(name: str, label: str) -> str:
    """Create a configuration/settings page"""
    return f'''import {{ useState }} from 'react'
import {{ Settings, Save }} from 'lucide-react'

export default function {name}() {{
  const [config, setConfig] = useState({{}})

  return (
    <div className="min-h-screen bg-[color:var(--osd-background)] p-6">
      <div className="max-w-4xl mx-auto">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-[color:var(--osd-text)] mb-2">
              {label}
            </h1>
            <p className="text-[color:var(--osd-muted)]">
              Configure {label.toLowerCase()} settings and preferences
            </p>
          </div>
          <button className="px-4 py-2 rounded-lg bg-[color:var(--osd-accent)] text-white hover:bg-[color:var(--osd-accent)]/90 flex items-center gap-2">
            <Save className="w-4 h-4" />
            Save Changes
          </button>
        </div>

        <div className="space-y-6">
          <div className="p-6 rounded-xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]">
            <h2 className="text-lg font-semibold mb-4 text-[color:var(--osd-text)] flex items-center gap-2">
              <Settings className="w-5 h-5" />
              General Settings
            </h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-[color:var(--osd-text)] mb-2">
                  Configuration Option
                </label>
                <input
                  type="text"
                  className="w-full p-3 rounded-lg border border-[color:var(--osd-border)] bg-[color:var(--osd-background)] text-[color:var(--osd-text)]"
                  placeholder="Enter configuration value..."
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}}
'''

def create_general_page(name: str, label: str) -> str:
    """Create a general feature page"""
    return f'''import {{ useState }} from 'react'

export default function {name}() {{
  return (
    <div className="min-h-screen bg-[color:var(--osd-background)] p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-[color:var(--osd-text)] mb-2">
            {label}
          </h1>
          <p className="text-[color:var(--osd-muted)]">
            {label} features and functionality
          </p>
        </div>

        <div className="p-6 rounded-xl border border-[color:var(--osd-border)] bg-[color:var(--osd-surface)]">
          <div className="text-center py-12 text-[color:var(--osd-muted)]">
            <p>Feature implementation in progress</p>
          </div>
        </div>
      </div>
    </div>
  )
}}
'''

def main():
    """Main restoration process"""
    print("🚀 Starting Comprehensive GUI Restoration")
    print("=" * 60)
    
    # Step 1: Extract routes from IA manifest
    print("\n📋 Step 1: Extracting routes from IA manifest...")
    routes = extract_routes_from_ia_manifest()
    print(f"  Found {len(routes['platforms'])} platforms")
    print(f"  Found {len(routes['categories'])} categories")
    print(f"  Found {len(routes['features'])} features")
    
    # Step 2: Find all pages in commits
    print("\n🔍 Step 2: Analyzing commits for best page versions...")
    all_pages = set()
    page_versions: Dict[str, List[Tuple[str, PageInfo]]] = defaultdict(list)
    
    for commit in COMMITS_TO_ANALYZE:
        print(f"  Analyzing commit {commit}...")
        pages = list_pages_in_commit(commit)
        all_pages.update(pages)
        print(f"    Found {len(pages)} pages")
    
    print(f"\n  Total unique pages found: {len(all_pages)}")
    
    # Step 3: Find best version for each page
    print("\n⭐ Step 3: Finding best version for each page...")
    best_versions: Dict[str, Tuple[str, PageInfo]] = {}
    
    for page_path in sorted(all_pages):
        result = find_best_commit_for_page(page_path)
        if result:
            commit, info = result
            best_versions[page_path] = (commit, info)
            if info.score > 50:  # Only show high-scoring pages
                print(f"  ✅ {page_path} (score: {info.score}) from {commit}")
    
    # Step 4: Restore pages from best commits
    print("\n📥 Step 4: Restoring pages from best commits...")
    restored_count = 0
    
    for page_path, (commit, info) in best_versions.items():
        target_path = BASE_DIR / page_path
        if restore_page_from_commit(commit, page_path, target_path):
            restored_count += 1
    
    print(f"\n  ✅ Restored {restored_count} pages")
    
    # Step 5: Create category home pages
    print("\n🏠 Step 5: Creating category home/dashboard pages...")
    category_homes_created = 0
    
    for category_route in routes['categories']:
        # Extract category label from route
        category_label = category_route.split("/")[-1].replace("-", " ").title()
        file_path = route_to_file_path(category_route)
        target_path = BASE_DIR / file_path
        
        if not target_path.exists():
            content = create_category_home_page(category_route, category_label)
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(content)
            print(f"  ✅ Created {file_path}")
            category_homes_created += 1
    
    print(f"\n  ✅ Created {category_homes_created} category home pages")
    
    # Step 6: Create missing feature pages
    print("\n✨ Step 6: Creating missing feature pages...")
    features_created = 0
    
    for feature_route in routes['features']:
        file_path = route_to_file_path(feature_route)
        target_path = BASE_DIR / file_path
        
        if not target_path.exists():
            feature_name = feature_route.split("/")[-1].replace("-", " ").title()
            content = create_feature_page(feature_route, feature_name)
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(content)
            print(f"  ✅ Created {file_path}")
            features_created += 1
    
    print(f"\n  ✅ Created {features_created} feature pages")
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ Restoration Complete!")
    print(f"  - Restored {restored_count} pages from commits")
    print(f"  - Created {category_homes_created} category home pages")
    print(f"  - Created {features_created} feature pages")
    print("=" * 60)

if __name__ == "__main__":
    main()
