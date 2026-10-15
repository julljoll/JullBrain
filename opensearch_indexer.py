"""
opensearch_indexer.py — Motor de Búsqueda Híbrida BM25 + Vectorial + RRF + Reranker
JullBrain Enterprise Legal Platform

Modo Dual:
  1. Modo Local Nativo 100% Offline (Air-Gapped): BM25 en memoria/disco + Vectores NumPy + RRF + Reranker.
  2. Modo OpenSearch Cluster: Opcional, activable desde pipeline_config.json.
"""

import os
import re
import json
import logging
import math
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

logger = logging.getLogger("JullBrain.OpenSearchIndexer")
logger.setLevel(logging.INFO)

CONFIG_PATH = Path(__file__).resolve().parent / "pipeline_config.json"
BASE_STORAGE_DIR = Path(__file__).resolve().parent / "RAG" / "notebooks_db"


def _tokenize(text: str) -> List[str]:
    """Tokenizador ligero para búsqueda léxica en español."""
    if not text:
        return []
    clean = re.sub(r"[^\w\sáéíóúÁÉÍÓÚñÑ]", " ", text.lower())
    return [t for t in clean.split() if len(t) > 1]


class LocalHybridIndexer:
    """
    Motor Híbrido Local Nativo 100% Offline (Air-Gapped).
    No requiere OpenSearch ni servicios externos.
    Persistencia JSON por expediente en RAG/notebooks_db/{notebook_id}/index_chunks.json
    """

    def __init__(self, storage_dir: Optional[Path] = None):
        self.storage_dir = Path(storage_dir or BASE_STORAGE_DIR)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._cache: Dict[str, Dict[str, Any]] = {}

    def _get_index_file(self, notebook_id: str) -> Path:
        nb_dir = self.storage_dir / notebook_id
        nb_dir.mkdir(parents=True, exist_ok=True)
        return nb_dir / "index_chunks.json"

    def save_chunks(self, notebook_id: str, chunks: List[Dict[str, Any]], embeddings: List[List[float]]) -> bool:
        """Guarda chunks y embeddings en disco y memoria para el cuaderno."""
        data = {
            "notebook_id": notebook_id,
            "chunks": chunks,
            "embeddings": embeddings
        }
        self._cache[notebook_id] = data

        try:
            filepath = self._get_index_file(notebook_id)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"[LocalIndexer] {len(chunks)} chunks indexados localmente en {filepath.name}")
            return True
        except Exception as e:
            logger.error(f"[LocalIndexer] Error al persistir chunks locales: {e}")
            return False

    def load_chunks(self, notebook_id: str) -> Dict[str, Any]:
        """Carga los chunks y vectores desde caché o disco."""
        if notebook_id in self._cache:
            return self._cache[notebook_id]

        filepath = self._get_index_file(notebook_id)
        if filepath.exists():
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._cache[notebook_id] = data
                    return data
            except Exception as e:
                logger.error(f"[LocalIndexer] Error al leer índice local: {e}")

        return {"notebook_id": notebook_id, "chunks": [], "embeddings": []}

    def bm25_search(self, notebook_id: str, query: str, top_k: int = 20) -> List[Dict[str, Any]]:
        """Búsqueda Léxica Okapi BM25 en memoria."""
        index_data = self.load_chunks(notebook_id)
        chunks = index_data.get("chunks", [])
        if not chunks:
            return []

        query_tokens = _tokenize(query)
        if not query_tokens:
            return []

        doc_tokens_list = []
        df: Dict[str, int] = {}
        for c in chunks:
            text = f"{c.get('content', '')} {c.get('article', '')} {c.get('chapter', '')} {c.get('document_id', '')}"
            tokens = _tokenize(text)
            doc_tokens_list.append(tokens)
            unique_tokens = set(tokens)
            for t in unique_tokens:
                df[t] = df.get(t, 0) + 1

        N = len(chunks)
        avgdl = sum(len(d) for d in doc_tokens_list) / max(1, N)
        k1 = 1.5
        b = 0.75

        scores = []
        for idx, (chunk, tokens) in enumerate(zip(chunks, doc_tokens_list)):
            score = 0.0
            doc_len = len(tokens)
            token_counts: Dict[str, int] = {}
            for t in tokens:
                token_counts[t] = token_counts.get(t, 0) + 1

            for qt in query_tokens:
                if qt in df:
                    n_q = df[qt]
                    idf = math.log((N - n_q + 0.5) / (n_q + 0.5) + 1.0)
                    tf = token_counts.get(qt, 0)
                    denom = tf + k1 * (1 - b + b * (doc_len / avgdl))
                    term_score = idf * (tf * (k1 + 1)) / max(1e-6, denom)
                    score += term_score

            # Bonificación por coincidencia exacta de artículo
            art_text = chunk.get("article", "").lower()
            if any(qt in art_text for qt in query_tokens):
                score += 2.0

            if score > 0:
                item = chunk.copy()
                item["score"] = round(score, 4)
                item["chunk_id"] = chunk.get("id", str(idx))
                scores.append(item)

        scores.sort(key=lambda x: x["score"], reverse=True)
        return scores[:top_k]

    def vector_search(self, notebook_id: str, query_vector: List[float], top_k: int = 20) -> List[Dict[str, Any]]:
        """Búsqueda Vectorial por Similitud Coseno con NumPy."""
        if not query_vector or not NUMPY_AVAILABLE:
            return []

        index_data = self.load_chunks(notebook_id)
        chunks = index_data.get("chunks", [])
        embeddings = index_data.get("embeddings", [])

        if not chunks or not embeddings or len(chunks) != len(embeddings):
            return []

        try:
            q_vec = np.array(query_vector, dtype=np.float32)
            q_norm = np.linalg.norm(q_vec)
            if q_norm == 0:
                return []
            q_vec = q_vec / q_norm

            emb_mat = np.array(embeddings, dtype=np.float32)
            norms = np.linalg.norm(emb_mat, axis=1, keepdims=True)
            norms[norms == 0] = 1e-10
            emb_norm = emb_mat / norms

            similarities = np.dot(emb_norm, q_vec)
            top_indices = np.argsort(similarities)[::-1][:top_k]

            results = []
            for i in top_indices:
                sim = float(similarities[i])
                if sim > 0.05:
                    item = chunks[i].copy()
                    item["score"] = round(sim, 4)
                    item["chunk_id"] = item.get("id", str(i))
                    results.append(item)
            return results
        except Exception as e:
            logger.error(f"[LocalIndexer] Error en vector_search: {e}")
            return []

    def hybrid_search(
        self,
        notebook_id: str,
        query: str,
        query_vector: List[float],
        top_k: int = 20,
        k: int = 60
    ) -> List[Dict[str, Any]]:
        """Ejecuta Búsqueda Híbrida Local (BM25 + Vector + RRF + Reranker)."""
        bm25_hits = self.bm25_search(notebook_id, query, top_k=top_k)
        vector_hits = self.vector_search(notebook_id, query_vector, top_k=top_k) if query_vector else []

        scores: Dict[str, float] = {}
        doc_map: Dict[str, Dict[str, Any]] = {}

        for rank, doc in enumerate(bm25_hits):
            doc_id = doc.get("chunk_id", str(rank))
            doc_map[doc_id] = doc
            scores[doc_id] = scores.get(doc_id, 0.0) + (1.0 / (k + rank + 1))

        for rank, doc in enumerate(vector_hits):
            doc_id = doc.get("chunk_id", str(rank))
            doc_map[doc_id] = doc
            scores[doc_id] = scores.get(doc_id, 0.0) + (1.0 / (k + rank + 1))

        sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
        merged = []
        for doc_id in sorted_ids:
            item = doc_map[doc_id].copy()
            item["rrf_score"] = round(scores[doc_id], 5)
            merged.append(item)

        # Reranker
        query_terms = set(query.lower().split())
        for doc in merged:
            content = doc.get("content", "").lower()
            article = doc.get("article", "").lower()
            overlap = sum(1 for term in query_terms if term in content)
            art_match = 2.0 if any(term in article for term in query_terms) else 0.0
            base_score = doc.get("rrf_score", 0.5)
            doc["reranker_score"] = round(base_score + (overlap * 0.1) + art_match, 4)

        merged.sort(key=lambda x: x["reranker_score"], reverse=True)
        return merged[:top_k]


