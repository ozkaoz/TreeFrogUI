# Pull Request — TreeFrogUI R36SX V2.6 Fork

## Summary

<!-- One-line: area: what + why. Link related component PRs (FrogUI / picoarch) -->

## Baseline

- **Base tag:** `v1.0.15` (`27f3bf3`) / `r36sx-v2.6-dev` `HEAD=` <!-- `git rev-parse HEAD` -->
- **FrogUI submodule:** `15ea12b` (`sf3000`) <!-- `git submodule status` -->
- **Lock:** `deps/treefrog-v1.0.15.lock.json` `schema 1` <!-- if relevant -->

## Validation

- [ ] `python tests/test_agent_context_contract.py` → PASS
- [ ] `python scripts/agent_preflight.py` → PASS (or `--allow-dirty` explained)
- [ ] `python tests/test_dependency_lock.py` → PASS (if lock touched)
- [ ] `./tests/test_release_base_selection.sh` → PASS (if release)
- [ ] `bash -n <scripts>` → PASS
- [ ] `./tools/dev-doctor.sh` → PASS/WARN (paste `READY_FOR_HOST_DEVELOPMENT`)
- [ ] No generated binaries committed (`build/`, `*.so`, `release/`, `cores/`, `*.o`, `log.txt`)

## Hardware (if CLASS C/D/E)

- [ ] `BUILD PASS` (WSL toolchain 6.3.0) — `build_all.sh` / `hijack/build_tfhijack.sh`
- [ ] `PACKAGING PASS` (`build_release.sh` → `release/latest/release`, `7z t`, no `icube`/`rkgame`, FAT32 no symlinks)
- [ ] **Human** `PHYSICAL TEST REQUIRED?` `YES / NO`
- [ ] **Human** `PHYSICAL PASS` performed on R36SX V2.6 (`FIRMWARE/BASELINE`, `ARTIFACT_SHA256`, `TEST_MATRIX`, `USER_OBSERVATIONS`, `PASS/FAIL`, `DATE` — foto/log)
- [ ] `CLEAN-INSTALL PHYSICAL PASS` (`POST_INSTALL_MANUAL_FIXES=0`)
- [ ] `DOWNLOAD-BACK PASS` (`REMOTE_SHA == LOCAL_SHA`)

## Risk & rollback

- [ ] Focused diff (no unrelated changes)
- [ ] Rollback considered / backup preserved (SD, `release/artifact/`)
- [ ] No `/home/tomaszz` new hardcode (see `docs/BUILDING.md` `PORTABILITY_DEBT`)
- [ ] No `icube`/`rkgame`/`ROMs`/`BIOS` in Git/release

## Related PRs

<!-- Separate repos = separate PRs, link them: FrogUI, picoarch -->

- FrogUI: <!-- https://github.com/tzubertowski/FrogUI/pull/... -->
- picoarch: <!-- https://github.com/tzubertowski/TreeFrogUI_picoarch/pull/... -->

## Checklist (human)

- [ ] `git status --short --branch` clean (or dirty explained)
- [ ] `git diff --check` clean
- [ ] Preserved `origin`/`upstream` remotes, no `force push` after review
