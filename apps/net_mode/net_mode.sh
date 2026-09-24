#!/bin/sh
# TreeFrogUI Net Mode — dispatcher.
# Default: ECM (CDC-ECM subclass 06, different from NCM subclass 0D).
# ncm.mode → NCM. Default → ECM (no blue screen expected).
LOG=/mnt/sdcard/NET_MODE_DEBUG.log
echo "$(date '+%H:%M:%S' 2>/dev/null) net_mode invoked" >> "$LOG" 2>/dev/null
if [ -f /mnt/sdcard/ncm.mode ]; then
    exec "$(dirname "$0")/net_ncm.sh"
fi
exec "$(dirname "$0")/net_ecm.sh"
