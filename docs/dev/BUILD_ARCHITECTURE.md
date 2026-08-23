# BUILD_ARCHITECTURE.md — Arquitectura de Build TreeFrogUI R36SX V2.6 — Fase B1

**Fecha:** 2026-08-23
**Estado:** `CLASS B — READ-ONLY audit` — no se compiló, no se clonó, no se instaló, no se modificó producto. Solo evidencia verificable.
**Repo:** `D:\R36SX\treefrog-ui-r36sx` (`r36sx-v2.6-dev` = `2e5ffa80c32e7a9d644ad8e80eb2bb8314f3484d`, BASELINE `v1.0.15` = `27f3bf33e906d90e0cd267059bf0559afc6f8a05`)
**Target:** `R36SX V2.6` — Stock OS — `640×480` `4/3` `fbwrite` `driver_r36sx.so` `stop` (ver `build_release.sh:HJ[r36sx]`)
**FrogUI submodule:** `15ea12bb4f6f642b1ec02aabebbad33e5e95ed2b` (branch `sf3000`)

---

## 1. Target y Baseline

| Propiedad | Valor | Evidencia |
|-----------|-------|-----------|
| **TARGET_DEVICE** | `R36SX V2.6` (y `R36HD` comparte `install_first/r36sx` con lógica `@R36@` stripped) | `build_release.sh:STOCK[r36sx]`, `HJ[r36sx]`, `install.md#R36SX v2.6` |
| **BASE_OS** | Stock OS (R36SX v2.6 Minimal Backup, Google Drive) | `install.md` — “DO NOT USE FACTORY/PREINSTALLED STOCK OS” + link `drive.google.com/file/d/1xTCNNRKfQmFJr2Zkd1oCBRChuWiidIBD` |
| **BASELINE_TAG** | `v1.0.15` — `27f3bf33e906d90e0cd267059bf0559afc6f8a05` | `git rev-parse v1.0.15`, `DECISIONS.md:D001` |
| **ACTIVE_BRANCH** | `r36sx-v2.6-dev` → `2e5ffa80c32e7a9d644ad8e80eb2bb8314f3484d` (1 commit ahead de `v1.0.15`, 27 behind `upstream/main` `41f15e2`) | `git log --oneline --decorate` |
| **Toolchain upstream** | `game-de-it/sf3000` `sf3000_toolchain_v0.1` → `mipsel-buildroot-linux-gnu_sdk-buildroot` | `README.md:280`, `frogui/DEVELOPMENT.md:21` |
| **Toolchain host** | Presente en WSL `~/sf3000-work/sf3000toolchain/mipsel-buildroot-linux-gnu_sdk-buildroot` + tarball 1.3 GB | `ls -la ~/sf3000-work/sf3000toolchain` |
| **Cross compiler** | `mips-mti-linux-gnu-gcc (Codescape GNU Tools 2018.09-02) 6.3.0` | `mips-mti-linux-gnu-gcc --version` |

---

## 2. Arquitectura Target (evidencia, no asunción)

| Propiedad | Valor | Evidencia |
|-----------|-------|-----------|
| **TARGET_ISA** | `MIPS32 Release 2` | `build_all.sh:SF3000_FLAGS="-mips32r2 -march=mips32r2 ..."` |
| **TARGET_ENDIANNESS** | `little` (`-EL`) | `SF3000_FLAGS` `-EL`, `file hijack/libemu_tfhijack.so: ELF 32-bit LSB`, `readelf Flags: 0x70001007 ... o32, mips32r2`, `build_all.sh` gpsp wrapper `-EL forces little-endian: this toolchain's g++ defaults to big-endian (gcc to LE), which silently produced BE objects...` |
| **TARGET_ABI** | `o32` | `readelf Flags: o32`, `Flags: 0x70001007 noreorder, pic, cpic, o32, mips32r2` (ambos `libemu_tfhijack.so` y `driver_sf3500.so`) |
| **CPU_TUNING** | `74Kc` (dual-issue out-of-order, DSP2 ASE `-mdspr2`) — evidenciado, no R3000 | `build_all.sh` comentario: “Device CPU is a MIPS 74Kc … Tune for 74kc and enable -mdspr2 — 24kc tuning schedules for wrong pipeline” + `SF3000_FLAGS` `-mtune=74kc -mdspr2` |
| **CPU_MODEL** | `74Kc` (tuning) — `MIPS R3000` NO usado (ELF `readelf -h` muestra genérico `Machine: MIPS R3000` por compatibilidad ELF, no CPU; Flags `mips32r2` es la evidencia real) | `readelf -h` `Machine: MIPS R3000` es header genérico; `Flags: mips32r2` + `-mtune=74kc` es evidencia CPU; no existe prueba de R3000 silicon |
| **TARGET_LIBC** | `mipsel-buildroot-linux-gnu` (Buildroot SDK, sysroot `mips-r2-hard` → glibc/uClibc hard-float) | `build_all.sh:SYSROOT=`, `mips-mti-linux-gnu-gcc -print-sysroot` → `.../sysroot/mips-r2-hard`, `TOOLCHAIN_PATH` |
| **TARGET_FLOAT_ABI** | `hard` (`-mhard-float -mfp32`) | `SF3000_FLAGS`, `apps/*/Makefile: -mhard-float`, `hijack/build_tfhijack.sh: -mhard-float` |
| **CROSS_COMPILE_PREFIX** | `mips-mti-linux-gnu-` | `build_all.sh:MIPS="$TOOLCHAIN/opt/ext-toolchain/bin/mips-mti-linux-gnu-"`, `Makefile.sf3000:MIPS_PREFIX` |
| **EXPECTED_CC / CXX / AR / LD / STRIP** | `mips-mti-linux-gnu-gcc` / `g++` / `ar` / `ld` / `strip` | `build_all.sh:AR="${MIPS}ar" STRIP="${MIPS}strip"`, `Makefile.sf3000: CC:=$(MIPS_PREFIX)gcc` |
| **EXPECTED_SYSROOT** | `~/sf3000-work/sf3000toolchain/mipsel-buildroot-linux-gnu_sdk-buildroot/mipsel-buildroot-linux-gnu/sysroot` (real `.../opt/ext-toolchain/bin/../sysroot/mips-r2-hard`) | `build_all.sh:SYSROOT`, `frogui/build_libretro.sh:SYSROOT`, `mips-mti-linux-gnu-gcc -print-sysroot` |
| **Stripping** | `strip` post-build para todos los `.so` y binarios | `build_all.sh:$(STRIP) $(OUT)/...`, `hijack/build_tfhijack.sh: "${MIPS}strip"` |

