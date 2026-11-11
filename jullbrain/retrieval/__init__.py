"""
jullbrain.retrieval — Dominio de Recuperación Híbrida (BM25 + k-NN RRF) y Cuadernos Forenses SHA-256
"""

from notebook_manager import NotebookManager, NotebookIntegrityError, default_notebook_manager
from opensearch_indexer import LocalHybridIndexer, OpenSearchHybridIndexer, default_opensearch_indexer

__all__ = [
    "NotebookManager",
    "NotebookIntegrityError",
    "default_notebook_manager",
    "LocalHybridIndexer",
    "OpenSearchHybridIndexer",
    "default_opensearch_indexer",
]

