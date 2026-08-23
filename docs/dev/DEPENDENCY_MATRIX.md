# DEPENDENCY_MATRIX.md — Matriz de Dependencias TreeFrogUI R36SX V2.6 — Fase B1

**Fecha:** 2026-08-23 — `CLASS B` READ-ONLY, no install, no clone, no build, no commit
**Baseline:** `v1.0.15` (`27f3bf33e906d90e0cd267059bf0559afc6f8a05`) → `r36sx-v2.6-dev` `2e5ffa80c32e7a9d644ad8e80eb2bb8314f3484d`
**WSL:** `Ubuntu-24.04` `x86_64` WSL `2.7.11.0`, `make 4.3` `gcc 13.3.0` `cmake MISSING` `python 3.12.3`
**Toolchain WSL:** `/home/dafunknoise/sf3000-work/sf3000toolchain/mipsel-buildroot-linux-gnu_sdk-buildroot` — `mips-mti-linux-gnu-gcc 6.3.0` `mips-mti-linux-gnu` PRESENT

---

## 1. Resumen de Conteos

| Métrica | Valor | Evidencia |
|---------|-------|-----------|
| **CORE_COUNT** | `78` | `grep -c '^clone ' clone_cores.sh` |
| **CORES_PINNED_COUNT** | `1` (solo `fake-08#sf3000`) | `clone fake-08 ... sf3000` es único con branch pin; resto `--depth=1` sin tag |
| **CORES_UNPINNED_COUNT** | `77` | `78 - 1` |
| **CORES_UNKNOWN_REVISION_COUNT** | `78` (ninguno con commit SHA pin) | `clone_cores.sh` no registra `git rev-parse HEAD` |
| **HARDCODED_PATH_COUNT** | `11` en `build_release.sh` (`/home/tomaszz/sf3000-work`) + `1` en `apps/*/Makefile` + `1` en `frogui/build_libretro.sh` + `4` en `deploy*.sh` | `grep -c "/home/tomaszz" build_release.sh = 11` |
| **PREBUILT_BINARY_COUNT** (repo) | `2` (`hijack/driver_sf3500.so`, `hijack/libemu_tfhijack.so`) | `find . -name "*.so" -not -path "./.git/*" | grep -v venv` |
| **UNKNOWN_PREBUILT_COUNT** (repo) | `1` (`driver_sf3500.so` sin source) | ver matriz |
| **PROPRIETARY_DEPENDENCY_COUNT** | `8` (7 `*_sdcard` stock dumps + `driver_sf3500.so` stock) | `build_release.sh:STOCK[]` 7 entries |
| **HOST_TOOLS_MISSING** | `1` (`cmake`) | `command -v cmake` → NO |

---

## 2. Matriz Principal

