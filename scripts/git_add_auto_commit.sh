#!/usr/bin/env bash
# Wrapper for `git add` that automatically triggers the auto-commit helper when
# the staged set includes the entire working tree (i.e., `git add .`).
#
# Usage:
#   ./scripts/git_add_auto_commit.sh .          # behaves like `git add .` and commits immediately
#   ./scripts/git_add_auto_commit.sh <paths...> # just runs `git add` on selected paths
#
# Environment variables:
#   GIT_STAGE_SKIP_PROMPTS=1  Skip all prompts and use AI to generate reasons
#
# For a fully transparent experience, add an alias in your shell profile:
#   alias gitadd='./scripts/git_add_auto_commit.sh'
# then run `gitadd .` instead of `git add .`.

set -euo pipefail
cd "$(dirname "$0")/.."

if [[ $# -eq 0 ]]; then
    set -- .
fi

# Perform the actual git add with the provided arguments.
if ! git add "$@"; then
    echo "git add failed. Ensure you have write access to the repository (.git/index)." >&2
    exit 1
fi

# Capture staged files and collect reasoning metadata.
# Pass through GIT_STAGE_SKIP_PROMPTS if set
REASONER_ARGS=""
if [[ "${GIT_STAGE_SKIP_PROMPTS:-}" == "1" ]]; then
    REASONER_ARGS="--skip-prompts"
fi
if ! python3 scripts/git_stage_reasoner.py $REASONER_ARGS; then
    echo "Warning: unable to capture staged file reasons." >&2
fi

# If the caller staged the whole tree (the common case the user asked about),
# immediately trigger the auto-commit helper.
if [[ $# -eq 1 && "$1" == "." ]]; then
    GIT_AUTO_SKIP_STAGE=1 python scripts/git_auto_commit.py
else
    echo "Staged: $* (auto-commit only runs on 'git add .')"
fi
