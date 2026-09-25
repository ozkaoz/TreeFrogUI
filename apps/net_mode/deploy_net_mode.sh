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

# usb_mtp.sh: UPSTREAM VERBATIM (USB Mode = MTP always). The Network menu
# entry (frogui core) launches net_mode.sh directly — first-class (AGENTS §15
# r36sx-hclinux). The legacy net.mode SD-root flag is retired: if present on
# an old card, remove it (it would no longer have any effect).
cat > "$DEST/usb_mtp.sh" << 'SHIM'
#!/bin/sh
# TreeFrogUI's user-facing USB mode entry point.  MTP keeps the SD mounted.
exec "$(dirname "$0")/usb_mode.sh" mtp
SHIM
chmod 0755 "$DEST/usb_mtp.sh"

echo "net_mode deployed to $DEST"
