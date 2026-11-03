"""
common_utils.py — Utilidades Comunes y Funciones Criptográficas Forenses
======================================================================
Módulo transversal para el ecosistema JullBrain Legal-RAG.
Provee funciones criptográficas (SHA-256), inspección de PDFs, carga
de configuración persistente y clasificación normativa venezolana.

Cumple con:
- ISO/IEC 27037 (Cadena de custodia e inmutabilidad digital).
- Principio DRY (Don't Repeat Yourself).
"""

import os
import re
import json
import hashlib
import logging
from pathlib import Path
from typing import Union, Dict, Any, Optional

logger = logging.getLogger("common_utils")

# ==============================================================================
# PATRONES Y CLASIFICACIÓN DE INSTRUMENTOS JURÍDICOS VENEZOLANOS
# ==============================================================================

RE_GACETA = re.compile(
    r'Gaceta\s+Oficial\s+(?:de\s+la\s+Rep[uú]blica\s+(?:Bolivariana\s+de\s+)?Venezuela\s+)?'
    r'N[°º\.]\s*([\d.,]+\s*(?:Extraordinario)?)',
    re.IGNORECASE
)

RE_FECHA = re.compile(
    r'(\d{1,2})\s+de\s+'
    r'(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)'
    r'\s+(?:de\s+)?(\d{4})',
    re.IGNORECASE
)

MESES_ES = {
    'enero': '01', 'febrero': '02', 'marzo': '03', 'abril': '04',
    'mayo': '05', 'junio': '06', 'julio': '07', 'agosto': '08',
    'septiembre': '09', 'octubre': '10', 'noviembre': '11', 'diciembre': '12'
}

TIPOS_INSTRUMENTO = [
    ('CONSTITUCION', 'Constitucion'),
    ('CODIGO', 'Codigo'),
    ('LEY ORGANICA', 'Ley Organica'),
    ('LEY ESPECIAL', 'Ley Especial'),
    ('DECRETO CON RANGO', 'Decreto con Rango de Ley'),
    ('DECRETO', 'Decreto'),
    ('RESOLUCION', 'Resolucion'),
    ('MANUAL', 'Manual'),
    ('REGLAMENTO', 'Reglamento'),
    ('PROVIDENCIA', 'Providencia'),
    ('NORMA', 'Norma'),
    ('GUIA', 'Guia'),
    ('LEY', 'Ley'),
]

CATEGORIAS_JURIDICAS = {
    'penal':          ['penal', 'delito', 'delitos', 'procesal penal', 'pena'],
    'civil':          ['civil', 'contratos', 'obligaciones', 'familia'],
    'administrativo': ['administracion publica', 'administrativo', 'procedimiento administrativo'],
    'laboral':        ['trabajo', 'laboral', 'empleo', 'trabajadores'],
    'tributario':     ['tributario', 'impuesto', 'renta', 'fiscal', 'aduanas'],
    'informatico':    ['informatico', 'informacion', 'datos', 'electronico', 'digital'],
    'constitucional': ['constituc', 'derechos', 'garantias'],
    'comercial':      ['comercio', 'mercantil', 'empresa', 'sociedad'],
    'ambiental':      ['ambiente', 'ambiental', 'ecolog'],
    'forense':        ['forense', 'evidencia', 'cadena de custodia', 'criminalistica'],
    'internacional':  ['iso', 'nist', 'internacional', 'norma internacional'],
}


# ==============================================================================
# CRIPTOGRAFÍA FORENSE (SHA-256)
# ==============================================================================

def sha256_file(path: Union[str, Path]) -> str:
    """
    Calcula el hash SHA-256 de un archivo en bloques de 64 KB.
    Protege la memoria RAM en PDFs o documentos de gran tamaño.
    Garantiza trazabilidad de cadena de custodia (ISO/IEC 27037).
    """
    p = Path(path)
    if not p.is_file():
        return "ERROR_NO_FILE"
    
    h = hashlib.sha256()
    try:
        with open(p, 'rb') as f:
            for chunk in iter(lambda: f.read(65536), b''):
                h.update(chunk)
        return h.hexdigest()
    except Exception as e:
        logger.error(f"Error calculando hash SHA-256 para {p}: {e}")
        return "ERROR_HASH"


def sha256_text(text: str) -> str:
    """Calcula el hash SHA-256 de un texto UTF-8."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ==============================================================================
# INSPECCIÓN DE DOCUMENTOS PDF
# ==============================================================================

def get_pdf_page_count(file_path: Union[str, Path]) -> int:
    """
    Retorna el número de páginas de un documento de forma ultrarrápida.
    Prioriza PyMuPDF (fitz) y utiliza fallback a pypdf si fitz no está disponible.
    """
    p = Path(file_path)
    if p.suffix.lower() != ".pdf":
        return 1

    try:
        import fitz
        doc = fitz.open(p)
        count = len(doc)
        doc.close()
        return count
    except Exception:
        pass

    try:
        import pypdf
        reader = pypdf.PdfReader(p)
        return len(reader.pages)
    except Exception:
        pass

    return 1


# ==============================================================================
# DETECCIÓN Y CLASIFICACIÓN JURÍDICA
# ==============================================================================

def detect_instrument_type(text: str) -> str:
    """
    Detecta el tipo de instrumento normativo a partir de su texto o título.
    Retorna una clasificación estándar ('Constitucion', 'Codigo', 'Ley Organica', etc.).
    """
    if not text:
        return 'Instrumento Legal'
    u = text[:2000].upper()
    for keyword, standard_name in TIPOS_INSTRUMENTO:
        if keyword in u:
            return standard_name
    return 'Instrumento Legal'


def detect_legal_categories(text: str) -> list:
    """
    Detecta todas las categorías jurídicas presentes a partir de palabras clave.
    Retorna lista de categorías (penal, civil, administrativo, etc.).
    """
    if not text:
        return ['general']
    u = text[:5000].lower()
    categories = []
    for cat, keywords in CATEGORIAS_JURIDICAS.items():
        if any(kw in u for kw in keywords):
            categories.append(cat)
    return categories if categories else ['general']


def detect_legal_category(text: str) -> str:
    """
    Retorna la primera o principal categoría jurídica detectada.
    """
    cats = detect_legal_categories(text)
    return cats[0] if cats else 'general'


# ==============================================================================
# CONFIGURACIÓN PERSISTENTE (JSON UTF-8)
# ==============================================================================

def load_json_config(path: Union[str, Path], default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Carga un archivo JSON de forma segura garantizando UTF-8."""
    p = Path(path)
    if not p.is_file():
        return default or {}
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"No se pudo leer {p}: {e}")
        return default or {}


def save_json_config(path: Union[str, Path], data: Dict[str, Any]) -> bool:
    """Guarda una estructura de datos en formato JSON formateado en UTF-8."""
    p = Path(path)
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Error escribiendo {p}: {e}")
        return False
