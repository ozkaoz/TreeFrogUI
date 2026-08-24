# SD_SAFETY.md — Contrato de Seguridad SD — TreeFrogUI R36SX

> La SD es FAT32, no tiene symlinks, y contiene Stock propietario + datos personales del usuario. **Nunca** asumir drive letter como anchor.

## 1. Reglas canónicas

1. **Identificar por layout, no por letra.** Verificar presencia de `cubegm/`, `frogui/`, `roms/`, `MD/dummy.md`, `cubegm/setting.xml`, `cubegm/cores/` antes de cualquier write. `G:\` puede ser disco del sistema — **DRIVE LETTER IS NOT A TRUST ANCHOR.**
2. **Backup antes de write.** Copiar `setting.xml`, `config.xml`, `filelist.csv`, drivers (`driver_r36sx*.so`), `frogui/settings.txt` + tarjeta completa si es clean-install test. Calcular `SHA256` antes de modificación.
3. **Solo ficheros autorizados.** No escribir recursivo salvo explícito. Lista autorizada por `update-force-include.txt` y release payload (`cubegm/`, `frogui/`, `roms/` scaffold, `MD/`). **Nunca** `icube`/`rkgame`/`driver.so` genérico stock, ROMs comerciales, BIOS no redistribuibles, `saves/`, `roms/*` personal, `screenshots/`.
4. **Hash antes y readback después.** `sha256sum` origen → copia → `sha256sum` destino post-write → comparar.
5. **Preservar rollback.** No borrar backup hasta `DOWNLOAD-BACK PASS` o confirmación humana. `release/artifact/` y `.treefrog-update/backup-<version>/` son rollback.
6. **Nunca auto-format.** `mkfs.vfat`, `format`, `diskpart clean` requieren autorización explícita + backup + confirmación de device path (`lsblk`, `findmnt`).
7. **Nunca auto-fsck/chkdsk.** `fsck.vfat -a`, `chkdsk /f`, `fsck` sin interacción pueden destruir FAT — solo sugerir como paso humano manual si se reporta corrupción.
8. **No reemplazo payload recursivo no autorizado.** `update.zip` es el único mecanismo delta autorizado; no hacer `rsync --delete` sobre SD salvo `scripts/flash_card.sh` / `deploy_device.sh` con `DEV=/dev/sdX` verificado (<64G, no `ROOTSRC`).
9. **Eject seguro es humano.** `sync` + eject del OS + retirada física — no automatizar power-off.

## 2. Mapeo WSL ↔ Windows

| Windows | WSL (DrvFs) | Ejemplo verify |
|---------|-------------|----------------|
| `G:\cubegm` | `/mnt/g/cubegm` | `ls /mnt/g/cubegm/cores/frogui_libretro.so` |
| `H:\frogui` | `/mnt/h/frogui` | `cat /mnt/h/frogui/settings.txt` |
| `D:\R36SX\treefrog-ui-r36sx` | `/mnt/d/R36SX/treefrog-ui-r36sx` | `git status` |

**Drive letter no es anchor:** un `G:` hoy puede ser `H:` mañana. Verificar siempre con:
```sh
lsblk -o NAME,SIZE,MOUNTPOINT,MODEL  # WSL
# o Windows: Get-PSDrive, dir G:\cubegm
ls /mnt/<letter>/cubegm/setting.xml /mnt/<letter>/cubegm/cores/  # debe existir
```

## 3. Procedimiento humano (clean-install / deploy)

```sh
# 1. Identificar
lsblk -bdno SIZE,NAME,MODEL | grep -v sda  # sda es root, evitar
findmnt /mnt/g; ls /mnt/g/cubegm/setting.xml  # layout check
sha256sum /mnt/g/cubegm/setting.xml > /tmp/pre.sha

# 2. Backup
mkdir -p ~/sd-backup/r36sx-$(date +%Y%m%d)
cp -a /mnt/g/cubegm/setting.xml ~/sd-backup/r36sx-.../
sha256sum /mnt/g/cubegm/cores/frogui_libretro.so >> /tmp/pre.sha

# 3. Write autorizado (ej. release)
# Desde WSL, tras ./build_release.sh:
cp -a release/latest/release/cubegm/cores/* /mnt/g/cubegm/cores/  # solo ficheros autorizados
sync; sha256sum /mnt/g/cubegm/cores/frogui_libretro.so  # readback vs /tmp/pre.sha

# 4. Eject humano (Windows: Safely Remove; WSL: sync + umount si aplica)
```

Para offline update: **solo** copiar `update.zip` a raíz (`cp release/latest/update.zip /mnt/g/update.zip`), eject, boot — hijack lo aplica. Ver `docs/RELEASING.md`, `hijack/tfupdate.sh:1`.

## 4. Qué nunca hacer en SD (agentes)

- `mkfs.vfat /dev/sdX`, `format G:`, `diskpart`, `dd if= /dev/sdX` overwrite sin backup.
- `chkdsk G: /f`, `fsck.vfat -a /dev/sdX` automático.
- `rm -rf /mnt/g/*`, `rsync --delete`, `cp -a release/latest/release/* /mnt/g/` sin filtro.
- `cp` a SD desde agente sin `ask` (permiso `cp: ask` en `implement.md` / `release.md`).
- Asumir `G:` es SD sin `ls cubegm/setting.xml`.

## 5. Evidencia y logging

- `log.txt` opt-in (crear vacío en raíz → boot escribe `/mnt/sdcard/log.txt`, prev `log.txt.prev`) — único diagnóstico SD-safe.
- `update.log` en raíz tras `update.zip` — no borrar hasta PASS.
- No escribir logs verbose a SD en modo normal (quita ciclos write).

Ver `AGENTS.md §10`, `docs/TESTING.md` (physical gate), `scripts/flash_card.sh` (usa `lsblk SIZE<64G` guard, `findmnt SOURCE` / check).
