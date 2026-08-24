# HARDWARE.md — R36SX V2.6 y Familias Soportadas — TreeFrogUI

> Hechos vs asunciones. Cada valor tiene nivel de evidencia. No inferir `PHYSICAL PASS` sin hardware.

## 1. Target primario vs familias upstream

| Alcance | Devices | Nota |
|---------|---------|------|
| **PRIMARY FORK TARGET** | **R36SX V2.6** (Stock OS) | Optimización activa del fork |
| **SUPPORTED_UPSTREAM DEVICES** | R36SX v2.6, R36SX v2.7, R36HD, SF3000, SF3000 HD, SF3100, SF3500, GB350 | 7–8 familias en `build_release.sh:STOCK[]`, `install.md`, `hijack/zhijack.tpl.sh`. Comparten boot hijack autorun pero difieren panel/driver/rkgame policy |

`AGENTS.md §1` es primario R36SX V2.6; esta tabla no pretende que el fork ya valide todas las familias — ver `docs/PROJECT_STATE.md` (`PHYSICAL_GOLDEN=NONE`).

## 2. Hechos validados R36SX V2.6

| FACT | VALUE | EVIDENCE LEVEL | SOURCE / REFERENCE |
|------|-------|----------------|--------------------|
| **SoC ISA** | MIPS32r2 little-endian o32 | **FACT** (ELF + flags) | `build_all.sh:53 SF3000_FLAGS -mips32r2 -march=mips32r2 -EL`, `readelf Flags: 0x70001007 o32 mips32r2`, `hijack/libemu_tfhijack.so: ELF 32-bit LSB MIPS32 rel2` |
| **CPU tuning** | 74Kc + DSP2 (`-mtune=74kc -mdspr2`) | **FACT** (build) | `build_all.sh:50` comment + `SF3000_FLAGS`; `frogui/build_libretro.sh -mtune=24kc` es deuda conocida (ver §6) |
| **Panel R36SX** | 640×480 4:3, `fbwrite`, `0°` | **FACT** | `build_release.sh:75 HJ[r36sx]="R36SX 640 480 4 3 0 fbwrite driver_r36sx.so stop"` |
| **Driver R36SX** | `driver_r36sx.so` (fallback SIGBUS→`driver_r36sx27.so`) | **FACT** (tpl) | `hijack/zhijack.tpl.sh:85-96` `@R36@` block, `build_release.sh:75` |
| **Driver selección** | 2× SIGBUS (`rc=138`) con full driver → `driver27.flag` permanente → `driver_r36sx27.so` | **FACT** | `hijack/zhijack.tpl.sh:172-182` |
| **RKGAME policy R36SX** | `stop` (1× `killall rkgame` boot, `kill -STOP icube`) — no `kill` loop | **FACT** | `build_release.sh:75 KILL=stop`, `hijack/zhijack.tpl.sh:53-54`, sanity `grep -c killall ==1` |
| **RKGAME policy SF family** | `kill` (3× `killall`) | **FACT** | `build_release.sh:77-81`, sanity `==3` |
| **FN raw bit** | **16** | **PHYSICAL_EVIDENCE** | `tests/test_frogui_fn.py` + `frogui/input.c` (input cubevol shm) — test valida mask, runner requiere hardware para PASS definitivo |
| **FN mask** | **0x00010000** | **PHYSICAL_EVIDENCE** | mismo + `frogui/input.h` |
| **L3 raw bit** | **1** | **PHYSICAL_EVIDENCE** | `tests/test_frogui_fn.py` |
| **R3 raw bit** | **2** | **PHYSICAL_EVIDENCE** | `tests/test_frogui_fn.py` |
| **Boot hijack** | Stock `icube`+`rkgame` NO sustituidos; autorun `setting.xml <autorun file="/mnt/sdcard/MD/dummy.md" driver="">` absoluto + override `cores/libemu_md.so=libemu_tfhijack.so` → `zhijack.sh` generado | **FACT** (release infra) | `build_release.sh:25-32`, `hijack/zhijack.tpl.sh:5`, `docs/ai/RELEASE_CONTRACT.md §4` |
| **Boot verifier** | SF3500 verifica `icube`/`rkgame` → "sdcard is damaged" si reemplazados | **FACT** (doc) | `README.md:359`, `build_release.sh:5` comment |
| **Input** | `cubevol → /tmp/joy_key` shm leído por picoarch/frogui | **FACT** | `hijack/zhijack.tpl.sh:118`, `frogui/input.c` |
| **Right analog R36SX** | Espeja face buttons X/A/B/Y on/off, no analógico real (hardware wiring) | **FACT** (doc upstream) | `README.md:400` + `docs/PROJECT_STATE.md` |
| **DRM driver encrypted** | SF3500/HD/SF3100 `driver.so` encrypted byte-identical (3 devices) vs R36SX plain ELF | **FACT** | `build_release.sh:50-58` comments, `hijack/driver_sf3500.so` 98k ELF |
| **Stock backup R36SX v2.6** | Minimal Backup Google Drive `1xTCNNRKfQmFJr2Zkd1oCBRChuWiidIBD` | **FACT** (link) | `install.md#R36SX v2.6` |