`file` ejemplos:
- `hijack/libemu_tfhijack.so: ELF 32-bit LSB shared object, MIPS, MIPS32 rel2 version 1 (SYSV), dynamically linked, stripped`
- `hijack/driver_sf3500.so: ELF 32-bit LSB shared object, MIPS, MIPS32 rel2 version 1 (SYSV), dynamically linked, with debug_info, not stripped`
- `~/sf3000-work/picoarch/picoarch: ELF 32-bit LSB executable, MIPS, MIPS32 rel2 version 1 (SYSV), dynamically linked, interpreter /lib/ld.so.1, for GNU/Linux 2.6.32, stripped`

---

## 3. Flujo de Boot Real (baseline, verificado — no esquema asumido)

```
Stock OS (R36SX v2.6 Minimal Backup, FAT32)
  ↓
[boot] Stock boot → icube (LOOP, NO sustituir)  — SF3500 verifica icube, reemplazarlo = "sdcard is damaged"
  ↓
rkgame (NO sustituir, NO tocar) — verificado en SF3500, resuelve core por extensión via config.xml
  ↓
setting.xml <autorun file="/mnt/sdcard/MD/dummy.md" driver="" />  — ruta ABSOLUTA obligatoria (relative es silenciosamente ignorada)
  .md → config.xml mapea a libemu_md.so (stock picodrive) — TreeFrogUI OVERRIDEA ese fichero:
  ↓
cubegm/cores/libemu_md.so  =  libemu_tfhijack.so  (stub libretro, PIC, libc-linked — corre dentro del proceso rkgame)
  retro_load_game() → fork() zhijack.sh  (rkgame permanece vivo para mantener cubevol → /tmp/joy_key shm)
  ↓
zhijack.sh  — GENERADO por device desde hijack/zhijack.tpl.sh, hardcodeado (no detección runtime):
  R36SX: TF_DEVICE=R36SX  TF_PANEL_W=640 TF_PANEL_H=480 TF_ASPECT 4/3 TF_ROTATE=0 TF_PRESENT=fbwrite TF_DRIVER=/mnt/sdcard/cubegm/driver_r36sx.so  RKGAME=stop
  + freeze icube: kill -STOP $(pidof icube)  (evita respawn de rkgame que redibuja menú fantasma)
  + killall rkgame (solo 1× en R36SX; 3× en SF3500-family)
  + escribe /tmp/tfdevice.env (leído por picoarch y frontends standalone)
  + opt-in logging: si /mnt/sdcard/log.txt existe → /mnt/sdcard/log.txt else /dev/null
  + offline update: cp /mnt/sdcard/cubegm/tfupdate.sh /tmp/tfupdate.sh; sh /tmp/tfupdate.sh; si rc=10 → exec zhijack.sh
  + CPU governor performance, cubevol shm init, nosleep watcher si disable_sleep=on
  + SIGBUS-count driver self-select (R36SX): 2× SIGBUS (rc=138) con driver full → driver_r36sx27.so permanente (marker driver27.flag)
  + HW-render watchdog (non-R36SX): 2× crash antes de /tmp/hw_rendered → force_sw.flag
  ↓
picoarch  (/mnt/sdcard/cubegm/picoarch)  +  picoarch_hi (para gpsp/pcsx/retro8)
  ↓
frogui_libretro.so  (/mnt/sdcard/cubegm/cores/frogui_libretro.so)  — UI, corre como core libretro
  ↓
Usuario selecciona ROM → fork() picoarch <game_core.so> <rom>  →  game corre → exit → waitpid() → vuelve a FrogUI
```

Invariantes preservados en el fork (`AGENTS.md §2`, `DECISIONS.md`, `docs/ai/RELEASE_CONTRACT.md`):
- `icube` y `rkgame` nunca se empaquetan ni sustituyen; el boot es hijack autorun no destructivo salvo decisión explícita en `DECISIONS.md`.
- No se incluyen Stock blobs propietarios, ROMs, BIOS no redistribuibles.
- `POST_INSTALL_MANUAL_FIXES=0` solo tras `PACKAGING PASS + CLEAN-INSTALL PHYSICAL PASS`.

---

## 4. Grafo Real de Build (solo evidencia)

