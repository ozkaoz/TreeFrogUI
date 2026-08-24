# MULTIREPO_COORDINATION.md — TreeFrogUI Workspace Coordination

**Protocol:** `TREEFROGUI_AGENT_PROTOCOL=1`
**Parent:** `ozkaoz/treefrog-ui-r36sx` (`/mnt/d/R36SX/treefrog-ui-r36sx`, WSL `~/sf3000-work/treefrog-ui-r36sx-build` mirror)
**Canonical env:** WSL Ubuntu, `~/sf3000-work` (`D:\R36SX` → `/mnt/d/R36SX`)

> This is the canonical cross-repo coordination contract. Do not duplicate entire `AGENTS.md` files here. Local `AGENTS.md` in each active repo must remain concise and reference this doc.

---

## 1. Development units

| Unit | Repository | Path (preferred) | Actual discovered (2026-08-24) | Role | Fork | Upstream |
|------|------------|------------------|--------------------------------|------|------|----------|
| **parent** | `treefrog-ui` | `/mnt/d/R36SX/treefrog-ui-r36sx` | `r36sx-v2.6-dev 76a6dca` `origin ozkaoz/treefrog-ui-r36sx` `upstream tzubertowski/treefrog-ui` `AGENTS.md:YES` | **INTEGRATION (B)** | `ozkaoz/treefrog-ui-r36sx` | `tzubertowski/treefrog-ui` |
| **FrogUI** | `FrogUI` | `~/sf3000-work/FrogUI` | `FrogUI-c0ff79f` `feature/fn-button-mapping-v1015 b1a9799` `origin tzubertowski/FrogUI` (no fork clone at preferred path; fork `ozkaoz/FrogUI` exists `2f41ace` but not cloned as `~/sf3000-work/FrogUI`) — `AGENTS.md:NO` (to be created) | **ACTIVE (A)** | `ozkaoz/FrogUI` (`2f41ace`) | `tzubertowski/FrogUI` (`15ea12b` submodule pin) |
| **picoarch** | `TreeFrogUI_picoarch` | `~/sf3000-work/TreeFrogUI_picoarch` | `~/sf3000-work/picoarch` `r36sx f8ff5ba` `origin tzubertowski` (upstream clone, not fork) + `~/sf3000-work/TreeFrogUI_picoarch-fn` `feature/fn-button-mapping b8f11f5` `origin ozkaoz` + `/mnt/d/R36SX/TreeFrogUI_picoarch` `feature/fn-button-mapping 543699b` `origin ozkaoz` `upstream tzubertowski` `AGENTS.md:NO` | **ACTIVE (A)** | `ozkaoz/TreeFrogUI_picoarch` (`e98af36`) | `tzubertowski/TreeFrogUI_picoarch` (`f8ff5ba`/`e98af36`) |
| **pcsx4all** | `TreeFrogUI_pcsx4all` | `~/sf3000-work/TreeFrogUI_pcsx4all` | **NOT FOUND** — `ozkaoz/TreeFrogUI_pcsx4all` `Repository not found`, no sibling clone | **DEPENDENCY (C)** | — | `tzubertowski/TreeFrogUI_pcsx4all` |
| **cores** | 78 libretro cores | `cores/` (populated by `clone_cores.sh`) | `cores/` gitignored, 77 unique, `deps/treefrog-v1.0.15.lock.json` | **DEPENDENCY (C)** | — | `libretro/*` + 9 `tzubertowski/*` forks |
| **toolchain** | `sf3000toolchain` | `~/sf3000-work/sf3000toolchain` | `mips-mti-linux-gnu-gcc 6.3.0` `sf3000_toolchain_v0.1` | **VENDOR (D)** | `game-de-it/sf3000` | — |

**Discovery:** `~/sf3000-work` contains 8 `FrogUI-*` variants, 3 `Pico-*` variants, `picoarch` upstream clone, `TreeFrogUI_picoarch-fn` fork, `treefrog-ui-r36sx-build` mirror; `/mnt/d/R36SX` contains `treefrog-ui-r36sx` parent and `TreeFrogUI_picoarch` fork (dirty 182). No `~/sf3000-work/FrogUI` fork clone at preferred path — must be created for `FROGUI_DEVELOPMENT_PATH`.

