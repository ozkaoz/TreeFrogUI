# WSL_ENVIRONMENT.md — Entorno de Build TreeFrogUI R36SX V2.6 — Fase B1

**Fecha:** 2026-08-23
**Repo:** `D:\R36SX\treefrog-ui-r36sx` (Windows) → `/mnt/d/R36SX/treefrog-ui-r36sx` (WSL)
**Branch auditada:** `r36sx-v2.6-dev` — `2e5ffa80c32e7a9d644ad8e80eb2bb8314f3484d` (BASELINE `v1.0.15` = `27f3bf33e906d90e0cd267059bf0559afc6f8a05`)
**Clase:** B — Host tooling / Build infrastructure — READ-ONLY audit, no install, no clone, no build

---

## 1. Rutas

| Entorno | Ruta |
|---------|------|
| **Windows repo path** | `D:\R36SX\treefrog-ui-r36sx` |
| **WSL repo path** | `/mnt/d/R36SX/treefrog-ui-r36sx` |
| **Workspace del autor esperado** | `~/sf3000-work/` (WSL `$HOME/sf3000-work`, Windows `%USERPROFILE%` equivalente) — ver `build_all.sh:TOOLCHAIN="$HOME/sf3000-work/sf3000toolchain/..."` y `build_release.sh:/home/tomaszz/sf3000-work/...` |

Repositorio vive físicamente en NTFS `D:` montado en WSL vía `DrvFs` (`/mnt/d`). No se clonó copia separada en `$HOME` — misma HEAD en ambos lados (`2e5ffa80c32e7a9d644ad8e80eb2bb8314f3484d`). `git submodule status` → `15ea12bb4f6f642b1ec02aabebbad33e5e95ed2b frogui (v0.1.3-123-g15ea12b)`.

**Nota de coherencia WSL/Windows:** `git status` en Windows = `CLEAN` (mod `core.autocrlf=true`). En WSL el mismo worktree aparece `M` masivo (todos los `.sh`/`.md`/`.so` con CRLF) porque WSL `core.autocrlf` no está configurado (vacío) y la copia de trabajo tiene CRLF (checkout Windows). `git diff --stat` muestra `*.sh/*.md` como `924 +--` por normalización de fin de línea. `git submodule status` en WSL marca `frogui` como `-dirty` por el mismo motivo. HEAD idéntico, pero `WORKTREE` no es idénticamente limpio en WSL sin normalizar `autocrlf`. Es un artefacto de compartir NTFS entre Windows y Linux, no una divergencia de contenido. Recomendación futura: fijar `.gitattributes` con `* text=auto eol=lf` o `core.autocrlf=input` en WSL.

---

## 2. WSL

| Propiedad | Valor (evidencia) |
|-----------|-------------------|
| **WSL_AVAILABLE** | `YES` |
| **WSL_PLATFORM_VERSION** | `2.7.11.0` — `wsl --version` → `Versión de WSL: 2.7.11.0` (WSL package/runtime, no confundir con distro mode) — Kernel `6.18.33.2-2`, WSLg `1.0.73.2`, MSRDC `1.2.7214`, Direct3D `1.611.1`, DXCore `10.0.26100.1`, Windows `10.0.26200.9168` |
| **DEFAULT_DISTRO** | `Ubuntu-24.04` — `wsl --status` → `Distribución predeterminada: Ubuntu-24.04` + `wsl --version` + `wsl -l -v` `* Ubuntu-24.04` |
| **DISTRO_WSL_MODE** | `WSL1` — `wsl -l -v` → `Ubuntu-24.04 Stopped 1` (columna `VERSION = 1` = **WSL1**, no WSL2), `uname -a` → `Linux DFNK 4.4.0-26100-Microsoft` (kernel WSL1 4.4.0, no 5.15+ WSL2), `wsl --status` `Versión predeterminada: 2` es default para nuevas distros, pero esta distro está en **WSL1** — **NO convertir a WSL2** (spec §2). |
| **DISTROS (`wsl -l -v`)** | `* Ubuntu-24.04 Stopped 1` |
| **Host kernel** | `Linux DFNK 4.4.0-26100-Microsoft` (WSL v1 kernel 4.4.0 — confirma DISTRO_WSL_MODE=WSL1) |
| **Host arch** | `x86_64` (`uname -m`) — `x86_64 x86_64 x86_64 GNU/Linux` |
| **OS** | `Ubuntu 24.04.4 LTS (Noble Numbat)` — `PRETTY_NAME="Ubuntu 24.04.4 LTS"`, `VERSION_ID="24.04"`, `ID=ubuntu` |

