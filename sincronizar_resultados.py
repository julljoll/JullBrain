"""
sincronizar_resultados.py — JullBrain V3.0
==========================================
Herramienta de sincronización y trazabilidad forense entre:
  1. Entorno local Windows (orquestador .bat)
  2. Repositorio oficial en GitHub
  3. Google Colab & Google Drive

Roles aplicados:
  - R2: Código funcional, robusto y multiplataforma.
  - R7: Integridad documental, sellado SHA-256, principio de no alteración.

Uso:
  python sincronizar_resultados.py --status
  python sincronizar_resultados.py --pull
  python sincronizar_resultados.py --manifiesto
  python sincronizar_resultados.py --verificar
"""

from __future__ import annotations
import sys
import os
import json
import hashlib
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Reconfigurar codificación UTF-8
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent
MANIFEST_FILE = BASE_DIR / "manifiesto_forense_sha256.json"


def calcular_sha256(archivo: Path) -> str:
    """Calcula el hash criptográfico SHA-256 de un archivo en bloques de 64 KB."""
    h = hashlib.sha256()
    with open(archivo, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def obtener_estado_git() -> Dict[str, Any]:
    """Obtiene información sobre el estado del repositorio git local y remoto."""
    info: Dict[str, Any] = {
        "es_repo_git": False,
        "rama_actual": "N/A",
        "commit_hash": "N/A",
        "cambios_locales": False,
        "remote_url": "N/A"
    }
    try:
        res = subprocess.run(["git", "status", "-s"], capture_output=True, text=True, cwd=str(BASE_DIR))
        if res.returncode == 0:
            info["es_repo_git"] = True
            info["cambios_locales"] = bool(res.stdout.strip())
            
            # Rama actual
            b_res = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True, cwd=str(BASE_DIR))
            info["rama_actual"] = b_res.stdout.strip() or "main"
            
            # Último commit
            c_res = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, cwd=str(BASE_DIR))
            info["commit_hash"] = c_res.stdout.strip()
            
            # URL Remota
            r_res = subprocess.run(["git", "remote", "get-url", "origin"], capture_output=True, text=True, cwd=str(BASE_DIR))
            info["remote_url"] = r_res.stdout.strip()
    except Exception as e:
        info["error"] = str(e)
    return info


def ejecutar_pull_git() -> bool:
    """Realiza git pull origin main para sincronizar el código con GitHub."""
    print("🔄 Conectando con GitHub para descargar actualizaciones...")
    try:
        res = subprocess.run(["git", "pull", "origin", "main"], capture_output=True, text=True, cwd=str(BASE_DIR))
        print(res.stdout.strip())
        if res.returncode == 0:
            print("✅ Sincronización completada con éxito.")
            return True
        else:
            print(f"❌ Error al sincronizar: {res.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ Excepción durante git pull: {e}")
        return False


def generar_manifiesto() -> Dict[str, str]:
    """
    Genera el manifiesto forense SHA-256 de todos los Markdowns procesados
    en normativas_rag y RAG/Informacion_docling_rag.
    """
    manifiesto: Dict[str, str] = {}
    carpetas = [BASE_DIR / "normativas_rag", BASE_DIR / "RAG" / "Informacion_docling_rag"]

    print("🔐 Calculando hashes SHA-256 de las normativas jurídicas transformadas...")
    total_archivos = 0
    for c in carpetas:
        if not c.exists():
            continue
        for md in c.rglob("*.md"):
            rel = str(md.relative_to(BASE_DIR)).replace("\\", "/")
            h = calcular_sha256(md)
            manifiesto[rel] = h
            total_archivos += 1

    payload = {
        "_version": "3.0.0",
        "generado_en": datetime.utcnow().isoformat() + "Z",
        "total_normativas": total_archivos,
        "algoritmo": "SHA-256",
        "hashes": manifiesto
    }

    with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    print(f"✅ Manifiesto guardado en: {MANIFEST_FILE}")
    print(f"   Total de normativas selladas: {total_archivos}")
    return manifiesto