| Component | Source | Revision | Pinned | Toolchain | Prebuilt | Provenance | License | Reproducible now | Blocker |
|-----------|--------|----------|--------|-----------|----------|------------|---------|------------------|---------|
| **FrogUI** | `tzubertowski/FrogUI` `sf3000` submodule `frogui/` | `15ea12bb4f6f642b1ec02aabebbad33e5e95ed2b` (`v0.1.3-123-g15ea12b`, log `Add System View`) | **YES** (submodule) | `mips-mti-linux-gnu-gcc 6.3.0` + `SYSROOT` (`-mips32r2 -mtune=24kc -EL` en `frogui/build_libretro.sh`) | NO (source-only) | `git submodule status` + `git -C frogui log -1` | CC BY-NC-SA 4.0 (ver `LICENSE.md`, `frogui/LICENSE`) | **PARTIAL** (source pinned sí, pero `frogui/build_libretro.sh:6 cd /home/tomaszz/sf3000-work/FrogUI` hardcode falla; con fix `$REPO/frogui` sería YES) | `FROGUI_BUILD_SCRIPT_HARDCODED_PATH` |
| **Picoarch** | `tzubertowski/TreeFrogUI_picoarch` `r36sx` | `f8ff5ba99968c6c5945dbf0459e88be4bb421ed6` (HEAD `r36sx`, log `Pause-menu battery...`) | **NO** (branch `r36sx`, no tag/SHA pin en `build_release.sh` — solo path `/home/tomaszz/.../picoarch/picoarch`) | `mips-mti-linux-gnu-gcc 6.3.0` (`-mips32r2 -mtune=74kc -mdspr2` via `build_sf3000.sh`) | **YES** prebuilt en `~/sf3000-work/picoarch/picoarch` (`ELF MIPS EXEC` 416820 bytes, stripped) | `ls -la ~/sf3000-work/picoarch` + `git -C ~/sf3000-work/picoarch rev-parse HEAD` + `readelf` | BSD-3 + libpicofe GPL2/LGPL2/MAME | **MAYBE** (source presente en `~/sf3000-work/picoarch`, reproducible si se pinnea `f8ff5ba` y se parametriza `build_release.sh:PICOARCH`) | `PICOARCH_PATH_HARDCODED` + `NOT_IN_REPO_SUBMODULE` |
| **Tyrquake** | `tzubertowski/tyrquake-og` (?) no repo explícito | UNKNOWN | NO | `mips-mti-linux-gnu-gcc` | YES prebuilt path `~/sf3000-work/tyrquake-og/tyrquake_libretro.so` | Solo `build_release.sh:TYRQUAKE=/home/tomaszz/.../tyrquake_libretro.so`, no `clone_cores.sh` entry | GPL | **NO** (path no portable, no source en `cores/`) | `TYRQUAKE_PATH_UNKNOWN_REPO` |
| **Hijack — libemu_tfhijack.so** | `hijack/tfhijack.c` + `tfexec.c` + `libretro.h` | Rev del repo (baseline `2e5ffa8`) | YES (versionado) | `mips-mti-linux-gnu-gcc 6.3.0` (`-mips32r2 -mtune=74kc -EL -fPIC -shared`, `hijack/build_tfhijack.sh`) | **YES** prebuilt `hijack/libemu_tfhijack.so` (`ELF MIPS SO` 6148 bytes, LSB, MIPS32r2 EL o32, stripped) — **reconstruible** | `hijack/build_tfhijack.sh` + `file`/`readelf` muestra `MIPS32r2 EL` | MIT? (ver header) | **YES** (si toolchain presente — `build_tfhijack.sh` lo construye) | NONE (con toolchain) |
| **Hijack — nosleep** | `hijack/nosleep.c` | Rev del repo | YES | `mips-mti-linux-gnu-gcc` (`-O2 -EL --sysroot`) | **YES** tras build `hijack/nosleep` (no versionado prebuilt, generado) | `hijack/build_tfhijack.sh` segunda mitad | MIT | **YES** | NONE |
| **Hijack — driver_sf3500.so (reference)** | **UNKNOWN** (no `driver_sf3500.c` en repo) | — | NO | — | **YES** prebuilt `hijack/driver_sf3500.so` (`ELF MIPS SO` 98216 bytes, LSB, MIPS32r2 EL o32, **not stripped**, `with debug_info`) | Prebuilt stock — comentario `build_release.sh: SF3500/HD/SF3100 byte-identical encrypted driver.so ... identical config` — proveniencia stock dump, byte-identical a SF3500/HD/SF3100 | Proprietary Stock (no GPL) | **NO** (sin source) | `NO_SOURCE` |
| **R36SX Driver — driver_r36sx.so / driver_r36sx27.so** | **UNKNOWN** (no source en repo) | — | NO | — | **YES** prebuilt externo `~/sf3000-work/driver*.so` (`driver.so` 98216, `driver_gb350.so` 98348, `driver_r36sx27.so` 98216 — análisis sueltos) + esperado en `sdcard/cubegm/driver_r36sx.so` (staging, gitignored, **ausente** en checkout) | Stock SD dump propietario (ver `build_release.sh:STOCK[r36sx]=/home/tomaszz/.../R36SX_sdcard/cubegm`) — no redistribuible, no source | Proprietary Stock | **NO** (no reconstruible) | `STOCK_PROPRIETARY_NO_SOURCE` |
| **Toolchain SDK** | `game-de-it/sf3000` `sf3000_toolchain_v0.1` | `Codescape GNU Tools 2018.09-02 for MIPS MTI Linux` `6.3.0` | **YES** (release tag `sf3000_toolchain_v0.1`) | — (es el toolchain) | **YES** SDK prebuilt `mipsel-buildroot-linux-gnu_sdk-buildroot.tar.gz` (1.3 GB, 2024-10-30) + extracted | `README.md:280` link, `ls -la ~/sf3000-work/sf3000toolchain` + `mips-mti-linux-gnu-gcc --version` | GPL (Codescape) | **YES** (descargable reproducible) | NONE (presente en WSL) |
| **Cores — 78 total** | `clone_cores.sh` — 12 tzubertowski forks (`libretro-fceumm`, `snes9x2005`, `snes9x2002`, `libretro-gambatte`, `gpsp_multicore`, `fake-08#sf3000`, etc.) + 66 upstream libretro (`picodrive`, `mgba`, `Genesis-Plus-GX`, `tyrquake`, `prboom`, `mame2000`, `fbalpha2012_*`, `FBNeo`, `stella2014`, `prosystem`, `nestopia`, `Gearboy`, `PokeMini`, ... `sf2000-uae`, `sf2000-atarist`, `pico-286`, `TIC-80`) | **NO** — `git clone --depth=1` sin branch/tag/commit pin (excepto `fake-08` con `sf3000` branch) | **NO** (77/78 unpinned, 1 branch-only) | `mips-mti-linux-gnu-gcc` via `.toolchain/mips-gcc` wrappers (`-Ofast`/`-O3`/`fba` variants, `build_all.sh:SF3000_FLAGS`) | NO (source clones) | `clone_cores.sh` URLs | Varía por core (GPL/LGPL/BSD/MIT/MAME, ver `cores.md`) | **NO** (unpinned — no reproducible a SHA exacto; con `$WRAP` + `patches/*.patch` (11 patches) sí compila, pero no bite-identical sin pins) | `CORES_UNPINNED_77` |
| **Cores — Patches (11)** | `patches/*.patch` | Rev del repo (`2e5ffa8`) | YES (versionados) | — (aplicados en `build_all.sh:_apply_patch`) | NO | `patches/ardens-sf3000.patch` etc. (ver `build_all.sh:_apply_patch` 11 calls) | MIT/GPL | **YES** (si cores clonados) | NONE |
| **Apps — video_player / image_viewer** | `apps/video_player/*.c`, `apps/image_viewer/*.c` | Rev del repo | YES | `mips-mti-linux-gnu-gcc` (`apps/*/Makefile:TOOLCHAIN ?= /home/tomaszz/...`) | **YES** binario esperado `cubegm/video_player` etc. en staging (si `make -C apps/...`) | `apps/*/Makefile` con `TOOLCHAIN ?= /home/tomaszz/...` | GPL | **PARTIAL** (hardcoded fallback `/home/tomaszz`, pero `?=` permite override) | `HARDCODED_TOOLCHAIN_FALLBACK` |
| **Packaging — build_release.sh** | `build_release.sh` | Rev `2e5ffa8` | YES | — (no compila, solo copia/staging) | NO (genera `release/latest/release/`) | `build_release.sh` (424 líneas) | CC BY-NC-SA 4.0 | **NO** (requiere STOCK dumps + staging + hardcoded paths) | `HARDCODED_11` + `STOCK_MISSING` + `STAGING_DRIVERS_MISSING` |
| **Packaging — libs target** | `sdcard/cubegm/lib/libSDL-1.2.so.0` etc. | UNKNOWN (prebuilt en staging) | NO | — | **YES** prebuilt `libSDL-1.2.so.0`, `libpng12.so.0`, `libpng16.so.16` | Stock o SDK (no source) | LGPL | **UNKNOWN** | `PREBUILT_LIB_NO_SOURCE` |
| **Assets — system-icons / icon-packs / theme** | `assets/system-icons`, `assets/icon-packs`, `frogui/fonts` | Rev `2e5ffa8` + Art Book Next `assets/system-icons` (CC BY-NC-SA 4.0) | YES | — | NO (png/svg) | `assets/icon-packs/README.md`, `theme.md` | CC BY-NC-SA 4.0 (Art Book Next) | **YES** | NONE |
| **Stock SD dumps (7 devices)** | No repo — backups Google Drive (`install.md` links: `R36SX v2.6 Minimal Backup` etc. + `Q-ta-s/q-ta-s.github.io` for SF3000) | — | — | — | **YES** prebuilt stock `setting.xml`, `config.xml`, `filelist.csv`, `xgame-logo.bmp`, `driver.so` por device | `/home/tomaszz/sf3000-work/*_sdcard/cubegm` (ver `build_release.sh:STOCK[]`) — proprietário, no redist, `driver.so` plain ELF vs encrypted SF3500-family | Proprietary Stock | **NO** | `PROPRIETARY_STOCK_7` |

