# TreeFrogUI ADB Mode: FunctionFS shell/debug (9-6f)

USB **ADB** transport for the R36SX console using **FunctionFS** — a
r36sx-hclinux 9-6f experiment (platform side: kernel fragment + evidence in
that repo; this app is the userspace stack side per AGENTS §15).

## Why

The AVP firmware paints a blue overlay when it sees **active networking in any
form** (NCM/ECM/RNDIS gadget, or pppd over ACM — ADR-015). MTP (class 0xFF,
vendor-specific) and the raw CDC-ACM serial shell are overlay-free. FunctionFS
lets userspace describe a **vendor-specific** interface (0xFF/0x42/0x01 —
plain ADB) with **no netdev and no u_ether**, carrying an interactive shell:
the same traffic profile as the proven-overlay-free ACM serial shell. If the
hypothesis holds, `adb shell` becomes the first overlay-free remote shell
that Windows can use without a COM-port terminal.

## Layout

| File | What |
|---|---|
| `min_adbd.c` | Minimal ADB daemon: ffs V2 descriptors (ff/42/01, 2 bulk EPs) + **empty STRINGS block (the ffs state machine requires the strings phase before ep1/ep2 files exist — f_fs.c:330-395; a zero-count block is accepted when descriptors reference no strings, f_fs.c:2600)**, CNXN (non-secure, no AUTH), `shell:` service only (v1 raw — we advertise `features=shell` so the host won't negotiate shell_v2), one-stream flow control (1 outstanding WRTE), everything else CLSE. **Each packet is sent as TWO separate USB transfers (24-byte header write + payload write + ZLP when payload is a 512 multiple) exactly like real adbd (daemon/usb.cpp Write) — adb's Windows backend requires an exactly-24-byte header chunk (transport_usb.cpp UsbReadMessage `n != 24` → connection terminated; root cause of the 2026-09-27 CNXN retry loop)** |
| `adbd` | Prebuilt static MIPS32r2 binary — rebuild below |
| `adb_mode.sh` | Console side: configfs gadget `adb_ffs` (0x18d1:0x4EE2), ffs mount, daemon launch (RAM copy), role switch, **retrying** UDC bind (the daemon must claim ep0/ep1/ep2 first), blocking session with B-button/cable exit, full teardown on `stop` |
| `deploy_adb_mode.sh` | SD installer: scripts + binary + dispatcher patch + `adb.mode` flag |

## Build (provenance)

```sh
# MTI Codescape 6.3.0 from the r36sx-hclinux buildroot (mipsel r2 hard)
/home/<user>/work/r36sx-hclinux/build/r36sx-v26-k512/host/bin/mips-mti-linux-gnu-gcc \
    -static -Os -Wall -Wextra -s -o adbd min_adbd.c
```

Kernel uapi headers (`linux/usb/functionfs.h`, `ch9.h`) come from the MTI
sysroot (`.../host/mipsel-buildroot-linux-gnu/sysroot/mipsel-r2-hard/`).
Current binary: `adbd` SHA-256
`ac8df608b565af924281dca951d6690d5891ec65e77a1b67600c69c87690c5f3`
(611 KB, `ELF 32-bit LSB MIPS32 rel2, statically linked, stripped`).

## Requirements (platform side)

Kernel 5.12.4 with `CONFIG_USB_FUNCTIONFS=y` + `CONFIG_USB_CONFIGFS_F_FS=y`
(r36sx-hclinux fragment `boards/r36sx-v26/kernel/r36sx-v26-k512.config.fragment`,
uncommitted→committed with 9-6f). The ffs function uses 2 bulk endpoints
(+ ep0) — fits the MUSB 4-EP budget.

## Usage

1. Deploy: `./deploy_adb_mode.sh /mnt/g` (creates the `adb.mode` flag).
2. Boot the console, connect USB to the PC, menu entry **NETWORK**.
3. PC side:

```sh
adb kill-server        # force fresh enumeration
adb devices            # expect: R36SX0001  device
adb shell              # interactive root shell (v1 raw — no PTY)
```

`adb_mode.sh` blocks until **B** is pressed or the cable is unplugged, then
restores gadget, ffs mount and host role. Console-side log:
`/mnt/sdcard/ADB_MODE_DEBUG.log` (kept separate from NET_MODE_DEBUG.log —
it is the experiment evidence).

## Test plan (see also r36sx-hclinux docs/experiments/2026-09-26_9-6f-*)

- **Phase A — enumeration, idle >60 s**: overlay must NOT appear (the NCM
  case showed it at ~30 s, so wait past that).
- **Phase B — interactive `adb shell`** (uname, free, ls): observe screen.
- **Phase C — sustained bulk traffic** (`adb shell 'dd if=/dev/urandom
  bs=4096 count=2048 | base64'` or an `adb pull` of a rom): observe screen.
- Every phase: photo/video of the display + ADB_MODE_DEBUG.log.

## Status

| Item | State |
|---|---|
| min_adbd (source + static mipsel binary) | BUILD PASS (clean `-Wall -Wextra`) |
| adb_mode.sh / dispatcher `adb.mode` | written — physical pending |
| Physical overlay test (phases A/B/C) | PENDING — needs Class F deploy authorization |
| `adb shell` end-to-end | PENDING — physical |
