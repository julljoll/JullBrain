"""
metadata_extractor.py
=====================
Extractor de metadatos semanticos para el sistema RAG de Normativas Venezolanas.

Genera un bloque YAML frontmatter con datos estructurados que el indexador
vectorial puede usar para filtrar, clasificar y enriquecer las busquedas.

Autor: Jull Ortiz (Arquitecto de Información IA y bases de datos vectoriales) - Copyright (c) 2026 MIT License
"""

import re
import hashlib
import json
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger("metadata_extractor")

# -----------------------------------------------------------
#  PATRONES
# -----------------------------------------------------------

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

RE_TITULO_OFICIAL = re.compile(
    r'(?:^|\n)\s*#{1,3}\s*([A-Z][A-Z\s]+(?:LEY|CODIGO|CONSTITUCION|DECRETO|RESOLUCION|MANUAL|REGLAMENTO)[A-Z\s]*)',
    re.MULTILINE
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
    ('NORMA', 'Norma'),
    ('GUIA', 'Guia'),
    ('LEY', 'Ley'),
]

CATEGORIAS_JURIDICAS = {
    'penal':          ['penal', 'delito', 'delitos', 'procesal penal', 'pena'],
    'civil':          ['civil', 'contratos', 'obligaciones', 'familia'],
    'administrativo': ['administracion publica', 'administrativo', 'procedimieno administrativo'],
    'laboral':        ['trabajo', 'laboral', 'empleo', 'trabajadores'],
    'tributario':     ['tributario', 'impuesto', 'renta', 'fiscal', 'aduanas'],
    'informatico':    ['informatico', 'informacion', 'datos', 'electronico', 'digital'],
    'constitucional': ['constituc', 'derechos', 'garantias'],
    'comercial':      ['comercio', 'mercantil', 'empresa', 'sociedad'],
    'ambiental':      ['ambiente', 'ambiental', 'ecolog'],
    'forense':        ['forense', 'evidencia', 'cadena de custodia', 'criminalistica'],
    'internacional':  ['iso', 'nist', 'internacional', 'norma internacional'],
}


def sha256_file(file_path: str) -> str:
    """Calcula el hash SHA-256 de un archivo."""
    h = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(65536), b''):
                h.update(chunk)
        return h.hexdigest()
    except Exception as e:
        logger.warning(f"No se pudo calcular SHA-256 para {file_path}: {e}")
        return ""


def detect_instrument_type(text: str) -> str:
    """Detecta tipo de instrumento juridico."""
    text_upper = text[:3000].upper()
    for keyword, tipo in TIPOS_INSTRUMENTO:
        if keyword in text_upper:
            return tipo
    return 'Instrumento Legal'


def detect_legal_category(text: str) -> list:
    """Detecta categorias juridicas del documento."""
    text_lower = text[:5000].lower()
    categories = []
    for cat, keywords in CATEGORIAS_JURIDICAS.items():
        if any(kw in text_lower for kw in keywords):
            categories.append(cat)
    return categories


def extract_official_title(text: str, filename: str = "") -> str:
    """Extrae el titulo oficial del documento."""
    # Intentar extraer del primer encabezado H2
    for line in text.splitlines()[:30]:
        line = line.strip()
        if line.startswith('## ') and len(line) > 5:
            title = line.lstrip('#').strip()
            if len(title) > 5 and not title.startswith('['):
                return title

    # Buscar lineas en mayusculas que parezcan titulos
    lines = text.splitlines()[:50]
    for line in lines:
        stripped = line.strip()
        if len(stripped) > 10 and stripped.isupper() and len(stripped) < 200:
            return stripped.title()

    # Fallback al nombre del archivo
    if filename:
        return Path(filename).stem.replace('_', ' ').replace('-', ' ').title()

    return "Instrumento Legal"


def count_articles(text: str) -> int:
    """Cuenta los articulos detectados en el texto."""
    # En el texto legalizado, los artículos reales están precedidos por ###### Articulo N
    matches = re.findall(r'^######\s+Articulo\s+\d+', text, re.IGNORECASE | re.MULTILINE)
    if matches:
        return len(matches)
    # Fallback si no está legalizado
    return len(re.findall(r'(?<!\w)Art(?:iculo|iculo)?\.?\s+\d+', text, re.IGNORECASE))