---

## 3. Detalle por Core (ejemplo, 78 total — ver `clone_cores.sh` lista completa)

| CORE | REPOSITORY | CLONE_URL | BRANCH/TAG | PINNED | PATCHES | BUILD_COMMAND (wrapper) | OUTPUT | LICENSE | REPRODUCIBLE_NOW |
|------|------------|-----------|------------|--------|---------|-------------------------|--------|---------|------------------|
| `fceumm` | `tzubertowski/libretro-fceumm` | `https://github.com/tzubertowski/libretro-fceumm` | `HEAD` `--depth=1` | NO | NO | `make -C cores/fceumm -f Makefile.libretro CC=$WRAP/mips-gcc` | `fceumm_libretro.so` | GPL | NO (unpinned) |
| `snes9x2005` | `tzubertowski/snes9x2005` | `.../snes9x2005` | `HEAD` | NO | NO | `CC=$WRAP/mips-gcc-O3` | `snes9x2005_plus_libretro.so` | GPL | NO |
| `gpsp` | `tzubertowski/gpsp_multicore` | `.../gpsp_multicore` | `HEAD` | NO | NO | `CC=$WRAP/gpsp-gcc` (no arch flags) | `gpsp_libretro.so` | GPL | NO |
| `fake-08` | `tzubertowski/fake-08` | `.../fake-08` | `sf3000` | **BRANCH** (no SHA) | `?` | `CC=$WRAP/mips-gcc-O3` | `fake08_libretro.so` | MIT | PARTIAL (branch) |
| `picodrive` | `libretro/picodrive` | `.../picodrive` | `HEAD` | NO | NO | `CC=$WRAP/mips-gcc` | `picodrive_libretro.so` | MAME | NO |
| `geolith` | `libretro/geolith-libretro` | `.../geolith` | `HEAD` | NO | `geolith-no-lto.patch` | `CC=$WRAP/mips-gcc` + patch | `geolith_libretro.so` | GPL | NO |
| `mame2000` | `libretro/mame2000-libretro` | `.../mame2000-libretro` | `HEAD` | NO | `mame2000-load-failure.patch` | `CC=$WRAP/mips-gcc` + patch | `mame2000_libretro.so` | MAME | NO |
| `Ardens` | `tiberiusbrown/Ardens` | `.../Ardens` | `HEAD` | NO | `ardens-sf3000.patch` | `CC=$WRAP/mips-gcc` + patch | `ardens_libretro.so` | MIT | NO |
| `pico-286` | `xrip/pico-286` | `.../pico-286` | `HEAD` | NO | `pico286-sf3000.patch` (87k) | `TC=$HOME/...` `pico-286` build | `pico286` | GPL | NO |
| `TIC-80` | `nesbox/TIC-80` | `.../TIC-80` | `HEAD` | NO | NO | `cmake` → `libretro` (requires `cmake`) | `tic80_libretro.so` | MIT | **NO** (`cmake` MISSING en WSL) |
| `sf2000-uae` | `angree/sf2000-uae-amiga-emulator` | `.../sf2000-uae...` | `HEAD` | NO | `uae-posix-fs.patch`, `uae-sf3000-fixes.patch` | `CC=$WRAP/mips-gcc` + patches | `uae_libretro.so` | GPL | NO |
| … (68 más) | … | … | `HEAD` `--depth=1` | NO | Ver `patches/` lista (11) | `build_all.sh:_b` + wrappers | `*_libretro.so` | — | NO |

