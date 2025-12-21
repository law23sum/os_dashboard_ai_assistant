#!/usr/bin/env python3
"""Fix double curly braces in generated TypeScript files."""

from pathlib import Path
import re

def fix_file(file_path: Path):
    """Fix double braces in a TypeScript file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Replace {{ with { and }} with } but preserve JSX expressions
    # JSX expressions like {variable} should stay as is
    # But function bodies and object literals need fixing
    
    # Fix function declarations: function Name() {{ -> function Name() {
    content = re.sub(r'\)\s*\{\{', ') {', content)
    
    # Fix arrow functions: => {{ -> => {
    content = re.sub(r'=>\s*\{\{', '=> {', content)
    
    # Fix object literals in return statements: return {{ -> return {
    content = re.sub(r'return\s+\{\{', 'return {', content)
    
    # Fix closing braces: }} -> }
    # But be careful - we want to preserve single } that are correct
    # Replace }} at end of lines or before newlines
    content = re.sub(r'\}\}\s*$', '}', content, flags=re.MULTILINE)
    content = re.sub(r'\}\}\s*\n', '}\n', content)
    content = re.sub(r'\}\}\s*\)', '})', content)
    content = re.sub(r'\}\}\s*,', '},', content)
    content = re.sub(r'\}\}\s*;', '};', content)
    
    # Fix object properties: {{ name: -> { name:
    content = re.sub(r'\{\{\s*name:', '{ name:', content)
    content = re.sub(r'\{\{\s*id:', '{ id:', content)
    content = re.sub(r'\{\{\s*value:', '{ value:', content)
    content = re.sub(r'\{\{\s*label:', '{ label:', content)
    content = re.sub(r'\{\{\s*type:', '{ type:', content)
    content = re.sub(r'\{\{\s*required:', '{ required:', content)
    content = re.sub(r'\{\{\s*options:', '{ options:', content)
    content = re.sub(r'\{\{\s*success:', '{ success:', content)
    content = re.sub(r'\{\{\s*results:', '{ results:', content)
    content = re.sub(r'\{\{\s*id:', '{ id:', content)
    
    # Fix array elements: [{{ -> [{
    content = re.sub(r'\[\s*\{\{', '[{', content)
    
    # Fix any remaining double braces in object contexts
    # This is a bit aggressive but should catch most cases
    lines = content.split('\n')
    fixed_lines = []
    for line in lines:
        # Skip lines that are clearly JSX (containing < or />)
        if '<' in line and ('<' in line.split('//')[0] if '//' in line else True):
            # In JSX, {{ should become { for expressions
            line = line.replace('{{', '{').replace('}}', '}')
        else:
            # In TypeScript code, fix double braces
            line = line.replace('{{', '{').replace('}}', '}')
        fixed_lines.append(line)
    
    content = '\n'.join(fixed_lines)
    
    with open(file_path, 'w') as f:
        f.write(content)

def main():
    """Fix all generated page files."""
    pages_dir = Path('frontend/src/pages')
    
    # Find all recently created files (those with double braces)
    fixed = 0
    for tsx_file in pages_dir.rglob('*.tsx'):
        try:
            with open(tsx_file, 'r') as f:
                content = f.read()
                if '{{' in content or '}}' in content:
                    fix_file(tsx_file)
                    fixed += 1
        except Exception as e:
            print(f"Error fixing {tsx_file}: {e}")
    
    print(f"Fixed {fixed} files")

if __name__ == '__main__':
    main()




