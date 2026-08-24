# CONTRIBUTING.md — TreeFrogUI R36SX V2.6 Fork

Gracias por contribuir. Este fork es R36SX V2.6 Stock OS first, preservando compatibilidad multi-repo upstream.

## TL;DR

- **Lee:** `AGENTS.md` → `docs/PROJECT_STATE.md` (verifica con `git`) → `CONTEXT_MAP.md`
- **Dev docs:** `docs/DEVELOPMENT.md`, `docs/BUILDING.md`, `docs/TESTING.md`, `docs/HARDWARE.md`, `docs/SD_SAFETY.md`, `docs/UPSTREAM.md`
- **Build:** `docs/BUILDING.md` (WSL Ubuntu, `~/sf3000-work`, toolchain `game-de-it/sf3000`)
- **No improvises hardware:** `BUILD PASS != PHYSICAL PASS`

## Desarrollo

1. **Verifica baseline:** `git rev-parse HEAD`, `git rev-parse v1.0.15`, `git submodule status`, `git remote -v`, `python scripts/agent_preflight.py`
2. **Clasifica cambio:** `CLASS A` docs, `B` tooling, `C` runtime, `D` device/hijack, `E` release (`docs/ai/VALIDATION.md`)
3. **Plan mínimo** — cambia lo justo.
4. **Build + host tests** en WSL (`./build_all.sh`, `python tests/test_agent_context_contract.py`)
5. **Para runtime/device:** prepara artefacto `release/latest/release` — **STOP** y pide test humano en R36SX V2.6 real (no auto-claim `PHYSICAL PASS`)
6. **Commit/push solo con `ask`** — humano autoriza. Commits enfocados, sin `rm -rf`/`reset --hard`/`force push`.

Detallado: `docs/DEVELOPMENT.md` (READ → VERIFY → AUDIT → PLAN → IMPLEMENT → BUILD → HOST TEST → STOP HUMAN → RECORD → COMMIT → PUSH → PR).

## Workspace multi-repositorio

```
~/sf3000-work/treefrog-ui + FrogUI (submodule frogui/ 15ea12b) + TreeFrogUI_picoarch@r36sx + cores/ + toolchain
```

- No editar `frogui/` como monolito — ver `docs/components/FROGUI.md`. PRs FrogUI Picoarch van a sus repos separados, linkeados.
- No mover workflows a PowerShell/Windows nativo.

## Build y tests

- **Build:** `docs/BUILDING.md` — `~/sf3000-work`, `mips-mti-linux-gnu-gcc 6.3.0`, `cmake` opcional (TIC-80)
- **Tests:** `docs/TESTING.md` — `STATIC` (`test_agent_context_contract.py`, `agent_preflight.py`), `HOST` (`test_release_base_selection.sh`, `dev-doctor.sh`), `BUILD`/`PACKAGING`/`PHYSICAL` gates
- **SD safety:** `docs/SD_SAFETY.md` — layout no drive letter, backup+SHA, solo ficheros autorizados, nunca auto-format/fsck, eject humano

## Upstream y PRs

```
upstream tzubertowski/treefrog-ui → fork ozkaoz/treefrog-ui-r36sx → feature branch → validation → commit → push origin → PR
```

- Preserva `upstream` remote, push solo a `origin`.
- No `force push` tras review.
- Documenta baseline (`docs/PROJECT_STATE.md` `v1.0.15 27f3bf3`).
- Linkea PRs de componentes (`FrogUI`, `picoarch`) si aplica. Ver `docs/UPSTREAM.md`.
- Confianza provenance: `HIGH` (pin) / `MEDIUM` (branch+cutoff) / `LOW` (default HEAD) / `UNCONFIRMED`.

## Qué no commitear

`build/`, `.toolchain/`, `cores/`, `release/` (artifact/latest), `*.o`/`*.so` compilados, `log.txt`/`update.log`, ROMs/BIOS, saves/screenshots, dumps, `venv/`. Ver `.gitignore`. `patches/` y fixtures sí.

Line endings `LF` (ver `.gitattributes`). No renormalizar repo entero — `REPOSITORY_WIDE_RENORMALIZATION=NO`.

## AI / agentes

AI usa `AGENTS.md` (constitución) + `docs/PROJECT_STATE.md` + `CONTEXT_MAP.md` (`opencode.json`). Regla epistémica: distinguir `FACT` / `PHYSICAL_EVIDENCE` / `INFERENCE` / `HYPOTHESIS` / `UNCONFIRMED` (nunca claim `PHYSICAL PASS` sin humano).

## Preguntas

Abre issue con `AGENTS.md` + evidencia `git status`/`log`/`submodule status`/`preflight`.
