#!/bin/bash
# Automates SSH setup, dotfile syncing, and Homebrew mirroring from the local Mac to a remote Mac.
# The script is intended to be run on the source Mac (e.g., MacBook Pro) and targets a remote Mac (e.g., Mac mini).

set -euo pipefail

readonly DEFAULT_SSH_KEY_PATH="${HOME}/.ssh/id_ed25519"
readonly DEFAULT_HOST_ALIAS="mac-mini"
readonly DEFAULT_BREWFILE="${HOME}/Brewfile.mac_migration"
readonly DEFAULT_SYNC_ITEMS=".zshrc .zprofile .zshenv .bashrc .bash_profile .config .gitconfig"

REMOTE_USER=""
REMOTE_HOST=""
SSH_KEY_PATH="${DEFAULT_SSH_KEY_PATH}"
HOST_ALIAS="${DEFAULT_HOST_ALIAS}"
BREWFILE_PATH="${DEFAULT_BREWFILE}"
SYNC_ITEMS="${DEFAULT_SYNC_ITEMS}"
SKIP_BREW=0
SKIP_DOTFILES=0

usage() {
  cat <<'EOF'
Usage: mac_sync_setup.sh --remote-user <username> --remote-host <host_or_ip> [options]

Options:
  --remote-user <user>     Remote macOS account name to connect as (required).
  --remote-host <host>     Remote hostname or IP (required).
  --ssh-key <path>         SSH private key path to use or create (default: ~/.ssh/id_ed25519).
  --host-alias <alias>     Alias to add to ~/.ssh/config for quick SSH access (default: mac-mini).
  --brewfile <path>        Path for generated Brewfile (default: ~/Brewfile.mac_migration).
  --sync-items <list>      Quoted space-separated list of files/dirs to rsync (default: standard shells + ~/.config).
  --skip-brew              Skip Homebrew dump/install steps.
  --skip-dotfiles          Skip rsync of dotfiles/config directories.
  --help                   Show this help and exit.

Example:
  ./mac_sync_setup.sh \
    --remote-user chris \
    --remote-host 192.168.254.148 \
    --host-alias macmini \
    --sync-items ".zshrc .config .gitconfig"
EOF
}

log() {
  printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"
}

warn() {
  printf '[%s] WARN: %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" >&2
}

error() {
  printf '[%s] ERROR: %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" >&2
  exit 1
}

require_command() {
  local cmd="$1"
  command -v "${cmd}" >/dev/null 2>&1 || error "Required command '${cmd}' not found. Please install it first."
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --remote-user)
        REMOTE_USER="$2"
        shift 2
        ;;
      --remote-host)
        REMOTE_HOST="$2"
        shift 2
        ;;
      --ssh-key)
        SSH_KEY_PATH="$2"
        shift 2
        ;;
      --host-alias)
        HOST_ALIAS="$2"
        shift 2
        ;;
      --brewfile)
        BREWFILE_PATH="$2"
        shift 2
        ;;
      --sync-items)
        SYNC_ITEMS="$2"
        shift 2
        ;;
      --skip-brew)
        SKIP_BREW=1
        shift
        ;;
      --skip-dotfiles)
        SKIP_DOTFILES=1
        shift
        ;;
      --help|-h)
        usage
        exit 0
        ;;
      *)
        error "Unknown argument: $1"
        ;;
    esac
  done

  [[ -n "${REMOTE_USER}" ]] || error "--remote-user is required."
  [[ -n "${REMOTE_HOST}" ]] || error "--remote-host is required."
}

generate_ssh_key() {
  local key_path="$1"

  if [[ -f "${key_path}" ]]; then
    log "SSH key ${key_path} already exists; skipping generation."
    return
  fi

  log "Generating new Ed25519 SSH key at ${key_path}..."
  ssh-keygen -t ed25519 -f "${key_path}" -C "mac_migration_$(hostname)" -N "" || error "ssh-keygen failed."
}

copy_ssh_key() {
  local key_path="$1"
  local pub_key="${key_path}.pub"

  [[ -f "${pub_key}" ]] || error "Public key ${pub_key} not found. Key generation likely failed."

  if command -v ssh-copy-id >/dev/null 2>&1; then
    log "Copying SSH key to ${REMOTE_USER}@${REMOTE_HOST} via ssh-copy-id..."
    ssh-copy-id -i "${pub_key}" "${REMOTE_USER}@${REMOTE_HOST}" || error "ssh-copy-id failed."
  else
    log "ssh-copy-id not available; falling back to manual authorized_keys append."
    cat "${pub_key}" | ssh "${REMOTE_USER}@${REMOTE_HOST}" "mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys" \
      || error "Manual key copy failed."
  fi
}

ensure_host_alias() {
  local alias="$1"
  local ssh_config="${HOME}/.ssh/config"
  local alias_block

  alias_block=$(cat <<EOF
Host ${alias}
    HostName ${REMOTE_HOST}
    User ${REMOTE_USER}
    IdentityFile ${SSH_KEY_PATH}
    IdentitiesOnly yes
    ServerAliveInterval 60
    ServerAliveCountMax 3
EOF
)

  mkdir -p "${HOME}/.ssh"
  touch "${ssh_config}"
  chmod 600 "${ssh_config}"

  if grep -qE "^Host[[:space:]]+${alias}([[:space:]]|\$)" "${ssh_config}"; then
    log "Host alias '${alias}' already exists in ${ssh_config}; verifying settings."
    if ! grep -A4 -q "Host ${alias}" "${ssh_config}" | grep -q "HostName ${REMOTE_HOST}"; then
      warn "Existing Host ${alias} entry uses a different HostName. Please adjust manually if needed."
    fi
    return
  fi

  log "Adding Host ${alias} entry to ${ssh_config}."
  {
    echo ""
    echo "${alias_block}"
  } >> "${ssh_config}"
}

