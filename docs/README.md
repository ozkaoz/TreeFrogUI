# docs/README.md — Índice — TreeFrogUI R36SX V2.6 Fork

> **Router de documentación.** No es snapshot. Para estado mutable: `git rev-parse HEAD`, `docs/PROJECT_STATE.md`.

## Inicio rápido

- **Propósito y reglas durables:** `AGENTS.md` (raíz) — constitución provider-neutral
- **Estado mutable verificado:** `docs/PROJECT_STATE.md` — HEAD `76a6dca`, branch `r36sx-v2.6-dev`, baseline `v1.0.15 27f3bf3`, FrogUI `15ea12b`
- **Router por subsistema:** `CONTEXT_MAP.md` — FrogUI, picoarch, input, audio, cores, hijack, R36SX, release, build, tests, docs

## Desarrollo

| Tema | Doc canónico | Qué cubre |
|------|--------------|-----------|
| **Flujo dev** | `docs/DEVELOPMENT.md` | READ→VERIFY→AUDIT→PLAN→BUILD→HOST TEST→STOP HUMAN PHYSICAL→RECORD→COMMIT→PUSH→PR, worktrees, multi-repo |
| **Build** | `docs/BUILDING.md` | WSL Ubuntu, `~/sf3000-work`, toolchain `6.3.0`, `clone_cores.sh` 78, `build_all.sh`, `BUILD_FLAG_CONSISTENCY=KNOWN_DEBT`, `PORTABILITY_DEBT` `/home/tomaszz` |
| **Tests** | `docs/TESTING.md` | Taxonomía STATIC/HOST/BUILD/PACKAGING/PHYSICAL, comandos, inventario `tests/*`, regla `PHYSICAL` humano |
| **Hardware** | `docs/HARDWARE.md` | R36SX V2.6 facts (FN 16/mask 0x10000, L3 1 R3 2, 640×480 fbwrite), familias 7 devices HJ[], NOSLEEP_ADDRS |
| **SD safety** | `docs/SD_SAFETY.md` | Layout no letra, backup+SHA, solo autorizados, nunca auto-format/fsck, eject humano, WSL `/mnt/g` |
| **Upstream** | `docs/UPSTREAM.md` | `upstream→fork→branch→validation→commit→push→PR`, multi-repo PRs linkeados, confianza HIGH/MEDIUM/LOW |
| **Release** | `docs/RELEASING.md` (upstream) + `docs/ai/RELEASE_CONTRACT.md` + `docs/ai/VALIDATION.md` | `TreeFrogUI_<ver>.zip` + `update.zip`, numeric-line base, `PACKAGING+CLEAN-INSTALL+DOWNLOAD-BACK` |

## Tiempo de ejecución e infraestructura

- **Release contract R36SX:** `docs/ai/RELEASE_CONTRACT.md` — `Stock OS + 1 ZIP → TreeFrogUI, POST_INSTALL_MANUAL_FIXES=0`
- **Gates:** `docs/ai/VALIDATION.md` — `STATIC/HOST/BUILD/PACKAGING/PHYSICAL/CLEAN-INSTALL/DOWNLOAD-BACK PASS/FAIL`
- **Componente FrogUI:** `docs/components/FROGUI.md` — submodule `15ea12b sf3000`, parent-owned (no `frogui/AGENTS.md`)
- **Decisiones duraderas:** `DECISIONS.md` — D001 baseline v1.0.15

## Referencias técnicas profundas

| Doc | Contenido | Estado |
|-----|-----------|--------|
| `docs/dev/BUILD_ARCHITECTURE.md` | Grafo build/boot completo, TARGET mips32r2, 11 hardcode paths, blockers | B1 READ-ONLY audit, no movido esta fase |
| `docs/dev/DEPENDENCY_MATRIX.md` | Matriz 78 cores, pinned 1, toolchain 6.3.0, reproducibilidad | B1 |
| `docs/dev/DEPENDENCY_LOCK.md` + `deps/treefrog-v1.0.15.lock.json` | Lock determinista `schema 1`, 77 cores, `NOT_CLAIMED`, `--check` | B2.2A VALID |
| `docs/dev/UPSTREAM_REPOSITORY_MAP.md` | 71 repos tzubertowski map, picoarch/frogui/tyrquake/gpsp reconciliación | B1.5 |
| `docs/dev/WSL_ENVIRONMENT.md` | WSL1 Ubuntu-24.04, NTFS CRLF artifact, toolchain paths | B1 |
| `docs/cores/*.md` | ebook, pce, ps1, etc. guías por core | Legacy upstream, retenido |
| `docs/standalone-apps.md`, `docs/osd-battery-volume.md` etc. | Apps standalone, OSD | Retenido |

## Investigaciones / legacy

- `docs/investigate-later.md`, `docs/pcsx*.md`, `docs/osd-battery-volume.md` — no mover esta fase (`EXISTING_DOC_FILES_MOVED=NO`)
- Futuro: `docs/checkpoints/`, `docs/investigations/` para `PHYSICAL_GOLDEN` records (no en `AGENTS.md`)
- Mutable histórico no es durable — ver `AGENTS.md §5` Source of Truth

## Herramientas

- `scripts/agent_preflight.py` — preflight no destructivo (Git/remotes/submodule/worktree)
- `tools/dev-doctor.sh` — checker WSL/toolchain/siblings (PASS/WARN/FAIL, no instala/modifica)
- `tests/test_agent_context_contract.py` — contrato IA STATIC
- `tests/test_dependency_lock.py`, `scripts/dev/validate_dependency_lock.py`, `scripts/dev/resolve_dependency_lock.py` — lock

Ver `AGENTS.md` para flujo agente y `CONTRIBUTING.md` para humanos.