**Classification:**

```
ACTIVE_SOURCE_REPOS= FrogUI, TreeFrogUI_picoarch
INTEGRATION_REPOS= treefrog-ui-r36sx
DEPENDENCY_REPOS= TreeFrogUI_pcsx4all, libretro cores, picoarch upstream (when not fork)
VENDOR_REPOS= sf3000toolchain, stock SD dumps, driver blobs
```

---

## 2. Responsibilities

**Parent `treefrog-ui-r36sx` (integration):**
- Cross-component payload assembly (`build_release.sh` → `release/latest/release` + `install_first/<dev>`)
- Release versioning, `pack_release.sh`/`select_release_base.sh`/`publish_release.sh`, `update.zip` delta
- `sdcard/` staging (`picoarch`/`driver_*.so`/`frogui/settings.txt`)
- Project state (`docs/PROJECT_STATE.md`), coordination (`docs/ai/MULTIREPO_COORDINATION.md`), `docs/RELEASING.md`, `docs/ai/RELEASE_CONTRACT.md`
- Upstream coordination across forks, `WORKSPACE_DOCTOR`

**FrogUI (frontend):**
- Menus, navigation, settings, recents, theme, carousel, box art, `frogui/input.c` (cubevol shm), `frogui_libretro.so` artifact
- `FROGUI_SUBMODULE_CHANGED=NO` in parent — parent submodule is integration reference only; feature dev in `~/sf3000-work/FrogUI` fork

**picoarch (launcher/runtime):**
- `picoarch`/`picoarch_hi` (normal vs high dynarec for `gpsp`/`pcsx`), platform input (`cubevol → /tmp/joy_key` → RetroPad), audio ALSA, `TF_DRIVER`/`TF_PANEL_*` via `/tmp/tfdevice.env`, `zhijack.sh` template + device hardcoding, `driver_r36sx` SIGBUS fallback, `TF_FORCE_SW` watchdog
- Preserve unrelated hotkeys, no invented libretro IDs, no `PHYSICAL PASS` without hardware

**pcsx4all (when ACTIVE):**
- Standalone PS1 core, `ps1` folder, PCSX4ALL standalone binary — currently **C** (no fork clone, no local AGENTS.md)

Do not invent responsibilities beyond source (`frogui/*.c`, `picoarch/*.c`, `hijack/zhijack.tpl.sh`, `build_all.sh`, `clone_cores.sh`).

---

## 3. Cross-repository feature workflow