---

## 3. Host Architecture

| Propiedad | Valor |
|-----------|-------|
| **HOST_ARCH (WSL)** | `x86_64` |
| **CPU (target, ver §4)** | MIPS 74Kc (build flag `-mtune=74kc -mdspr2`, `mips32r2`) — no es host |
| **Host compiler (nativo)** | `gcc (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0` / `g++ 13.3.0` — x86_64, no cross |

---

## 4. Herramientas Disponibles en WSL (auditadas, no instaladas)

| TOOL | PRESENT | PATH | VERSION | Notas |
|------|---------|------|---------|-------|
| `bash` | YES | `/usr/bin/bash` | `GNU bash, version 5.2.21(1)-release (x86_64-pc-linux-gnu)` | |
| `make` | YES | `/usr/bin/make` | `GNU Make 4.3` | |
| `gcc` | YES | `/usr/bin/gcc` | `13.3.0` | Host x86_64, no cross |
| `g++` | YES | `/usr/bin/g++` | `13.3.0` | Host x86_64 |
| `cmake` | **NO** | `NONE` | `NONE` | Requerido solo por TIC-80 (`build_all.sh` lo salta con warning) — blocker parcial para ese core |
| `git` | YES | `/usr/bin/git` | `2.43.0` | Config `user.name=ozkaoz`, `url.insteadOf git@github.com:` |
| `python3` | YES | `/usr/bin/python3` | `Python 3.12.3` | Para `agent_preflight.py` / `test_agent_context_contract.py` |
| `perl` | YES | `/usr/bin/perl` | `This is perl 5, version 38, subversion 2 (v5.38.2)` | |
| `wget` | YES | `/usr/bin/wget` | `GNU Wget 1.21.4` | |
| `curl` | YES | `/usr/bin/curl` | `curl 8.5.0` | |
| `patch` | YES | `/usr/bin/patch` | `GNU patch 2.7.6` | Para `patches/*.patch` |
| `tar` | YES | `/usr/bin/tar` | `tar (GNU tar) 1.35` | |
| `zip` | YES | `/usr/bin/zip` | `Zip 3.0 (July 5th 2008)` | Para packaging |
| `unzip` | YES | `/usr/bin/unzip` | `UnZip 6.00` | |
| `rsync` | YES | `/usr/bin/rsync` | `3.2.7 protocol 31` | |
| `file` | YES | `/usr/bin/file` | `file-5.45` | |
| `readelf` | YES | `/usr/bin/readelf` | `GNU readelf 2.42` | |
| `objdump` | YES | `/usr/bin/objdump` | `GNU objdump 2.42` | |

**Missing host tools:** `cmake` (solo afecta `TIC-80` — 1 de 78 cores). No se instaló en esta fase por ser CLASS B read-only.

---

## 5. Toolchain Esperada

