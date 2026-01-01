import json
import re
import os
import subprocess

GUI_DOC_PATH = "documentation/gui_nav_structure/GUI_STRUCTURE_LATEST.md"
ROUTE_MATRIX_PATH = "route_matrix.json"
MANIFEST_PATH = "frontend/src/data/iaManifest.generated.ts"
ROUTES_PATH = "frontend/src/routesIA.tsx"

# Helper to slugify
def slugify(text):
    return text.lower().replace(" & ", "-").replace(" ", "-").replace("/", "-")

def read_route_matrix():
    with open(ROUTE_MATRIX_PATH, "r") as f:
        return json.load(f)

def get_best_version(route_entry):
    if not route_entry or not route_entry.get("best_commit"):
        return None
    return route_entry

def restore_file(sha, path):
    if not path or sha == "main":
        return # Already there
    
    # Check if file exists in current workspace (it might differ from main if we modified it)
    # But git restore will overwrite.
    print(f"Restoring {path} from {sha}...")
    try:
        subprocess.run(["git", "restore", "--source", sha, "--", path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to restore {path}: {e}")

def create_stub_page(name, route, path):
    # Sanitize path
    clean_path = path.replace("**[NEW]**", "").replace("**", "").replace("[", "").replace("]", "").replace(" ", "").replace("&", "")
    clean_path = re.sub(r"[^a-zA-Z0-9/._-]", "", clean_path)
    
    print(f"Creating stub for {name} at {clean_path}...")
    content = f"""
import React from 'react';
import {{ Card, CardContent, CardHeader, CardTitle }} from "@/components/ui/card";
import {{ Button }} from "@/components/ui/button";

const {slugify(name).replace("-", "").capitalize()}Page = () => {{
  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold tracking-tight">{name}</h1>
        <div className="space-x-2">
            <Button variant="outline">Configuration</Button>
            <Button>Execute</Button>
        </div>
      </div>
      
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">Active</div>
            <p className="text-xs text-muted-foreground">System operational</p>
          </CardContent>
        </Card>
      </div>

      <Card className="min-h-[400px]">
        <CardHeader>
          <CardTitle>Results & Output</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center h-64 text-muted-foreground">
             <p>Results placeholder for {route}</p>
             <p className="text-sm">Implied functionality based on IA.</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}};

export default {slugify(name).replace("-", "").capitalize()}Page;
"""
    # Ensure dir exists
    try:
        os.makedirs(os.path.dirname(clean_path), exist_ok=True)
        with open(clean_path, "w") as f:
            f.write(content.strip())
    except Exception as e:
        print(f"Error creating stub {clean_path}: {e}")
    
    return clean_path

def parse_ia_and_restore():
    matrix = read_route_matrix()
    matrix_map = {m["route"]: m for m in matrix}
    
    platforms = []
    current_platform = None
    current_category = None
    current_group = None
    
    with open(GUI_DOC_PATH, "r") as f:
        lines = f.readlines()
        
    for line in lines:
        line = line.strip()
        
        # Platform (H2)
        if line.startswith("## ") and not line.startswith("###"):
            name = line.replace("## ", "").strip()
            if name in ["Legend", "Information Architecture Rules"]: continue
            
            scope = 'enterprise' if "Enterprise" in name else 'personal'
            
            current_platform = {
                "id": slugify(name),
                "title": name,
                "categories": [],
                "actorScope": scope
            }
            platforms.append(current_platform)
            current_category = None
            
        # Category (H3)
        elif line.startswith("### ") and current_platform:
            name = line.replace("### ", "").strip()
            current_category = {
                "id": slugify(name),
                "title": name,
                "route": f"/{current_platform['id']}/{slugify(name)}",
                "features": [],
                "actorScope": current_platform['actorScope'] # Inherit
            }
            current_platform["categories"].append(current_category)
            current_group = None
            
            # Category Home Logic
            cat_file = f"frontend/src/pages/{name.replace(' ', '').replace('&', '')}Home.tsx"
            cat_file = cat_file.replace("**", "")
            
            if not os.path.exists(cat_file):
                cat_file = create_stub_page(name + " Home", current_category["route"], cat_file)
            
            current_category["componentPath"] = cat_file
            
        # Group (H4)
        elif line.startswith("#### ") and current_category:
            current_group = line.replace("#### ", "").strip()
            
        # Feature (List item)
        elif line.startswith("- ") and current_category:
            match = re.search(r"- (?:\[NEW\] )?(.+?) \(`(/.*?)`\)", line)
            if match:
                feat_name = match.group(1).strip()
                orig_route = match.group(2).strip()
                
                new_route = f"/{current_platform['id']}/{current_category['id']}/{slugify(feat_name)}"
                
                entry = matrix_map.get(orig_route)
                
                component_path = ""
                if entry and entry.get("best_path"):
                    if entry.get("best_commit"):
                        restore_file(entry["best_commit"], entry["best_path"])
                    component_path = entry["best_path"]
                else:
                    # Create stub
                    stub_name = slugify(feat_name).replace("-", "").capitalize() + ".tsx"
                    component_path = f"frontend/src/pages/{stub_name}"
                    if not os.path.exists(component_path):
                         component_path = create_stub_page(feat_name, new_route, component_path)
                
                current_category["features"].append({
                    "title": feat_name,
                    "route": new_route,
                    "original_route": orig_route,
                    "group": current_group,
                    "componentPath": component_path,
                    "actorScope": current_category['actorScope']
                })

    return platforms

def generate_manifest_ts(platforms):
    print(f"Writing manifest to {MANIFEST_PATH}...")
    try:
        content = f"""
// Generated by restore_ia.py

export type ActorScope = 'personal' | 'enterprise' | 'both';

export interface IAFeature {{
  title: string;
  route: string;
  original_route?: string;
  group?: string;
  componentPath?: string;
  actorScope: ActorScope;
}}

export interface IACategory {{
  id: string;
  title: string;
  route: string;
  features: IAFeature[];
  componentPath?: string;
  actorScope: ActorScope;
}}

export interface IAPlatform {{
  id: string;
  title: string;
  categories: IACategory[];
  actorScope: ActorScope;
}}

export const IAManifest: IAPlatform[] = {json.dumps(platforms, indent=2)};
"""
        with open(MANIFEST_PATH, "w") as f:
            f.write(content)
        print("Manifest written successfully.")
    except Exception as e:
        print(f"Error writing manifest: {e}")

def generate_routes_tsx(platforms):
    imports = [] # Lazy imports map
    routes = []
    
    # We need to map component paths to imports
    comp_map = {}
    comp_counter = 0
    
    def get_comp_name(path):
        nonlocal comp_counter
        if path not in comp_map:
            comp_counter += 1
            name = f"Component{comp_counter}"
            # Convert path to relative import
            rel_path = os.path.relpath(path, "frontend/src").replace(".tsx", "").replace(".js", "")
            # Lazy load definition
            imports.append(f"""
const {name} = React.lazy(async () => {{
  const mod = await import('./{rel_path}');
  // Try to find a valid component export: default, or first exported function
  const component = mod.default || Object.values(mod).find(v => typeof v === 'function' && (v.name || '').match(/^[A-Z]/));
  return {{ default: component || (() => <div>Component not found in module</div>) }};
}});""")
            comp_map[path] = name
        return comp_map[path]

    # Helper to generate route lines
    for plat in platforms:
        for cat in plat["categories"]:
            # Category Home
            if "componentPath" in cat:
                cname = get_comp_name(cat["componentPath"])
                routes.append(f"""<Route path="{cat['route']}" element={{<React.Suspense fallback={{<div>Loading...</div>}}><{cname} /></React.Suspense>}} />""")
            
            for feat in cat["features"]:
                if "componentPath" in feat:
                    fname = get_comp_name(feat["componentPath"])
                    routes.append(f"""<Route path="{feat['route']}" element={{<React.Suspense fallback={{<div>Loading...</div>}}><{fname} /></React.Suspense>}} />""")

    # Redirect root to first platform/category
    first_route = platforms[0]["categories"][0]["route"] if platforms and platforms[0]["categories"] else "/"
    
    content = f"""
import React from 'react';
import {{ Routes, Route, Navigate }} from 'react-router-dom';

// Lazy Loaded Components
{chr(10).join(imports)}

export const AppRoutesIA = () => {{
  return (
    <Routes>
      <Route path="/" element={{<Navigate to="{first_route}" replace />}} />
      {chr(10).join(routes)}
      <Route path="*" element={{<div>Page Not Found</div>}} />
    </Routes>
  );
}};
"""
    with open(ROUTES_PATH, "w") as f:
        f.write(content)

def main():
    print("Starting IA Restoration...")
    platforms = parse_ia_and_restore()
    print("Generating Manifest...")
    generate_manifest_ts(platforms)
    print("Generating Routes...")
    generate_routes_tsx(platforms)
    print("Done.")

if __name__ == "__main__":
    main()
