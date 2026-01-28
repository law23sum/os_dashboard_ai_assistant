#!/usr/bin/env python3
"""
Restore/generate all pages from IA manifest.
Reads the TypeScript manifest and creates/restores pages accordingly.
"""

import json
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

# Source commits
COMMITS = {
    'stable': '3a154a6e6305fe9f3a760f44b1b10d73e1ed3256',
    'increments': '58cfc345630f68bf10909538aba48c12f87ce9df',
    'backup': '4acea80190121b8ab79d8cd1367166bcfead8bde'
}

def run_git(cmd: List[str], check=False) -> tuple[str, int]:
    """Run git command."""
    try:
        result = subprocess.run(['git'] + cmd, capture_output=True, text=True, check=check)
        return result.stdout.strip(), result.returncode
    except:
        return "", 1

def get_file_content(commit: str, filepath: str) -> Optional[str]:
    """Get file content from commit."""
    output, code = run_git(['show', f'{commit}:{filepath}'], check=False)
    return output if code == 0 else None

def extract_manifest_data(ts_file: Path) -> Dict:
    """Extract manifest data from TypeScript file."""
    with open(ts_file, 'r') as f:
        content = f.read()
    
    # Find the iaManifest array
    match = re.search(r'export const iaManifest: IAPlatform\[\] = (\[.*?\])', content, re.DOTALL)
    if not match:
        # Try JSON format
        match = re.search(r'= (\[.*?\])', content, re.DOTALL)
    
    if match:
        json_str = match.group(1)
        # Clean up TypeScript syntax
        json_str = re.sub(r'//.*?\n', '', json_str)  # Remove comments
        json_str = re.sub(r',\s*}', '}', json_str)  # Remove trailing commas
        json_str = re.sub(r',\s*]', ']', json_str)
        try:
            return json.loads(json_str)
        except:
            pass
    
    # Fallback: parse as JSON directly if it's valid JSON
    try:
        # Try to extract just the array part
        start = content.find('[')
        end = content.rfind(']') + 1
        if start >= 0 and end > start:
            json_str = content[start:end]
            return json.loads(json_str)
    except:
        pass
    
    return []

def generate_feature_page(component_path: str, feature: Dict) -> str:
    """Generate feature page component."""
    component_name = Path(component_path).stem
    label = feature.get('label', 'Feature')
    route = feature.get('route', '/')
    
    return f'''import {{ useParams, useLocation }} from 'react-router-dom'
import {{ FeaturePageTemplate }} from '../components/templates/FeaturePageTemplate'

/**
 * {label} Page
 * Route: {route}
 */
export default function {component_name}() {{
  const params = useParams()
  const location = useLocation()
  
  return (
    <FeaturePageTemplate
      title="{label}"
      route="{route}"
      description="Feature page for {label}"
    />
  )
}}
'''

def generate_category_home(component_path: str, category: Dict) -> str:
    """Generate category home page."""
    component_name = Path(component_path).stem
    label = category.get('label', 'Category')
    route = category.get('homeRoute', '/')
    features = category.get('features', [])
    feature_labels = [f.get('label', '') for f in features[:20]]
    
    return f'''import {{ useParams, useLocation }} from 'react-router-dom'
import {{ CategoryHomeTemplate }} from '../components/templates/CategoryHomeTemplate'

/**
 * {label} Category Home
 * Route: {route}
 * 
 * Hybrid dashboard/home page for {label}
 */
export default function {component_name}() {{
  const params = useParams()
  const location = useLocation()
  
  const features = {json.dumps(feature_labels, indent=2)}
  
  return (
    <CategoryHomeTemplate
      title="{label}"
      route="{route}"
      description="Category home and dashboard for {label}"
      features={features}
    />
  )
}}
'''

