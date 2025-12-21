
import re
import os

def main():
    manifest_path = 'frontend/src/data/iaManifest.ts'
    with open(manifest_path, 'r') as f:
        content = f.read()
        
    # Extract paths
    home_paths = re.findall(r"homeComponentPath:\s*['\"](.*?)['\"]", content)
    feat_paths = re.findall(r"componentPath:\s*['\"](.*?)['\"]", content)
    
    # Filter out feature paths that are also home paths (duplicates in regex)
    # In manifest structure: homeComponentPath is unique, componentPath is unique per feature.
    # Total pages = set(home_paths + feat_paths)
    
    all_paths = set(home_paths + feat_paths)
    
    print(f"Total unique paths in manifest: {len(all_paths)}")
    
    missing = []
    for p in all_paths:
        if not os.path.exists(p):
            missing.append(p)
            
    print(f"Missing files on disk: {len(missing)}")
    if missing:
        print("First 20 missing:")
        for m in missing[:20]:
            print(m)

if __name__ == '__main__':
    main()