**Total:** `78`, **Pinned:** `1` (`fake-08#sf3000` branch), **Unpinned:** `77`, **Unknown revision:** `78` (ninguno con SHA). Reproducible solo si se registra `git rev-parse HEAD` tras `clone_cores.sh`.

---

## 4. Prebuilt vs Stock (clasificación)

| FILE | TYPE | ARCH | PURPOSE | SOURCE_AVAILABLE | PROVENANCE | CLASS | REPRODUCIBLE | REDISTRIBUTABLE |
|------|------|------|---------|-----------------|------------|-------|--------------|-----------------|
| `hijack/libemu_tfhijack.so` | `ELF MIPS SO stripped` | MIPS32r2 EL o32 | hijack | YES (`tfhijack.c`) | `hijack/build_tfhijack.sh` (mips-gcc) — **A** | YES | YES |
| `hijack/driver_sf3500.so` | `ELF MIPS SO not stripped` | MIPS32r2 EL o32 | driver SF3500 ref | NO | Stock dump byte-identical SF3500/HD/SF3100 — **D/F** | NO | NO (proprietary) |
| `hijack/tfexec` | `ELF` | MIPS? | rkgame exec forwarder | YES (`tfexec.c`) | `hijack/build_tfhijack.sh` — **A** | YES | YES |
| `hijack/nosleep` | `ELF MIPS EXEC stripped` | MIPS | live-patcher sleep | YES (`nosleep.c`) | `hijack/build_tfhijack.sh` — **A** | YES | YES |
| `sdcard/cubegm/lib/*` | `ELF MIPS SO` | MIPS | SDL/png libs | NO | Prebuilt staging — **D** | UNKNOWN | YES (LGPL) |
| `~/sf3000-work/picoarch/picoarch` | `ELF MIPS EXEC stripped` | MIPS32r2 EL | frontend | YES (`~/sf3000-work/picoarch/*.c`) | External `r36sx` branch `f8ff5ba` — **B/C** | MAYBE (pin) | YES (BSD) |
| `~/sf3000-work/sf3000toolchain/.../mips-mti-linux-gnu-gcc` | `ELF x86_64` | x86_64 | cross compiler | SDK tarball — **D** | `game-de-it/sf3000` `sf3000_toolchain_v0.1` | YES | YES |
| `~/sf3000-work/driver*.so` | `ELF MIPS` | MIPS | drivers stock análisis | NO | Stock dump — **F** | NO | NO |

