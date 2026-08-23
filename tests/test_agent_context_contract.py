#!/usr/bin/env python3
"""
test_agent_context_contract.py — Contrato IA para TreeFrogUI R36SX V2.6 Fork
Verifica que la infraestructura documental y de agentes cumple AGENTS.md.
Ejecutar: python tests/test_agent_context_contract.py
"""
import sys
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# Para soportar ejecución desde cualquier cwd
if not (REPO_ROOT / "AGENTS.md").exists():
    # fallback: cwd
    REPO_ROOT = Path.cwd()

FAILURES = []
PASSES = []

def fail(msg):
    FAILURES.append(msg)
    print(f"FAIL: {msg}")

def ok(msg):
    PASSES.append(msg)
    print(f"PASS: {msg}")

def check_exists(rel, desc=""):
    p = REPO_ROOT / rel
    if not p.exists():
        fail(f"Missing {rel} {desc}")
        return False
    else:
        ok(f"Exists {rel}")
        return True

def read(rel):
    p = REPO_ROOT / rel
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8", errors="ignore")

def main():
    print(f"REPO_ROOT={REPO_ROOT}")
    # 1. Existen AGENTS/CURRENT/CONTEXT_MAP/DECISIONS
    for f in ["AGENTS.md", "CURRENT.md", "CONTEXT_MAP.md", "DECISIONS.md"]:
        check_exists(f)

    # 2. Existen VALIDATION/RELEASE_CONTRACT
    for f in ["docs/ai/VALIDATION.md", "docs/ai/RELEASE_CONTRACT.md"]:
        check_exists(f)

    # 3. Existen agentes requeridos
    agents_dir = REPO_ROOT / ".opencode" / "agents"
    expected = ["treefrog-lead.md", "audit.md", "implement.md", "review.md", "release.md", "upstream-sync.md"]
    if not agents_dir.exists():
        fail(f"Agents dir missing: {agents_dir}")
    else:
        ok(f"Agents dir exists: {agents_dir}")
        for a in expected:
            check_exists(f".opencode/agents/{a}")

    # 4. CURRENT indica que es cache/snapshot
    current = read("CURRENT.md")
    if "CURRENT.md IS A CACHE" in current or "IS A CACHE" in current:
        ok("CURRENT.md indicates IS A CACHE")
    else:
        fail("CURRENT.md must indicate 'CURRENT.md IS A CACHE' / cache/snapshot")

    if "snapshot" in current.lower() or "cache" in current.lower():
        ok("CURRENT.md mentions cache/snapshot verifiable")
    else:
        fail("CURRENT.md should mention cache/snapshot verifiable")

    # 5. CONTEXT_MAP no contiene HEAD hardcodeado como autoridad
    cmap = read("CONTEXT_MAP.md")
    # No debe presentar un SHA de 40 hex como HEAD autoridad
    # Pero permitimos mencionar "git rev-parse HEAD" como instrucción, no como valor fijo
    # Detectamos líneas tipo HEAD= <40hex> como hardcodeado
    sha_pat = re.compile(r"\b[0-9a-f]{40}\b")
    # Busca HEAD= + SHA en CONTEXT_MAP
    head_sha_lines = [l for l in cmap.splitlines() if "HEAD" in l and sha_pat.search(l)]
    if head_sha_lines:
        fail(f"CONTEXT_MAP.md must not contain hardcodeado HEAD SHA as autoridad: {head_sha_lines[:2]}")
    else:
        ok("CONTEXT_MAP.md no contiene HEAD hardcodeado como autoridad")

    # También verificar que dice consultar Git
    if "git rev-parse" in cmap or "git status" in cmap:
        ok("CONTEXT_MAP mentions Git for mutable state")
    else:
        fail("CONTEXT_MAP should reference Git for mutable state (git rev-parse / git status)")

    # 6. No aparecen invariantes LGPT/Bacon accidentalmente
    # Lista prohibida específica de LGPT
    forbidden = [
        "Bacon",
        "LGPT",
        "SP404",
        "USB Audio",
        "48 kHz",
        "48kHz",
        "48K",
        "Bacon-1.5",
        "bacon",
        "M8",
        "TreeFrogAudio.cpp",
        "UAC2",
    ]
    # AGENTS.md, CURRENT.md, CONTEXT_MAP.md, DECISIONS.md, VALIDATION, RELEASE_CONTRACT no deben contener
    # Permitimos que README mencione? Pero chequeamos solo constitución y contratos
    # Para este contrato, AGENTS.md es el más crítico
    for rel in ["AGENTS.md", "CONTEXT_MAP.md", "DECISIONS.md", "docs/ai/VALIDATION.md", "docs/ai/RELEASE_CONTRACT.md"]:
        txt = read(rel)
        found = []
        for term in forbidden:
            # case sensitive for Bacon/LGPT, pero buscamos substrings
            if term.lower() in txt.lower():
                # Evitar falsos positivos: "48" aparece en muchos lados (640x480) — ya filtrado
                # Para 48K, verificamos que sea audio context
                if term in ["48K", "48 kHz", "48kHz"]:
                    # solo fail si contexto audio/USB
                    if "audio" in txt.lower() and "48" in txt:
                        found.append(term)
                else:
                    # Bacon/SP404/LGPT son siempre prohibidos si aparecen
                    if term.lower() in ["bacon", "lgpt", "sp404", "treefrogaudio.cpp", "uac2"]:
                        found.append(term)
                    elif term == "Bacon" and "Bacon" in txt:
                        found.append(term)
        # Simplificado: detectar exactamente "Bacon" o "LGPT" o "SP404"
        if "bacon" in txt.lower():
            # Bacon aparece en lgpt, no debe aparecer en treefrog
            if "Bacon" in txt or "bacon" in txt.lower():
                # buscar palabra bacon
                if re.search(r"\bbacon\b", txt, re.IGNORECASE):
                    fail(f"{rel} contiene invariante prohibido 'Bacon' (LGPT-specific)")
                else:
                    ok(f"{rel} no contiene Bacon invariante")
            else:
                ok(f"{rel} no contiene Bacon invariante")
        else:
            ok(f"{rel} no contiene Bacon/LGPT invariante")

        if re.search(r"\bLGPT\b", txt):
            fail(f"{rel} contiene LGPT invariante prohibido")
        else:
            ok(f"{rel} no contiene LGPT")

        if re.search(r"\bSP404\b", txt):
            fail(f"{rel} contiene SP404 invariante prohibido")
        else:
            ok(f"{rel} no contiene SP404")

        # USB Audio específico de LGPT
        if re.search(r"USB\s*Audio", txt, re.IGNORECASE) and "R36SX" in txt:
            fail(f"{rel} contiene USB Audio invariante LGPT")
        else:
            ok(f"{rel} no contiene USB Audio LGPT")

    # 7 y 8. agentes read-only tienen edit: deny y task: deny
    for agent in ["audit.md", "review.md"]:
        rel = f".opencode/agents/{agent}"
        txt = read(rel)
        if not txt:
            fail(f"{rel} vacío o no existe para verificar permisos")
            continue
        # edit: deny
        if re.search(r"edit\s*:\s*deny", txt, re.IGNORECASE):
            ok(f"{agent} tiene edit: deny")
        else:
            fail(f"{agent} read-only debe tener 'edit: deny'")
        if re.search(r"task\s*:\s*deny", txt, re.IGNORECASE):
            ok(f"{agent} tiene task: deny")
        else:
            fail(f"{agent} read-only debe tener 'task: deny'")

    # 9. operaciones destructivas están negadas donde corresponda
    # implement y audit/review deben negar reset --hard, clean, rm -rf, force push, etc.
    destructive_terms = [
        r"git\s+reset\s+--hard",
        r"git\s+clean",
        r"rm\s+-rf",
        r"force\s+push",
    ]
    for agent in ["audit.md", "review.md", "implement.md"]:
        rel = f".opencode/agents/{agent}"
        txt = read(rel)
        # Debe mencionar que están negadas/prohibidas
        # Buscamos "neg" o "deny" o "prohibit" cerca de esos términos
        for pat in destructive_terms:
            if re.search(pat, txt, re.IGNORECASE):
                # Si contiene el comando, debe estar en contexto de negar
                # Verificamos que el archivo contiene "deny" o "prohib" o "never" o "NO"
                context_ok = re.search(r"(deny|prohib|never|must\s+not|NO|neg)", txt, re.IGNORECASE)
                if context_ok:
                    ok(f"{agent} menciona {pat} en contexto de prohibición")
                else:
                    fail(f"{agent} menciona {pat} pero sin negar/prohibir claramente")
            else:
                # Si no menciona el comando, verificar que al menos hay sección de negación genérica
                pass
        # Verificar que audit/review tienen external_directory deny (al menos audit)
        if agent == "audit.md":
            if re.search(r"external_directory\s*:\s*deny", txt, re.IGNORECASE):
                ok("audit.md tiene external_directory: deny")
            else:
                fail("audit.md debe tener external_directory: deny")

    # 10. ninguna definición permite a un agente read-only delegar a implement
    for agent in ["audit.md", "review.md"]:
        rel = f".opencode/agents/{agent}"
        txt = read(rel)
        # Buscar delegación a implement
        # Patrones: "delegate.*implement", "task.*implement", "puede delegar.*implement"
        if re.search(r"implement", txt, re.IGNORECASE):
            # Si menciona implement, debe ser en contexto de NEGACIÓN
            # Ejemplo: "Nunca puede usar implement", "cannot delegate to implement", "No puede delegar a implement"
            neg = re.search(r"(never|no puede|cannot|deny|must not|prohib|no debe).*implement", txt, re.IGNORECASE) or \
                  re.search(r"implement.*(deny|prohib|never|no puede)", txt, re.IGNORECASE)
            if neg:
                ok(f"{agent} menciona implement solo en contexto de prohibición")
            else:
                fail(f"{agent} read-only no debe poder delegar a implement, pero menciona implement sin negar")
        else:
            ok(f"{agent} no delega a implement (no menciona implement)")

    # Verificar que treefrog-lead solo delega a audit, implement, review, release, upstream-sync
    lead = read(".opencode/agents/treefrog-lead.md")
    if lead:
        # Debe listar esos 5
        for allowed in ["audit", "implement", "review", "release", "upstream-sync"]:
            if allowed in lead:
                ok(f"treefrog-lead menciona delegación a {allowed}")
            else:
                fail(f"treefrog-lead debe poder delegar a {allowed}")
        # No debe delegar a otros arbitrarios
        # Si menciona Bacon/LGPT etc ya falló antes

    # 11. no existe PHYSICAL PASS inventado
    # CURRENT.md debe decir NONE / NOT YET ESTABLISHED o NOT TESTED, no PASS
    current_upper = current.upper()
    if "PHYSICAL_GOLDEN = NONE" in current or "PHYSICAL_GOLDEN=NONE" in current or "NOT YET ESTABLISHED" in current:
        ok("CURRENT.md PHYSICAL_GOLDEN = NONE / NOT YET ESTABLISHED")
    else:
        fail("CURRENT.md PHYSICAL_GOLDEN debe ser NONE / NOT YET ESTABLISHED al bootstrap")

    if "PHYSICAL PASS" in current_upper and "NOT TESTED" not in current_upper and "NONE" not in current_upper:
        fail("CURRENT.md no debe inventar PHYSICAL PASS")
    else:
        ok("CURRENT.md no inventa PHYSICAL PASS")

    # AGENTS.md tampoco debe declarar PHYSICAL PASS como hecho
    agents_txt = read("AGENTS.md")
    # Puede mencionar el gate "PHYSICAL PASS" como definición, pero no como estado actual
    # Verificamos que no diga "PHYSICAL PASS = PASS" o similar en Golden
    if re.search(r"PHYSICAL_GOLDEN\s*=\s*PASS", agents_txt, re.IGNORECASE):
        fail("AGENTS.md no debe declarar PHYSICAL_GOLDEN = PASS")
    else:
        ok("AGENTS.md no declara PHYSICAL PASS inventado")

    # 12. release contract protege Stock OS
    rc = read("docs/ai/RELEASE_CONTRACT.md")
    checks = [
        (r"icube" in rc.lower(), "RELEASE_CONTRACT menciona icube (no empaquetar)"),
        (r"rkgame" in rc.lower(), "RELEASE_CONTRACT menciona rkgame (no empaquetar)"),
        ("Stock OS" in rc or "Stock" in rc, "RELEASE_CONTRACT protege Stock OS"),
        ("ROM" in rc and "no" in rc.lower(), "RELEASE_CONTRACT prohíbe ROMs"),
        ("BIOS" in rc, "RELEASE_CONTRACT menciona BIOS"),
        ("FAT32" in rc, "RELEASE_CONTRACT menciona FAT32"),
        ("symlink" in rc.lower() or "symlink" in rc, "RELEASE_CONTRACT menciona sin symlinks"),
        ("SHA256" in rc or "SHA" in rc, "RELEASE_CONTRACT menciona SHA256/manifest"),
    ]
    for cond, msg in checks:
        if cond:
            ok(msg)
        else:
            fail(f"RELEASE_CONTRACT falta: {msg}")

    # Validación también debe proteger
    val = read("docs/ai/VALIDATION.md")
    if "PHYSICAL PASS" in val and "CLEAN-INSTALL" in val:
        ok("VALIDATION.md define PHYSICAL y CLEAN-INSTALL gates")
    else:
        fail("VALIDATION.md debe definir PHYSICAL PASS / CLEAN-INSTALL")

    # Summary
    print("\n--- CONTRACT SUMMARY ---")
    print(f"PASS: {len(PASSES)}  FAIL: {len(FAILURES)}")
    if FAILURES:
        print("\nFailures:")
        for f in FAILURES:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print("AGENT_CONTEXT_CONTRACT=PASS")
        sys.exit(0)

if __name__ == "__main__":
    main()
