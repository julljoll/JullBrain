"""
granite_embedder.py — JullBrain RAG-Pipeline v0.2.0
═══════════════════════════════════════════════════════════════════════
Módulo de Embeddings Semánticos con IBM Granite Embedding R2
Motor: sentence-transformers (ibm-granite/granite-embedding-311m-multilingual-r2)
Almacenamiento Local de Ciberseguridad: ./RAG/modelos_ia/granite_embeddings
Fallback: Ollama API local (http://localhost:11434)

Principios aplicados:
  - Ciberseguridad IBM & Zero-Trust: Los pesos del modelo se guardan y cargan
    localmente en RAG/modelos_ia/granite_embeddings con telemetría deshabilitada
    y verificación criptográfica SHA-256 (model_vault_manifest.json).
  - Espejo documental: el campo 'embedding' se añade sin modificar
    ningún campo original del chunk (content, metadata, article_id, etc.).
  - Abstención explícita: si el modelo no carga, lanza excepción descriptiva.
"""

from __future__ import annotations
import os as _os
import sys
from pathlib import Path

# Reconfigurar salida estándar para UTF-8 en Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent
MODELS_VAULT_DIR = BASE_DIR / "RAG" / "modelos_ia"
GRANITE_EMB_DIR = MODELS_VAULT_DIR / "granite_embeddings"
HF_CACHE_DIR = MODELS_VAULT_DIR / "huggingface"
GRANITE_EMB_DIR.mkdir(parents=True, exist_ok=True)
HF_CACHE_DIR.mkdir(parents=True, exist_ok=True)

# ── Ciberseguridad IBM: Telemetría Cero y Bóveda Local de Modelos ──
_os.environ["HF_HUB_DISABLE_XET_STORAGE"] = "1"
_os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
_os.environ["DO_NOT_TRACK"] = "1"
_os.environ["ANONYMIZED_TELEMETRY"] = "False"
_os.environ.setdefault("HF_HOME", str(HF_CACHE_DIR))
_os.environ.setdefault("SENTENCE_TRANSFORMERS_HOME", str(GRANITE_EMB_DIR))

import json
import logging
import time
from typing import Any

from audit_logger import default_audit_logger

logger = logging.getLogger(__name__)

CONFIG_PATH = BASE_DIR / "pipeline_config.json"

_DEFAULT_MODEL   = "ibm-granite/granite-embedding-311m-multilingual-r2"
_DEFAULT_BACKEND = "sentence-transformers"
_DEFAULT_BATCH   = 32
_DEFAULT_DEVICE  = "cpu"


def load_embedding_config() -> dict[str, Any]:
    """Lee pipeline_config.json y devuelve los parámetros de embedding."""
    if not CONFIG_PATH.exists():
        logger.warning("pipeline_config.json no encontrado, usando defaults.")
        return {}
    with CONFIG_PATH.open(encoding="utf-8") as f:
        return json.load(f)


