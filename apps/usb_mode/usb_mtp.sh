#!/bin/sh
# TreeFrogUI USB Mode entry. Flag net.mode en la raiz SD -> modo red (apps/net_mode);
# sin flag -> MTP clasico (upstream verbatim). Dentro de net_mode: ncm.mode selecciona
# NCM (subclass 0D); default = ECM (subclass 06, Windows 7+ nativo, sin pantalla azul).
[ -f /mnt/sdcard/log.txt ] && echo "usb_mtp mode=$( [ -f /mnt/sdcard/net.mode ] && echo net || echo mtp)" >> /mnt/sdcard/USB_MODE_INVOKE.log 2>/dev/null
if [ -f /mnt/sdcard/net.mode ]; then
    exec "$(dirname "$0")/net_mode.sh"
fi
exec "$(dirname "$0")/usb_mode.sh" mtp