```
[SOURCE]                     [EXTERNAL SOURCE]                     [STOCK DEPENDENCY]
TreeFrogUI repo              tzubertowski forks / libretro         R36SX/SF3000/..._sdcard dumps
├── frogui/ (submodule)      ├── libretro-fceumm ─┐                ├── cubegm/setting.xml (autorun base)
│   └── 15ea12b              ├── snes9x2005 ─┤                   ├── cubegm/cubegm generic driver.so (stock, NO ship)
├── hijack/*.c               ├── gpsp_multicore ─┤  clone_cores.sh  ├── /usr/bin/cubevol (stock, NO ship)
├── apps/*                   ├── Gambatte ─┤  --depth=1           ├── xgame-logo.bmp (stock, reemplazado por release)
├── patches/*.patch          ├── ... (78 clones, ver §6) │        └── kernel 4.4.186 + dtb (geometría)
├── build_all.sh ────────────┤  patches/*.patch aplicado │             ↓
├── Makefile.sf3000 ─────────┤  en build_all.sh ─┘                  build_release.sh STOCK[] paths
├── build_release.sh ────────┼───────────────────────────────────────→ /home/tomaszz/sf3000-work/*_sdcard/cubegm
├── clone_cores.sh           │
└── sdcard/ (staging)        │

[TOOLCHAIN]                  [BUILD]
~/sf3000-work/sf3000toolchain/mipsel-buildroot-linux-gnu_sdk-buildroot
└── opt/ext-toolchain/bin/mips-mti-linux-gnu-{gcc,g++,ar,strip} 6.3.0
    └── sysroot/mips-r2-hard  ──→  .toolchain/{mips-gcc, gpsp-gcc, fba-gcc} wrappers
                                   ├── build_all.sh → build/*.so (57 cores, .so stripped, O32 MIPS32r2 EL)
                                   ├── hijack/build_tfhijack.sh → hijack/libemu_tfhijack.so + nosleep (ELF MIPS)
                                   ├── frogui/build_libretro.sh → FrogUI/frogui_libretro.so (fuente frogui/, hardcode /home/tomaszz/FrogUI)
                                   └── apps/*/Makefile → cubegm/video_player, image_viewer (ELF MIPS)

[EXTERNAL SOURCE (picoarch)]          [PREBUILT]
~/sf3000-work/picoarch (r36sx branch f8ff5ba, tzubertowski/TreeFrogUI_picoarch)
├── picoarch (416820 bytes, MIPS EXEC stripped)
├── picoarch_hi
└── libpicofe (vendored)  ─────────→  build_release.sh: PICOARCH=/home/tomaszz/.../picoarch/picoarch
                                      PICOARCH_HI, FROGUI=/home/tomaszz/.../FrogUI/frogui_libretro.so, TYRQUAKE=/home/tomaszz/.../tyrquake_libretro.so

[STAGING]              [GENERATED OUTPUT]                      [PACKAGE]
sdcard/cubegm/*        build_release.sh → release/latest/release/
├── cores/*.pcsx4all     ├── cubegm/cores/*.so (universal, de build/ + prebuilt drivers)
├── xgame-logo.bmp       ├── cubegm/{picoarch,picoarch_hi,nosleep} (de ~/sf3000-work/picoarch)
├── frogui/settings.txt  ├── cubegm/lib/libSDL-... (de sdcard/cubegm/lib, cp -L)
└── picoarch.cfg ?       ├── cubegm/{driver_*.so} (de sdcard/cubegm — NO en repo, ver §9)
                         ├── frogui/ (de sdcard/frogui + assets/system-icons, icon-packs)
                         ├── roms/ (estructura vacía)
                         ├── MD/dummy.md (generado printf 'TF')
                         └── docs/{README.md,...} (de repo root)

                          build_release.sh for dev in STOCK[]:
                           ├── install_first/<dev>/cubegm/cores/libemu_md.so (= hijack core, override)
                           ├── install_first/<dev>/cubegm/setting.xml (stock + sed autorun ABSOLUTE)
                           ├── install_first/<dev>/cubegm/xgame-logo.bmp (device-correct)
                           └── install_first/<dev>/cubegm/zhijack.sh (GENERATED desde hijack/zhijack.tpl.sh + HJ[] + NOSLEEP_ADDRS[])

                                                         ↓  pack_release.sh
                                                      [RELEASE]
                                                      release/latest/release/ + release/latest/*.zip
                                                      + release/latest/update.zip (offline delta, tfupdate.sh)
                                                      FAT32, sin symlinks, manifest + SHA256
```

Legend:
- **SOURCE** — versionado en este repo
- **EXTERNAL SOURCE** — clones vía `clone_cores.sh` (78), submodule `frogui`, `picoarch` en `~/sf3000-work`
- **PREBUILT** — `hijack/*.so`, `driver_*.so` en `~/sf3000-work` (sin source)
- **STOCK DEPENDENCY** — dumps SD del autor bajo `/home/tomaszz/sf3000-work/*_sdcard` (hardcoded, no redistribuible, no en repo)
- **GENERATED OUTPUT** — `release/latest/release/` (gitignored, creado por `build_release.sh`)

---

## 5. Separación de Componentes

| Categoría (spec §5) | Qué es | Ejemplo | En repo |
|---------------------|--------|---------|---------|
| **BUILD_INPUT** | Fuente compilable en este repo | `frogui/*.c`, `hijack/*.c`, `apps/video_player/*.c`, `cores/` (tras `clone_cores.sh`), `patches/*.patch` | Sí (excepto `cores/` ignorado, poblado por clone) |
| **BUILD_OUTPUT** | Artefactos compilados | `build/*.so` (57 cores), `.toolchain/mips-gcc`, `hijack/libemu_tfhijack.so`, `frogui_libretro.so` | No (gitignored: `/build/`, `/.toolchain/`) |
| **PREBUILT_INPUT** | Binario prebuilt que entra al staging sin compilar en este repo | `hijack/driver_sf3500.so` (98k, MIPS SO con debug), `hijack/libemu_tfhijack.so` (6k, stripped, reconstruible), `driver_r36sx*.so` sueltos en `~/sf3000-work` | Parcial (solo `driver_sf3500.so`+`libemu_tfhijack.so` versionados; el resto externo) |
| **STAGING_INPUT** | Contenido copiado tal cual a `release/latest/release/` | `sdcard/cubegm/*` (picoarch, drivers, libs, bios), `sdcard/frogui/*`, `assets/system-icons`, `assets/icon-packs` | Sí (`sdcard/` gitignored pero existe vacío; assets sí) |
| **R36SX_OVERLAY** | Config por device generada | `install_first/r36sx/cubegm/{setting.xml, xgame-logo.bmp, cores/libemu_md.so, zhijack.sh}` — generado desde `STOCK[r36sx]` + `HJ[r36sx]` + `hijack/zhijack.tpl.sh` | No (generado — no existe `install_first/` en el checkout baseline) |
| **STOCK_OS_DEPENDENCY** | Stock dumps del autor (no redistribuible) | `/home/tomaszz/sf3000-work/R36SX_sdcard/cubegm/setting.xml`, `driver.so`, `xgame-logo.bmp` para 7 devices (`r36sx, r36hd, sf3000, sf3500, sf3000hd, sf3100, gb350`) | No (paths hardcodeados, no en repo, no en este host salvo `driver.so` sueltos para análisis) |