class OpenSearchHybridIndexer:
    """
    Indexador y Buscador Híbrido para JullBrain Enterprise.
    Enrutador inteligente: Modo Local Offline por defecto, OpenSearch si está disponible y configurado.
    """

    def __init__(self, host: str = "localhost", port: int = 9200, index_prefix: str = "jullbrain_expediente"):
        self.host = os.getenv("OPENSEARCH_HOST", host)
        self.port = int(os.getenv("OPENSEARCH_PORT", str(port)))
        self.index_prefix = index_prefix
        self.client = None
        self.local_indexer = LocalHybridIndexer()

        # Determinar si OpenSearch está habilitado en configuración
        self.enabled = False
        if CONFIG_PATH.exists():
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    self.enabled = cfg.get("opensearch_enabled", False)
            except Exception:
                self.enabled = False

        if self.enabled:
            self._init_client()
        else:
            logger.info("OpenSearch deshabilitado en pipeline_config.json. Modo Local Nativo 100% Offline activo.")

    def _init_client(self):
        """Inicializa la conexión con el clúster de OpenSearch si está configurado."""
        try:
            from opensearchpy import OpenSearch
            self.client = OpenSearch(
                hosts=[{"host": self.host, "port": self.port}],
                http_compress=True,
                use_ssl=False,
                verify_certs=False,
                ssl_show_warn=False,
                timeout=1,
                max_retries=0
            )
            if self.client.ping():
                logger.info(f"Conexión exitosa a OpenSearch en {self.host}:{self.port}")
            else:
                logger.warning("OpenSearch ping no respondió. Operando con Motor Híbrido Local Offline.")
                self.client = None
        except Exception as e:
            logger.info(f"OpenSearch no disponible ({e}). Operando con Motor Híbrido Local Offline.")
            self.client = None

    def create_notebook_index(self, notebook_id: str) -> str:
        """Crea el índice con mapeo BM25 y vectorial k-NN para un cuaderno específico."""
        index_name = f"{self.index_prefix}_{notebook_id.replace('-', '_')}"
        if self.client:
            mapping = {
                "settings": {
                    "index": {
                        "knn": True,
                        "knn.algo_param.ef_search": 100
                    }
                },
                "mappings": {
                    "properties": {
                        "chunk_id": {"type": "keyword"},
                        "document_id": {"type": "keyword"},
                        "notebook_id": {"type": "keyword"},
                        "content": {"type": "text", "analyzer": "spanish"},
                        "chapter": {"type": "text"},
                        "article": {"type": "text"},
                        "clause": {"type": "text"},
                        "page_number": {"type": "integer"},
                        "doc_tags": {"type": "keyword"},
                        "embedding": {
                            "type": "knn_vector",
                            "dimension": 384,
                            "method": {
                                "name": "hnsw",
                                "space_type": "l2",
                                "engine": "nmslib"
                            }
                        }
                    }
                }
            }
            try:
                if not self.client.indices.exists(index=index_name):
                    self.client.indices.create(index=index_name, body=mapping)
                    logger.info(f"Índice OpenSearch creado: {index_name}")
            except Exception as e:
                logger.warning(f"Error al crear índice en OpenSearch: {e}")
        return index_name

    def index_chunks(self, notebook_id: str, chunks: List[Dict[str, Any]], embeddings: List[List[float]]) -> bool:
        """Indexa chunks en almacenamiento local y en OpenSearch si está disponible."""
        # 1. Indexación Local Siempre Garantizada (Offline)
        self.local_indexer.save_chunks(notebook_id, chunks, embeddings)

        # 2. Indexación en OpenSearch si está conectado
        if self.client:
            try:
                index_name = self.create_notebook_index(notebook_id)
                for idx, chunk in enumerate(chunks):
                    doc_body = {
                        "chunk_id": chunk.get("id", str(idx)),
                        "document_id": chunk.get("document_id", ""),
                        "notebook_id": notebook_id,
                        "content": chunk.get("content", ""),
                        "chapter": chunk.get("chapter", ""),
                        "article": chunk.get("article", ""),
                        "clause": chunk.get("clause", ""),
                        "page_number": chunk.get("page_number", 1),
                        "doc_tags": chunk.get("doc_tags", []),
                        "embedding": embeddings[idx] if idx < len(embeddings) else [0.0] * 384
                    }
                    self.client.index(index=index_name, id=doc_body["chunk_id"], body=doc_body, refresh=True)
                logger.info(f"Indexados {len(chunks)} chunks en OpenSearch ({index_name})")
            except Exception as e:
                logger.warning(f"No se pudo indexar en OpenSearch ({e}), datos preservados en motor local.")

        return True

    def reciprocal_rank_fusion(
        self,
        bm25_results: List[Dict[str, Any]],
        vector_results: List[Dict[str, Any]],
        k: int = 60
    ) -> List[Dict[str, Any]]:
        """Aplica la Fusión Recíproca de Rangos (RRF) para combinar BM25 y Vectores."""
        scores = {}
        doc_map = {}

        for rank, doc in enumerate(bm25_results):
            doc_id = doc["chunk_id"]
            doc_map[doc_id] = doc
            scores[doc_id] = scores.get(doc_id, 0.0) + (1.0 / (k + rank + 1))

        for rank, doc in enumerate(vector_results):
            doc_id = doc["chunk_id"]
            doc_map[doc_id] = doc
            scores[doc_id] = scores.get(doc_id, 0.0) + (1.0 / (k + rank + 1))

        sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
        merged = []
        for doc_id in sorted_ids:
            item = doc_map[doc_id].copy()
            item["rrf_score"] = round(scores[doc_id], 5)
            merged.append(item)

        return merged

    def rerank_results(self, query: str, candidate_docs: List[Dict[str, Any]], top_k: int = 20) -> List[Dict[str, Any]]:
        """Aplica Reranking basado en superposición léxico-semántica y coincidencia de términos clave."""
        query_terms = set(query.lower().split())
        for doc in candidate_docs:
            content = doc.get("content", "").lower()
            article = doc.get("article", "").lower()
            overlap = sum(1 for term in query_terms if term in content)
            art_match = 2.0 if any(term in article for term in query_terms) else 0.0
            base_score = doc.get("rrf_score", doc.get("score", 0.5))
            doc["reranker_score"] = round(base_score + (overlap * 0.1) + art_match, 4)

        candidate_docs.sort(key=lambda x: x["reranker_score"], reverse=True)
        return candidate_docs[:top_k]

    def hybrid_search(
        self,
        notebook_id: str,
        query: str,
        query_vector: List[float],
        top_k: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Búsqueda Híbrida: si OpenSearch está disponible, ejecuta en clúster;
        de lo contrario ejecuta con el motor Local Nativo 100% Offline.
        """
        index_name = f"{self.index_prefix}_{notebook_id.replace('-', '_')}"
        if self.client:
            try:
                if self.client.indices.exists(index=index_name):
                    bm25_hits = []
                    vector_hits = []

                    # 1. BM25 Lexical
                    bm25_query = {
                        "query": {"match": {"content": query}},
                        "size": top_k
                    }
                    res_bm25 = self.client.search(index=index_name, body=bm25_query)
                    for hit in res_bm25["hits"]["hits"]:
                        source = hit["_source"]
                        source["score"] = hit["_score"]
                        bm25_hits.append(source)

                    # 2. Vector k-NN
                    if query_vector:
                        knn_query = {
                            "query": {
                                "knn": {
                                    "embedding": {
                                        "vector": query_vector,
                                        "k": top_k
                                    }
                                }
                            },
                            "size": top_k
                        }
                        res_knn = self.client.search(index=index_name, body=knn_query)
                        for hit in res_knn["hits"]["hits"]:
                            source = hit["_source"]
                            source["score"] = hit["_score"]
                            vector_hits.append(source)

                    fused = self.reciprocal_rank_fusion(bm25_hits, vector_hits)
                    return self.rerank_results(query, fused, top_k=top_k)
            except Exception as e:
                logger.warning(f"Falla en consulta OpenSearch ({e}), recurriendo al motor Local Híbrido.")

        # Fallback autónomo: Motor Local Nativo (0 ms de retardo, sin red)
        return self.local_indexer.hybrid_search(
            notebook_id=notebook_id,
            query=query,
            query_vector=query_vector,
            top_k=top_k
        )


# Instancia global por defecto
default_opensearch_indexer = OpenSearchHybridIndexer()
