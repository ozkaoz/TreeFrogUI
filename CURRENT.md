# CURRENT.md — Compat Stub — TreeFrogUI R36SX V2.6 Fork

> **CURRENT.md IS A CACHE.** Snapshot verificado obsoleto.
> **Canonical mutable state:** `docs/PROJECT_STATE.md` — verificar con `git rev-parse HEAD`, `git status --short --branch`, `git submodule status`, `git remote -v`.

Este fichero se mantiene solo para compatibilidad con tooling que aún referencia `CURRENT.md` (ver `opencode.json` previo). No duplicar estado aquí — toda referencia nueva debe usar `docs/PROJECT_STATE.md`.

- **Snapshot anterior:** `v1.0.15 → 27f3bf33e906d90e0cd267059bf0559afc6f8a05` (tag), `r36sx-v2.6-dev HEAD 76a6dca` al 2026-08-24 — ver `docs/PROJECT_STATE.md` para `LAST_VERIFIED_UTC`, `CURRENT_HEAD`, `FROGUI 15ea12b`, `DEPENDENCY_LOCK`.
- **Golden:** `SOURCE_BASELINE = v1.0.15 + 27f3bf3` — `PHYSICAL_GOLDEN = NONE / NOT YET ESTABLISHED` — `RELEASE_GOLDEN = NONE / NOT YET ESTABLISHED` (snapshot verifiable, cache)
- **PHYSICAL_GOLDEN = NONE / NOT YET ESTABLISHED** — no hay `PHYSICAL PASS` inventado; requiere hardware R36SX V2.6 real fechado (`docs/TESTING.md`, `docs/ai/VALIDATION.md`).
- **Instrucciones canónicas:** `AGENTS.md` → `docs/PROJECT_STATE.md` → `CONTEXT_MAP.md` → `docs/DEVELOPMENT.md` → `docs/BUILDING.md` → resto en `docs/README.md`.

```
AGENTS.md (constitución) → docs/PROJECT_STATE.md (snapshot mutable)
                         → CONTEXT_MAP.md (router)
                         → DECISIONS.md (duraderas)
```

Para migrar: actualizar `opencode.json` instructions a `["AGENTS.md", "docs/PROJECT_STATE.md", "CONTEXT_MAP.md"]` (ya hecho en esta fase).
