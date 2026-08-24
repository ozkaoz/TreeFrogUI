# BUILDING.md — Cómo Compilar TreeFrogUI — R36SX V2.6 Fork

> **Canonical: WSL Ubuntu.** No compilar en PowerShell/Windows nativo salvo requisito Windows-only explícito.
> Workspace: `~/sf3000-work` (WSL `$HOME/sf3000-work`). Repo Windows `D:\R36SX\treefrog-ui-r36sx` → WSL `/mnt/d/R36SX/treefrog-ui-r36sx`.

## 1. Qué compila y dónde

| Componente | Repo / Path | Build output | Toolchain |
|------------|-------------|--------------|-----------|
| **FrogUI** (frontend) | `frogui/` submodule `tzubertowski/FrogUI@sf3000 15ea12b` + `~/sf3000-work/FrogUI` hermano (histórico) | `frogui_libretro.so` → `cubegm/cores/` | `mips-mti-linux-gnu-gcc 6.3.0` |
| **Picoarch** (libretro host, display/audio) | `~/sf3000-work/picoarch` (`tzubertowski/TreeFrogUI_picoarch@r36sx` f8ff5ba local, e98af36 upstream) | `picoarch`, `picoarch_hi` (hi para gpsp/pcsx) | mismo |
| **Cores** (57+ emuladores) | `cores/` (78 clones via `clone_cores.sh`) | `build/*.so` | wrappers `.toolchain/mips-gcc` |
| **Hijack** | `hijack/*.c` | `hijack/libemu_tfhijack.so`, `hijack/nosleep` | mismo |
| **Apps** | `apps/video_player`, `apps/image_viewer` | `cubegm/video_player`, `image_viewer` | mismo |
| **Pcsx4all** (PS1 standalone) | `~/sf3000-work` sibling (clone `TreeFrogUI_pcsx4all`) | `pcsx4all` | mismo |

Workspace esperado (upstream documenta `~/sf3000-work`):

```
~/sf3000-work/
├── treefrog-ui          ← este repo (si clonas upstream) o /mnt/d/R36SX/treefrog-ui-r36sx (fork WSL)
├── FrogUI               ← tzubertowski/FrogUI@sf3000 (opcional hermano, submodule frogui/ es fuente)
├── TreeFrogUI_picoarch  ← tzubertowski/TreeFrogUI_picoarch@r36sx
├── TreeFrogUI_pcsx4all  ← standalone PS1 (opcional)
├── cores/               ← 78 clones via clone_cores.sh (gitignored)
└── sf3000toolchain/     ← game-de-it/sf3000 sf3000_toolchain_v0.1 (mips-mti-linux-gnu-gcc 6.3.0)
```

Ver `README.md#Building from source`, `docs/dev/BUILD_ARCHITECTURE.md`, `docs/dev/UPSTREAM_REPOSITORY_MAP.md`.

## 2. Toolchain

- **SDK:** `game-de-it/sf3000` `sf3000_toolchain_v0.1` → `~/sf3000-work/sf3000toolchain/mipsel-buildroot-linux-gnu_sdk-buildroot`
  - `opt/ext-toolchain/bin/mips-mti-linux-gnu-gcc` 6.3.0 (Codescape 2018.09-02)
  - Sysroot `mipsel-buildroot-linux-gnu/sysroot` (real `.../opt/ext-toolchain/bin/../sysroot/mips-r2-hard`)
- **Ubicación esperada WSL:** `/home/<user>/sf3000-work/sf3000toolchain/mipsel-buildroot-linux-gnu_sdk-buildroot` (presente en host de referencia)
- Verificar: `~/sf3000-work/sf3000toolchain/.../mips-mti-linux-gnu-gcc --version` → `6.3.0`
- **No instalar** automáticamente — `tools/dev-doctor.sh` solo valida presencia.

## 3. Requisitos host

| Tool | Requerido | Versión host ref | Notas |
|------|-----------|------------------|-------|
| WSL Ubuntu 24.04 | **YES** | 24.04.4 LTS WSL1 4.4.0 | Canonical; `WSL Ubuntu is canonical` |
| `make` | **YES** | 4.3 | |
| `gcc` (host x86) | **YES** | 13.3.0 | solo host, no cross |
| `git` | **YES** | 2.43.0 | con `url.insteadOf` para SSH |
| `python3` | **YES** | 3.12.3 | `agent_preflight.py` |
| `cmake` | **OPTIONAL** | 3.28.3 (ahora presente) | Solo TIC-80 (`build_all.sh` skipea con warning si falta) |
| `7z` / `zip` / `unzip` | **YES** para release |  | `pack_release.sh` |
| `patch`, `tar`, `file`, `readelf` | **YES** | | |

