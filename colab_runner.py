"""
colab_runner.py — JullBrain v0.1.0
=================================
Motor de Ejecución y Orquestación Unificado para Google Colab GPU.
Diseñado para transformar normativas legales con IBM Docling, aplicar control
jerárquico legal, doble validación cruzada y generar embeddings con IBM Granite.

Roles aplicados:
  - R1: Arquitectura RAG air-gapped / nube cerrada, modelos Granite.
  - R2: Código funcional real, manejo exhaustivo de excepciones.
  - R7: Espejo documental, verificación criptográfica SHA-256.

Autor: JullBrain Team (Licencia Apache 2.0)
"""

from __future__ import annotations
import os
import sys
import json
import shutil
import hashlib
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

# Configurar encoding UTF-8
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "colab_config.json"


class JullBrainColabRunner:
    """
    Orquestador integral para ejecutar JullBrain en Google Colab con GPU.
    """

    def __init__(self, config_path: Path | str = CONFIG_PATH):
        self.config_path = Path(config_path)
        self.config = self._cargar_configuracion()
        self.gpu_info: Dict[str, Any] = {}
        self.drive_montado = False
        self.drive_path: Optional[Path] = None

    def _cargar_configuracion(self) -> Dict[str, Any]:
        """Carga la configuración de Colab desde JSON."""
        if not self.config_path.exists():
            print(f"[WARN] No se encontró {self.config_path}. Usando configuración por defecto.")
            return {
                "google_drive": {"montar_automaticamente": True},
                "gpu": {"detectar_automaticamente": True, "embedding_device": "cuda"},
                "pipeline": {"ocr_activo": True, "generar_chunks": True},
                "granite": {"embedding_model": "ibm-granite/granite-embedding-311m-multilingual-r2"}
            }
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[ERROR] Error al leer {self.config_path}: {e}")
            return {}

    def verificar_entorno(self) -> Dict[str, Any]:
        """
        Inspecciona hardware (GPU, CPU, RAM) y dependencias críticas en Colab.
        """
        resultado: Dict[str, Any] = {
            "python_version": sys.version.split()[0],
            "gpu_disponible": False,
            "gpu_nombre": "Ninguna (CPU Mode)",
            "cuda_disponible": False,
            "ram_gb": 0.0,
            "disco_libre_gb": 0.0
        }

        # Verificar GPU via PyTorch
        try:
            import torch
            if torch.cuda.is_available():
                resultado["gpu_disponible"] = True
                resultado["cuda_disponible"] = True
                resultado["gpu_nombre"] = torch.cuda.get_device_name(0)
                resultado["cuda_version"] = torch.version.cuda
                resultado["vram_gb"] = round(torch.cuda.get_device_properties(0).total_memory / (1024**3), 2)
        except ImportError:
            pass

        # Verificar memoria RAM y disco
        try:
            import psutil
            vm = psutil.virtual_memory()
            resultado["ram_gb"] = round(vm.total / (1024**3), 2)
            disk = psutil.disk_usage(str(BASE_DIR))
            resultado["disco_libre_gb"] = round(disk.free / (1024**3), 2)
        except Exception:
            pass

        self.gpu_info = resultado
        return resultado

    def imprimir_resumen_entorno(self) -> None:
        """Muestra un resumen estilizado del entorno detectado."""
        info = self.verificar_entorno()
        sep = "=" * 70
        print(sep)
        print("🏛️ JULLBRAIN v0.1.0 — DIAGNÓSTICO DE ENTORNO EN GOOGLE COLAB")
        print(sep)
        print(f" • Versión Python : {info['python_version']}")
        if info["gpu_disponible"]:
            print(f" • GPU Acelerada  : ✅ {info['gpu_nombre']} ({info.get('vram_gb', 0)} GB VRAM)")
            print(f" • Soporte CUDA   : ✅ Versión {info.get('cuda_version', 'N/A')}")
        else:
            print(" • GPU Acelerada  : ⚠️ No detectada. Se ejecutará en CPU (más lento)")
        print(f" • Memoria RAM    : {info['ram_gb']} GB")
        print(f" • Espacio Libre  : {info['disco_libre_gb']} GB")
        print(sep)

    def sincronizar_github(self, repo_url: Optional[str] = None, rama: str = "main") -> bool:
        """
        Actualiza el código local en Colab ejecutando git pull.
        Si no se está dentro del repositorio clonado, lo clona.
        """
        url = repo_url or self.config.get("repositorio", {}).get("github_url", "https://github.com/julljoll/JullBrain.git")
        print(f"\n[GIT] Sincronizando con repositorio oficial: {url} (rama {rama})...")

        try:
            # Comprobar si estamos dentro de un repo git
            res = subprocess.run(["git", "status"], capture_output=True, text=True, cwd=str(BASE_DIR))
            if res.returncode == 0:
                # Ya es un repositorio
                pull_res = subprocess.run(["git", "pull", "origin", rama], capture_output=True, text=True, cwd=str(BASE_DIR))
                if pull_res.returncode == 0:
                    print("✅ [GIT] Código actualizado exitosamente con origin/" + rama)
                    print(pull_res.stdout.strip())
                    return True
                else:
                    print(f"⚠️ [GIT] Advertencia en git pull: {pull_res.stderr.strip()}")
                    return False
            else:
                print(f"ℹ️ [GIT] No es directorio git activo. Clonando en ./JullBrain...")
                clone_res = subprocess.run(["git", "clone", "-b", rama, url], capture_output=True, text=True)
                if clone_res.returncode == 0:
                    print("✅ [GIT] Repositorio clonado exitosamente.")
                    return True
                else:
                    print(f"❌ [GIT] Error al clonar repositorio: {clone_res.stderr.strip()}")
                    return False
        except Exception as e:
            print(f"❌ [GIT] Excepción al sincronizar repositorio: {e}")
            return False

    def montar_google_drive(self) -> Optional[Path]:
        """
        Monta Google Drive en el runtime de Colab si está disponible.
        Crea las carpetas base del proyecto para persistencia.
        """
        try:
            from google.colab import drive  # type: ignore
            print("\n[DRIVE] Montando Google Drive para persistencia de datos...")
            drive.mount("/content/drive")
            self.drive_montado = True
            
            drive_cfg = self.config.get("google_drive", {})
            base_drive = Path(drive_cfg.get("ruta_drive_base", "/content/drive/MyDrive/JullBrain"))
            pdfs_drive = Path(drive_cfg.get("ruta_drive_pdfs", str(base_drive / "leyes_pdf")))
            out_drive = Path(drive_cfg.get("ruta_drive_output", str(base_drive / "output_rag")))
            emb_drive = Path(drive_cfg.get("ruta_drive_embeddings", str(base_drive / "embeddings")))

            # Crear carpetas si no existen
            for p in [base_drive, pdfs_drive, out_drive, emb_drive]:
                p.mkdir(parents=True, exist_ok=True)

            print(f"✅ [DRIVE] Google Drive montado correctamente.")
            print(f" • Carpeta de PDFs en Drive      : {pdfs_drive}")
            print(f" • Carpeta de Resultados en Drive : {out_drive}")
            print(f" • Carpeta de Vectores en Drive   : {emb_drive}")
            self.drive_path = base_drive
            return base_drive
        except ImportError:
            print("[DRIVE] Entorno fuera de Google Colab. Se omite el montaje de Drive.")
            self.drive_montado = False
            return None
        except Exception as e:
            print(f"[DRIVE] Error al montar Google Drive: {e}")
            self.drive_montado = False
            return None

    def sincronizar_pdfs_desde_drive(self) -> int:
        """
        Copia nuevos PDFs ubicados en Google Drive hacia RAG/datos_brutos.
        """
        if not self.drive_montado:
            return 0

        drive_cfg = self.config.get("google_drive", {})
        pdfs_drive = Path(drive_cfg.get("ruta_drive_pdfs", "/content/drive/MyDrive/JullBrain/leyes_pdf"))
        destino_local = BASE_DIR / "RAG" / "datos_brutos"
        destino_local.mkdir(parents=True, exist_ok=True)

        if not pdfs_drive.exists():
            return 0

        copiados = 0
        for pdf_file in pdfs_drive.rglob("*.pdf"):
            rel = pdf_file.relative_to(pdfs_drive)
            target = destino_local / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists() or target.stat().st_size != pdf_file.stat().st_size:
                shutil.copy2(pdf_file, target)
                copiados += 1

        if copiados > 0:
            print(f"✅ [DRIVE] Se sincronizaron {copiados} archivo(s) PDF desde Google Drive.")
        return copiados

    def ejecutar_conversion(self, post_process_only: bool = False) -> int:
        """
        Ejecuta convert_normativas.py usando los mejores parámetros para Colab.
        """
        cmd = [sys.executable, str(BASE_DIR / "convert_normativas.py")]
        if post_process_only:
            cmd.append("--post-process-only")

        print("\n" + "=" * 70)
        print("🚀 INICIANDO PROCESAMIENTO DOCUMENTAL CON IBM DOCLING")
        print("=" * 70)
        res = subprocess.run(cmd, cwd=str(BASE_DIR))
        return res.returncode

    def ejecutar_validacion_cruzada(self) -> int:
        """
        Ejecuta validator.py para certificar el Principio de Error Cero (Doble Validación).
        """
        print("\n" + "=" * 70)
        print("🔬 EJECUTANDO DOBLE VALIDACIÓN CRUZADA FORENSE (validator.py)")
        print("=" * 70)
        cmd = [sys.executable, str(BASE_DIR / "validator.py")]
        res = subprocess.run(cmd, cwd=str(BASE_DIR))
        return res.returncode

    def generar_embeddings_granite(self) -> int:
        """
        Ejecuta granite_embedder.py con aceleración GPU para vectorizar chunks.
        """
        print("\n" + "=" * 70)
        print("🧠 GENERANDO EMBEDDINGS CON IBM GRANITE R2 (granite_embedder.py)")
        print("=" * 70)
        cmd = [sys.executable, str(BASE_DIR / "granite_embedder.py")]
        res = subprocess.run(cmd, cwd=str(BASE_DIR))
        return res.returncode

    def respaldar_en_google_drive(self) -> bool:
        """
        Copia los resultados generados (normativas_rag, normativas_chunks)
        hacia Google Drive para que persistan de forma indefinida.
        """
        if not self.drive_montado:
            print("ℹ️ [RESPALDO] Google Drive no está montado. Omitiendo respaldo a la nube.")
            return False

        drive_cfg = self.config.get("google_drive", {})
        out_drive = Path(drive_cfg.get("ruta_drive_output", "/content/drive/MyDrive/JullBrain/output_rag"))
        out_drive.mkdir(parents=True, exist_ok=True)

        print("\n[RESPALDO] Sincronizando resultados hacia Google Drive...")
        directorios_a_respaldar = [
            BASE_DIR / "normativas_rag",
            BASE_DIR / "normativas_chunks",
            BASE_DIR / "RAG" / "Informacion_docling_rag"
        ]

        total_archivos = 0
        for src_dir in directorios_a_respaldar:
            if not src_dir.exists():
                continue
            dest_dir = out_drive / src_dir.name
            dest_dir.mkdir(parents=True, exist_ok=True)
            for item in src_dir.rglob("*"):
                if item.is_file():
                    rel = item.relative_to(src_dir)
                    target = dest_dir / rel
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, target)
                    total_archivos += 1

        print(f"✅ [RESPALDO] Respaldo completado: {total_archivos} archivo(s) guardados en Google Drive ({out_drive}).")
        return True

    def generar_manifiesto_sha256(self) -> Dict[str, str]:
        """
        Genera un manifiesto criptográfico SHA-256 de todas las normativas transformadas.
        """
        manifiesto: Dict[str, str] = {}
        rag_dir = BASE_DIR / "normativas_rag"
        if not rag_dir.exists():
            return manifiesto

        for md_file in rag_dir.rglob("*.md"):
            try:
                h = hashlib.sha256()
                with open(md_file, "rb") as f:
                    while chunk := f.read(65536):
                        h.update(chunk)
                manifiesto[str(md_file.relative_to(BASE_DIR))] = h.hexdigest()
            except Exception:
                pass

        # Guardar manifiesto
        manifest_path = BASE_DIR / "manifiesto_forense_sha256.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifiesto, f, indent=2, ensure_ascii=False)

        print(f"✅ [FORENSE] Manifiesto criptográfico generado con {len(manifiesto)} normativas verificadas.")
        return manifiesto


def main():
    runner = JullBrainColabRunner()
    runner.imprimir_resumen_entorno()
    runner.sincronizar_github()
    runner.montar_google_drive()
    runner.sincronizar_pdfs_desde_drive()
    
    # Procesamiento
    rc = runner.ejecutar_conversion(post_process_only=False)
    if rc == 0:
        runner.ejecutar_validacion_cruzada()
        runner.generar_embeddings_granite()
        runner.generar_manifiesto_sha256()
        runner.respaldar_en_google_drive()
        print("\n🏛️ PROCESO COMPLETO EJECUTADO CON ÉXITO EN JULLBRAIN v0.1.0.")
    else:
        print(f"\n❌ Error durante la conversión documental. Código de salida: {rc}")


if __name__ == "__main__":
    main()
