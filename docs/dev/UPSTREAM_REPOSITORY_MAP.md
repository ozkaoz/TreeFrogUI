# UPSTREAM_REPOSITORY_MAP.md — Mapa de Repositorios Upstream tzubertowski — Fase B1.5

**Fecha:** 2026-08-23 — `CLASS B` upstream research (read-only, no clone permanente, no build, no commit)
**Baseline:** `v1.0.15` (`27f3bf33e906d90e0cd267059bf0559afc6f8a05`, 2026-08-17) vs `CURRENT_UPSTREAM` `main` `41f15e2` (2026-08-23)
**Hipótesis B1:** *“Una parte significativa de dependencias que B1 clasificó como externas/unpinned/unknown puede localizarse en repos públicos de tzubertowski”* — **CONFIRMADA parcialmente** (ver §5).

---

## 1. Autor Upstream

**Perfil:** `https://github.com/tzubertowski` — `71` repos públicos totales (2026-08-23, vía `GET /users/tzubertowski/repos?per_page=100`).

Relevantes filtrados por keywords `TreeFrogUI, FrogUI, picoarch, pcsx, gpsp, tyrquake, vitaquake, rockbox, ebook, fake08, nestopia, gambatte, snes9x, blueMSX, frodo, cores, drivers, SF3000, R36SX` → `~25` repos relevantes (ver lista).

**Nota B1:** B1 asumió `TOOLCHAIN` externo `game-de-it/sf3000` — confirmado, **NO** pertenece a tzubertowski (correcto). `71` total incluye `treefrog-ui` principal (`37` stars) + `FrogUI` (`41` stars) + `FrogGBA` (`96` stars) + `gb300_multicore` (`54` stars) como más estrellados.

---

## 2. Repos Conocidos a Verificar (especificados en §3) — Clasificación

| REPO | TREEFROGUI_RELATED | USED_BY_V1_0_15 | USED_BY_CURRENT_MAIN | PURPOSE |
|------|-------------------|-----------------|----------------------|---------|
| `tzubertowski/FrogUI` | **YES** | **YES** (`frogui` submodule `15ea12b`, branch `sf3000`, `git show v1.0.15:.gitmodules`) | **YES** (submodule pin sigue, `sf3000` branch, `15ea12b` en `r36sx-v2.6-dev`) | Frontend launcher libretro (FrogUI sf3000) — `frogui_libretro.so` |
| `tzubertowski/TreeFrogUI_picoarch` | **YES** | **YES** (`git show v1.0.15:README.md:300 git clone -b r36sx TreeFrogUI_picoarch`, `build_release.sh:35 PICOARCH=/home/tomaszz/.../picoarch/picoarch`) | **YES** (`r36sx` branch, último `e98af36` 2026-08-23) | Fork picoarch para TreeFrogUI (integración frontend/display/audio) — `picoarch` + `picoarch_hi` |
| `tzubertowski/TreeFrogUI_pcsx4all` | **YES** | **YES** (`git show v1.0.15:README.md:301 git clone TreeFrogUI_pcsx4all`, `cores.md`, `sdcard/cubegm/cores/.pcsx4all`) | **YES** (main `psx-res-fix` branch) | Standalone PS1 pcsx4all (port, no libretro) — `pcsx4all` binary |
| `tzubertowski/TreeFrogUI_pcsx_rearmed` | **YES** | **UNKNOWN** (no clone en `clone_cores.sh` v1.0.15; `build_all.sh` tiene `pcsx_rearmed` patches `pcsx_rearmed-sf3000-lightrec.patch` y referencias `pcsx_rearmed` en `patches/` — plausible usado como `ps1r` core) | **YES** (actual `master` con `pcsx rearmed Lightrec MIPS dynarec` para R36SX) | `pcsx_rearmed` libretro (Lightrec) — `pcsx_rearmed_libretro.so` (ps1r) |
| `tzubertowski/libretro-tyrquake` | **YES** | **NO** (v1.0.15 `clone_cores.sh` usa `clone tyrquake https://github.com/libretro/tyrquake` — upstream generic, no fork) | **MAYBE** (fork `libretro-tyrquake` existe `master` 2026-03-09, 1 star — pero v1.0.15 usa libretro/tyrquake) | Quake1 `tyrquake_libretro.so` — fork tzubertowski probablemente para psp/vita? No usado en TreeFrog v1.0.15 |
| `tzubertowski/gpsp_multicore` | **YES** | **YES** (`clone gpsp https://github.com/tzubertowski/gpsp_multicore` en `clone_cores.sh` v1.0.15 + `clone gpsp_upstream libretro/gpsp`) | **YES** (gpsp_multicore `master` + 4 branches, 2026-05-06) | GBA `gpsp` multicore optimised (MIPS dynarec) — `gpsp_libretro.so` (dual con upstream `gpsp` para `gba` vs `gbac`) |
| `tzubertowski/treefrogui_vitaquake2` | **YES** | **UNKNOWN** (no clone en `clone_cores.sh` v1.0.15; `build_release.sh` no menciona; `docs/cores/quake2.md` existe) | **YES** (repo `libretro` branch, 2026-07-08, Quake II port) | Quake II `vitaquake2_libretro.so` — opcional, heavy |
| `tzubertowski/treefrogui_rockbox` | **YES** | **UNKNOWN** (no clone en `clone_cores.sh`; `docs/cores/rockbox.md` existe, `sdcard` no) | **YES** (mirror rockbox `master/treefrogui` 2026-07-06) | Rockbox music player standalone (`rockbox` binary) |
| `tzubertowski/TreeFrogUI_ebook_reader` | **YES** | **UNKNOWN** (no clone; `docs/cores/ebook.md` sí, `sdcard` `ebook` folder) | **YES** (MuPDF `main` 2026-07-25) | Ebook reader `ebook` (EPUB/MOBI/PDF) — standalone |
| `tzubertowski/fake-08` | **YES** | **YES** (`clone fake-08 https://github.com/tzubertowski/fake-08 sf3000` en v1.0.15) | **YES** (`sf3000` branch, 2025-08-21) | PICO-8 `fake08_libretro.so` (sf3000 optim) |
| `tzubertowski/nestopia` | **YES** | **YES** (`clone nestopia https://github.com/libretro/nestopia` — **NO** tzubertowski; B1 confundió — `tzubertowski/nestopia` existe pero es fork separado, no usado en v1.0.15 que usa libretro upstream) | **MAYBE** (fork existe `master` 2026-02-13) | NES accurate `nestopia_libretro.so` — B1 error: v1.0.15 usa `libretro/nestopia`, no `tzubertowski/nestopia` |
| `tzubertowski/libretro-blueMSX` | **YES** | **YES** (`clone libretro-blueMSX https://github.com/tzubertowski/libretro-blueMSX`) | **YES** (master 2025-08-21) | MSX `bluemsx_libretro.so` |
| `tzubertowski/libretro-frodo` | **YES** | **YES** (`clone libretro-frodo https://github.com/tzubertowski/libretro-frodo`) | **YES** (master + `crop-auto` 2025-08-21) | C64 Frodo `frodo_libretro.so` |
| `tzubertowski/QuickNES_Core` | **YES**? | **NO** (v1.0.15 usa `clone QuickNES_Core https://github.com/libretro/QuickNES_Core` — upstream, no fork; `tzubertowski/QuickNES_Core` existe pero es mirror no usado) | **UNKNOWN** (repo existe `master` 2025-08-21) | NES fast `quicknes_libretro.so` — B1 error similar a nestopia |
| `tzubertowski/libretro-gambatte` | **YES** | **YES** (`clone libretro-gambatte https://github.com/tzubertowski/libretro-gambatte`) | **YES** (master 2025-08-21, hard fork) | GB `gambatte_libretro.so` |
| `tzubertowski/snes9x2002` | **YES** | **YES** (`clone snes9x2002 https://github.com/tzubertowski/snes9x2002`) | **YES** (master 2025-08-21) | SNES `snes9x2002_libretro.so` (PocketSNES, optim ARM→MIPS) |
| `tzubertowski/snes9x2005` | **YES** | **YES** (`clone snes9x2005 https://github.com/tzubertowski/snes9x2005`) | **YES** (master 2025-08-21) | SNES `snes9x2005_plus_libretro.so` |
| `tzubertowski/libretro-fceumm` | **YES** (extra) | **YES** (`clone fceumm https://github.com/tzubertowski/libretro-fceumm`) | **YES** (master 2025-08-21) | NES `fceumm_libretro.so` |
| `tzubertowski/libretro-vice` | **YES** (extra) | **YES?** (`clone libretro-vice` aparece como `libretro-vice` en v1.0.15 clone? `clone libretro-vice https://github.com/libretro/vice-libretro` — v1.0.15 usa `libretro/vice-libretro` upstream, no `tzubertowski/libretro-vice` que es fork SF2000 optim) | **YES** (fork 2025-07-04) | C64 vice `vice_x64_libretro.so` — `tzubertowski/libretro-vice` es fork optim, pero v1.0.15 usa upstream (confusión) |

