"""
legalizer.py
============
Post-procesador legal para el sistema RAG de Normativas Venezolanas.

Toma el Markdown crudo generado por IBM Docling y produce un Markdown
estructurado con jerarquia legal formal:
  LIBRO > TITULO > CAPITULO > SECCION > Articulo > Paragrafo

# Autor: Jull Ortiz (Arquitecto de Información IA y bases de datos vectoriales) - Copyright (c) 2026 Apache License 2.0
"""

import re
import logging
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger("legalizer")

# -----------------------------------------------------------
#  PATRONES REGEX - Jerarquia Legal Venezolana
# -----------------------------------------------------------

RE_LIBRO     = re.compile(r'^\s*#*\s*LIBRO\s+([IVXLCDM]+|[0-9]+)\b(.*)?$',       re.IGNORECASE | re.MULTILINE)
RE_TITULO    = re.compile(r'^\s*#*\s*T[IÍ]TULO\s+([IVXLCDM]+|[0-9]+)\b(.*)?$',   re.IGNORECASE | re.MULTILINE)
RE_CAPITULO  = re.compile(r'^\s*#*\s*CAP[IÍ]TULO\s+([IVXLCDM]+|[0-9]+|[A-Z]+)\b(.*)?$', re.IGNORECASE | re.MULTILINE)
RE_SECCION   = re.compile(r'^\s*#*\s*SECCI[OÓ]N\s+([IVXLCDM]+|[0-9]+|[A-Z]+)\b(.*)?$',  re.IGNORECASE | re.MULTILINE)

RE_PAGE_NUM  = re.compile(
    r'(?:^|\n)\s*-\s*\d{1,4}\s*-\s*(?:\n|$)'
    r'|(?:^|\n)\s*P[aá]g(?:ina)?\.?\s*\d+\s*(?:\n|$)',
    re.IGNORECASE | re.MULTILINE
)

RE_OCR_NOISE = re.compile(r'[□■▪▫]{3,}')
RE_GACETA    = re.compile(r'Gaceta\s+Oficial\s+N[°º\.]\s*([\d.]+\s*(?:Extraordinario)?)', re.IGNORECASE)
RE_FECHA     = re.compile(
    r'(\d{1,2})\s+de\s+(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\s+(?:de\s+)?(\d{4})',
    re.IGNORECASE
)

MESES_ES = {
    'enero': '01', 'febrero': '02', 'marzo': '03', 'abril': '04',
    'mayo': '05', 'junio': '06', 'julio': '07', 'agosto': '08',
    'septiembre': '09', 'octubre': '10', 'noviembre': '11', 'diciembre': '12'
}


def clean_noise(text):
    # 1. Eliminar números de página y ruido de OCR (cuadros/símbolos ilegibles)
    text = RE_PAGE_NUM.sub('\n', text)
    text = RE_OCR_NOISE.sub('', text)
    
    # 2. Corregir palabras partidas por salto de línea según instruccion docling.md (ej: constitu-\nción -> constitución)
    text = re.sub(r'(\b[a-zA-ZáéíóúÁÉÍÓÚñÑ]+)-\s*\n\s*([a-zA-ZáéíóúÁÉÍÓÚñÑ]+\b)', r'\1\2', text)
    
    # 3. Normalizar múltiples saltos de línea innecesarios
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def normalize_article_marker(text):
    """
    Normaliza TODAS las variantes de marcadores de articulo a 'ARTICULO_N_SEP'.
    Maneja: Articulo / Articulo / Art. con o sin tilde, con °, -, . o nada.
    Maneja rangos derogados (ej. Artículos 6 al 10 -> ARTICULO_6_SEP ... ARTICULO_10_SEP).
    Solo se aplica si el marcador está al inicio de una línea o del documento,
    para evitar emparejar citas o referencias cruzadas dentro de oraciones.
    """
    # 1. Normalizar rangos derogados (ej. Artículos 6 al 10 / Art. 15 a 20)
    range_pattern = re.compile(
        r'(^|\n)(\s*(?:#{1,6}\s+)?(?:\*\*|__)?)\b(?:Art[\xed\xcc\u00ed\u0131]?culos|Artic[uú]los|Art[i\xed]culos|Arts\.?)\s+(\d+)\s+(?:al?|a)\s+(\d+)\s*(?:[°\xba]|[-\u2013\.\s]*)?(?:\*\*|__)?',
        re.IGNORECASE
    )
    def expand_range(m):
        start_art = int(m.group(3))
        end_art = int(m.group(4))
        prefix = f"{m.group(1)}{m.group(2)}"
        if start_art < end_art and (end_art - start_art) <= 50:
            expanded = []
            for n in range(start_art, end_art + 1):
                expanded.append(f"{prefix}ARTICULO_{n}_SEP (Derogado)")
            return "\n".join(expanded)
        return m.group(0)

    text = range_pattern.sub(expand_range, text)

    # 2. Normalizar artículos individuales
    pattern = re.compile(
        r'(^|\n)(\s*(?:#{1,6}\s+)?(?:\*\*|__)?)\b(?:Art[\xed\xcc\u00ed\u0131]?culo|Artic[uú]lo|Art[i\xed]culo|Art\.?)\s+(?:N[°º\.]\s*)?(\d+)\s*(?:[°\xba]|[-\u2013\.\s]*)?(?:\*\*|__)?',
        re.IGNORECASE
    )
    text = pattern.sub(
        lambda m: f"{m.group(1)}{m.group(2)}ARTICULO_{m.group(3)}_SEP ",
        text
    )
    return text


