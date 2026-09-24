#!/bin/sh
# net_ecm.sh — USB networking via CDC-ECM (subclass 06, NOT NCM subclass 0D).
# Windows 7+ native network adapter, same result as NCM but different CDC subclass.
# Root fix for: blue screen (AVP reacts to NCM subclass 0D) + SD/USB bus contention
# (AVP locks bus during blue overlay, breaking fork/exec from SD bind mounts).
# ACM (02) proved no blue screen — ECM (06) should behave the same.
# Shell: busybox + exit_watcher in RAM (/tmp/bin), telnetd uses RAM wrapper.
LOG=/mnt/sdcard/NET_MODE_DEBUG.log
ROLE_PATH=/sys/devices/platform/soc/18844000.usb/musb-hdrc.0.auto/mode
UDC_NAME=musb-hdrc.0.auto
G=/sys/kernel/config/usb_gadget/ecm_net

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
        rm -f "$G/configs/c.1/ecm.usb0" 2>/dev/null
        rmdir "$G/configs/c.1/strings/0x409" "$G/configs/c.1" 2>/dev/null
        rmdir "$G/functions/ecm.usb0" "$G/strings/0x409" "$G" 2>/dev/null
    fi
    printf 'host\n' > "$ROLE_PATH" 2>/dev/null
    log "restore done rc=$rc"
    sync
    exit "$rc"
}
trap restore EXIT INT

: >> "$LOG"
log "=== ECM session uptime=$(cut -d' ' -f1 /proc/uptime) ==="

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
printf 'ecm\n' > "$G/configs/c.1/strings/0x409/configuration"
printf '250\n' > "$G/configs/c.1/MaxPower" 2>/dev/null

mkdir "$G/functions/ecm.usb0" 2>>"$LOG" || log "ecm exists"
ln -s "$G/functions/ecm.usb0" "$G/configs/c.1/ecm.usb0" 2>>"$LOG" || { log "FAIL link"; exit 1; }
log "ECM gadget creado (subclass 06)"

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

# RAM shell: busybox + exit_watcher + symlinks en tmpfs.
mkdir -p /tmp/bin
cp /bin/busybox /tmp/bin/busybox 2>/dev/null
chmod +x /tmp/bin/busybox
# Symlinks para que 'ls', 'cat', etc. usen busybox de RAM
for app in ls cat cp mv rm mkdir rmdir echo printf grep find sed awk sort head tail wc ps kill top df du du mount umount ifconfig ping netstat free dmesg uptime uname lsmod insmod rmmod modinfo sleep env which id whoami hostname date tar gzip gunzip vi touch chmod chown ln readlink stat file dd sync reboot poweroff halt shutdown; do
    [ -e "/tmp/bin/busybox" ] && ln -sf busybox "/tmp/bin/$app" 2>/dev/null
done
# PATH override: RAM primero
printf '#!/tmp/bin/busybox sh\nexport PATH=/tmp/bin:/bin:/sbin:/usr/bin:/usr/sbin\nexec /tmp/bin/busybox sh\n' > /tmp/bin/sh
chmod +x /tmp/bin/sh
# Windows: exit_watcher en RAM
EWATCH="/mnt/sdcard/cubegm/usb_exit_watcher"
if [ -x "$EWATCH" ]; then
    cp "$EWATCH" /tmp/bin/exit_watcher 2>/dev/null
    chmod +x /tmp/bin/exit_watcher
    "$EWATCH" $$ >/dev/null 2>&1 &
    WATCHER_PID=$!
    log "exit_watcher started pid=$WATCHER_PID"
else
    log "WARN: exit_watcher no encontrado"
    WATCHER_PID=""
fi
telnetd -l /tmp/bin/sh 2>>"$LOG" && log "telnetd OK (RAM shell)" || log "telnetd FAIL"
log "ECM READY - PC: adapter 192.168.137.1, telnet 192.168.137.2"
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