---

## 6. Staging y Packaging

**`sdcard/` (staging, gitignored):**
- `sdcard/cubegm/xgame-logo.bmp` (1.6 MB, BMP stock placeholder)
- `sdcard/cubegm/cores/.pcsx4all/pcsx4all.cfg` (config stock)
- `sdcard/frogui/settings.txt` (default settings)
- Resto (`picoarch`, `driver_*.so`, `lib/*`, `bios/*`) no presente en checkout limpio — debe poblarse vía build o copia desde `~/sf3000-work` / stock dumps antes de `build_release.sh`. Ver `build_release.sh:cp_if_diff "$PICOARCH" "$STAGE/cubegm/picoarch"` (falla silencioso si no existe).

**`build_release.sh` inputs → `release/latest/release` (gitignored, FAT32-safe):**

| INPUT | SOURCE_PATH (repo o externo) | DESTINATION | GENERATED_BY | HARDCODED | REQUIRED |
|-------|------------------------------|-------------|--------------|-----------|----------|
| picoarch | `/home/tomaszz/sf3000-work/picoarch/picoarch` | `release/latest/release/cubegm/picoarch` | `build_release.sh:cp_if_diff "$PICOARCH"` | YES `/home/tomaszz` | YES |
| picoarch_hi | `/home/tomaszz/sf3000-work/picoarch/picoarch_hi` | `.../picoarch_hi` | `build_release.sh` | YES | YES (gpsp/pcsx) |
| frogui_libretro.so | `/home/tomaszz/sf3000-work/FrogUI/frogui_libretro.so` | `.../cubegm/cores/frogui_libretro.so` | `build_release.sh:cp_if_diff "$FROGUI"` | YES | YES |
| tyrquake_libretro.so | `/home/tomaszz/sf3000-work/tyrquake-og/tyrquake_libretro.so` | `.../cores/tyrquake_libretro.so` | `build_release.sh` | YES | NO (opcional) |
| hijack core | `hijack/libemu_tfhijack.so` (construido por `hijack/build_tfhijack.sh`) | `.../install_first/<dev>/cubegm/cores/libemu_md.so` (7×) | `build_release.sh:cp "$HIJACK_CORE" "$dst/cubegm/cores/$OVERRIDE_CORE"` | NO | YES |
| STOCK setting.xml | `/home/tomaszz/sf3000-work/R36SX_sdcard/cubegm/setting.xml` (y 6 más) | `.../install_first/<dev>/cubegm/setting.xml` (sed autorun) | `build_release.sh:cp "$src/setting.xml"` | YES (7 paths) | YES |
| STOCK cubegm drivers (para universal) | `sdcard/cubegm/driver_*.so` (staging) | `.../cubegm/driver_*.so` (6 drivers) | `build_release.sh:for f in driver_*.so; do cp "$STAGE/cubegm/$f"...` | NO (usa STAGE) | YES |
| libs | `sdcard/cubegm/lib/libSDL-1.2.so.0` (symlink → .0.11.4) | `.../cubegm/lib/libSDL-1.2.so.0` (real, cp -L) | `build_release.sh:cp -L` | NO | YES |
| frogui assets | `sdcard/frogui/*` + `assets/system-icons` + `assets/icon-packs` | `.../frogui/*` | `build_release.sh:cp -a` | NO | YES |
| roms scaffolding | `sdcard/roms/*` | `.../roms/*` | `build_release.sh` | NO | YES |
| zhijack.sh | `hijack/zhijack.tpl.sh` + `HJ[]` + `NOSLEEP_ADDRS[]` | `.../install_first/<dev>/cubegm/zhijack.sh` (7×, chmod +x) | `build_release.sh:sed ... "$HIJACK/zhijack.tpl.sh" > "$dst/...zhijack.sh"` | NO (template) pero `HJ[]` hardcodea geometría | YES |
| dummy MD | generado `printf 'TF' > "$OUT/$DUMMY_REL"` | `MD/dummy.md` + `MD/filelist.csv` | `build_release.sh` | NO | YES |
| docs | `README.md`, `cores.md`, etc. | `.../README.md`, `.../docs/*` | `build_release.sh:cp` | NO | NO |

`HARDCODED_PATH_COUNT` (solo `build_release.sh`): `11` refs a `/home/tomaszz/sf3000-work` (4 vars `PICOARCH*`/`FROGUI`/`TYRQUAKE` + 7 `STOCK[]`). `build_all.sh` usa `$HOME/sf3000-work` (portable), `apps/*/Makefile` hardcodea `/home/tomaszz` como `?=` fallback (parametrizable), `frogui/build_libretro.sh` hardcodea `cd /home/tomaszz/sf3000-work/FrogUI` (no portable), `deploy*.sh` hardcodea `WORK=/home/tomaszz/sf3000-work`.

**Packaging (`pack_release.sh` / `publish_release.sh`):**
- `OUTPUT`: `TreeFrogUI_<version>.zip` (full) + `update.zip` (delta offline) en `release/latest/`, comparación con `release/artifact/TreeFrogUI_v*.zip` (retained).
- `FAT32 guard`: `find "$OUT" -type l` → fail si symlinks.
- `Sanity checks`: no generic `zhijack.sh`, no `tf_detect.sh`, cada `zhijack.sh` debe contener `kill -STOP $(pidof icube)` y `killall rkgame` (1× r36sx, 3× others), `dummy.md`, `tfupdate.sh`, offline `sh /tmp/tfupdate.sh`.
- `PREBUILT` no incluye `icube`/`rkgame`/`cubegm/icube_start`/`driver.so` stock genérico — filtrado explícito.

---

## 7. Componentes Externos (solo evidencia, no install)