def detect_instrument_type(text):
    u = text[:2000].upper()
    if 'CONSTITUCI' in u: return 'Constitucion'
    if 'CODIGO' in u or 'CÓDIGO' in u: return 'Codigo'
    if 'LEY ORGANICA' in u or 'LEY ORGÁNICA' in u: return 'Ley Organica'
    if 'LEY ESPECIAL' in u: return 'Ley Especial'
    if 'DECRETO' in u: return 'Decreto'
    if 'RESOLUCION' in u or 'RESOLUCIÓN' in u: return 'Resolucion'
    if 'MANUAL' in u: return 'Manual'
    if 'REGLAMENTO' in u: return 'Reglamento'
    if 'LEY' in u: return 'Ley'
    return 'Instrumento Legal'


def extract_preamble_metadata(text):
    meta = {}
    gaceta_match = RE_GACETA.search(text[:3000])
    if gaceta_match:
        meta['gaceta_oficial'] = gaceta_match.group(1).strip()
    fecha_match = RE_FECHA.search(text[:3000])
    if fecha_match:
        dia  = fecha_match.group(1).zfill(2)
        mes  = MESES_ES.get(fecha_match.group(2).lower(), '??')
        anio = fecha_match.group(3)
        meta['fecha_publicacion'] = f"{anio}-{mes}-{dia}"
    return meta


def split_into_articles(text):
    """
    Divide el texto en bloques de articulos usando el marcador normalizado ARTICULO_N_SEP.
    Retorna lista de tuplas: (numero_articulo, hint_titulo, cuerpo_texto)
    """
    positions = []
    for m in re.finditer(
        r'ARTICULO_(\d+)_SEP\s*',
        text
    ):
        num = int(m.group(1))
        positions.append((num, m.start(), m.end()))

    if not positions:
        return []

    articles = []
    for i, (num, start, end) in enumerate(positions):
        next_start = positions[i + 1][1] if i + 1 < len(positions) else len(text)
        body = text[end:next_start].strip()
        # Eliminar el marcador propio si quedó en el cuerpo
        body = re.sub(r'^ARTICULO_\d+_SEP\s*', '', body).strip()

        hint = ""
        hint_match = re.match(r'^([A-Za-záéíóúÁÉÍÓÚñÑ][^.]{3,60})\.\s+', body)
        if hint_match and len(hint_match.group(1).split()) <= 8:
            hint = hint_match.group(1).strip()

        articles.append((num, hint, body))

    return articles


def validate_article_sequence(articles):
    issues = []
    if not articles:
        return issues
    nums = [a[0] for a in articles]
    for i in range(1, len(nums)):
        expected = nums[i - 1] + 1
        actual   = nums[i]
        if actual > expected:
            issues.append({'tipo': 'salto', 'descripcion': f"Salto Art. {nums[i-1]} -> Art. {actual} (faltan: {list(range(expected, actual))})"})
        elif actual == nums[i - 1]:
            issues.append({'tipo': 'duplicado', 'descripcion': f"Art. {actual} duplicado"})
    return issues


