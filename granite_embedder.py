"""
granite_embedder.py — JullBrain RAG-Pipeline
═══════════════════════════════════════════════════════════════════════
Módulo de Embeddings Semánticos con IBM Granite Embedding R2
Motor: sentence-transformers (ibm-granite/granite-embedding-english-r2)
Fallback: Ollama API local (http://localhost:11434)

Principios aplicados:
  - Espejo documental (R7): el campo 'embedding' se añade sin modificar
    ningún campo original del chunk (content, metadata, article_id, etc.)
  - Abstención explícita: si el modelo no carga, lanza excepción descriptiva
    en lugar de silenciar el error.
  - Corpus cerrado: el modelo se configura en pipeline_config.json,
    nunca hardcodeado en producción.

Nota de compatibilidad Windows:
  HF_HUB_DISABLE_XET_STORAGE se fija a "1" en tiempo de importación para
  forzar descarga HTTP estándar desde HuggingFace. Esto evita que la DLL
  hf_xet sea bloqueada por políticas de Control de Aplicaciones de Windows.

Autor: JullBrain — Arquitecto de Datos con IA (R1/R2)
"""

from __future__ import annotations

# ── Forzar descarga HTTP estándar (deshabilita protocolo Xet de HuggingFace)
# Necesario en Windows con políticas de Control de Aplicaciones que bloquean
# la DLL hf_xet. Debe establecerse ANTES de cualquier import de huggingface_hub.
import os as _os
_os.environ.setdefault("HF_HUB_DISABLE_XET_STORAGE", "1")

import json
import logging
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ── Ruta base del proyecto (relativa a este archivo) ──────────────────
BASE_DIR = Path(__file__).parent
CONFIG_PATH = BASE_DIR / "pipeline_config.json"

# ── Defaults por si pipeline_config.json no tiene las claves nuevas ───
_DEFAULT_MODEL     = "ibm-granite/granite-embedding-english-r2"
_DEFAULT_BACKEND   = "sentence-transformers"
_DEFAULT_BATCH     = 32
_DEFAULT_DEVICE    = "cpu"


# ══════════════════════════════════════════════════════════════════════
# Carga de configuración
# ══════════════════════════════════════════════════════════════════════

def load_embedding_config() -> dict[str, Any]:
    """Lee pipeline_config.json y devuelve los parámetros de embedding."""
    if not CONFIG_PATH.exists():
        logger.warning("pipeline_config.json no encontrado, usando defaults.")
        return {}
    with CONFIG_PATH.open(encoding="utf-8") as f:
        cfg = json.load(f)
    return cfg


# ══════════════════════════════════════════════════════════════════════
# Clase principal
# ══════════════════════════════════════════════════════════════════════