| Componente | External Repository | Ubicación Esperada | Revisión | Pinned? |
|------------|---------------------|--------------------|----------|---------|
| **SF3000 toolchain SDK** | `game-de-it/sf3000` `sf3000_toolchain_v0.1` | `~/sf3000-work/sf3000toolchain/mipsel-buildroot-linux-gnu_sdk-buildroot` | `2018.09-02` (Codescape 6.3.0) | YES (release tag) |
| **FrogUI** | `tzubertowski/FrogUI` `sf3000` | `frogui/` submodule | `15ea12b` | YES (submodule pin) |
| **Picoarch** | `tzubertowski/TreeFrogUI_picoarch` `r36sx` | `~/sf3000-work/picoarch` | `f8ff5ba` (actual HEAD, `origin/r36sx`) | NO (branch, no tag/commit pin en `build_release.sh` — solo path) |
| **Tyrquake** | `tzubertowski/tyrquake-og` (?) | `~/sf3000-work/tyrquake-og/tyrquake_libretro.so` | UNKNOWN (no repo ref, solo path) | NO |
| **Cores (78)** | `clone_cores.sh` — 12 tzubertowski forks + 66 libretro upstream (ver `DEPENDENCY_MATRIX.md` lista) | `cores/` (poblado por `clone_cores.sh --depth=1`) | **NO** — `--depth=1` sin tag/commit pin (salvo `fake-08#sf3000`) | NO (unpinned) |
| **Pico286** | `xrip/pico-286` + `patches/pico286-sf3000.patch` (87k) | `cores/pico-286` (tras `clone` + patch) | UNKNOWN (no pin) | NO |
| **Stock SD dumps** | No repo (propietario, Google Drive links en `install.md`) | `/home/tomaszz/sf3000-work/*_sdcard/cubegm` (7 devices) | — | — |

---

## 8. Prebuilt Binarios

| FILE | TYPE | ARCH | PURPOSE | SOURCE_AVAILABLE | BUILD_SCRIPT | PROVENANCE | CLASSIFICATION | REPRODUCIBLE | REDISTRIBUTABLE |
|------|------|------|---------|-----------------|--------------|------------|----------------|--------------|-----------------|
| `hijack/libemu_tfhijack.so` | `ELF 32-bit LSB SO MIPS32r2 EL stripped` | MIPS32r2 EL o32 | Hijack core (override `libemu_md.so`) | YES (`hijack/tfhijack.c`, `tfexec.c`, `libretro.h`) | `hijack/build_tfhijack.sh` (mips-gcc -shared) | Construible desde source en este repo | **A** (buildable from source) | YES (si toolchain presente) | YES (MIT/CC?) |
| `hijack/driver_sf3500.so` | `ELF 32-bit LSB SO MIPS32r2 EL not stripped` | MIPS32r2 EL o32 | Driver SF3500 (encrypted? plain ELF? con debug) — referencia / fallback para R36SX sf3000-v3 detect | **UNKNOWN** (no `driver_sf3500.c` en repo) | **NONE** en repo | Prebuilt con proveniencia conocida (stock dump, byte-identical a SF3500/HD/SF3100 — `build_release.sh` comentario “byte-identical encrypted driver.so”) | **D** (prebuilt known provenance, stock) | NO (sin source) | **NO** (propietario, Stock) — pero ship como `driver_sf3500.so` (no `driver.so` stock genérico) |
| `hijack/nosleep` (tras build) | `ELF MIPS EXEC` | MIPS | Live-patcher cubevol sleep (opt-in) | YES (`hijack/nosleep.c`) | `hijack/build_tfhijack.sh` (segunda mitad) | Construible | **A** | YES | YES |
| `hijack/tfexec` | `ELF ?` | ? | Forwarder para rkgame exec driver prog | YES (`hijack/tfexec.c`) | `hijack/build_tfhijack.sh`? | Construible | **A** | YES | YES |
| `frogui/venv/**/*.so` | `ELF x86_64` | x86_64 | Python env (numpy/Pillow) — no es target | — | — | No es TreeFrog payload | **—** (ignorar, no redist) | — | — |
| `~/sf3000-work/driver*.so` (`driver.so`, `driver_gb350.so`, `driver_r36sx27.so`) | `ELF MIPS` | MIPS | Drivers stock sueltos para análisis (no en repo) | NO | NO | Prebuilt stock | **F** (Stock/proprietary) | NO | NO |
| `~/sf3000-work/picoarch/picoarch` | `ELF 32-bit LSB EXEC MIPS32r2 stripped` | MIPS32r2 EL | Frontend picoarch (r36sx branch f8ff5ba) | YES (`~/sf3000-work/picoarch/*.c`, `libpicofe`) | `build_picoarch_hi.sh` / `build_sf3000.sh` | External source presente | **B** (buildable from pinned external source? branch r36sx, no tag) | **MAYBE** (si se fija commit f8ff5ba) | YES (BSD/GPL) |
| `~/sf3000-work/sf3000toolchain/.../mips-mti-linux-gnu-gcc` | `ELF x86_64` | x86_64 | Cross compiler | SDK tarball | — | Prebuilt SDK `game-de-it/sf3000` | **D** | YES (SDK reproducible) | YES (GPL) |
| `sdcard/cubegm/lib/libSDL-1.2.so.0` etc. | `ELF MIPS SO` | MIPS | Libs target (SDL/png) | NO (prebuilt en staging) | NO | Prebuilt stock/built? | **D** | UNKNOWN | YES? (LGPL) |

Conteo relevante (excluyendo `frogui/venv`):
- **PREBUILT_BINARY_COUNT** = `2` versionados en repo (`driver_sf3500.so`, `libemu_tfhijack.so` prebuilt) + `~6` drivers stock esperados en staging (`driver_r36sx.so` etc.) que no están versionados (externos) = **8** si se cuenta staging completo; **2** en repo puro.
- **UNKNOWN_PREBUILT_COUNT** = `1` (`driver_sf3500.so` sin source) + `6` drivers stock = **7** si se cuenta staging; `1` en repo.
- **PROPRIETARY_DEPENDENCY_COUNT** = `7` stock dumps (`R36SX_sdcard`, `SF3000_sdcard`, etc.) + `1` driver_sf3500 (stock) = **8** (no redistribuibles; no se empaqueta `icube`/`rkgame`/`driver.so` genérico).