def track_hierarchy(text_before):
    ctx = {'libro': '', 'titulo': '', 'capitulo': '', 'seccion': ''}
    for m in RE_LIBRO.finditer(text_before):
        desc = (m.group(2) or '').strip().strip('-').strip()
        ctx['libro'] = f"LIBRO {m.group(1)}" + (f" - {desc}" if desc else '')
    for m in RE_TITULO.finditer(text_before):
        desc = (m.group(2) or '').strip().strip('-').strip()
        ctx['titulo'] = f"TITULO {m.group(1)}" + (f" - {desc}" if desc else '')
    for m in RE_CAPITULO.finditer(text_before):
        desc = (m.group(2) or '').strip().strip('-').strip()
        ctx['capitulo'] = f"CAPITULO {m.group(1)}" + (f" - {desc}" if desc else '')
    for m in RE_SECCION.finditer(text_before):
        desc = (m.group(2) or '').strip().strip('-').strip()
        ctx['seccion'] = f"SECCION {m.group(1)}" + (f" - {desc}" if desc else '')
    return ctx


def generate_toc(articles_with_ctx):
    lines = [
        "## INDICE DE ARTICULOS\n",
        "| Art. | Descripcion | Ubicacion |",
        "|------|-------------|-----------|"
    ]
    for item in articles_with_ctx:
        num  = item['number']
        hint = item.get('hint', '') or (item['body'][:60].replace('\n', ' ').strip() + '...')
        ubicacion_parts = [item.get('titulo', ''), item.get('capitulo', '')]
        ubicacion = ' / '.join(p for p in ubicacion_parts if p) or '---'
        lines.append(f"| {num} | {hint} | {ubicacion} |")
    return '\n'.join(lines)


def legalize(raw_markdown, document_name=""):
    """
    Funcion principal del legalizer.
    Toma Markdown crudo de Docling y retorna Markdown estructurado para RAG.
    """
    text = clean_noise(raw_markdown)
    meta = extract_preamble_metadata(text)
    tipo = detect_instrument_type(text)
    text = normalize_article_marker(text)
    articles_raw = split_into_articles(text)

    if not articles_raw:
        logger.warning(f"[{document_name}] No se detectaron articulos. Retornando texto limpio.")
        return text

    logger.info(f"[{document_name}] Detectados {len(articles_raw)} articulos.")

    issues = validate_article_sequence(articles_raw)
    if issues:
        for issue in issues:
            logger.warning(f"[{document_name}] {issue['tipo'].upper()}: {issue['descripcion']}")
    else:
        logger.info(f"[{document_name}] Secuencia de articulos: OK (sin saltos).")

    # El texto ya fue normalizado por normalize_article_marker,
    # por lo que los marcadores de artículo ahora tienen el formato 'ARTICULO_N_SEP '
    first_art_pos = text.find(f"ARTICULO_{articles_raw[0][0]}_SEP ")
    preambulo_text = text[:first_art_pos].strip() if first_art_pos > 0 else ""

    articles_with_ctx = []
    for num, hint, body in articles_raw:
        art_marker = f"ARTICULO_{num}_SEP "
        art_pos    = text.find(art_marker)
        ctx        = track_hierarchy(text[:art_pos]) if art_pos > 0 else {}
        
        # Limpiar encabezados jerárquicos del cuerpo de este artículo
        clean_body_lines = []
        for line in body.splitlines():
            if RE_LIBRO.match(line) or RE_TITULO.match(line) or RE_CAPITULO.match(line) or RE_SECCION.match(line):
                continue
            clean_body_lines.append(line)
        clean_body = '\n'.join(clean_body_lines).strip()
        
        articles_with_ctx.append({
            'number':   num,
            'hint':     hint,
            'body':     clean_body,
            'libro':    ctx.get('libro', ''),
            'titulo':   ctx.get('titulo', ''),
            'capitulo': ctx.get('capitulo', ''),
            'seccion':  ctx.get('seccion', ''),
        })

    output_parts = []

    if preambulo_text:
        preambulo_lines = [l for l in preambulo_text.splitlines() if l.strip() and not l.strip().startswith('#')]
        if preambulo_lines:
            output_parts.append("## PREAMBULO\n")
            output_parts.append('\n'.join(preambulo_lines))
            output_parts.append('\n\n---\n')

    output_parts.append(generate_toc(articles_with_ctx))
    output_parts.append('\n\n---\n')

    prev_titulo   = None
    prev_capitulo = None
    prev_seccion  = None
    prev_libro    = None

    for item in articles_with_ctx:
        if item['libro'] and item['libro'] != prev_libro:
            output_parts.append(f"\n## {item['libro']}\n")
            prev_libro = item['libro']
            prev_titulo = prev_capitulo = prev_seccion = None

        if item['titulo'] and item['titulo'] != prev_titulo:
            output_parts.append(f"\n### {item['titulo']}\n")
            prev_titulo = item['titulo']
            prev_capitulo = prev_seccion = None

        if item['capitulo'] and item['capitulo'] != prev_capitulo:
            output_parts.append(f"\n#### {item['capitulo']}\n")
            prev_capitulo = item['capitulo']
            prev_seccion  = None

        if item['seccion'] and item['seccion'] != prev_seccion:
            output_parts.append(f"\n##### {item['seccion']}\n")
            prev_seccion = item['seccion']

        num  = item['number']
        hint = item['hint']
        if hint:
            output_parts.append(f"\n###### Articulo {num} - {hint}\n")
        else:
            output_parts.append(f"\n###### Articulo {num}\n")

        output_parts.append(f"{item['body'].strip()}\n")

    return '\n'.join(output_parts)


