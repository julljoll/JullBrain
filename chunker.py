"""
chunker.py
==========
Generador de chunks semanticos por articulo para RAG preciso.

Toma el Markdown legalizado y genera archivos individuales por articulo
en normativas_chunks/ con sus metadatos completos para indexacion vectorial.

Autor: Jull Ortiz - Copyright (c) 2026 MIT License
"""

import re
import json
import logging
from pathlib import Path
from dataclasses import dataclass, field

logger = logging.getLogger("chunker")

# Rutas predeterminadas (usando rutas dinámicas relativas al directorio del script)
CHUNKS_DIR = Path(__file__).resolve().parent / "normativas_chunks"


@dataclass
class ArticleChunk:
    """Un chunk individual de articulo listo para RAG."""
    ley:        str  = ""
    tipo:       str  = ""
    articulo:   int  = 0
    titulo:     str  = ""
    capitulo:   str  = ""
    seccion:    str  = ""
    libro:      str  = ""
    hint:       str  = ""
    texto:      str  = ""
    gaceta:     str  = ""
    fecha:      str  = ""


def parse_frontmatter(md_text: str) -> tuple[dict, str]:
    """
    Separa el YAML frontmatter del cuerpo del Markdown.
    Retorna (metadata_dict, body_text)
    """
    if not md_text.startswith('---\n'):
        return {}, md_text

    end = md_text.find('\n---\n', 4)
    if end < 0:
        return {}, md_text

    frontmatter_text = md_text[4:end]
    body             = md_text[end + 5:]
    meta             = {}

    for line in frontmatter_text.splitlines():
        if ':' in line:
            key, _, val = line.partition(':')
            key  = key.strip()
            val  = val.strip().strip('"')
            if val.startswith('[') and val.endswith(']'):
                val = [v.strip().strip('"') for v in val[1:-1].split(',') if v.strip()]
            meta[key] = val

    return meta, body


def extract_article_chunks(md_text: str, doc_meta: dict) -> list[ArticleChunk]:
    """
    Extrae los chunks de articulos de un Markdown legalizado.
    Detecta el contexto jerarquico (titulo, capitulo, seccion) de cada articulo.
    """
    chunks = []

    # Extraer la jerarquia estructural del documento completo
    hierarchy_markers = []
    current_libro    = ""
    current_titulo   = ""
    current_capitulo = ""
    current_seccion  = ""

    lines = md_text.splitlines()
    i = 0
    current_article_lines = []
    current_article_num   = None
    current_article_hint  = ""

    while i < len(lines):
        line = lines[i]

        # Detectar cambios de jerarquia
        h2_match = re.match(r'^##\s+(.+)$', line)
        h3_match = re.match(r'^###\s+(.+)$', line)
        h4_match = re.match(r'^####\s+(.+)$', line)
        h5_match = re.match(r'^#####\s+(.+)$', line)
        h6_match = re.match(r'^######\s+Articulo\s+(\d+)(?:\s*[-—]\s*(.+))?$', line, re.IGNORECASE)

        if h2_match:
            txt = h2_match.group(1).strip()
            if 'LIBRO' in txt.upper():
                current_libro = txt
                current_titulo = current_capitulo = current_seccion = ""
            elif 'INDICE' not in txt.upper() and 'PREAMBULO' not in txt.upper():
                current_titulo = txt
                current_capitulo = current_seccion = ""

        elif h3_match:
            txt = h3_match.group(1).strip()
            if 'TITULO' in txt.upper():
                current_titulo = txt
                current_capitulo = current_seccion = ""
            else:
                current_titulo = txt

        elif h4_match:
            txt = h4_match.group(1).strip()
            if 'CAPITULO' in txt.upper():
                current_capitulo = txt
                current_seccion  = ""
            else:
                current_capitulo = txt

        elif h5_match:
            current_seccion = h5_match.group(1).strip()

        elif h6_match:
            # Guardar el articulo anterior
            if current_article_num is not None and current_article_lines:
                body = '\n'.join(current_article_lines).strip()
                if body:
                    chunks.append(ArticleChunk(
                        ley      = doc_meta.get('nombre_oficial', ''),
                        tipo     = doc_meta.get('tipo_instrumento', ''),
                        articulo = current_article_num,
                        titulo   = current_titulo,
                        capitulo = current_capitulo,
                        seccion  = current_seccion,
                        libro    = current_libro,
                        hint     = current_article_hint,
                        texto    = body,
                        gaceta   = doc_meta.get('gaceta_oficial', ''),
                        fecha    = doc_meta.get('fecha_publicacion', ''),
                    ))

            current_article_num   = int(h6_match.group(1))
            current_article_hint  = (h6_match.group(2) or '').strip()
            current_article_lines = []

        elif current_article_num is not None:
            current_article_lines.append(line)

        i += 1

    # Guardar el ultimo articulo
    if current_article_num is not None and current_article_lines:
        body = '\n'.join(current_article_lines).strip()
        if body:
            chunks.append(ArticleChunk(
                ley      = doc_meta.get('nombre_oficial', ''),
                tipo     = doc_meta.get('tipo_instrumento', ''),
                articulo = current_article_num,
                titulo   = current_titulo,
                capitulo = current_capitulo,
                seccion  = current_seccion,
                libro    = current_libro,
                hint     = current_article_hint,
                texto    = body,
                gaceta   = doc_meta.get('gaceta_oficial', ''),
                fecha    = doc_meta.get('fecha_publicacion', ''),
            ))

    return chunks


