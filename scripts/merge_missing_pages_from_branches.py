#!/usr/bin/env python3
"""
Merge missing page files from branches into incremeents.
Checks for .tsx files in frontend/src/pages/ and merges any that are missing.
"""

import subprocess
from pathlib import Path
from collections import defaultdict

def run_git(cmd: str, check: bool = True) -> str:
    """Run git command and return output"""
    result = subprocess.run(
        f"git {cmd}",
        shell=True,
        capture_output=True,
        text=True,
        check=check
    )
    return result.stdout.strip()

def get_files_in_branch(branch: str, path_prefix: str = "frontend/src/pages/") -> set:
    """Get all .tsx files in a branch"""
    try:
        output = run_git(f"ls-tree -r --name-only {branch} {path_prefix}", check=False)
        if output:
            files = {f for f in output.split('\n') if f.endswith('.tsx') and path_prefix in f}
            return files
    except:
        pass
    return set()

def get_current_files(path_prefix: str = "frontend/src/pages/") -> set:
    """Get all .tsx files in current working directory"""
    pages_dir = Path(path_prefix)
    if pages_dir.exists():
        files = set()
        for f in pages_dir.rglob("*.tsx"):
            try:
                rel_path = str(f.relative_to(Path.cwd()))
                files.add(rel_path)
            except ValueError:
                # File is outside cwd, use absolute path but make it relative to repo root
                files.add(str(f))
        return files
    return set()

def get_file_content_from_branch(branch: str, file_path: str) -> str:
    """Get file content from a branch"""
    try:
        output = run_git(f"show {branch}:{file_path}", check=False)
        if output and not output.startswith("fatal:") and not output.startswith("error:"):
            return output
    except:
        pass
    return None

def main():
    print("="*70)
    print("MERGE MISSING PAGES FROM BRANCHES")
    print("="*70)
    
    current_branch = run_git("branch --show-current")
    if current_branch != "incremeents":
        print(f"⚠️  Not on incremeents branch (currently on {current_branch})")
        print("Switching to incremeents...")
        run_git("checkout incremeents")
    
    # Get current files
    current_files = get_current_files()
    print(f"\nCurrent branch has {len(current_files)} .tsx files in frontend/src/pages/")
    
    # Branches to check
    branches = [
        "fix/ia-navigation-merge",
        "fix/restore-gui-glory-20251220",
        "gui-fully-restored",
        "ia-reorg-merge-20251221",
        "integration/ia-navigation-final",
        "integration/restore-pages-ia-ktg",
    ]
    
    # Also check specific commits
    commits_to_check = {
        "4acea80": "4acea80190121b8ab79d8cd1367166bcfead8bde",
        "58cfc34": "58cfc345630f68bf10909538aba48c12f87ce9df",
        "3a154a6": "3a154a6e6305fe9f3a760f44b1b10d73e1ed3256",
    }
    
    all_missing_files = defaultdict(list)  # file_path -> [branches that have it]
    
    print(f"\nAnalyzing {len(branches)} branches and {len(commits_to_check)} commits...\n")
    
    # Check branches
    for branch in branches:
        branch_files = get_files_in_branch(branch)
        if branch_files:
            missing = branch_files - current_files
            if missing:
                print(f"  {branch}: {len(missing)} files not in current branch")
                for file_path in missing:
                    all_missing_files[file_path].append(branch)
            else:
                print(f"  {branch}: All files already present")
        else:
            print(f"  {branch}: No files found or branch doesn't exist")
    
    # Check commits
    for name, commit_hash in commits_to_check.items():
        commit_files = get_files_in_branch(commit_hash)
        if commit_files:
            missing = commit_files - current_files
            if missing:
                print(f"  commit-{name}: {len(missing)} files not in current branch")
                for file_path in missing:
                    all_missing_files[file_path].append(f"commit-{name}")
        else:
            print(f"  commit-{name}: No files found")
    
    if not all_missing_files:
        print(f"\n✓ All page files are already present in incremeents branch!")
        return
    
    print(f"\n{'='*70}")
    print(f"FOUND {len(all_missing_files)} MISSING FILES")
    print(f"{'='*70}\n")
    
    # Show summary
    for file_path, sources in list(all_missing_files.items())[:20]:
        print(f"  {file_path}")
        print(f"    Available in: {', '.join(sources[:3])}")
    
    if len(all_missing_files) > 20:
        print(f"  ... and {len(all_missing_files) - 20} more")
    
    # Strategy: For each missing file, take it from the first branch that has it
    print(f"\n{'='*70}")
    print("COPYING MISSING FILES")
    print(f"{'='*70}\n")
    
    copied_count = 0
    failed_count = 0
    
    for file_path, sources in all_missing_files.items():
        source = sources[0]  # Take from first available source
        content = get_file_content_from_branch(source, file_path)
        
        if content:
            # Write file
            target_path = Path(file_path)
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(content)
            print(f"  ✓ Copied {file_path} from {source}")
            copied_count += 1
        else:
            print(f"  ✗ Failed to copy {file_path} from {source}")
            failed_count += 1
    
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    print(f"Files copied: {copied_count}")
    print(f"Files failed: {failed_count}")
    print(f"\nNext steps:")
    print(f"1. Review the copied files")
    print(f"2. Stage them: git add frontend/src/pages/")
    print(f"3. Commit the changes")
    print(f"4. Test that pages render correctly")

if __name__ == "__main__":
    main()

