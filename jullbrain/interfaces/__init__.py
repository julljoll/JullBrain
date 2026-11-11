"""
jullbrain.interfaces — Dominio de Interfaces (Consola TUI Rich, API REST FastAPI Zero-Trust y Open WebUI Pipe)
"""

from app import app
from openwebui_pipeline import Pipeline
from orquestador import JullBrainOrquestador

__all__ = [
    "app",
    "Pipeline",
    "JullBrainOrquestador",
]