def main():
    """Restore/generate all pages."""
    print("=" * 80)
    print("Page Restoration from IA Manifest")
    print("=" * 80)
    
    manifest_file = Path(__file__).parent.parent / 'frontend' / 'src' / 'data' / 'iaManifest.ts'
    if not manifest_file.exists():
        print(f"Error: {manifest_file} not found")
        return
    
    print(f"\nLoading manifest from {manifest_file}...")
    platforms = extract_manifest_data(manifest_file)
    
    if not platforms:
        print("Error: Could not parse manifest. Using JSON fallback...")
        json_file = Path(__file__).parent.parent / 'documentation' / 'gui_nav_structure' / 'gui_nav.latest.json'
        if json_file.exists():
            with open(json_file, 'r') as f:
                nav_data = json.load(f)
            # Convert to platform structure (simplified)
            platforms = []
        else:
            print("Error: No manifest data found")
            return
    
    pages_dir = Path(__file__).parent.parent / 'frontend' / 'src' / 'pages'
    pages_dir.mkdir(parents=True, exist_ok=True)
    
    restored = 0
    generated = 0
    skipped = 0
    
    print(f"\nProcessing {len(platforms)} platforms...")
    
    for platform in platforms:
        platform_id = platform.get('id', '')
        print(f"\nPlatform: {platform.get('label', platform_id)}")
        
        for category in platform.get('categories', []):
            category_id = category.get('id', '')
            
            # Category home page
            home_path = category.get('homeComponentPath', '')
            if home_path:
                # Extract relative path
                if 'frontend/src/pages' in home_path:
                    rel_path = home_path.replace('frontend/src/pages/', '')
                    target_file = pages_dir / rel_path
                else:
                    target_file = pages_dir / Path(home_path).name
                
                if not target_file.exists():
                    best_commit = category.get('homeBestCommit', 'stable')
                    commit_sha = COMMITS.get(best_commit, COMMITS['stable'])
                    
                    # Try to restore from commit
                    content = get_file_content(commit_sha, home_path)
                    if content:
                        target_file.parent.mkdir(parents=True, exist_ok=True)
                        target_file.write_text(content)
                        print(f"  ✓ Restored category home: {target_file.name}")
                        restored += 1
                    else:
                        # Generate template
                        target_file.parent.mkdir(parents=True, exist_ok=True)
                        content = generate_category_home(str(target_file), category)
                        target_file.write_text(content)
                        print(f"  + Generated category home: {target_file.name}")
                        generated += 1
                else:
                    skipped += 1
            
            # Feature pages
            for feature in category.get('features', []):
                feature_path = feature.get('componentPath', '')
                if not feature_path:
                    continue
                
                # Extract relative path
                if 'frontend/src/pages' in feature_path:
                    rel_path = feature_path.replace('frontend/src/pages/', '')
                    target_file = pages_dir / rel_path
                else:
                    target_file = pages_dir / Path(feature_path).name
                
                if not target_file.exists():
                    best_commit = feature.get('bestCommit', 'stable')
                    commit_sha = COMMITS.get(best_commit, COMMITS['stable'])
                    
                    # Try to restore from commit
                    content = get_file_content(commit_sha, feature_path)
                    if content:
                        target_file.parent.mkdir(parents=True, exist_ok=True)
                        target_file.write_text(content)
                        print(f"    ✓ Restored feature: {target_file.name}")
                        restored += 1
                    else:
                        # Generate template
                        target_file.parent.mkdir(parents=True, exist_ok=True)
                        content = generate_feature_page(str(target_file), feature)
                        target_file.write_text(content)
                        print(f"    + Generated feature: {target_file.name}")
                        generated += 1
                else:
                    skipped += 1
    
    print(f"\n{'='*80}")
    print(f"Restoration complete!")
    print(f"  Restored: {restored} pages")
    print(f"  Generated: {generated} pages")
    print(f"  Skipped (exist): {skipped} pages")
    print(f"  Total processed: {restored + generated + skipped} pages")

if __name__ == '__main__':
    main()

