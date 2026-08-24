# CONTEXT_MAP.md — Router — TreeFrogUI R36SX V2.6 Fork

> Router estable. Indica qué leer por tarea. No es snapshot. Estado mutable en `docs/PROJECT_STATE.md` + Git.

> Mutable: `git rev-parse HEAD`, `git status --short --branch`, `git submodule status`, `git remote -v`, `git tag --list`

## Cómo usar

1. Identifica tarea.
2. Lee ficheros listados (orden).
3. Para SHA/branch vivo, consulta Git — no SHA hardcodeado.

---

### Current state (snapshot mutable)

- `docs/PROJECT_STATE.md` — branch/HEAD/remotes/lock/golden (verificar con Git)
- `CURRENT.md` — stub compat que redirige a `docs/PROJECT_STATE.md` (`IS A CACHE`)
- `DECISIONS.md` — decisiones duraderas (D001 baseline)

### FrogUI / UI

- `frogui/` — submodule `tzubertowski/FrogUI@sf3000 15ea12b` (`frogui_libretro.so`)
- Parent-owned ref: `docs/components/FROGUI.md` (no crear `frogui/AGENTS.md`)
- `frogui/*.c`/`*.h`, `frogui/Makefile.sf3000`, `frogui/CLAUDE.md`
- `theme.md`, `assets/icon-packs`, `assets/system-icons`, `sdcard/frogui/settings.txt` (SD, no Git)

### Picoarch (display/audio, libretro host)

- `hijack/tfhijack.c` → `libemu_tfhijack.so` → `hijack/zhijack.tpl.sh` → `install_first/<dev>/cubegm/zhijack.sh`
- `~/sf3000-work/TreeFrogUI_picoarch@r36sx` (hermano, f8ff5ba local) — ver `docs/BUILDING.md`, `docs/dev/UPSTREAM_REPOSITORY_MAP.md`
- `docs/HARDWARE.md` — panel/driver por device

### Input

- `hijack/zhijack.tpl.sh` `cubevol → /tmp/joy_key` shm
- `frogui/input.c`, `frogui/input.h`
- `docs/HARDWARE.md` (FN 16/mask 0x10000, L3 1 R3 2) + `tests/test_frogui_fn.py`

### Audio

- Picoarch ALSA + `hijack/zhijack.tpl.sh` (governor), `TF_DRIVER` en `/tmp/tfdevice.env`
- `docs/HARDWARE.md`, `docs/cores/*` por core si aplica
- Sin invariantes de hardware externo no relacionado

### Cores

- `cores/` (78 via `clone_cores.sh`, gitignored), `clone_cores.sh`, `build_all.sh`, `patches/*.patch`, `cores.md`, `ARCADE_CORES.md`, `build/` (gitignored), `Makefile.sf3000`
- `deps/treefrog-v1.0.15.lock.json` + `docs/dev/DEPENDENCY_LOCK.md` (determinismo)
- `docs/BUILDING.md` §4-5 (`--depth=1` unpinned)

### Hijack / Boot (no destructivo Stock)

- `hijack/tfhijack.c`, `tfexec.c`, `build_tfhijack.sh`, `zhijack.tpl.sh`, `tfupdate.sh`, `nosleep.c`, `driver_sf3500.so` (ref)
- `sdcard/cubegm/` staging, `sdcard/frogui/`, `install.md` flujo `backup + TreeFrogUI + install_first/<dev>`
- `docs/HARDWARE.md` boot hijack, `docs/SD_SAFETY.md`, `docs/ai/RELEASE_CONTRACT.md`

### R36SX v2.6 (primary)

- `docs/HARDWARE.md` — tabla facts (640×480 4/3 fbwrite, driver_r36sx.so, stop, SIGBUS fallback, NOSLEEP)
- `install.md#R36SX`, `build_release.sh:HJ[r36sx]`, `hijack/zhijack.tpl.sh @R36@`
- `docs/components/FROGUI.md` para FroGUI R36SX input

### Familias soportadas (upstream)

- `install.md` 7 devices, `build_release.sh:STOCK[]`/`HJ[]` 640×480 fbwrite vs 854×480 dispframe
- `docs/HARDWARE.md §3` tabla HJ completa

### Release / Packaging

- `build_release.sh` (staging `release/latest/release` + `install_first/<dev>` + zhijack generado), `pack_release.sh`, `select_release_base.sh`, `publish_release.sh`
- `docs/RELEASING.md`, `docs/ai/RELEASE_CONTRACT.md` (single-ZIP R36SX objetivo), `docs/ai/VALIDATION.md` gates, `update-force-include.txt`, `release-notes.md`, `hijack/tfupdate.sh`, `release/` gitignored

### Themes / Assets / Media Apps

- `theme.md` 30 temas, `assets/`, `frogui/fonts/`, `frogui/res/`, `docs/cores/ebook.md|rockbox.md|pico286.md`

### Build / Toolchain

- `docs/BUILDING.md` canónico (WSL Ubuntu, `~/sf3000-work`, `mips-mti-linux-gnu-gcc 6.3.0`, `cmake` 3.28.3, wrappers `.toolchain/`)
- `build_all.sh`, `clone_cores.sh`, `Makefile.sf3000`, `patches/`, `deps/` lock
- `build_release.sh` debt `/home/tomaszz` 11× (documentado, no fijado esta fase), `docs/dev/WSL_ENVIRONMENT.md`, `docs/dev/BUILD_ARCHITECTURE.md`

### Upstream

- `docs/UPSTREAM.md` — `upstream→fork→branch→validation→commit→push→PR`, multi-repo link, confianza HIGH/MEDIUM/LOW
- `git fetch upstream --tags`, `git log upstream/main..HEAD`, `.opencode/agents/upstream-sync.md`

### Testing / Validation

- `docs/TESTING.md` — taxonomía STATIC/HOST/BUILD/PACKAGING/PHYSICAL, `tools/dev-doctor.sh`
- `tests/test_agent_context_contract.py`, `tests/test_dependency_lock.py`, `tests/test_offline_update.sh`, `tests/test_release_base_selection.sh`, `scripts/agent_preflight.py`, `scripts/dev/validate_dependency_lock.py`, `docs/ai/VALIDATION.md`

### Docs / Índice

- `docs/README.md` — hub, `docs/DEVELOPMENT.md` flujo, `AGENTS.md` constitución, `DECISIONS.md` duraderas, `docs/SD_SAFETY.md`, `CONTRIBUTING.md`, `opencode.json` (`AGENTS.md`, `docs/PROJECT_STATE.md`, `CONTEXT_MAP.md`)

---

## Reglas

- No duplicar invariantes — referenciar `AGENTS.md`.
- No hardcodear SHA/branch — consultar Git / `docs/PROJECT_STATE.md`.
- Nuevo subsistema → ampliar aquí + `DECISIONS.md` si duradero.
