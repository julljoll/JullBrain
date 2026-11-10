"""
gpu_detector.py — JullBrain v0.2.0
===================================
Analizador de Hardware Host, Optimizador de Procesador (CPU) para IBM Docling
y Selector de Dispositivo de Cómputo para IBM Granite.

Dado que IBM Docling ejecuta su pipeline de layout, tablas y OCR sobre CPU,
este módulo analiza la computadora donde se ejecuta, calcula el número óptimo
de hilos de procesador y configura las variables de bajo nivel (OpenMP, MKL,
PyTorch y Docling) antes de procesar documentos.
"""

from __future__ import annotations
import os
import sys
import json
import shutil
import platform
from pathlib import Path
from typing import Literal, Dict, Any, List

BASE_DIR = Path(__file__).resolve().parent
GPU_CONFIG_PATH = BASE_DIR / "gpu_config.json"
MODELS_VAULT_DIR = BASE_DIR / "RAG" / "modelos_ia"
DeviceType = Literal["cpu", "directml", "rocm", "cuda"]


def analizar_computadora_host() -> Dict[str, Any]:
    """
    Analiza exhaustivamente el hardware y entorno de la computadora actual:
    CPU, núcleos físicos/lógicos, RAM, disco, sistema operativo, versión de Python,
    disponibilidad de Podman y estado de la bóveda local de modelos IA (RAG/modelos_ia).
    """
    so = platform.system()
    arquitectura = platform.machine() or os.environ.get("PROCESSOR_ARCHITECTURE", "x86_64")
    procesador = platform.processor() or os.environ.get("PROCESSOR_IDENTIFIER", "CPU Genérico")
    nucleos_logicos = os.cpu_count() or 2
    nucleos_fisicos = max(1, nucleos_logicos // 2)

    ram_total_gb = 8.0
    ram_disponible_gb = 4.0
    disco_libre_gb = 20.0

    try:
        import psutil
        
        fisicos = psutil.cpu_count(logical=False)
        if fisicos:
            nucleos_fisicos = fisicos
        vm = psutil.virtual_memory()
        ram_total_gb = round(vm.total / (1024 ** 3), 2)
        ram_disponible_gb = round(vm.available / (1024 ** 3), 2)
        du = psutil.disk_usage(str(BASE_DIR))
        disco_libre_gb = round(du.free / (1024 ** 3), 2)
    except Exception:
        pass

    # Calcular hilos óptimos para IBM Docling en CPU (evita saturar el SO)
    hilos_docling = max(2, min(nucleos_logicos - 1, 8)) if nucleos_logicos > 2 else nucleos_logicos
    workers_lotes = max(1, min(3, nucleos_fisicos - 1 if nucleos_fisicos > 2 else 1))

    # Detectar Podman nativo
    podman_bin = shutil.which("podman")
    podman_disponible = podman_bin is not None

    # Verificar bóveda local de modelos IA en RAG/modelos_ia
    MODELS_VAULT_DIR.mkdir(parents=True, exist_ok=True)
    archivos_modelos = list(MODELS_VAULT_DIR.rglob("*.safetensors")) + \
                       list(MODELS_VAULT_DIR.rglob("*.onnx")) + \
                       list(MODELS_VAULT_DIR.rglob("*.gguf")) + \
                       list(MODELS_VAULT_DIR.rglob("*.bin"))

    reporte = {
        "sistema_operativo": f"{so} {platform.release()} ({platform.version()})",
        "arquitectura": arquitectura,
        "procesador": procesador,
        "nucleos_fisicos": nucleos_fisicos,
        "nucleos_logicos": nucleos_logicos,
        "hilos_optimos_docling": hilos_docling,
        "cpu_hilos_docling": hilos_docling,
        "docling_device": "cpu",
        "workers_optimos": workers_lotes,
        "ram_total_gb": ram_total_gb,
        "ram_disponible_gb": ram_disponible_gb,
        "disco_libre_gb": disco_libre_gb,
        "python_version": sys.version.split()[0],
        "python_executable": sys.executable,
        "podman_disponible": podman_disponible,
        "podman_path": podman_bin or "No detectado",
        "boveda_modelos_ia": str(MODELS_VAULT_DIR),
        "artefactos_modelos_locales": len(archivos_modelos),
    }
    return reporte


def configurar_entorno_cpu_docling() -> Dict[str, Any]:
    """
    Configura en tiempo de ejecución las variables de entorno para optimizar
    IBM Docling sobre el procesador local y fijar la bóveda local de modelos
    por razones de ciberseguridad (Zero-Telemetry & Air-Gapped).
    """
    info = analizar_computadora_host()
    hilos_str = str(info["hilos_optimos_docling"])

    # Optimización de CPU para IBM Docling / PyTorch / ONNXRuntime
    os.environ["OMP_NUM_THREADS"] = hilos_str
    os.environ["MKL_NUM_THREADS"] = hilos_str
    os.environ["OPENBLAS_NUM_THREADS"] = hilos_str
    os.environ["VECLIB_MAXIMUM_THREADS"] = hilos_str
    os.environ["NUMEXPR_NUM_THREADS"] = hilos_str
    os.environ["TORCH_NUM_THREADS"] = hilos_str
    os.environ["DOCLING_NUM_THREADS"] = hilos_str

    # Ciberseguridad IBM: Telemetría Cero y Bóveda Local de Modelos en RAG/modelos_ia
    os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
    os.environ["HF_HUB_DISABLE_XET_STORAGE"] = "1"
    os.environ["DO_NOT_TRACK"] = "1"
    os.environ["ANONYMIZED_TELEMETRY"] = "False"

    os.environ.setdefault("HF_HOME", str(MODELS_VAULT_DIR / "huggingface"))
    os.environ.setdefault("SENTENCE_TRANSFORMERS_HOME", str(MODELS_VAULT_DIR / "granite_embeddings"))
    os.environ.setdefault("DOCLING_ARTIFACTS_PATH", str(MODELS_VAULT_DIR / "docling"))
    os.environ.setdefault("TORCH_HOME", str(MODELS_VAULT_DIR / "torch"))

    try:
        import torch
        torch.set_num_threads(info["hilos_optimos_docling"])
    except Exception:
        pass

    return info


def detectar_backends_disponibles() -> List[Dict[str, Any]]:
    """
    Detecta qué backends de cómputo están disponibles en el sistema actual.
    IBM Docling opera siempre sobre CPU optimizada; los embeddings pueden usar CPU o GPU local.
    """
    info = analizar_computadora_host()
    so = platform.system()
    disponibles: List[Dict[str, Any]] = [
        {
            "id": "cpu",
            "nombre": f"CPU Optimizado ({info['nucleos_fisicos']}C/{info['nucleos_logicos']}T — {info['hilos_optimos_docling']} hilos Docling)",
            "disponible": True,
            "descripcion": "Motor nativo para IBM Docling + IBM Granite Embedding R2 (100% determinístico)."
        }
    ]

    if so == "Windows":
        try:
            import torch_directml  # type: ignore
            _ = torch_directml.device()
            disponibles.append({
                "id": "directml",
                "nombre": "GPU Windows — DirectML (DirectX 12)",
                "disponible": True,
                "descripcion": "Aceleración GPU para embeddings Granite via DirectX 12."
            })
        except ImportError:
            pass

    if so == "Linux":
        try:
            import torch
            if torch.cuda.is_available():
                nombre_gpu = torch.cuda.get_device_name(0)
                if "AMD" in nombre_gpu or "Radeon" in nombre_gpu or "gfx" in nombre_gpu.lower():
                    disponibles.append({
                        "id": "rocm",
                        "nombre": f"GPU AMD — ROCm ({nombre_gpu})",
                        "disponible": True,
                        "descripcion": "Aceleración ROCm en Linux."
                    })
                else:
                    disponibles.append({
                        "id": "cuda",
                        "nombre": f"GPU NVIDIA — CUDA ({nombre_gpu})",
                        "disponible": True,
                        "descripcion": "CUDA nativo en Linux."
                    })
        except ImportError:
            pass

    return disponibles


def preguntar_backend_al_usuario(console=None, auto_select_cpu: bool = True) -> DeviceType:
    """
    Muestra el diagnóstico del computador host, configura el procesador para IBM Docling
    y selecciona el dispositivo de cómputo (por defecto CPU optimizado sin bloquear).
    """
    from rich.table import Table
    from rich.prompt import IntPrompt
    from rich.console import Console
    from rich import box

    if console is None:
        console = Console()

    info = configurar_entorno_cpu_docling()
    backends = detectar_backends_disponibles()
    disponibles_activos = [b for b in backends if b["disponible"]]

    tabla = Table(
        title="🖥️ Diagnóstico de Hardware Host & Motor IBM Docling (CPU)",
        title_style="bold #FECF06",
        box=box.ROUNDED
    )
    tabla.add_column("Parámetro del Sistema", style="bold cyan", width=28)
    tabla.add_column("Valor Detectado / Configuración Aplicada", style="white")

    tabla.add_row("Sistema Operativo", f"{info['sistema_operativo']} [{info['arquitectura']}]")
    tabla.add_row("Procesador (CPU)", f"{info['procesador'][:65]}")
    tabla.add_row("Núcleos / Hilos Docling", f"{info['nucleos_fisicos']} Físicos / {info['nucleos_logicos']} Lógicos → [bold green]{info['hilos_optimos_docling']} hilos asignados a Docling[/]")
    tabla.add_row("Memoria RAM / Disco Libre", f"{info['ram_disponible_gb']} GB libres de {info['ram_total_gb']} GB | Disco libre: {info['disco_libre_gb']} GB")
    tabla.add_row("Intérprete Python Activo", f"Python {info['python_version']} ({info['python_executable']})")
    tabla.add_row("Motor Contenedores Podman", "[bold green]✅ Detectado[/]" if info["podman_disponible"] else "[yellow]No detectado en PATH (Modo Nativo Activo)[/]")
    tabla.add_row("Bóveda Local Modelos IBM", f"{info['boveda_modelos_ia']} ({info['artefactos_modelos_locales']} artefactos locales)")

    console.print(tabla)
    console.print()

    if len(disponibles_activos) == 1 or auto_select_cpu:
        elegido = disponibles_activos[0]
    else:
        opciones_validas = [str(i) for i, b in enumerate(backends, start=1) if b["disponible"]]
        respuesta = IntPrompt.ask(
            f"  Seleccione el dispositivo [{'/'.join(opciones_validas)}]",
            choices=opciones_validas,
            default=opciones_validas[0]
        )
        elegido = backends[int(respuesta) - 1]

    if elegido["id"] == "rocm":
        os.environ["HSA_OVERRIDE_GFX_VERSION"] = "8.0.3"

    try:
        cfg = json.loads(GPU_CONFIG_PATH.read_text(encoding="utf-8")) if GPU_CONFIG_PATH.exists() else {}
        cfg["modo_seleccionado"] = elegido["id"]
        cfg["ultimo_diagnostico_host"] = info
        GPU_CONFIG_PATH.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass

    console.print(f"[bold green]  ✅ Motor activo: {elegido['nombre']} | Ciberseguridad IBM Air-Gapped habilitada.[/]\n")
    return elegido["id"]


def get_device_string(backend: DeviceType) -> str:
    """Retorna el string de dispositivo compatible con sentence-transformers/torch."""
    if backend == "directml":
        try:
            import torch_directml  # type: ignore
            return str(torch_directml.device())
        except ImportError:
            return "cpu"
    elif backend in ("rocm", "cuda"):
        return "cuda"
    return "cpu"


if __name__ == "__main__":
    from rich.console import Console
    cons = Console()
    sel = preguntar_backend_al_usuario(cons, auto_select_cpu=True)
    print(f"Dispositivo activo: {sel} -> torch string: {get_device_string(sel)}")
