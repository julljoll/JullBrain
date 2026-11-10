"""
jullbrain.transforms — Dominio de Ingesta y Transformación Documental (IBM Data Prep Kit + Docling)
"""

from legalizer import legalize, clean_noise, normalize_article_marker, detect_instrument_type
from metadata_extractor import extract_metadata, inject_frontmatter, sha256_file
from validator import (
    extract_article_blocks,
    validate_sequence,
    validate_article_length,
    validate_md_file,
    cross_validate_against_pdf,
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
    "legalize",
    "clean_noise",
    "normalize_article_marker",
    "detect_instrument_type",
    "extract_metadata",
    "inject_frontmatter",
    "sha256_file",
    "extract_article_blocks",
    "validate_sequence",
    "validate_article_length",
    "validate_md_file",
    "cross_validate_against_pdf",
    "AbstractIBMTransform",
    "TransformResult",
    "LegalHierarchyTransform",
    "MetadataFrontmatterTransform",
    "ForensicValidatorTransform",
    "GraniteGuardianTransform",
    "IBMDataPrepPipeline",
]