def legalize_file(input_path, output_path=None):
    """
    Procesa un archivo Markdown y escribe el resultado legalizado.
    Soporta dos formatos de entrada:
    1. Archivos existentes con header de licencia (#/> [!NOTE]...---\ncontent\n---\nfooter)
    2. Archivos nuevos con YAML frontmatter (---\nkey: val\n---\ncontent)
    """
    from pathlib import Path

    in_path  = Path(input_path)
    out_path = Path(output_path) if output_path else in_path

    if not in_path.exists():
        raise FileNotFoundError(f"No existe el archivo: {in_path}")

    raw = in_path.read_text(encoding='utf-8')

    # Detectar si es un archivo con YAML frontmatter (nuevo formato)
    if raw.startswith('---\n'):
        end_fm = raw.find('\n---\n', 4)
        if end_fm > 0:
            mit_header   = raw[:end_fm + 5]
            rest         = raw[end_fm + 5:]
        else:
            mit_header   = ''
            rest         = raw
    else:
        first_sep = raw.find('\n---\n')
        if first_sep >= 0:
            mit_header   = raw[:first_sep + 5]
            rest         = raw[first_sep + 5:]
        else:
            mit_header   = ''
            rest         = raw

    # Buscar el footer robustamente para excluirlo del body
    footer_idx = rest.rfind('FIN DEL DOCUMENTO ESTRUCTURADO')
    if footer_idx >= 0:
        last_sep = rest.rfind('\n---\n', 0, footer_idx)
        if last_sep >= 0:
            docling_body = rest[:last_sep].strip()
        else:
            docling_body = rest.strip()
    else:
        last_sep = rest.rfind('\n---\n')
        if last_sep >= 0:
            docling_body = rest[:last_sep].strip()
        else:
            docling_body = rest.strip()

    structured   = legalize(docling_body, document_name=in_path.stem)
    final_output = mit_header + '\n' + structured
    out_path.write_text(final_output, encoding='utf-8')
    logger.info(f"[OK] Archivo legalizado guardado en: {out_path}")
    return str(out_path)


# -----------------------------------------------------------
#  MODO STANDALONE
# -----------------------------------------------------------
if __name__ == "__main__":
    import sys
    import argparse

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    parser = argparse.ArgumentParser(description="Legalizer - Post-procesador de Normativas RAG")
    parser.add_argument("input", help="Archivo Markdown de entrada (crudo Docling)")
    parser.add_argument("--output", "-o", help="Archivo Markdown de salida (default: sobreescribe entrada)")
    args = parser.parse_args()

    try:
        result = legalize_file(args.input, args.output)
        print(f"[OK] Archivo procesado: {result}")
    except Exception as e:
        print(f"[ERR] Error: {e}")
        sys.exit(1)