generate_brewfile() {
  local brewfile="$1"

  if [[ "${SKIP_BREW}" -eq 1 ]]; then
    log "Skipping Homebrew bundle dump as requested."
    return
  fi

  require_command brew
  log "Dumping current Homebrew bundle to ${brewfile}..."
  brew bundle dump --file "${brewfile}" --describe --force || warn "Failed to create Brewfile. Check Homebrew installation."
}

push_brewfile() {
  local brewfile="$1"

  [[ "${SKIP_BREW}" -eq 0 ]] || return
  [[ -f "${brewfile}" ]] || { warn "Brewfile ${brewfile} not found; skipping upload."; return; }

  log "Copying Brewfile to remote host..."
  scp "${brewfile}" "${REMOTE_USER}@${REMOTE_HOST}:~/mac_migration/Brewfile" \
    || warn "Failed to copy Brewfile to remote host."
}

remote_bootstrap_brew() {
  [[ "${SKIP_BREW}" -eq 0 ]] || return

  log "Running remote Homebrew bootstrap..."
  ssh "${REMOTE_USER}@${REMOTE_HOST}" /bin/bash <<'EOF'
set -euo pipefail
mkdir -p ~/mac_migration
BUNDLE_PATH="${HOME}/mac_migration/Brewfile"

if ! command -v xcode-select >/dev/null 2>&1; then
  echo "[Remote] xcode-select not found. Install Command Line Tools manually before running again."
else
  if ! xcode-select -p >/dev/null 2>&1; then
    echo "[Remote] Command Line Tools missing. Run 'xcode-select --install' on the remote Mac and rerun this script."
  fi
fi

if ! command -v brew >/dev/null 2>&1; then
  echo "[Remote] Homebrew not detected; installing non-interactively..."
  NONINTERACTIVE=1 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" || {
    echo "[Remote] Homebrew installation failed. Install manually and rerun." >&2
    exit 1
  }
  eval "$(/opt/homebrew/bin/brew shellenv 2>/dev/null || /usr/local/bin/brew shellenv)"
else
  eval "$(/opt/homebrew/bin/brew shellenv 2>/dev/null || /usr/local/bin/brew shellenv)"
fi

if [[ -f "${BUNDLE_PATH}" ]]; then
  echo "[Remote] Applying Brew bundle..."
  brew bundle --file "${BUNDLE_PATH}" || {
    echo "[Remote] Brew bundle encountered errors. Review output above." >&2
  }
else
  echo "[Remote] Brewfile not found at ${BUNDLE_PATH}; skipping bundle install."
fi
EOF
}

rsync_dotfiles() {
  [[ "${SKIP_DOTFILES}" -eq 0 ]] || { log "Skipping dotfile sync as requested."; return; }

  require_command rsync
  local item
  local rsync_args=(-avh --progress)

  log "Syncing dotfiles/config items to remote host..."

  for item in ${SYNC_ITEMS}; do
    local source_path
    source_path="${HOME}/${item}"

    if [[ ! -e "${source_path}" ]]; then
      warn "Skipping ${source_path}; file or directory not found."
      continue
    fi

    log "Rsync ${source_path} -> ${REMOTE_USER}@${REMOTE_HOST}:~/${item}"
    rsync "${rsync_args[@]}" "${source_path}" "${REMOTE_USER}@${REMOTE_HOST}:~/${item}" || \
      warn "Rsync failed for ${source_path}. Check remote permissions."
  done
}

verify_connection() {
  log "Verifying SSH connection to ${REMOTE_USER}@${REMOTE_HOST}..."
  ssh -o BatchMode=yes -o ConnectTimeout=5 "${REMOTE_USER}@${REMOTE_HOST}" "echo 'Remote connection OK'" \
    || error "SSH connection check failed. Ensure the remote host is reachable and SSH is enabled."
}

main() {
  parse_args "$@"

  require_command ssh
  require_command scp

  generate_ssh_key "${SSH_KEY_PATH}"
  copy_ssh_key "${SSH_KEY_PATH}"
  ensure_host_alias "${HOST_ALIAS}"
  verify_connection
  generate_brewfile "${BREWFILE_PATH}"
  push_brewfile "${BREWFILE_PATH}"
  remote_bootstrap_brew
  rsync_dotfiles

  log "Migration steps complete. You can now SSH using: ssh ${HOST_ALIAS}"
  if [[ "${SKIP_BREW}" -eq 0 ]]; then
    log "Remote Brewfile located at ~/mac_migration/Brewfile."
  fi
  if [[ "${SKIP_DOTFILES}" -eq 0 ]]; then
    log "Dotfiles synced. Consider reviewing remote ~/.config for conflicts."
  fi
}

main "$@"