class GraniteEmbedder:
    """
    Motor de embeddings semánticos usando IBM Granite Embedding R2
    con almacenamiento local aislado en RAG/modelos_ia/granite_embeddings.
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
        self.cache_dir  = str(GRANITE_EMB_DIR)

        self._model = None
        self._load_time_s: float = 0.0
        self._vector_dim: int = 0

        logger.info(
            "GraniteEmbedder init | model=%s | backend=%s | device=%s | vault=%s",
            self.model_name, self.backend, self.device, self.cache_dir,
        )

    def _ensure_model(self) -> None:
        """Carga el modelo desde la bóveda local RAG/modelos_ia (o lo descarga y sella si falta)."""
        if self._model is not None:
            return

        if self.backend == "sentence-transformers":
            self._load_st_model()
        elif self.backend == "ollama":
            self._check_ollama_connection()
        else:
            raise ValueError(
                f"Backend desconocido: '{self.backend}'. "
                "Valores válidos: 'sentence-transformers', 'ollama'."
            )

    def _load_st_model(self) -> None:
        """Carga el modelo sentence-transformers en la bóveda local RAG/modelos_ia/granite_embeddings."""
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore
        except ImportError as exc:
            raise ImportError(
                "sentence-transformers no está instalado. "
                "Ejecuta: pip install sentence-transformers>=3.0.0"
            ) from exc

        logger.info("Cargando modelo IBM '%s' desde bóveda '%s' en '%s'…", self.model_name, self.cache_dir, self.device)
        t0 = time.perf_counter()

        # Verificar si ya existe copia local directa en RAG/modelos_ia/granite_embeddings
        local_model_subdir = GRANITE_EMB_DIR / self.model_name.replace("/", "--")
        target_source = str(local_model_subdir) if local_model_subdir.exists() and any(local_model_subdir.iterdir()) else self.model_name

        self._model = SentenceTransformer(
            target_source,
            device=self.device,
            cache_folder=self.cache_dir,
            trust_remote_code=False,
        )

        # Si se descargó por primera vez, guardar copia explícita en local_model_subdir para modo Air-Gapped
        if not local_model_subdir.exists() or not any(local_model_subdir.iterdir()):
            try:
                local_model_subdir.mkdir(parents=True, exist_ok=True)
                self._model.save(str(local_model_subdir))
                default_audit_logger.seal_and_verify_model_vault()
                logger.info("Modelo IBM Granite guardado localmente y sellado con SHA-256 en: %s", local_model_subdir)
            except Exception as e:
                logger.warning("No se pudo guardar copia directa del modelo en %s: %s", local_model_subdir, e)

        self._load_time_s = time.perf_counter() - t0
        sample_vec = self._model.encode("test", convert_to_numpy=True)
        self._vector_dim = int(sample_vec.shape[0])
        logger.info("Modelo listo | dim=%d | tiempo_carga=%.2fs", self._vector_dim, self._load_time_s)

    def _check_ollama_connection(self) -> None:
        """Verifica que el servidor Ollama local responde."""
        import urllib.request
        import urllib.error

        check_url = f"{self.ollama_url}/api/tags"
        try:
            with urllib.request.urlopen(check_url, timeout=5) as resp:
                _ = json.loads(resp.read())
            self._model = "ollama"
            sample = self._ollama_embed("test")
            self._vector_dim = len(sample)
            self._load_time_s = 0.0
        except (urllib.error.URLError, OSError) as exc:
            raise ConnectionError(
                f"No se puede conectar a Ollama en {self.ollama_url}. Error: {exc}"
            ) from exc

    def embed_text(self, text: str) -> list[float]:
        """Genera el vector de embedding para un texto."""
        self._ensure_model()

        if self.backend == "sentence-transformers":
            vec = self._model.encode(text, convert_to_numpy=True)
            return vec.tolist()
        elif self.backend == "ollama":
            return self._ollama_embed(text)
        else:
            raise ValueError(f"Backend no soportado: {self.backend}")

    def _ollama_embed(self, text: str) -> list[float]:
        import urllib.request

        payload = json.dumps({"model": self.model_name, "prompt": text}).encode("utf-8")
        req = urllib.request.Request(
            f"{self.ollama_url}/api/embeddings",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
        return result["embedding"]

    def embed_chunks(
        self,
        chunks: list[dict],
        text_field: str = "content",
        progress_callback: Any | None = None,
    ) -> list[dict]:
        """
        Añade el campo 'embedding' a cada chunk del pipeline JullBrain
        preservando el espejo documental (sin alterar campos existentes).
        """
        self._ensure_model()

        total = len(chunks)
        embedded: list[dict] = []

        for batch_start in range(0, total, self.batch_size):
            batch_slice = chunks[batch_start : batch_start + self.batch_size]
            texts = []
            for chunk in batch_slice:
                raw_text = chunk.get(text_field, "")
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
                    new_chunk = dict(chunk)
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

    def validate_model_health(self) -> dict[str, Any]:
        """Verifica que el modelo está operativo en la bóveda local y devuelve métricas."""
        try:
            self._ensure_model()
            sample_vec = self.embed_text("Artículo 1. El presente Código regula…")
            vault_status = default_audit_logger.seal_and_verify_model_vault()
            return {
                "status": "ok",
                "model": self.model_name,
                "backend": self.backend,
                "device": self.device,
                "local_vault": self.cache_dir,
                "vault_integrity": vault_status.get("integrity_status", "VERIFIED_OK"),
                "dim": self._vector_dim or len(sample_vec),
                "load_time_s": round(self._load_time_s, 3),
                "sample_preview": [round(v, 6) for v in sample_vec[:5]],
            }
        except Exception as exc:
            logger.exception("validate_model_health falló")
            return {
                "status": "error",
                "model": self.model_name,
                "backend": self.backend,
                "local_vault": self.cache_dir,
                "error": str(exc),
            }

    def embed_chunks_file(
        self,
        input_path: str | Path,
        output_path: str | Path | None = None,
        text_field: str = "content",
        progress_callback: Any | None = None,
    ) -> Path:
        """Carga un hierarchical_chunks.json, genera embeddings y guarda el resultado."""
        input_path = Path(input_path)
        if not input_path.exists():
            raise FileNotFoundError(f"Archivo de chunks no encontrado: {input_path}")

        with input_path.open(encoding="utf-8") as f:
            chunks = json.load(f)

        if isinstance(chunks, dict) and "chunks" in chunks:
            raw_chunks = chunks["chunks"]
            wrapper = {k: v for k, v in chunks.items() if k != "chunks"}
        else:
            raw_chunks = chunks
            wrapper = None

        embedded = self.embed_chunks(
            raw_chunks,
            text_field=text_field,
            progress_callback=progress_callback,
        )

        if output_path is None:
            stem = input_path.stem.replace("_embedded", "")
            output_path = input_path.parent / f"{stem}_embedded.json"
        output_path = Path(output_path)

        out_data = {**wrapper, "chunks": embedded} if wrapper is not None else embedded
        output_path.write_text(
            json.dumps(out_data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        logger.info("Chunks embebidos guardados en: %s", output_path)
        return output_path


if __name__ == "__main__":
    import argparse

    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")

    parser = argparse.ArgumentParser(description="Granite Embedder — JullBrain CLI")
    parser.add_argument("--health", action="store_true", help="Verifica el estado del modelo y la bóveda local.")
    parser.add_argument("--embed-text", metavar="TEXTO", help="Genera el embedding para un texto dado.")
    parser.add_argument("--embed-file", metavar="RUTA_JSON", help="Genera embeddings para todos los chunks en el archivo JSON.")
    parser.add_argument("--backend", default=None, help="Backend a usar: 'sentence-transformers' o 'ollama'.")
    parser.add_argument("--model", default=None, help="Nombre del modelo.")
    args = parser.parse_args()

    embedder = GraniteEmbedder(model_name=args.model, backend=args.backend)

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
        print("[INIT] 🚀 Verificando motor de embeddings IBM Granite R2 en bóveda local RAG/modelos_ia...")
        health = embedder.validate_model_health()
        print(json.dumps(health, indent=2, ensure_ascii=False))
        if health.get("status") == "ok":
            print(f"[OK] ✅ Modelo activo en dispositivo: {health.get('device')}, dimensión: {health.get('dim')}")
        else:
            print(f"[ERROR] ❌ Modelo no pudo inicializarse: {health.get('error')}")
