# AGENTS.md — Constitución — TreeFrogUI R36SX V2.6 Fork

**Repo:** https://github.com/ozkaoz/treefrog-ui-r36sx
**Upstream:** https://github.com/tzubertowski/treefrog-ui
**Target primario:** R36SX V2.6 — Stock OS — TreeFrogUI (fork soporta 7 devices upstream, ver `docs/HARDWARE.md`)
**Baseline:** `v1.0.15` (SHA verificado `git rev-parse v1.0.15`) — rama `r36sx-v2.6-dev`
**Protocol:** `TREEFROGUI_AGENT_PROTOCOL=1` (ver `docs/ai/MULTIREPO_COORDINATION.md`)

> Constitución durable, provider-neutral. Valores mutables (HEAD, branch, SHA, worktree) viven en `docs/PROJECT_STATE.md` y en Git — nunca hardcodeados aquí.
> `CURRENT.md` es compat stub que redirige a `docs/PROJECT_STATE.md`.

```
AGENTS.md (constitución) → docs/PROJECT_STATE.md (snapshot mutable, verificar con git)
                         → CONTEXT_MAP.md (router)
                         → DECISIONS.md (duraderas)
                         → docs/ai/{VALIDATION.md, RELEASE_CONTRACT.md, MULTIREPO_COORDINATION.md}
```

---

## 1. Propósito

TreeFrogUI es un frontend libretro para handhelds MIPS Hichip. Este fork optimiza el desarrollo para R36SX V2.6 (Stock OS) preservando compatibilidad con el workspace multi-repositorio upstream y sin romper el boot Stock.

## 2. Entorno canónico

- **WSL Ubuntu es canónico.** Toda compilación, scripting, análisis, hashing, generación de patches y operaciones Git debe correr normalmente en WSL Ubuntu.
- Repositorios en Windows se acceden via `/mnt/<drive>/R36SX/treefrog-ui-r36sx` (ej. `D:\R36SX` → `/mnt/d/R36SX`). Drive letter **no es trust anchor** — verificar layout.
- No mover workflows de compilación a PowerShell/Windows nativo salvo requisito Windows-only explícito.
- Scripts son executables y pueden usar `set -euo pipefail`; **no** colocar `exit`/`set -e` a nivel top-level en documentación que pueda matar la shell interactiva del usuario — usar subshells/funciones/condicionales.

## 3. Arquitectura de repositorios

Workspace multi-repositorio (no monolito):

```
~/sf3000-work/
├── treefrog-ui          ← este repo (build scripts, patches, staging, docs)
├── FrogUI               ← tzubertowski/FrogUI@sf3000 (submodule frogui/, 15ea12b)
├── TreeFrogUI_picoarch  ← tzubertowski/TreeFrogUI_picoarch@r36sx (display/audio, picoarch+picoarch_hi)
├── TreeFrogUI_pcsx4all  ← standalone PS1 (opcional)
├── cores/               ← 78 clones via clone_cores.sh (gitignored)
└── sf3000toolchain/     ← game-de-it/sf3000 sf3000_toolchain_v0.1 (mips-mti-linux-gnu-gcc 6.3.0)
```

- `FrogUI` es **submodule separado** — no editar `frogui/` como si fuera monolito. Reglas FrogUI documentadas en `docs/components/FROGUI.md` (parent-owned) y `docs/dev/*`.
- `TreeFrogUI_picoarch` es repositorio hermano separado (branch `r36sx`, no submodule).
- No fabricar commits de integración parent — cada repositorio = commits/PRs separados, linkeados entre sí.

Ver: `.gitmodules`, `build_all.sh`, `build_release.sh`, `clone_cores.sh`, `Makefile.sf3000`, `docs/BUILDING.md`, `docs/dev/UPSTREAM_REPOSITORY_MAP.md`.

## 4. Invariantes

- Preservar arranque Stock. No tocar particiones/bootloader; **no sustituir `icube`/`rkgame`** (SF3500 verifica boot — reemplazar = "sdcard is damaged").
- Mecanismo no destructivo obligatorio: `Stock boot → rkgame → setting.xml <autorun file="/mnt/sdcard/MD/dummy.md" driver=""> → libemu_tfhijack.so → zhijack.sh (generado por device) → picoarch/frogui` salvo decisión explícita en `DECISIONS.md`.
- No incluir blobs propietarios Stock OS, ROMs comerciales, BIOS no redistribuibles en Git/releases sin autorización inequívoca.
- **Compilar != validar.** `BUILD PASS` / `HOST PASS` nunca implica `PHYSICAL PASS`.
- No publicar releases sin `PACKAGING PASS` + `CLEAN-INSTALL PHYSICAL PASS` + `DOWNLOAD-BACK PASS` (`REMOTE_SHA == LOCAL_SHA`). Ver `docs/ai/RELEASE_CONTRACT.md`.

