#!/bin/sh
# net_ppp.sh — TreeFrogUI Net Mode: PPP sobre CDC-ACM (EXPERIMENTAL — refutado).
#
# Hipotesis original: networking por serial (sin gadget de red) evitaria el
# overlay azul del AVP. TEST FISICO 2026-09-24: REFUTADO — la sesion PPP
# TAMBIEN dispara el azul (solo con pppd corriendo y LCP sin respuesta fue
# suficiente). El overlay correlaciona con networking ACTIVO en cualquier forma
# (gadget CDC-network o pppd sobre ACM); el serial ACM puro (shell interactivo
# sin pppd) NO lo dispara. Produccion: net_ncm.sh (ADR-015 r36sx-hclinux).
#
# Consola: ppp0 = 192.168.137.2 (peer .1) + telnetd.  PC: dial-up (modem nulo)
# sobre el COM del ACM -> 192.168.137.1; telnet 192.168.137.2.
# B o desconexion del cable termina la sesion.

LOG=/mnt/sdcard/NET_MODE_DEBUG.log
ROLE_PATH=/sys/devices/platform/soc/18844000.usb/musb-hdrc.0.auto/mode
UDC_NAME=musb-hdrc.0.auto
G=/sys/kernel/config/usb_gadget/ppp_serial
TTY=/dev/ttyGS0
PPPD=/usr/sbin/pppd
PPP_LOG=/mnt/sdcard/PPP_DEBUG.log
LOCAL_IP=192.168.137.2
PEER_IP=192.168.137.1

log() { echo "$(date '+%H:%M:%S' 2>/dev/null || echo t) $*" >> "$LOG"; }

NET_EXIT=0
PPPD_PID=""
WATCHER_PID=""
trap "NET_EXIT=1" TERM

restore() {
    rc=$?
    trap - EXIT INT TERM
    [ -n "$PPPD_PID" ] && kill "$PPPD_PID" 2>/dev/null
    [ -n "$WATCHER_PID" ] && kill "$WATCHER_PID" 2>/dev/null
    killall telnetd 2>/dev/null
    if [ -d "$G" ]; then
        printf '\n' > "$G/UDC" 2>/dev/null
        sleep 1
        rm -f "$G/configs/c.1/acm.usb0" 2>/dev/null
        rmdir "$G/configs/c.1/strings/0x409" "$G/configs/c.1" 2>/dev/null
        rmdir "$G/functions/acm.usb0" "$G/strings/0x409" "$G" 2>/dev/null
    fi
    printf 'host\n' > "$ROLE_PATH" 2>/dev/null
    log "restore done rc=$rc"
    sync
    exit "$rc"
}
trap restore EXIT INT

: >> "$LOG"
log "=== PPP session uptime=$(cut -d' ' -f1 /proc/uptime) ==="

# tool presente?
if [ ! -x "$PPPD" ]; then
    log "FAIL: no existe $PPPD (desplegar pppd al runtime)"
    exit 1
fi

# configfs
mkdir -p /sys/kernel/config 2>/dev/null
mount -t configfs none /sys/kernel/config 2>/dev/null || true
[ -d /sys/kernel/config/usb_gadget ] || { log "FAIL: no configfs"; exit 1; }

# gadget CDC-ACM
[ -d "$G" ] && { log "stale - cleaning"; restore 2>/dev/null; }
mkdir "$G" 2>>"$LOG" || { log "FAIL mkdir"; exit 1; }
printf '0x02\n' > "$G/bDeviceClass" 2>/dev/null
printf '0x00\n' > "$G/bDeviceSubClass" 2>/dev/null
printf '0x00\n' > "$G/bDeviceProtocol" 2>/dev/null
printf '0x0525\n' > "$G/idVendor"
printf '0xa4a7\n' > "$G/idProduct"
mkdir -p "$G/strings/0x409" "$G/configs/c.1/strings/0x409" 2>/dev/null
printf 'TreeFrogUI\n' > "$G/strings/0x409/manufacturer"
printf 'TreeFrogUI PPP Link\n' > "$G/strings/0x409/product"
printf 'ppp\n' > "$G/configs/c.1/strings/0x409/configuration"
printf '250\n' > "$G/configs/c.1/MaxPower" 2>/dev/null
mkdir "$G/functions/acm.usb0" 2>>"$LOG" || log "acm exists"
ln -s "$G/functions/acm.usb0" "$G/configs/c.1/acm.usb0" 2>>"$LOG" || { log "FAIL link"; exit 1; }
log "gadget ACM creado"