def verificar_integridad() -> None:
    """
    Verifica que los archivos actuales coincidan con los hashes registrados en el manifiesto.
    """
    if not MANIFEST_FILE.exists():
        print("⚠️ No existe manifiesto forense previo. Ejecuta primero con --manifiesto")
        return

    try:
        with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Error al leer el manifiesto: {e}")
        return

    hashes = data.get("hashes", {})
    correctos = 0
    alterados = 0
    faltantes = 0

    print(f"🔬 Verificando integridad de {len(hashes)} archivos registrados...")
    for rel_path, h_esperado in hashes.items():
        p = BASE_DIR / rel_path
        if not p.exists():
            print(f"❌ [FALTANTE] {rel_path}")
            faltantes += 1
            continue

        h_actual = calcular_sha256(p)
        if h_actual == h_esperado:
            correctos += 1
        else:
            print(f"⚠️ [ALTERADO] {rel_path}")
            print(f"   Esperado: {h_esperado}")
            print(f"   Actual  : {h_actual}")
            alterados += 1

    print("\n" + "=" * 60)
    print("RESUMEN DE AUDITORÍA FORENSE:")
    print(f" • Integridad comprobada : {correctos} archivos")
    print(f" • Inconsistencias/Alter : {alterados} archivos")
    print(f" • Faltantes             : {faltantes} archivos")
    if alterados == 0 and faltantes == 0:
        print("✅ CADENA DE CUSTODIA ÍNTEGRA (100% Coincidencia SHA-256)")
    else:
        print("⚠️ SE DETECTARON ANOMALÍAS EN EL CORPUS DOCUMENTAL")
    print("=" * 60)


def mostrar_estado() -> None:
    """Muestra un panel informativo del estado de sincronización y del corpus."""
    git_info = obtener_estado_git()
    sep = "=" * 65
    print(sep)
    print("🏛️ JULLBRAIN V3.0 — ESTADO DEL ECOSISTEMA DE CONOCIMIENTO LEGAL")
    print(sep)
    print(f" • Repositorio Git  : {'✅ Conectado' if git_info['es_repo_git'] else '❌ Desconectado'}")
    print(f" • Rama activa      : {git_info['rama_actual']}")
    print(f" • Commit local     : {git_info['commit_hash']}")
    print(f" • Origen remoto    : {git_info['remote_url']}")
    print(f" • Cambios locales  : {'⚠️ Pendientes de commit' if git_info['cambios_locales'] else '✅ Al día'}")

    # Conteo de archivos
    pdf_brutos = list((BASE_DIR / "RAG" / "datos_brutos").rglob("*.pdf")) if (BASE_DIR / "RAG" / "datos_brutos").exists() else []
    md_rag = list((BASE_DIR / "normativas_rag").rglob("*.md")) if (BASE_DIR / "normativas_rag").exists() else []
    chunks = list((BASE_DIR / "normativas_chunks").rglob("*.json")) if (BASE_DIR / "normativas_chunks").exists() else []

    print("-" * 65)
    print("CORPUS DOCUMENTAL LOCAL:")
    print(f" • Leyes en PDF (datos brutos) : {len(pdf_brutos)} archivos")
    print(f" • Normativas en Markdown RAG  : {len(md_rag)} archivos")
    print(f" • Chunks Atómicos por Art.   : {len(chunks)} archivos JSON")
    print(f" • Manifiesto Forense SHA-256 : {'✅ Generado' if MANIFEST_FILE.exists() else '⚠️ No generado'}")
    print(sep)


def main():
    parser = argparse.ArgumentParser(description="JullBrain — Sincronizador Local ↔ GitHub ↔ Google Colab")
    parser.add_argument("--status", action="store_true", help="Muestra el estado general de sincronización y corpus")
    parser.add_argument("--pull", action="store_true", help="Descarga las últimas actualizaciones desde GitHub")
    parser.add_argument("--manifiesto", action="store_true", help="Genera el manifiesto forense criptográfico SHA-256")
    parser.add_argument("--verificar", action="store_true", help="Verifica la integridad de los archivos contra el manifiesto")

    args = parser.parse_args()

    if args.pull:
        ejecutar_pull_git()
    elif args.manifiesto:
        generar_manifiesto()
    elif args.verificar:
        verificar_integridad()
    else:
        mostrar_estado()


if __name__ == "__main__":
    main()
