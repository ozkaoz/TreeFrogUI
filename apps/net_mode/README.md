# TreeFrogUI Net Mode: network transports for R36SX

A TreeFrogUI app that manages USB network connectivity on the console,
following the same structure as `apps/usb_mode/`. It provides alternative
USB-gadget transports, selected by mode flags on the SD root.

## Dispatch

FrogUI's USB MODE entry (`usb_mtp.sh`) launches the stack. `net_mode.sh`
dispatches on flags in the SD root:

```text
usb_mtp.sh
  ├── /mnt/sdcard/net.mode exists -> net_mode.sh
  │        ├── /mnt/sdcard/ppp.mode exists -> net_ppp.sh   (CDC-ACM + pppd, experimental)
  │        ├── /mnt/sdcard/ecm.mode exists -> net_ecm.sh   (CDC-ECM, experimental)
  │        └── otherwise                  -> net_ncm.sh   (CDC-NCM — DEFAULT, production)
  └── otherwise -> usb_mode.sh mtp  (classic MTP, upstream verbatim)
```

`net_rndis.sh`, `net_serial.sh` and `net_wifi.sh` are present as transports
but are **not currently wired into the dispatcher** (they were used during the
blue-screen investigation and kept for reuse).

## Transports

| Script | Transport | Selection | Status |
|---|---|---|---|
| `net_ncm.sh` | USB CDC-NCM network adapter | **default** | **production** (ADR-015): Windows sees a network adapter, telnet root works; triggers the AVP blue overlay (accepted limitation) |
| `net_ppp.sh` | CDC-ACM + pppd (dial-up networking) | `ppp.mode` | experimental — **refuted** (2026-09-24): triggers the blue overlay too |
| `net_ecm.sh` | USB CDC-ECM network adapter | `ecm.mode` | built; physical validation pending (expected: same blue overlay) |
| `net_rndis.sh` | USB RNDIS network adapter | `rndis.mode` (unwired) | rolled back (Windows driver Code 28) |
| `net_serial.sh` | USB CDC-ACM serial shell | `serial.mode` (unwired) | works: **no blue overlay**, shell via COM port (no networking) |
| `net_wifi.sh` | WiFi client | `wifi.mode` (unwired) | placeholder |

All active transports create a **single-function gadget** (max 3 endpoints —
fits the MUSB controller's 4-EP budget; a combined MTP+network gadget needs 5
EPs and was the original blue-screen suspect). The console side uses
`192.168.137.2/24`; set the PC adapter to `192.168.137.1/24` and
`telnet 192.168.137.2` for a root shell. The session blocks until the cable is
unplugged or the B button is pressed (`usb_exit_watcher`).

## The AVP blue overlay (platform context)

On this platform the AVP firmware paints a uniform blue overlay (`06 f2` in the
framebuffer) whenever **networking is active** — a CDC-network gadget (NCM/ECM/
RNDIS) **or** even PPP over a plain serial ACM port. This is AVP firmware
behavior, not a Linux kernel bug: the kernel stays alive under the overlay
(telnet + network keep working). Every evasion strategy was physically refuted
on 2026-09-24 (DTS `usb0` disabled, CDC subclass, serial-ACM networking); a
plain interactive serial shell (no networking) does **not** trigger it. The
overlay is an **accepted, display-only limitation** of the production network
mode (ADR-015 in r36sx-hclinux). Eliminating it requires custom AVP firmware
(parked — class D, hardware authorization).

## Platform notes (r36sx-hclinux)

- All gadget functions are **built-in** on this port (the on-device module
  loader is unreliable; see the `resolve_symbol` OOPS). `usb_mode.sh` detects
  the built-in stack with `[ -d "$CONFIG_ROOT/usb_gadget" ]`.
- `usb_f_*`/`configfs` function types register at boot; the gadget is created at
  session time via configfs. Requires `S90configfs` (configfs mountpoint) from
  the platform initramfs overlay.
- A RAM shell (`/tmp/bin/busybox` + symlinks + `telnetd -l /tmp/bin/sh`) is used
  to avoid fork/exec from the SD bind mount while the USB bus is saturated.

## Files

- `net_mode.sh` — app entry point (transport dispatch)
- `net_ncm.sh` — production transport (CDC-NCM network adapter)
- `net_ecm.sh` / `net_ppp.sh` / `net_rndis.sh` / `net_serial.sh` — experimental/auxiliary USB transports
- `net_wifi.sh` — WiFi placeholder (pending kernel module support)
- `deploy_net_mode.sh` — SD deployment helper

## Deploy

```bash
./deploy_net_mode.sh /path/to/sd-root
```
