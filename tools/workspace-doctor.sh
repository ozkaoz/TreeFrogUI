#!/usr/bin/env bash
# tools/workspace-doctor.sh — Multi-repo workspace checker — TreeFrogUI R36SX
# READ-ONLY: never clones, fetches, pulls, checkouts, resets, cleans, modifies.
# Usage: ./tools/workspace-doctor.sh  (WSL Ubuntu canonical)
# Checks PARENT_REPO, FROGUI_REPO, PICOARCH_REPO, PCSX4ALL_REPO and CROSS_REPO_READY.
# Protocol: TREEFROGUI_AGENT_PROTOCOL=1
set -uo pipefail

PROTOCOL_EXPECTED=1
PASS=0; WARN=0; FAIL=0
say()  { printf "%-32s %s\n" "$1" "$2"; }
ok()   { say "$1" "PASS: $2"; PASS=$((PASS+1)); }
warn() { say "$1" "WARN: $2"; WARN=$((WARN+1)); }
fail() { say "$1" "FAIL: $2"; FAIL=$((FAIL+1)); }

repo_report() {
  local label="$1" path="$2"
  local found="NO" branch="?" head="?" dirty="?" origin="?" upstream="?" agents="NO" proto="?"
  if [ -d "$path/.git" ]; then
    found="YES"
    branch="$(git -C "$path" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "?")"
    head="$(git -C "$path" rev-parse --short HEAD 2>/dev/null || echo "?")"
    if [ -n "$(git -C "$path" status --porcelain 2>/dev/null | head -n 1)" ]; then dirty="DIRTY"; else dirty="CLEAN"; fi
    origin="$(git -C "$path" remote get-url origin 2>/dev/null || echo "(no origin)")"
    upstream="$(git -C "$path" remote get-url upstream 2>/dev/null || echo "(no upstream)")"
    if [ -f "$path/AGENTS.md" ]; then
      agents="YES"
      if grep -q "TREEFROGUI_AGENT_PROTOCOL=$PROTOCOL_EXPECTED" "$path/AGENTS.md" 2>/dev/null; then proto="1 OK"; else proto="MISMATCH"; fi
    else
      agents="NO"
      proto="NO AGENTS.md"
    fi
  else
    found="NO"
  fi
  say "${label}_FOUND" "$found $path"
  say "${label}_BRANCH" "$branch"
  say "${label}_HEAD" "$head"
  say "${label}_DIRTY" "$dirty"
  say "${label}_ORIGIN" "$origin"
  say "${label}_UPSTREAM" "$upstream"
  say "${label}_AGENTS" "$agents ($proto)"
  # return found for logic
  if [ "$found" = "YES" ] && [ "$agents" = "YES" ] && [ "$proto" = "1 OK" ]; then return 0; else return 1; fi
}

echo "TREEFROGUI_AGENT_PROTOCOL=$PROTOCOL_EXPECTED"
echo "WORKSPACE_ROOT= ~/sf3000-work + /mnt/d/R36SX"
echo "---"

# PARENT
PARENT_CANDIDATES=(
  "/mnt/d/R36SX/treefrog-ui-r36sx"
  "$HOME/sf3000-work/treefrog-ui-r36sx-build"
  "$HOME/sf3000-work/treefrog-ui"
)
PARENT_FOUND=0
for p in "${PARENT_CANDIDATES[@]}"; do
  if [ -d "$p/.git" ]; then
    if repo_report "PARENT_REPO" "$p"; then PARENT_FOUND=1; fi
    break
  fi
done
if [ "$PARENT_FOUND" -eq 0 ]; then
  # fallback to script's own repo
  SELF="$(cd "$(dirname "$0")/.." && pwd)"
  repo_report "PARENT_REPO" "$SELF" || true
fi
echo "---"

# FROGUI — preferred ~/sf3000-work/FrogUI (fork), fallback variants
FROGUI_CANDIDATES=(
  "$HOME/sf3000-work/FrogUI"
  "$HOME/sf3000-work/FrogUI-c0ff79f"
  "/mnt/d/R36SX/FrogUI"
)
FROGUI_FOUND=0
for p in "${FROGUI_CANDIDATES[@]}"; do
  if [ -d "$p/.git" ]; then
    if repo_report "FROGUI_REPO" "$p"; then FROGUI_FOUND=1; fi
    break
  fi
done
if [ "$FROGUI_FOUND" -eq 0 ]; then
  # check preferred path even if not git (to report NOT FOUND)
  repo_report "FROGUI_REPO" "$HOME/sf3000-work/FrogUI" || true
fi
echo "---"

# PICOARCH — preferred ~/sf3000-work/TreeFrogUI_picoarch (fork)
PICOARCH_CANDIDATES=(
  "$HOME/sf3000-work/TreeFrogUI_picoarch"
  "/mnt/d/R36SX/TreeFrogUI_picoarch"
  "$HOME/sf3000-work/picoarch"
  "$HOME/sf3000-work/TreeFrogUI_picoarch-fn"
)
PICOARCH_FOUND=0
for p in "${PICOARCH_CANDIDATES[@]}"; do
  if [ -d "$p/.git" ]; then
    if repo_report "PICOARCH_REPO" "$p"; then PICOARCH_FOUND=1; fi
    break
  fi
done
if [ "$PICOARCH_FOUND" -eq 0 ]; then
  repo_report "PICOARCH_REPO" "$HOME/sf3000-work/TreeFrogUI_picoarch" || true
fi
echo "---"

# PCSX4ALL — optional
PCSX_CANDIDATES=(
  "$HOME/sf3000-work/TreeFrogUI_pcsx4all"
  "/mnt/d/R36SX/TreeFrogUI_pcsx4all"
)
PCSX_FOUND=0
for p in "${PCSX_CANDIDATES[@]}"; do
  if [ -d "$p/.git" ]; then
    if repo_report "PCSX4ALL_REPO" "$p"; then PCSX_FOUND=1; fi
    break
  fi
done
if [ "$PCSX_FOUND" -eq 0 ]; then
  # report not found as WARN not FAIL (dependency)
  say "PCSX4ALL_REPO_FOUND" "NO (optional, not required for R36SX)"
  say "PCSX4ALL_REPO" "$HOME/sf3000-work/TreeFrogUI_pcsx4all (not found, DEPENDENCY C)"
fi
echo "---"

# Cross-repo readiness
if [ "$PARENT_FOUND" -eq 1 ] && [ "$FROGUI_FOUND" -eq 1 ] && [ "$PICOARCH_FOUND" -eq 1 ]; then
  echo "CROSS_REPO_READY=PASS (parent + FrogUI + picoarch all FOUND with AGENTS protocol 1)"
  exit 0
elif [ "$PARENT_FOUND" -eq 1 ] && [ "$FROGUI_FOUND" -eq 1 ]; then
  echo "CROSS_REPO_READY=WARN (parent+FrogUI OK, picoarch missing AGENTS or not at preferred path)"
  exit 0
else
  echo "CROSS_REPO_READY=FAIL (parent or FrogUI missing AGENTS protocol 1)"
  exit 1
fi