Clases: `A=buildable from source in this repo` `B=buildable from pinned external source` `C=external source exists but revision unpinned` `D=prebuilt known provenance` `E=prebuilt unknown provenance` `F=Stock/proprietary/non-redistributable`.

---

## 5. Hardcoded Paths (origen: `build_all.sh`, `build_release.sh`, `apps/*/Makefile`, `frogui/build_libretro.sh`, `deploy*.sh`)

| FILE | LINE | PATH_REFERENCE | PURPOSE | REQUIRED_FOR_BUILD | REQUIRED_FOR_PACKAGING | HOST_SPECIFIC | SOURCE_AVAILABLE | FUTURE_PARAMETERIZATION |
|------|------|----------------|---------|--------------------|------------------------|---------------|------------------|--------------------------|
| `build_release.sh:35` | `PICOARCH=/home/tomaszz/sf3000-work/picoarch/picoarch` | PICOARCH binary | NO (build) | **YES** (staging) | YES (`/home/tomaszz`) | YES (external binary) | YES (`$HOME`/`$REPO`) |
| `build_release.sh:36` | `PICOARCH_HI=.../picoarch_hi` | PICOARCH_HI | NO | YES | YES | YES | YES |
| `build_release.sh:37` | `FROGUI=/home/tomaszz/sf3000-work/FrogUI/frogui_libretro.so` | FrogUI libretro | NO (build tras submodule) | YES | YES | YES (external build) | YES (`$REPO/frogui`) |
| `build_release.sh:38` | `TYRQUAKE=.../tyrquake-og/...` | Tyrquake | NO | YES (optional) | YES | UNKNOWN | YES? |
| `build_release.sh:42` | `STOCK[r36sx]=/home/tomaszz/.../R36SX_sdcard/cubegm` | Stock R36SX | NO | YES | YES | NO (propietario) | **NO** (propietario, requiere backup) |
| `build_release.sh:48-64` | `STOCK[...6 más]` | Stock SF3000-family/GB350 | NO | YES (7 devices) | YES | NO | NO |
| `build_all.sh:38` | `TOOLCHAIN="$HOME/sf3000-work/..."` | Toolchain | **YES** | NO | NO (`$HOME` portable) | YES (SDK) | **ALREADY OK** (`$HOME`) |
| `apps/*/Makefile:1` | `TOOLCHAIN ?= /home/tomaszz/...` | Toolchain fallback | YES | NO | YES | YES | YES (`?=` permite override) |
| `frogui/build_libretro.sh:6` | `cd /home/tomaszz/sf3000-work/FrogUI` | FrogUI build chdir | **YES** (frogui) | NO | YES | YES | YES (`$REPO/frogui`) |
| `deploy_device.sh:18` | `WORK=/home/tomaszz/sf3000-work` | Workspace | NO | YES (deploy) | YES | YES | YES |
| `deploy.sh:4`, `deploy_r36sx.sh:4` | `exec /home/tomaszz/...` | Deploy wrappers | NO | YES | YES | YES | YES |

