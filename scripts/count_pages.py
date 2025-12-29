
import re

def count_pages():
    with open('frontend/src/data/iaManifest.ts', 'r') as f:
        content = f.read()
    
    # Count componentPath occurrences as they represent leaf nodes (features) or category homes
    # Note: iaManifest structure has componentPath for features and homeComponentPath for categories.
    
    feature_paths = re.findall(r"componentPath: '(.*?)'", content)
    home_paths = re.findall(r"homeComponentPath: '(.*?)'", content)
    
    # Filter out duplicates if any (though regex shouldn't overlap for these specific keys)
    # Actually, feature definition uses 'componentPath'. Category uses 'homeComponentPath'.
    # In my generator script:
    # category home -> homeComponentPath
    # feature -> componentPath
    
    all_paths = set(feature_paths + home_paths)
    
    print(f"Total unique page components defined in Manifest: {len(all_paths)}")
    print(f"Feature pages: {len(feature_paths)}")
    print(f"Category home pages: {len(home_paths)}")

if __name__ == '__main__':
    count_pages()