class GraniteEmbedder:
    """
    Motor de embeddings semánticos usando IBM Granite Embedding R2.

    Modos de backend:
        "sentence-transformers"  →  Descarga y corre el modelo localmente
                                    vía la librería sentence-transformers.
        "ollama"                 →  Llama a la API REST de Ollama en
                                    http://localhost:11434/api/embeddings
    """

    def __init__(
        self,
        model_name: str | None = None,
        backend: str | None = None,
        device: str | None = None,
        batch_size: int | None = None,
        ollama_url: str = "http://localhost:11434",
    ) -> None:
        cfg = load_embedding_config()

        self.model_name = model_name or cfg.get("ragflow_embedding_model", _DEFAULT_MODEL)
        self.backend    = backend    or cfg.get("embedding_backend",       _DEFAULT_BACKEND)
        self.device     = device     or cfg.get("embedding_device",        _DEFAULT_DEVICE)
        self.batch_size = batch_size or cfg.get("embedding_batch_size",    _DEFAULT_BATCH)
        self.ollama_url = ollama_url

        self._model = None          # cargado lazy en _ensure_model()
        self._load_time_s: float = 0.0
        self._vector_dim: int = 0

        logger.info(
            "GraniteEmbedder init | model=%s | backend=%s | device=%s | batch=%d",
            self.model_name, self.backend, self.device, self.batch_size,
        )

    # ──────────────────────────────────────────────────────────────────
    # Carga lazy del modelo
    # ──────────────────────────────────────────────────────────────────

    def _ensure_model(self) -> None:
        """Carga el modelo si aún no está en memoria."""
        if self._model is not None:
            return

        if self.backend == "sentence-transformers":
            self._load_st_model()
        elif self.backend == "ollama":
            # Ollama no requiere cargar un modelo local; solo verifica conectividad.
            self._check_ollama_connection()
        else:
            raise ValueError(
                f"Backend desconocido: '{self.backend}'. "
                "Valores válidos: 'sentence-transformers', 'ollama'."
            )

    def _load_st_model(self) -> None:
        """Carga el modelo sentence-transformers desde HuggingFace / caché local."""
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore
        except ImportError as exc:
            raise ImportError(
                "sentence-transformers no está instalado. "
                "Ejecuta: pip install sentence-transformers>=3.0.0"
            ) from exc

        logger.info("Cargando modelo '%s' en dispositivo '%s'…", self.model_name, self.device)
        t0 = time.perf_counter()
        self._model = SentenceTransformer(self.model_name, device=self.device)
        self._load_time_s = time.perf_counter() - t0

        # Detectar dimensión del vector con una codificación de prueba
        sample_vec = self._model.encode("test", convert_to_numpy=True)
        self._vector_dim = int(sample_vec.shape[0])
        logger.info(
            "Modelo listo | dim=%d | tiempo_carga=%.2fs",
            self._vector_dim, self._load_time_s
        )

    def _check_ollama_connection(self) -> None:
        """Verifica que el servidor Ollama responde."""
        import urllib.request  # stdlib, sin dependencias extra
        import urllib.error

        check_url = f"{self.ollama_url}/api/tags"
        try:
            with urllib.request.urlopen(check_url, timeout=5) as resp:
                _ = json.loads(resp.read())
            logger.info("Ollama disponible en %s", self.ollama_url)
            self._model = "ollama"          # marcador para saber que está "cargado"
            # Estimamos dim enviando un embed de prueba
            sample = self._ollama_embed("test")
            self._vector_dim = len(sample)
            self._load_time_s = 0.0
        except (urllib.error.URLError, OSError) as exc:
            raise ConnectionError(
                f"No se puede conectar a Ollama en {self.ollama_url}. "
                "Asegúrate de que Ollama esté corriendo. Error: " + str(exc)
            ) from exc

    # ──────────────────────────────────────────────────────────────────
    # API pública — embedding de texto único
    # ──────────────────────────────────────────────────────────────────

    def embed_text(self, text: str) -> list[float]:
        """
        Genera el vector de embedding para un texto.

        Args:
            text: El texto a embeber.

        Returns:
            Lista de floats con el vector de embedding.
        """
        self._ensure_model()

        if self.backend == "sentence-transformers":
            vec = self._model.encode(text, convert_to_numpy=True)
            return vec.tolist()
        elif self.backend == "ollama":
            return self._ollama_embed(text)
        else:
            raise ValueError(f"Backend no soportado: {self.backend}")

    def _ollama_embed(self, text: str) -> list[float]:
        """Llama al endpoint /api/embeddings de Ollama."""
        import urllib.request

        payload = json.dumps({
            "model": self.model_name,
            "prompt": text,
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{self.ollama_url}/api/embeddings",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
        return result["embedding"]

    # ──────────────────────────────────────────────────────────────────
    # API pública — embedding por lotes de chunks
    # ──────────────────────────────────────────────────────────────────

    def embed_chunks(
        self,
        chunks: list[dict],
        text_field: str = "content",
        progress_callback: Any | None = None,
    ) -> list[dict]:
        """
        Añade el campo 'embedding' a cada chunk del pipeline JullBrain.

        El campo 'embedding' se AGREGA sin modificar ningún campo existente
        (principio de espejo documental — R7).

        Args:
            chunks:            Lista de dicts del hierarchical_chunks.json.
            text_field:        Clave dentro del chunk que contiene el texto
                               a embeber. Por defecto 'content'.
            progress_callback: Callable opcional (current_idx, total) para
                               reportar progreso en Plotly Dash / UI.

        Returns:
            Nueva lista de chunks con campo 'embedding' añadido.
        """
        self._ensure_model()

        total = len(chunks)
        embedded: list[dict] = []

        for batch_start in range(0, total, self.batch_size):
            batch_slice = chunks[batch_start : batch_start + self.batch_size]
            texts = []
            for chunk in batch_slice:
                raw_text = chunk.get(text_field, "")
                # Fallback: buscar en estructuras anidadas comunes de Docling
                if not raw_text and isinstance(chunk.get("text"), str):
                    raw_text = chunk["text"]
                texts.append(raw_text or "")

            if self.backend == "sentence-transformers":
                vecs = self._model.encode(
                    texts,
                    convert_to_numpy=True,
                    batch_size=self.batch_size,
                    show_progress_bar=False,
                )
                for chunk, vec in zip(batch_slice, vecs):
                    new_chunk = dict(chunk)          # copia superficial, no muta el original
                    new_chunk["embedding"] = vec.tolist()
                    new_chunk["embedding_model"] = self.model_name
                    new_chunk["embedding_dim"] = int(vec.shape[0])
                    embedded.append(new_chunk)

            elif self.backend == "ollama":
                for chunk, text in zip(batch_slice, texts):
                    vec = self._ollama_embed(text)
                    new_chunk = dict(chunk)
                    new_chunk["embedding"] = vec
                    new_chunk["embedding_model"] = self.model_name
                    new_chunk["embedding_dim"] = len(vec)
                    embedded.append(new_chunk)

            if progress_callback:
                progress_callback(min(batch_start + self.batch_size, total), total)

        logger.info("embed_chunks: %d chunks procesados (dim=%d)", total, self._vector_dim)
        return embedded

    # ──────────────────────────────────────────────────────────────────
    # API pública — estado del modelo
    # ──────────────────────────────────────────────────────────────────

    def validate_model_health(self) -> dict[str, Any]:
        """
        Verifica que el modelo está operativo y devuelve métricas de estado.

        Returns:
            dict con campos: status, model, backend, device, dim, load_time_s,
                             sample_preview (primeros 5 valores de un embed de prueba).
        """
        try:
            self._ensure_model()
            sample_vec = self.embed_text("Artículo 1. El presente Código regula…")
            return {
                "status":         "ok",
                "model":          self.model_name,
                "backend":        self.backend,
                "device":         self.device,
                "dim":            self._vector_dim or len(sample_vec),
                "load_time_s":    round(self._load_time_s, 3),
                "sample_preview": [round(v, 6) for v in sample_vec[:5]],
            }
        except Exception as exc:
            logger.exception("validate_model_health falló")
            return {
                "status":  "error",
                "model":   self.model_name,
                "backend": self.backend,
                "error":   str(exc),
            }

    # ──────────────────────────────────────────────────────────────────
    # Utilidades de I/O para archivos JSON del pipeline
    # ──────────────────────────────────────────────────────────────────

    def embed_chunks_file(
        self,
        input_path: str | Path,
        output_path: str | Path | None = None,
        text_field: str = "content",
        progress_callback: Any | None = None,
    ) -> Path:
        """
        Carga un hierarchical_chunks.json, genera embeddings y guarda el resultado.

        Args:
            input_path:  Ruta al JSON de chunks de entrada.
            output_path: Ruta de salida. Si es None, genera
                         '<nombre>_embedded.json' en la misma carpeta.
            text_field:  Campo de texto dentro de cada chunk.
            progress_callback: Callable opcional (current, total).

        Returns:
            Ruta del archivo de salida generado.
        """
        input_path = Path(input_path)
        if not input_path.exists():
            raise FileNotFoundError(f"Archivo de chunks no encontrado: {input_path}")

        with input_path.open(encoding="utf-8") as f:
            chunks = json.load(f)

        # Aceptar tanto lista directa como wrapper {"chunks": [...]}
        if isinstance(chunks, dict) and "chunks" in chunks:
            raw_chunks  = chunks["chunks"]
            wrapper     = {k: v for k, v in chunks.items() if k != "chunks"}
        else:
            raw_chunks  = chunks
            wrapper     = None

        embedded = self.embed_chunks(raw_chunks, text_field=text_field,
                                     progress_callback=progress_callback)

        if output_path is None:
            stem = input_path.stem.replace("_embedded", "")
            output_path = input_path.parent / f"{stem}_embedded.json"
        output_path = Path(output_path)

        if wrapper is not None:
            out_data = {**wrapper, "chunks": embedded}
        else:
            out_data = embedded

        output_path.write_text(
            json.dumps(out_data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        logger.info("Chunks embebidos guardados en: %s", output_path)
        return output_path


# ══════════════════════════════════════════════════════════════════════
# CLI — ejecución directa para pruebas rápidas
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse

    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")

    parser = argparse.ArgumentParser(
        description="Granite Embedder — JullBrain CLI"
    )
    parser.add_argument(
        "--health", action="store_true",
        help="Verifica el estado del modelo y muestra métricas."
    )
    parser.add_argument(
        "--embed-text", metavar="TEXTO",
        help="Genera el embedding para un texto dado y muestra los primeros 10 valores."
    )
    parser.add_argument(
        "--embed-file", metavar="RUTA_JSON",
        help="Genera embeddings para todos los chunks en el archivo JSON."
    )
    parser.add_argument(
        "--backend", default=None,
        help="Backend a usar: 'sentence-transformers' o 'ollama'."
    )
    parser.add_argument(
        "--model", default=None,
        help="Nombre del modelo (override de pipeline_config.json)."
    )
    args = parser.parse_args()

    embedder = GraniteEmbedder(
        model_name=args.model,
        backend=args.backend,
    )

    if args.health:
        health = embedder.validate_model_health()
        print(json.dumps(health, indent=2, ensure_ascii=False))

    elif args.embed_text:
        vec = embedder.embed_text(args.embed_text)
        print(f"Dimensión del vector: {len(vec)}")
        print(f"Primeros 10 valores : {[round(v, 6) for v in vec[:10]]}")

    elif args.embed_file:
        out = embedder.embed_chunks_file(args.embed_file)
        print(f"Archivo de salida generado: {out}")

    else:
        parser.print_help()