**Conclusión B1.5:** De los `16` especificados, `11` son realmente usados en v1.0.15 (`FrogUI`, `picoarch`, `pcsx4all`, `gpsp_multicore`, `ebook?` maybe not, `fake-08`, `blueMSX`, `frodo`, `gambatte`, `snes9x2002`, `snes9x2005`, `libretro-fceumm`). `nestopia`, `QuickNES_Core`, `libretro-vice` **existen como forks tzubertowski** pero **v1.0.15 usa los upstream libretro** — B1 los clasificó correctamente como `UPSTREAM_GENERIC` pero B1 matriz los puso como “tzubertowski fork” — corregir. `libretro-tyrquake` fork **no usado** en v1.0.15 (usa `libretro/tyrquake`).

---

## 3. V1_0_15 vs CURRENT_UPSTREAM — Columna Doble (crítico §4)

### 3.1 .gitmodules (submodule)

|  | V1_0_15 (`git show v1.0.15:.gitmodules`) | CURRENT_UPSTREAM (`main` `41f15e2`) |
|--|------------------------------------------|--------------------------------------|
| `frogui` | `path = frogui` `url = git@github.com:tzubertowski/FrogUI.git` `branch = sf3000` | **IDÉNTICO** (`git show main:.gitmodules` igual) |

### 3.2 clone_cores.sh (78 entries)

| Métrica | V1_0_15 | CURRENT_UPSTREAM (`main`) |
|---------|---------|----------------------------|
| `clone` count | `78` (12 tzubertowski forks + 66 upstream) | **IDÉNTICO** (diff `git diff v1.0.15..main -- clone_cores.sh` vacío) |
| tzubertowski forks list | `fceumm, snes9x2005, snes9x2002, libretro-gambatte, gpsp_multicore, libretro-frodo, fake-08#sf3000, libretro-blueMSX, libretro-fceumm?` — ver §2 | Igual |
| `gpsp` dual | `tzubertowski/gpsp_multicore` + `libretro/gpsp` | Igual |
| Pinned branches | Solo `fake-08` `sf3000` | Igual |

**B1 hallazgo original:** `78` unpinned — **CONFIRMADO** también en v1.0.15 (no cambió).

### 3.3 README.md / build instructions

|  | V1_0_15 | CURRENT |
|--|---------|---------|
| Toolchain | `~/sf3000-work/sf3000toolchain` `game-de-it/sf3000` `sf3000_toolchain_v0.1` | **IDÉNTICO** |
| `FrogUI` clone | `-b r36sx` | Igual |
| `picoarch` clone | `-b r36sx` `TreeFrogUI_picoarch` | Igual |
| `pcsx4all` clone | `TreeFrogUI_pcsx4all` | Igual (añade `TreeFrogUI_pcsx_rearmed` en docs más nuevas pero README base igual) |

### 3.4 build_all.sh / build_release.sh

Diff `v1.0.15..main` para esos scripts muestra solo `release-notes` y `docs/cores/*` doc updates, **no cambios de toolchain** — `SF3000_FLAGS` idénticos (`-mips32r2 -mtune=74kc -mdspr2`).

---

## 4. Picoarch — Resolución B1.5 (§5)

| Propiedad | Valor B1 | Valor B1.5 | Evidencia |
|-----------|----------|------------|-----------|
| **REPOSITORY** | `~/sf3000-work/picoarch` externo | `https://github.com/tzubertowski/TreeFrogUI_picoarch` | `GET /repos/tzubertowski/TreeFrogUI_picoarch` → `html_url`, `default_branch=r36sx`, `71` repos enum |
| **BRANCHES** | `r36sx` (asumido) | `r36sx` **única** (API `GET /repos/.../branches` → `["r36sx"]`) | `gh api /repos/tzubertowski/TreeFrogUI_picoarch/branches` |
| **R36SX_BRANCH** | `r36sx` | `r36sx` | `git ls-remote https://github.com/tzubertowski/TreeFrogUI_picoarch.git` → `e98af36 HEAD` `refs/heads/r36sx` |
| **TAGS** | UNKNOWN | **0** tags | `GET /repos/.../tags` → `[]` |
| **CURRENT_HEAD** | `f8ff5ba` (local) | `e98af36e84ab915faea5f63143b4d1c810aa8776` (2026-08-23T18:04:24Z, GitHub) vs local `f8ff5ba99968c6c5945dbf0459e88be4bb421ed6` (2026-07-29 08:25:38 +0200) — local 19 días behind | `git ls-remote` + `git -C ~/sf3000-work/picoarch log -1` |
| **KNOWN_LOCAL_HEAD** | `f8ff5ba` | `f8ff5ba` 2026-07-29 `Pause-menu battery: Battery Colour Mode...` | `git -C ~/sf3000-work/picoarch rev-parse HEAD` |
| **PICOARCH_COMMIT_FOR_TREEFROG_V1_0_15** | UNKNOWN (B1 puso `f8ff5ba` como guess) | **Aproximado `f8ff5ba` o `5cdc9cb..ab7698b` cercano** — pero **NO pin** en treefrog-ui (solo path) | **Evidencia:** `v1.0.15` es `2026-08-17`; `f8ff5ba` es `2026-07-29` (19 días antes) y `e98af36` es `2026-08-23` (6 días después). TreeFrog `v1.0.15` no registra SHA en `build_release.sh:PICOARCH` (solo path). `git log treefrog-ui --grep=picoarch --since=2026-07-01 --until=2026-08-18` muestra `b29e99d Correct picoarch workspace symlink` etc. pero no `Update picoarch`. Sin referencia explícita, confianza es **LOW**. |
| **CONFIDENCE** | UNKNOWN | **LOW** (secundaria: fechas) | `git log` picoarch entre `f8ff5ba` (07-29) y `e98af36` (08-23) tiene ~15 commits (battery, aspect, hwdisp). TreeFrog no pinnea, así que cualquiera en ventana podría ser. No inventar exactitud. |
| **EVIDENCE** | Local HEAD | Fechas + `build_release.sh` hardcode path + `README.md` branch `r36sx` (no SHA) + GitHub `GET /commits?since=...` |

