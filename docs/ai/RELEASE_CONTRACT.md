# RELEASE_CONTRACT.md — Contrato de Release — TreeFrogUI R36SX V2.6 Fork

**Target:** `R36SX V2.6 — Stock OS`
**Upstream:** `tzubertowski/treefrog-ui`
**Fork:** `ozkaoz/treefrog-ui-r36sx`
**Estado bootstrap:** `RELEASE_GOLDEN = NONE / NOT YET ESTABLISHED` — este documento define el contrato objetivo, no un artefacto ya validado. No implementar empaquetado nuevo durante el bootstrap.

---

## 1. Objetivo

```
R36SX V2.6 Stock OS
+ contenido de UN único ZIP específico del fork copiado a la raíz de la SD
= TreeFrogUI funcional
POST_INSTALL_MANUAL_FIXES=0
```

El ZIP R36SX del fork debe generarse en el futuro combinando el **payload universal** de TreeFrogUI (`cubegm/`, `frogui/`, `roms/`, `MD/dummy.md`) con la **configuración R36SX** que upstream mantiene bajo `install_first/r36sx` (XML `setting.xml`/`config.xml`, `zhijack.sh` generado desde `hijack/zhijack.tpl.sh`, `libemu_tfhijack.so` como `libemu_md.so`, boot logo), de modo que el usuario final **no tenga que realizar dos overlays manuales** (`release/.../ + install_first/r36sx/`). Actual: ese overlay en dos pasos es el contrato upstream vigente — este contrato lo **unifica** para R36SX V2.6.

Importante: **NO implementar** este nuevo empaquetado durante el bootstrap. Solo documentar el contrato.

---

## 2. Partición del ZIP objetivo

```
TreeFrogUI_R36SX_V2.6_<version>.zip  (un único ZIP, FAT32, sin symlinks)
├── cubegm/                 # universal + override hijack (ver §5)
│   ├── cores/              # cores .so + frogui_libretro.so + hijack core
│   ├── lib/ , usr/lib      # si aplica
│   ├── picoarch , picoarch_hi
│   ├── zhijack.sh          # GENERADO por device (640×480, fbwrite, driver_r36sx.so, stop) — NO runtime detection
│   ├── version.txt         # versión instalada
│   └── ...
├── frogui/                 # settings por defecto, fonts, themes
├── roms/                   # estructura vacía / docs
├── MD/dummy.md             # autorun target (.md → libemu_md.so hijack)
├── install_first/          # opcional retenido para trazabilidad, pero NO requerido para instalación manual
│   └── r36sx/              # referencia espejo de lo ya integrado en cubegm/
└── manifest.txt + SHA256SUMS
```

Variante aceptable si se mantiene compatibilidad con `tfupdate.sh`: mantener `install_first/r36sx/` dentro del ZIP como espejo documentado, pero la raíz ya es funcional sin copiarlo manualmente.

---

## 3. Instalación limpia (contrato usuario)

1. Partir del **backup minimal R36SX v2.6 provisto** (ver `install.md#R36SX v2.6`) — formatear SD, restaurar backup oficial.
2. Descomprimir **UN único ZIP** del fork en la **raíz de la SD** (sobrescribir si existe).
3. Sin pasos manuales adicionales, sin copiar `install_first/r36sx` separado, sin editar `setting.xml`.
4. Eyectar seguro, arrancar en R36SX V2.6 → `rkgame → autorun (/mnt/sdcard/MD/dummy.md) → libemu_tfhijack.so → zhijack.sh → picoarch/frogui`.

`POST_INSTALL_MANUAL_FIXES=0`. Cualquier fix manual post-instalación es fallo del contrato.

---

## 4. Mecanismo de arranque preservado (invariante)

```
Stock boot → icube (NO sustituir) → rkgame (NO sustituir)
           → setting.xml <autorun file="/mnt/sdcard/MD/dummy.md" driver="">
           → libemu_md.so (es libemu_tfhijack.so) → retro_load_game() → fork zhijack.sh
```