Clasificación usada (`DEPENDENCY_MATRIX.md`): `A=buildable from source in this repo`, `B=buildable from pinned external source`, `C=external source exists but revision unpinned`, `D=prebuilt binary with known provenance`, `E=prebuilt binary with unknown provenance`, `F=Stock/proprietary/non-redistributable`.

---

## 9. Separación Universal / R36SX

| Aspecto | Universal (payload) | R36SX overlay (`install_first/r36sx`) |
|---------|----------------------|----------------------------------------|
| **Origen** | `sdcard/cubegm/*` + `build/`, `hijack`, `assets`, `apps` | Generado: `STOCK[r36sx]` (`/home/tomaszz/.../R36SX_sdcard/cubegm/setting.xml`) + `HJ[r36sx]` (`R36SX 640 480 4 3 0 fbwrite driver_r36sx.so stop`) |
| **Contenido** | `cubegm/cores/*.so`, `picoarch`, `libSDL`, `frogui/`, `roms/`, `MD/dummy.md` | `setting.xml` (autorun ABSOLUTE), `cores/libemu_md.so` (hijack override), `xgame-logo.bmp` (640×480), `zhijack.sh` (hardcoded R36SX, 1× killall, SIGBUS driver27 fallback, @R36@ block, no @HW@) |
| **Shippado** | Siempre | Solo si usuario copia `install_first/r36sx/` (upstream) — **RELEASE_CONTRACT objetivo**: fusionar en single-ZIP para R36SX, `POST_INSTALL_MANUAL_FIXES=0` |
| **En repo** | `sdcard/` (vacío parcial, gitignored) + `hijack/` + `assets/` | **No existe** `install_first/` en el checkout baseline — se genera; stock dumps no versionados |
| **Dependencia Stock** | No (excepto libs) | Sí (stock `setting.xml`/`driver.so` del backup minimal) |

---

## 10. Blockers (no corregidos, solo auditados)

| Blocker | Origen | Impacto | Evidencia | Parametrizable? |
|---------|--------|---------|-----------|-----------------|
| **HARDCODED_PATHS `/home/tomaszz/sf3000-work` (11 en `build_release.sh`)** | `build_release.sh:35-38 PICOARCH/FROGUI/TYRQUAKE + STOCK[7]` | `build_release.sh` falla si `WORK != /home/tomaszz` o si stock dumps no existen | `grep -c "/home/tomaszz" build_release.sh = 11`, `grep -n "/home/tomaszz"` | **YES** — reemplazar por `$HOME`/`$REPO` o args, como `build_all.sh` ya hace (`$HOME/sf3000-work`) |
| **`~/sf3000-work/FrogUI` hardcode** | `frogui/build_libretro.sh:6 cd /home/tomaszz/sf3000-work/FrogUI` | Build FrogUI standalone falla (path autor) | `grep tomaszz frogui/build_libretro.sh` | YES — debe usar `$(dirname)`/`$REPO/frogui` |
| **`frogui/build_libretro.sh` usa `-mtune=24kc` viejo** | `frogui/build_libretro.sh: CFLAGS -mtune=24kc` | No óptimo vs `build_all.sh: -mtune=74kc -mdspr2` (74Kc) — inconsistencia | `grep mtune frogui/build_libretro.sh` vs `build_all.sh` | YES |
| **Stock dumps ausentes en este host** | `build_release.sh:STOCK[r36sx]=/home/tomaszz/.../R36SX_sdcard/cubegm` | `build_release.sh` WARN “no stock for $dev” y no genera `setting.xml`/`zhijack.sh` | `ls -la ~/sf3000-work/*_sdcard 2>&1` → No such file (salvo `picoarch`) | **NO** (propietario, no redist) — requiere backup minimal manual o mock |
| **Staging drivers ausentes** | `sdcard/cubegm/driver_*.so` no versionado (gitignored) | `build_release.sh:for f in driver_*.so; cp "$STAGE/cubegm/$f"` falla silencioso, universal sin drivers | `ls sdcard/cubegm` → solo `xgame-logo.bmp`, `cores/.pcsx4all` | **MAYBE** — extraer de stock dump o build? |
| **Picoarch/Tyrquake paths externos** | `build_release.sh:PICOARCH=/home/tomaszz/...` | Staging/drivers sin picoarch si no existe `~/sf3000-work/picoarch` en host de build (en este host sí existe `f8ff5ba`, pero no es portable) | `ls ~/sf3000-work/picoarch/picoarch` → YES en este WSL, NO en CI limpio | YES — usar submodules o `$REPO/picoarch` |
| **Tyrquake OG path desconocido** | `TYRQUAKE=/home/tomaszz/.../tyrquake-og/...` | No hay repo `tyrquake-og` documentado (solo `tyrquake` libretro) | `grep TYRQUAKE build_release.sh` | UNKNOWN |
| **Missing `cmake`** | Host WSL sin `cmake` | `TIC-80` no compila (`build_all.sh` warning) — 1 core perdido | `command -v cmake` → NO | YES — `sudo apt install cmake` |
| **NTFS CRLF sharing** | Windows `autocrlf=true` vs WSL vacío | WSL `git status` masivo `M` espurio | `wsl bash -c "cd /mnt/d/... && git status"` → 80+ `M` | YES — `.gitattributes` |
| **No `install_first/` versionado** | Baseline no incluye overlay | No se puede verificar R36SX sin generar | `find . -type d -name install_first` → none | **BY DESIGN** (generado) |
| **73 cores unpinned** | `clone_cores.sh` `--depth=1` sin tag | No reproducible a SHA exacto | `grep clone clone_cores.sh | wc -l = 78`, `grep -c "depth=1"` | YES — pin con `git rev-parse` tras clone |
| **Driver R36SX sin source** | `driver_r36sx.so` no en repo | No reconstruible, solo prebuilt stock | `grep -R driver_r36sx`, `find . -name "*driver*"` → solo refs, no source | NO |

