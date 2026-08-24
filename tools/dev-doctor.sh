#!/usr/bin/env bash
# tools/dev-doctor.sh — Non-destructive environment checker — TreeFrogUI R36SX V2.6 Fork
# READ-ONLY: never installs, clones, fetches, pulls, checkouts, resets, cleans, modifies submodules/SD.
# Usage: ./tools/dev-doctor.sh  (WSL Ubuntu canonical)
# Exit 0 = READY / WARN, 1 = FAIL (critical: not WSL/Linux or not git repo)
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PASS=0; WARN=0; FAIL=0
say()  { printf "%-28s %s\n" "$1" "$2"; }
ok()   { say "$1" "PASS: $2"; PASS=$((PASS+1)); }
warn() { say "$1" "WARN: $2"; WARN=$((WARN+1)); }
fail() { say "$1" "FAIL: $2"; FAIL=$((FAIL+1)); }

# ENV_WSL
if grep -qi microsoft /proc/version 2>/dev/null; then
  if uname -r | grep -q "4.4."; then ok "ENV_WSL" "WSL1 $(uname -r)"; else ok "ENV_WSL" "WSL $(uname -r)"; fi
elif [ -f /proc/version ] && grep -qi linux /proc/version; then
  warn "ENV_WSL" "Linux native (expected WSL Ubuntu, but Linux OK)"
else
  fail "ENV_WSL" "Not WSL/Linux — canonical is WSL Ubuntu"
fi

# REPO_ROOT
if [ -d "$REPO_ROOT/.git" ]; then ok "REPO_ROOT" "$REPO_ROOT"; else fail "REPO_ROOT" "Not a git repo: $REPO_ROOT"; fi
say "BRANCH" "$(git -C "$REPO_ROOT" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "?")"
say "HEAD" "$(git -C "$REPO_ROOT" rev-parse --short HEAD 2>/dev/null || echo "?") ($(git -C "$REPO_ROOT" rev-parse HEAD 2>/dev/null || echo "?"))"

# GIT_STATUS
if git -C "$REPO_ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  PORCELAIN="$(git -C "$REPO_ROOT" status --porcelain 2>/dev/null || true)"
  if [ -z "$PORCELAIN" ]; then ok "GIT_STATUS" "clean"
  else
    CNT="$(echo "$PORCELAIN" | wc -l | tr -d ' ')"
    warn "GIT_STATUS" "dirty ($CNT files) — run git status --short --branch"
    git -C "$REPO_ROOT" status --short --branch 2>/dev/null | head -n 10 | while IFS= read -r l; do echo "  $l"; done
  fi
else fail "GIT_STATUS" "Not inside git work-tree"; fi

# Remotes
ORIGIN="$(git -C "$REPO_ROOT" remote get-url origin 2>/dev/null || true)"
UPSTREAM="$(git -C "$REPO_ROOT" remote get-url upstream 2>/dev/null || true)"
if [ -n "$ORIGIN" ]; then ok "FORK_REMOTE" "$ORIGIN"; else warn "FORK_REMOTE" "origin missing (expected https://github.com/ozkaoz/treefrog-ui-r36sx.git)"; fi
if [ -n "$UPSTREAM" ]; then ok "UPSTREAM_REMOTE" "$UPSTREAM"; else warn "UPSTREAM_REMOTE" "upstream missing (expected https://github.com/tzubertowski/treefrog-ui.git)"; fi
# branch sync hint
if [ -n "$UPSTREAM" ] && git -C "$REPO_ROOT" rev-parse --verify upstream/main >/dev/null 2>&1; then
  AB="$(git -C "$REPO_ROOT" rev-list --left-right --count HEAD...upstream/main 2>/dev/null || echo "? ?")"
  say "AHEAD_BEHIND" "HEAD...upstream/main $AB (ahead behind)"
fi

# FROGUI_SUBMODULE
SUB="$(git -C "$REPO_ROOT" submodule status 2>/dev/null || true)"
if echo "$SUB" | grep -q "15ea12bb4f6f642b1ec02aabebbad33e5e95ed2b"; then ok "FROGUI_SUBMODULE" "15ea12b sf3000 $(echo "$SUB" | head -n1 | cut -c1-80)"
elif [ -z "$SUB" ]; then warn "FROGUI_SUBMODULE" "no submodule status"
elif echo "$SUB" | grep -q "^-"; then warn "FROGUI_SUBMODULE" "uninitialized — run git submodule update --init"
elif echo "$SUB" | grep -q "^+"; then warn "FROGUI_SUBMODULE" "modified $(echo "$SUB" | head -n1)"
else warn "FROGUI_SUBMODULE" "$SUB"
fi

