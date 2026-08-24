# DEVELOPMENT.md — Flujo de Desarrollo — TreeFrogUI R36SX V2.6 Fork

## 1. Principio

> Leer → Verificar baseline → Auditar → Plan mínimo → Implementar → Build → Host test → Preparar artefacto device → **STOP humano físico** → Registrar → Commit (ask) → Push (ask) → PR upstream.

Todo cambio pasa por gates `docs/ai/VALIDATION.md`. Regla permanente: **la evidencia manda sobre el plan** (`AGENTS.md §15`).

## 2. Startup obligatorio (cada sesión)

1. `AGENTS.md` → `docs/PROJECT_STATE.md` → `CONTEXT_MAP.md` (verificar mutable con `git rev-parse HEAD`, `git status --short --branch`, `git submodule status`, `git remote -v`)
2. `python scripts/agent_preflight.py` (`--allow-dirty` solo inspección) y/o `python tests/test_agent_context_contract.py` → `PREFLIGHT_RESULT=PASS` o `FAIL:DIRTY_WORKTREE` explicado
3. Clasificar `CLASS A–E` (`docs/ai/VALIDATION.md`, `AGENTS.md §6`)
4. Delegar con privilegio mínimo (`treefrog-lead` → `audit|implement|review|release|upstream-sync`)

Si `DIRTY_WORKTREE` no explicado → reportar `git status` y pedir autorización antes de editar.

## 3. Flujo por clase

### CLASS A — Context/docs
`AGENTS.md`, `CONTEXT_MAP.md`, `DECISIONS.md`, `docs/`:
```
READ → VERIFY → AUDIT → PLAN MIN → EDIT → STATIC PASS (test_agent_context_contract + agent_preflight) → COMMIT(ask)
```
No requiere hardware.

### CLASS B — Host tooling
Scripts WSL, toolchain, audits, `tools/dev-doctor.sh`:
```
+ HOST PASS (test_release_base_selection.sh, bash -n, dev-doctor)
```

### CLASS C/D/E — Runtime/Device/Release
`frogui`, `picoarch`, `hijack/zhijack`, `setting.xml`, drivers, ZIP:
```
+ BUILD (./build_all.sh o hijack/build_tfhijack.sh, requiere toolchain WSL) → HOST PACKAGING checks → PREPARE ARTIFACT (release/latest/release) → STOP → HUMAN PHYSICAL (R36SX V2.6 real, docs/TESTING.md) → RECORD (device, baseline, SHA, matrix, observaciones, PASS/FAIL, DATE) → COMMIT(ask) → PUSH(ask) → PR
```

**Nunca auto-claim `PHYSICAL PASS`.** Solo humano con hardware reporta `PHYSICAL PASS` fechado.

## 4. Workspace multi-repositorio

- **Parent** `treefrog-ui` (este repo) — build scripts, patches, staging, docs, `frogui/` submodule.
- **FrogUI** `tzubertowski/FrogUI@sf3000 15ea12b` — submodule `frogui/`, **no editar como monolito**. Reglas parent-owned en `docs/components/FROGUI.md`. Cambios = PR separado en `tzubertowski/FrogUI`.
- **Picoarch** `tzubertowski/TreeFrogUI_picoarch@r36sx` (f8ff5ba local) — hermano `~/sf3000-work/picoarch`, no submodule. Cambios = PR separado.
- **Cores** 78 clones `cores/` (gitignored) — upstream `libretro/*` + 9 forks `tzubertowski/*` — no versionar `cores/` en este repo.
- **Toolchain** `game-de-it/sf3000` — `~/sf3000-work/sf3000toolchain` (no submodule).

```
feature treefrog-ui
  ├── PR ozkaoz/treefrog-ui-r36sx → tzubertowski/treefrog-ui
  ├── (si toca FrogUI) PR tzubertowski/FrogUI@sf3000 — linkeados
  └── (si toca picoarch) PR tzubertowski/TreeFrogUI_picoarch@r36sx — linkeados
```

No fabricar commit parent que mezcle histories.

## 5. Worktrees para experimentos

Investigaciones diagnósticas temporales = worktrees/branches disposable:

```sh
git worktree add ../treefrog-ui-r36sx-exp-diag -b exp/diag-foo r36sx-v2.6-dev
cd ../treefrog-ui-r36sx-exp-diag
# ... prueba, no toca r36sx-v2.6-dev
git worktree remove ../treefrog-ui-r36sx-exp-diag
git branch -D exp/diag-foo  # si descartado
```

Ver `git worktree list`, `git stash list`. Preflight nunca modifica worktrees.

## 6. Commits y ramas

- Ramas: `r36sx-v2.6-dev` (dev), `feature/r36sx-<topic>` para PRs. No `force push` tras review.
- Commits enfocados, sin cambios no relacionados. Mensaje: `area: verbo` (ej. `hijack: fix r36sx SIGBUS fallback count`).
- `git commit`/`push`/`tag`/`gh release` = `ask` (humano autoriza). Verificar `git diff --stat`, `git remote -v`, `SHA` tras push.
- Preservar `origin` (fork) y `upstream` (tzubertowski). Push solo a `origin`.

## 7. Qué tocar / qué no

| Safe (CLASS A/B) | Requiere gate C/D/E + humano + decisión |
|------------------|------------------------------------------|
| `docs/`, `AGENTS.md`, `CONTEXT_MAP.md`, `DECISIONS.md`, `scripts/agent_preflight.py`, `tools/dev-doctor.sh`, `tests/*`, `.gitignore` (conservador) | `frogui/*.c`, `hijack/*.c`/`zhijack.tpl.sh`, `picoarch` (externo), `drivers/*.so`, `setting.xml`, `kernel/DTB/rootfs`, `build_release.sh` portability, SD payload |

## 8. Checkpoints físicos

Registrar en `docs/checkpoints/` o `docs/PROJECT_STATE.md` post-physical:

```
FEATURE= DEVICE=R36SX V2.6 FIRMWARE=Stock v2.6 Minimal ARTIFACT_SHA256=... TEST_MATRIX=... USER_OBSERVATIONS=... PASS/FAIL=... DATE=...
```

Ver `docs/TESTING.md`, `docs/ai/VALIDATION.md`, `docs/HARDWARE.md`.

## 9. Enlaces

- `AGENTS.md` — constitución
- `docs/PROJECT_STATE.md` — estado mutable
- `docs/BUILDING.md` — build detallado
- `docs/TESTING.md` — gates
- `docs/HARDWARE.md` — facts device
- `docs/SD_SAFETY.md` — SD contract
- `docs/UPSTREAM.md` — contribución
- `docs/RELEASING.md` / `docs/ai/RELEASE_CONTRACT.md` — release
- `docs/dev/*` — investigaciones profundas (reproducibilidad, WSL, dependency lock)