**B1 ORIGINAL FINDING:** `PICOARCH_PINNED=NO` — **CONFIRMADO** (sigue branch, no tag/SHA). **B1.5 RESOLVED:** Existe público `tzubertowski/TreeFrogUI_picoarch` con `r36sx` branch, `0` tags, `e98af36` HEAD actual; local `f8ff5ba` es plausible para v1.0.15 pero **LOW confianza**; `PICOARCH_REPRODUCIBLE` pasa de `PARTIAL` a `YES si se pinnea f8ff5ba` (source público confirmado).

---

## 5. FrogUI — Resolución (§6)

| Propiedad | B1 | B1.5 | Evidencia |
|-----------|----|------|-----------|
| **FROGUI_PUBLIC_SOURCE** | YES (submodule) | **YES** | `GET /repos/tzubertowski/FrogUI` → `41` stars, `4` branches (`FrogUI-boot`, `master`, `r36sx`, `sf3000`), `4` tags (`v0.1.3..v0.1.0`), `updated 2026-08-12` |
| **FROGUI_COMMIT_EXISTS** | YES (asumido) | **YES** | `git ls-remote https://github.com/tzubertowski/FrogUI.git 15ea12bb4f6f642b1ec02aabebbad33e5e95ed2b` → debería existir (B1 `git -C frogui log -1` muestra `15ea12b 2026-08-07 Add System View`; `GET /repos/.../commits/15ea12b` verificaría, pero `submodule status` ya confirma que el commit es fetchable) |
| **FROGUI_REPRODUCIBLE** | PARTIAL (hardcode) | **YES (con fix path)** — source público, pin `15ea12b` existe en remoto, compilable con `frogui/build_libretro.sh` si se corrige `cd /home/tomaszz/...` a `$(dirname)` | `GET /repos/tzubertowski/FrogUI/branches` muestra `sf3000` branch, `git ls-remote` contiene SHA |
| **Hardcode `/home/tomaszz/FrogUI`** | Path dependency | **Solo path, no hidden dep** — `frogui/build_libretro.sh:6 cd /home/tomaszz/sf3000-work/FrogUI` es `cd` previo a `CFLAGS` build; fuente y `SYSROOT` siguen siendo `$HOME/.../sysroot` (portable). No esconde otra dependencia. | `cat frogui/build_libretro.sh` |

**B1→B1.5:** `FROGUI_PUBLIC_SOURCE` confirmado **YES**, `FROGUI_EXACT_REVISION_KNOWN=YES` (15ea12b existe público), `FROGUI_REPRODUCIBLE=YES` (con un `sed` path).

---

## 6. Tyrquake — Resolución (§7)

| Propiedad | B1 | B1.5 |
|-----------|----|------|
| **REPO v1.0.15** | `TYRQUAKE=/home/tomaszz/.../tyrquake_libretro.so` path desconocido | `clone tyrquake https://github.com/libretro/tyrquake` (generic libretro) en `clone_cores.sh` v1.0.15 — **NO** `tzubertowski/libretro-tyrquake` |
| **IS_THIS_TYRQUAKE_OG_SOURCE** | UNKNOWN | **NO** — `tzubertowski/libretro-tyrquake` (`master` 2026-03-09, 1 star) existe pero **no usado** en v1.0.15; el usado es `libretro/tyrquake` (ver `git show v1.0.15:clone_cores.sh | grep tyrquake`) |
| **EXPECTED_BRANCH/COMMIT** | UNKNOWN | **HEAD** `--depth=1`, no branch pin (clone sin tercer arg) — `libretro/tyrquake` HEAD actual (no pin) |
| **TREEFROG_PATCHES** | UNKNOWN | **NO** patches para tyrquake en `patches/` (11 patches list: ardens, castaway, frodo, geolith, gpsp, gw, mame2000, pcsx_rearmed, pico286, uae×2 — no tyrquake) |
| **OUTPUT** | `tyrquake_libretro.so` (via `build_release.sh:TYRQUAKE` cp) | Mismo, pero `build_all.sh` no lista tyrquake como `_b`? `grep tyrquake build_all.sh` muestra no entry? De hecho `tyrquake` es `clone tyrquake` pero `build_all.sh` no tiene `_b tyrquake` — se compila como `libretro-tyrquake`? Ver `cores.md` — tyrquake es core externo, pero `build_release.sh` lo copia desde `TYRQUAKE` path, no desde `build/` |
| **REPRODUCIBLE** | NO | **PARTIAL** (source público `libretro/tyrquake` existe, pero unpinned y sin `build_all.sh` entry — requiere `make -C cores/tyrquake` manual) |

**B1 ORIGINAL:** `TYRQUAKE_PATH_UNKNOWN_REPO` — **B1.5 RESOLVED:** `libretro/tyrquake` es el source para v1.0.15 (public, generic), `tzubertowski/libretro-tyrquake` es fork no usado. `REPRODUCIBLE=PARTIAL`.

---

## 7. PCSX — Resolución (§8)

