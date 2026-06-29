"""
validator.py
============
Validador de integridad de articulos para el sistema RAG de Normativas Venezolanas.

Verifica que los archivos Markdown generados contengan todos los articulos
sin saltos, duplicados ni articulos con extraccion fallida.

Autor: Jull Ortiz - Copyright (c) 2026 MIT License
"""

import re
import logging
from pathlib import Path
from dataclasses import dataclass, field

logger = logging.getLogger("validator")

# Minimo de caracteres para considerar un articulo valido
MIN_ARTICLE_CHARS = 50
# Maximo de articulos cortos permitidos antes de emitir advertencia critica
MAX_SHORT_ARTICLES_WARNING = 5


@dataclass
class ValidationReport:
    """Resultado de la validacion de un documento."""
    filename:            str   = ""
    articles_found:      int   = 0
    articles_expected:   int   = 0
    short_articles:      list  = field(default_factory=list)
    sequence_gaps:       list  = field(default_factory=list)
    duplicates:          list  = field(default_factory=list)
    has_toc:             bool  = False
    has_frontmatter:     bool  = False
    overall_status:      str   = "UNKNOWN"  # OK | WARNING | ERROR

    def is_ok(self) -> bool:
        return self.overall_status == "OK"

    def summary(self) -> str:
        lines = [
            f"[VALIDACION] {self.filename}",
            f"  [{'OK' if self.articles_found > 0 else '!'}]  Articulos detectados : {self.articles_found}",
            f"  [{'OK' if not self.sequence_gaps else '!'}]  Saltos de secuencia  : {len(self.sequence_gaps)}",
            f"  [{'OK' if not self.duplicates else '!'}]  Duplicados           : {len(self.duplicates)}",
            f"  [{'OK' if len(self.short_articles) <= MAX_SHORT_ARTICLES_WARNING else '!'}]  Articulos cortos     : {len(self.short_articles)}",
            f"  [{'OK' if self.has_toc else 'i'}]  Tabla de contenido   : {'Si' if self.has_toc else 'No'}",
            f"  [{'OK' if self.has_frontmatter else 'i'}]  YAML Frontmatter     : {'Si' if self.has_frontmatter else 'No'}",
            f"  >>> Estado global: {self.overall_status}",
        ]
        if self.sequence_gaps:
            lines.append(f"  [GAPS] {self.sequence_gaps}")
        if self.duplicates:
            lines.append(f"  [DUPS] {self.duplicates}")
        if self.short_articles:
            lines.append(f"  [SHORT] Arts. cortos: {self.short_articles[:10]}")
        return '\n'.join(lines)


def extract_article_blocks(md_text: str) -> list[dict]:
    """
    Extrae todos los bloques de articulos del Markdown estructurado.
    Compatible con el formato del legalizer (######) y con el formato crudo.
    """
    articles = []

    # Patron 1: formato legalizer (###### Articulo N)
    header_pattern = re.compile(
        r'#{4,6}\s+Articulo\s+(\d+)(?:\s*[-—]\s*([^\n]+))?\n(.*?)(?=\n#{4,6}\s+Articulo\s+\d+|\Z)',
        re.IGNORECASE | re.DOTALL
    )
    for m in header_pattern.finditer(md_text):
        articles.append({
            'number': int(m.group(1)),
            'hint':   (m.group(2) or '').strip(),
            'body':   m.group(3).strip(),
            'format': 'legalizer'
        })

    # Patron 2: formato crudo (Articulo N. texto)
    if not articles:
        for m in re.finditer(
            r'(?<!\w)Articulo\s+(\d+)\.\s*(.*?)(?=(?<!\w)Articulo\s+\d+\.|\Z)',
            md_text,
            re.IGNORECASE | re.DOTALL
        ):
            body = m.group(2).strip()
            articles.append({
                'number': int(m.group(1)),
                'hint':   '',
                'body':   body,
                'format': 'raw'
            })

    return sorted(articles, key=lambda x: x['number'])


def validate_sequence(articles: list[dict]) -> tuple[list, list]:
    """
    Valida la secuencia de articulos.
    Retorna (gaps, duplicates)
    """
    gaps       = []
    duplicates = []

    if not articles:
        return gaps, duplicates

    nums = [a['number'] for a in articles]

    for i in range(1, len(nums)):
        expected = nums[i - 1] + 1
        actual   = nums[i]
        if actual > expected:
            missing = list(range(expected, actual))
            gaps.append({'between': (nums[i - 1], actual), 'missing': missing})
        elif actual == nums[i - 1]:
            duplicates.append(actual)

    return gaps, duplicates