**PRIMARY_BLOCKER para reproducibilidad completa:** `HARDCODED_PATHS + STOCK dumps propietarios ausentes` (build_release.sh no puede completar `release/latest/release` en un host limpio sin los 7 stock SD dumps del autor y sin staging drivers pre-poblados).

---

## 11. Reproducibilidad (estricta separación — B1.6 §4)

### A. Public source availability (¿Existe código fuente?)

| Componente | Public source | Evidencia |
|------------|---------------|-----------|
| FrogUI | **YES** — `tzubertowski/FrogUI` `15ea12b` (`sf3000` branch, 4 tags) | `GET /repos/tzubertowski/FrogUI`, `git ls-remote 15ea12b`, `git submodule status` |
| Picoarch | **YES** — `tzubertowski/TreeFrogUI_picoarch` `r36sx` (`e98af36` HEAD, `f8ff5ba` local) | `GET /repos/.../TreeFrogUI_picoarch`, branches `r36sx` única, `0` tags |
| Hijack | **YES** — `hijack/*.c` en este repo | `hijack/tfhijack.c`, `build_tfhijack.sh` |
| Cores (78) | **YES** — `9` forks tzubertowski + `58` generic `libretro/*` + `8` patched + `TIC-80` etc. son todos `https://github.com/...` públicos | `clone_cores.sh` 78 URLs verificadas vía `GET /users/tzubertowski/repos` 71 + `libretro/*` |
| Toolchain | **YES** — `game-de-it/sf3000` `sf3000_toolchain_v0.1` SDK tarball | `README.md:281`, `ls -la ~/sf3000-work/sf3000toolchain` 1.3GB |
| R36SX driver | **NO** — `0` drivers con source en `71` tzubertowski repos; solo `hijack/driver_sf3500.so` prebuilt stock | `grep -R driver_r36sx` 71 repos `0` hits |

### B. Deterministic fork build (¿Podemos fijar hoy SHA/toolchain y generar repetidamente el mismo build?)

| Nivel | Reproducible ahora? | Blocker | Evidencia |
|-------|---------------------|---------|-----------|
| **SOURCE_REPRODUCIBLE** (A) | **PARTIAL** — ver tabla A: FrogUI YES, Picoarch YES (con pin), Cores YES code pero 77/78 unpinned, Drivers NO | `clone_cores.sh --depth=1` sin SHA |
| **BUILD_REPRODUCIBLE** | **PARTIAL** | Toolchain presente **YES** (`6.3.0` Codescape), host `cmake` **NO** (solo TIC-80), `frogui/build_libretro.sh:6 cd /home/tomaszz` hardcode falla, pero con fix `$REPO` sería YES | `command -v cmake` NO, `frogui/build_libretro.sh` hardcode |
| **PACKAGE_REPRODUCIBLE** | **NO** | Requiere `BUILD` + `sdcard/cubegm/driver_*.so` staging (gitignored, ausente) + `STOCK` dumps 7 hardcode + `11` hardcode paths en `build_release.sh` | `build_release.sh` WARN no stock, `ls sdcard/cubegm` solo `xgame-logo.bmp` |
| **PHYSICAL_VALIDATED** | **NO** | Requiere hardware R36SX V2.6 + `PACKAGING PASS` + `CLEAN-INSTALL PHYSICAL PASS` | `PHYSICAL_EVIDENCE=NONE — NOT TESTED` |

**No afirmar `v1.0.15 reproducible` si solo tenemos fuentes actuales/aproximadas — ver C.**

### C. Historical v1.0.15 reconstruction (¿Sabemos con certeza qué SHA externo usó el autor para producir v1.0.15 2026-08-17?)

| Componente | PUBLIC_SOURCE | HISTORICAL_EXACT_SHA | CANDIDATE_SHA | CONFIDENCE | Evidencia |
|------------|---------------|----------------------|---------------|------------|-----------|
| FrogUI | YES | **KNOWN** `15ea12bb4f6f642b1ec02aabebbad33e5e95ed2b` (2026-08-07) | `15ea12b` | **HIGH** (submodule pin existe público `git ls-remote`) | `git -C frogui log -1 --format=%ci 15ea12b` 2026-08-07 < `27f3bf3` 2026-08-17 |
| Picoarch | YES | **UNKNOWN** | `f8ff5ba` (2026-07-29) o `e98af36` (2026-08-23) | **LOW** (branch `r36sx`, no tag/SHA pin en `build_release.sh:PICOARCH` solo path; ventana 07-29–08-23; `git log treefrog-ui --grep=picoarch` no menciona pin) | `wsl bash -c "git -C ~/sf3000-work/picoarch log --oneline --before=2026-08-18"` 15 commits, `git ls-remote` e98af36 vs f8ff5ba |
| Cores (77/78) | YES | **UNKNOWN para 77/78** | `HEAD --depth=1` actual (p.ej. `libretro/picodrive` HEAD 2026-08-23) | **LOW** (unpinned) | `clone_cores.sh` sin SHA; `git log treefrog-ui` no registra `clone SHA` |
| fake-08 | YES | **UNKNOWN** (branch `sf3000` pin) | `sf3000` branch HEAD | **MEDIUM** (branch pin, no SHA) | `clone fake-08 ... sf3000` |

**Ver `DEPENDENCY_MATRIX.md` para matriz por componente y `WSL_ENVIRONMENT.md` para host/toolchain detallado.**

### Baseline vs Minimal Profile (B1.6 §5)

**Estrategia inicial:** `UPSTREAM_FEATURE_SET_FIRST` — reproducir matriz upstream v1.0.15 completa (78 cores, 7 devices STOCK, toolchain 6.3.0). **No reducir baseline a 15-16 repos.**

**FUTURE_R36SX_MINIMAL_PROFILE** (documentado como futuro, no baseline): `~15-16` repos externos para R36SX V2.6 solo (FrogUI + picoarch + hijack + toolchain + ~12 cores críticos `gpsp_multicore` `gambatte` `snes9x2005/2002` `fceumm` `picodrive` `pcsx4all` etc., excluye SF3000/SF3500/GB350 drivers y cores opcionales `vitaquake2/rockbox/ebook` — ver `UPSTREAM_REPOSITORY_MAP.md §15`). **Primero upstream, luego minimal.**

