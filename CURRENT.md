# CURRENT.md — Snapshot Verificable — TreeFrogUI R36SX V2.6 Fork

> **CURRENT.md IS A CACHE.** Instantánea potencialmente obsoleta. La autoridad es `git status` / `git log` / `git submodule status` / `git remote -v` y la evidencia directa. Si este fichero contradice Git, gana Git — reparar este fichero primero. No es changelog ni historial.

**Fecha:** 2026-08-23 (UTC)
**Repo local:** `D:\R36SX\treefrog-ui-r36sx`
**GitHub Fork (origin):** `https://github.com/ozkaoz/treefrog-ui-r36sx.git` — `origin`
**Upstream:** `https://github.com/tzubertowski/treefrog-ui.git` — `upstream`
**Branch activa:** `r36sx-v2.6-dev` (creada desde `v1.0.15`)
**HEAD:** `27f3bf33e906d90e0cd267059bf0559afc6f8a05` — `27f3bf3 Clarify R36HD backup entry` (tag `v1.0.15`)
**Baseline:** `v1.0.15` → `27f3bf33e906d90e0cd267059bf0559afc6f8a05`
**Tag upstream verificado:** `v1.0.15` existe (`git rev-parse v1.0.15`); `v1.1.0_b` es `upstream/main` HEAD actual (`41f15e24e124f90ad23146de217a8f3408921d02`) — no es baseline.
**Submodule `frogui`:** `15ea12bb4f6f642b1ec02aabebbad33e5e95ed2b` — `v0.1.3-123-g15ea12b` — branch `sf3000` — URL `git@github.com:tzubertowski/FrogUI.git` (local override HTTPS `https://github.com/`→`git@github.com:` via `url.insteadOf`)
**Remotes:**
```
origin    https://github.com/ozkaoz/treefrog-ui-r36sx.git (fetch/push)
upstream  https://github.com/tzubertowski/treefrog-ui.git (fetch/push)
```
**Worktree (al bootstrap, antes de commit):** `DIRTY` — ficheros bootstrap CLASS A sin commitear (AGENTS.md, CURRENT.md, CONTEXT_MAP.md, DECISIONS.md, docs/ai/*, scripts/agent_preflight.py, tests/test_agent_context_contract.py, .opencode/agents/*). Ver `git status --short --branch`. `PREFLIGHT_RESULT=FAIL` sin `--allow-dirty`; `PASS` con `--allow-dirty` es esperado en esta fase.
**Último preflight:** `python scripts/agent_preflight.py --allow-dirty` → `PREFLIGHT=PASS (allow-dirty)` / sin flag → `FAIL:DIRTY_WORKTREE` (correcto, no es error). `python tests/test_agent_context_contract.py` → `PASS` esperado tras bootstrap.
**Objetivo actual:** Bootstrap CLASS A completado. Fork `ozkaoz/treefrog-ui-r36sx` creado y clonado en `D:\R36SX\treefrog-ui-r36sx`; rama `r36sx-v2.6-dev` anclada a `v1.0.15`; submodules inicializados; infraestructura de agentes/documental implantada. NO compilar, NO tocar runtime/hijack/drivers/SD, NO publicar.
**Golden states:**
```
SOURCE_BASELINE = v1.0.15 + 27f3bf33e906d90e0cd267059bf0559afc6f8a05
PHYSICAL_GOLDEN = NONE / NOT YET ESTABLISHED
RELEASE_GOLDEN  = NONE / NOT YET ESTABLISHED
```
**Riesgos conocidos:**
- R36SX v2.6/v2.7 comparten `install_first/r36sx` pero el kernel/DTB difiere; la selección de `driver_r36sx.so` vs `driver_r36sx27.so` es runtime (SIGBUS-count) — documentado en `hijack/zhijack.tpl.sh`.
- `build_release.sh` contiene rutas absolutas del mantenedor (`/home/tomaszz/...`) — requiere revisión antes de build reproducible en WSL.
- `.gitmodules` usa SSH (`git@github.com:`) — requiere `url.insteadOf` local HTTPS en Windows sin clave SSH.
- `release/` no existe en este checkout (gitignored) — no hay artefacto empaquetado que validar.
- `PHYSICAL_EVIDENCE=NONE — NOT TESTED` — ninguna afirmación de validación en hardware.

**Siguiente acción exacta:**
1. Verificar `python tests/test_agent_context_contract.py` y `python scripts/agent_preflight.py --allow-dirty`.
2. Mostrar `git status --short --branch; git diff --stat; git remote -v; git submodule status; git log -5`.
3. Hacer commit CLASS A del bootstrap (requiere aprobación humana) — NO push, NO release.
4. Siguiente fase (post-bootstrap): toolchain WSL, auditoría `build_release.sh` / staging, pero NO modificar runtime/hijack hasta decisión explícita.

**Change class del bootstrap:** `CLASS A` (solo documentación/contexto + operaciones Git de fork/baseline; `RUNTIME_CHANGED=NO`, `HIJACK_CHANGED=NO`, `SD_PAYLOAD_CHANGED=NO`).

**Validación:** `STATIC PASS` (vía `test_agent_context_contract.py`); `HOST PASS` pendiente de preflight limpio post-commit; todos los gates superiores `NOT TESTED`.