```
FEATURE REQUEST
  ↓ identify affected repos (parent / FrogUI / picoarch / pcsx4all)
  ↓ verify baseline in EACH repo: git status, git rev-parse HEAD, git remote -v, git submodule status (parent)
  ↓ create separate feature branches/worktrees (never cross-repo single branch)
       parent:  git worktree add ../treefrog-ui-r36sx-feat -b feature/r36sx-foo r36sx-v2.6-dev
       FrogUI:  git -C ~/sf3000-work/FrogUI checkout -b feature/r36sx-foo 15ea12b
       picoarch: git -C ~/sf3000-work/TreeFrogUI_picoarch checkout -b feature/r36sx-foo f8ff5ba
  ↓ implement smallest changes (ONE agent + ONE repo + ONE worktree = write owner)
  ↓ build each component:
       FrogUI:  make -C ~/sf3000-work/FrogUI -f Makefile.sf3000 frogui_libretro.so (or frogui/build_libretro.sh)
       picoarch: (cd ~/sf3000-work/TreeFrogUI_picoarch && sh build_sf3000.sh) → picoarch/picoarch_hi
       parent:  ./clone_cores.sh (if needed) && ./build_all.sh → build/*.so ; sh hijack/build_tfhijack.sh
  ↓ host/static regression:
       FrogUI:  (repo-local tests if any) ; parent: python tests/test_agent_context_contract.py ; python scripts/agent_preflight.py
       picoarch: (host tests if any)
       parent:  ./tests/test_release_base_selection.sh ; python tests/test_dependency_lock.py ; ./tools/dev-doctor.sh ; ./tools/workspace-doctor.sh
  ↓ assemble parent integration payload: ./build_release.sh → release/latest/release (check 640×480 fbwrite, driver_r36sx.so, kill -STOP icube)
  ↓ hash artifacts: sha256sum release/latest/release/cubegm/cores/frogui_libretro.so release/latest/release/cubegm/picoarch
  ↓ STOP FOR HUMAN HARDWARE TEST (R36SX V2.6, FAT32, backup+SHA, install_first/r36sx, log.txt opt-in)
  ↓ record physical result: docs/checkpoints/<feature>.md (FEATURE, COMPONENTS, BASELINES, ARTIFACT_SHA256, TEST_MATRIX, USER_OBSERVATIONS, PASS/FAIL, DATE)
  ↓ commit separately in each repo (focused, no cross-repo giant commit, git commit = ask)
  ↓ push separately to forks (git push origin feature/r36sx-foo, verify SHA, no force push after review)
  ↓ open/link upstream PRs (parent→tzubertowski/treefrog-ui, FrogUI→tzubertowski/FrogUI, picoarch→tzubertowski/TreeFrogUI_picoarch, link Related PRs)
  ↓ only then update integration state (docs/PROJECT_STATE.md) if required
```

**Critical rule:** `ONE REPOSITORY ≠ ONE GIANT CROSS-REPO COMMIT`. Each Git history is independent. Never manufacture a parent commit merely to represent a child change.

---

## 4. Agent handoff contract

Every agent completing substantial work must report:

```
WORKSPACE= ~/sf3000-work or /mnt/d/R36SX
REPOSITORY= treefrog-ui-r36sx | FrogUI | TreeFrogUI_picoarch
BRANCH= feature/r36sx-foo
BASE_HEAD= 15ea12b (or 27f3bf3)
CURRENT_HEAD= b1a9799
WORKTREE_DIRTY= YES/NO (git status --porcelain count)

TASK= Add FN input
CHANGE_CLASS= C (FrogUI) / C (picoarch) / D (parent integration)

FILES_CHANGED= frogui/input.c:12, frogui/input.h:4
FILES_ADDED= docs/checkpoints/fn.md
FILES_DELETED= (none)

BUILD_RESULT= FrogUI PASS (make sf3000), picoarch PASS, parent BUILD PASS
STATIC_TEST_RESULT= PASS (test_agent_context_contract.py)
HOST_TEST_RESULT= PASS (test_release_base_selection.sh, dev-doctor)

PHYSICAL_TEST_REQUIRED= YES (hijack/input/driver)
PHYSICAL_TEST_RESULT= UNTESTED (until user reports R36SX V2.6 observation)

ARTIFACTS= release/latest/release/cubegm/cores/frogui_libretro.so, release/latest/release/cubegm/picoarch
ARTIFACT_SHA256= abc123... (sha256sum)

RELATED_REPOSITORIES= FrogUI (b1a9799), picoarch (b8f11f5), parent (76a6dca)
RELATED_COMMITS= FrogUI:b1a9799, picoarch:b8f11f5
RELATED_PRS= https://github.com/tzubertowski/FrogUI/pull/... , https://github.com/tzubertowski/TreeFrogUI_picoarch/pull/...

FACTS_PROVEN= FrogUI 15ea12b submodule pin, picoarch f8ff5ba, build flags 74kc
INFERENCES= FN mask 0x10000 inferred from input.c
HYPOTHESES= SIGBUS fallback works on v2.7
UNCONFIRMED= upstream PR status

COMMIT_CREATED= NO (await auth)
PUSH_PERFORMED= NO

NEXT_EXACT_ACTION= Human tests R36SX V2.6 clean-install, reports PASS/FAIL with log.txt, then commit/push/PR
```

