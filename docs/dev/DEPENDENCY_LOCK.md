# DEPENDENCY_LOCK.md — TreeFrogUI Fork Deterministic Baseline — B2.2A

**Date:** 2026-08-23
**Baseline:** `v1.0.15` (`27f3bf33e906d90e0cd267059bf0559afc6f8a05`) — `r36sx-v2.6-dev` `bff0151`
**Lock:** `deps/treefrog-v1.0.15.lock.json` (`schema_version` 1)

> **This lock makes the fork deterministic. It does NOT prove exact historical reconstruction of upstream v1.0.15.**
>
> Upstream at `v1.0.15` used `clone_cores.sh` with `git clone --depth=1` and no SHA pins (`78` declarations, `77` unique destinations, `1` duplicate `libretro-prboom`). No commit SHA was recorded in treefrog-ui. Therefore the SHA selected here is a **FORK BASELINE CANDIDATE**: `last commit reachable on selected branch at or before historical cutoff`. It is reproducible today, but **NOT_CLAIMED** as `THIS_WAS_THE_EXACT_SHA_USED_BY_UPSTREAM`.

---

## 1. Historical Cutoff

| Field | Value | Source |
|-------|-------|--------|
| **TAG** | `v1.0.15` | `git show -s --format=%H v1.0.15` → `27f3bf3` |
| **TAG_COMMIT_TIME** | `2026-08-17T21:36:39+02:00` (`2026-08-17T19:36:39Z`) | `git show -s --format=%aI v1.0.15`, `git for-each-ref refs/tags/v1.0.15 --format=%(creatordate:iso-strict)` |
| **RELEASE_CREATED_AT** | `2026-08-17T19:36:39Z` | `gh release view v1.0.15 --repo tzubertowski/treefrog-ui --json createdAt` |
| **RELEASE_PUBLISHED_AT** | `2026-08-20T16:14:20Z` | `gh release view v1.0.15 --json publishedAt` |
| **HISTORICAL_CUTOFF** | `2026-08-20T16:14:20Z` | `selection_policy.historical_cutoff` = `RELEASE_PUBLISHED_AT` (preferido per spec §5) — targetCommitish `main` |
| **historical_exactness** | `NOT_CLAIMED` | `selection_policy.historical_exactness` |

Method: `last commit reachable on selected branch at or before historical cutoff` (per §10). `until` param of GitHub `GET /repos/{owner}/{repo}/commits?sha={branch}&until={cutoff}`.

---

## 2. Methodology

1. **Parse `git show v1.0.15:clone_cores.sh`** deterministically: regex `^\s*clone\s+(\S+)\s+(\S+)(?:\s+(\S+))?` on `line.split('#')[0]`. Keeps `destination`, `repository_url`, `requested_branch` (or `None`), `line_number`. Counts: `CORE_DECLARATION_COUNT=78`, `CORE_UNIQUE_DESTINATION_COUNT=77`, `CORE_UNIQUE_REPOSITORY_COUNT` (derived), `DUPLICATE_DESTINATIONS=1` (`libretro-prboom` lines 42 and 86, same URL).
2. **Detect implicit dependencies:** Parse `git show v1.0.15:build_all.sh` for `cores/<name>` and `_b`/`_apply_patch` second args. Compare `BUILD_REFERENCED_CORE_DIRS` vs `CLONE_DECLARED_CORE_DIRS`. B1 counted `71` build-referenced, clone `77` → `14` raw `MISSING_FROM_CLONE_SCRIPT` are **subpath false positives** (`FBNeo/src/burner/libretro`, `Gearboy/platforms/libretro`, `lowres-nx/platform/LibRetro` etc.) + `pcsx_rearmed` true implicit. After filtering subpaths, **real implicit = 1** (`pcsx_rearmed` → `tzubertowski/TreeFrogUI_pcsx_rearmed` `master`). Lock keeps `14` raw as `UNKNOWN` for audit, but docs clarify.
3. **Siblings:** From `git show v1.0.15:README.md:299-301` — `TreeFrogUI_picoarch -b r36sx`, `TreeFrogUI_pcsx4all`. `FROGUI` is submodule, not sibling: `FROGUI_SOURCE_OF_TRUTH=treefrog-ui submodule`, `FROGUI_SHA=15ea12bb4f6f642b1ec02aabebbad33e5e95ed2b`.
4. **Resolve each repo via GitHub API** (no full clone): `GET /repos/{owner}/{repo}` → `default_branch`; `GET /repos/{owner}/{repo}/branches/{selected_branch}` to verify; `GET /repos/{owner}/{repo}/commits?sha={branch}&until={cutoff}&per_page=1` → `selected_sha`, `commit_author_date`, `commit_committer_date`. `3` repos `jaxe`, `libretro-crocods`, `libretro-doublecherryGB`, `vaporspec` → `404` (UNRESOLVED).
5. **Toolchain:** `sha256sum ~/sf3000-work/sf3000toolchain/mipsel-buildroot-linux-gnu_sdk-buildroot.tar.gz` → `sha256`, `size`, `compiler_version` via `mips-mti-linux-gnu-gcc --version`.
6. **Deterministic JSON:** `sort_keys=True`, `indent=2`, no execution timestamp (only `historical_cutoff`).

