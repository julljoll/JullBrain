"""
jullbrain — Paquete Modular Senior (IBM Data Prep Kit & IBM Granite RAG Reference Architecture)
===============================================================================================
Organiza el ecosistema JullBrain v0.2.0 bajo el patrón arquitectónico oficial de IBM Research:
- `jullbrain.dpk_framework` : Motor de Transformaciones Deterministas (IBM Data Prep Kit - DPK).
- `jullbrain.transforms`    : Etapa 1 — Ingesta Docling (CPU), Jerarquía Legal, Metadata YAML y Validación.
- `jullbrain.granite`       : Etapa 2 — Embeddings IBM Granite R2 (768d) y Grafo LightRAG (Granite 3.3).
- `jullbrain.security`      : Etapa 3 — Guardrails Cognitivos 6D (Granite Guardian) y Custodia HMAC-SHA256.
- `jullbrain.retrieval`     : Etapa 4 — Indexador Híbrido BM25 + k-NN RRF y Cuadernos Forenses SHA-256.
- `jullbrain.runtime`       : Etapa 5 — Diagnóstico de CPU/RAM/Podman y Mantenimiento Air-Gapped.
- `jullbrain.interfaces`    : Etapa 6 — Consola TUI Rich, API REST FastAPI Zero-Trust y Open WebUI Pipe.
"""

from version import (
    __version__,
    __version_info__,
    __git_tag__,
    SEMVER_SPEC_VERSION,
    SemanticVersion,
    CURRENT_SEMVER,
    PUBLIC_API_DECLARATION,
    get_version_metadata,
)
from jullbrain.dpk_framework import (
    AbstractIBMTransform,
    TransformResult,
    LegalHierarchyTransform,
    MetadataFrontmatterTransform,
    ForensicValidatorTransform,
    GraniteGuardianTransform,
    IBMDataPrepPipeline,
)

__all__ = [
    "__version__",
    "__version_info__",
    "__git_tag__",
    "SEMVER_SPEC_VERSION",
    "SemanticVersion",
    "CURRENT_SEMVER",
    "PUBLIC_API_DECLARATION",
    "get_version_metadata",
    "AbstractIBMTransform",
    "TransformResult",
    "LegalHierarchyTransform",
    "MetadataFrontmatterTransform",
    "ForensicValidatorTransform",
    "GraniteGuardianTransform",
    "IBMDataPrepPipeline",
]
