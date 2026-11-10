"""
sincronizar_resultados.py — JullBrain v0.2.0
============================================
Herramienta de sincronización y sellado forense SHA-256 entre:
  1. Entorno local (orquestador_JullBrain.bat / Podman)
  2. Repositorio oficial en GitHub
  3. Despliegue en Oracle Cloud Infrastructure (OCI)

Núcleo único de información: ./RAG/
"""

from __future__ import annotations
import sys
import json
import hashlib
import argparse
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent
RAG_DIR = BASE_DIR / "RAG"
MANIFEST_FILE = RAG_DIR / "manifiesto_forense_sha256.json"


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
            b_res = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True, cwd=str(BASE_DIR))
            info["rama_actual"] = b_res.stdout.strip() or "main"
            c_res = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, cwd=str(BASE_DIR))
            info["commit_hash"] = c_res.stdout.strip()
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
        print(f"❌ Error al sincronizar: {res.stderr.strip()}")
        return False
    except Exception as e:
        print(f"❌ Excepción durante git pull: {e}")
        return False


def generar_manifiesto() -> Dict[str, str]:
    """
    Genera el manifiesto forense SHA-256 de todos los Markdowns y JSONs procesados
    en RAG/Informacion_docling_rag y RAG/normativas_chunks.
    """
    manifiesto: Dict[str, str] = {}
    carpetas = [RAG_DIR / "Informacion_docling_rag", RAG_DIR / "normativas_chunks"]

    print("🔐 Calculando hashes SHA-256 de las normativas jurídicas en ./RAG/...")
    total_archivos = 0
    for c in carpetas:
        if not c.exists():
            continue
        for archivo in sorted(c.rglob("*")):
            if archivo.is_file() and archivo.suffix.lower() in (".md", ".json"):
                rel = str(archivo.relative_to(BASE_DIR)).replace("\\", "/")
                manifiesto[rel] = calcular_sha256(archivo)
                total_archivos += 1

    payload = {
        "_version": "0.2.0",
        "generado_en": datetime.now(timezone.utc).isoformat(),
        "total_normativas": total_archivos,
        "algoritmo": "SHA-256",
        "hashes": manifiesto
    }

    with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    print(f"✅ Manifiesto guardado en: {MANIFEST_FILE}")
    print(f"   Total de archivos sellados: {total_archivos}")
    return manifiesto


def verificar_integridad() -> None:
    """Verifica que los archivos actuales coincidan con los hashes registrados en el manifiesto."""
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

    print(f"🔬 Verificando integridad de {len(hashes)} archivos registrados en ./RAG/...")
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
    """Muestra un panel informativo del estado de sincronización y del núcleo ./RAG/."""
    git_info = obtener_estado_git()
    sep = "=" * 65
    print(sep)
    print("🏛️ JULLBRAIN v0.2.0 — ESTADO DEL NÚCLEO DE CONOCIMIENTO ./RAG/")
    print(sep)
    print(f" • Repositorio Git  : {'✅ Conectado' if git_info['es_repo_git'] else '❌ Desconectado'}")
    print(f" • Rama activa      : {git_info['rama_actual']}")
    print(f" • Commit local     : {git_info['commit_hash']}")
    print(f" • Origen remoto    : {git_info['remote_url']}")
    print(f" • Cambios locales  : {'⚠️ Pendientes de commit' if git_info['cambios_locales'] else '✅ Al día'}")

    pdf_brutos = list((RAG_DIR / "datos_brutos").rglob("*.pdf")) if (RAG_DIR / "datos_brutos").exists() else []
    md_rag = list((RAG_DIR / "Informacion_docling_rag").rglob("*.md")) if (RAG_DIR / "Informacion_docling_rag").exists() else []
    chunks = list((RAG_DIR / "normativas_chunks").rglob("*.json")) if (RAG_DIR / "normativas_chunks").exists() else []
    modelos = list((RAG_DIR / "modelos_ia").rglob("*")) if (RAG_DIR / "modelos_ia").exists() else []
    modelos_files = [m for m in modelos if m.is_file() and m.name != ".gitkeep"]

    print("-" * 65)
    print("CORPUS DOCUMENTAL Y BÓVEDA IA EN ./RAG/:")
    print(f" • Leyes en PDF (RAG/datos_brutos)            : {len(pdf_brutos)} archivos")
    print(f" • Normativas en MD (RAG/Informacion_docling) : {len(md_rag)} archivos")
    print(f" • Chunks JSON (RAG/normativas_chunks)        : {len(chunks)} archivos JSON")
    print(f" • Artefactos en Bóveda IA (RAG/modelos_ia)   : {len(modelos_files)} archivos")
    print(f" • Manifiesto Forense SHA-256                 : {'✅ Generado' if MANIFEST_FILE.exists() else '⚠️ No generado'}")
    print(sep)


def main():
    parser = argparse.ArgumentParser(description="JullBrain — Sincronizador Local ↔ GitHub ↔ Oracle Cloud")
    parser.add_argument("--status", action="store_true", help="Muestra el estado general del núcleo RAG")
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