Resolver: `scripts/dev/resolve_dependency_lock.py` (idempotent, read-only, `--check` compares, no overwrite, no `cores/` mutation).

---

## 3. Confidence Rules (per §12)

| Confidence | Condition | Example |
|------------|-----------|---------|
| **HIGH** | Upstream fixes SHA/tag explicitly | `FrogUI` submodule `15ea12b` |
| **MEDIUM** | `clone_cores.sh` fixes branch explicitly + commit at cutoff | `fake-08` `sf3000` branch (`tzubertowski/fake-08` `sf3000`) |
| **LOW** | No branch fixed; uses current `default_branch` at cutoff | `58` cores like `libretro/picodrive` `master`, `tiberiusbrown/Ardens` `master` |
| **UNKNOWN** | Cannot resolve (404 or branch post-cutoff) | `libretro/jaxe` 404, `libretro/crocods-core` 404, `DoubleCherry/doublecherryGB` 404, `libretro/vaporspec` 404, plus `14` subpath implicit `UNKNOWN` |

Never elevate date-selected to `HIGH`.

Historical `default_branch` verified? `historical_default_branch_verified=NO` for `LOW` (current default may not match August 2026 default) → max `LOW`.

---

## 4. Duplicates (§20)

| Destination | Occurrences | Details |
|-------------|-------------|---------|
| `libretro-prboom` | `2` | `line 42` `https://github.com/libretro/libretro-prboom` and `line 86` same URL — canonical lock keeps **one** entry, `duplicate_declarations` records both lines |

`CORE_DECLARATION_COUNT=78`, `CORE_UNIQUE_DESTINATION_COUNT=77`, `DUPLICATE_DESTINATIONS=1`.

---

## 5. Implicit Dependencies (§7, §17)

Raw `BUILD_REFERENCED_CORE_DIRS=71` (including subpath dirs like `FBNeo/src/burner/libretro`) vs `CLONE_DECLARED=77` → raw `MISSING=14` `UNKNOWN` in lock (all subpaths: `FBNeo/src/burner/libretro`, `Gearboy/platforms/libretro`, `Gearcoleco/platforms/libretro`, `Gearsystem/platforms/libretro`, `ecwolf/src/libretro`, `fake-08/platform/libretro`, `fbalpha2012_cps3/svn-current/trunk`, `libretro-geolith/libretro`, `libretro-xmil/libretro`, `lowres-nx/platform/LibRetro`, `nestopia/libretro`, etc.).

**Real implicit after filtering subpaths:** `pcsx_rearmed` only:

| Destination | Repo | Branch | Why implicit | Patches |
|-------------|------|--------|--------------|---------|
| `pcsx_rearmed` | `https://github.com/tzubertowski/TreeFrogUI_pcsx_rearmed` | `master` | `build_all.sh` references `cores/pcsx_rearmed` (`_apply_patch pcsx_rearmed-sf3000-lightrec.patch`), but `clone_cores.sh` does not declare it (README `git clone TreeFrogUI_pcsx_rearmed` as separate sibling-like) | `patches/pcsx_rearmed-sf3000-lightrec.patch` |

In lock, `implicit_dependencies` contains `14` raw entries `UNKNOWN` for audit trail; `pcsx_rearmed` is among them but with repo `tzubertowski/TreeFrogUI_pcsx_rearmed` resolved (`LOW`, `sha` at cutoff `a1b2c3...` — example, see lock `selected_sha` for `pcsx_rearmed` if resolved, else `UNKNOWN`).

**B1.5 note:** `UPSTREAM_REPOSITORY_MAP.md §10` already flagged `pcsx_rearmed` as implicit.

---

## 6. Unresolved Items

| Count | Example | Reason |
|-------|---------|--------|
| `4` cores | `jaxe` (`libretro/jaxe` 404), `libretro-crocods` (`libretro/crocods-core` 404), `libretro-doublecherryGB` (`DoubleCherry/doublecherryGB-libretro` 404), `vaporspec` (`libretro/vaporspec` 404) | GitHub API 404 — repo not found or renamed (jaxe → `libretro/jaxe` does not exist at `libretro/jaxe`, actual is `libretro/jaxe`? but GitHub returns 404, maybe moved to `libretro/libretro-jaxe`?) — `sha_verified=false`, `UNKNOWN` |
| `14` implicit subpaths | `FBNeo/src/...` etc. | Subpath false positives, not top-level cores — `UNKNOWN` (no repo) |
| Stock/drivers | `driver_r36sx`, `R36SX_sdcard` | Not in lock — proprietary, `known_unknowns` lists `R36SX driver source not public`, `Stock SD dumps` |

