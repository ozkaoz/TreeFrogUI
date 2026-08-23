# AGENTS.md — Constitución Permanente — TreeFrogUI R36SX V2.6 Fork

**Repo:** https://github.com/ozkaoz/treefrog-ui-r36sx
**Upstream:** https://github.com/tzubertowski/treefrog-ui
**Target:** R36SX V2.6 — Stock OS — TreeFrogUI
**Baseline:** v1.0.15 (SHA resuelto desde Git, no hardcodeado aquí como autoridad mutable)
**Versión:** 1.0 — 2026-08-23

> Constitución permanente. Provider-neutral. No es historial ni snapshot.
> Valores mutables (HEAD, branch, SHA, estado worktree) viven en `CURRENT.md` o en Git — nunca aquí como fuente primaria.

```
AGENTS.md (constitución) → CURRENT.md (snapshot verificable, potencialmente obsoleto)
                         → CONTEXT_MAP.md (router de contexto)
                         → DECISIONS.md (decisiones duraderas)
                         → docs/ai/{VALIDATION.md, RELEASE_CONTRACT.md}
```

---

## 1. Target Inicial

```
TARGET_DEVICE = R36SX V2.6
BASE_OS       = Stock OS
UPSTREAM      = tzubertowski/treefrog-ui
BASELINE      = v1.0.15, SHA resuelto desde Git (ver CURRENT.md y `git rev-parse v1.0.15`)
```

No hardcodear HEAD actual como permanente. HEAD, branch y SHA exactos se resuelven siempre con `git`.

---

## 2. Invariantes

- Preservar el arranque Stock. No tocar particiones ni bootloader.
- No sustituir `icube`.
- No sustituir `rkgame`.
- El fork debe continuar usando un mecanismo no destructivo de autorun/hijack (Stock boot → `rkgame` → `setting.xml` `<autorun>` → `libemu_tfhijack.so` → `zhijack.sh` → `picoarch/frogui`) salvo decisión técnica explícita sustentada por evidencia y registrada en `DECISIONS.md`.
- No incluir archivos propietarios del Stock OS en Git o releases salvo que exista autorización/licencia inequívoca.
- No incluir ROMs comerciales.
- No incluir BIOS no redistribuibles.
- No inferir compatibilidad física. Una compilación exitosa no valida hardware.
- Compilar != validar en R36SX.
- HOST PASS != PHYSICAL PASS.
- Un árbol de desarrollo funcional no implica que un ZIP de release sea completo.
- No publicar releases sin `PACKAGING PASS` + `CLEAN-INSTALL PHYSICAL PASS` + verificación de identidad SHA descargada.

---

## 3. Source-of-Truth (orden)

1. Requerimiento actual explícito del usuario.
2. `AGENTS.md` (esta constitución).
3. Decisiones `ACTIVE` de `DECISIONS.md`.
4. Evidencia directa (Git, build, filesystem, release assets, hardware).
5. `CURRENT.md` — snapshot verificable, potencialmente obsoleto.
6. Documentación estructural (`CONTEXT_MAP.md`, `docs/ai/*`).
7. Documentación histórica.

Regla: `CURRENT.md IS A CACHE`. Si CURRENT contradice evidencia directa, gana la evidencia directa — reparar CURRENT primero.

---

## 4. Golden-State Model

- **SOURCE BASELINE / SOURCE GOLDEN:** `v1.0.15` + SHA real resuelto (`27f3bf33e906d90e0cd267059bf0559afc6f8a05` al momento del bootstrap; confirmar siempre con `git rev-parse v1.0.15`). Es el árbol que compila y del que parte `r36sx-v2.6-dev`.
- **PHYSICAL GOLDEN:** payload exacto instalado en R36SX y validado físicamente. Al finalizar este bootstrap: `NONE / NOT YET ESTABLISHED`.
- **RELEASE GOLDEN:** artefacto publicado, instalado en limpio, validado físicamente y verificado por descarga (`REMOTE_SHA == LOCAL_SHA`). Al finalizar este bootstrap: `NONE / NOT YET ESTABLISHED`.

Nunca inventar `PHYSICAL PASS` ni `RELEASE GOLDEN`.

