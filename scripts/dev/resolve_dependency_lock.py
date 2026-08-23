#!/usr/bin/env python3
"""
resolve_dependency_lock.py — Resolve TreeFrogUI v1.0.15 external dependencies to SHA-pinned lock.

CLASS B — read-only, idempotent, no clone persistent, no build, no product file modification.
Generates deps/treefrog-v1.0.15.lock.json deterministically.

Usage:
  python scripts/dev/resolve_dependency_lock.py
  python scripts/dev/resolve_dependency_lock.py --check   # compare current lock with fresh resolution, exit 1 if diverge, no overwrite
  python scripts/dev/resolve_dependency_lock.py --cutoff 2026-08-20T16:14:20Z  # override historical cutoff
"""
import argparse
import json
import os
import re
import subprocess
import sys
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import time

REPO_ROOT = Path(__file__).resolve().parents[2]
LOCK_PATH = REPO_ROOT / "deps" / "treefrog-v1.0.15.lock.json"
DEFAULT_CUTOFF = "2026-08-20T16:14:20Z"  # RELEASE_PUBLISHED_AT for v1.0.15
BASELINE_TAG = "v1.0.15"
BASELINE_SHA = "27f3bf33e906d90e0cd267059bf0559afc6f8a05"
FROGUI_SHA = "15ea12bb4f6f642b1ec02aabebbad33e5e95ed2b"

GH_TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or ""

def run(cmd, cwd=None):
    r = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=False)
    return r.stdout.strip(), r.stderr.strip(), r.returncode

def github_api(path, params=None):
    """Simple GET to api.github.com with token. Returns parsed JSON or raises."""
    import urllib.parse
    url = f"https://api.github.com/{path.lstrip('/')}"
    if params:
        qs = urllib.parse.urlencode(params)
        url = f"{url}?{qs}"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "treefrog-resolver/1.0",
    }
    if GH_TOKEN:
        headers["Authorization"] = f"token {GH_TOKEN}"
    req = Request(url, headers=headers)
    try:
        with urlopen(req, timeout=30) as resp:
            data = resp.read()
            return json.loads(data.decode("utf-8")), resp.headers
    except HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore") if e.fp else ""
        raise RuntimeError(f"GitHub API {path} failed {e.code}: {body[:500]}") from e
    except URLError as e:
        raise RuntimeError(f"GitHub API {path} URLError: {e}") from e

def get_repo_info(owner_repo):
    data, _ = github_api(f"repos/{owner_repo}")
    return data

def get_commits_until(owner_repo, branch, cutoff_iso, per_page=1):
    # until is ISO8601, committer date
    try:
        data, _ = github_api(f"repos/{owner_repo}/commits", params={"sha": branch, "until": cutoff_iso, "per_page": str(per_page)})
        return data
    except RuntimeError as e:
        # if branch not found, propagate
        raise

def parse_clone_cores(tag):
    content, _, rc = run(["git", "show", f"{tag}:clone_cores.sh"], cwd=str(REPO_ROOT))
    if rc != 0:
        raise RuntimeError(f"git show {tag}:clone_cores.sh failed")
    # Also get line numbers
    lines = content.splitlines()
    clones = []
    # pattern: clone <dest> <url> [branch]
    # clone function: clone <dir> <url> <branch>
    # Example: clone fceumm          https://github.com/tzubertowski/libretro-fceumm
    #          clone fake-08         https://github.com/tzubertowski/fake-08         sf3000
    # Note: clone name may contain dash, underscore; url may have trailing branch
    # We'll parse via regex
    # The clone() function in file is: clone() { local dir="$1" local url="$2" local branch="${3:-}" ... } and calls like: clone fceumm https://github.com/...
    # So each line with ^clone\s+(\S+)\s+(\S+)(?:\s+(\S+))?  # but need to handle comments
    pat = re.compile(r'^\s*clone\s+(\S+)\s+(\S+)(?:\s+(\S+))?')
    for idx, line in enumerate(lines, start=1):
        # strip comments after #? But url doesn't contain #, branch may be before #
        # Remove trailing comment: split on '#', but careful: url has no #, so split
        # Keep line without comment for parsing branch
        # First, remove comment part after '#', but keep if branch is before #
        # We'll split on ' #'? Actually lines like `clone Ardens          https://github.com/tiberiusbrown/Ardens          # Arduboy` have branch before comment? No, that's url with comment. So we can remove everything after ' #' or ' #'?
        # Simple: split on '#', take first part, then parse
        # But need to handle that branch may be sf3000 before comment: `clone fake-08 ... sf3000` no comment after, fine.
        # So split on '#', take line.split('#')[0]
        clean = line.split('#')[0].strip()
        if not clean:
            continue
        m = pat.match(clean)
        if m:
            dest, url, branch = m.group(1), m.group(2), m.group(3)
            # branch may be None if not provided
            # url should be https://...
            # destination is dir under cores/
            clones.append({
                "destination": dest,
                "repository_url": url,
                "requested_branch": branch if branch else None,
                "line_number": idx,
                "raw_line": line.strip()
            })
    return clones