Ver `tools/dev-doctor.sh` y `docs/dev/WSL_ENVIRONMENT.md`.

## 4. Clonar cores

```sh
# Desde WSL, en repo root /mnt/d/R36SX/treefrog-ui-r36sx
./clone_cores.sh      # 78 repos, --depth=1, solo fake-08#sf3000 pinned branch
ls cores/ | wc -l     # 77 unique destinos (dup libretro-prboom)
```

- `CORE_DECLARATION_COUNT=78`, `UNIQUE=77`, `PINNED=1` (branch only), `UNPINNED=77` — determinismo vía `deps/treefrog-v1.0.15.lock.json` (`historical_exactness=NOT_CLAIMED`).
- Validar lock: `python tests/test_dependency_lock.py`, `python scripts/dev/validate_dependency_lock.py`, `python scripts/dev/resolve_dependency_lock.py --check`.

## 5. Compilar

### Todo (recomendado)

```sh
./build_all.sh        # wrappers .toolchain/mips-gcc + patches/ (11 patches), output build/*.so
ls build/*.so | wc -l
```

Flags: `SF3000_FLAGS="-mips32r2 -march=mips32r2 -mtune=74kc -mdspr2 -mfp32 -mhard-float -mlong-calls -EL --sysroot=$SYSROOT -Ofast -DNDEBUG"` (ver `build_all.sh:53`).

Variantes: `gpsp` sin arch flags (`-EL --sysroot` solo), `FBA` sin `-mdspr2` + `-fsigned-char -fno-strict-aliasing`.

### Solo FrogUI

```sh
cd frogui
make -f Makefile.sf3000 frogui_libretro.so   # o frogui/build_libretro.sh (ver deuda abajo)
```

### Hijack

```sh
sh hijack/build_tfhijack.sh   # → hijack/libemu_tfhijack.so + nosleep
file hijack/libemu_tfhijack.so  # ELF 32-bit LSB MIPS32 rel2
```

### Apps

```sh
make -C apps/video_player
make -C apps/image_viewer
```

## 6. Inconsistencias conocidas (no corregir aquí)

```
BUILD_FLAG_CONSISTENCY=KNOWN_DEBT
```

| Script | Flag | Estado |
|--------|------|--------|
| `build_all.sh:53` | `-mtune=74kc -mdspr2` | Correcto (74Kc DSP2) |
| `Makefile.sf3000:14` | `-mtune=24kc` | **DEUDA** — 24kc legacy |
| `frogui/build_libretro.sh:6` | `-mtune=24kc` + `cd /home/tomaszz/...` hardcode | **DEUDA** |

No corregir silenciosamente — requiere test de reproducibilidad separado.

```
BUILD_PATH_PORTABILITY_STATUS=KNOWN_DEBT
```

Hardcoded `/home/tomaszz/sf3000-work` en: `build_release.sh:35-64` (11 refs: PICOARCH, PICOARCH_HI, FROGUI, TYRQUAKE, STOCK[7]), `frogui/build_libretro.sh:6`, `apps/*/Makefile:1` (`TOOLCHAIN ?=` fallback), `deploy*.sh:4` (`WORK=/home/tomaszz/...`). Documentado, **no modificado esta fase** (ver `AGENTS.md` corrección 3).

`build_all.sh:38` usa `$HOME` portable (OK), `hijack/build_tfhijack.sh:7` usa `$HOME` (OK).

## 7. Output

- `build/*.so` → copiar a `/mnt/sdcard/cubegm/cores/` (SD FAT32)
- `hijack/libemu_tfhijack.so` → `cubegm/cores/libemu_md.so` via `build_release.sh`
- `frogui/frogui_libretro.so`, `picoarch/picoarch*` → `sdcard/cubegm` staging → `release/latest/release` (gitignored)
- Staging `sdcard/cubegm` requiere drivers `driver_r36sx*.so` (gitignored, de Stock dump — ver `docs/PROJECT_STATE.md`).

## 8. Limpio

```sh
rm -rf build/ .toolchain/          # gitignored, no commit
git clean -fd  # PROHIBIDO sin autorización — usar rm explícito
```

Ver `docs/DEVELOPMENT.md` flujo build→host test→physical, `docs/TESTING.md` gates, `docs/dev/BUILD_ARCHITECTURE.md` grafo completo.
