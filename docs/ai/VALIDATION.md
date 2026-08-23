# VALIDATION.md — Gates de Validación — TreeFrogUI R36SX V2.6 Fork

Define los gates A–E (ver `AGENTS.md §5`). Prohíbe etiquetas ambiguas. Requiere evidencia específica por gate. Ningún gate inferior implica uno superior.

---

## Etiquetas exactas

```
STATIC PASS / FAIL
HOST PASS / FAIL
BUILD PASS / FAIL
PACKAGING PASS / FAIL
PHYSICAL PASS / FAIL
CLEAN-INSTALL PHYSICAL PASS / FAIL
DOWNLOAD-BACK PASS / FAIL
```

Prohibido usar simplemente:

```
DONE
VERIFIED
VALIDATED
```

sin especificar qué gate se cumplió y con qué evidencia.

---

## CLASS A — Context / Documentation

**Alcance:** `AGENTS.md`, `CURRENT.md`, `CONTEXT_MAP.md`, `DECISIONS.md`, `.opencode/agents`, `docs`, tests de contrato IA.

**Gate:** `STATIC PASS`.

**Procedimiento:**
```sh
python tests/test_agent_context_contract.py
python scripts/agent_preflight.py [--allow-dirty solo para inspección bootstrap]
git diff --check
# opcional: sh -n scripts/*.sh  (si hubiera shell scripts nuevos)
```

**Evidencia:** salida `PASS` del test de contrato + `PREFLIGHT=PASS` (o `FAIL:DIRTY_WORKTREE` explicado) + diff sin errores whitespace/trail.

**Falla si:** faltan ficheros de contexto, agentes read-only sin `edit: deny`/`task: deny`, `CURRENT.md` no indica `IS A CACHE`, `CONTEXT_MAP.md` contiene HEAD hardcodeado como autoridad, aparecen invariantes específicos de otros proyectos, se declara `PHYSICAL PASS` inventado, o `release contract` no protege Stock OS.

---

## CLASS B — Host tooling / Build infrastructure

**Alcance:** scripts de desarrollo, scripts WSL, toolchain setup, auditorías, empaquetado host-only, CI, reproducibilidad.

**Gate:** `STATIC PASS + HOST PASS`.

**Procedimiento:**
```sh
python tests/test_agent_context_contract.py
python scripts/agent_preflight.py
# tests host existentes:
./tests/test_release_base_selection.sh
# + ejecutar el tool auditado en modo dry-run / host:
python scripts/agent_preflight.py --allow-dirty   # ejemplo
sh -n build_release.sh pack_release.sh publish_release.sh select_release_base.sh hijack/tfupdate.sh hijack/zhijack.tpl.sh
```

**Evidencia:** `STATIC PASS` + ejecución exitosa en host + salida determinista. `BUILD PASS` no requerido si no se compila.

---

## CLASS C — Runtime / UI

**Alcance:** `frogui/`, picoarch integration, frontend, rendering, input, audio runtime, aplicaciones integradas, cores, comportamiento visible.

**Gate mínimo:** `STATIC + BUILD + HOST TESTS + PHYSICAL R36SX`.

**Procedimiento:**
```sh
# 1. STATIC + HOST
python tests/test_agent_context_contract.py
python scripts/agent_preflight.py
./tests/test_release_base_selection.sh

# 2. BUILD (requiere toolchain WSL)
./clone_cores.sh   # si aplica
./build_all.sh     # o make -f Makefile.sf3000 en frogui/
# verificar .so en build/

# 3. PHYSICAL R36SX (hardware real, nunca inferido)
# - SD limpia + backup R36SX v2.6 + payload nuevo
# - boot → frogui visible, navegación, settings, launch ROM, save/load
# - log.txt con boot sequence si se requiere diagnóstico (crear log.txt vacío en SD)
```

**Evidencia:** `BUILD PASS` (compilación cruzada OK) + `PHYSICAL PASS` (foto/video/log fechado con device, versión Git SHA, y comportamiento observado). `HOST PASS` solo no basta.

---

## CLASS D — Device integration / Deployment

**Alcance:** `hijack`, `zhijack`, `autorun`, `setting.xml`, driver selection, `install_first/r36sx`, SD layout, boot behavior.

**Gate:** `PACKAGING PASS + PHYSICAL R36SX`.

