#!/usr/bin/env bash
set -euo pipefail

# Universal "execute project with guardrails" wrapper.
#
# Usage:
#   scripts/osd_run.sh --repo /path/to/repo -- <your command...>
#
# Behavior:
# - Runs quick checks + optional autofix (if enabled by env).
# - Executes the requested command.
# - On failure, writes a Codex prompt file you can paste into Codex/agent tooling.

repo=""
timeout="${OSDASH_RUN_TIMEOUT:-300}"
categories="${OSDASH_RUN_CATEGORIES:-lint,test}"
autofix="${OSDASH_RUN_AUTOFIX:-0}"
prompt_path="${OSDASH_CODEX_PROMPT_PATH:-}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)
      repo="${2:-}"; shift 2;;
    --timeout)
      timeout="${2:-}"; shift 2;;
    --categories)
      categories="${2:-}"; shift 2;;
    --)
      shift; break;;
    *)
      break;;
  esac
done

if [[ -z "$repo" ]]; then
  repo="$(pwd)"
fi

if [[ -z "$prompt_path" ]]; then
  prompt_path="$(cd "$repo" && pwd)/logs/osdash_autofix/codex-prompt.txt"
fi

python3 "/workspace/scripts/osd_autofix.py" \
  --repo "$repo" \
  --categories "$categories" \
  --timeout "$timeout" \
  $( [[ "$autofix" == "1" ]] && echo --autofix ) \
  --write-codex-prompt "$prompt_path" \
  || true

if [[ $# -eq 0 ]]; then
  echo "[osd_run] no command provided; checks only."
  exit 0
fi

echo "[osd_run] ▶ running in $repo: $*"
(cd "$repo" && "$@")
