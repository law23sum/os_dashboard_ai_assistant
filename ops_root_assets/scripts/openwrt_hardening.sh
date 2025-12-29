#!/bin/sh
set -eu

TARGET="root@192.168.1.1"
WAN_DOWN_MBIT=""
WAN_UP_MBIT=""
SQM_IFACE="wan"
WIFI_ENCRYPTION="sae-mixed"
WIFI_COUNTRY="US"
APPLY=0

usage() {
  cat <<'USAGE'
Usage: openwrt_hardening.sh [options]

Options:
  --target user@host     Router SSH target (default: root@192.168.1.1)
  --wan-down-mbps N      Downstream bandwidth for SQM (Mbps)
  --wan-up-mbps N        Upstream bandwidth for SQM (Mbps)
  --sqm-interface name   Interface to shape (default: wan)
  --wifi-encryption mode Set wifi encryption (default: sae-mixed)
  --wifi-country code    Regulatory domain (default: US)
  --apply                Execute commands over SSH instead of printing
  -h, --help             Show this help

Without --apply the script prints the remote shell snippet so you can review it.
USAGE
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --target)
      TARGET="$2"; shift 2 ;;
    --wan-down-mbps)
      WAN_DOWN_MBIT="$2"; shift 2 ;;
    --wan-up-mbps)
      WAN_UP_MBIT="$2"; shift 2 ;;
    --sqm-interface)
      SQM_IFACE="$2"; shift 2 ;;
    --wifi-encryption)
      WIFI_ENCRYPTION="$2"; shift 2 ;;
    --wifi-country)
      WIFI_COUNTRY="$2"; shift 2 ;;
    --apply)
      APPLY=1; shift ;;
    -h|--help)
      usage; exit 0 ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 1 ;;
  esac
done

conv_mbps() {
  if [ -z "$1" ]; then
    echo 0
    return
  fi
  python3 - "$1" <<'PY'
import sys
val = float(sys.argv[1])
print(int(val * 1000))
PY
}

WAN_DOWN_KBIT=$(conv_mbps "$WAN_DOWN_MBIT")
WAN_UP_KBIT=$(conv_mbps "$WAN_UP_MBIT")

REMOTE_SCRIPT=$(cat <<REMOTE
set -euo pipefail
log() { echo "[openwrt-harden] \$1"; }

log "Applying base system/firewall defaults"
uci -q batch <<'UCI'
set system.@system[0].conloglevel='5'
set system.@system[0].log_size='256'
set firewall.@defaults[0].synflood_protect='1'
set firewall.@defaults[0].flow_offloading='1'
set firewall.@defaults[0].flow_offloading_hw='1'
set firewall.@defaults[0].drop_invalid='1'
set firewall.@defaults[0].fullcone='0'
set dhcp.@dnsmasq[0].dnssec='1'
set dhcp.@dnsmasq[0].filterwin2k='1'
set dhcp.@dnsmasq[0].localservice='1'
set uhttpd.main.redirect_https='1'
set uhttpd.main.rfc1918_filter='1'
set dropbear.@dropbear[0].PasswordAuth='off'
set dropbear.@dropbear[0].RootPasswordAuth='off'
set dropbear.@dropbear[0].Interface='lan'
UCI

log "Hardening wifi interfaces"
for section in \$(uci show wireless | awk -F= '/@wifi-device/{print \$1}'); do
  uci set "\$section.country"='${WIFI_COUNTRY}'
  uci set "\$section.disabled"='0'
  uci set "\$section.txpower"='20'
  uci set "\$section.channel"='auto'
done

for section in \$(uci show wireless | awk -F= '/@wifi-iface/{print \$1}'); do
  uci set "\$section.ieee80211w"='1'
  uci set "\$section.wpa_disable_eapol_key_retries"='1'
  uci set "\$section.encryption"='${WIFI_ENCRYPTION}'
  uci set "\$section.isolate"='0'
done

if [ ${WAN_DOWN_KBIT} -gt 0 ] && [ ${WAN_UP_KBIT} -gt 0 ]; then
  log "Configuring SQM (${SQM_IFACE})"
  if ! uci -q show sqm | grep -q '@queue\[0\]'; then
    uci add sqm queue >/dev/null
  fi
  uci set sqm.@queue[0].interface='${SQM_IFACE}'
  uci set sqm.@queue[0].download='${WAN_DOWN_KBIT}'
  uci set sqm.@queue[0].upload='${WAN_UP_KBIT}'
  uci set sqm.@queue[0].qdisc='cake'
  uci set sqm.@queue[0].script='piece_of_cake.qos'
  uci set sqm.@queue[0].linklayer='ethernet'
  uci set sqm.@queue[0].enabled='1'
fi

log "Commit + restart"
uci commit system
uci commit firewall
uci commit dhcp
uci commit dropbear
uci commit wireless
uci commit sqm >/dev/null 2>&1 || true
/etc/init.d/firewall restart
/etc/init.d/dnsmasq restart
/etc/init.d/dropbear restart
wifi reload
if [ -x /etc/init.d/sqm ] && [ ${WAN_DOWN_KBIT} -gt 0 ] && [ ${WAN_UP_KBIT} -gt 0 ]; then
  /etc/init.d/sqm enable >/dev/null 2>&1 || true
  /etc/init.d/sqm restart >/dev/null 2>&1 || true
fi
log "Done"
REMOTE
)

if [ "$APPLY" -eq 1 ]; then
  printf '%s\n' "[local] Connecting to $TARGET"
  ssh "$TARGET" "$REMOTE_SCRIPT"
else
  cat <<'NOTE'
# Review the commands below and run with --apply when ready.
NOTE
  printf '%s\n' "$REMOTE_SCRIPT"
fi