**Procedimiento:**
```sh
# 1. PACKAGING PASS
./build_release.sh
# verificar:
#   release/latest/release/cubegm/zhijack.sh contiene TF_DEVICE=R36SX, 640×480, fbwrite, driver_r36sx.so
#   [ "$(grep -c 'killall rkgame' release/latest/release/install_first/r36sx/cubegm/zhijack.sh)" = 1 ]
#   grep -q 'kill -STOP $(pidof icube)' release/latest/release/install_first/r36sx/cubegm/zhijack.sh
#   7z t release/latest/release  (si hubiera ZIP staging)
#   sh -n hijack/zhijack.tpl.sh hijack/tfupdate.sh

# 2. PHYSICAL R36SX — clean install real
#   formatear SD, restaurar backup R36SX v2.6, copiar payload completo (universal + install_first/r36sx)
#   boot → zhijack → picoarch → frogui sin flicker/respawn icube
#   verificar /tmp/tfdevice.env contiene TF_DEVICE=R36SX y TF_DRIVER correcto
#   test de fallback SIGBUS→driver_r36sx27.so solo si aplica (requiere kernel v2.7-class)
```

**Evidencia:** `PACKAGING PASS` (staging correcto, sin symlinks, manifest) + `PHYSICAL PASS` / `CLEAN-INSTALL PHYSICAL PASS` (boot físico documentado). Declarar `R36SX V2.6 #[serial/test-run]`.

---

## CLASS E — Release

**Alcance:** ZIP público, manifests, SHA256, release notes, install contract.

**Gate:** deterministic package + `CLEAN-INSTALL PHYSICAL PASS` + `DOWNLOAD-BACK PASS`.

**Procedimiento:**
```sh
# 1. PACKAGING PASS determinista
./build_release.sh
./pack_release.sh vX.Y.Z_r36sx   # futuro script R36SX single-ZIP (hoy: pack_release.sh upstream)
7z t ./release/latest/TreeFrogUI_*.zip
7z t ./release/latest/update.zip
sh -n build_release.sh pack_release.sh publish_release.sh select_release_base.sh hijack/tfupdate.sh hijack/zhijack.tpl.sh
git diff --check
cat release/latest/release/cubegm/version.txt
cat release/latest/release/manifest.txt 2>/dev/null || 7z e -so release/latest/update.zip treefrog-update/manifest.txt

# 2. CLEAN-INSTALL PHYSICAL PASS
#   - SD formateada FAT32, backup R36SX v2.6, UN único ZIP a raíz, boot, frogui, rom launch
#   - POST_INSTALL_MANUAL_FIXES=0

# 3. DOWNLOAD-BACK PASS (solo tras publish)
#   - gh release download <tag> --pattern "*.zip" --dir /tmp/dl
#   - sha256sum /tmp/dl/*.zip == sha256sum release/latest/*.zip
#   - 7z e -so /tmp/dl/update.zip treefrog-update/manifest.txt == local manifest
```

**Evidencia:** `PACKAGING PASS` + `CLEAN-INSTALL PHYSICAL PASS` fechado + `DOWNLOAD-BACK PASS` con SHAs idénticos (`REMOTE_SHA == LOCAL_SHA`). Sin esto, el release no es `RELEASE_GOLDEN`.

---

## Matriz de gates por clase

| Clase | STATIC | HOST | BUILD | PACKAGING | PHYSICAL | CLEAN-INSTALL | DOWNLOAD-BACK |
|-------|--------|------|-------|-----------|----------|---------------|---------------|
| **A** | **PASS** requerido | — | — | — | — | — | — |
| **B** | PASS | **PASS** | — | — | — | — | — |
| **C** | PASS | PASS | **PASS** | — | **PASS** | — | — |
| **D** | PASS | — | — | **PASS** | **PASS** | (**PASS** para boot) | — |
| **E** | PASS | — | PASS si compila | **PASS** | — | **PASS** | **PASS** |

---

## Reglas generales

- **Nunca inferir `PHYSICAL PASS`.** Solo cuenta si se ejecutó en R36SX V2.6 real con evidencia (log.txt, foto, video, SHA).
- **`BUILD PASS` != `PHYSICAL PASS`.** Compilar en WSL no valida display/input/driver en hardware.
- **`HOST PASS` != `PHYSICAL PASS`.**
- **Un árbol funcional != ZIP completo.** Verificar manifest y `7z t`.
- **Dirty worktree no explicado → `PREFLIGHT_RESULT=FAIL`**, bloquear avance hasta `git status --short --branch` limpio o `--allow-dirty` explícito para inspección.
- Todo gate `FAIL` debe reportar `PREFLIGHT_REASON` o log de test que lo explique.
