#!/bin/bash
# Deploy the net_mode app to a TreeFrogUI SD card.
# Usage: deploy_net_mode.sh /mnt/sd-root
set -e
MNT="${1:?uso: deploy_net_mode.sh /mnt/sd-root}"
DEST="$MNT/treefrog"
HERE="$(cd "$(dirname "$0")" && pwd)"
[ -f "$DEST/zhijack.sh" ] || { echo "not a TreeFrogUI SD: $MNT"; exit 1; }

for f in net_mode.sh net_ecm.sh net_ncm.sh net_ppp.sh net_rndis.sh net_serial.sh net_wifi.sh; do
    install -m 0755 "$HERE/$f" "$DEST/$f"
done

# usb_mtp.sh dispatcher: net.mode -> net_mode.sh, otherwise classic MTP.
cat > "$DEST/usb_mtp.sh" << 'SHIM'
#!/bin/sh
# TreeFrogUI USB Mode entry. Flag net.mode en la raiz SD -> modo red (apps/net_mode);
# sin flag -> MTP clasico (upstream verbatim). Dentro de net_mode: default = NCM
# (adaptador de red; produccion, ADR-015 r36sx-hclinux); ppp.mode/ecm.mode = experimental.
[ -f /mnt/sdcard/log.txt ] && echo "usb_mtp mode=$( [ -f /mnt/sdcard/net.mode ] && echo net || echo mtp)" >> /mnt/sdcard/USB_MODE_INVOKE.log 2>/dev/null
if [ -f /mnt/sdcard/net.mode ]; then
    exec "$(dirname "$0")/net_mode.sh"
fi
exec "$(dirname "$0")/usb_mode.sh" mtp
SHIM
chmod 0755 "$DEST/usb_mtp.sh"

echo "net_mode deployed to $DEST"
