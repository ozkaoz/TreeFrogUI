# FROGUI.md — FrogUI Submodule — Parent-Owned Reference

> `frogui/` es **submodule separado** `tzubertowski/FrogUI@sf3000` — no monolito. No crear `frogui/AGENTS.md`. Este doc es parent-owned.

## Fuente

- **Upstream:** `https://github.com/tzubertowski/FrogUI.git` (branch `sf3000`)
- **Pin actual:** `15ea12bb4f6f642b1ec02aabebbad33e5e95ed2b` (`v0.1.3-123-g15ea12b`) — `git submodule status`
- **Path parent:** `frogui/` (git submodule, `.gitmodules: branch = sf3000`, URL SSH `git@github.com:` con `url.insteadOf` HTTPS en Windows)
- **Workspace hermano histórico:** `~/sf3000-work/FrogUI` (path hardcode `frogui/build_libretro.sh:6 cd /home/tomaszz/...` — deuda, ver `docs/BUILDING.md`)

Verificar: `git -C frogui rev-parse HEAD`, `git -C frogui log -1 --oneline`, `git ls-remote https://github.com/tzubertowski/FrogUI.git 15ea12b`.

## Qué es

Frontend launcher libretro (`frogui_libretro.so`) cargado por picoarch. UI: navegación, settings, recents, carousel, theme, play-time stats, ebook/video/image viewers integration.

Fuente: `frogui/*.c` / `*.h` (`input.c`, `render`, `settings`, `recents`), `frogui/Makefile.sf3000`, `frogui/CLAUDE.md` (upstream).

Persistencia: `sdcard/frogui/settings.txt` (no en Git).

## Build

```sh
# Parent repo (este fork) — FrogUI como submodule
git submodule update --init frogui
make -f frogui/Makefile.sf3000 -C frogui frogui_libretro.so  # o
bash frogui/build_libretro.sh   # requiere fix $HOME (deuda -mtune 24kc vs 74kc)
cp frogui/frogui_libretro.so cubegm/cores/  # via build_release.sh:37 FROGUI path
```

Ver `docs/BUILDING.md §1/§5`, `docs/dev/BUILD_ARCHITECTURE.md §4`.

No editar `frogui/` como si fuera monolito para fixes parent — cambios upstreamables = PR separado en `tzubertowski/FrogUI`.

## Input y hardware R36SX

- `frogui/input.c` lee `cubevol → /tmp/joy_key` shm (ver `hijack/zhijack.tpl.sh:118`, `docs/HARDWARE.md`).
- **FN/L3/R3 bits R36SX V2.6:** FN raw 16 mask `0x00010000`, L3 1, R3 2 — validados por `tests/test_frogui_fn.py` (PHYSICAL_EVIDENCE solo con hardware, ver `docs/HARDWARE.md §2`).
- Right analog espeja face buttons (hardware wiring, no analog real) — `frogui/input.c` filtra drift.

## Contribución

- **Parent PR:** `ozkaoz/treefrog-ui-r36sx` `r36sx-v2.6-dev` → `tzubertowski/treefrog-ui` (build scripts, `release`, docs).
- **FrogUI PR:** `tzubertowski/FrogUI@sf3000` branch — linkear PRs (`Related: https://github.com/tzubertowski/FrogUI/pull/...`), ver `docs/UPSTREAM.md §3`.
- No fabricar commit parent que mezcle historia FrogUI + treefrog-ui.

## Licencia

FrogUI frontend: CC BY-NC-SA 4.0 (ver `LICENSE.md`, `frogui/LICENSE`). Ver `docs/dev/DEPENDENCY_MATRIX.md` FrogUI row.

## No tocar

```
FROGUI_SUBMODULE_CHANGED=NO
```

Cambios a `frogui/` en esta fase de infra = 0. Todo cambio futuro requiere `DECISIONS.md` si rompe submodule pin.
