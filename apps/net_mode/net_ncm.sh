#!/bin/sh
# net_ncm.sh — TreeFrogUI Net Mode. CDC-NCM gadget (3 EP: bulk IN + bulk OUT + intr IN).
# USB networking adapter for Windows 7+ (native CDC-NCM driver, no extra software).
# RAM shell: busybox + exit_watcher copied to /tmp (avoids SD/USB bus contention).
# B-button exit via usb_exit_watcher (SIGTERM).
# Blue screen: AVP firmware behavior (documented, not fixable from Linux).
LOG=/mnt/sdcard/NET_MODE_DEBUG.log
ROLE_PATH=/sys/devices/platform/soc/18844000.usb/musb-hdrc.0.auto/mode
UDC_NAME=musb-hdrc.0.auto
G=/sys/kernel/config/usb_gadget/ncm_net

log() { echo "$(date '+%H:%M:%S' 2>/dev/null || echo t) $*" >> "$LOG"; }

NET_EXIT=0
trap "NET_EXIT=1" TERM
restore() {
    rc=$?
    trap - EXIT INT TERM
    [ -n "$WATCHER_PID" ] && kill $WATCHER_PID 2>/dev/null
    killall telnetd 2>/dev/null
    if [ -d "$G" ]; then
        printf '\n' > "$G/UDC" 2>/dev/null
        sleep 1
        rm -f "$G/configs/c.1/ncm.usb0" 2>/dev/null
        rmdir "$G/configs/c.1/strings/0x409" "$G/configs/c.1" 2>/dev/null
        rmdir "$G/functions/ncm.usb0" "$G/strings/0x409" "$G" 2>/dev/null
    fi
    printf 'host\n' > "$ROLE_PATH" 2>/dev/null
    log "restore done rc=$rc"
    sync
    exit "$rc"
}
trap restore EXIT INT

: >> "$LOG"
log "=== NCM session uptime=$(cut -d' ' -f1 /proc/uptime) role=$(cat "$ROLE_PATH" 2>/dev/null) ==="

# configfs
mkdir -p /sys/kernel/config 2>/dev/null
mount -t configfs none /sys/kernel/config 2>/dev/null || true
[ -d /sys/kernel/config/usb_gadget ] || { log "FAIL: no configfs"; exit 1; }

# gadget
[ -d "$G" ] && { log "stale - cleaning"; restore 2>/dev/null; }
mkdir "$G" 2>>"$LOG" || { log "FAIL mkdir"; exit 1; }

printf '0x0525\n' > "$G/idVendor"
printf '0xa4a2\n' > "$G/idProduct"
printf '0x0200\n' > "$G/bcdUSB"
mkdir -p "$G/strings/0x409" "$G/configs/c.1/strings/0x409" 2>/dev/null
printf 'TreeFrogUI\n' > "$G/strings/0x409/manufacturer"
printf 'TreeFrogUI Network\n' > "$G/strings/0x409/product"
printf 'ncm\n' > "$G/configs/c.1/strings/0x409/configuration"
printf '250\n' > "$G/configs/c.1/MaxPower" 2>/dev/null

mkdir "$G/functions/ncm.usb0" 2>>"$LOG" || log "ncm exists"
ln -s "$G/functions/ncm.usb0" "$G/configs/c.1/ncm.usb0" 2>>"$LOG" || { log "FAIL link"; exit 1; }
log "gadget creado"

# role switch
ORIG_ROLE=$(cat "$ROLE_PATH" 2>/dev/null)
printf 'peripheral\n' > "$ROLE_PATH" 2>>"$LOG" || printf 'b_peripheral\n' > "$ROLE_PATH" 2>>"$LOG" || { log "FAIL role"; exit 1; }
log "role: $ORIG_ROLE -> peripheral"

n=0; while [ "$n" -lt 20 ] && [ ! -e "/sys/class/udc/$UDC_NAME" ]; do sleep 0.5; n=$((n+1)); done
[ -e "/sys/class/udc/$UDC_NAME" ] || { log "FAIL: UDC no aparecio"; exit 1; }
printf '%s\n' "$UDC_NAME" > "$G/UDC" 2>>"$LOG" || { log "FAIL UDC"; exit 1; }
log "UDC bound"

# la red
n=0; while [ "$n" -lt 20 ] && [ ! -e /sys/class/net/usb0 ]; do sleep 0.5; n=$((n+1)); done
if [ -e /sys/class/net/usb0 ]; then
    ifconfig usb0 192.168.137.2 netmask 255.255.255.0 up 2>>"$LOG" && log "usb0 UP" || log "FAIL ifconfig"
else
    log "FAIL: usb0 no aparecio"
fi

# RAM shell wrapper: busybox y exit_watcher en tmpfs.
# Sin esto, fork/exec lee del SD bind-mounted mientras el musb satura el bus.
mkdir -p /tmp/bin
cp /bin/busybox /tmp/bin/busybox 2>/dev/null
chmod +x /tmp/bin/busybox
echo '#!/tmp/bin/busybox sh' > /tmp/bin/sh
echo 'export PATH=/tmp/bin:/bin:/sbin:/usr/bin:/usr/sbin' >> /tmp/bin/sh
echo 'exec /tmp/bin/busybox sh' >> /tmp/bin/sh
chmod +x /tmp/bin/sh

# exit_watcher tambien en RAM
EWATCH="/mnt/sdcard/cubegm/usb_exit_watcher"
if [ -x "$EWATCH" ]; then
    cp "$EWATCH" /tmp/bin/exit_watcher 2>/dev/null
    chmod +x /tmp/bin/exit_watcher 2>/dev/null
    "$EWATCH" $$ >/dev/null 2>&1 &
    WATCHER_PID=$!
    log "exit_watcher started pid=$WATCHER_PID"
else
    log "WARN: exit_watcher no encontrado"
    WATCHER_PID=""
fi

# telnetd usa el shell wrapper en RAM
telnetd -l /tmp/bin/sh 2>>"$LOG" && log "telnetd OK (RAM shell)" || log "telnetd FAIL"

log "NCM READY - PC adapter IP 192.168.137.1, telnet 192.168.137.2"
sync

# bloquear hasta B exit o cable unplug
configured=0
while :; do
    if [ "$NET_EXIT" = 1 ]; then
        log "B exit"
        break
    fi
    state=$(cat "/sys/class/udc/$UDC_NAME/state" 2>/dev/null || echo detached)
    [ "$state" = "configured" ] && configured=1
    if [ "$configured" = 1 ] && [ "$state" = "not attached" ]; then
        log "PC disconnected"
        break
    fi
    sleep 1
done
log "saliendo"