# role switch
ORIG_ROLE=$(cat "$ROLE_PATH" 2>/dev/null)
printf 'peripheral\n' > "$ROLE_PATH" 2>>"$LOG" || printf 'b_peripheral\n' > "$ROLE_PATH" 2>>"$LOG" || { log "FAIL role"; exit 1; }
log "role: $ORIG_ROLE -> peripheral"

n=0; while [ "$n" -lt 20 ] && [ ! -e "/sys/class/udc/$UDC_NAME" ]; do sleep 0.5; n=$((n+1)); done
printf '%s\n' "$UDC_NAME" > "$G/UDC" 2>>"$LOG" || { log "FAIL UDC"; exit 1; }
log "UDC bound"

# esperar ttyGS0
n=0; while [ "$n" -lt 30 ] && [ ! -e "$TTY" ]; do sleep 0.5; n=$((n+1)); done
[ -e "$TTY" ] || { log "FAIL: $TTY no aparecio"; exit 1; }
log "$TTY ready"

# RAM shell + telnetd (shell remoto una vez que PPP levante)
mkdir -p /tmp/bin
cp /bin/busybox /tmp/bin/busybox 2>/dev/null
chmod +x /tmp/bin/busybox 2>/dev/null
printf '#!/tmp/bin/busybox sh\nexport PATH=/tmp/bin:/bin:/sbin:/usr/bin:/usr/sbin\nexec /tmp/bin/busybox sh\n' > /tmp/bin/sh
chmod +x /tmp/bin/sh
telnetd -l /tmp/bin/sh 2>>"$LOG" && log "telnetd OK (RAM shell)" || log "telnetd FAIL"

# exit_watcher (B) en RAM
EWATCH="/mnt/sdcard/treefrog/usb_exit_watcher"
if [ -x "$EWATCH" ]; then
    cp "$EWATCH" /tmp/bin/exit_watcher 2>/dev/null
    chmod +x /tmp/bin/exit_watcher 2>/dev/null
    "$EWATCH" $$ >/dev/null 2>&1 &
    WATCHER_PID=$!
    log "exit_watcher started pid=$WATCHER_PID"
fi

# PPP sobre el tty del gadget. local=sinstema de modem, noauth, nolock (sin /var/lock).
: > "$PPP_LOG"
"$PPPD" "$TTY" 115200 "$LOCAL_IP:$PEER_IP" local noauth nolock nodetach persist maxfail 0 debug logfile "$PPP_LOG" &
PPPD_PID=$!
log "pppd started pid=$PPPD_PID (local=$LOCAL_IP peer=$PEER_IP)"
log "PPP READY - PC: dial-up sobre el COM del ACM -> IP $PEER_IP, telnet $LOCAL_IP"
sync

# bloquear hasta B exit o cable unplug
configured=0
while :; do
    if [ "$NET_EXIT" = 1 ]; then log "B exit"; break; fi
    state=$(cat "/sys/class/udc/$UDC_NAME/state" 2>/dev/null || echo detached)
    [ "$state" = "configured" ] && configured=1
    if [ "$configured" = 1 ] && [ "$state" = "not attached" ]; then log "PC disconnected"; break; fi
    kill -0 "$PPPD_PID" 2>/dev/null || { log "pppd exited"; break; }
    sleep 1
done
log "saliendo"
