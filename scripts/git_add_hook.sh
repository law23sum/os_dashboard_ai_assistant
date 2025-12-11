#!/usr/bin/env bash
# Source this script from ~/.bashrc or ~/.bash_profile to wrap `git add`.
# The wrapper calls the stage reasoner (and auto-commit helper on `git add .`)
# whenever you're working inside the OS Dashboard repo.

if [[ -n "${_OS_DASHBOARD_GIT_HOOK:-}" ]]; then
    return
fi
export _OS_DASHBOARD_GIT_HOOK=1

_OS_DASHBOARD_REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

_os_dashboard_git_wrapper() {
    command git "$@"
    local status=$?
    if [[ $status -ne 0 ]]; then
        return $status
    fi

    if [[ "$1" != "add" ]]; then
        return $status
    fi

    local repo_root
    repo_root="$(git rev-parse --show-toplevel 2>/dev/null)" || return $status
    if [[ "$repo_root" != "$_OS_DASHBOARD_REPO_ROOT" ]]; then
        return $status
    fi

    (cd "$_OS_DASHBOARD_REPO_ROOT" && python3 scripts/git_stage_reasoner.py)

    local last_arg="${@: -1}"
    if [[ "$#" -eq 2 && "$last_arg" == "." ]]; then
        (cd "$_OS_DASHBOARD_REPO_ROOT" && GIT_AUTO_SKIP_STAGE=1 python3 scripts/git_auto_commit.py)
    fi
    return $status
}

if [[ "$(type -t git)" == "function" ]]; then
    unset -f git
fi

git() {
    if [[ "$1" == "add" ]]; then
        _os_dashboard_git_wrapper "$@"
    else
        command git "$@"
    fi
}

export -f git