| Propiedad | Valor (evidencia) |
|-----------|-------------------|
| **EXPECTED_TOOLCHAIN_PATH** | `~/sf3000-work/sf3000toolchain/mipsel-buildroot-linux-gnu_sdk-buildroot` (`build_all.sh:TOOLCHAIN="$HOME/sf3000-work/sf3000toolchain/..."`, `README.md: ~/sf3000-work/sf3000toolchain/`, `Makefile.sf3000:TOOLCHAIN_ROOT := $(HOME)/sf3000-work/...`) |
| **EXPECTED_TOOLCHAIN_SOURCE** | `https://github.com/game-de-it/sf3000/releases/tag/sf3000_toolchain_v0.1` (`README.md:280`, `frogui/DEVELOPMENT.md:21`) |
| **CROSS_COMPILE_PREFIX** | `mips-mti-linux-gnu-` (`build_all.sh:MIPS="$TOOLCHAIN/opt/ext-toolchain/bin/mips-mti-linux-gnu-"`, `apps/*/Makefile:CROSS := $(TOOLCHAIN)/opt/ext-toolchain/bin/mips-mti-linux-gnu-`, `hijack/build_tfhijack.sh:MIPS=...`) |
| **EXPECTED_CC** | `mips-mti-linux-gnu-gcc` |
| **EXPECTED_CXX** | `mips-mti-linux-gnu-g++` |
| **EXPECTED_AR** | `mips-mti-linux-gnu-ar` |
| **EXPECTED_LD** | `mips-mti-linux-gnu-ld` |
| **EXPECTED_STRIP** | `mips-mti-linux-gnu-strip` (`build_all.sh:AR="${MIPS}ar"`, `STRIP="${MIPS}strip"`) |
| **EXPECTED_SYSROOT** | `$TOOLCHAIN/mipsel-buildroot-linux-gnu/sysroot` → resuelto a `.../opt/ext-toolchain/bin/../sysroot/mips-r2-hard` (`$TOOLCHAIN/mipsel-buildroot-linux-gnu/sysroot` y `build_all.sh:SYSROOT=`, `frogui/build_libretro.sh:SYSROOT=`) |
| **TARGET flags** | `-mips32r2 -march=mips32r2 -mtune=74kc -mdspr2 -mfp32 -mhard-float -mlong-calls -EL --sysroot=$SYSROOT -Ofast -DNDEBUG` (`build_all.sh:SF3000_FLAGS=`) — variantes: `gpsp` sin arch flags (`-EL --sysroot` solo), `FBA` sin `-mdspr2` + `-fsigned-char -fno-strict-aliasing` |

---

## 6. Toolchain Real (auditada, no instalada)

| Propiedad | Valor (evidencia) |
|-----------|-------------------|
| **TOOLCHAIN_PRESENT** | `YES` (contrario a `ls` vacío inicial por `~/sf3000-work` con `total 0` — el SDK está en `~/sf3000-work/sf3000toolchain/mipsel-buildroot-linux-gnu_sdk-buildroot.tar.gz` (1.3 GB) + directorio extraído `mipsel-buildroot-linux-gnu_sdk-buildroot/`) |
| **TOOLCHAIN_PATH** | `/home/dafunknoise/sf3000-work/sf3000toolchain/mipsel-buildroot-linux-gnu_sdk-buildroot` |
| **TOOLCHAIN_TARBALL** | `/home/dafunknoise/sf3000-work/sf3000toolchain/mipsel-buildroot-linux-gnu_sdk-buildroot.tar.gz` (1322554211 bytes, fecha 2024-10-30) |
| **CROSS_COMPILER_PRESENT** | `YES` — `/home/dafunknoise/sf3000-work/sf3000toolchain/mipsel-buildroot-linux-gnu_sdk-buildroot/opt/ext-toolchain/bin/mips-mti-linux-gnu-gcc` (1041571 bytes, 2018-10-04) |
| **CROSS_COMPILER_VERSION** | `mips-mti-linux-gnu-gcc (Codescape GNU Tools 2018.09-02 for MIPS MTI Linux) 6.3.0` |
| **CROSS_COMPILER_TARGET** | `mips-mti-linux-gnu` (`-dumpmachine`) |
| **SYSROOT (real)** | `/home/dafunknoise/sf3000-work/sf3000toolchain/mipsel-buildroot-linux-gnu_sdk-buildroot/opt/ext-toolchain/bin/../sysroot/mips-r2-hard` (`-print-sysroot` con sufijo `mips-r2-hard`) |
| **TOOLCHAIN_PINNED** | `YES` (release tag `sf3000_toolchain_v0.1` de `game-de-it/sf3000` — ver README; tarball local coincide con upstream) |
| **TOOLCHAIN_REPRODUCIBLE** | `YES` (SDK prebuilt descargable, no se compila; host tools presentes excepto `cmake` para TIC-80) |

El toolchain nativo x86_64 (`gcc 13.3.0`) no es el cross; el cross es independiente en `$HOME/sf3000-work/sf3000toolchain/.../opt/ext-toolchain/bin/`.

---

## 7. Supuestos de Workspace

