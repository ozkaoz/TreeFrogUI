# TESTING.md — Validación — TreeFrogUI R36SX

> Ver `docs/ai/VALIDATION.md` para gates A–E autoritativos. Este doc es guía operativa.

## 1. Taxonomía

| Tipo | Qué valida | Automatizable | Gate |
|------|------------|---------------|------|
| **STATIC TEST** | Contratos docs/agentes, sintaxis `bash -n`, `git diff --check` | **YES** (agente) | `STATIC PASS/FAIL` |
| **HOST TEST** | Tooling host, selección base release, lógica sin hardware | **YES** | `HOST PASS/FAIL` |
| **BUILD TEST** | Compilación cruzada MIPS (`build_all.sh`, `hijack/build_tfhijack.sh`) | **YES** (con toolchain WSL) | `BUILD PASS/FAIL` |
| **RELEASE/PACKAGING TEST** | Staging `release/latest/release`, ZIP, manifest, FAT32, `7z t` | **YES** | `PACKAGING PASS/FAIL` |
| **DEVICE TEST** | Boot hijack, zhijack, driver, picoarch/frogui en device (staging) | **NO** — requiere `PACKAGING PASS` previo | — |
| **PHYSICAL ACCEPTANCE** | R36SX V2.6 real: clean-install, navegación, launch ROM, save/load, hibernación | **NO — humano** | `PHYSICAL PASS`, `CLEAN-INSTALL PHYSICAL PASS`, `DOWNLOAD-BACK PASS` |

**Regla:** Agentes pueden reportar `STATIC/HOST/BUILD/PACKAGING PASS` — **nunca** `PHYSICAL PASS` / `CLEAN-INSTALL PASS` / `DOWNLOAD-BACK PASS` sin observación humana fechada.

## 2. Comandos

### STATIC (siempre)

```sh
python tests/test_agent_context_contract.py   # contrato AGENTS/CURRENT/CONTEXT_MAP/DECISIONS + agents + RELEASE_CONTRACT
python scripts/agent_preflight.py             # PREFLIGHT_RESULT=PASS (o --allow-dirty para inspección)
python tests/test_dependency_lock.py          # lock deps/treefrog-v1.0.15.lock.json schema 1
python scripts/dev/validate_dependency_lock.py
git diff --check                              # whitespace
bash -n build_release.sh pack_release.sh publish_release.sh select_release_base.sh hijack/tfupdate.sh hijack/zhijack.tpl.sh
bash -n tools/dev-doctor.sh
```

### HOST

```sh
./tests/test_release_base_selection.sh        # v1.0.13_b→v1.0.12_c
./tools/dev-doctor.sh                         # PASS/WARN/FAIL (WSL, toolchain, sibling repos)
python scripts/dev/resolve_dependency_lock.py --check  # diverge si upstream movió cutoff
```

### BUILD (requiere WSL + toolchain)

```sh
./clone_cores.sh        # si cores/ vacío
./build_all.sh          # → build/*.so
sh hijack/build_tfhijack.sh  # → libemu_tfhijack.so
make -C frogui -f Makefile.sf3000 frogui_libretro.so
```

Verificar: `ls build/*.so`, `file hijack/libemu_tfhijack.so` (MIPS32r2 EL).

### PACKAGING / RELEASE

```sh
./build_release.sh                            # → release/latest/release/ (requiere STOCK dumps + sdcard/cubegm drivers — ver KNOWN_DEBT)
./pack_release.sh vX.Y.Z_? release/artifact/TreeFrogUI_v*.zip  # + 7z t
7z t ./release/latest/TreeFrogUI_*.zip
7z t ./release/latest/update.zip
7z e -so release/latest/update.zip treefrog-update/manifest.txt
sh -n hijack/zhijack.tpl.sh hijack/tfupdate.sh
grep -c 'killall rkgame' release/latest/release/install_first/r36sx/cubegm/zhijack.sh  # 1 r36sx, 3 SF
```

