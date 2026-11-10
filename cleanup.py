"""
Módulo de Limpieza y Mantenimiento del Workspace (cleanup.py)
Permite purgar cachés temporales, artefactos generados en RAG/ y logs de sesión
de forma segura e interactiva sin tocar los datos brutos ni la bóveda de modelos.
"""

from pathlib import Path
import shutil
import os

_BASE_DIR = Path(__file__).resolve().parent


def purge_pycache(root_dir: Path = _BASE_DIR) -> int:
    """Elimina todos los directorios __pycache__ y archivos .pyc."""
    removed = 0
    for path in root_dir.rglob("__pycache__"):
        if path.is_dir() and "docling_env" not in path.parts:
            shutil.rmtree(path, ignore_errors=True)
            removed += 1
    return removed


def purge_generated_artifacts(
    chunks_dir: Path = _BASE_DIR / "RAG" / "normativas_chunks",
    md_dir: Path = _BASE_DIR / "RAG" / "Informacion_docling_rag",
    keep_gitkeep: bool = True,
) -> dict:
    """Limpia los archivos JSON y Markdown generados por el pipeline dentro de RAG/."""
    stats = {"chunks_removed": 0, "md_removed": 0}

    if chunks_dir.exists():
        for f in chunks_dir.iterdir():
            if keep_gitkeep and f.name == ".gitkeep":
                continue
            if f.is_file() and f.suffix == ".json":
                f.unlink()
                stats["chunks_removed"] += 1

    if md_dir.exists():
        for f in md_dir.iterdir():
            if keep_gitkeep and f.name == ".gitkeep":
                continue
            if f.is_file() and f.suffix in (".md", ".json"):
                f.unlink()
                stats["md_removed"] += 1

    return stats


def purge_databases(
    notebooks_dir: Path = _BASE_DIR / "RAG" / "notebooks_db",
    lightrag_dir: Path = _BASE_DIR / "RAG" / "lightrag_db",
) -> dict:
    """Limpia las bases de datos locales de Cuadernos y Grafo LightRAG en RAG/."""
    stats = {"notebooks_cleared": False, "lightrag_cleared": False}
    if notebooks_dir.exists():
        shutil.rmtree(notebooks_dir, ignore_errors=True)
        notebooks_dir.mkdir(parents=True, exist_ok=True)
        stats["notebooks_cleared"] = True

    if lightrag_dir.exists():
        shutil.rmtree(lightrag_dir, ignore_errors=True)
        lightrag_dir.mkdir(parents=True, exist_ok=True)
        stats["lightrag_cleared"] = True

    return stats


if __name__ == "__main__":
    print("=== JullBrain Workspace Cleanup (Núcleo RAG/) ===")
    pyc = purge_pycache()
    print(f"[+] Directorios __pycache__ eliminados: {pyc}")