def validate_article_length(articles: list[dict]) -> list[int]:
    """
    Detecta articulos con cuerpo sospechosamente corto.
    Retorna lista de numeros de articulo cortos.
    """
    short = []
    for art in articles:
        if len(art['body']) < MIN_ARTICLE_CHARS:
            short.append(art['number'])
    return short


def validate_md_file(md_path: str) -> ValidationReport:
    """
    Valida un archivo Markdown completo.

    Args:
        md_path: Ruta al archivo .md

    Returns:
        ValidationReport con todos los resultados
    """
    path = Path(md_path)
    report = ValidationReport(filename=path.name)

    if not path.exists():
        report.overall_status = "ERROR"
        logger.error(f"Archivo no encontrado: {md_path}")
        return report

    text = path.read_text(encoding='utf-8', errors='replace')

    # Verificar frontmatter YAML
    report.has_frontmatter = text.startswith('---\n')

    # Verificar tabla de contenido
    report.has_toc = bool(re.search(r'INDICE\s+DE\s+ARTICULOS', text, re.IGNORECASE))

    # Extraer articulos
    articles = extract_article_blocks(text)
    report.articles_found = len(articles)

    if not articles:
        report.overall_status = "WARNING"
        logger.warning(f"[{path.name}] No se detectaron articulos en el archivo.")
        return report

    # Validar secuencia
    gaps, duplicates = validate_sequence(articles)
    report.sequence_gaps = [g['missing'] for g in gaps]
    report.duplicates    = duplicates

    # Validar longitud
    report.short_articles = validate_article_length(articles)

    # Determinar estado global
    if gaps and len([n for g in gaps for n in g['missing']]) > 5:
        report.overall_status = "ERROR"
    elif gaps or duplicates or len(report.short_articles) > MAX_SHORT_ARTICLES_WARNING:
        report.overall_status = "WARNING"
    else:
        report.overall_status = "OK"

    return report


def validate_directory(md_dir: str) -> list[ValidationReport]:
    """
    Valida todos los archivos .md en un directorio.

    Args:
        md_dir: Directorio con archivos Markdown

    Returns:
        Lista de ValidationReport para cada archivo
    """
    reports = []
    md_path = Path(md_dir)

    for md_file in sorted(md_path.glob("*.md")):
        report = validate_md_file(str(md_file))
        reports.append(report)

    return reports


def print_validation_summary(reports: list[ValidationReport]):
    """Imprime un resumen consolidado de las validaciones."""
    total   = len(reports)
    ok      = sum(1 for r in reports if r.overall_status == "OK")
    warning = sum(1 for r in reports if r.overall_status == "WARNING")
    error   = sum(1 for r in reports if r.overall_status == "ERROR")
    total_articles = sum(r.articles_found for r in reports)

    print("\n" + "=" * 70)
    print("  RESUMEN DE VALIDACION - NORMATIVAS RAG")
    print("=" * 70)
    print(f"  Archivos validados  : {total}")
    print(f"  [OK] Sin problemas  : {ok}")
    print(f"  [!]  Con advertencia: {warning}")
    print(f"  [X]  Con errores    : {error}")
    print(f"  Total de articulos  : {total_articles}")
    print("=" * 70 + "\n")

    for report in reports:
        print(report.summary())
        print()


# -----------------------------------------------------------
#  MODO STANDALONE
# -----------------------------------------------------------
if __name__ == "__main__":
    import sys
    import argparse

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    parser = argparse.ArgumentParser(description="validator - Validador de integridad de Normativas RAG")
    parser.add_argument("path", help="Archivo .md o directorio con archivos .md")
    args = parser.parse_args()

    target = Path(args.path)
    if target.is_dir():
        reports = validate_directory(str(target))
    elif target.is_file():
        reports = [validate_md_file(str(target))]
    else:
        print(f"[ERR] No existe: {target}")
        sys.exit(1)

    print_validation_summary(reports)

    # Exit code segun estado
    has_errors = any(r.overall_status == "ERROR" for r in reports)
    sys.exit(1 if has_errors else 0)
