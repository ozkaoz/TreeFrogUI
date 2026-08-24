# UPSTREAM.md — Contribución Upstream — TreeFrogUI R36SX

## 1. Fork vs upstream

| Repo | URL | Rol |
|------|-----|-----|
| **upstream** | `https://github.com/tzubertowski/treefrog-ui.git` (`upstream`) | Fuente canónica (tzubertowski) |
| **fork** | `https://github.com/ozkaoz/treefrog-ui-r36sx.git` (`origin`) | R36SX V2.6 fork (este repo, rama `r36sx-v2.6-dev` desde `v1.0.15 27f3bf3`) |
| **siblings** | `tzubertowski/FrogUI@sf3000 15ea12b` (submodule `frogui/`), `tzubertowski/TreeFrogUI_picoarch@r36sx` (f8ff5ba), `tzubertowski/TreeFrogUI_pcsx4all`, 78 cores `libretro/*`, toolchain `game-de-it/sf3000` | Componentes separados, no monolito |

Preservar remotes `origin` y `upstream`. Push solo a `origin` salvo autorización explícita.

## 2. Flujo correcto

```
upstream (tzubertowski/treefrog-ui)
  ↓ git fetch upstream --tags
fork (ozkaoz/treefrog-ui-r36sx, branch r36sx-v2.6-dev o feature/r36sx-<topic>)
  ↓ local validation (AGENTS.md CLASS A/B/C/D/E gates)
  ↓ physical validation donde aplique (R36SX V2.6 humano, docs/TESTING.md)
  ↓ commit enfocado
  ↓ git push origin feature/r36sx-<topic>   (verificar SHA tras push)
  ↓ focused PR a upstream (tzubertowski/treefrog-ui)
  ↓ review → no force push salvo coordinado → link PRs componentes
```

```sh
git fetch upstream --tags
git checkout -b feature/r36sx-foo r36sx-v2.6-dev
# ... edit
python tests/test_agent_context_contract.py && python scripts/agent_preflight.py
git diff --stat; git status --short --branch
git commit -m "hijack: explain r36sx driver fallback"
git push -u origin feature/r36sx-foo
gh pr create --repo tzubertowski/treefrog-ui --base main --title "..." --body "..."
```

## 3. Multi-repositorio = commits/PRs separados

- `treefrog-ui` (parent) — build scripts, patches, staging, docs.
- `FrogUI` — frontend launcher (`frogui/` submodule). Cambios → PR en `tzubertowski/FrogUI@sf3000` (no editar `frogui/` como monolito; documentar parent-owned en `docs/components/FROGUI.md`).
- `TreeFrogUI_picoarch` — display/audio (`~/sf3000-work/picoarch@r36sx`). Cambios → PR en `tzubertowski/TreeFrogUI_picoarch@r36sx`.
- `cores` — 78 clones (no versionar `cores/` en parent).

**No fabricar** commits de integración parent que mezclen histories. Cada repo = commits/PRs separados, **linkeados** entre sí en descripción (`Related: https://github.com/tzubertowski/FrogUI/pull/...`).

## 4. Reglas duras

- **No `git push upstream`** sin autorización.
- **No `force push`** tras review iniciado salvo coordinado (`AGENTS.md §9`).
- **No cambios no relacionados** en mismo commit/PR.
- **No `git commit`/`push`/`tag`/`gh release` sin `ask`** (humano autoriza, ver `implement.md` / `release.md` permissions).
- Verificar SHA remoto tras push: `git ls-remote origin feature/r36sx-foo` == `git rev-parse HEAD`.

## 5. Provenance y confianza

Nunca afirmar "source commit oficial" sin pin. Usar:

| Confianza | Cuándo |
|-----------|--------|
| **HIGH** | SHA/tag fijado explícitamente (ej. `FrogUI` submodule `15ea12b`, `sf3000_toolchain_v0.1`) |
| **MEDIUM** | Branch fijado + cutoff date (`fake-08#sf3000`, `TreeFrogUI_picoarch@r36sx` f8ff5ba) |
| **LOW** | `default_branch HEAD` sin pin (`libretro/picodrive master` via `clone_cores.sh --depth=1`) |
| **UNCONFIRMED** | No resoluble sin red (`jaxe` 404) |