`PHYSICAL_TEST_RESULT` must be `UNTESTED` until user provides hardware observation (`docs/TESTING.md`, `docs/ai/VALIDATION.md`).

---

## 5. Write ownership

```
WRITE_OWNERSHIP_MODEL=SERIAL_PER_WORKTREE
ONE AGENT + ONE REPOSITORY + ONE WORKTREE = WRITE OWNER (others audit/review read-only)
```

- `treefrog-lead` orchestrates, classifies, selects repo, never edits two repos simultaneously.
- `audit`/`review` are read-only (`edit: deny, task: deny`).
- `implement` edits one explicitly selected repo (`task: audit/review:allow` only).
- `release`/`upstream-sync` never delegate to `implement`.

Avoid circular delegation. At most one `implement` active per worktree.

---

## 6. Baseline verification (before any edit)

In **each** affected repo:

```sh
git status --porcelain
git rev-parse --abbrev-ref HEAD
git rev-parse HEAD && git rev-parse --short HEAD
git remote -v
git submodule status  # parent only
git ls-remote --tags origin  # if network allowed, else UNCONFIRMED
```

Record `BASE_REPOSITORY`, `BASE_BRANCH`, `BASE_SHA`, `UPSTREAM_RELATION`. Never infer baseline from `docs/PROJECT_STATE.md` or `CURRENT.md` alone.

---

## 7. Test coordination matrix

| Change scope | Required checks (derive from repo content, do not invent) |
|--------------|-----------------------------------------------------------|
| **Parent only** (docs, scripts, packaging) | `python tests/test_agent_context_contract.py` + `python scripts/agent_preflight.py` + `bash -n` + `./tests/test_release_base_selection.sh` + `python tests/test_dependency_lock.py` + `./tools/dev-doctor.sh` + `./tools/workspace-doctor.sh` + `7z t` if ZIP |
| **FrogUI** | `make -C FrogUI -f Makefile.sf3000` (or `frogui/build_libretro.sh`) → `frogui_libretro.so` + repo-local tests (if any) + parent `BUILD PASS` + parent `build_release.sh` packaging + `PHYSICAL` if input/UI hardware-facing |
| **picoarch** | `sh build_sf3000.sh` → `picoarch`/`picoarch_hi` + `picoarch` host tests (if any) + normal/high regression + parent integration + `PHYSICAL` |
| **Multi-repo (FrogUI+picoarch+parent)** | Each component tests individually + integration artifact `release/latest/release` + `sha256sum` + full `PHYSICAL` regression matrix (R36SX V2.6, SF family if applicable) |

Derive exact commands from `docs/BUILDING.md`, `FrogUI/AGENTS.md`, `TreeFrogUI_picoarch/AGENTS.md`.

---

## 8. Upstream coordination

- **FrogUI change** → commit in `~/sf3000-work/FrogUI` → push `origin` `ozkaoz/FrogUI` → PR `tzubertowski/FrogUI` (`sf3000` branch)
- **picoarch change** → commit in `~/sf3000-work/TreeFrogUI_picoarch` → push `origin` `ozkaoz/TreeFrogUI_picoarch` → PR `tzubertowski/TreeFrogUI_picoarch` (`r36sx`)
- **Parent change** → commit in `/mnt/d/R36SX/treefrog-ui-r36sx` → push `origin` `ozkaoz/treefrog-ui-r36sx` → PR `tzubertowski/treefrog-ui` (`main` or `r36sx-v2.6-dev` as agreed)
- **No parent commit for child-only change.** Related PRs reference each other (`Related: https://github.com/.../pull/...`).

Provenance confidence: `HIGH` (submodule pin `15ea12b`), `MEDIUM` (branch+cutoff `TreeFrogUI_picoarch` `f8ff5ba`), `LOW` (default HEAD core), `UNCONFIRMED` (no network).

---

## 9. Coordination version

```
TREEFROGUI_AGENT_PROTOCOL=1
```

Parent `AGENTS.md`, this doc, and each child `AGENTS.md` must declare `1`. `tools/workspace-doctor.sh` checks mismatch.

---