def extract_metadata(md_text: str, pdf_path: str = "", filename: str = "") -> dict:
    """
    Extrae todos los metadatos de un documento Markdown.

    Args:
        md_text:  Texto del archivo Markdown
        pdf_path: Ruta al PDF original (para calcular hash)
        filename: Nombre del archivo (para titulo fallback)

    Returns:
        Diccionario con todos los metadatos extraidos
    """
    meta = {}

    # Tipo de instrumento
    meta['tipo_instrumento'] = detect_instrument_type(md_text)

    # Titulo oficial
    meta['nombre_oficial'] = extract_official_title(md_text, filename)

    # Gaceta Oficial
    gaceta_match = RE_GACETA.search(md_text[:4000])
    meta['gaceta_oficial'] = gaceta_match.group(1).strip() if gaceta_match else ""

    # Fecha de publicacion
    fecha_match = RE_FECHA.search(md_text[:4000])
    if fecha_match:
        dia  = fecha_match.group(1).zfill(2)
        mes  = MESES_ES.get(fecha_match.group(2).lower(), '??')
        anio = fecha_match.group(3)
        meta['fecha_publicacion'] = f"{anio}-{mes}-{dia}"
    else:
        meta['fecha_publicacion'] = ""

    # Conteo de articulos detectados
    meta['articulos_detectados'] = count_articles(md_text)

    # Categorias juridicas
    meta['categorias'] = detect_legal_category(md_text)

    # Hash SHA-256 del PDF origen
    if pdf_path and Path(pdf_path).exists():
        meta['hash_pdf_sha256'] = sha256_file(pdf_path)
    else:
        meta['hash_pdf_sha256'] = ""

    # Metadatos de procesamiento
    meta['autor_procesamiento'] = "Jull Ortiz (Arquitecto de Información IA y bases de datos vectoriales)"
    meta['sistema']             = "IBM Docling + LegalProcessor v2"
    meta['version_md']          = "2.0"
    meta['procesado_en']        = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    return meta


def generate_yaml_frontmatter(meta: dict) -> str:
    """
    Genera el bloque YAML frontmatter para el archivo Markdown.

    El frontmatter NO consume espacio de contexto en la mayoria de
    sistemas RAG modernos (es filtrado como metadata del chunk).
    """
    def safe_str(v):
        if isinstance(v, list):
            return '[' + ', '.join(f'"{x}"' for x in v) + ']'
        if v:
            return f'"{v}"'
        return '""'

    lines = ['---']
    lines.append(f'tipo_instrumento: {safe_str(meta.get("tipo_instrumento", ""))}')
    lines.append(f'nombre_oficial: {safe_str(meta.get("nombre_oficial", ""))}')
    lines.append(f'gaceta_oficial: {safe_str(meta.get("gaceta_oficial", ""))}')
    lines.append(f'fecha_publicacion: {safe_str(meta.get("fecha_publicacion", ""))}')
    lines.append(f'articulos_detectados: {meta.get("articulos_detectados", 0)}')
    lines.append(f'categorias: {safe_str(meta.get("categorias", []))}')
    lines.append(f'hash_pdf_sha256: {safe_str(meta.get("hash_pdf_sha256", ""))}')
    lines.append(f'autor_procesamiento: {safe_str(meta.get("autor_procesamiento", ""))}')
    lines.append(f'sistema: {safe_str(meta.get("sistema", ""))}')
    lines.append(f'version_md: {safe_str(meta.get("version_md", ""))}')
    lines.append(f'procesado_en: {safe_str(meta.get("procesado_en", ""))}')
    lines.append('---\n')

    return '\n'.join(lines)


def inject_frontmatter(md_text: str, pdf_path: str = "", filename: str = "") -> str:
    """
    Inyecta el YAML frontmatter al inicio del documento Markdown.
    Si ya existe un frontmatter YAML, lo reemplaza.

    Args:
        md_text:  Texto Markdown completo
        pdf_path: Ruta al PDF original
        filename: Nombre del archivo

    Returns:
        Texto Markdown con frontmatter YAML al inicio
    """
    # Eliminar frontmatter existente si hay
    if md_text.startswith('---\n'):
        end = md_text.find('\n---\n', 4)
        if end > 0:
            md_text = md_text[end + 5:]

    meta = extract_metadata(md_text, pdf_path, filename)
    frontmatter = generate_yaml_frontmatter(meta)

    return frontmatter + md_text


def save_manifest(manifest_path: str, manifest: dict):
    """Guarda el manifesto de conversion JSON."""
    Path(manifest_path).write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding='utf-8'
    )


def load_manifest(manifest_path: str) -> dict:
    """Carga el manifesto de conversion JSON."""
    p = Path(manifest_path)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding='utf-8'))
    except Exception:
        return {}


# -----------------------------------------------------------
#  MODO STANDALONE
# -----------------------------------------------------------
if __name__ == "__main__":
    import sys
    import argparse

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    parser = argparse.ArgumentParser(description="metadata_extractor - Inyector de YAML frontmatter")
    parser.add_argument("input",  help="Archivo Markdown de entrada")
    parser.add_argument("--pdf",  help="Ruta al PDF original para hash SHA-256")
    parser.add_argument("--output", "-o", help="Archivo de salida (default: sobreescribe entrada)")
    args = parser.parse_args()

    try:
        in_path  = Path(args.input)
        out_path = Path(args.output) if args.output else in_path
        text     = in_path.read_text(encoding='utf-8')
        result   = inject_frontmatter(text, args.pdf or "", in_path.stem)
        out_path.write_text(result, encoding='utf-8')
        print(f"[OK] Frontmatter inyectado en: {out_path}")
    except Exception as e:
        print(f"[ERR] {e}")
        sys.exit(1)