**Evidencia física necesaria para cerrar `PHYSICAL_EVIDENCE` completo:** `CLEAN-INSTALL PHYSICAL PASS` fechado con `FIRMWARE/BASELINE`, `ARTIFACT_SHA256`, `TEST_MATRIX`, `USER_OBSERVATIONS`, `PASS/FAIL`, `DATE` — aún `NONE` (`docs/PROJECT_STATE.md`).

## 3. Familias soportadas por release infra (no primarias)

| Device | Panel | Aspect | Present | Driver | RKGAME | Fuente |
|--------|-------|--------|---------|--------|--------|--------|
| r36sx | 640×480 | 4:3 | fbwrite | driver_r36sx.so | stop | `HJ[r36sx]` |
| r36hd | 640×480 | 4:3 | fbwrite | driver_r36sx.so (sin swap) | stop | `HJ[r36hd]` stripped @R36@ |
| sf3000 | 854×480 | 16:9 90° | dispframe | driver_sf3000.so | kill | `HJ[sf3000]` |
| sf3500 | 854×480 | 16:9 90° | dispframe | driver_sf3500.so | kill | `HJ[sf3500]` |
| sf3000hd | 854×480 | 16:9 90° | dispframe | driver_sf3500.so | kill | `HJ[sf3000hd]` |
| sf3100 | 854×480 | 16:9 90° | dispframe | driver_sf3500.so | kill | `HJ[sf3100]` |
| gb350 | 640×480 | 4:3 | dispframe | driver_gb350.so | kill | `HJ[gb350]` |

Clones R36HD requieren `vmlinux.uImage+avp.uImage+dtb.bin` propios sobre backup v2.7 + `install_first/r36hd` (ver `install.md#R36SX clones`).

## 4. Sleep / nosleep

| Device | NOSLEEP_ADDRS (fileoffset:LE16) | Notas |
|--------|----------------------------------|-------|
| r36sx | `0x406d24:0xac62bb18 0x40701c:0xae02bb18 ...` (6) | Opt-in `disable_sleep=on` → `hijack/nosleep -w` live-patch RAM |
| r36hd | 3 addrs (variante R36SX) | — |
| sf3500/hd/sf3100/gb350 | ver `build_release.sh:92-101` | SF3500 boot-verifica cubevol → no on-disk patch; sf3000 no sleep en cubevol |

Ver `hijack/nosleep.c`, `hijack/zhijack.tpl.sh:127`.

## 5. No asumido / UNCONFIRMED

- `R36SX v2.7 kernel/DTB` difiere de v2.6 pero no hay tabla de diferencias versionadas en repo — usar `install.md` + dumps propietarios.
- `driver_r36sx.so` source **NO público** (0 hits en 71 tzubertowski repos, `docs/dev/UPSTREAM_REPOSITORY_MAP.md §12`) — stock proprietary.
- `R3/L3/FN` valores arriba son **PHYSICAL_EVIDENCE** solo si `tests/test_frogui_fn.py` pasa en hardware R36SX V2.6 real fechado; host build no cuenta.

## 6. Deuda técnica hardware-relacionada

- `BUILD_FLAG_CONSISTENCY=KNOWN_DEBT` — `frogui/build_libretro.sh -mtune=24kc` vs `build_all.sh 74kc` (ver `docs/BUILDING.md`).
- `BTN_HW` — SF family `SF3000 HD` reporta como `SF3500` en log (`has /panel`, encrypted driver) — esperado.

## 7. Referencias

- `install.md` — backups por device, `install_first/<dev>` contract
- `build_release.sh:75 HJ[]` — geometría/driver por device
- `hijack/zhijack.tpl.sh` — template generado, @R36@/@HW@/@KILL@/@NOSLEEP@
- `docs/dev/BUILD_ARCHITECTURE.md` — grafo boot completo
- `tests/test_frogui_fn.py` — FN/L3/R3 bit validation (requiere hardware para PASS final)