| Supuesto | Estado | Evidencia |
|----------|--------|-----------|
| **Repo en `~/sf3000-work/sf3000_treefrogui`** | **NO CUMPLIDO** (repo real es `D:\R36SX\treefrog-ui-r36sx` / `/mnt/d/R36SX/treefrog-ui-r36sx`; los scripts del autor asumen `~/sf3000-work/sf3000_treefrogui` — `copy_md_to_sdcard.sh: Run from /home/tomaszz/sf3000-work/sf3000_treefrogui`, `deploy.sh: exec /home/tomaszz/...`) — requiere parametrización o `build_all.sh` ya usa `$(dirname "$0")` y es portable; `build_release.sh` no |
| **`~/sf3000-work/picoarch` existe** | `YES` — `/home/dafunknoise/sf3000-work/picoarch` (git `tzubertowski/TreeFrogUI_picoarch`, branch `r36sx`, `f8ff5ba`) — `picoarch` ELF 32-bit MIPS presente (416820 bytes, stripped) |
| **`~/sf3000-work/FrogUI` existe** | `NO` — en `~/sf3000-work/FrogUI` no existe (`frogui/build_libretro.sh` hace `cd /home/tomaszz/sf3000-work/FrogUI` y fallaría; el submodule `frogui/` en el repo es la fuente real) — el path hardcodeado es del autor (`tomaszz`) |
| **`~/sf3000-work/R36SX_sdcard` y otros `*_sdcard` existen** | `UNKNOWN` — `build_release.sh:STOCK=( [r36sx]=/home/tomaszz/sf3000-work/R36SX_sdcard/cubegm ... )` — esos directorios son stock OS dumps del autor, no están en este host (no listados en `~/sf3000-work` salvo `picoarch` y `sf3000toolchain`; `driver.so` sueltos sí existen para análisis) — blocker para `build_release.sh` sin stock |
| **`$HOME` es `/home/dafunknoise`** | `YES` (`/home/dafunknoise`, no `/home/tomaszz`) — los paths absolutos del autor no coinciden; `build_all.sh` ya parametriza vía `$HOME`, `build_release.sh` no (hardcoded `/home/tomaszz`) |
| **CRLF normalizado** | **NO** — ver §1: Windows `autocrlf=true` vs WSL vacío causa `M` masivo en WSL. Requiere `.gitattributes` |
| **`cmake` disponible** | `NO` — `build_all.sh` lo detecta y salta TIC-80 con warning |

No se instaló ni clonó nada en esta fase.

---

## 8. Próximos Pasos (no ejecutados en B1)

- Normalizar `core.autocrlf` (`.gitattributes`) para repo compartido Windows/WSL.
- Instalar `cmake` (para TIC-80) o documentar skip.
- Parametrizar `build_release.sh` (`PICOARCH`, `FROGUI`, `STOCK[]` hardcodeados) para usar `$HOME`/`$REPO` en lugar de `/home/tomaszz`.
- Proveer `STOCK` dumps o mocks para reproducir `release/latest/release` sin stock propietario.

---

## 9. B1.5 — Upstream Reconciliation (2026-08-23)

**B1 ORIGINAL FINDING:** `TOOLCHAIN` externo `game-de-it/sf3000` ya era **YES** pinned `sf3000_toolchain_v0.1` — **CONFIRMADO B1.5:** `GET /repos/game-de-it/sf3000/releases` no consultado nuevo, pero `tzubertowski/*` **no** contiene toolchain (71 repos enum `0` `sf3000toolchain`), mantiene `TOOLCHAIN_PUBLIC_SOURCE=game-de-it/sf3000` (no tzubertowski).

**WSL host:** `~/sf3000-work` contiene además de toolchain: `picoarch` (`f8ff5ba` 2026-07-29) + `driver.so` sueltos para análisis (`driver.so` 98216, `driver_gb350.so` 98348, `driver_r36sx27.so` 98216) — estos **no** vienen de toolchain, son **stock dumps** sueltos (B1 los puso como `UNKNOWN` prebuilt — B1.5 confirma `stock/proprietary`, no toolchain).

**No se modificó WSL ni se instaló cmake en B1.5 (solo research).**