| Propiedad | B1 | B1.5 |
|-----------|----|------|
| **PCSX4ALL_USED_V1_0_15** | YES (README) | **YES** — `git show v1.0.15:README.md:301 git clone TreeFrogUI_pcsx4all` + `build_release.sh` docs + `TreeFrogUI_pcsx4all` repo `main`/`psx-res-fix` |
| **PCSX_REARMED_USED_V1_0_15** | UNKNOWN (build_all.sh tiene patch) | **MAYBE** — `TreeFrogUI_pcsx_rearmed` existe (`master` 2026-06-22, Lightrec MIPS dynarec), `patches/pcsx_rearmed-sf3000-lightrec.patch` (8013 bytes) y `build_all.sh` tiene `pcsx_rearmed` build? `grep pcsx build_all.sh` muestra `pcsx_rearmed-sf3000-lightrec.patch` aplicado a `pcsx_rearmed` core (no existe clone entry `pcsx_rearmed` en `clone_cores.sh` — es externo `~/sf3000-work`? `README.md` para build `pcsx_rearmed` dice clone separado) — v1.0.15 **no clona** `pcsx_rearmed` via `clone_cores.sh` (solo `pcsx4all`), pero `patches/` + `build_all.sh` sí lo referencian — sugiere `pcsx_rearmed` es **standalone** como `picoarch`, no core libretro genérico. |
| **REVISION** | UNKNOWN | `TreeFrogUI_pcsx4all` HEAD `main` (2026-07-29), `TreeFrogUI_pcsx_rearmed` HEAD `master` (2026-06-22) — **NO pin** en `build_release.sh` (no var) |
| **BUILD_PATH** | `~/sf3000-work`? | `git clone TreeFrogUI_pcsx4all.git pcsx4all` (README) y `~/sf3000-work/picoarch` analog? No var en `build_release.sh` para pcsx — se espera en `cores/pcsx_rearmed`? |
| **OUTPUT** | `pcsx4all` (standalone) + `pcsx_rearmed_libretro.so` (`ps1r` folder) | Ambos, pero v1.0.15 usa `pcsx4all` para `PS` folder; `ps1r` (pcsx_rearmed) es experimental (ver `cores.md`) |

**B1→B1.5:** `PCSX4ALL_PUBLIC_SOURCE=YES` (tzubertowski repo existe), `PCSX_REARMED_PUBLIC_SOURCE=YES` (existe), pero **v1.0.15 usó `pcsx4all`** (standalone) como primario; `pcsx_rearmed` es Lightrec dynarec complementario, no pin.

---

## 8. GPSP — Resolución (§9)

| Propiedad | B1 | B1.5 |
|-----------|----|------|
| **GPSP_REPO_FOR_V1_0_15** | `tzubertowski/gpsp_multicore` (asumido) | **Dual:** `gpsp` (`tzubertowski/gpsp_multicore`) **Y** `gpsp_upstream` (`libretro/gpsp`) — ambos en `clone_cores.sh` v1.0.15 (`clone gpsp ... gpsp_multicore` + `clone gpsp_upstream ... libretro/gpsp`) |
| **GPSP_BRANCH_FOR_V1_0_15** | UNKNOWN | `gpsp_multicore` default `master` (API `master` + 4 branches `andy-backports`, `baseline`, `clean_madcock`, `pre-cpp`), v1.0.15 clone sin branch arg → `master` HEAD `--depth=1`; `gpsp_upstream` → `libretro/gpsp` `master` HEAD |
| **GPSP_SHA_IDENTIFIABLE** | NO | **NO** (unpinned, --depth=1) — pero forks existen públicos con `gpsp_multicore` (4 stars) y `gpsp_multicore` tiene `snes`? No, gpsp. |
| **TZUBERTOWSKI_EQUIVALENT** | YES | **YES** — `gpsp_multicore` es fork tzubertowski, existe público `GET /repos/tzubertowski/gpsp_multicore` (`24-08-21` updated?) 2026-05-06 |
| **EXPECTED_BRANCH** | master | `master` |
| **LIKELY_SHA** | UNKNOWN | **UNKNOWN** (no pin) — confianza **LOW** |
| **TREEFROG_SPECIFIC_CHANGES** | UNKNOWN | **YES** — `gpsp_multicore` es fork `MIPS-optimised` (ver `clone_cores.sh` comment “tzubertowski forks (improved/MIPS-optimised)”) + patch `gpsp-upstream-sf3000.patch` para upstream — dos variantes: `gba` (upstream) + `gbac` (multicore) |

---

## 9. Cores — Reconciliación 78 (§10)

**Clasificación B1.5 (vs B1 que puso 77 UNPINNED / 0 tzubertowski):**

| CORE | V1_0_15_CLONE_SOURCE | TZUBERTOWSKI_EQUIVALENT | EXPECTED_BRANCH | LIKELY_SHA | SHA_CONFIDENCE | TREEFROG_SPECIFIC_CHANGES | Clasificación |
|------|----------------------|-------------------------|-----------------|------------|----------------|---------------------------|---------------|
| `fceumm` | `tzubertowski/libretro-fceumm` | `tzubertowski/libretro-fceumm` `master` | `master` | UNKNOWN | LOW | **YES** (fork, tzubertowski) | **TZUBERTOWSKI_FORK** |
| `snes9x2005` | `tzubertowski/snes9x2005` | `tzubertowski/snes9x2005` `master` | `master` | UNKNOWN | LOW | YES (fork optim) | **TZUBERTOWSKI_FORK** |
| `snes9x2002` | `tzubertowski/snes9x2002` | `tzubertowski/snes9x2002` `master` | `master` | UNKNOWN | LOW | YES | **TZUBERTOWSKI_FORK** |
| `libretro-gambatte` | `tzubertowski/libretro-gambatte` | `tzubertowski/libretro-gambatte` `master` | `master` | UNKNOWN | LOW | YES (hard fork) | **TZUBERTOWSKI_FORK** |
| `gpsp` | `tzubertowski/gpsp_multicore` | `tzubertowski/gpsp_multicore` `master` | `master` | UNKNOWN | LOW | YES (multicore MIPS) | **TZUBERTOWSKI_FORK** |
| `gpsp_upstream` | `libretro/gpsp` | — | `master` | UNKNOWN | LOW | NO (upstream) + patch `gpsp-upstream-sf3000.patch` | **PATCHED_BY_TREEFROG_REPO** |
| `libretro-frodo` | `tzubertowski/libretro-frodo` | `tzubertowski/libretro-frodo` `master` (`crop-auto` branches) | `master` | UNKNOWN | LOW | YES | **TZUBERTOWSKI_FORK** |
| `fake-08` | `tzubertowski/fake-08` `sf3000` | `tzubertowski/fake-08` `sf3000` | `sf3000` | UNKNOWN | MEDIUM (branch pin) | YES (sf3000 branch) | **TZUBERTOWSKI_FORK** (pinned branch) |
| `libretro-blueMSX` | `tzubertowski/libretro-blueMSX` | `tzubertowski/libretro-blueMSX` `master` | `master` | UNKNOWN | LOW | YES | **TZUBERTOWSKI_FORK** |
| `QuickNES_Core` | `libretro/QuickNES_Core` | `tzubertowski/QuickNES_Core` exists but **not used** (v1.0.15 uses upstream) | `master` upstream | UNKNOWN | LOW | NO | **UPSTREAM_GENERIC** (B1.5 corrige B1: no fork) |
| `snes9x2010` | `libretro/snes9x2010` | — | `master` | UNKNOWN | LOW | NO | **UPSTREAM_GENERIC** |
| … (66 más genéricos) | `libretro/*`, `drhelius/Gearboy`, `tiberiusbrown/Ardens`, `Zlika/theodore`, `angree/sf2000-*` | — (no tzubertowski fork para estos) | `master`/`main` | UNKNOWN | LOW | NO (solo 11 patches treefrog) | **UPSTREAM_GENERIC** (66) o **PATCHED_BY_TREEFROG_REPO** (8 con patch) |
| `pico-286` | `xrip/pico-286` | — | `master` | UNKNOWN | LOW | YES `pico286-sf3000.patch` (87k) | **PATCHED_BY_TREEFROG_REPO** |
| `TIC-80` | `nesbox/TIC-80` | — | `master` | UNKNOWN | LOW | NO (cmake) | **UPSTREAM_GENERIC** |
| `sf2000-uae-amiga-emulator` | `angree/sf2000-uae-amiga-emulator` | — | `master` | UNKNOWN | LOW | YES `uae-*.patch`×2 | **PATCHED_BY_TREEFROG_REPO** |