**HARDCODED_PATH_COUNT (build_release.sh) = 11** (`/home/tomaszz` refs) — documentado en `build_release.sh:35-64`. `~/sf3000-work` refs = `0` en ese script (usa absoluto), pero `build_all.sh` usa `$HOME` (portable).

---

## 6. Matriz de Reproducibilidad por Componente

| COMPONENT | SOURCE_AVAILABLE | SOURCE_PINNED | TOOLCHAIN_REQUIRED | TOOLCHAIN_AVAILABLE | BUILD_INSTRUCTIONS_AVAILABLE | HOST_PATH_DEPENDENCY | PREBUILT_DEPENDENCY | REPRODUCIBLE_NOW | BLOCKER |
|-----------|-----------------|---------------|--------------------|---------------------|------------------------------|----------------------|---------------------|------------------|---------|
| **FrogUI** | YES | YES `15ea12b` | YES `mips-gcc` | YES `6.3.0` | YES (`frogui/build_libretro.sh`, `Makefile.sf3000` en repo root) | YES (`/home/tomaszz` hardcode) | NO | **PARTIAL** | `BUILD_SCRIPT_HARDCODED` |
| **Picoarch** | YES (`~/sf3000-work/picoarch` f8ff5ba) | NO (branch `r36sx`, no pin en `build_release.sh`) | YES | YES | YES (`build_sf3000.sh`, `build_picoarch_hi.sh`) | YES (`/home/tomaszz` path) | YES prebuilt `picoarch` (MIPS EXEC) | **PARTIAL** | `PIN_MISSING + PATH_HARDCODED` |
| **Tyrquake** | UNKNOWN | NO | YES | YES | UNKNOWN | YES | YES prebuilt path | **NO** | `NO_REPO` |
| **Hijack (tfhijack/nosleep)** | YES | YES | YES | YES | YES (`hijack/build_tfhijack.sh`) | NO (usa `$HOME`) | YES prebuilt `libemu_tfhijack.so` reconstruible | **YES** | NONE (con toolchain) |
| **Hijack driver_sf3500** | NO | — | — | — | NO | NO | YES prebuilt `driver_sf3500.so` stock | **NO** | `NO_SOURCE` |
| **R36SX Driver (driver_r36sx.so)** | NO | — | — | — | NO | YES (`STOCK` dump) | YES prebuilt externo + staging ausente | **NO** | `STOCK_PROPRIETARY` |
| **Cores — 78** | YES (tras `clone_cores.sh`) | NO (77 unpinned, 1 branch) | YES (`mips-gcc` wrappers) | YES (cmake solo TIC-80) | YES (`build_all.sh`, `patches/`) | NO (`$HOME` portable) | NO | **NO** (unpinned) | `CORES_UNPINNED` + `cmake missing` |
| **Cores — TIC-80** | YES | NO | YES | **NO** (`cmake` missing) | YES (cmake) | NO | NO | **NO** | `cmake missing` |
| **Toolchain SDK** | SDK tarball | YES (`sf3000_toolchain_v0.1`) | — | YES (1.3 GB tar + extracted) | YES (`README.md`) | NO | YES SDK | **YES** | NONE |
| **Apps video/image** | YES | YES | YES | YES | YES (`apps/*/Makefile` `?=` ) | YES (fallback) | NO | **PARTIAL** | `HARDCODED_FALLBACK` |
| **Packaging (build_release.sh)** | YES (script) | YES | NO (solo cp) | — | YES | **YES** (`/home/tomaszz` 11, `STOCK` 7) | YES (STOCK + staging drivers) | **NO** | `HARDCODED_11 + STOCK_MISSING + STAGING_DRIVERS_MISSING` |
| **Assets/themes** | YES | YES | NO | — | NO | NO | NO | **YES** | NONE |

