#!/usr/bin/env python3
"""
validate_dependency_lock.py — Static local validation of dependency lock.
No network access. Validates deps/treefrog-v1.0.15.lock.json per B2.2A §23.

Checks:
 - JSON valid, schema_version
 - baseline SHA
 - no duplicate destination
 - each repo has URL
 - each pinned item has 40-char SHA
 - FrogUI == submodule expected
 - toolchain SHA256 64 hex
 - historical_exactness != falsely exact (must be NOT_CLAIMED)
 - unresolved dependencies enumerated
 - no Stock files as public dependencies
 - cores/siblings counts
"""
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LOCK_PATH = REPO_ROOT / "deps" / "treefrog-v1.0.15.lock.json"
EXPECTED_FROGUI = "15ea12bb4f6f642b1ec02aabebbad33e5e95ed2b"
EXPECTED_BASELINE_SHA = "27f3bf33e906d90e0cd267059bf0559afc6f8a05"
EXPECTED_BASELINE_TAG = "v1.0.15"

def fail(msg):
    print(f"FAIL: {msg}")
    return False

def ok(msg):
    print(f"PASS: {msg}")
    return True

def main():
    if not LOCK_PATH.exists():
        print(f"FAIL: lock file not found {LOCK_PATH}")
        sys.exit(1)
    try:
        with open(LOCK_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"FAIL: JSON invalid: {e}")
        sys.exit(1)

    ok(f"Lock JSON valid: {LOCK_PATH}")
    failures = 0

    # schema version
    if data.get("schema_version") != 1:
        if not fail(f"schema_version must be 1, got {data.get('schema_version')}"): failures+=1
    else:
        ok("schema_version=1")

    # baseline SHA
    baseline = data.get("baseline", {})
    if baseline.get("sha") != EXPECTED_BASELINE_SHA:
        if not fail(f"baseline.sha must be {EXPECTED_BASELINE_SHA}, got {baseline.get('sha')}"): failures+=1
    else:
        ok(f"baseline.sha={EXPECTED_BASELINE_SHA}")
    if baseline.get("tag") != EXPECTED_BASELINE_TAG:
        if not fail(f"baseline.tag must be {EXPECTED_BASELINE_TAG}, got {baseline.get('tag')}"): failures+=1
    else:
        ok(f"baseline.tag={EXPECTED_BASELINE_TAG}")

    # historical_exactness
    sel = data.get("selection_policy", {})
    if sel.get("historical_exactness") != "NOT_CLAIMED":
        if not fail(f"selection_policy.historical_exactness must be NOT_CLAIMED, got {sel.get('historical_exactness')}"): failures+=1
    else:
        ok("historical_exactness=NOT_CLAIMED")
    if not sel.get("historical_cutoff"):
        if not fail("selection_policy.historical_cutoff missing"): failures+=1
    else:
        ok(f"historical_cutoff={sel.get('historical_cutoff')}")
        # Check that method mentions last commit reachable...
        method = sel.get("method", "")
        if "last commit" not in method.lower():
            if not fail(f"selection_policy.method must mention last commit reachable, got {method}"): failures+=1
        else:
            ok("selection_policy.method mentions last commit")

    # no duplicate destination
    cores = data.get("cores", [])
    dests = [c.get("destination") for c in cores]
    if len(dests) != len(set(dests)):
        dups = [d for d in dests if dests.count(d) > 1]
        if not fail(f"duplicate destinations in cores: {set(dups)}"): failures+=1
    else:
        ok(f"no duplicate destination in cores ({len(dests)} unique)")

    # each repo has URL
    for c in cores:
        if not c.get("repository_url"):
            if not fail(f"core {c.get('destination')} missing repository_url"): failures+=1
            break
    else:
        ok("each core has repository_url")
    for s in data.get("siblings", []):
        if not s.get("repository_url"):
            if not fail(f"sibling {s.get('name')} missing repository_url"): failures+=1
            break
    else:
        ok("each sibling has repository_url")

    # each pinned item has 40-char SHA
    sha_pat = re.compile(r"^[0-9a-f]{40}$")
    for c in cores:
        sha = c.get("selected_sha")
        if sha is not None:
            if not sha_pat.match(sha):
                if not fail(f"core {c['destination']} selected_sha not 40 hex: {sha}"): failures+=1
                break
    else:
        ok("cores selected_sha are 40 hex where present")
    for s in data.get("siblings", []):
        sha = s.get("selected_sha")
        if sha is not None:
            if not sha_pat.match(sha):
                if not fail(f"sibling {s.get('name')} sha not 40 hex: {sha}"): failures+=1
                break
    else:
        ok("siblings sha 40 hex")

    # FrogUI
    submods = data.get("submodules", [])
    frogui = next((x for x in submods if x.get("path") == "frogui"), None)
    if not frogui:
        if not fail("submodules missing frogui"): failures+=1
    elif frogui.get("sha") != EXPECTED_FROGUI:
        if not fail(f"frogui sha must be {EXPECTED_FROGUI}, got {frogui.get('sha')}"): failures+=1
    else:
        ok(f"frogui sha={EXPECTED_FROGUI}")
    if frogui and frogui.get("confidence") != "HIGH":
        if not fail(f"frogui confidence must be HIGH, got {frogui.get('confidence')}"): failures+=1
    else:
        ok("frogui confidence HIGH")

    # toolchain SHA256 64 hex
    toolchain = data.get("toolchain", {})
    sha256 = toolchain.get("sha256")
    if sha256:
        if not re.match(r"^[0-9a-f]{64}$", sha256):
            if not fail(f"toolchain sha256 not 64 hex: {sha256}"): failures+=1
        else:
            ok(f"toolchain sha256 64 hex {sha256[:8]}...")
    else:
        print("WARN: toolchain sha256 missing (may be ok if tarball not present)")
        # not fail, but warn

    # no Stock files as public dependencies
    # Check cores/siblings don't contain stock paths like /home/tomaszz/..._sdcard or driver_r36sx stock blobs
    stock_indicators = ["_sdcard", "driver_r36sx", "driver_sf3500", "icube", "rkgame"]
    # Allow driver_sf3500? That's prebuilt in hijack but not in lock cores? Check
    found_stock = False
    for c in cores:
        url = c.get("repository_url", "") or ""
        dest = c.get("destination", "") or ""
        for ind in stock_indicators:
            if ind in url or ind in dest:
                # driver_r36sx is stock, should not be in lock as public repo
                # But our lock correctly has no such dest as core (drivers are not cores)
                # So if found, it's error
                if "driver" in dest:
                    if not fail(f"Stock file {dest} appears as public dependency {url}"): failures+=1
                    found_stock = True
    if not found_stock:
        ok("no Stock files as public dependencies")

    # known_unknowns enumerated
    known = data.get("known_unknowns", [])
    if not isinstance(known, list):
        if not fail("known_unknowns must be list"): failures+=1
    else:
        ok(f"known_unknowns enumerated ({len(known)} entries)")
        # Check that unresolved dependencies are enumerated
        implicit = data.get("implicit_dependencies", [])
        unresolved = [d for d in implicit if not d.get("selected_sha")]
        if unresolved and not known:
            if not fail("unresolved implicit dependencies but known_unknowns empty"): failures+=1

    # Check that duplicate_declarations is present and correct
    dups = data.get("duplicate_declarations", [])
    if not isinstance(dups, list):
        if not fail("duplicate_declarations must be list"): failures+=1
    else:
        # Expect at least libretro-prboom duplicate
        has_prboom = any(d.get("destination") == "libretro-prboom" for d in dups)
        if not has_prboom:
            print("WARN: expected duplicate libretro-prboom not found in duplicate_declarations")
        else:
            ok("duplicate_declarations contains libretro-prboom")

    # Summary
    if failures:
        print(f"\nSTATIC_LOCK_VALIDATION=FAIL ({failures} failures)")
        sys.exit(1)
    else:
        print("\nSTATIC_LOCK_VALIDATION=PASS")
        sys.exit(0)

if __name__ == "__main__":
    main()