## 5. Source of Truth (orden)

1. Requerimiento explícito del usuario actual
2. `AGENTS.md` (esta constitución) + `docs/ai/MULTIREPO_COORDINATION.md` (protocolo `TREEFROGUI_AGENT_PROTOCOL=1`)
3. Decisiones `ACTIVE` de `DECISIONS.md`
4. Evidencia directa (Git, build, filesystem, release assets, hardware)
5. `docs/PROJECT_STATE.md` — snapshot mutable, potencialmente obsoleto (verificar `git rev-parse HEAD`, `git status`, `git submodule status`)
6. `docs/DEVELOPMENT.md` → `docs/BUILDING.md` → `docs/TESTING.md` → `docs/HARDWARE.md` → `docs/SD_SAFETY.md` → `docs/UPSTREAM.md` → `docs/RELEASING.md`
7. Documentación estructural (`CONTEXT_MAP.md`, `docs/ai/*`, `docs/dev/*`)
8. Histórica

Regla: si `docs/PROJECT_STATE.md` contradice Git, gana Git — reparar snapshot primero.

## 6. Clasificación y gates (resumen)

| Clase | Alcance | Gate mínimo | Detalle |
|-------|---------|-------------|---------|
| A | Context/docs, `AGENTS.md`, `CONTEXT_MAP.md`, `DECISIONS.md`, `docs`, contrato IA | `STATIC PASS` | `python tests/test_agent_context_contract.py` |
| B | Host tooling, scripts WSL, toolchain, audits | `STATIC+HOST PASS` | + `tests/test_release_base_selection.sh`, `bash -n` |
| C | Runtime/UI, `frogui`, picoarch, cores | `STATIC+BUILD+HOST+PHYSICAL` | requiere R36SX real |
| D | Device integration, `hijack/zhijack`, `setting.xml`, drivers | `PACKAGING+PHYSICAL` | staging `release/latest/release` |
| E | Release ZIP, manifest, SHA256 | `PACKAGING+CLEAN-INSTALL PHYSICAL+DOWNLOAD-BACK` | `7z t`, `SHA256SUMS` |

Etiquetas exactas en `docs/ai/VALIDATION.md`: `STATIC/HOST/BUILD/PACKAGING/PHYSICAL/CLEAN-INSTALL/DOWNLOAD-BACK PASS/FAIL`. Prohibido `DONE/VERIFIED` sin gate.

## 7. Reglas epistémicas (anti-alucinación)

Distinguir explícitamente:

- **FACT** — verificable en Git/build/filesystem (`git rev-parse v1.0.15 == 27f3bf3...`)
- **PHYSICAL_EVIDENCE** — observado en hardware R36SX V2.6 real (foto/log fechado, SHA, device)
- **INFERENCE** — deducido de evidencia parcial
- **HYPOTHESIS** — no probado, requiere validación
- **UNCONFIRMED** — no verificable sin red/hardware

Nunca afirmar:

- "source commit oficial" sin `HIGH` confidence pin o reproducción
- `PHYSICAL PASS` sin reporte humano de hardware
- `driver cargado` / `device existe` por solo strings binarios

Usar confianzas `HIGH/MEDIUM/LOW` (ver `docs/DEPENDENCY_LOCK.md`, `docs/UPSTREAM.md`). Nombrar `historical_exactness=NOT_CLAIMED` si no reproducido.

## 8. Startup obligatorio

1. Leer `AGENTS.md` → `docs/PROJECT_STATE.md` → `CONTEXT_MAP.md`
2. `python scripts/agent_preflight.py` (`--allow-dirty` solo inspección)
3. Resolver `REPO_ROOT / BRANCH / HEAD / ORIGIN / UPSTREAM / AHEAD_BEHIND / WORKTREE` desde **Git** (`git rev-parse HEAD`, `git status --short --branch`, `git submodule status`)
4. Clasificar cambio A–E (ver §6)
5. Delegar con privilegio mínimo