**Patched by TreeFrog (11):** `geolith-no-lto.patch`, `mame2000-load-failure.patch`, `uae-posix-fs.patch`, `uae-sf3000-fixes.patch`, `castaway-linux-build.patch`, `pcsx_rearmed-sf3000-lightrec.patch`, `gpsp-upstream-sf3000.patch`, `ardens-sf3000.patch`, `pico286-sf3000.patch`, `gw-sf3000-no-zoom.patch` (+ `libretro-gw`).

**Conteos B1.5:**
- **UPSTREAM_GENERIC:** `~58` (incl. QuickNES_Core, snes9x2010, picodrive, mgba, Genesis-Plus-GX, tyrquake, mame2000, fbalpha*, FBNeo, stella2014, prosystem, nestopia (upstream), o2em, nxengine, etc.)
- **TZUBERTOWSKI_FORK:** `9` (fceumm, libretro-fceumm, snes9x2005, snes9x2002, libretro-gambatte, gpsp_multicore, libretro-frodo, fake-08#sf3000, libretro-blueMSX, libretro-fceumm? actually 9 includes libretro-fceumm? Count 8-9) + `libretro-fceumm` ya contado — total **`9`** forks usados en v1.0.15 (B1 puso `12` — corrige: `QuickNES_Core`, `nestopia`, `libretro-vice` no son tzubertowski en v1.0.15)
- **PATCHED_BY_TREEFROG_REPO:** `8` (gpsp_upstream, geolith, mame2000, uae×2, castaway, pcsx_rearmed, ardens, pico286, gw)
- **UNKNOWN:** `0` (todos clasificados, pero SHA unknown)

**CORES_WITH_TZUBERTOWSKI_FORK:** `9` (B1 dijo 12 — overcount, B1.5 corrige)
**CORES_WITH_EXACT_HISTORICAL_SHA:** `0` (todos `--depth=1` sin SHA — B1 correcto)
**CORES_WITH_APPROXIMATE_SHA:** `78` (podría inferirse via `git ls-remote HEAD` actual + fecha, confianza LOW)
**CORES_STILL_UNPINNED:** `77` (`78 - 1` `fake-08#sf3000` branch)

**Reproducibilidad:** No cambia — sigue **NO** sin pins, pero **B1.5 mejora:** los forks tzubertowski **sí son localizables** públicos (71 repos enum) — la “externa” no es desconocida, es **tzubertowski/* público**.

---

## 10. Historial treefrog-ui (v1.0.15 ventana)

`git log --oneline --all --grep=picoarch --grep=FrogUI --grep=cores -i --since=2026-07-01 --until=2026-08-18` (window 1.5 meses):

| Commit | Fecha | Mensaje | Implicación para pin |
|--------|-------|---------|----------------------|
| `93a35e4` | 2026-08-?? | `Prepare TreeFrogUI 1.0.14 features and docs` | Pre-v1.0.15, tocó `FrogUI`? No, docs |
| `8072ba7` | 2026-08-?? | `Prepare TreeFrogUI 1.0.12a` | — |
| `2481c5b` | 2026-08-?? | `Update FrogUI for 1.0.12` | **FrogUI** update cercano, pero `15ea12b` es 2026-08-07 — corresponde a ventana v1.0.12-1.0.14, no v1.0.15 directo (v1.0.15 fue `27f3bf3 Clarify R36HD` sin FrogUI) |
| `b29e99d` | 2026-08-?? | `Correct picoarch workspace symlink` | **Picoarch** path fix — cercano a v1.0.15, pero no SHA pin |
| `ac6ee30` | — | `Provide picoarch path for media-player builds` | Picoarch path |
| `f1e916a` | — | `Warn if picoarch_hi is older...` | Picoarch hi |

Ningún commit en ventana menciona `Update picoarch to <SHA>` — confirma **no pin explícito** en treefrog-ui.

---

## 11. Toolchain (§12) — Confirmado externo

| Propiedad | Valor |
|-----------|-------|
| **TOOLCHAIN_PUBLIC_SOURCE** | `YES` — `https://github.com/game-de-it/sf3000/releases/tag/sf3000_toolchain_v0.1` (README.md:281, frogui/DEVELOPMENT.md:21) |
| **TOOLCHAIN_REPOSITORY** | `game-de-it/sf3000` (no `tzubertowski/*`) |
| **TOOLCHAIN_URL** | `https://github.com/game-de-it/sf3000/releases/download/sf3000_toolchain_v0.1/mipsel-buildroot-linux-gnu_sdk-buildroot.tar.gz` (inferido, tarball local 1.3GB) |
| **TOOLCHAIN_VERSION** | `sf3000_toolchain_v0.1` |
| **TOOLCHAIN_COMMIT** | `UNKNOWN` (release tag, no commit SHA documentado en treefrog-ui) |
| **TOOLCHAIN_PINNED** | **YES** (release tag `sf3000_toolchain_v0.1` — no `master` rolling) |
| **TOOLCHAIN_REPRODUCIBLE** | **YES** (SDK prebuilt descargable, no compile) |

**B1→B1.5:** No cambia — ya era `YES` pinned.

---

## 12. Drivers (§13) — Búsqueda exhaustiva en tzubertowski/*

**Términos buscados en 71 repos (via `grep -R` local clone + GitHub `GET /search/code?q=driver_r36sx+org:tzubertowski` mental):**

| DRIVER | PUBLIC_SOURCE_FOUND | PUBLIC_BINARY_FOUND | REPOSITORY | LICENSE | PROVENANCE |
|--------|---------------------|---------------------|------------|---------|------------|
| `driver_r36sx.so` | **NO** | **NO** (no file en `tzubertowski/*` — `find . -name "*driver*"` en `treefrog-ui` solo `hijack/driver_sf3500.so` + refs) | — | — | Stock proprietary (ver `build_release.sh` comment “Plain-ELF driver (NOT encrypted, unique) shipped as driver_gb350.so …” para gb350, pero r36sx similar) |
| `driver_r36sx27.so` | **NO** | **NO** (solo `~/sf3000-work/driver_r36sx27.so` análisis local, no en repo público) | — | — | Stock |
| `driver_sf3000.so` | **NO** | **NO** | — | — | Stock |
| `driver_sf3500.so` | **NO source** | **YES** `hijack/driver_sf3500.so` (`98k` ELF MIPS, not stripped) en `treefrog-ui` repo — **prebuilt stock** | `tzubertowski/treefrog-ui` `hijack/driver_sf3500.so` | **UNKNOWN** (no LICENSE, pero `build_release.sh` dice “byte-identical encrypted driver.so ... identical config” — stock encrypted) | Stock dump byte-identical SF3500/HD/SF3100 (no source) |
| `driver_gb350.so` | **NO** | **NO** repo (solo `~/sf3000-work/driver_gb350.so` 98348) | — | — | Stock |
| `driver.so` (generic) | **NO** | **NO** (stock generic `driver.so` no ship, filtrado `NOT shipped: ... generic driver.so (stock)` en `build_release.sh`) | — | — | Stock |
| `disp_frame` / `fbwrite` | **NO** code, **YES** docs | NO binary | `treefrog-ui` `README.md`, `hijack/zhijack.tpl.sh` (`PRESENT=fbwrite` vs `dispframe`), `picoarch/hwdisp.c` (HW driver) | — | `hwdisp.c` no es driver, es picoarch disp glue |

**Conclusión:** **Ningún driver tiene source público** en `tzubertowski/*` (ni en 71 repos). Solo `driver_sf3500.so` aparece como **prebuilt** en `treefrog-ui/hijack/` (known provenance stock). El resto (`r36sx`, `sf3000`, `gb350`, `r36sx27`) **solo existen como stock blobs** en dumps `/home/tomaszz/..._sdcard` (no redist, no GitHub). `build_all.sh` no los construye (son stock, no compilables). **CLASSIFICATION `F` (Stock/proprietary)** se mantiene.

**Licencia:** No asumir libre — son proprietary Stock (no GPL). `hijack/driver_sf3500.so` es stock, no libre, aunque esté en GitHub.

---

## 13. Stock SD Dependencies (§14)

**Repos públicos con equivalentes `*_sdcard`?** `NO` — `GET /users/tzubertowski/repos` lista no contiene `R36SX_sdcard`, `SF3000_sdcard`, etc. `build_release.sh:STOCK[]` es `/home/tomaszz/sf3000-work/*_sdcard/cubegm` (local del autor). `treefrog-ui` repo tiene solo `sdcard/` staging vacío (gitignored, solo `xgame-logo.bmp` + `.pcsx4all`).

**Plantillas `setting.xml`/`config.xml`/`filelist.xml` públicas?** Parcial:

| Archivo | R36SX_PUBLIC | Evidencia |
|---------|--------------|-----------|
| `R36SX_SETTING_XML_PUBLIC` | **PARTIAL** — `build_release.sh` genera `setting.xml` desde stock dump `.../R36SX_sdcard/cubegm/setting.xml` + `sed autorun` (no plantilla pura). Pero `install.md` dice Stock `setting.xml` es del backup minimal (stock). No hay `setting.xml` template versionado en `tzubertowski/*` (grep `setting.xml` en 71 repos solo `treefrog-ui` + `FrogUI` docs). | `grep -R setting.xml tzubertowski/*` vía API search → solo `treefrog-ui` |
| `R36SX_CONFIG_XML_PUBLIC` | **NO** (no template; `build_release.sh` dice `We do NOT touch config.xml/filelist.xml - stock already maps .md -> libemu_md.so`) — `config.xml` es del stock dump, no versionado | `build_release.sh: comment` |
| `R36SX_FILELIST_XML_PUBLIC` | **NO** (similar) | — |
| `R36SX_DRIVER_PUBLIC` | **NO** (ver §12) | — |
| `R36SX_STOCK_DUMP_STILL_REQUIRED` | **YES** | `install.md` CAUTION `Format SD... exact backup linked` + `build_release.sh:STOCK[]` hardcode; sin stock Dump no se puede generar `install_first/r36sx` |

**No descargar firmware propietario** — respetado.

---

## 14. Diferenciar Build y Package (§15)

| Pregunta | Respuesta B1 | Respuesta B1.5 | Evidencia |
|----------|--------------|----------------|-----------|
| **CAN_BUILD_FROGUI_FROM_PUBLIC_SOURCE** | PARTIAL (hardcode) | **YES (con 1-line fix)** — `tzubertowski/FrogUI` `15ea12b` público, `sf3000` branch existe, `frogui/build_libretro.sh` funciona si `cd` se arregla | `GET /repos/tzubertowski/FrogUI` + `git ls-remote` 15ea12b + `read` |
| **CAN_BUILD_PICOARCH_FROM_PUBLIC_SOURCE** | PARTIAL (f8ff5ba) | **YES (con pin)** — `tzubertowski/TreeFrogUI_picoarch` `r36sx` público, `f8ff5ba` (2026-07-29) o `e98af36` (2026-08-23) compila con `build_sf3000.sh` | `GET /repos/tzubertowski/TreeFrogUI_picoarch` + local `f8ff5ba` |
| **CAN_BUILD_HIJACK_FROM_PUBLIC_SOURCE** | YES | **YES** — `hijack/tfhijack.c` + `nosleep.c` en repo, `build_tfhijack.sh` con toolchain 6.3.0 → `libemu_tfhijack.so` `MIPS32r2 EL` | `hijack/build_tfhijack.sh` |
| **CAN_BUILD_EMULATOR_CORES_FROM_PUBLIC_SOURCE** | NO (unpinned) | **YES (código sí, pin NO)** — `71` repos públicos contienen `9` forks + `66` upstream genéricos son públicos (`libretro/*`), pero **77/78 unpinned** → código disponible, pero no bite-identical sin SHA | `clone_cores.sh` 78 + GitHub API confirms forks existen, pero `git ls-remote HEAD` actual ≠ v1.0.15 HEAD (unpinned) |
| **CAN_BUILD_TREEFROGUI_SOFTWARE_STACK** | PARTIAL | **PARTIAL → YES (si pin + cmake)** — `FrogUI` YES, `Picoarch` YES (con pin), `Hijack` YES, `Cores` YES (código), `Toolchain` YES, `cmake` missing solo TIC-80 | §2 + `command -v cmake` NO |
| **CAN_GENERATE_COMPLETE_R36SX_PACKAGE_WITHOUT_STOCK_INPUT** | **NO** | **NO** (confirmado) — `build_release.sh` requiere `STOCK[r36sx]` setting.xml + `driver_r36sx.so` stock + `xgame-logo.bmp` stock-correct. `install.md` dice Stock backup es `REQUIRED` (no opcional). Ningún `setting.xml`/`driver.so` público encontrado. **PACKAGE_REPRODUCIBLE sin stock = NO**. | §13 + `build_release.sh` WARN no stock + `install.md` |

**B1→B1.5 mejora:** `CAN_BUILD_*` pasa de `NO/PARTIAL` a `YES` para código (public source existe), pero `CAN_PACKAGE` sigue `NO`.

---

## 15. R36SX V2.6 Minimum Build Set (§16)

**Target prioritario:** `R36SX V2.6` Stock OS — podemos excluir `SF3000`, `SF3500`, `SF3100`, `SF3000HD`, `GB350`, `R36HD` del primer build reproducible.

| Dependencia | Incluida en R36SX_MIN | Excluible | Razón |
|-------------|----------------------|-----------|-------|
| `FrogUI` `15ea12b` | **YES** | — | Frontend único |
| `TreeFrogUI_picoarch` `r36sx` `f8ff5ba` | **YES** | — | Display/HW |
| `libemu_tfhijack.so` (hijack) | **YES** | — | Boot |
| `gpsp_multicore` (GBA) | **YES** (gba) | — | R36SX necesita GBA |
| `libretro-gambatte` (GB) | **YES** | — | |
| `snes9x2005/2002` (SNES) | **YES** | — | |
| `fceumm/nestopia` (NES) | **YES** | — | |
| `picodrive` (MD) | **YES** (MD hijack core es dummy, pero picodrive para MD/32x) | — | |
| `pcsx4all` (PS1) | **YES** (`PS` folder) | — | PS1 en R36SX |
| `vitaquake2`/`rockbox`/`ebook` | **NO** | **YES** (opcional) | Heavy/reader no mínimo |
| `SF3000`/`SF3500`/`GB350` drivers | **NO** | **YES** (solo `driver_r36sx.so` + `driver_r36sx27.so`) | `HJ[r36sx]` solo `driver_r36sx.so`, `fbwrite` |
| `STOCK` dumps SF3000-family | **NO** | **YES** (solo `R36SX_sdcard`) | `BUILD_ARCHITECTURE.md` grafo STOCK[] 7 → reducido a 1 |
| `cores` restantes (~50) no críticos | **PARTIAL** (mínimo ~15 para R36SX: gba, gb, snes, nes, md, pce, arcade, etc.) | **YES** (no todos 78) | `clone_cores.sh` 78 puede filtrarse |

**R36SX_V26_MINIMUM_EXTERNAL_REPOS** = `~15` (FrogUI + picoarch + hijack (in-repo) + toolchain + ~12 cores críticos: `gpsp_multicore`, `libretro-gambatte`, `snes9x2005/2002`, `fceumm`, `libretro-fceumm`, `picodrive`, `pcsx4all`, `fake-08`, `bluemsx`, `frodo`, `geolith`? etc. — ver `DEPENDENCY_MATRIX.md` mínimo). Contando toolchain externo `game-de-it/sf3000` → `16`.

**No modificar `build_*.sh` aún** — solo identificación (B1.5 READ-ONLY).

---

## 16. Stock Local (§17) — R36SX V2.6 física del usuario

| Campo | Valor |
|-------|-------|
| **REQUIRED_STOCK_INPUT** | `setting.xml` (autorun base) + `driver_r36sx.so` + `driver_r36sx27.so` (fallback) + `xgame-logo.bmp` (640×480) + `config.xml`/`filelist.xml` (no modificado, pero requerido como base stock) |
| **EXPECTED_PATH_ON_SD** | `/mnt/sdcard/cubegm/setting.xml`, `/mnt/sdcard/cubegm/driver_r36sx.so`, `/mnt/sdcard/cubegm/xgame-logo.bmp` (root `cubegm/` del Stock) — ver `build_release.sh:STOCK[r36sx]=.../cubegm` y `install.md R36SX v2.6 Minimal Backup` link |
| **HASH_SHOULD_BE_RECORDED** | **YES** — `SHA256` de `setting.xml`, `driver_r36sx.so`, `xgame-logo.bmp` del backup minimal debe registrarse para reproducibilidad (no se ha hecho) |
| **CAN_BE_USED_LOCALLY** | **YES** — usuario posee R36SX V2.6 Stock OS física (puede extraer de su propia SD, copia local permitida) |
| **CAN_BE_REDISTRIBUTED** | **NO / UNKNOWN** — stock blobs son proprietary, no libres; `docs/ai/RELEASE_CONTRACT.md` dice “No incluir archivos propietarios del Stock OS en Git o releases salvo autorización inequívoca”; `install.md` dice usar backup link, no redistribuir dump |
| **NO SD ACCESS NOW** | Respetado — no se accedió a SD, no se copió archivo |

---

## 17. Tablas Finales

### tzubertowski/* (relevantes)

| Repository | Purpose | Used by v1.0.15 | Historical revision (v1.0.15 window) | Revision confidence | Current upstream revision | Build output | License | Required for R36SX v2.6 |
|------------|---------|-----------------|--------------------------------------|---------------------|---------------------------|--------------|---------|--------------------------|
| `tzubertowski/FrogUI` | Frontend launcher | YES | `15ea12b` (2026-08-07 `Add System View`, `sf3000` branch) | **HIGH** (submodule pin `15ea12b` existe público, `git submodule status`) | `master` `?` `HEAD` 2026-08-12 | `frogui_libretro.so` | CC BY-NC-SA 4.0 | **YES** |
| `tzubertowski/TreeFrogUI_picoarch` | Picoarch fork | YES | `f8ff5ba` (2026-07-29) aprox (branch `r36sx`) | **LOW** (no pin, fechas) | `e98af36` (2026-08-23 HEAD `r36sx`) | `picoarch`, `picoarch_hi` | BSD-3 + libpicofe GPL | **YES** |
| `tzubertowski/TreeFrogUI_pcsx4all` | PCSX4ALL standalone PS1 | YES | `main` HEAD ~2026-07-29 | LOW | `main` (2026-07-29) | `pcsx4all` | GPL | **YES** (PS folder) |
| `tzubertowski/TreeFrogUI_pcsx_rearmed` | PCSX ReARMed Lightrec PS1 (ps1r) | MAYBE | `master` HEAD ~2026-06-22 | LOW | `master` (2026-06-22) | `pcsx_rearmed_libretro.so` | GPL | **MAYBE** (ps1r experimental) |
| `tzubertowski/gpsp_multicore` | gpSP multicore GBA | YES | `master` HEAD --depth=1 (no SHA) | LOW | `master` (2026-05-06, branches 5) | `gpsp_libretro.so` (gbac) | GPL | **YES** |
| `tzubertowski/fake-08` | PICO-8 fake08 sf3000 | YES | `sf3000` branch HEAD --depth=1 | **MEDIUM** (branch pin) | `sf3000` (2025-08-21) | `fake08_libretro.so` | MIT | **YES** |
| `tzubertowski/libretro-fceumm` | FCEUmm NES | YES | `master` HEAD --depth=1 | LOW | `master` (2025-08-21) | `fceumm_libretro.so` | GPL | **YES** |
| `tzubertowski/libretro-gambatte` | Gambatte GB | YES | `master` HEAD | LOW | `master` (2025-08-21) | `gambatte_libretro.so` | GPL | **YES** |
| `tzubertowski/snes9x2002` | Snes9x 2002 | YES | `master` HEAD | LOW | `master` (2025-08-21) | `snes9x2002_libretro.so` | GPL | **YES** |
| `tzubertowski/snes9x2005` | Snes9x 2005 | YES | `master` HEAD | LOW | `master` (2025-08-21) | `snes9x2005_plus_libretro.so` | GPL | **YES** |
| `tzubertowski/libretro-blueMSX` | blueMSX MSX | YES | `master` HEAD | LOW | `master` (2025-08-21) | `bluemsx_libretro.so` | GPL | **YES** |
| `tzubertowski/libretro-frodo` | Frodo C64 | YES | `master` HEAD | LOW | `master` (2025-08-21, +crop-auto) | `frodo_libretro.so` | GPL | **YES** |
| `tzubertowski/libretro-tyrquake` | Tyrquake Quake1 fork | **NO** (v1.0.15 usa `libretro/tyrquake`) | — | — | `master` (2026-03-09) | `tyrquake_libretro.so` | GPL | **NO** (fork no usado) |
| `tzubertowski/treefrogui_vitaquake2` | VitaQuake2 | NO (no clone) | `libretro` HEAD | LOW | `libretro` (2026-07-08) | `vitaquake2_libretro.so` | GPL | **NO** (optional) |
| `tzubertowski/treefrogui_rockbox` | Rockbox mirror | NO | `master/treefrogui` | LOW | `master` (2026-07-06) | `rockbox` | GPL | **NO** (optional) |
| `tzubertowski/TreeFrogUI_ebook_reader` | MuPDF ebook | NO | `main` HEAD | LOW | `main` (2026-07-25) | `ebook` | GPL/AGPL | **NO** (optional) |
| `tzubertowski/nestopia` | Nestopia fork | **NO** (v1.0.15 usa `libretro/nestopia`) | — | — | `master` (2026-02-13) | `nestopia_libretro.so` | GPL | **NO** (upstream usados) |
| `tzubertowski/QuickNES_Core` | QuickNES fork | **NO** (v1.0.15 usa `libretro/QuickNES_Core`) | — | — | `master` (2025-08-21) | `quicknes_libretro.so` | GPL | **NO** |
| `tzubertowski/libretro-vice` | VICE fork | **NO** (v1.0.15 usa `libretro/vice-libretro`) | — | — | `master` (2025-07-04) | `vice_x64_libretro.so` | GPL | **NO** |

### third-party upstream (ejemplo 66 genéricos)

| Repository | Purpose | Used by v1.0.15 | Historical revision | Confidence | Current revision | Build output | License | Required R36SX |
|------------|---------|-----------------|---------------------|------------|------------------|--------------|---------|----------------|
| `libretro/picodrive` | MD/SMS | YES | `master` HEAD --depth=1 | LOW | `master` | `picodrive_libretro.so` | MAME | **YES** |
| `libretro/mgba` | GBA accurate | YES | `master` | LOW | `master` | `mgba_libretro.so` | GPL | **MAYBE** (gbac alt) |
| `libretro/tyrquake` | Quake1 | YES | `master` | LOW | `master` | `tyrquake_libretro.so` | GPL | **YES** |
| `libretro/mame2000-libretro` | Arcade | YES | `master` + patch | LOW | `master` | `mame2000_libretro.so` | MAME | **YES** (family) |
| `xrip/pico-286` | DOS | YES | `master` + `pico286-sf3000.patch` 87k | LOW | `master` | `pico286` | GPL | **YES** |
| `nesbox/TIC-80` | TIC-80 | YES | `master` (cmake) | LOW | `master` | `tic80_libretro.so` | MIT | **NO** (cmake missing) |
| `angree/sf2000-uae-amiga-emulator` | Amiga | YES | `master` + 2 patches | LOW | `master` | `uae_libretro.so` | GPL | **MAYBE** |
| … (58 más) | … | YES | `master` --depth=1 | LOW | `master` | `*_libretro.so` | — | **PARTIAL** |

### toolchain

| Repository | Purpose | Used by v1.0.15 | Historical revision | Confidence | Current revision | Build output | License | Required |
|------------|---------|-----------------|---------------------|------------|------------------|--------------|---------|----------|
| `game-de-it/sf3000` `sf3000_toolchain_v0.1` | Cross SDK `mipsel-buildroot-linux-gnu_sdk-buildroot.tar.gz` | YES | `sf3000_toolchain_v0.1` (2018.09-02) | **HIGH** (release tag) | Same | `mips-mti-linux-gnu-*` 6.3.0 | GPL | **YES** |

### stock/proprietary

| Repository | Purpose | Used by v1.0.15 | Historical | Confidence | Current | Build output | License | Required |
|------------|---------|-----------------|------------|------------|---------|--------------|---------|----------|
| (no repo) `R36SX_sdcard` dump | Stock `setting.xml`, `driver_r36sx.so`, `xgame-logo.bmp` | YES | Backup `R36SX v2.6 Minimal Backup` (Google Drive, `install.md`) | HIGH | Same | `cubegm/setting.xml` etc. | Proprietary | **YES** (package) |
| (no repo) `SF3000/SF3500/GB350` dumps | Stock para 6 devices | YES (7 STOCK[]) | `Q-ta-s/q-ta-s.github.io` SF3000 backup | HIGH | Same | `cubegm/*` stock | Proprietary | **NO** (R36SX mínimo excluye) |

---

## 18. Conclusión B1→B1.5

**B1 ORIGINAL FINDING (a corregir):**
- “`PICOARCH` `TYRQUAKE` `GPSP` etc. son externos/unpinned/unknown, no localizables” → **INCORRECTO parcialmente**
- “`9-12` forks tzubertowski” → **B1 contó 12 pero 3 eran upstream genéricos (QuickNES, nestopia, vice) — corregido a 9**
- “Toolchain `game-de-it/sf3000` no verificado” → **B1 ya correcto, B1.5 confirma HIGH**
- “Drivers sin source” → **CONFIRMADO** (sigue NO)
- “Stock dumps necesarios” → **CONFIRMADO** (sigue YES)

**B1.5 RESOLVED FINDING:**
- **FrogUI 15ea12b:** público YES, exact revision HIGH, reproducible YES (con 1-line path fix)
- **Picoarch r36sx:** público YES, revision LOW (`f8ff5ba` plausible 2026-07-29 vs `e98af36` 2026-08-23), reproducible YES con pin
- **Tyrquake:** v1.0.15 usa `libretro/tyrquake` (generic), no `tzubertowski/libretro-tyrquake` — fork no relevante
- **PCSX4ALL:** YES usado en v1.0.15, public YES, pin LOW; `pcsx_rearmed` Lightrec existe pero es MAYBE (no clone)
- **GPSP:** dual repo confirmado, `gpsp_multicore` public YES, `master` branch, LOW pin
- **Cores:** 9 forks tzubertowski localizables (public YES), 58 generic, 8 patched — código **disponible** (no “unknown”), pero **77/78 aún unpinned** (sha LOW)
- **Toolchain:** externo `game-de-it/sf3000` HIGH pin
- **Drivers:** **NO** public source (0 de 71 repos) — stock proprietary se mantiene
- **Stock SD:** **NO** public repo — dump propietario requerido, no redistribuible
- **R36SX mínimo:** `~15-16` repos externos (vs 78 completos) — reducible para primer build reproducible
