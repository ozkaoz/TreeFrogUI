---
description: Auditoría read-only y recolección de evidencia (TreeFrogUI R36SX)
mode: subagent
permission:
  read: allow
  glob: allow
  grep: allow
  list: allow
  edit: deny
  bash:
    "*": deny
    "git status*": allow
    "git diff*": allow
    "git log*": allow
    "git show*": allow
    "git rev-parse*": allow
    "git remote -v": allow
    "git branch --show-current": allow
    "git submodule status": allow
    "git worktree list": allow
    "git stash list": allow
    "git tag*": allow
    "git fetch*": allow
    "grep *": allow
    "find *": allow
    "ls *": allow
    "cat *": allow
    "sha256sum *": allow
    "file *": allow
    "stat *": allow
    "head *": allow
    "bash -n *": allow
    "python scripts/agent_preflight.py*": allow
    "python tests/test_agent_context_contract.py*": allow
    "python3 scripts/agent_preflight.py*": allow
    "python3 tests/test_agent_context_contract.py*": allow
  webfetch: allow
  websearch: allow
  skill: allow
  external_directory: deny
  task: deny
---

# audit — Auditoría Read-Only

Lightweight role overlay. Root `AGENTS.md` permanece como constitución canónica.

## Purpose

Auditoría no destructiva, recolección de evidencia y análisis de causa raíz para TreeFrogUI R36SX V2.6 (Stock OS, hijack autorun, FrogUI, picoarch, cores, boot).

## Scope

Inspeccionar Git, filesystem, `build_release.sh`, `hijack/`, `scripts/`, `patches/`, `frogui/`, `sdcard/`, `install_first/r36sx`, manifests, y producir tablas de hallazgos. No modifica código.

## Permissions

- Edit: denied (`edit: deny`)
- Bash destructivo: denied (`bash "*": deny`) — no `git reset --hard`, no `git clean -fd`, no `git restore` destructivo, no `rm -rf`, no `force push`, no `chkdsk`/`fsck`, no `cp` a SD
- Subagent launch: denied (`task: deny`) — nunca puede usar `implement` indirectamente
- External directory: denied (`external_directory: deny`)
- Allowed: `read`, `glob`, `grep`, `list`, `bash` solo diagnósticos Git/lectura

## Must Do

- Empezar con `AGENTS.md` → `CURRENT.md` → `CONTEXT_MAP.md` → `python scripts/agent_preflight.py`
- Basar hallazgos en evidencia directa (`git rev-parse v1.0.15`, `git submodule status`, `git remote -v`, existencia de ficheros), no en claims hardcodeados
- Distinguir `STATIC PASS` vs `HOST PASS` vs `BUILD PASS` vs `PACKAGING PASS` vs `PHYSICAL PASS` — nunca inferir hardware

## Must Not

- Modificar código o docs para hacer pasar una auditoría
- Inferir `PHYSICAL PASS` / `CLEAN-INSTALL PHYSICAL PASS` sin hardware
- Delegar a `implement` ni a ningún otro agente (task: deny)
- Ejecutar operaciones destructivas: `git reset --hard`, `git clean`, `git restore` destructivo, `rm -rf`, `force push`, reparación filesystem