def chunk_to_markdown(chunk: ArticleChunk) -> str:
    """
    Convierte un ArticleChunk a un Markdown individual con frontmatter.
    """
    # YAML frontmatter
    ubicacion_parts = [chunk.libro, chunk.titulo, chunk.capitulo, chunk.seccion]
    ubicacion = ' > '.join(p for p in ubicacion_parts if p)

    frontmatter_lines = [
        '---',
        f'ley: "{chunk.ley}"',
        f'tipo: "{chunk.tipo}"',
        f'articulo: {chunk.articulo}',
        f'ubicacion: "{ubicacion}"',
        f'titulo: "{chunk.titulo}"',
        f'capitulo: "{chunk.capitulo}"',
        f'seccion: "{chunk.seccion}"',
        f'gaceta_oficial: "{chunk.gaceta}"',
        f'fecha_publicacion: "{chunk.fecha}"',
        '---\n',
    ]

    # Encabezado del articulo
    title_line = f"# Articulo {chunk.articulo}"
    if chunk.hint:
        title_line += f" — {chunk.hint}"
    if chunk.ley:
        title_line += f"\n\n**Ley:** {chunk.ley}"
    if ubicacion:
        title_line += f"\n**Ubicacion:** {ubicacion}\n"

    chunk_footer = """

---

<!-- RAG_IGNORE_START -->
> **DERECHOS DE AUTOR Y LICENCIA MIT**
>
> Este archivo de texto estructurado ha sido generado y optimizado automáticamente para su consumo por sistemas de Inteligencia Artificial (RAG).
> 
> * **Creador:** Jull Ortiz (Arquitecto de Información IA y bases de datos vectoriales)
> * **Propósito:** Avanzar en la transformación tecnológica del sistema de justicia venezolano.
> * **Licencia:** MIT License
> * **Copyright (c) 2026 Jull Ortiz**
>
> Se concede permiso por la presente, sin cargo, a cualquier persona que obtenga una copia de este software y de los archivos de documentación asociados, para utilizarlo sin restricciones, incluyendo el derecho a usar, copiar, modificar, fusionar y publicar. El aviso de copyright anterior y este aviso de permiso se incluirán en todas las copias o partes sustanciales del archivo.
<!-- RAG_IGNORE_END -->
"""
    return '\n'.join(frontmatter_lines) + title_line + '\n\n' + chunk.texto + chunk_footer


def chunk_file(md_path: str, output_dir: str = None) -> list[str]:
    """
    Procesa un archivo Markdown legalizado y genera chunks individuales.

    Args:
        md_path:    Ruta al .md legalizado
        output_dir: Directorio de salida (default: normativas_chunks/<stem>/)

    Returns:
        Lista de rutas de chunks generados
    """
    in_path = Path(md_path)
    if not in_path.exists():
        raise FileNotFoundError(f"No existe: {md_path}")

    text = in_path.read_text(encoding='utf-8', errors='replace')
    doc_meta, body = parse_frontmatter(text)

    # Directorio de salida
    out_dir = Path(output_dir) if output_dir else CHUNKS_DIR / in_path.stem.strip()
    out_dir.mkdir(parents=True, exist_ok=True)

    chunks = extract_article_chunks(body, doc_meta)

    if not chunks:
        logger.warning(f"[{in_path.name}] No se extrajeron chunks. El archivo puede no estar legalizado aun.")
        return []

    generated = []
    for chunk in chunks:
        chunk_md   = chunk_to_markdown(chunk)
        chunk_name = f"articulo_{chunk.articulo:04d}.md"
        chunk_path = out_dir / chunk_name
        chunk_path.write_text(chunk_md, encoding='utf-8')
        generated.append(str(chunk_path))

    # Guardar manifest JSON de chunks
    manifest = {
        'fuente':           in_path.name,
        'ley':              doc_meta.get('nombre_oficial', ''),
        'tipo':             doc_meta.get('tipo_instrumento', ''),
        'chunks_generados': len(generated),
        'articulos':        [c.articulo for c in chunks],
    }
    manifest_path = out_dir / '_manifest.json'
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')

    logger.info(f"[{in_path.name}] {len(generated)} chunks generados en: {out_dir}")
    return generated


def chunk_directory(md_dir: str, output_dir: str = None) -> dict:
    """
    Genera chunks para todos los .md en un directorio.

    Returns:
        Diccionario {filename: [chunk_paths]}
    """
    results = {}
    md_dir_path = Path(md_dir)

    for md_file in sorted(md_dir_path.glob("*.md")):
        try:
            chunk_paths = chunk_file(str(md_file), output_dir)
            results[md_file.name] = chunk_paths
        except Exception as e:
            logger.error(f"Error generando chunks para {md_file.name}: {e}")
            results[md_file.name] = []

    return results


# -----------------------------------------------------------
#  MODO STANDALONE
# -----------------------------------------------------------
if __name__ == "__main__":
    import sys
    import argparse

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    parser = argparse.ArgumentParser(description="chunker - Generador de chunks por articulo para RAG")
    parser.add_argument("input",  help="Archivo .md legalizado o directorio")
    parser.add_argument("--output", "-o", help="Directorio de salida para los chunks")
    args = parser.parse_args()

    target = Path(args.input)
    if target.is_dir():
        results = chunk_directory(str(target), args.output)
        total = sum(len(v) for v in results.values())
        print(f"[OK] {total} chunks generados para {len(results)} archivos.")
    elif target.is_file():
        chunks = chunk_file(str(target), args.output)
        print(f"[OK] {len(chunks)} chunks generados.")
    else:
        print(f"[ERR] No existe: {target}")
        sys.exit(1)
