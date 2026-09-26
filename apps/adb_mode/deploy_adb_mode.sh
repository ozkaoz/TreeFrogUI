#!/bin/bash
# Deploy the adb_mode app to a TreeFrogUI SD card (r36sx-hclinux 9-6f test).
# Usage: deploy_adb_mode.sh /mnt/sd-root
#
# Installs:
#   treefrog/adb_mode.sh   — gadget/ffs session script
#   treefrog/min_adbd      — prebuilt static MIPS daemon (see README.md)
#   treefrog/net_mode.sh   — dispatcher with the adb.mode flag (from ../net_mode)
#   adb.mode               — SD-root flag: enables ADB transport on "Network"
#
# The flag file is created by default (this IS the test enable); delete it to
# return the console to production NCM behaviour.
set -e
MNT="${1:?uso: deploy_adb_mode.sh /mnt/sd-root}"
DEST="$MNT/treefrog"
HERE="$(cd "$(dirname "$0")" && pwd)"
[ -f "$DEST/zhijack.sh" ] || { echo "not a TreeFrogUI SD: $MNT"; exit 1; }

install -m 0755 "$HERE/adb_mode.sh" "$DEST/adb_mode.sh"
install -m 0755 "$HERE/adbd" "$DEST/min_adbd"
install -m 0755 "$HERE/../net_mode/net_mode.sh" "$DEST/net_mode.sh"

touch "$MNT/adb.mode"

echo "adb_mode deployed to $DEST (flag: $MNT/adb.mode)"
