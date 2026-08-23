# DECISIONS.md — Decisiones Técnicas Duraderas — TreeFrogUI R36SX V2.6 Fork

> Solo decisiones duraderas. No es changelog ni bitácora de commits. Formato mínimo: ID / Date / Status / Scope / Context / Decision / Reason / Consequences / Evidence / Related files.

---

## D001 — Baseline estable v1.0.15 para el fork R36SX V2.6

- **ID:** D001
- **Date:** 2026-08-23
- **Status:** ACTIVE
- **Scope:** TreeFrogUI R36SX V2.6 fork — baseline de desarrollo y branching

- **Context:**
  Upstream `tzubertowski/treefrog-ui` tiene `main` en `v1.1.0_b` (2026-08-23) con cambios recientes de docs/instalador/CI. Para el fork R36SX V2.6 se necesita una base estable, etiquetada y reproducible sobre la que auditar Stock OS → `rkgame` → `autorun` → `hijack` y la geometría/drivers R36SX antes de introducir cambios propios. El historial reciente incluye múltiples líneas `v1.0.15`, `v1.1.0_a/b`.

- **Decision:**
  Usar **`v1.0.15` (`27f3bf33e906d90e0cd267059bf0559afc6f8a05`, `Clarify R36HD backup entry`) como `SOURCE_BASELINE` inicial. Crear rama local `r36sx-v2.6-dev` exactamente desde ese tag. Mantener `upstream/main` como rama de sincronización futura, sin merge automático en el bootstrap.

- **Reason:**
  `v1.0.15` es el último tag estable de la línea `v1.0.*` antes de `v1.1.0` unstable; está documentado en `release-notes.md` y verificado con `git rev-parse v1.0.15` / `git tag --list`. Aislar el desarrollo R36SX de cambios inestables de `v1.1.0` reduce riesgo y permite auditar `build_release.sh`, `hijack/`, `frogui` submodule (`15ea12b`) y `install_first/r36sx` en estado conocido.

- **Consequences:**
  - `r36sx-v2.6-dev` diverge de `upstream/main` (`41f15e2` al bootstrap); requiere `git fetch upstream --tags` periódico y agente `upstream-sync` para evaluar `merge`/`rebase`/`cherry-pick`.
  - Releases futuros del fork deberán declarar si siguen en `v1.0.15+` o si hacen forward-port a `v1.1.0` y documentarlo como nueva decisión.
  - No se modifica `.gitmodules` ni `frogui` pin en esta decisión.

- **Evidence:**
  - `git rev-parse v1.0.15` → `27f3bf33e906d90e0cd267059bf0559afc6f8a05`
  - `git show --oneline --no-patch v1.0.15` → `27f3bf3 Clarify R36HD backup entry`
  - `git tag --list | grep v1.0.15`
  - `git submodule status` → `15ea12bb4f6f642b1ec02aabebbad33e5e95ed2b frogui (v0.1.3-123-g15ea12b)`
  - `git remote -v` → `origin=ozkaoz/treefrog-ui-r36sx`, `upstream=tzubertowski/treefrog-ui`
  - `git log -5 --oneline --decorate` en `r36sx-v2.6-dev`

- **Related files:**
  `AGENTS.md §1/§4`, `CURRENT.md`, `CONTEXT_MAP.md`, `.gitmodules`, `frogui/`, `build_release.sh`, `hijack/zhijack.tpl.sh`, `install.md`, `docs/RELEASING.md`

---

<!-- Plantilla para futuras decisiones:

## D00X — Título
- **ID:** D00X
- **Date:** YYYY-MM-DD
- **Status:** ACTIVE | SUPERSEDED | DEPRECATED
- **Scope:** ...
- **Context:** ...
- **Decision:** ...
- **Reason:** ...
- **Consequences:** ...
- **Evidence:** ...
- **Related files:** ...

-->