```
SOURCE_BASELINE = v1.0.15 + SHA real
PHYSICAL_GOLDEN = NONE / NOT YET ESTABLISHED
RELEASE_GOLDEN  = NONE / NOT YET ESTABLISHED
```

---

## 5. Clasificación de Cambios y Gates

### CLASS A — Context / Documentation
Ejemplos: `AGENTS.md`, `CURRENT.md`, `CONTEXT_MAP.md`, `DECISIONS.md`, `.opencode/agents`, `docs`, tests de contrato IA.

Gate: `STATIC PASS`.

### CLASS B — Host tooling / Build infrastructure
Ejemplos: scripts de desarrollo, scripts WSL, toolchain setup, auditorías, empaquetado host-only, CI, reproducibilidad de builds.

Gate: `STATIC PASS + HOST PASS`.

### CLASS C — Runtime / UI
Ejemplos: `frogui`, picoarch integration, frontend, rendering, input, audio runtime, aplicaciones integradas, cores, comportamiento visible durante ejecución.

Gate mínimo: `STATIC + BUILD + HOST TESTS + PHYSICAL R36SX`.

### CLASS D — Device integration / Deployment
Ejemplos: `hijack`, `zhijack`, `autorun`, `setting.xml`, device driver selection, `install_first/r36sx`, SD layout, boot behavior.

Gate: `PACKAGING PASS + PHYSICAL R36SX`.

### CLASS E — Release
Ejemplos: ZIP público, manifests, SHA256, release notes, install contract.

Gate: deterministic package + `CLEAN-INSTALL PHYSICAL PASS` + downloaded asset identity verification (`DOWNLOAD-BACK PASS`).

Etiquetas exactas (ver `docs/ai/VALIDATION.md`): `STATIC PASS / FAIL`, `HOST PASS / FAIL`, `BUILD PASS / FAIL`, `PACKAGING PASS / FAIL`, `PHYSICAL PASS / FAIL`, `CLEAN-INSTALL PHYSICAL PASS / FAIL`, `DOWNLOAD-BACK PASS / FAIL`. Prohibido usar `DONE / VERIFIED / VALIDATED` sin gate específico.

---

## 6. Protocolo de Inicio (Startup)

Toda sesión DEBE:

1. Leer `AGENTS.md` → `CURRENT.md` → `CONTEXT_MAP.md`.
2. Ejecutar preflight: `python scripts/agent_preflight.py` (o `python tests/test_agent_context_contract.py`).
3. Resolver `REPO_ROOT`, `ACTIVE_BRANCH`, `HEAD`, `UPSTREAM`, `AHEAD_BEHIND`, `WORKTREE_STATE` desde **Git directamente** — nunca confiar en docs hardcodeados.
4. Clasificar el cambio (Clase A–E) antes de editar.
5. Delegar según clase y privilegio mínimo.

Si existe `DIRTY_WORKTREE` no explicado: `PREFLIGHT_RESULT=FAIL` — reportar `git status --short --branch` y pedir autorización.

---

## 7. Seguridad y Operaciones Prohibidas

Permanentemente prohibido sin autorización explícita y evidencia:

- `git reset --hard`, `git clean -fd`, `git restore` destructivo, `git checkout -- <file>`, `rm -rf`, borrado recursivo del repo, formatear unidades, `chkdsk`/`fsck`, escribir sobre SD, copiar a R36SX, crear releases, publicar assets, `force push`.

El preflight y los agentes read-only nunca modifican Git, nunca tocan SD, nunca reparan filesystem.

Dirty worktree no explicado → `PREFLIGHT_RESULT=FAIL / PREFLIGHT_REASON=DIRTY_WORKTREE` (solo `--allow-dirty` para inspección).

---

## 8. Separación de Evidencia

- **Estática:** lectura de repo, diff, logs Git.
- **Build:** compilación cruzada (requiere toolchain, WSL).
- **Host:** tests en host, empaquetado sin hardware.
- **Hardware:** pruebas físicas en R36SX V2.6 real (nunca inferidas).
- **Release:** identidad de artefacto publicado y descargado.

Ningún gate superior puede inferirse de uno inferior.

---

## 9. Agentes y Privilegio Mínimo