# TOOLCHAIN
TOOLCHAIN="$HOME/sf3000-work/sf3000toolchain/mipsel-buildroot-linux-gnu_sdk-buildroot"
TOOLCHAIN_CC="$TOOLCHAIN/opt/ext-toolchain/bin/mips-mti-linux-gnu-gcc"
if [ -x "$TOOLCHAIN_CC" ]; then
  VER="$("$TOOLCHAIN_CC" --version 2>/dev/null | head -n1)"
  ok "TOOLCHAIN" "$TOOLCHAIN"
  ok "C_COMPILER" "$VER"
else
  fail "TOOLCHAIN" "missing $TOOLCHAIN_CC — see docs/BUILDING.md (game-de-it/sf3000 sf3000_toolchain_v0.1)"
  warn "C_COMPILER" "mips-mti-linux-gnu-gcc not found"
fi

# Sibling repos (optional, WARN not FAIL)
for sib in "$HOME/sf3000-work/picoarch" "$HOME/sf3000-work/FrogUI" "$HOME/sf3000-work/TreeFrogUI_pcsx4all"; do
  if [ -d "$sib/.git" ]; then ok "SIBLING" "$(basename "$sib") $(git -C "$sib" rev-parse --short HEAD 2>/dev/null || echo "?")"
  else warn "SIBLING" "$(basename "$sib") not found at $sib (optional, see docs/BUILDING.md)"
  fi
done

# Host tools
if command -v make >/dev/null 2>&1; then ok "MAKE" "$(make --version 2>&1 | head -n1)"; else fail "MAKE" "make not found"; fi
if command -v cmake >/dev/null 2>&1; then ok "CMAKE" "$(cmake --version 2>&1 | head -n1) (optional, TIC-80 only)"; else warn "CMAKE" "cmake not found (TIC-80 will be skipped)"; fi
if command -v python3 >/dev/null 2>&1; then ok "PYTHON" "$(python3 --version 2>&1)"; else fail "PYTHON" "python3 not found"; fi
if command -v sha256sum >/dev/null 2>&1; then ok "SHA256SUM" "$(sha256sum --version 2>&1 | head -n1)"; else warn "SHA256SUM" "sha256sum not found"; fi
if command -v 7z >/dev/null 2>&1; then ok "7Z" "$(7z 2>&1 | head -n1)"; else warn "7Z" "7z not found (release pack needs 7z or zip)"; fi

# DEPENDENCY_LOCK
LOCK="$REPO_ROOT/deps/treefrog-v1.0.15.lock.json"
if [ -f "$LOCK" ]; then
  if python3 -c "import json; json.load(open('$LOCK'))" 2>/dev/null; then ok "DEPENDENCY_LOCK" "$LOCK (valid JSON)"
  else fail "DEPENDENCY_LOCK" "$LOCK invalid JSON"; fi
  # quick schema check
  if python3 "$REPO_ROOT/scripts/dev/validate_dependency_lock.py" >/dev/null 2>&1; then ok "LOCK_VALIDATE" "validate_dependency_lock.py PASS"
  else warn "LOCK_VALIDATE" "validate_dependency_lock.py WARN/FAIL — run python scripts/dev/validate_dependency_lock.py"
  fi
else warn "DEPENDENCY_LOCK" "missing $LOCK"; fi

# .gitignore / .gitattributes hint
if [ -f "$REPO_ROOT/.gitignore" ]; then ok "GITIGNORE" "present"; else warn "GITIGNORE" "missing"; fi
if [ -f "$REPO_ROOT/.gitattributes" ]; then ok "GITATTRIBUTES" "present (LF policy)"; else warn "GITATTRIBUTES" "missing (see docs/BUILDING.md, WSL CRLF)"; fi

# READY
echo "---"
if [ "$FAIL" -gt 0 ]; then
  echo "READY_FOR_HOST_DEVELOPMENT=FAIL ($FAIL FAIL, $WARN WARN, $PASS PASS)"
  exit 1
elif [ "$WARN" -gt 0 ]; then
  echo "READY_FOR_HOST_DEVELOPMENT=WARN ($PASS PASS, $WARN WARN) — safe for docs/host dev, check WARNs before BUILD"
  exit 0
else
  echo "READY_FOR_HOST_DEVELOPMENT=PASS ($PASS PASS)"
  exit 0
fi
