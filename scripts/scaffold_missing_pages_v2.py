#!/usr/bin/env python3
"""
Scaffold missing page components using FeaturePageTemplate.
Creates pages that use the existing template component.
"""

import json
import re
from pathlib import Path
from typing import Dict

def route_to_component_name(route: str) -> str:
    """Convert route to PascalCase component name."""
    if route == '/':
        return 'Dashboard'
    
    route = route.strip('/')
    parts = route.split('/')
    component_name = ''.join(word.capitalize().replace('-', '') for word in parts)
    
    return component_name

def generate_page_component(route_info: Dict) -> str:
    """Generate a page component using FeaturePageTemplate."""
    route = route_info['route']
    component_name = route_to_component_name(route)
    route_type = route_info.get('type', 'feature')
    
    # Determine page title from route
    title_parts = route.strip('/').split('/')
    if not title_parts or title_parts == ['']:
        title = 'Dashboard'
    else:
        title = ' '.join(word.capitalize().replace('-', ' ') for word in title_parts)
    
    # Use FeaturePageTemplate for features, CategoryHomeTemplate for category homes
    if route_type == 'categoryHome':
        template = '''import { CategoryHomeTemplate } from '../components/templates/CategoryHomeTemplate'
import { useIARouteContext } from '../navigation/iaContext'

/**
 * {title} - Category Home Page
 * Route: {route}
 */
export default function {component_name}() {{
  const routeContext = useIARouteContext()
  const features = routeContext.category?.features || []
  
  return (
    <CategoryHomeTemplate
      title="{title}"
      description="Category home dashboard for {title}"
      features={features.map((f) => ({{
        title: f.label,
        path: f.route
      }}))}
    />
  )
}}
'''
    else:
        template = '''import { FeaturePageTemplate } from '../components/templates/FeaturePageTemplate'
import { useIARouteContext } from '../navigation/iaContext'

/**
 * {title} - Feature Page
 * Route: {route}
 */
export default function {component_name}() {{
  const routeContext = useIARouteContext()
  
  
  return (
    <FeaturePageTemplate
      title="{title}"
      description="Feature page for {title}"
      parameters={[
        {{ name: 'input1', label: 'Input Parameter 1', type: 'text', required: true }},
        {{ name: 'input2', label: 'Input Parameter 2', type: 'number', required: false }},
        {{ name: 'input3', label: 'Input Parameter 3', type: 'select', options: [
          {{ value: 'option1', label: 'Option 1' }},
          {{ value: 'option2', label: 'Option 2' }}
        ]}}
      ]}
      configSelector={{
        label: 'Configuration Profile',
        options: [
          {{ id: 'default', name: 'Default' }},
          {{ id: 'custom', name: 'Custom' }},
          {{ id: 'optimized', name: 'Optimized' }}
        ]
      }}
    />
  )
}}
'''
    
    # Replace placeholders manually to avoid f-string escaping issues
    component_code = template.replace('{title}', title)
    component_code = component_code.replace('{route}', route)
    component_code = component_code.replace('{component_name}', component_name)
    
    return component_code

def main():
    """Scaffold missing page components."""
    missing_report = Path('missing_pages_report.json')
    
    if not missing_report.exists():
        print("Error: missing_pages_report.json not found. Run verify_all_page_components.py first.")
        return
    
    with open(missing_report, 'r') as f:
        missing_pages = json.load(f)
    
    print(f"Found {len(missing_pages)} missing pages to scaffold\n")
    
    created = 0
    skipped = 0
    errors = []
    
    for page_info in missing_pages:
        component_path = Path(page_info['path'])
        
        # Skip if file already exists
        if component_path.exists():
            skipped += 1
            continue
        
        # Create directory if needed
        component_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate component code
        try:
            component_code = generate_page_component(page_info)
            
            # Write file
            with open(component_path, 'w') as f:
                f.write(component_code)
            print(f"✅ Created {component_path}")
            created += 1
        except Exception as e:
            error_msg = f"Failed to create {component_path}: {e}"
            errors.append(error_msg)
            print(f"❌ {error_msg}")
    
    print(f"\nSummary:")
    print(f"  ✅ Created: {created}")
    print(f"  ⏭️  Skipped: {skipped}")
    print(f"  ❌ Errors: {len(errors)}")
    print(f"  📝 Total: {len(missing_pages)}")
    
    if errors:
        print(f"\nErrors (showing first 10):")
        for error in errors[:10]:
            print(f"  - {error}")

if __name__ == '__main__':
    main()
