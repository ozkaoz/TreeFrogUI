#!/bin/sh
# TreeFrogUI ADB Mode — USB FunctionFS + minimal adbd (r36sx-hclinux 9-6f)
#
# Hypothesis under test: FunctionFS exposes a vendor-specific interface
# (class 0xFF, like MTP which does NOT trigger the AVP blue overlay) and
# carries an interactive shell (same traffic profile as CDC-ACM serial,
# proven overlay-free). No netdev, no u_ether, no pppd — "networking" in
# any active form is the known overlay trigger (ADR-015).
#
# Gadget: single function ffs.adb (2 bulk EPs + ep0 = 3 EPs — fits the
# MUSB 4-EP budget). The ADB daemon (min_adbd) must mount functionfs and
# claim the endpoints BEFORE the UDC bind, so the bind is retried until
# the daemon is ready.
#
# Modes: (no arg) blocking session (B button / cable unplug = exit)
#        stop             teardown (used by restore and re-entry)
#
# Selected via the "adb.mode" flag on the SD root (net_mode.sh dispatcher),
# i.e. this is an EXPERIMENT transport, not production.
LOG=/mnt/sdcard/ADB_MODE_DEBUG.log
ROLE_PATH=/sys/devices/platform/soc/18844000.usb/musb-hdrc.0.auto/mode
UDC_NAME=musb-hdrc.0.auto
G=/sys/kernel/config/usb_gadget/adb_ffs
FFS=/dev/ffs-adb
ADBD="$(dirname "$0")/min_adbd"

log() { echo "$(date '+%H:%M:%S' 2>/dev/null || echo t) $*" >> "$LOG"; }

teardown_gadget() {
    # order matters: unbind UDC -> kill daemon -> umount ffs -> remove tree
    if [ -d "$G" ]; then
        printf '\n' > "$G/UDC" 2>/dev/null
        sleep 1
    fi
    killall min_adbd 2>/dev/null
    sleep 1
    umount "$FFS" 2>/dev/null
    if [ -d "$G" ]; then
        rm -f "$G/configs/c.1/ffs.adb" 2>/dev/null
        rmdir "$G/configs/c.1/strings/0x409" "$G/configs/c.1" 2>/dev/null
        rmdir "$G/functions/ffs.adb" "$G/strings/0x409" "$G" 2>/dev/null
    fi
}

restore() {
    rc=$?
    trap - EXIT INT TERM
    [ -n "$WATCHER_PID" ] && kill "$WATCHER_PID" 2>/dev/null
    teardown_gadget
    printf 'host\n' > "$ROLE_PATH" 2>/dev/null
    log "restore done rc=$rc"
    sync
    exit "$rc"
}

# ---- stop ----
if [ "${1:-}" = "stop" ]; then
    log "stop requested"
    teardown_gadget
    printf 'host\n' > "$ROLE_PATH" 2>/dev/null
    log "stop done"
    sync
    exit 0
fi

NET_EXIT=0
trap "NET_EXIT=1" TERM
trap restore EXIT INT

: >> "$LOG"
log "=== ADB(ffs) session uptime=$(cut -d' ' -f1 /proc/uptime) ==="

# configfs
mkdir -p /sys/kernel/config 2>/dev/null
mount -t configfs none /sys/kernel/config 2>/dev/null || true
[ -d /sys/kernel/config/usb_gadget ] || { log "FAIL: no configfs"; exit 1; }

# stale state from a previous run?
if [ -d "$G" ] || grep -q " $FFS " /proc/mounts 2>/dev/null; then
    log "stale state - cleaning"
    "$0" stop
    sleep 1
fi

# gadget (IDs: Google vendor, classic android adb product — adb matches by
# interface class ff/42/01 anyway)
mkdir "$G" 2>>"$LOG" || { log "FAIL mkdir gadget"; exit 1; }
printf '0x18d1\n' > "$G/idVendor"
printf '0x4EE2\n' > "$G/idProduct"
printf '0x0200\n' > "$G/bcdUSB"
mkdir -p "$G/strings/0x409" "$G/configs/c.1/strings/0x409" 2>/dev/null
printf 'TreeFrogUI\n' > "$G/strings/0x409/manufacturer"
printf 'TreeFrogUI ADB (FunctionFS)\n' > "$G/strings/0x409/product"
printf 'adb\n' > "$G/configs/c.1/strings/0x409/configuration"
printf '250\n' > "$G/configs/c.1/MaxPower" 2>/dev/null

# ffs function + config link
mkdir "$G/functions/ffs.adb" 2>>"$LOG" || log "ffs.adb exists"
ln -s "$G/functions/ffs.adb" "$G/configs/c.1/ffs.adb" 2>>"$LOG" || { log "FAIL link"; exit 1; }
log "gadget creado (ff/42/01, 2 bulk eps)"

# functionfs mount + daemon (RAM copy — avoid SD reads during USB activity)
mkdir -p "$FFS" 2>>"$LOG"
mount -t functionfs adb "$FFS" 2>>"$LOG" || { log "FAIL mount functionfs"; exit 1; }
mkdir -p /tmp/bin 2>/dev/null
cp "$ADBD" /tmp/bin/min_adbd 2>>"$LOG" && chmod +x /tmp/bin/min_adbd
/tmp/bin/min_adbd "$FFS" >> "$LOG" 2>&1 &
ADBD_PID=$!
log "min_adbd started pid=$ADBD_PID"

# role switch to peripheral
ORIG_ROLE=$(cat "$ROLE_PATH" 2>/dev/null)
printf 'peripheral\n' > "$ROLE_PATH" 2>>"$LOG" || printf 'b_peripheral\n' > "$ROLE_PATH" 2>>"$LOG" || { log "FAIL role"; exit 1; }
log "role: $ORIG_ROLE -> peripheral"

# UDC bind — retried: min_adbd must open ep0/ep1/ep2 first (ffs activation)
n=0
bound=0
while [ "$n" -lt 30 ]; do
    printf '%s\n' "$UDC_NAME" > "$G/UDC" 2>/dev/null && { bound=1; break; }
    n=$((n+1))
    sleep 0.5
done
[ "$bound" = 1 ] || { log "FAIL UDC bind after $n tries"; exit 1; }
log "UDC bound (tries=$n)"

# exit watcher (B button)
EWATCH="/mnt/sdcard/treefrog/usb_exit_watcher"
WATCHER_PID=""
if [ -x "$EWATCH" ]; then
    "$EWATCH" $$ >/dev/null 2>&1 &
    WATCHER_PID=$!
    log "exit_watcher started pid=$WATCHER_PID"
else
    log "WARN: exit_watcher no encontrado"
fi

log "ADB READY — PC: 'adb kill-server; adb devices' (expected: R36SX0001 device)"
sync

# block until B exit or cable unplug
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