### Stock vs Build (B1.6 §7)

`Stock input required for packaging != source required for compilation` — `SOFTWARE_STACK_BUILD` (FrogUI+picoarch+hijack+cores+toolchain) puede ser posible sin SD Stock, pero `COMPLETE_R36SX_INSTALL_PACKAGE` (`release/latest/release` + `install_first/r36sx` con `setting.xml`/`driver_r36sx.so`/`xgame-logo.bmp`) requiere actualmente ciertos inputs locales provenientes del Stock OS (proprietary, no redistribuible — ver `R36SX_DRIVER_PUBLIC_SOURCE=NO`).

### Toolchain (B1.6 §8)

`TOOLCHAIN_DOWNLOAD_REPRODUCIBLE = YES` — SDK `sf3000_toolchain_v0.1` tarball 1.3GB descargable de `game-de-it/sf3000` (release tag `sf3000_toolchain_v0.1`, `62018.09-02`, 6.3.0) — ver `WSL_ENVIRONMENT.md §6`.

`TOOLCHAIN_SOURCE_BUILD_REPRODUCIBLE = UNKNOWN / NO` — no reconstruimos el compilador Codescape desde fuente; el SDK es prebuilt.

### Driver R36SX (B1.6 §6)

`R36SX_DRIVER_PUBLIC_SOURCE=NO` — `0` `tzubertowski/*` repos con `driver_r36sx` source (71 enum). `R36SX_DRIVER_PUBLIC_BINARY=NO` — solo `driver_sf3500.so` (SF3500) prebuilt en `treefrog-ui/hijack` (98k ELF MIPS, stock), **no** `driver_r36sx.so`. `R36SX_DRIVER_ORIGIN=STOCK_OS` (Stock dump `R36SX_sdcard`), `REDISTRIBUTABLE=NO/NOT_AUTHORIZED` (proprietary, `docs/ai/RELEASE_CONTRACT` no incluir Stock blobs).

---

## 12. Próximos Pasos (CLASS B → B2, no ejecutados)

1. `.gitattributes` para CRLF.
2. `cmake` para TIC-80.
3. Parametrizar `build_release.sh` (`${HOME}/sf3000-work` o `$REPO`/`$STOCK_ROOT`).
4. Documentar provisión de stock dumps (links `install.md` + scripts `fetch-stock-mock.sh` si se permite).
5. Pinnear cores (`clone_cores.sh` → `git rev-parse HEAD > cores/<name>.pin` tras clone).
6. Pinnear picoarch (`git -C ~/sf3000-work/picoarch rev-parse HEAD` → `f8ff5ba`).
7. Poblar `sdcard/cubegm` staging drivers/libs (o build libs desde SDK).

No se corrigió nada en B1 — solo auditoría.

---

## 13. B1.5 — Upstream Reconciliation (2026-08-23)

**Correcciones sobre B1 ORIGINAL FINDING (ver `docs/dev/UPSTREAM_REPOSITORY_MAP.md`):**

- **B1 ORIGINAL:** `PICOARCH` `TYRQUAKE` `GPSP` etc. “externos/unpinned/unknown, no localizables” → **B1.5 RESOLVED:** `tzubertowski/TreeFrogUI_picoarch` existe público (`r36sx` única branch, `0` tags, `e98af36` HEAD 2026-08-23 vs local `f8ff5ba` 2026-07-29) — localizable **YES**, pero v1.0.15 no pinnea SHA (confianza **LOW**, ventana 07-29 – 08-23). `gpsp_multicore` public **YES** (`master` + 4 branches), dual con `libretro/gpsp`. `libretro-tyrquake` fork existe (`master` 2026-03-09) pero **v1.0.15 usa `libretro/tyrquake` generic** — fork no relevante (B1 overcount).
- **B1 ORIGINAL:** `12` forks tzubertowski en v1.0.15 → **B1.5 RESOLVED:** `9` forks realmente usados (`fceumm`, `snes9x2005/2002`, `libretro-gambatte`, `gpsp_multicore`, `libretro-frodo`, `fake-08#sf3000`, `libretro-blueMSX`, `libretro-fceumm`) — `QuickNES_Core`, `nestopia`, `libretro-vice` **no** usan fork tzubertowski en v1.0.15 (usan `libretro/*` upstream) — ver `UPSTREAM_REPOSITORY_MAP.md §2`.
- **B1 ORIGINAL:** `TOOLCHAIN` externo `game-de-it/sf3000` no verificado → **CONFIRMADO B1.5:** `game-de-it/sf3000` `sf3000_toolchain_v0.1` **HIGH** pin (release tag, no tzubertowski) — `FROGUI` `15ea12b` **HIGH** (submodule pin existe público `tzubertowski/FrogUI` `sf3000` branch, `4` tags).
- **B1 ORIGINAL:** Drivers sin source — **CONFIRMADO B1.5:** `0` repos driver con source en `71` tzubertowski repos (búsqueda `driver_r36sx` `disp_frame` etc. en GitHub API `GET /users/tzubertowski/repos` — solo `hijack/driver_sf3500.so` prebuilt stock, `98k` ELF MIPS) — `PROPRIETARY` se mantiene.
- **B1 ORIGINAL:** Stock SD dumps necesarios — **CONFIRMADO B1.5:** `0` repos `*_sdcard` públicos; `R36SX_SETTING_XML_PUBLIC=PARTIAL` (solo stock dump), `STOCK_DUMP_STILL_REQUIRED=YES`.
- **R36SX mínimo:** B1 no redujo; **B1.5 RESOLVED:** `~15-16` repos externos para R36SX V2.6 (vs `78` full) — ver `UPSTREAM_REPOSITORY_MAP.md §15` (FrogUI + picoarch + hijack + toolchain + ~12 cores críticos, excluye SF3000/SF3500/GB350 drivers y cores opcionales `vitaquake2/rockbox/ebook`).

**No se modificó código productivo en B1.5 (solo docs/dev).**