`DIRTY_WORKTREE` no explicado → `PREFLIGHT_RESULT=FAIL` — reportar `git status` y pedir autorización.

## 9. Git y seguridad

- No `git reset --hard`, `git clean -fd`, `restore` destructivo, `rm -rf`, `force push`, `mkfs/chkdsk/fsck` sobre SD, `cp` a SD, crear releases/publicar assets sin autorización y sin gates.
- Preservar remotes `origin` (fork) y `upstream` (tzubertowski). Push solo a `origin` salvo autorización explícita.
- No `force push` tras revisión de PR. Commits enfocados, sin cambios no relacionados. Repos separados = commits/PRs separados, linkeados.
- `git commit`/`push`/`tag`/`gh release` = `ask`. Agentes read-only nunca delegan a `implement`.
- Preflight y agentes read-only nunca modifican Git/SD/filesystem.

## 10. Validación física y SD

- **Host/Build pueden automatizarse; físico requiere humano.** Agentes solo reportan `STATIC/HOST/BUILD PASS`; nunca `PHYSICAL PASS` / `CLEAN-INSTALL PASS` sin observación humana (`docs/TESTING.md`, `docs/HARDWARE.md`).
- Todo cambio `hijack`/`zhijack`/`driver` requiere `PACKAGING PASS` + boot físico documentado (`FIRMWARE/BASELINE`, `ARTIFACT_SHA256`, `TEST_MATRIX`, `USER_OBSERVATIONS`, `PASS/FAIL`, `DATE`).
- SD: ver `docs/SD_SAFETY.md` — identificar por layout no por letra, backup+SHA256 antes de overwrite, solo ficheros autorizados, readback+hash tras write, rollback preservado, nunca formato/fsck automático, eject seguro es acción humana. Windows `G:\cubegm` → WSL `/mnt/g/cubegm` (drive no es anchor).

## 11. Kernel / rootfs / DTB

Cambios requieren **autorización explícita + evidencia**:

`rmmod`/`insmod`/`kernel`/`DTB`/`rootfs`/`vendor driver`/`sysfs` hardware writes. No tocar particiones. Stock blobs solo si autorización/licencia inequívoca.

## 12. Ficheros generados

No commitear: `build/`, `.toolchain/`, `cores/`, `release/` (artifact/latest), `*.o`/`*.lo`, `*.so` compilados, backups SD, `log.txt`/`update.log`, ROMs/BIOS, saves/screenshots, dumps diagnóstico, `venv/`, toolchain. Ver `.gitignore` y `docs/DEVELOPMENT.md`. Parches sí se versionan; fixtures de test sí.

Line endings: `*.sh`/`*.py`/`*.c`/`*.h`/`*.md` = `LF` (ver `.gitattributes`). No renormalizar repo entero sin autorización — `REPOSITORY_WIDE_RENORMALIZATION=NO`.

## 13. Agentes y privilegio mínimo

- `treefrog-lead` (primary): clasifica, delega solo a `audit|implement|review|release|upstream-sync`, no edita runtime directo salvo CLASS A menor.
- `audit` (read-only): `edit: deny`, `task: deny`, `external_directory: deny`. Solo Git/filesystem diagnóstico.
- `review` (read-only): `edit: deny`, `task: deny`. Revisa diff sin auto-corregir.
- `implement` (scoped edit): requiere preflight+clase, `task: audit/review:allow` resto `deny`, `git commit/push` = `ask`, niega `reset --hard`/`clean`/`rm -rf`/`force push`.
- `release`: `ask` edit, verifica manifest/SHA/download-back, nunca delega a `implement`.
- `upstream-sync` (read-only): `git fetch upstream`, compara `upstream/main..HEAD`, lista tags, recomienda `merge/rebase/cherry-pick` sin integrar.

## 14. Flujo de trabajo (resumen)

`READ → VERIFY BASELINE → AUDIT → PLAN MIN → BUILD → STATIC/HOST TEST → PREPARE ARTIFACT → STOP for HUMAN PHYSICAL → RECORD → COMMIT(ask) → PUSH(ask) → PR upstream` — detalle en `docs/DEVELOPMENT.md`.

## 15. Regla permanente

> La evidencia manda sobre el plan. Si nueva evidencia contradice docs, reparar contexto PRIMERO y continuar solo desde checkpoint válido. `STATIC+HOST` nunca equivale a `PHYSICAL`. Mantener docs precisos es ingeniería.
