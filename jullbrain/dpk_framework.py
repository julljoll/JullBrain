"""
jullbrain/dpk_framework.py — Marco de Trabajo IBM Data Prep Kit (DPK) para Legal-RAG Forense
============================================================================================
Implementa el patrón arquitectónico modular de "Transforms" de IBM Research (IBM Data Prep Kit)
combinado con la Arquitectura de Referencia RAG de IBM Granite y trazabilidad forense ISO/IEC 27037.

Cada etapa del procesamiento documental es una clase `AbstractIBMTransform` desacoplada, auditable
y determinista que recibe y emite un sobre inmutable `TransformResult` con huella SHA-256.
"""

from __future__ import annotations

import hashlib
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from audit_logger import default_audit_logger
from granite_guardian_guardrail import default_guardian_guardrail
from legalizer import legalize
from metadata_extractor import extract_metadata, inject_frontmatter
from validator import extract_article_blocks, validate_sequence, validate_article_length


@dataclass
class TransformResult:
    """
    Sobre de datos estandarizado del patrón IBM Data Prep Kit (DPK).
    Preserva el contenido transformado, su hash SHA-256 en cada etapa, métricas y trazabilidad.
    """
    document_id: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    chunks: List[Dict[str, Any]] = field(default_factory=list)
    stage_history: List[Dict[str, Any]] = field(default_factory=list)
    status: str = "PENDING"
    errors: List[str] = field(default_factory=list)

    @property
    def content_sha256(self) -> str:
        """Calcula el hash SHA-256 actual del contenido documental."""
        return hashlib.sha256(self.content.encode("utf-8")).hexdigest()


class AbstractIBMTransform(ABC):
    """
    Clase base abstracta inspirada en `AbstractTransform` de IBM Data Prep Kit (DPK).
    Define el contrato obligatorio para toda transformación en el pipeline JullBrain.
    """

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None) -> None:
        self.name = name
        self.config = config or {}

    @abstractmethod
    def apply(self, data: TransformResult) -> TransformResult:
        """Ejecuta la transformación específica sobre el sobre `TransformResult`."""

    def transform(self, data: TransformResult) -> TransformResult:
        """Ejecuta `apply()` midiendo tiempos, calculando SHA-256 pre/post y registrando métricas."""
        t0 = time.perf_counter()
        sha_before = data.content_sha256
        result = self.apply(data)
        elapsed_ms = round((time.perf_counter() - t0) * 1000, 3)
        sha_after = result.content_sha256

        result.stage_history.append({
            "transform_name": self.name,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "elapsed_ms": elapsed_ms,
            "sha256_in": sha_before,
            "sha256_out": sha_after,
            "status": result.status,
        })
        return result


class LegalHierarchyTransform(AbstractIBMTransform):
    """Transform DPK 01: Estructuración Jerárquica Legal Venezolana (`legalizer.py`)."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(name="IBM-DPK::LegalHierarchyTransform", config=config)

    def apply(self, data: TransformResult) -> TransformResult:
        data.content = legalize(data.content, document_name=data.document_id)
        data.status = "LEGALIZED"
        return data


class MetadataFrontmatterTransform(AbstractIBMTransform):
    """Transform DPK 02: Extracción de Metadata Jurídica e Inyección de YAML Frontmatter (`metadata_extractor.py`)."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(name="IBM-DPK::MetadataFrontmatterTransform", config=config)

    def apply(self, data: TransformResult) -> TransformResult:
        pdf_path = str(data.metadata.get("pdf_path", "") or "")
        meta_dict = extract_metadata(
            data.content,
            pdf_path=pdf_path,
            filename=data.document_id,
        )
        data.metadata.update(meta_dict)
        data.content = inject_frontmatter(
            data.content,
            pdf_path=pdf_path,
            filename=data.document_id,
        )
        data.status = "METADATA_INJECTED"
        return data


class ForensicValidatorTransform(AbstractIBMTransform):
    """Transform DPK 03: Validación Forense de Secuencia de Artículos y Calidad OCR (`validator.py`)."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(name="IBM-DPK::ForensicValidatorTransform", config=config)

    def apply(self, data: TransformResult) -> TransformResult:
        articles = extract_article_blocks(data.content)
        gaps, duplicates = validate_sequence(articles)
        short_articles = validate_article_length(articles)
        has_frontmatter = data.content.startswith("---\n")
        overall = "OK" if (articles and not gaps and not duplicates) else "WARNING"
        data.metadata["validation_report"] = {
            "overall_status": overall,
            "articles_found": len(articles),
            "sequence_gaps": gaps,
            "duplicates": duplicates,
            "short_articles": short_articles,
            "has_frontmatter": has_frontmatter,
        }
        data.status = f"VALIDATED_{overall}"
        return data


class GraniteGuardianTransform(AbstractIBMTransform):
    """Transform DPK 04: Escaneo Cognitivo de Seguridad y PII con IBM Granite Guardian (`granite_guardian_guardrail.py`)."""

    def __init__(self, redact_pii: bool = False, config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(name="IBM-DPK::GraniteGuardianTransform", config=config)
        self.redact_pii = redact_pii

    def apply(self, data: TransformResult) -> TransformResult:
        pii_scan = default_guardian_guardrail.scan_and_redact_pii(data.content)
        data.metadata["pii_detected"] = pii_scan["pii_detected"]
        data.metadata["pii_types"] = pii_scan["pii_types"]
        if self.redact_pii and pii_scan["pii_detected"]:
            data.content = pii_scan["sanitized_text"]
        data.status = "GUARDIAN_VERIFIED"
        return data


class IBMDataPrepPipeline:
    """
    Orquestador de Pipeline de Transformaciones basado en IBM Data Prep Kit (DPK).
    Ejecuta en cadena una lista de `AbstractIBMTransform` y registra el resultado final
    en la cadena criptográfica inmutable `HMAC-SHA256` (`audit_logger.py`).
    """

    def __init__(self, transforms: Optional[List[AbstractIBMTransform]] = None) -> None:
        self.transforms: List[AbstractIBMTransform] = transforms or [
            LegalHierarchyTransform(),
            MetadataFrontmatterTransform(),
            ForensicValidatorTransform(),
            GraniteGuardianTransform(redact_pii=False),
        ]

    def run(
        self,
        raw_markdown: str,
        document_id: str = "normativa.md",
        initial_metadata: Optional[Dict[str, Any]] = None,
        actor: str = "ibm_dpk_pipeline",
    ) -> TransformResult:
        """Ejecuta todas las transformaciones DPK sobre un documento y firma la auditoría HMAC-SHA256."""
        envelope = TransformResult(
            document_id=document_id,
            content=raw_markdown,
            metadata=dict(initial_metadata or {}),
        )

        for transform in self.transforms:
            envelope = transform.transform(envelope)

        audit_entry = default_audit_logger.log_event(
            event_type="IBM_DPK_PIPELINE_EXECUTION",
            user_id=actor,
            document_sha256=envelope.content_sha256,
            action_details={
                "document_id": document_id,
                "final_status": envelope.status,
                "stages_executed": len(envelope.stage_history),
                "validation": envelope.metadata.get("validation_report", {}),
            },
        )
        envelope.metadata["audit_hmac_sha256"] = audit_entry.get("hmac_sha256")
        return envelope
