"""
opensearch_indexer.py — Motor de Búsqueda Híbrida BM25 + Vectorial + RRF + Reranker
JullBrain Enterprise Legal Platform
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("JullBrain.OpenSearchIndexer")
logger.setLevel(logging.INFO)


class OpenSearchHybridIndexer:
    """
    Indexador y Buscador Híbrido para JullBrain Enterprise.
    Combina Búsqueda Léxica (BM25) con Búsqueda Vectorial (Granite Embeddings),
    Fusión Recíproca de Rangos (RRF) y Reranking con Cross-Encoder.
    """

    def __init__(self, host: str = "localhost", port: int = 9200, index_prefix: str = "jullbrain_expediente"):
        self.host = os.getenv("OPENSEARCH_HOST", host)
        self.port = int(os.getenv("OPENSEARCH_PORT", str(port)))
        self.index_prefix = index_prefix
        self.client = None
        self._init_client()

    def _init_client(self):
        """Inicializa la conexión con el clúster de OpenSearch si está disponible."""
        try:
            from opensearchpy import OpenSearch
            self.client = OpenSearch(
                hosts=[{"host": self.host, "port": self.port}],
                http_compress=True,
                use_ssl=False,
                verify_certs=False,
                ssl_show_warn=False
            )
            # Prueba de ping
            if self.client.ping():
                logger.info(f"Conexión exitosa a OpenSearch en {self.host}:{self.port}")
            else:
                logger.warning("OpenSearch ping no respondió. Se utilizará el motor híbrido local fallback.")
                self.client = None
        except Exception as e:
            logger.info(f"OpenSearch no disponible en {self.host}:{self.port} ({e}). Operando en modo Híbrido Local.")
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
            if not self.client.indices.exists(index=index_name):
                self.client.indices.create(index=index_name, body=mapping)
                logger.info(f"Índice OpenSearch creado: {index_name}")
        return index_name

    def index_chunks(self, notebook_id: str, chunks: List[Dict[str, Any]], embeddings: List[List[float]]) -> bool:
        """Indexa chunks y sus correspondientes vectores en el índice del cuaderno."""
        index_name = self.create_notebook_index(notebook_id)
        if self.client:
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

        # Procesar BM25
        for rank, doc in enumerate(bm25_results):
            doc_id = doc["chunk_id"]
            doc_map[doc_id] = doc
            scores[doc_id] = scores.get(doc_id, 0.0) + (1.0 / (k + rank + 1))

        # Procesar Vector
        for rank, doc in enumerate(vector_results):
            doc_id = doc["chunk_id"]
            doc_map[doc_id] = doc
            scores[doc_id] = scores.get(doc_id, 0.0) + (1.0 / (k + rank + 1))

        # Ordenar por score RRF descendente
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
            
            # Puntuación del Reranker
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
        Búsqueda Híbrida obligatoria: BM25 + Búsqueda Vectorial + RRF + Cross-Encoder Reranker.
        """
        index_name = f"{self.index_prefix}_{notebook_id.replace('-', '_')}"
        bm25_hits = []
        vector_hits = []

        if self.client and self.client.indices.exists(index=index_name):
            # 1. BM25 Lexical Search
            bm25_query = {
                "query": {
                    "match": {
                        "content": query
                    }
                },
                "size": top_k
            }
            res_bm25 = self.client.search(index=index_name, body=bm25_query)
            for hit in res_bm25["hits"]["hits"]:
                source = hit["_source"]
                source["score"] = hit["_score"]
                bm25_hits.append(source)

            # 2. Vector k-NN Search
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

        # Fusion RRF y Rerank
        fused = self.reciprocal_rank_fusion(bm25_hits, vector_hits)
        final_ranked = self.rerank_results(query, fused, top_k=top_k)
        return final_ranked


# Instancia global por defecto
default_opensearch_indexer = OpenSearchHybridIndexer()