- `autorun` debe ser **ruta ABSOLUTA** (`/mnt/sdcard/MD/dummy.md`), `driver=""` (rkgame resuelve por extensión).
- `zhijack.sh` es **generado por device** (sin detección runtime salvo bloque `driver_r36sx27` y `encrypted-driver` para SF3000-family; ver `hijack/zhijack.tpl.sh`).
- R36SX política: `kill -STOP icube` + `killall rkgame` (stop, no respawn flaky); display `fbwrite` (no `disp_frame`); driver `driver_r36sx.so` (fallback SIGBUS→`driver_r36sx27.so`).

Cualquier cambio a este mecanismo requiere `DECISIONS.md` explícita.

---

## 5. Reglas de empaquetado

- **Nunca empaquetar:** `icube`, `rkgame`, binarios propietarios del Stock OS, ROMs comerciales, BIOS no redistribuibles, saves/screenshots/logs personales, estado runtime (`/tmp`, `/tmp/joy_key`, FIFO, PID), `log.txt`/`log.txt.prev`.
- **NO depender de ficheros residuales** de instalación anterior — clean install debe funcionar desde SD formateada + backup + ZIP.
- **FAT32 compatible:** sin symlinks, sin hardlinks, sin permisos Unix > FAT, sin nombres con `:` `*` `?`. Todo en `8.3` o LFN FAT-safe.
- **Determinismo:** mismo Git SHA + misma toolchain → mismo ZIP byte-identical (salvo timestamp intencional). `manifest.txt` lista todos los ficheros con SHA256, tamaño y modo esperado; `SHA256SUMS` firma el ZIP.
- **Manifest obligatorio:** `manifest.txt` incluye cada fichero del ZIP (relativo a raíz), SHA256, tamaño. `version.txt` en `cubegm/` refleja `vX.Y.Z[_suffix]`.
- **Sin estado temporal:** ningún `*.log`, `*.tmp`, `build.log`, `bpreplay.zip` personal en el ZIP.
- **Licencias:** respetar `LICENSE.md` (CC BY-NC-SA 4.0 para frogui, BSD/GPL para picoarch, licencias por core). No silenciar atribuciones.
- **Offline updates:** si se mantiene `update.zip` delta, debe cumplir `docs/RELEASING.md` (manifest, SHA, `treefrog-update/manifest.txt`, backup de configs).

---

## 6. Validación de release (gates, ver `docs/ai/VALIDATION.md`)

Un ZIP solo puede declararse estable tras:

```
PACKAGING PASS  (determinismo, manifest, FAT32, sin prohibidos, 7z t, sh -n)
+ CLEAN-INSTALL PHYSICAL PASS (formateo real + backup R36SX v2.6 + ZIP → boot → frogui → launch ROM → save/load)
+ DOWNLOAD-BACK PASS (asset de GitHub descargado de nuevo y SHA256 idéntico al local publicado)
```

Declaraciones `PHYSICAL PASS` requieren evidencia física (foto/log con fecha, device, versión, SHA). Compilar o empaquetar en host no es evidencia física.

---

## 7. Compatibilidad y alcance

- Este contrato es **inicialmente solo para R36SX V2.6**. `R36SX v2.7`, `R36HD`, `SF3000` family y `GB350` quedan fuera de este contrato hasta decisión y validación propias.
- El payload universal sigue siendo compartido; la diferenciación es solo `zhijack.sh`/`driver`/`setting.xml` por device (ver `build_release.sh` arrays `STOCK[]` y `HJ[]`).
- Todo ZIP debe arrancar también en `HOST PASS` staging (si existe emulación host) pero eso no sustituye `PHYSICAL PASS`.

---

## 8. Futuro empaquetado R36SX (no implementar en bootstrap)

Cuando se implemente (post-bootstrap, CLASS D/E):

- Modificar `build_release.sh` / `pack_release.sh` para producir `TreeFrogUI_R36SX_V2.6_<ver>.zip` que ya contenga `install_first/r36sx` fusionado.
- Añadir test `tests/test_release_r36sx_single_zip.sh` (por crear) que verifique `POST_INSTALL_MANUAL_FIXES=0` y compare con upstream `release/latest/release/`.
- Documentar en `release-notes.md` y `install.md` el flujo de un solo ZIP para R36SX V2.6 sin romper el flujo upstream de dos pasos para otras devices.