- `treefrog-lead` (primary, orquestador): lee constitución, ejecuta preflight, clasifica, delega. No modifica código productivo directamente salvo CLASS A menor. Solo delega a `audit`, `implement`, `review`, `release`, `upstream-sync`.
- `audit` (read-only): `edit: deny`, `task: deny`, `external_directory: deny`. Solo lectura y Git diagnóstico. Nunca puede delegar a `implement`.
- `review` (read-only independiente): `edit: deny`, `task: deny`. Revisa diff y pruebas sin corregir sus propios hallazgos.
- `implement` (edición scopada): requiere preflight, clase conocida, nunca infiere `PHYSICAL PASS`. Solo puede delegar a `audit`/`review`. Debe negar `git reset --hard`, `git clean`, `rm -rf`, `force push`, `filesystem repair`. `git commit`/`git push`/publicación requieren `ask`.
- `release` (no implement): puede usar `audit`/`review`, nunca llamar a `implement`. `tag`/`push`/`publish` = `ask`. Nunca publica sin `PACKAGING PASS` + `CLEAN-INSTALL PHYSICAL PASS` + SHA identity.
- `upstream-sync` (read-only por ahora): `git fetch upstream`, comparar, listar tags, analizar divergencia, recomendar `merge`/`rebase`/`cherry-pick`. No integra automáticamente. Nunca `force push`.

Provider-neutral: `AGENTS.md` es canónico. Si existen `CLAUDE.md`/`GEMINI.md` deben ser routers mínimos que apunten aquí — nunca duplicar política completa.

---

## 10. Mantenimiento de Contexto

- `CURRENT.md` = snapshot operativo conciso (no changelog), incluye fecha, repo local, origin/upstream, branch, HEAD, baseline, submodule, estado worktree, objetivo, último preflight, Golden states, riesgos, siguiente acción. Debe dejar claro `CURRENT.md IS A CACHE`.
- `CONTEXT_MAP.md` = router estable (qué leer para FrogUI/picoarch/input/audio/cores/hijack/R36SX/release/...). No almacenar HEAD mutable como autoridad.
- `DECISIONS.md` = solo decisiones duraderas con formato `ID/Date/Status/Scope/Context/Decision/Reason/Consequences/Evidence/Related files`.
- Mantener DRY: no duplicar invariantes — referenciar `AGENTS.md`.

---

## 11. Contrato de Release (resumen, detalle en `docs/ai/RELEASE_CONTRACT.md`)

Objetivo futuro:

```
R36SX V2.6 Stock OS + contenido de UN único ZIP del fork copiado a la raíz de la SD = TreeFrogUI funcional
POST_INSTALL_MANUAL_FIXES=0
```

El ZIP R36SX del fork debería generarse combinando el payload universal con `install_first/r36sx` para que el usuario no haga dos overlays. Durante bootstrap solo se documenta el contrato — no se implementa el nuevo empaquetado.

Reglas: no empaquetar `icube`/`rkgame`, no depender de ficheros residuales, FAT32 compatible, sin symlinks, manifest, SHA256, sin estado runtime temporal, sin ROMs/BIOS no redistribuibles, clean install física obligatoria antes de estable.

---

## 12. Condiciones de Parada

Parar y pedir intervención humana cuando: regresión, dependencia inesperada, evidencia contradice hipótesis, scope creep, evidencia insuficiente, checkpoint necesita humano, o se requiere validación física sin hardware disponible. No auto-continuar encadenando fix B tras fix A sin re-validar.

---

## 13. Handoff Compacto

```
CHANGE_CLASS=  FILES_CHANGED=  HEAD=  CHECKS_RUN=  PHYSICAL_EVIDENCE=  RELEASE_EVIDENCE=  BLOCKER=  NEXT_EXACT_ACTION=  STOP_CONDITION=
```

Logs crudos van a ficheros de evidencia dedicados, no a `CURRENT.md`. Handoff debe ser reproducible solo con Git + evidencias.

---

## 14. Regla Permanente

> La evidencia tiene prioridad sobre el plan. Si nueva evidencia contradice contexto escrito, actualizar contexto PRIMERO, ajustar hipótesis, y continuar solo desde el siguiente checkpoint válido. Compilar no es validar. `STATIC PASS + HOST PASS` nunca equivale a `PHYSICAL PASS`. Mantener los ficheros de contexto precisos es trabajo de ingeniería.