Nombrar `historical_exactness=NOT_CLAIMED` si no reproducido (ver `deps/treefrog-v1.0.15.lock.json`, `docs/dev/DEPENDENCY_LOCK.md`). Para cores unpinned, lock candidate `last commit on branch at or before 2026-08-20T16:14:20Z`.

## 6. Sincronización con upstream

```sh
git fetch upstream --tags
git tag --list | grep v1.0
git log --oneline --graph --decorate upstream/main --not HEAD | head -n 20
git rev-list --left-right --count HEAD...upstream/main
git submodule status  # 15ea12b
```

Agente `upstream-sync` (read-only): analiza divergencia, lista tags, recomienda `merge`/`rebase`/`cherry-pick` sin integrar. Ver `.opencode/agents/upstream-sync.md`.

Decisión de forward-port `v1.0.15 → v1.1.0_b` requiere `DECISIONS.md` explícita (no auto-merge).

## 7. Upstream feature PR cleanliness

```
UPSTREAM_FEATURE_DIFF_MUST_NOT_INCLUDE_AGENT_INFRASTRUCTURE=YES
```

Agent-infrastructure (`AGENTS.md`, `docs/ai/MULTIREPO_COORDINATION.md`, `docs/`, fork-only `tools/`) es **FORK/DEVELOPMENT INFRASTRUCTURE**. No incluirla en PRs de feature a upstream salvo que el PR contribuya infra intencionalmente.

```sh
# Antes de cada PR a upstream, verificar:
git diff --name-status upstream/<target>...HEAD
# debe NO incluir AGENTS.md, docs/ai/, docs/UPSTREAM.md infra
```

Ramas FN existentes (`feature/fn-button-mapping-v1015 b1a9799`, `feature/fn-button-mapping 543699b`) deben permanecer intactas — no hacerles amend/rebase para añadir infra.

## 8. Infra development vs clean PR

```
INFRA_DEVELOPMENT_MODEL_DOCUMENTED=YES
CLEAN_UPSTREAM_PR_BRANCH_REQUIRED=YES

DEVELOPMENT BASE:  infra/agent-coordination (parent) / infra/agent-rules (FrogUI, picoarch) — contains AGENTS.md
UPSTREAM PR BASE:  upstream/<target> (upstream/sf3000, upstream/r36sx, upstream/main)
```

Infra está disponible en `infra/*` para desarrollo asistido, pero **no debe entrar** en PRs de feature a menos que se proponga infra intencionalmente.

**Preparación limpia:**

1. Verificar commits funcionales validados
2. Crear rama limpia desde upstream: `git checkout -b feature/r36sx-foo upstream/<target>`
3. Cherry-pick **solo** commits funcionales: `git cherry-pick <sha>`
4. No cherry-pick `infra/*`
5. Inspeccionar: `git diff --name-status upstream/<target>...HEAD` — debe NO incluir `AGENTS.md`, `docs/ai/`, `tools/dev-doctor.sh`, `tools/workspace-doctor.sh`
6. Rechazar si aparece infra no relacionada

Ver `docs/ai/MULTIREPO_COORDINATION.md` §13 para modelo canónico.

## 9. Checklist PR (ver `.github/pull_request_template.md`)

- Diff enfocado (verificar `upstream/<target>...HEAD` no incluye infra)
- Baseline documentado (`docs/PROJECT_STATE.md` tag SHA)
- `STATIC/HOST/BUILD` PASS (logs)
- Sin binarios generados (`build/`, `*.so`, `release/`)
- ¿Requiere hardware? ¿Human PHYSICAL PASS fechado?
- Rollback considerado
- PR componente hermano linkeado
- Sin `/home/tomaszz` nuevo hardcode (ver `docs/BUILDING.md` debt)

Ver `docs/RELEASING.md`, `docs/ai/RELEASE_CONTRACT.md` para release gates `PACKAGING+CLEAN-INSTALL+DOWNLOAD-BACK`.
