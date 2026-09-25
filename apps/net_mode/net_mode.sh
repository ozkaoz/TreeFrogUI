#!/bin/sh
# TreeFrogUI Net Mode — dispatcher (daemon toggle by default).
# La entrada NETWORK del menu frogui llama este script; cada invocacion es un
# TOGGLE: red arriba (daemon, menu navegable con internet) <-> red abajo.
#   session.mode flag en la SD -> sesion clasica bloqueante (tests).
#   ncm.mode -> NCM explicito; ppp.mode/ecm.mode -> experimental.
LOG=/mnt/sdcard/NET_MODE_DEBUG.log
echo "$(date '+%H:%M:%S' 2>/dev/null) net_mode invoked" >> "$LOG" 2>/dev/null
MODE="daemon"
[ -f /mnt/sdcard/session.mode ] && MODE="session"
if [ -f /mnt/sdcard/ppp.mode ]; then
    exec "$(dirname "$0")/net_ppp.sh"
fi
if [ -f /mnt/sdcard/ecm.mode ]; then
    exec "$(dirname "$0")/net_ecm.sh"
fi
exec "$(dirname "$0")/net_ncm.sh" "$MODE"