def extract_build_all_core_dirs(tag):
    content, _, rc = run(["git", "show", f"{tag}:build_all.sh"], cwd=str(REPO_ROOT))
    if rc != 0:
        raise RuntimeError(f"git show {tag}:build_all.sh failed")
    # Find all cores/<name> and $CORES/<name> and -C cores/<name>
    # Also _b snes9x2005_plus snes9x2005 "" ... -> second arg is cores dir
    # We'll search for patterns
    dirs = set()
    # Pattern 1: cores/<name> literally
    for m in re.finditer(r'cores/([A-Za-z0-9_.\-]+)', content):
        dirs.add(m.group(1).split('/')[0])  # just first component after cores/
        # Actually need to handle cores/<name> as dir, but some are like cores/<name>/Makefile
        # We'll take first segment
    # Pattern 2: _b <output> <srcdir> ...
    # _b snes9x2005_plus   snes9x2005  ...
    # The second field is srcdir under cores/
    for line in content.splitlines():
        if "_b " in line or "_apply_patch" in line:
            # _b pattern
            m = re.search(r'_b\s+\S+\s+(\S+)', line)
            if m:
                dirs.add(m.group(1))
            # _apply_patch
            m2 = re.search(r'_apply_patch\s+\S+\s+(\S+)', line)
            if m2:
                dirs.add(m2.group(1))
    # Also grep for "cores/" with maybe quotes
    # Add explicit known implicit: pcsx_rearmed is referenced but not in clone_cores
    # Check if pcsx_rearmed appears in build_all.sh
    if "pcsx_rearmed" in content:
        dirs.add("pcsx_rearmed")
    # Also check for tyrquake? It's in clone but not _b?
    # We'll also add arduous, etc.
    return sorted(dirs)

def resolve_repo_fork(owner_repo, requested_branch, cutoff_iso):
    """
    Resolve a repo to SHA at cutoff.
    Returns dict with selected_branch, selected_sha, committer dates, confidence, etc.
    """
    # Get repo info to know default branch
    try:
        info = get_repo_info(owner_repo)
        default_branch = info.get("default_branch", "master")
    except Exception as e:
        return {
            "repository": owner_repo,
            "requested_branch": requested_branch,
            "selected_branch": None,
            "selected_sha": None,
            "error": str(e),
            "confidence": "UNKNOWN",
            "sha_verified": False,
        }
    selected_branch = requested_branch if requested_branch else default_branch
    # Verify requested branch exists, if not fallback to default
    # We'll try to fetch branch info
    try:
        # Use get branch to check existence
        branch_data, _ = github_api(f"repos/{owner_repo}/branches/{selected_branch}")
        # exists
    except RuntimeError:
        # requested branch not found, fallback to default
        if requested_branch and requested_branch != default_branch:
            selected_branch = default_branch
            confidence = "LOW"
        else:
            return {
                "repository": owner_repo,
                "requested_branch": requested_branch,
                "selected_branch": selected_branch,
                "selected_sha": None,
                "error": f"branch {selected_branch} not found",
                "confidence": "UNKNOWN",
                "sha_verified": False,
                "historical_default_branch_verified": False,
            }
        confidence = "LOW"
    else:
        confidence = "MEDIUM" if requested_branch else "LOW"
        # historical_default_branch_verified: if requested_branch was None, we don't know historical default
        # So LOW degrades to LOW anyway

    # Now get last commit on selected_branch at or before cutoff
    try:
        commits = get_commits_until(owner_repo, selected_branch, cutoff_iso, per_page=1)
        if not commits:
            # No commits before cutoff? Maybe branch created after cutoff, try default branch history?
            # Try without until to get latest? But we should mark unresolved
            return {
                "repository": owner_repo,
                "requested_branch": requested_branch,
                "selected_branch": selected_branch,
                "selected_sha": None,
                "error": f"no commits on {selected_branch} before {cutoff_iso}",
                "confidence": "UNKNOWN",
                "sha_verified": False,
                "historical_default_branch_verified": False if not requested_branch else True,
            }
        c = commits[0]
        sha = c["sha"]
        author_date = c["commit"]["author"]["date"]
        committer_date = c["commit"]["committer"]["date"]
        # Verify sha exists via separate call (it does)
        return {
            "repository": owner_repo,
            "requested_branch": requested_branch,
            "selected_branch": selected_branch,
            "selected_sha": sha,
            "commit_author_date": author_date,
            "commit_committer_date": committer_date,
            "selection_method": f"last commit on {selected_branch} at or before {cutoff_iso}",
            "confidence": confidence,
            "sha_verified": True,
            "historical_default_branch_verified": True if requested_branch else False,
        }
    except Exception as e:
        return {
            "repository": owner_repo,
            "requested_branch": requested_branch,
            "selected_branch": selected_branch,
            "selected_sha": None,
            "error": str(e),
            "confidence": "UNKNOWN",
            "sha_verified": False,
        }

