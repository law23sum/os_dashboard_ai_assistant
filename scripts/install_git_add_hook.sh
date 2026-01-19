#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
source_line="if [ -f \"$repo_root/scripts/git_add_hook.sh\" ]; then source \"$repo_root/scripts/git_add_hook.sh\"; fi"

update_file() {
    local file="$1"
    if [[ -f "$file" ]] && grep -F "$source_line" "$file" >/dev/null 2>&1; then
        echo "[git-hook] $file already contains the hook."
        return
    fi
    echo "" >>"$file"
    echo "# Auto-loaded AI OS git-add hook" >>"$file"
    echo "$source_line" >>"$file"
    echo "[git-hook] Added hook reference to $file"
}

for target in "$HOME/.bashrc" "$HOME/.bash_profile"; do
    touch "$target"
    update_file "$target"
done

echo "[git-hook] Installation complete. Restart your shell to enable the wrapper."
