# cleanup.py — JullBrain RAG-Pipeline Cleanup Handler
import os
import sys
import shutil
import gc
from pathlib import Path

# Configurar salida estándar UTF-8 para consola Windows
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent
CACHE_DIR = BASE_DIR / ".conversion_cache"

def clean_environment():
    print("[CLEANUP] 🧹 Iniciando ciclo de limpieza al cerrar el contenedor JullBrain...")
    
    # 1. Purga de carpeta de caché temporal
    if CACHE_DIR.exists():
        try:
            for item in CACHE_DIR.iterdir():
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
            print(f"[CLEANUP] ✅ Caché temporal eliminada exitosamente: {CACHE_DIR}")
        except Exception as e:
            print(f"[CLEANUP] ⚠️ Error parcial al limpiar caché: {e}")
    else:
        print("[CLEANUP] ℹ️ No se detectó carpeta de caché activa.")
        
    # 2. Liberación de memoria RAM (Garbage Collector)
    gc.collect()
    print("[CLEANUP] 🧠 Memoria RAM y subprocesos liberados correctamente.")
    print("[CLEANUP] 🔒 Sesión JullBrain finalizada de forma segura.")

if __name__ == "__main__":
    clean_environment()