**Separación estricta:**
- **SOURCE_REPRODUCIBLE** = `PARTIAL` (FrogUI pinned YES, cores NO, picoarch NO, drivers NO)
- **BUILD_REPRODUCIBLE** = `PARTIAL` (toolchain presente YES, host tools OK excepto cmake, pero hardcodes + stock dumps bloquean)
- **PACKAGE_REPRODUCIBLE** = `NO` (requiere `BUILD` + staging drivers + stock dumps + hardcoded paths)
- **PHYSICAL_VALIDATED** = `NO` (`PHYSICAL_EVIDENCE=NONE — NOT TESTED`, `RELEASE_EVIDENCE=NONE — NOT TESTED`)

---

## 7. Próximos Pasos No Ejecutados (B1)

- `.gitattributes` eol=lf
- `sudo apt install cmake` (TIC-80)
- Parametrizar `build_release.sh` → `$HOME/sf3000-work` / `$STOCK_ROOT`
- Pinnear cores (`git rev-parse HEAD > cores/<name>.pin`)
- Pinnear picoarch (`f8ff5ba`)
- Documentar provisión stock dumps (links `install.md` — ya documentados, pero no mocks)

No se instaló, clonó ni compiló nada en esta fase.

---

## 8. B1.5 — Upstream Reconciliation (2026-08-23)

**Correcciones sobre B1 ORIGINAL FINDING (ver `docs/dev/UPSTREAM_REPOSITORY_MAP.md`):**

