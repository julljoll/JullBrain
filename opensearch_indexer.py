"""
opensearch_indexer.py — Motor de Búsqueda Híbrida BM25 + Vectorial + RRF + Reranker
JullBrain Legal-RAG Platform — Stack Enterprise OpenRAG + OpenSearch

Modo Dual:
  1. Modo Local Nativo 100% Offline (Air-Gapped): BM25 en memoria/disco + Vectores NumPy + RRF + Reranker.
  2. Modo OpenSearch Cluster (OpenRAG Compatible): k-NN HNSW + BM25 Spanish + Ingesta Masiva (Bulk).
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
except Exception:
    NUMPY_AVAILABLE = False

try:
    from opensearchpy import OpenSearch, helpers
    OPENSEARCH_LIB_AVAILABLE = True
except ImportError:
    OPENSEARCH_LIB_AVAILABLE = False

from common_utils import load_json_config, sha256_file

logger = logging.getLogger("JullBrain.OpenSearchIndexer")
logger.setLevel(logging.INFO)

CONFIG_PATH = Path(__file__).resolve().parent / "pipeline_config.json"
BASE_STORAGE_DIR = Path(__file__).resolve().parent / "RAG" / "notebooks_db"
DEFAULT_CHUNKS_DIR = Path(__file__).resolve().parent / "normativas_chunks"


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
        """Búsqueda Vectorial por Similitud Coseno con NumPy o fallback nativo Python."""
        if not query_vector:
            return []

        index_data = self.load_chunks(notebook_id)
        chunks = index_data.get("chunks", [])
        embeddings = index_data.get("embeddings", [])

        if not chunks or not embeddings or len(chunks) != len(embeddings):
            return []

        try:
            if NUMPY_AVAILABLE:
                q_vec = np.array(query_vector, dtype=np.float32)
                q_norm = np.linalg.norm(q_vec)
                if q_norm == 0:
                    return []
                q_vec = q_vec / q_norm

                emb_mat = np.array(embeddings, dtype=np.float32)
                norms = np.linalg.norm(emb_mat, axis=1, keepdims=True)
                norms[norms == 0] = 1e-10
                emb_norm = emb_mat / norms

                similarities = [float(x) for x in np.dot(emb_norm, q_vec)]
            else:
                q_norm = math.sqrt(sum(float(x) * float(x) for x in query_vector))
                if q_norm == 0:
                    return []
                similarities = []
                for emb in embeddings:
                    e_norm = math.sqrt(sum(float(x) * float(x) for x in emb)) or 1e-10
                    dot = sum(float(a) * float(b) for a, b in zip(emb, query_vector))
                    similarities.append(dot / (e_norm * q_norm))

            indexed_sims = sorted(
                enumerate(similarities),
                key=lambda pair: (round(pair[1], 6), pair[0]),
                reverse=True,
            )[:top_k]

            results = []
            for i, sim in indexed_sims:
                if sim > 0.05:
                    item = chunks[i].copy()
                    item["score"] = round(sim, 4)
                    item["chunk_id"] = chunks[i].get("id", str(i))
                    results.append(item)
            return results
        except Exception as e:
            logger.error(f"[LocalIndexer] Error en vector search: {e}")
            return []

    def hybrid_search(
        self,
        notebook_id: str,
        query: str,
        query_vector: Optional[List[float]] = None,
        top_k: int = 20,
        k: int = 60
    ) -> List[Dict[str, Any]]:
        """Fusión RRF y Reranker en el motor local."""
        bm25_hits = self.bm25_search(notebook_id, query, top_k=top_k * 2)
        vector_hits = self.vector_search(notebook_id, query_vector, top_k=top_k * 2) if query_vector else []

        scores: Dict[str, float] = {}
        doc_map: Dict[str, Dict[str, Any]] = {}

        for rank, doc in enumerate(bm25_hits):
            doc_id = doc["chunk_id"]
            doc_map[doc_id] = doc
            scores[doc_id] = scores.get(doc_id, 0.0) + (1.0 / (k + rank + 1))

        for rank, doc in enumerate(vector_hits):
            doc_id = doc["chunk_id"]
            doc_map[doc_id] = doc
            scores[doc_id] = scores.get(doc_id, 0.0) + (1.0 / (k + rank + 1))

        sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
        merged = []
        query_terms = set(query.lower().split())
        for doc_id in sorted_ids:
            item = doc_map[doc_id].copy()
            rrf = round(scores[doc_id], 5)
            content = item.get("content", "").lower()
            article = item.get("article", "").lower()
            overlap = sum(1 for term in query_terms if term in content)
            art_match = 2.0 if any(term in article for term in query_terms) else 0.0
            item["rrf_score"] = rrf
            item["reranker_score"] = round(rrf + (overlap * 0.1) + art_match, 4)
            merged.append(item)

        merged.sort(key=lambda x: x["reranker_score"], reverse=True)
        return merged[:top_k]


class OpenSearchHybridIndexer:
    """
    Indexador y Buscador Híbrido OpenRAG + OpenSearch para JullBrain Enterprise.
    Totalmente compatible con el esquema de OpenRAG (`documents_*`).
    """

    def __init__(self, host: str = "localhost", port: int = 9200, index_prefix: str = "documents"):
        self.cfg = load_json_config(CONFIG_PATH)
        self.host = os.getenv("OPENSEARCH_HOST", self.cfg.get("opensearch_host", host))
        self.port = int(os.getenv("OPENSEARCH_PORT", str(self.cfg.get("opensearch_port", port))))
        self.index_name = self.cfg.get("opensearch_index_name", "documents_legal_venezuela")
        self.index_prefix = index_prefix
        self.dimension = self._infer_dimension()
        self.client = None
        self.local_indexer = LocalHybridIndexer()
        self.enabled = self.cfg.get("opensearch_enabled", True)

        if self.enabled:
            self._init_client()
        else:
            logger.info("OpenSearch deshabilitado en pipeline_config.json. Modo Local Nativo 100% Offline activo.")

    def _infer_dimension(self) -> int:
        """Infiere la dimensionalidad del vector para IBM Granite Embedding."""
        if "opensearch_dimension" in self.cfg:
            return int(self.cfg["opensearch_dimension"])
        emb_model = self.cfg.get("granite_embedding_model", "").lower()
        if "english-r2" in emb_model:
            return 1024
        return 768

    def _init_client(self):
        """Inicializa la conexión con el clúster de OpenSearch si está disponible."""
        if not OPENSEARCH_LIB_AVAILABLE:
            logger.info("opensearch-py no disponible. Operando en modo Local Offline.")
            self.client = None
            return

        try:
            self.client = OpenSearch(
                hosts=[{"host": self.host, "port": self.port}],
                http_compress=True,
                use_ssl=False,
                verify_certs=False,
                ssl_show_warn=False,
                timeout=2,
                max_retries=1
            )
            if self.client.ping():
                logger.info(f"Conexión exitosa a OpenSearch en {self.host}:{self.port} (dim={self.dimension})")
                self.ensure_index(self.index_name)
            else:
                logger.warning(f"OpenSearch ping no respondió en {self.host}:{self.port}. Usando Motor Local.")
                self.client = None
        except Exception as e:
            logger.info(f"OpenSearch no disponible en {self.host}:{self.port} ({e}). Usando Motor Local.")
            self.client = None

    def check_cluster_health(self) -> Dict[str, Any]:
        """Comprueba el estado de salud del clúster OpenSearch."""
        if not self.client:
            return {
                "connected": False,
                "host": f"{self.host}:{self.port}",
                "status": "OFFLINE",
                "mode": "local_hybrid_fallback",
                "message": "Clúster OpenSearch no conectado. Operando en modo local autónomo."
            }
        try:
            info = self.client.info()
            health = self.client.cluster.health()
            doc_count = 0
            if self.client.indices.exists(index=self.index_name):
                stats = self.client.indices.stats(index=self.index_name)
                doc_count = stats.get("indices", {}).get(self.index_name, {}).get("total", {}).get("docs", {}).get("count", 0)

            return {
                "connected": True,
                "host": f"{self.host}:{self.port}",
                "status": health.get("status", "green"),
                "cluster_name": info.get("cluster_name", ""),
                "version": info.get("version", {}).get("number", ""),
                "index_name": self.index_name,
                "dimension": self.dimension,
                "total_documents": doc_count,
                "mode": "opensearch_cluster"
            }
        except Exception as e:
            return {
                "connected": False,
                "host": f"{self.host}:{self.port}",
                "status": "ERROR",
                "error": str(e)
            }

    def ensure_index(self, index_name: str) -> bool:
        """Crea el índice con mapeo BM25 + k-NN compatible con OpenRAG."""
        if not self.client:
            return False

        mapping = {
            "settings": {
              "index": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
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
                "owner": {"type": "keyword"},
                "embedding": {
                  "type": "knn_vector",
                  "dimension": self.dimension,
                  "method": {
                    "name": "hnsw",
                    "space_type": "cosinesimil",
                    "engine": "nmslib",
                    "parameters": {
                      "ef_construction": 128,
                      "m": 24
                    }
                  }
                },
                "metadata": {
                  "properties": {
                    "source_pdf": {"type": "keyword"},
                    "sha256_pdf": {"type": "keyword"},
                    "sha256_chunk": {"type": "keyword"},
                    "instrumento": {"type": "keyword"},
                    "gaceta": {"type": "keyword"}
                  }
                }
              }
            }
        }
        try:
            if not self.client.indices.exists(index=index_name):
                self.client.indices.create(index=index_name, body=mapping)
                logger.info(f"Índice OpenRAG creado en OpenSearch: {index_name}")
            return True
        except Exception as e:
            logger.warning(f"Error al verificar/crear índice {index_name}: {e}")
            return False

    def create_notebook_index(self, notebook_id: str) -> str:
        """Crea o asegura un índice para un expediente específico."""
        index_name = f"{self.index_prefix}_{notebook_id.replace('-', '_')}"
        if self.client:
<<<<<<< HEAD
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
                            "dimension": 768,
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
=======
            self.ensure_index(index_name)
>>>>>>> 9dc0729da20b5212662bb449cb68c84c940431b8
        return index_name

    def index_chunks(self, notebook_id: str, chunks: List[Dict[str, Any]], embeddings: List[List[float]]) -> bool:
        """Indexa chunks en local y en OpenSearch si está disponible."""
        self.local_indexer.save_chunks(notebook_id, chunks, embeddings)

        if self.client:
            try:
                index_name = self.create_notebook_index(notebook_id)
                actions = []
                for idx, chunk in enumerate(chunks):
                    emb = embeddings[idx] if idx < len(embeddings) else [0.0] * self.dimension
                    if len(emb) != self.dimension:
                        # Relleno o truncado de seguridad si difiere
                        emb = (emb + [0.0] * self.dimension)[:self.dimension]

                    doc_body = {
                        "_index": index_name,
                        "_id": chunk.get("id", f"{notebook_id}_{idx}"),
                        "_source": {
                            "chunk_id": chunk.get("id", str(idx)),
                            "document_id": chunk.get("document_id", notebook_id),
                            "notebook_id": notebook_id,
                            "content": chunk.get("content", ""),
                            "chapter": chunk.get("chapter", ""),
                            "article": chunk.get("article", ""),
                            "clause": chunk.get("clause", ""),
                            "page_number": chunk.get("page_number", 1),
                            "doc_tags": chunk.get("doc_tags", []),
                            "owner": chunk.get("owner", "jullbrain_auditor"),
                            "embedding": emb,
                            "metadata": {
                                "source_pdf": chunk.get("source_pdf", ""),
                                "sha256_pdf": chunk.get("sha256_pdf", ""),
                                "sha256_chunk": chunk.get("sha256_chunk", "")
                            }
                        }
                    }
                    actions.append(doc_body)

                if OPENSEARCH_LIB_AVAILABLE and actions:
                    success, failed = helpers.bulk(self.client, actions, refresh=True)
                    logger.info(f"Indexados {success} chunks en OpenSearch ({index_name})")
            except Exception as e:
                logger.warning(f"No se pudo indexar en OpenSearch ({e}), datos preservados en motor local.")

        return True

    def bulk_index_corpus(self, chunks_dir: Optional[Path] = None, batch_size: int = 100) -> Dict[str, Any]:
        """
        Indexa masivamente todos los archivos JSON de chunks normativos en OpenSearch.
        Soporta los archivos generados en normativas_chunks/*.json
        """
        c_dir = Path(chunks_dir or DEFAULT_CHUNKS_DIR)
        stats = {
            "total_files": 0,
            "total_chunks": 0,
            "indexed_chunks": 0,
            "failed_chunks": 0,
            "index_name": self.index_name,
            "opensearch_cluster": bool(self.client)
        }

        if not c_dir.exists():
            return stats

        json_files = list(c_dir.glob("*.json"))
        stats["total_files"] = len(json_files)

        actions = []
        for jf in json_files:
            try:
                with open(jf, "r", encoding="utf-8") as f:
                    chunk_list = json.load(f)
                    if not isinstance(chunk_list, list):
                        continue
                    stats["total_chunks"] += len(chunk_list)

                    for idx, c in enumerate(chunk_list):
                        emb = c.get("embedding", [])
                        if not emb:
                            continue
                        if len(emb) != self.dimension:
                            emb = (emb + [0.0] * self.dimension)[:self.dimension]

                        cid = c.get("chunk_id") or f"{jf.stem}_{idx}"
                        doc = {
                            "_index": self.index_name,
                            "_id": cid,
                            "_source": {
                                "chunk_id": cid,
                                "document_id": jf.stem,
                                "notebook_id": "corpus_nacional",
                                "content": c.get("text", c.get("content", "")),
                                "article": f"Artículo {c.get('article_number', '')}",
                                "chapter": c.get("hierarchy_path", ""),
                                "owner": "jullbrain_forensic_auditor",
                                "embedding": emb,
                                "metadata": {
                                    "source_pdf": str(jf.name),
                                    "sha256_chunk": c.get("text_hash", ""),
                                    "gaceta": c.get("gaceta_number", "")
                                }
                            }
                        }
                        actions.append(doc)

                        if self.client and len(actions) >= batch_size:
                            success, _ = helpers.bulk(self.client, actions, refresh=True)
                            stats["indexed_chunks"] += success
                            actions = []
            except Exception as e:
                logger.error(f"Error procesando archivo de chunks {jf.name}: {e}")

        if self.client and actions:
            try:
                success, _ = helpers.bulk(self.client, actions, refresh=True)
                stats["indexed_chunks"] += success
            except Exception as e:
                logger.error(f"Error final en bulk OpenSearch: {e}")

        return stats

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
        query_vector: Optional[List[float]] = None,
        top_k: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Búsqueda Híbrida: si OpenSearch está disponible, ejecuta en clúster;
        de lo contrario ejecuta con el motor Local Nativo 100% Offline.
        """
        index_name = f"{self.index_prefix}_{notebook_id.replace('-', '_')}" if notebook_id != "default_notebook" else self.index_name

        if self.client:
            try:
                target_index = index_name if self.client.indices.exists(index=index_name) else self.index_name
                if self.client.indices.exists(index=target_index):
                    bm25_hits = []
                    vector_hits = []

                    bm25_query = {
                        "query": {"match": {"content": query}},
                        "size": top_k
                    }
                    res_bm25 = self.client.search(index=target_index, body=bm25_query)
                    for hit in res_bm25["hits"]["hits"]:
                        source = hit["_source"]
                        source["score"] = hit["_score"]
                        source["chunk_id"] = hit["_id"]
                        bm25_hits.append(source)

                    if query_vector:
                        q_vec = query_vector
                        if len(q_vec) != self.dimension:
                            q_vec = (q_vec + [0.0] * self.dimension)[:self.dimension]
                        knn_query = {
                            "query": {
                                "knn": {
                                    "embedding": {
                                        "vector": q_vec,
                                        "k": top_k
                                    }
                                }
                            },
                            "size": top_k
                        }
                        res_knn = self.client.search(index=target_index, body=knn_query)
                        for hit in res_knn["hits"]["hits"]:
                            source = hit["_source"]
                            source["score"] = hit["_score"]
                            source["chunk_id"] = hit["_id"]
                            vector_hits.append(source)

                    fused = self.reciprocal_rank_fusion(bm25_hits, vector_hits)
                    return self.rerank_results(query, fused, top_k=top_k)
            except Exception as e:
                logger.warning(f"Falla en consulta OpenSearch ({e}), recurriendo al motor Local Híbrido.")

        return self.local_indexer.hybrid_search(
            notebook_id=notebook_id,
            query=query,
            query_vector=query_vector,
            top_k=top_k
        )


# Instancia global por defecto
default_opensearch_indexer = OpenSearchHybridIndexer()
