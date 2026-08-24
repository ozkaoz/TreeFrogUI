# PROJECT_STATE.md — Snapshot Mutable — TreeFrogUI R36SX V2.6 Fork

> **THIS FILE IS A SNAPSHOT AND MUST BE VERIFIED AGAINST GIT BEFORE ACTING ON MUTABLE VALUES.**
> Autoridad: `git rev-parse HEAD`, `git status --short --branch`, `git submodule status`, `git remote -v`, `git tag --list`, `git log upstream/main..HEAD`.
> Si este fichero contradice Git, gana Git — reparar este fichero primero.

**LAST_VERIFIED_UTC:** `2026-08-24T00:40:00Z` (WSL `date -u`, re-verificar con `git log -1 --format=%ci HEAD`)
**REPO:** `D:\R36SX\treefrog-ui-r36sx` → WSL `/mnt/d/R36SX/treefrog-ui-r36sx`
**Protocol:** `TREEFROGUI_AGENT_PROTOCOL=1` (ver `docs/ai/MULTIREPO_COORDINATION.md`)

## Git

| Campo | Valor | Verificación |
|-------|-------|--------------|
| **CURRENT_BRANCH** | `r36sx-v2.6-dev` | `git rev-parse --abbrev-ref HEAD` |
| **CURRENT_HEAD** | `76a6dca2dba9c69b42714c89fc7f3d6fa162e7d4` (`76a6dca`) | `git rev-parse HEAD` |
| **UPSTREAM_REMOTE** | `https://github.com/tzubertowski/treefrog-ui.git` (`upstream`) | `git remote get-url upstream` |
| **FORK_REMOTE (origin)** | `https://github.com/ozkaoz/treefrog-ui-r36sx.git` (`origin`) | `git remote get-url origin` |
| **upstream/main HEAD** | `41f15e24e124f90ad23146de217a8f3408921d02` (`v1.1.0_b` lineage) | `git rev-parse upstream/main` |
| **AHEAD_BEHIND vs upstream/main** | `ahead 2, behind 27` aprox (2 commits fork vs 27 upstream desde v1.0.15) | `git rev-list --left-right --count HEAD...upstream/main` |
| **WORKTREE** | `DIRTY` — CRLF artifact (`git status --short \| wc -l` ≈93, ver `WSL_ENVIRONMENT.md` autocrlf) — no es divergencia de contenido | `git status --short --branch` |
| **Submodule `frogui`** | `15ea12bb4f6f642b1ec02aabebbad33e5e95ed2b` (`v0.1.3-123-g15ea12b`, branch `sf3000`) | `git submodule status` |

```
origin    https://github.com/ozkaoz/treefrog-ui-r36sx.git (fetch/push)
upstream  https://github.com/tzubertowski/treefrog-ui.git (fetch/push)
```

## Baseline y release

| Campo | Valor |
|-------|-------|
| **TARGET_REFERENCE_RELEASE** | `v1.0.15` |
| **TARGET_REFERENCE_TAG_SHA** | `27f3bf33e906d90e0cd267059bf0559afc6f8a05` (`Clarify R36HD backup entry`, `2026-08-17`) — `git rev-parse v1.0.15` |
| **FROGUI_SUBMODULE_SHA** | `15ea12bb4f6f642b1ec02aabebbad33e5e95ed2b` |
| **FROGUI_SUBMODULE_BRANCH** | `sf3000` (`.gitmodules`) |
| **DEPENDENCY_LOCK_PATH** | `deps/treefrog-v1.0.15.lock.json` |
| **DEPENDENCY_LOCK_STATUS** | `VALID` — `schema_version 1`, `77` cores locked, `78` declares, `historical_exactness=NOT_CLAIMED`, `python tests/test_dependency_lock.py` PASS |
| **DEPENDENCY_LOCK_CUTOFF** | `2026-08-20T16:14:20Z` (RELEASE_PUBLISHED_AT) — ver `docs/dev/DEPENDENCY_LOCK.md` |

## Golden states

```
SOURCE_BASELINE  = v1.0.15 + 27f3bf33e906d90e0cd267059bf0559afc6f8a05
PHYSICAL_GOLDEN  = NONE / NOT YET ESTABLISHED
RELEASE_GOLDEN   = NONE / NOT YET ESTABLISHED
```

- `PHYSICAL_GOLDEN = NONE` — no hay `CLEAN-INSTALL PHYSICAL PASS` fechado en R36SX V2.6 real. No inventar.
- `RELEASE_GOLDEN = NONE` — no hay `PACKAGING + CLEAN-INSTALL + DOWNLOAD-BACK PASS` publicado.

## Active components (multi-repo, `TREEFROGUI_AGENT_PROTOCOL=1`)

> Ver `docs/ai/MULTIREPO_COORDINATION.md` para arquitectura canónica. Verificar con `git` antes de actuar.