| Campo B1 | B1 ORIGINAL FINDING | B1.5 RESOLVED FINDING | Evidencia |
|----------|---------------------|------------------------|-----------|
| **Tyrquake** | `tzubertowski/tyrquake-og` UNKNOWN (B1 fila: Tyrquake UNKNOWN, NO_REPO) | **B1.5 RESOLVED:** v1.0.15 `clone tyrquake https://github.com/libretro/tyrquake` — **generic libretro**, no fork tzubertowski. `tzubertowski/libretro-tyrquake` existe (`master` 2026-03-09, 1 star) pero **NO usado** en v1.0.15. Reproducible **PARTIAL** (source público libretro, unpinned, sin patch). | `git show v1.0.15:clone_cores.sh \| grep tyrquake` + API `GET /repos/tzubertowski/libretro-tyrquake` |
| **Cores tzubertowski fork count** | `12` forks | **9** forks realmente usados en v1.0.15 (`fceumm`, `libretro-fceumm`, `snes9x2005`, `snes9x2002`, `libretro-gambatte`, `gpsp_multicore`, `libretro-frodo`, `fake-08#sf3000`, `libretro-blueMSX`) — `QuickNES_Core`, `nestopia`, `libretro-vice` usan **upstream** `libretro/*` en v1.0.15, no fork tzubertowski (B1 overcount 3) | `git show v1.0.15:clone_cores.sh` vs `GET /repos/tzubertowski/*` 71 repos enum |
| **QuickNES / nestopia / vice** | Clasificados como `TZUBERTOWSKI_FORK` | **B1.5 CORREGIDO:** `UPSTREAM_GENERIC` (v1.0.15 usa `libretro/QuickNES_Core`, `libretro/nestopia`, `libretro/vice-libretro`; forks tzubertowski existen pero no usados) | `git show v1.0.15:clone_cores.sh` |
| **Picoarch pin** | `f8ff5ba` plausible pero UNKNOWN | **B1.5 RESOLVED:** `tzubertowski/TreeFrogUI_picoarch` public **YES** (`r36sx` única branch, `0` tags, `e98af36` HEAD 2026-08-23 vs local `f8ff5ba` 2026-07-29) — ventana v1.0.15 (2026-08-17) cae entre ambos; confianza **LOW** (no pin en treefrog-ui). | API `GET /repos/tzubertowski/TreeFrogUI_picoarch`, `git ls-remote`, fechas `f8ff5ba 2026-07-29` vs `27f3bf3 2026-08-17` vs `e98af36 2026-08-23` |
| **FrogUI** | `15ea12b` pinned YES | **CONFIRMADO B1.5:** `tzubertowski/FrogUI` public **YES** (`4` branches `sf3000/r36sx`, `4` tags `v0.1.3..`, `15ea12b` 2026-08-07 `Add System View` existe público) — `FROGUI_PUBLIC_SOURCE=YES`, `FROGUI_EXACT_REVISION_KNOWN=YES` | `GET /repos/tzubertowski/FrogUI`, `git ls-remote` 15ea12b |
| **PCSX** | `pcsx4all` YES, `pcsx_rearmed` UNKNOWN | **B1.5 RESOLVED:** `PCSX4ALL_PUBLIC_SOURCE=YES` (`tzubertowski/TreeFrogUI_pcsx4all` `main` 2026-07-29) usado en v1.0.15 (`git show v1.0.15:README.md:301`); `PCSX_REARMED_PUBLIC_SOURCE=YES` (`TreeFrogUI_pcsx_rearmed` `master` 2026-06-22 Lightrec) existe pero **MAYBE** no clon en `clone_cores.sh` v1.0.15 (es standalone) | API `GET /repos/.../TreeFrogUI_pcsx*` + `git show` |
| **GPSP** | `gpsp_multicore` YES | **CONFIRMADO + DUAL:** v1.0.15 es **dual**: `tzubertowski/gpsp_multicore` (`master` + 4 branches `andy-backports` etc. 2026-05-06) **Y** `libretro/gpsp` upstream — **B1 ya correcto, B1.5 añade branch detail** | `git show v1.0.15:clone_cores.sh` dual + API |
| **Toolchain** | `game-de-it/sf3000` HIGH | **CONFIRMADO B1.5:** `TOOLCHAIN_PUBLIC_SOURCE=YES` `game-de-it/sf3000` `sf3000_toolchain_v0.1` (no tzubertowski), `TOOLCHAIN_PINNED=YES` (release tag) | `README.md:281` + API |
| **Drivers** | `NO_SOURCE` (B1 correcto) | **CONFIRMADO B1.5:** `0` repos driver source en `71` tzubertowski repos (búsqueda `driver_r36sx` etc. API) — solo `hijack/driver_sf3500.so` prebuilt stock (98k ELF MIPS) | `GET /users/tzubertowski/repos` 71 enum, `grep` 0 hits |
| **Stock SD** | `NO` public | **CONFIRMADO:** `0` repos `*_sdcard` públicos; `R36SX_SETTING_XML_PUBLIC=PARTIAL`, `STOCK_DUMP_STILL_REQUIRED=YES` | API + `build_release.sh:STOCK[]` |
| **Cores SHA** | `0` exact | **Sigue `0` exact**, pero **B1.5 mejora:** código **disponible** (9 forks + 58 generic + 8 patched = 71 public de 78) — no “unknown source”, solo “unpinned SHA” (77/78, solo `fake-08#sf3000` branch) | `clone_cores.sh` 78 + API 71 repos |

**Matriz reducida R36SX V2.6 mínimo (B1.5 §15-16):** `~15-16` repos externos (vs 78 full) — ver `UPSTREAM_REPOSITORY_MAP.md §15` (FrogUI + picoarch + 9 forks + 4 genéricos críticos + toolchain + `gpsp` dual, excluye SF3500/GB350 drivers y cores opcionales `vitaquake2/rockbox/ebook`).
