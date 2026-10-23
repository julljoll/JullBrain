"""
gpu_detector.py — JullBrain V3.0
=================================
Detector de aceleración GPU para AMD RX 580 en Windows (DirectML)
y Linux (ROCm gfx803), con fallback garantizado a CPU.

NO modifica ningún archivo de leyes ni documentos.
Solo configura el dispositivo de cómputo para embeddings.
"""
import os
import sys
import platform
import json
from pathlib import Path
from typing import Literal

GPU_CONFIG_PATH = Path(__file__).resolve().parent / "gpu_config.json"
DeviceType = Literal["cpu", "directml", "rocm", "cuda"]


def detectar_backends_disponibles() -> list[dict]:
    """
    Detecta qué backends de cómputo están realmente disponibles
    en el sistema actual. Retorna lista ordenada de opciones.
    """
    disponibles = []
    so = platform.system()  # 'Windows' | 'Linux' | 'Darwin'

    # 1. CPU — siempre disponible
    disponibles.append({
        "id": "cpu",
        "nombre": "CPU del sistema",
        "disponible": True,
        "descripcion": "Compatible con todos los entornos. Sin configuración extra."
    })

    # 2. DirectML — Windows + AMD/Intel/NVIDIA via DirectX 12
    if so == "Windows":
        try:
            import torch_directml
            dml_device = torch_directml.device()
            disponibles.append({
                "id": "directml",
                "nombre": "GPU AMD RX 580 — DirectML (Windows DirectX 12)",
                "disponible": True,
                "descripcion": "Aceleración GPU via DirectX 12. ~60% rendimiento vs CUDA."
            })
        except ImportError:
            disponibles.append({
                "id": "directml",
                "nombre": "GPU AMD — DirectML (NO INSTALADO)",
                "disponible": False,
                "descripcion": "Instalar con: pip install torch-directml"
            })

    # 3. ROCm — Linux + AMD (gfx803 legacy, requiere HSA_OVERRIDE)
    if so == "Linux":
        try:
            import torch
            # ROCm expone su interfaz como 'cuda' en PyTorch
            if torch.cuda.is_available():
                nombre_gpu = torch.cuda.get_device_name(0)
                # Verificar que es AMD (ROCm), no NVIDIA
                if "AMD" in nombre_gpu or "Radeon" in nombre_gpu or "gfx" in nombre_gpu.lower():
                    disponibles.append({
                        "id": "rocm",
                        "nombre": f"GPU AMD RX 580 — ROCm gfx803 ({nombre_gpu})",
                        "disponible": True,
                        "descripcion": "ROCm 5.7. Requiere HSA_OVERRIDE_GFX_VERSION=8.0.3"
                    })
                else:
                    disponibles.append({
                        "id": "cuda",
                        "nombre": f"NVIDIA GPU — CUDA ({nombre_gpu})",
                        "disponible": True,
                        "descripcion": "CUDA nativo. Máximo rendimiento."
                    })
        except ImportError:
            pass

    return disponibles


def preguntar_backend_al_usuario(console=None) -> DeviceType:
    """
    Muestra una tabla con los backends disponibles y pregunta al usuario.
    Llamada UNA SOLA VEZ al inicio de la sesión del orquestador.
    Guarda la elección en gpu_config.json para la sesión.
    """
    from rich.table import Table
    from rich.prompt import IntPrompt
    from rich.console import Console
    from rich import box

    if console is None:
        console = Console()

    backends = detectar_backends_disponibles()
    disponibles_activos = [b for b in backends if b["disponible"]]

    tabla = Table(
        title="⚡ Selección de Dispositivo de Cómputo",
        title_style="bold yellow",
        box=box.ROUNDED
    )
    tabla.add_column("#", style="cyan", justify="center", width=3)
    tabla.add_column("Dispositivo", style="bold white")
    tabla.add_column("Estado", justify="center")
    tabla.add_column("Descripción", style="dim white")

    for i, b in enumerate(backends, start=1):
        estado = "✅ Disponible" if b["disponible"] else "❌ No instalado"
        estado_style = "bold green" if b["disponible"] else "bold red"
        tabla.add_row(
            str(i) if b["disponible"] else "-",
            b["nombre"],
            f"[{estado_style}]{estado}[/]",
            b["descripcion"]
        )

    console.print(tabla)
    console.print()

    if len(disponibles_activos) == 1:
        console.print(f"[bold cyan]  Solo se detectó un dispositivo disponible: {disponibles_activos[0]['nombre']}[/]")
        elegido = disponibles_activos[0]
    else:
        opciones_validas = [str(i) for i, b in enumerate(backends, start=1) if b["disponible"]]
        respuesta = IntPrompt.ask(
            f"  Seleccione el dispositivo [{'/'.join(opciones_validas)}]",
            choices=opciones_validas,
            default=opciones_validas[0]
        )
        elegido = backends[int(respuesta) - 1]

    # Configurar variable de entorno si es ROCm
    if elegido["id"] == "rocm":
        os.environ["HSA_OVERRIDE_GFX_VERSION"] = "8.0.3"
        console.print("[dim]  [OK] HSA_OVERRIDE_GFX_VERSION=8.0.3 activado para gfx803[/]")

    # Guardar en gpu_config.json
    try:
        cfg = json.loads(GPU_CONFIG_PATH.read_text(encoding='utf-8'))
        cfg["modo_seleccionado"] = elegido["id"]
        GPU_CONFIG_PATH.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding='utf-8')
    except Exception:
        pass

    console.print(f"[bold green]  ✅ Dispositivo seleccionado: {elegido['nombre']}[/]\n")
    return elegido["id"]


def get_device_string(backend: DeviceType) -> str:
    """Retorna el string de dispositivo compatible con sentence-transformers/torch."""
    if backend == "directml":
        try:
            import torch_directml
            return str(torch_directml.device())
        except ImportError:
            return "cpu"
    elif backend in ("rocm", "cuda"):
        return "cuda"
    return "cpu"


if __name__ == "__main__":
    from rich.console import Console
    cons = Console()
    sel = preguntar_backend_al_usuario(cons)
    print(f"Dispositivo activo: {sel} -> torch string: {get_device_string(sel)}")
