#!/usr/bin/env python3
"""
agent_preflight.py — Preflight cross-platform (Windows/Linux) para TreeFrogUI R36SX V2.6 Fork
No destructivo: no modifica Git, no toca SD, no repara filesystem.
Uso:
  python scripts/agent_preflight.py           # FAIL si dirty worktree no explicado
  python scripts/agent_preflight.py --allow-dirty  # inspección, permite dirty
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path

def run(cmd, cwd=None):
    try:
        r = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=False)
        return r.stdout.strip(), r.stderr.strip(), r.returncode
    except Exception as e:
        return "", str(e), 1

def run_shell(cmd, cwd=None):
    try:
        r = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
        return r.stdout.strip(), r.stderr.strip(), r.returncode
    except Exception as e:
        return "", str(e), 1

def main():
    parser = argparse.ArgumentParser(description="TreeFrogUI R36SX preflight")
    parser.add_argument("--allow-dirty", action="store_true", help="Permite worktree dirty solo para inspección")
    parser.add_argument("--repo", type=str, default=None, help="Ruta repo (default: auto-detect)")
    args = parser.parse_args()

    # Resolver repo root
    cwd = Path(args.repo) if args.repo else Path.cwd()
    # Intenta encontrar root via git rev-parse
    out, err, rc = run(["git", "rev-parse", "--show-toplevel"], cwd=str(cwd))
    if rc != 0 or not out:
        # fallback: intentar desde script location
        script_dir = Path(__file__).resolve().parents[1]
        out2, _, rc2 = run(["git", "rev-parse", "--show-toplevel"], cwd=str(script_dir))
        if rc2 == 0 and out2:
            repo_root = Path(out2)
        else:
            print("PREFLIGHT_RESULT=FAIL")
            print("PREFLIGHT_REASON=NOT_A_GIT_REPO")
            print(f"cwd={cwd}")
            print(f"err={err}")
            return 1
    else:
        repo_root = Path(out)

    print(f"REPO_ROOT={repo_root}")

    # Branch, HEAD
    branch, _, _ = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=str(repo_root))
    head, _, _ = run(["git", "rev-parse", "HEAD"], cwd=str(repo_root))
    head_short, _, _ = run(["git", "rev-parse", "--short", "HEAD"], cwd=str(repo_root))
    print(f"BRANCH={branch}")
    print(f"HEAD={head} ({head_short})")
    # Remotes
    origin, _, rc_o = run(["git", "remote", "get-url", "origin"], cwd=str(repo_root))
    upstream, _, rc_u = run(["git", "remote", "get-url", "upstream"], cwd=str(repo_root))
    print(f"ORIGIN={'(missing)' if rc_o!=0 else origin}")
    print(f"UPSTREAM={'(missing)' if rc_u!=0 else upstream}")
    # Verify expected
    if rc_o != 0:
        print("WARN: origin missing (esperado: https://github.com/ozkaoz/treefrog-ui-r36sx.git)")
    if rc_u != 0:
        print("WARN: upstream missing (esperado: https://github.com/tzubertowski/treefrog-ui.git)")

    # Fetch info ahead/behind (no fetch, solo local)
    # Intenta comparar con origin/branch y upstream/main si existen
    ahead_behind = "UNKNOWN"
    try:
        # Determinar tracking branch
        sb_out, _, _ = run(["git", "status", "--short", "--branch"], cwd=str(repo_root))
        print(f"STATUS_BRANCH={sb_out.splitlines()[0] if sb_out else ''}")
        # ahead/behind vs origin/main y upstream/main
        for remote_branch in ["origin/main", "upstream/main", f"origin/{branch}"]:
            _, _, rc_rb = run(["git", "rev-parse", "--verify", remote_branch], cwd=str(repo_root))
            if rc_rb == 0:
                ab_out, _, rc_ab = run(["git", "rev-list", "--left-right", "--count", f"HEAD...{remote_branch}"], cwd=str(repo_root))
                if rc_ab == 0:
                    ahead, behind = ab_out.split()
                    print(f"AHEAD_BEHIND vs {remote_branch}: ahead={ahead} behind={behind} ({ab_out})")
                else:
                    print(f"AHEAD_BEHIND vs {remote_branch}: error")
    except Exception as e:
        print(f"AHEAD_BEHIND error: {e}")

    # Worktree status
    status_porcelain, _, _ = run(["git", "status", "--porcelain"], cwd=str(repo_root))
    status_short_branch, _, _ = run(["git", "status", "--short", "--branch"], cwd=str(repo_root))
    print("--- git status --short --branch ---")
    print(status_short_branch if status_short_branch else "(clean)")
    untracked = [l for l in status_porcelain.splitlines() if l.startswith("??")]
    modified = [l for l in status_porcelain.splitlines() if not l.startswith("??") and l.strip() != ""]
    print(f"MODIFIED_COUNT={len(modified)}")
    print(f"UNTRACKED_COUNT={len(untracked)}")
    if untracked:
        print("UNTRACKED:")
        for u in untracked[:20]:
            print(f"  {u}")
        if len(untracked) > 20:
            print(f"  ... +{len(untracked)-20} more")
    if modified:
        print("MODIFIED:")
        for m in modified[:20]:
            print(f"  {m}")

    dirty = bool(status_porcelain.strip())
    print(f"DIRTY={'YES' if dirty else 'NO'}")

    # Worktrees y stash
    wt_out, _, _ = run(["git", "worktree", "list"], cwd=str(repo_root))
    print("--- git worktree list ---")
    print(wt_out if wt_out else "(none)")

    stash_out, _, _ = run(["git", "stash", "list"], cwd=str(repo_root))
    print("--- git stash list ---")
    print(stash_out if stash_out else "(empty)")

    # Submodules
    sub_out, sub_err, rc_sub = run(["git", "submodule", "status"], cwd=str(repo_root))
    print("--- git submodule status ---")
    if rc_sub == 0:
        print(sub_out if sub_out else "(no submodules or not init)")
        # check for uninitialized: line starting with '-'
        uninit = [l for l in sub_out.splitlines() if l.startswith("-")]
        if uninit:
            print(f"SUBMODULE_UNINITIALIZED={len(uninit)}")
        # check for modified: '+' or 'U'
        mod_sub = [l for l in sub_out.splitlines() if l.startswith("+") or l.startswith("U")]
        if mod_sub:
            print(f"SUBMODULE_MODIFIED={len(mod_sub)}")
            for m in mod_sub:
                print(f"  {m}")
    else:
        print(f"submodule status failed: {sub_err}")

    # Archivos de contexto
    print("--- context files ---")
    required = [
        "AGENTS.md",
        "CURRENT.md",
        "CONTEXT_MAP.md",
        "DECISIONS.md",
        "docs/ai/VALIDATION.md",
        "docs/ai/RELEASE_CONTRACT.md",
    ]
    missing = []
    for rel in required:
        p = repo_root / rel
        exists = p.exists()
        print(f"{rel}: {'OK' if exists else 'MISSING'}")
        if not exists:
            missing.append(rel)

    # Agentes
    print("--- agents ---")
    agents_dir = repo_root / ".opencode" / "agents"
    if agents_dir.exists():
        agents = list(agents_dir.glob("*.md"))
        print(f"AGENTS_DIR={agents_dir} count={len(agents)}")
        for a in agents:
            print(f"  {a.name}")
        expected_agents = ["treefrog-lead.md", "audit.md", "implement.md", "review.md", "release.md", "upstream-sync.md"]
        for exp in expected_agents:
            if not (agents_dir / exp).exists():
                print(f"AGENT_MISSING={exp}")
                missing.append(f".opencode/agents/{exp}")
    else:
        print(f"AGENTS_DIR MISSING: {agents_dir}")
        missing.extend([".opencode/agents/treefrog-lead.md", ".opencode/agents/audit.md", ".opencode/agents/implement.md", ".opencode/agents/review.md", ".opencode/agents/release.md", ".opencode/agents/upstream-sync.md"])

    # Contrato agentes básico (read-only deny)
    # No falla preflight por contrato, pero advierte
    print("--- agent contract quick check ---")
    for agent_name in ["audit.md", "review.md"]:
        p = agents_dir / agent_name
        if p.exists():
            txt = p.read_text(encoding="utf-8", errors="ignore")
            has_edit_deny = "edit: deny" in txt or "edit:deny" in txt
            has_task_deny = "task: deny" in txt or "task:deny" in txt
            print(f"{agent_name} edit:deny={has_edit_deny} task:deny={has_task_deny} {'OK' if has_edit_deny and has_task_deny else 'WARN'}")

    # Resultado final
    print("--- PREFLIGHT SUMMARY ---")
    if missing:
        print("PREFLIGHT_RESULT=FAIL")
        print(f"PREFLIGHT_REASON=MISSING_FILES: {', '.join(missing)}")
        return 1

    if dirty and not args.allow_dirty:
        print("PREFLIGHT_RESULT=FAIL")
        print("PREFLIGHT_REASON=DIRTY_WORKTREE")
        print("HINT: commit/stash or run with --allow-dirty for inspection only")
        return 1

    if dirty and args.allow_dirty:
        print("PREFLIGHT_RESULT=PASS (allow-dirty)")
        print("PREFLIGHT_REASON=DIRTY_BUT_ALLOWED_FOR_INSPECTION")
        return 0

    print("PREFLIGHT_RESULT=PASS")
    return 0

if __name__ == "__main__":
    sys.exit(main())
