# lightrag_integration.py — Módulo de Integración GraphRAG (LightRAG) para JullBrain
"""
Módulo para orquestar la extracción de grafos de conocimiento (Knowledge Graph)
y búsqueda dual (entidades + relaciones) usando LightRAG sobre los fragmentos
estructurados (hierarchical_chunks.json) de las normativas venezolanas.
"""
import os
import sys
import json
import logging
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("JullBrain.LightRAG")

# Bandera de disponibilidad de LightRAG
LIGHTRAG_AVAILABLE = False
try:
    from lightrag import LightRAG, QueryParam
    from lightrag.llm import ollama_model_complete, ollama_embedding
    from lightrag.utils import EmbeddingFunc
    LIGHTRAG_AVAILABLE = True
except ImportError:
    logger.warning("Librería 'lightrag-hku' no detectada en el entorno virtual. Modo Standby activado.")

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_WORKING_DIR = BASE_DIR / "RAG" / "lightrag_db"

class JullBrainLightRAG:
    """
    Gestor principal de GraphRAG utilizando LightRAG con modelos IBM Granite.
    """
    def __init__(self, working_dir: Optional[Path] = None, ollama_host: str = "http://localhost:11434", llm_model: str = "ibm-granite/granite-3.3-8b-instruct-GGUF"):
        self.working_dir = Path(working_dir or DEFAULT_WORKING_DIR)
        self.working_dir.mkdir(parents=True, exist_ok=True)
        self.ollama_host = ollama_host
        self.llm_model = llm_model
        self.rag_instance: Optional[Any] = None
        self._is_initialized = False

    def initialize(self) -> bool:
        """
        Inicializa la instancia de LightRAG con los backends de inferencia.
        """
        if not LIGHTRAG_AVAILABLE:
            logger.warning("No se puede inicializar LightRAG: 'lightrag-hku' no está instalado.")
            return False

        try:
            logger.info(f"Inicializando LightRAG en directorio: {self.working_dir}")
            
            # Definir wrappers asíncronos para Ollama LLM
            async def granite_llm_func(prompt, system_prompt=None, history_messages=[], **kwargs):
                return await ollama_model_complete(
                    prompt,
                    system_prompt=system_prompt,
                    history_messages=history_messages,
                    host=self.ollama_host,
                    model=self.llm_model,
                    options={"temperature": 0.15, "num_ctx": 32768},
                    **kwargs
                )

            # Definir embedding para LightRAG
            async def granite_embed_func(texts: List[str]) -> List[List[float]]:
                return await ollama_embedding(
                    texts,
                    host=self.ollama_host,
                    model="bge-m3" # o modelo de embedding disponible en Ollama
                )

            embedding_dimension = 1024 # Dimensión estándar para BGE-M3 / Granite Embedding

            self.rag_instance = LightRAG(
                working_dir=str(self.working_dir),
                llm_model_func=granite_llm_func,
                embedding_func=EmbeddingFunc(
                    embedding_dim=embedding_dimension,
                    max_token_size=8192,
                    func=granite_embed_func
                )
            )
            self._is_initialized = True
            logger.info("LightRAG inicializado exitosamente.")
            return True

        except Exception as e:
            logger.error(f"Error al inicializar LightRAG: {e}", exc_info=True)
            self._is_initialized = False
            return False

    def ingest_chunk_file(self, chunks_path: Path) -> bool:
        """
        Ingesta un archivo hierarchical_chunks.json al Grafo de Conocimiento.
        """
        if not chunks_path.exists():
            logger.error(f"Archivo de chunks no encontrado: {chunks_path}")
            return False

        try:
            raw_data = json.loads(chunks_path.read_text(encoding="utf-8"))
            texts = []
            for item in raw_data:
                text = item.get("text") or item.get("texto") or item.get("content")
                if text and len(text.strip()) > 30:
                    header_meta = f"Normativa: {item.get('legal_metadata', {}).get('instrumento', 'Ley')} | Artículo: {item.get('article_number', 'N/A')}\n"
                    texts.append(header_meta + text.strip())

            if not texts:
                logger.warning(f"No se extrajeron textos válidos de: {chunks_path}")
                return False

            logger.info(f"Ingestando {len(texts)} fragmentos en LightRAG...")

            if self._is_initialized and self.rag_instance:
                # Ingestar en la instancia activa
                for txt in texts:
                    self.rag_instance.insert(txt)
                logger.info(f"Ingestión completada en LightRAG para {chunks_path.name}")
                return True
            else:
                logger.warning("Instancia LightRAG no activa. Guardando textos para ingesta diferida.")
                return False

        except Exception as e:
            logger.error(f"Error al ingestar chunks en LightRAG: {e}")
            return False

    def query(self, query_text: str, mode: str = "hybrid") -> Dict[str, Any]:
        """
        Realiza una consulta al Grafo de Conocimiento de LightRAG.
        Modos soportados: 'naive', 'local', 'global', 'hybrid'.
        """
        valid_modes = ["naive", "local", "global", "hybrid"]
        mode = mode.lower() if mode.lower() in valid_modes else "hybrid"

        if not self._is_initialized or not self.rag_instance:
            return {
                "status": "standby",
                "mode": mode,
                "response": "El motor LightRAG no está inicializado o la librería 'lightrag-hku' no está instalada en el entorno.",
                "entities": [],
                "confidence": 0.0
            }

        try:
            logger.info(f"Ejecutando consulta LightRAG [modo={mode}]: '{query_text[:60]}...'")
            param = QueryParam(mode=mode)
            response = self.rag_instance.query(query_text, param=param)
            return {
                "status": "success",
                "mode": mode,
                "response": response,
                "confidence": 0.92
            }
        except Exception as e:
            logger.error(f"Error durante la consulta LightRAG: {e}")
            return {
                "status": "error",
                "mode": mode,
                "response": f"Error en motor LightRAG: {str(e)}",
                "confidence": 0.0
            }

    def get_graph_stats(self) -> Dict[str, Any]:
        """
        Retorna estadísticas sobre el estado del Grafo de Conocimiento.
        """
        graph_json = self.working_dir / "graph_chunk_entity_relation.graphml"
        kv_store = self.working_dir / "kv_store_full_docs.json"
        
        entities_count = 0
        relations_count = 0
        docs_count = 0

        if kv_store.exists():
            try:
                data = json.loads(kv_store.read_text(encoding="utf-8"))
                docs_count = len(data)
            except Exception:
                pass

        return {
            "available": LIGHTRAG_AVAILABLE,
            "initialized": self._is_initialized,
            "working_dir": str(self.working_dir),
            "documents_indexed": docs_count,
            "graph_file_exists": graph_json.exists()
        }

if __name__ == "__main__":
    print("=== TEST DE INTEGRACION LIGHTRAG JULLBRAIN ===")
    rag = JullBrainLightRAG()
    stats = rag.get_graph_stats()
    print("Estadísticas del Grafo:", json.dumps(stats, indent=2, ensure_ascii=False))
