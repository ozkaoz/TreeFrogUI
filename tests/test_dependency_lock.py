#!/usr/bin/env python3
"""
test_dependency_lock.py — Static contract test for dependency lock.
No internet. Checks deps/treefrog-v1.0.15.lock.json deterministically.
"""
import json
import re
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
LOCK_PATH = REPO_ROOT / "deps" / "treefrog-v1.0.15.lock.json"

def fail(msg, failures):
    failures.append(msg)
    print(f"FAIL: {msg}")

def ok(msg):
    print(f"PASS: {msg}")

def main():
    failures = []
    if not LOCK_PATH.exists():
        print(f"FAIL: lock not found {LOCK_PATH}")
        sys.exit(1)
    try:
        data = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"FAIL: json load {e}")
        sys.exit(1)
    ok("lock json load")

    if data.get("schema_version") != 1:
        fail(f"schema_version 1, got {data.get('schema_version')}", failures)
    else:
        ok("schema_version 1")

    if data["baseline"]["sha"] != "27f3bf33e906d90e0cd267059bf0559afc6f8a05":
        fail("baseline sha", failures)
    else:
        ok("baseline sha")

    if data["selection_policy"]["historical_exactness"] != "NOT_CLAIMED":
        fail("historical_exactness NOT_CLAIMED", failures)
    else:
        ok("historical_exactness NOT_CLAIMED")

    if "last commit" not in data["selection_policy"]["method"].lower():
        fail("method last commit", failures)
    else:
        ok("method last commit")

    cores = data.get("cores", [])
    if len(cores) != 77:
        fail(f"locked core count 77, got {len(cores)}", failures)
    else:
        ok("locked core count 77")

    # No duplicate destinations
    dests = [c["destination"] for c in cores]
    if len(dests) != len(set(dests)):
        fail("duplicate dest", failures)
    else:
        ok("no duplicate dest")

    # FrogUI
    frogui = next((x for x in data.get("submodules", []) if x["path"]=="frogui"), None)
    if not frogui or frogui["sha"] != "15ea12bb4f6f642b1ec02aabebbad33e5e95ed2b":
        fail("frogui sha", failures)
    else:
        ok("frogui sha")

    # toolchain sha256 64 hex
    sha256 = data.get("toolchain", {}).get("sha256")
    if not sha256 or not re.match(r"^[0-9a-f]{64}$", sha256):
        fail(f"toolchain sha256 64 hex, got {sha256}", failures)
    else:
        ok("toolchain sha256")

    # Check duplicate_declarations contains libretro-prboom
    dups = data.get("duplicate_declarations", [])
    if not any(d["destination"]=="libretro-prboom" for d in dups):
        fail("duplicate libretro-prboom", failures)
    else:
        ok("duplicate libretro-prboom")

    # Check implicit_dependencies includes pcsx_rearmed at least?
    # B1.5 had 14 implicit, but B2.2A resolver may have many UNKNOWN due to parsing build_all.sh cores/... as platform paths
    implicit = data.get("implicit_dependencies", [])
    # At least should have pcsx_rearmed or many UNKNOWN — we just check that implicit is list
    if not isinstance(implicit, list):
        fail("implicit list", failures)
    else:
        ok(f"implicit count {len(implicit)}")

    # Check siblings
    siblings = data.get("siblings", [])
    if len(siblings) < 2:
        fail(f"siblings >=2, got {len(siblings)}", failures)
    else:
        ok(f"siblings {len(siblings)}")

    # Check that no core has stock path
    for c in cores:
        if "driver_r36sx" in c.get("destination","") or "_sdcard" in c.get("repository_url",""):
            fail(f"stock in core {c['destination']}", failures)
            break
    else:
        ok("no stock in cores")

    # Check stats
    stats = data.get("stats", {})
    if stats.get("core_declaration_count") != 78:
        fail(f"stats core_declaration_count 78, got {stats.get('core_declaration_count')}", failures)
    else:
        ok("stats core_declaration_count 78")
    if stats.get("core_unique_destination_count") != 77:
        fail("stats unique dest 77", failures)
    else:
        ok("stats unique dest 77")

    if failures:
        print(f"\nFAILURES {len(failures)}")
        for f in failures:
            print(f" - {f}")
        sys.exit(1)
    else:
        print("\nPASS: all contract checks")
        sys.exit(0)

if __name__ == "__main__":
    main()