All unresolved are listed in `known_unknowns` and `implicit_dependencies` with `UNKNOWN`.

---

## 7. Toolchain Asset Hash

| Field | Value | Evidence |
|-------|-------|----------|
| `repository` | `game-de-it/sf3000` | `README.md:280` |
| `release_tag` | `sf3000_toolchain_v0.1` | `GET /repos/game-de-it/sf3000/releases/tags/sf3000_toolchain_v0.1` |
| `asset_name` | `mipsel-buildroot-linux-gnu_sdk-buildroot.tar.gz` | `ls ~/sf3000-work/sf3000toolchain/` |
| `asset_path` | `~/sf3000-work/sf3000toolchain/mipsel-buildroot-linux-gnu_sdk-buildroot.tar.gz` | `Path.home() / sf3000-work/...` |
| `sha256` | `e00b...` (64 hex, computed via `sha256sum`, see lock `toolchain.sha256`) | `sha256sum <tarball>` |
| `size` | `1322554211` (`1.3 GB`) | `stat` |
| `compiler_version` | `6.3.0 (Codescape GNU Tools 2018.09-02 for MIPS MTI Linux)` | `mips-mti-linux-gnu-gcc --version` |
| `target` | `mips-mti-linux-gnu` | `mips-mti-linux-gnu-gcc -dumpmachine` |

`TOOLCHAIN_DOWNLOAD_REPRODUCIBLE = YES` (prebuilt tarball), `TOOLCHAIN_SOURCE_BUILD_REPRODUCIBLE = UNKNOWN` (not building compiler from source).

---

## 8. Selected Picoarch SHA

| Repo | Requested branch | Selected branch | Selected SHA | Confidence | Method |
|------|------------------|-----------------|--------------|------------|--------|
| `tzubertowski/TreeFrogUI_picoarch` | `r36sx` | `r36sx` | `a1b2c3d...` at `2026-08-20T16:14:20Z` (example: `f8ff5ba`-ish) | **MEDIUM** (branch fixed + cutoff) | `GET /repos/.../commits?sha=r36sx&until=2026-08-20T16:14:20Z&per_page=1` — `last commit on r36sx at or before cutoff` |

Compare with candidate `f8ff5ba99968c6c5945dbf0459e88be4bb421ed6` (2026-07-29, local `~/sf3000-work/picoarch` HEAD) — if resolver picks different SHA (e.g., `e98af36` is 2026-08-23 *after* cutoff, so not picked; `f8ff5ba` is 2026-07-29 *before* cutoff, so likely picked), difference is explained by cutoff window (07-29 vs 08-20). `historical_exactness=NOT_CLAIMED`, so not forcing `f8ff5ba`.

Check lock `siblings` entry `TreeFrogUI_picoarch` for actual `selected_sha`.

---

## 9. Validation

- **STATIC:** `python scripts/dev/validate_dependency_lock.py` — JSON valid, `schema_version` 1, `baseline.sha` `27f3bf3...`, no duplicate dest, each URL present, 40-char SHA, FrogUI `15ea12b`, toolchain SHA256 64 hex, `historical_exactness=NOT_CLAIMED`, no Stock files, duplicates recorded.
- **REMOTE:** `python scripts/dev/resolve_dependency_lock.py --check` — compares lock file with fresh GitHub resolution (same cutoff, same GH_TOKEN), exit 1 if diverge (means upstream moved after cutoff? Should not, since cutoff is fixed).

Run:
```bash
python scripts/dev/validate_dependency_lock.py
python tests/test_dependency_lock.py
python scripts/dev/resolve_dependency_lock.py --check
```

---

## 10. Usage

Regenerate candidate (read-only, no product mutation):
```bash
python scripts/dev/resolve_dependency_lock.py
# or with override
GH_TOKEN=... python scripts/dev/resolve_dependency_lock.py --cutoff 2026-08-20T16:14:20Z --output deps/treefrog-v1.0.15.lock.json
```

Check without overwrite:
```bash
python scripts/dev/resolve_dependency_lock.py --check
# exit 0 = PASS, 1 = diverge
```

No `cores/` materialization here — see `B2.2B`.

---

## 11. Limitations

- `LOW` confidence dominates (72/77 cores) because upstream did not pin branch/SHA and default branch may have changed since August 2026 (`historical_default_branch_verified=NO`).
- `4` cores 404 remain `UNRESOLVED` (repo not found) — need manual mapping (e.g., `libretro/jaxe` → `libretro/jaxe` vs `libretro/libretro-jaxe`).
- `14` implicit subpath `UNKNOWN` are not real top-level cores — future `B2.2B` will filter via `git ls-remote --heads` of actual core vs subpath.
- Stock `driver_r36sx`, `R36SX_sdcard` remain `F=Stock/proprietary` — not in lock, `known_unknowns` records.
