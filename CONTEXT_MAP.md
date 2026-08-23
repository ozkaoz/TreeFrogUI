# CONTEXT_MAP.md — Router de Contexto — TreeFrogUI R36SX V2.6 Fork

> Router estable. Indica **qué leer / dónde mirar** para cada subsistema. No es snapshot ni log. No almacenar HEAD, SHA o branch mutable aquí — eso vive en `CURRENT.md` y en `git`.

> Para resolver estado mutable: `git rev-parse HEAD`, `git status --short --branch`, `git submodule status`, `git remote -v`, `git tag --list`.

## Cómo usar este mapa

1. Identifica tu tarea (columna izquierda).
2. Lee los ficheros listados (orden recomendado).
3. Si necesitas estado vivo, consulta Git directamente — no confíes en un SHA escrito aquí.

---

### FrogUI / UI (frontend, navegación, settings, recents, theme)

- `frogui/` — submodule `tzubertowski/FrogUI` (branch `sf3000`) — fuente del frontend (`frogui_libretro.so`)
- `frogui/*.c` / `*.h` — lógica UI, rendering, settings, recents
- `frogui/Makefile.sf3000`, `frogui/CLAUDE.md`
- `theme.md`, `docs/` (theming, fonts, wallpapers)
- `sdcard/frogui/settings.txt` — configuración persistida en SD (no en Git)
- `assets/`, `assets/icon-packs`, `assets/system-icons`

### Picoarch (wrapper libretro, display, ejecución)

- `frogui/` (interfaz `frogui_libretro.so` cargada por picoarch)
- `hijack/tfhijack.c`, `hijack/libemu_tfhijack.so` (stub que lanza zhijack)
- `hijack/zhijack.tpl.sh` → genera `release/.../install_first/<dev>/cubegm/zhijack.sh`
- Picoarch binarios no versionados aquí: se espera en `~/sf3000-work/picoarch/picoarch` en build host (ver `build_release.sh` — rutas del mantenedor)

### Input

- `hijack/zhijack.tpl.sh` — pipeline `cubevol → /tmp/joy_key` (shm)
- `frogui/input.c`, `frogui/input.h`
- Stock `cubevol` daemon (no versionado, binario en Stock OS)

### Audio

- Picoarch audio (ALSA) + `hijack/zhijack.tpl.sh` (gobernador CPU, no audio específico R36SX)
- Drivers ALSA en Stock OS; `TF_DRIVER` en `/tmp/tfdevice.env` selecciona `driver_r36sx.so` / `driver_r36sx27.so`
- Sin invariantes de audio/hardware de otros proyectos aquí — ver `docs/cores/` si aplica por core

### Cores (emuladores)

- `cores/` — clonados vía `clone_cores.sh` (gitignored en builds limpios)
- `clone_cores.sh`, `build_all.sh`, `patches/*.patch`
- `cores.md`, `ARCADE_CORES.md`
- `build/` (salida `.so` — gitignored)
- `Makefile.sf3000`, `build_all.sh` wrappers `.toolchain/`

### Hijack / Boot (cadena no destructiva Stock OS)

- `hijack/tfhijack.c`, `hijack/tfexec.c`, `hijack/build_tfhijack.sh`
- `hijack/zhijack.tpl.sh` (plantilla), `hijack/tfupdate.sh` (offline updater)
- `hijack/nosleep.c`, `hijack/driver_sf3500.so` (referencia)
- `sdcard/cubegm/` (staging universal), `sdcard/frogui/`
- `install.md` — flujo `Stock backup + TreeFrogUI + install_first/<dev>`

### R36SX (device v2.6)

- `install.md#R36SX` — backup minimal v2.6, carpeta `install_first/r36sx/`
- `hijack/zhijack.tpl.sh` — bloque `TF_DEVICE=R36SX`, `640×480`, `4/3`, `fbwrite`, `driver_r36sx.so`, política `stop` (no `killall`), lógica SIGBUS→`driver_r36sx27.so`
- `build_release.sh` — associative arrays `STOCK[r36sx]`, `HJ[r36sx]`, geometría, driver, política RKGAME
- `docs/` no tiene doc R36SX dedicada — la evidencia está en `install.md` + `build_release.sh` + `hijack/zhijack.tpl.sh`

### Release (empaquetado y updates)

- `build_release.sh` — staging universal + `install_first/<dev>/` + `zhijack.sh` generado por device
- `pack_release.sh`, `select_release_base.sh`, `publish_release.sh`
- `docs/RELEASING.md`, `docs/ai/RELEASE_CONTRACT.md`, `docs/ai/VALIDATION.md`
- `update-force-include.txt`, `release-notes.md`
- `hijack/tfupdate.sh` — instalador offline `update.zip`
- `release/` — gitignored (`release/latest/`, `release/artifact/`)

### Themes / Assets / Media Apps

- `theme.md` — 30 temas, wallpapers, icon packs
- `assets/`, `frogui/fonts/`, `frogui/res/` (muPDF, video, image viewer)
- `docs/cores/ebook.md`, `docs/cores/rockbox.md`, `docs/cores/pico286.md`

### Build / Toolchain

- `build_all.sh`, `clone_cores.sh`, `Makefile.sf3000`
- `patches/` — patches aplicados en build
- Toolchain esperado: `~/sf3000-work/sf3000toolchain/mipsel-buildroot-linux-gnu_sdk-buildroot` (ver `build_all.sh` y `README.md#Building from source`)
- `build_release.sh` rutas `/home/tomaszz/sf3000-work/...` — absolutas del mantenedor; auditar antes de build reproducible

### Upstream Sync

- `git remote -v` — `origin` (fork) vs `upstream` (tzubertowski/treefrog-ui)
- `git fetch upstream --tags`, `git tag --list`, `git log upstream/main..HEAD`
- `.opencode/agents/upstream-sync.md` — agente de análisis (no integra automáticamente)

### Testing / Validation

- `tests/test_offline_update.sh`, `tests/test_release_base_selection.sh`
- `tests/test_agent_context_contract.py` (contrato IA), `scripts/agent_preflight.py` (preflight cross-platform)
- `docs/ai/VALIDATION.md` — gates `STATIC/HOST/BUILD/PACKAGING/PHYSICAL/CLEAN-INSTALL/DOWNLOAD-BACK`

### Docs / Config

- `README.md`, `install.md`, `cores.md`, `LICENSE.md`, `.gitmodules`, `.gitignore`
- `AGENTS.md` (constitución), `CURRENT.md` (cache), `DECISIONS.md` (duraderas)
- `.opencode/agents/*.md`, `opencode.json` si existe (config project-local)

---

## Reglas del router

- No duplicar invariantes — referenciar `AGENTS.md`.
- No escribir aquí SHA/Branch vigentes — consultar Git.
- Al añadir un subsistema nuevo, ampliar este mapa y registrar decisión en `DECISIONS.md` si es duradera.