## 10. Records

- **Forensic:** `docs/investigations/<topic>.md` (audio hiss, picoarch reconstruction)
- **Checkpoints:** `docs/checkpoints/<feature>.md` (validated hardware)

Checkpoint must contain: `FEATURE=`, `COMPONENTS=`, `BASELINES=`, `ARTIFACT_SHA256=`, `STATIC_TESTS=`, `HOST_TESTS=`, `PHYSICAL_TEST=`, `RELATED_COMMITS=`, `RELATED_PRS=`

Naming: `docs/checkpoints/<YYYY-MM-DD>-<feature>.md` or `docs/investigations/<YYYY-MM-DD>-<topic>.md`.

Do not create empty dirs for appearance.

---

## 11. No runtime changes in this phase

This phase modifies only `AGENTS.md`, `docs/`, `opencode` agents, `tools/*` read-only checkers. `RUNTIME_SOURCE_CHANGED=NO`.

## 12. Upstream feature PR cleanliness

```
UPSTREAM_FEATURE_DIFF_MUST_NOT_INCLUDE_AGENT_INFRASTRUCTURE=YES
```

Agent-infrastructure commits are **FORK/DEVELOPMENT INFRASTRUCTURE** (`AGENTS.md`, `docs/ai/*`, `docs/`, fork-only `tools/`). Runtime feature PRs to upstream must contain **only feature-relevant commits**.

- A feature branch for upstream (`feature/r36sx-<topic>`) must be based on the appropriate upstream target (`upstream/sf3000`, `upstream/r36sx`, `upstream/main`) or cherry-picked so that fork-only infra is **not** in `upstream/<target>...feature_branch`.
- Before every upstream PR, verify:

```sh
git diff --name-status upstream/<target>...HEAD
# must NOT include AGENTS.md, docs/ai/MULTIREPO_COORDINATION.md, docs/UPSTREAM.md infra
# unless that PR intentionally contributes infra upstream
```

- Existing FN feature branches (`FrogUI feature/fn-button-mapping-v1015 b1a9799`, `picoarch feature/fn-button-mapping 543699b`) must remain untouched — do not amend/rebase them to add infra.

Ver: `docs/UPSTREAM.md` §6, `docs/ai/MULTIREPO_COORDINATION.md` §8.

## 13. Infra development vs clean upstream PR

```
INFRA_DEVELOPMENT_MODEL_DOCUMENTED=YES
CLEAN_UPSTREAM_PR_BRANCH_REQUIRED=YES

DEVELOPMENT BASE:  infra/agent-coordination (parent) / infra/agent-rules (FrogUI, picoarch) — contains AGENTS.md
UPSTREAM PR BASE:  upstream/<target> (upstream/sf3000, upstream/r36sx, upstream/main)
```

Agent infrastructure is **available during development** on `infra/*` branches, but **must not enter** runtime feature PRs unless intentionally upstreamed.

**Clean PR preparation:**

1. Verify validated functional commits (BUILD/HOST/PHYSICAL as per §7)
2. Create clean branch from upstream target: `git checkout -b feature/r36sx-foo upstream/<target>`
3. Cherry-pick **only** functional commits: `git cherry-pick <functional-sha>`
4. Do **NOT** cherry-pick `infra/*` agent-infrastructure commit
5. Inspect: `git diff --name-status upstream/<target>...HEAD` — must NOT include `AGENTS.md`, `docs/ai/`, `tools/dev-doctor.sh`, `tools/workspace-doctor.sh` unless PR intentionally contributes infra
6. Reject PR preparation if unrelated infrastructure appears; prohibited unexpected paths in runtime feature PRs: `AGENTS.md`, `docs/ai/`, `tools/dev-doctor.sh`, `tools/workspace-doctor.sh`

Documented once here and linked from `docs/UPSTREAM.md` §7 — do not duplicate.

---

Ver: `docs/PROJECT_STATE.md` `ACTIVE COMPONENTS`, `docs/README.md` hub, `AGENTS.md` Source of Truth, `docs/dev/*` deep refs.