| Repository | Path (preferred) | Branch | HEAD | Role | Status |
|------------|------------------|--------|------|------|--------|
| **treefrog-ui-r36sx** (parent) | `/mnt/d/R36SX/treefrog-ui-r36sx` (WSL `~/sf3000-work/treefrog-ui-r36sx-build` mirror `bff0151`) | `r36sx-v2.6-dev` | `76a6dca2dba9c69b42714c89fc7f3d6fa162e7d4` (`76a6dca`) | **INTEGRATION (B)** | `DIRTY` Phase2 docs uncommitted, `AGENTS.md` + `MULTIREPO_COORDINATION.md` `PROTOCOL=1` |
| **FrogUI** | `~/sf3000-work/FrogUI` | `sf3000` | `15ea12bb4f6f642b1ec02aabebbad33e5e95ed2b` (`15ea12b`, fork `ozkaoz/FrogUI` `2f41ace` HEAD `master`) | **ACTIVE (A)** | `CLEAN` after `AGENTS.md` created (`TREEFROGUI_AGENT_PROTOCOL=1`), upstream `tzubertowski/FrogUI` |
| **TreeFrogUI_picoarch** | `~/sf3000-work/TreeFrogUI_picoarch` | `r36sx` | `e98af36e84ab915faea5f63143b4d1c810aa8776` (`e98af36`, baseline `f8ff5ba`) | **ACTIVE (A)** | `CLEAN` after `AGENTS.md` created (`PROTOCOL=1`), upstream `tzubertowski/TreeFrogUI_picoarch` |
| **TreeFrogUI_picoarch** (mirror) | `/mnt/d/R36SX/TreeFrogUI_picoarch` | `feature/fn-button-mapping` | `543699bc7b08f633934696b722ec41774d2ee968` (`543699b`) | **ACTIVE (A) mirror** | `DIRTY` 182, `AGENTS.md` created (same fork) |
| **TreeFrogUI_pcsx4all** | `~/sf3000-work/TreeFrogUI_pcsx4all` | — | — | **DEPENDENCY (C)** | `NOT FOUND` — `ozkaoz/TreeFrogUI_pcsx4all` `Repository not found`, no sibling clone |
| **cores** | `cores/` (`~/sf3000-work/cores` when populated) | — | 78 declares, 77 unique, `deps/treefrog-v1.0.15.lock.json` | **DEPENDENCY (C)** | `UNNECESSARY_AGENT_FILES_CREATED=0` |
| **toolchain** | `~/sf3000-work/sf3000toolchain` | `sf3000_toolchain_v0.1` | `mips-mti-linux-gnu-gcc 6.3.0` | **VENDOR (D)** | `PRESENT` |

`FROGUI_DEVELOPMENT_PATH= ~/sf3000-work/FrogUI` (fork `ozkaoz/FrogUI`, not `treefrog-ui-r36sx/frogui` submodule)
`PICOARCH_DEVELOPMENT_PATH= ~/sf3000-work/TreeFrogUI_picoarch` (fork `ozkaoz/TreeFrogUI_picoarch`, not `~/sf3000-work/picoarch` upstream clone)
`PCSX4ALL_DEVELOPMENT_PATH= UNCONFIRMED / NOT FOUND`
`PARENT_SUBMODULE_EDIT_POLICY= FROGUI_SUBMODULE_CHANGED=NO — do not edit treefrog-ui-r36sx/frogui, use sibling fork`

## Trabajo abierto

**OPEN_FEATURE_WORK=**
- Phase 2 — AI repository optimization: documentación + agent infra CLASS A/B (este snapshot). `RUNTIME_CHANGED=NO`, `BUILD_SCRIPT_BEHAVIOR_CHANGED=NO`. Ver `docs/README.md`.
- Próximo requerido: toolchain WSL validado (`cmake` ahora presente 3.28.3), staging `sdcard/cubegm` drivers, validar `build_release.sh` portability debt sin ejecutar.

**KNOWN_BLOCKERS=**
- `PORTABILITY_DEBT` — `build_release.sh:35-64` 11× `/home/tomaszz/sf3000-work` hardcode (documentado en `docs/BUILDING.md`, no modificado esta fase).
- `STOCK_DUMPS` — `R36SX_sdcard` y 6 dumps SF family propietarios no redistribuibles, requeridos para `build_release.sh:STOCK[]` (ver `docs/BUILDING.md`, `install.md#R36SX`).
- `WSL CRLF` — WSL1 `autocrlf` vs Windows `autocrlf=true` causa `DIRTY` masivo (≈93 files) sin divergencia SHA — mitigado por `.gitattributes` futuro, sin renormalización.

**KNOWN_TECHNICAL_DEBT=**
- `BUILD_FLAG_CONSISTENCY=KNOWN_DEBT` — `build_all.sh -mtune=74kc -mdspr2` vs `Makefile.sf3000 / frogui/build_libretro.sh -mtune=24kc`.
- `CMAKE` — ahora instalado (`3.28.3`) pero TIC-80 sigue opcional (ver `docs/BUILDING.md`).
- `Picoarch` branch `r36sx` unpinned (f8ff5ba local 2026-07-29 vs e98af36 upstream 2026-08-23) — lock usa cutoff, confianza LOW.
- `Cores` 77/78 unpinned (`--depth=1`) — lock candidate, not proven historical.

## Verificación rápida

```sh
# Desde WSL Ubuntu, repo /mnt/d/R36SX/treefrog-ui-r36sx
git rev-parse HEAD; git rev-parse --short HEAD
git status --short --branch | head -n 20
git submodule status
git remote -v
git tag --list | grep v1.0.15
git rev-parse v1.0.15
python tests/test_agent_context_contract.py
python scripts/agent_preflight.py --allow-dirty
python tests/test_dependency_lock.py
bash -n tools/dev-doctor.sh && ./tools/dev-doctor.sh
```

**UNCONFIRMED:** PRs upstream actuales no consultados (requiere `gh` + red). Usar `UNCONFIRMED` si no verificable, nunca asumir `none`.

---

*Snapshot mutable — reparar con `git` antes de actuar.*
