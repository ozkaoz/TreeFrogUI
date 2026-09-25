#!/bin/sh
# TreeFrogUI Net Mode — dispatcher.
# Default: NCM (adaptador de red nativo en Windows). PRODUCCION (ADR-015 del
# repo r36sx-hclinux): CUALQUIER networking activo dispara el overlay azul del
# AVP (display-only; el kernel y la red siguen vivos debajo) — limitacion
# aceptada de la plataforma. NCM es el transporte validado fisicamente.
#   ppp.mode -> PPP sobre CDC-ACM (experimental; TAMBIEN dispara el azul).
#   ecm.mode -> ECM (experimental).
LOG=/mnt/sdcard/NET_MODE_DEBUG.log
echo "$(date '+%H:%M:%S' 2>/dev/null) net_mode invoked" >> "$LOG" 2>/dev/null
if [ -f /mnt/sdcard/ppp.mode ]; then
    exec "$(dirname "$0")/net_ppp.sh"
fi
if [ -f /mnt/sdcard/ecm.mode ]; then
    exec "$(dirname "$0")/net_ecm.sh"
fi
exec "$(dirname "$0")/net_ncm.sh"