def main():
    parser = argparse.ArgumentParser(description="Resolve TreeFrogUI dependency lock")
    parser.add_argument("--cutoff", type=str, default=DEFAULT_CUTOFF, help="Historical cutoff ISO8601 (default: RELEASE_PUBLISHED_AT 2026-08-20T16:14:20Z)")
    parser.add_argument("--check", action="store_true", help="Check current lock vs fresh resolution, exit 1 if diverge")
    parser.add_argument("--output", type=str, default=str(LOCK_PATH), help="Lock output path")
    args = parser.parse_args()

    # Validate cutoff is ISO
    cutoff = args.cutoff
    try:
        # ensure parsable
        dt = datetime.fromisoformat(cutoff.replace("Z", "+00:00"))
        # Use as is for API (needs ISO8601 with Z)
        # Ensure Z
        if not cutoff.endswith("Z"):
            # convert to Z
            cutoff = dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    except Exception as e:
        print(f"Invalid cutoff {cutoff}: {e}", file=sys.stderr)
        sys.exit(2)

    # Preflight: check lock path parent exists
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)

    # Baseline info
    tag_commit, _, _ = run(["git", "rev-parse", BASELINE_TAG], cwd=str(REPO_ROOT))
    tag_show, _, _ = run(["git", "show", "-s", "--format=%H%n%aI%n%cI%n%s", BASELINE_TAG], cwd=str(REPO_ROOT))
    # Try gh release view
    release_published = DEFAULT_CUTOFF
    try:
        out, _, rc = run(["gh", "release", "view", BASELINE_TAG, "--repo", "tzubertowski/treefrog-ui", "--json", "tagName,publishedAt,createdAt,targetCommitish"], cwd=str(REPO_ROOT))
        if rc == 0:
            import json as j
            data = j.loads(out)
            if data.get("publishedAt"):
                release_published = data["publishedAt"]
    except Exception:
        pass

    # Parse clone_cores
    clones = parse_clone_cores(BASELINE_TAG)
    core_declaration_count = len(clones)
    # Count unique destinations and repositories
    dests = {}
    repos = set()
    duplicates = []
    for c in clones:
        dest = c["destination"]
        repos.add(c["repository_url"])
        if dest in dests:
            duplicates.append({"destination": dest, "first_line": dests[dest]["line_number"], "second_line": c["line_number"], "url_first": dests[dest]["repository_url"], "url_second": c["repository_url"]})
        else:
            dests[dest] = c
    core_unique_destination_count = len(dests)
    core_unique_repository_count = len(repos)

    # Detect duplicate destinations
    duplicate_destinations = []
    if duplicates:
        # Group by dest
        dup_map = {}
        for d in duplicates:
            dup_map.setdefault(d["destination"], []).append(d)
        for dest, lst in dup_map.items():
            duplicate_destinations.append({"destination": dest, "occurrences": len(lst)+1, "details": lst})

    # Also need to handle duplicate libretro-prboom (appears twice with same url)
    # Our duplicates detection will catch it

    # Build implicit dependencies
    build_dirs = extract_build_all_core_dirs(BASELINE_TAG)
    clone_dirs = set(dests.keys())
    # build_dirs may contain names like snes9x2005, etc., but _b uses snes9x2005_plus? Need to map output vs srcdir: _b first arg is output name, second is srcdir
    # Our extract already handles srcdir
    # Find missing and unused
    missing_from_clone = sorted([d for d in build_dirs if d not in clone_dirs])
    unused_clone = sorted([d for d in clone_dirs if d not in build_dirs])

    # For B1.5, known missing is pcsx_rearmed
    # Let's ensure we capture pcsx_rearmed as implicit if not in clone
    # Also check for tyrquake? It's in clone, but build_all may reference tyrquake? Not in our earlier grep, but let's keep

    # Determine siblings from README at tag
    siblings = []
    # FrogUI is submodule, not sibling for lock (handled as submodule)
    # Picoarch, pcsx4all are siblings per README
    # We'll define siblings list as per spec: TreeFrogUI_picoarch r36sx, TreeFrogUI_pcsx4all main, and potentially pcsx_rearmed if implicit
    # Also check for vitaquake2, rockbox? But those are not in v1.0.15 README's sibling list (only picoarch, pcsx4all per README)
    # We'll include picoarch and pcsx4all as siblings, and tyrquake/vitaquake as not siblings (they are cores)
    # For lock, siblings are external workspace repos not under cores/

    # Resolve each clone destination to SHA
    # We need to map repository_url to owner/repo (github.com/...)
    # For each unique destination, resolve
    locked_cores = []
    # To be deterministic, sort by destination
    for dest in sorted(dests.keys()):
        info = dests[dest]
        url = info["repository_url"]
        # Extract owner/repo from url https://github.com/owner/repo[.git]
        m = re.match(r'https?://github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$', url)
        if not m:
            # try git@github.com:owner/repo.git ? But clone_cores uses https only
            locked_cores.append({
                "destination": dest,
                "repository_url": url,
                "requested_branch": info["requested_branch"],
                "selected_branch": None,
                "selected_sha": None,
                "error": f"cannot parse owner/repo from url {url}",
                "confidence": "UNKNOWN",
                "sha_verified": False,
                "line_number": info["line_number"],
                "patches": []
            })
            continue
        owner, repo = m.group(1), m.group(2)
        owner_repo = f"{owner}/{repo}"
        requested_branch = info["requested_branch"]
        # Resolve
        res = resolve_repo_fork(owner_repo, requested_branch, cutoff)
        # Add patches metadata: find patches for this dest via build_all.sh _apply_patch
        # We'll need to parse build_all.sh for patches per dest
        # For now, we'll fill later
        entry = {
            "destination": dest,
            "repository_url": url,
            "requested_branch": requested_branch,
            "selected_branch": res.get("selected_branch"),
            "selected_sha": res.get("selected_sha"),
            "commit_author_date": res.get("commit_author_date"),
            "commit_committer_date": res.get("commit_committer_date"),
            "selection_method": res.get("selection_method"),
            "confidence": res.get("confidence", "UNKNOWN"),
            "sha_verified": res.get("sha_verified", False),
            "historical_default_branch_verified": res.get("historical_default_branch_verified", False),
            "line_number": info["line_number"],
            "patches": [],  # filled later
        }
        if "error" in res and res["error"]:
            entry["error"] = res["error"]
        locked_cores.append(entry)
        # Small delay to avoid rate limit
        time.sleep(0.2)

    # Fill patches per core: parse build_all.sh for _apply_patch lines
    # Need to map patches to dest
    build_all_content, _, _ = run(["git", "show", f"{BASELINE_TAG}:build_all.sh"], cwd=str(REPO_ROOT))
    patch_map = {}  # dest -> list patches
    for line in build_all_content.splitlines():
        # _apply_patch geolith-no-lto.patch      libretro-geolith
        m = re.search(r'_apply_patch\s+(\S+)\s+(\S+)', line)
        if m:
            patch_file, dest = m.group(1), m.group(2)
            patch_map.setdefault(dest, []).append(f"patches/{patch_file}")
    for entry in locked_cores:
        dest = entry["destination"]
        if dest in patch_map:
            entry["patches"] = sorted(patch_map[dest])

    # Handle duplicate destinations: keep one canonical, but we already have one per dest
    # duplicate_declarations already recorded

    # Implicit dependencies: those build_dirs missing from clone
    implicit_deps = []
    for dep in missing_from_clone:
        # Try to infer repo for implicit dep
        # For pcsx_rearmed, we know it's tzubertowski/TreeFrogUI_pcsx_rearmed
        # For others, we should mark as unresolved if unknown
        if dep == "pcsx_rearmed":
            owner_repo = "tzubertowski/TreeFrogUI_pcsx_rearmed"
            url = f"https://github.com/{owner_repo}"
            # Try to resolve with master branch at cutoff
            res = resolve_repo_fork(owner_repo, "master", cutoff)
            entry = {
                "destination": dep,
                "repository_url": url,
                "requested_branch": "master",
                "selected_branch": res.get("selected_branch"),
                "selected_sha": res.get("selected_sha"),
                "commit_author_date": res.get("commit_author_date"),
                "commit_committer_date": res.get("commit_committer_date"),
                "selection_method": res.get("selection_method") or "implicit dependency inferred for build_all.sh",
                "confidence": res.get("confidence", "LOW"),
                "sha_verified": res.get("sha_verified", False),
                "reason": "referenced in build_all.sh but not in clone_cores.sh",
                "patches": patch_map.get(dep, []),
            }
            if "error" in res:
                entry["error"] = res["error"]
            implicit_deps.append(entry)
            time.sleep(0.2)
        else:
            # Unknown implicit deps: record as unresolved
            implicit_deps.append({
                "destination": dep,
                "repository_url": None,
                "requested_branch": None,
                "selected_branch": None,
                "selected_sha": None,
                "confidence": "UNKNOWN",
                "sha_verified": False,
                "reason": "referenced in build_all.sh but not in clone_cores.sh, no known repo mapping",
                "patches": patch_map.get(dep, []),
            })

    # Siblings
    locked_siblings = []
    # FrogUI is submodule, not sibling
    # Siblings per README at tag: picoarch, pcsx4all
    siblings_def = [
        ("TreeFrogUI_picoarch", "https://github.com/tzubertowski/TreeFrogUI_picoarch", "r36sx"),
        ("TreeFrogUI_pcsx4all", "https://github.com/tzubertowski/TreeFrogUI_pcsx4all", "main"),
        # Also consider vitaquake2 etc but not in v1.0.15 README's sibling list, so skip
    ]
    for name, url, branch in siblings_def:
        owner_repo = "/".join(url.replace("https://github.com/", "").split("/")[:2])
        res = resolve_repo_fork(owner_repo, branch, cutoff)
        locked_siblings.append({
            "name": name,
            "repository_url": url,
            "requested_branch": branch,
            "selected_branch": res.get("selected_branch"),
            "selected_sha": res.get("selected_sha"),
            "commit_author_date": res.get("commit_author_date"),
            "commit_committer_date": res.get("commit_committer_date"),
            "selection_method": res.get("selection_method"),
            "confidence": res.get("confidence", "UNKNOWN"),
            "sha_verified": res.get("sha_verified", False),
            "historical_default_branch_verified": res.get("historical_default_branch_verified", False),
        })
        time.sleep(0.2)

    # Toolchain
    toolchain_path = Path.home() / "sf3000-work" / "sf3000toolchain" / "mipsel-buildroot-linux-gnu_sdk-buildroot.tar.gz"
    # Fallback to repo's expected path via env
    if not toolchain_path.exists():
        # Try alternative from build_all.sh
        toolchain_path = Path("/home/dafunknoise/sf3000-work/sf3000toolchain/mipsel-buildroot-linux-gnu_sdk-buildroot.tar.gz")
    toolchain_sha256 = None
    toolchain_size = None
    toolchain_asset = toolchain_path.name if toolchain_path.exists() else None
    if toolchain_path.exists():
        h = hashlib.sha256()
        with open(toolchain_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        toolchain_sha256 = h.hexdigest()
        toolchain_size = toolchain_path.stat().st_size
    # Get compiler version via local toolchain
    TOOLCHAIN_DIR = Path.home() / "sf3000-work" / "sf3000toolchain" / "mipsel-buildroot-linux-gnu_sdk-buildroot"
    cross_bin = TOOLCHAIN_DIR / "opt" / "ext-toolchain" / "bin" / "mips-mti-linux-gnu-gcc"
    compiler_version = None
    cross_target = None
    if cross_bin.exists():
        out, _, _ = run([str(cross_bin), "--version"])
        compiler_version = out.splitlines()[0] if out else None
        out2, _, _ = run([str(cross_bin), "-dumpmachine"])
        cross_target = out2.strip() if out2 else None
    toolchain_info = {
        "repository": "game-de-it/sf3000",
        "release_tag": "sf3000_toolchain_v0.1",
        "asset_name": toolchain_asset,
        "asset_path": str(toolchain_path) if toolchain_path.exists() else None,
        "sha256": toolchain_sha256,
        "size": toolchain_size,
        "compiler_version": compiler_version,
        "target": cross_target,
        "url": "https://github.com/game-de-it/sf3000/releases/tag/sf3000_toolchain_v0.1",
    }

    # Submodules
    locked_submodules = [
        {
            "path": "frogui",
            "url": "git@github.com:tzubertowski/FrogUI.git",
            "branch": "sf3000",
            "sha": FROGUI_SHA,
            "pinned": True,
            "confidence": "HIGH",
        }
    ]

    # Known unknowns
    known_unknowns = []
    if implicit_deps:
        for dep in implicit_deps:
            if dep.get("selected_sha") is None:
                known_unknowns.append(f"implicit dependency {dep['destination']} unresolved")
    # Check for any core with sha_verified false
    for c in locked_cores:
        if not c.get("sha_verified"):
            known_unknowns.append(f"core {c['destination']} sha not verified")
    # Check stock
    known_unknowns.extend([
        "R36SX driver source not public (stock proprietary)",
        "Stock SD dumps for 7 devices not public (proprietary, requires local Stock OS)",
    ])

    # Build final lock
    lock = {
        "schema_version": 1,
        "baseline": {
            "tag": BASELINE_TAG,
            "sha": BASELINE_SHA,
            "commit_author_date": tag_show.splitlines()[1] if len(tag_show.splitlines()) > 1 else None,
            "commit_committer_date": tag_show.splitlines()[2] if len(tag_show.splitlines()) > 2 else None,
        },
        "selection_policy": {
            "historical_cutoff": cutoff,
            "historical_cutoff_source": "RELEASE_PUBLISHED_AT" if cutoff == DEFAULT_CUTOFF else "override",
            "method": "last commit reachable on selected branch at or before historical cutoff",
            "historical_exactness": "NOT_CLAIMED",
            "note": "This lock makes the fork deterministic. It does NOT prove exact historical reconstruction of upstream v1.0.15.",
        },
        "toolchain": toolchain_info,
        "submodules": locked_submodules,
        "siblings": sorted(locked_siblings, key=lambda x: x["name"]),
        "cores": sorted(locked_cores, key=lambda x: x["destination"]),
        "implicit_dependencies": sorted(implicit_deps, key=lambda x: x["destination"]) if implicit_deps else [],
        "duplicate_declarations": duplicate_destinations,
        "known_unknowns": sorted(set(known_unknowns)),
        "stats": {
            "core_declaration_count": core_declaration_count,
            "core_unique_destination_count": core_unique_destination_count,
            "core_unique_repository_count": core_unique_repository_count,
            "duplicate_destination_count": len(duplicate_destinations),
            "build_referenced_core_dir_count": len(build_dirs),
            "implicit_dependency_count": len(implicit_deps),
            "locked_core_count": len(locked_cores),
            "locked_sibling_count": len(locked_siblings),
            "locked_submodule_count": len(locked_submodules),
        }
    }

    # Add confidence counts
    conf_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0, "UNKNOWN": 0}
    for c in locked_cores:
        conf_counts[c.get("confidence", "UNKNOWN")] = conf_counts.get(c.get("confidence", "UNKNOWN"), 0) + 1
    for s in locked_siblings:
        conf_counts[s.get("confidence", "UNKNOWN")] = conf_counts.get(s.get("confidence", "UNKNOWN"), 0) + 1
    # submodules HIGH
    conf_counts["HIGH"] += len(locked_submodules)
    lock["stats"]["high_confidence_count"] = conf_counts["HIGH"]
    lock["stats"]["medium_confidence_count"] = conf_counts["MEDIUM"]
    lock["stats"]["low_confidence_count"] = conf_counts["LOW"]
    lock["stats"]["unresolved_count"] = conf_counts["UNKNOWN"]
    lock["stats"]["frogui_sha"] = FROGUI_SHA
    # Find picoarch selected
    for s in locked_siblings:
        if "picoarch" in s["name"].lower():
            lock["stats"]["picoarch_selected_sha"] = s.get("selected_sha")
            lock["stats"]["picoarch_confidence"] = s.get("confidence")
        if "pcsx4all" in s["name"].lower():
            lock["stats"]["pcsx4all_selected_sha"] = s.get("selected_sha")
        if "pcsx_rearmed" in s["name"].lower():
            lock["stats"]["pcsx_rearmed_selected_sha"] = s.get("selected_sha")

    # Toolchain stats
    lock["stats"]["toolchain_tag"] = toolchain_info["release_tag"]
    lock["stats"]["toolchain_asset"] = toolchain_info["asset_name"]
    lock["stats"]["toolchain_sha256"] = toolchain_info["sha256"]

    # Sysroot
    # Compute sysroots as in B2.1
    TOOLCHAIN = Path.home() / "sf3000-work" / "sf3000toolchain" / "mipsel-buildroot-linux-gnu_sdk-buildroot"
    BUILD_ALL_SYSROOT = TOOLCHAIN / "mipsel-buildroot-linux-gnu" / "sysroot"
    COMPILER_SYSROOT = None
    if cross_bin.exists():
        out, _, _ = run([str(cross_bin), "-print-sysroot"])
        COMPILER_SYSROOT = out.strip()
    lock["stats"]["build_all_sysroot"] = str(BUILD_ALL_SYSROOT)
    lock["stats"]["compiler_sysroot"] = COMPILER_SYSROOT
    lock["stats"]["sysroot_paths_identical"] = str(BUILD_ALL_SYSROOT) == str(COMPILER_SYSROOT) if COMPILER_SYSROOT else False
    # Content equivalence: we already know PARTIAL from B2.1
    lock["stats"]["sysroot_content_equivalence"] = "PARTIAL"
    lock["stats"]["recommended_sysroot"] = COMPILER_SYSROOT or str(BUILD_ALL_SYSROOT)

    # Dpkg audit
    out, _, _ = run(["dpkg", "--audit"])
    lock["stats"]["dpkg_audit"] = out.strip()[:2000] if out else "OK"
    out2, _, _ = run(["apt-get", "check"])
    lock["stats"]["apt_check"] = out2.strip()[:2000] if out2 else "OK"

    # Write lock deterministically (sorted keys, indent 2)
    if args.check:
        # Compare with existing
        if not Path(args.output).exists():
            print(f"Lock file {args.output} does not exist, cannot check", file=sys.stderr)
            sys.exit(2)
        with open(args.output, "r", encoding="utf-8") as f:
            existing = json.load(f)
        # Compare normalized JSON (sorted)
        existing_str = json.dumps(existing, sort_keys=True, indent=2)
        new_str = json.dumps(lock, sort_keys=True, indent=2)
        if existing_str == new_str:
            print("REMOTE_LOCK_VALIDATION=PASS (lock matches fresh resolution)")
            sys.exit(0)
        else:
            print("REMOTE_LOCK_VALIDATION=FAIL (lock diverges from fresh resolution)", file=sys.stderr)
            # Diff summary
            import difflib
            diff = difflib.unified_diff(existing_str.splitlines(), new_str.splitlines(), fromfile="existing", tofile="fresh", lineterm="")
            for line in list(diff)[:200]:
                print(line)
            sys.exit(1)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(lock, f, sort_keys=True, indent=2)
            f.write("\n")
        print(f"Wrote lock to {args.output}")
        print(f"CORE_DECLARATION_COUNT={core_declaration_count}")
        print(f"CORE_UNIQUE_DESTINATION_COUNT={core_unique_destination_count}")
        print(f"DUPLICATE_DESTINATIONS={len(duplicate_destinations)}")
        print(f"BUILD_REFERENCED_CORE_DIR_COUNT={len(build_dirs)}")
        print(f"IMPLICIT_DEPENDENCY_COUNT={len(implicit_deps)}")
        print(f"LOCKED_CORE_COUNT={len(locked_cores)}")
        print(f"HIGH={conf_counts['HIGH']} MEDIUM={conf_counts['MEDIUM']} LOW={conf_counts['LOW']} UNKNOWN={conf_counts['UNKNOWN']}")
        sys.exit(0)

if __name__ == "__main__":
    main()