### DEVICE / PHYSICAL (humano, R36SX V2.6)

No automatizar. Preparar artefacto, entregar a humano:

```sh
# build host (WSL)
./build_release.sh && ./pack_release.sh vX.Y.Z_r36sx
sha256sum release/latest/TreeFrogUI_*.zip release/latest/update.zip > SHA256SUMS
```

Humano en R36SX V2.6:
1. Formatear SD FAT32, restaurar backup minimal v2.6 (`install.md#R36SX`), `sha256sum` backup
2. Copiar UN ZIP (o universal + `install_first/r36sx`) a raíz, eject seguro
3. Boot → Stock → rkgame → zhijack → picoarch/frogui (ver `log.txt` si `log.txt` vacío creado)
4. Test matrix: navegación, settings, recents, carousel, launch `FC/GBA/SFC` ROM, save/load state, auto-save, screenshot, ebook/video si aplica
5. Si update.zip: copiar `update.zip` a raíz → reboot → verificar `update.log` → `cubegm/version.txt` + backup `.treefrog-update/backup-<ver>/`
6. Registrar: `FEATURE= DEVICE=R36SX V2.6 FIRMWARE=v2.6 Minimal ARTIFACT_SHA256= TEST_MATRIX= USER_OBSERVATIONS= PASS/FAIL= DATE=` (foto/log)

`CLEAN-INSTALL PHYSICAL PASS` requiere `POST_INSTALL_MANUAL_FIXES=0`. `DOWNLOAD-BACK PASS` → `gh release download <tag>` + `REMOTE_SHA == LOCAL_SHA`.

## 3. Inventario existente (no inventar nuevos)

| Test | Archivo | Tipo | Uso |
|------|---------|------|-----|
| Agent contract | `tests/test_agent_context_contract.py` | STATIC | `AGENTS/CURRENT/CONTEXT_MAP/DECISIONS` + `audit/review edit:deny` + `RELEASE_CONTRACT` icube/rkgame/FAT32 |
| Preflight | `scripts/agent_preflight.py` | STATIC | BRANCH/HEAD/UPSTREAM/DIRTY/worktree/submodule |
| Dependency lock | `tests/test_dependency_lock.py` + `scripts/dev/validate_dependency_lock.py` | STATIC | lock JSON schema, 77 cores, TOOLCHAIN sha256 |
| Release base | `tests/test_release_base_selection.sh` | HOST | numeric-line selection |
| Offline update | `tests/test_offline_update.sh` | HOST (sim) | delta, checksum, backup, delete protection |
| FN bits | `tests/test_frogui_fn.py` (untracked) | PHYSICAL (unit) | FN 16 mask 0x10000 L3 1 R3 2 — requiere decisión separación |
| Dev doctor | `tools/dev-doctor.sh` | HOST | WSL/toolchain/siblings (nuevo) |

Ver `tests/` y `scripts/dev/` — no crear wrappers redundantes si comandos nativos existen.

## 4. Cuándo parar

- Todo cambio `hijack/zhijack/driver/setting.xml` → `PACKAGING PASS` + **parar** para humano físico (`docs/ai/VALIDATION.md CLASS D`).
- Release ZIP → `PACKAGING` + `CLEAN-INSTALL PHYSICAL` + `DOWNLOAD-BACK` antes de estable (`CLASS E`).
- Si evidencia contradice hipótesis → reparar contexto (`docs/PROJECT_STATE.md`) primero, no encadenar fixes.

## 5. Referencias

- `docs/ai/VALIDATION.md` — gates exactos A–E, matriz PASS/FAIL, reglas `DONE/VERIFIED` prohibidos
- `docs/ai/RELEASE_CONTRACT.md` — ZIP contract, `POST_INSTALL_MANUAL_FIXES=0`
- `docs/HARDWARE.md` — facts device para test matrix
- `docs/SD_SAFETY.md` — SD handling durante tests físicos
