"""
validator.py
============
Validador de integridad de articulos para el sistema RAG de Normativas Venezolanas.

Verifica que los archivos Markdown generados contengan todos los articulos
sin saltos, duplicados ni articulos con extraccion fallida.
Incluye doble validación cruzada contra el PDF original (PyMuPDF).

Autor: Jull Ortiz - Copyright (c) 2026 Apache License 2.0
"""

import re
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger("validator")

# Minimo de caracteres para considerar un articulo valido
MIN_ARTICLE_CHARS = 50
# Maximo de articulos cortos permitidos antes de emitir advertencia critica
MAX_SHORT_ARTICLES_WARNING = 5

# Umbrales de calidad del skill
QUALITY_THRESHOLDS = {
    'critical': 0.90,   # Por debajo → ERROR, detener/marcar pipeline
    'warning': 0.95,    # Por debajo → WARNING, revisar manualmente  
    'good': 0.98,       # Por debajo → INFO, aceptable
    'excellent': 1.00,  # Perfecto
}

try:
    from rich.console import Console
    from rich.table import Table
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


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
    cross_validation:    Optional[dict] = None  # {pdf_articles, md_articles, missing_in_md, extra_in_md}

    @property
    def quality_score(self) -> float:
        if self.articles_found == 0:
            return 0.0
        total_missing = sum(len(gap) for gap in self.sequence_gaps) if isinstance(self.sequence_gaps, list) else 0
        penalties = total_missing + (len(self.duplicates) * 2) + len(self.short_articles)
        return max(0.0, 1.0 - (penalties / self.articles_found))

    def is_ok(self) -> bool:
        return self.overall_status == "OK"

    def summary(self) -> str:
        total_missing = sum(len(gap) for gap in self.sequence_gaps)
        lines = [
            f"[VALIDACION] {self.filename}",
            f"  [{'OK' if self.articles_found > 0 else '!'}]  Articulos detectados : {self.articles_found}",
            f"  [{'OK' if not self.sequence_gaps else '!'}]  Saltos de secuencia  : {total_missing} artículos faltantes",
            f"  [{'OK' if not self.duplicates else '!'}]  Duplicados           : {len(self.duplicates)}",
            f"  [{'OK' if len(self.short_articles) <= MAX_SHORT_ARTICLES_WARNING else '!'}]  Articulos cortos     : {len(self.short_articles)}",
            f"  [{'OK' if self.has_toc else 'i'}]  Tabla de contenido   : {'Si' if self.has_toc else 'No'}",
            f"  [{'OK' if self.has_frontmatter else 'i'}]  YAML Frontmatter     : {'Si' if self.has_frontmatter else 'No'}",
            f"  Score de calidad    : {self.quality_score:.1%}",
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

    # Determinar estado global usando score de calidad y thresholds
    score = report.quality_score
    total_missing = sum(len(gap) for gap in report.sequence_gaps)

    if score < QUALITY_THRESHOLDS['critical'] or total_missing > 5 or len(report.duplicates) > 2:
        report.overall_status = "ERROR"
    elif score < QUALITY_THRESHOLDS['good'] or total_missing > 0 or report.duplicates or len(report.short_articles) > MAX_SHORT_ARTICLES_WARNING:
        report.overall_status = "WARNING"
    else:
        report.overall_status = "OK"

    return report


def cross_validate_against_pdf(pdf_path: str, md_path: str) -> dict:
    """
    Doble validación cruzada: extrae artículos del PDF original
    con PyMuPDF y los contrasta con los detectados en el Markdown.
    Retorna diccionario con discrepancias para revisión humana.
    
    Este método implementa el Principio 10 (Doble Validación Cruzada)
    del proyecto JullBrain: todo documento debe ser validado por al menos
    dos métodos independientes de conteo de artículos.
    """
    result = {
        'pdf_articles': [],
        'md_articles': [],
        'missing_in_md': [],
        'extra_in_md': [],
        'match': False,
        'error': None
    }
    
    # 1. Extraer artículos del Markdown
    md_file = Path(md_path)
    if md_file.exists():
        md_text = md_file.read_text(encoding='utf-8', errors='replace')
        md_articles = extract_article_blocks(md_text)
        result['md_articles'] = sorted(set(a['number'] for a in md_articles))
    else:
        result['error'] = f"Archivo MD no encontrado: {md_path}"
        return result
    
    # 2. Extraer artículos directamente del PDF con PyMuPDF
    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        result['error'] = f"PDF original no encontrado: {pdf_path}"
        return result
    
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(str(pdf_file))
        full_text = ""
        for page in doc:
            full_text += page.get_text() + "\n"
        doc.close()
        
        # Patrón independiente del legalizer para detección directa
        pdf_art_pattern = re.compile(
            r'(?:^|\n)\s*(?:Art[íi]culo|Art\.?)\s+(\d+)',
            re.IGNORECASE
        )
        pdf_nums = sorted(set(int(m.group(1)) for m in pdf_art_pattern.finditer(full_text)))
        result['pdf_articles'] = pdf_nums
        
    except ImportError:
        result['error'] = "PyMuPDF (fitz) no disponible para validación cruzada"
        return result
    except Exception as e:
        result['error'] = f"Error leyendo PDF: {e}"
        return result
    
    # 3. Calcular discrepancias
    pdf_set = set(result['pdf_articles'])
    md_set = set(result['md_articles'])
    
    result['missing_in_md'] = sorted(pdf_set - md_set)
    result['extra_in_md'] = sorted(md_set - pdf_set)
    result['match'] = (pdf_set == md_set)
    
    if result['missing_in_md']:
        logger.warning(
            f"[CROSS-VAL] {pdf_file.name}: {len(result['missing_in_md'])} artículos "
            f"en PDF no encontrados en MD: {result['missing_in_md'][:10]}"
        )
    if result['extra_in_md']:
        logger.warning(
            f"[CROSS-VAL] {pdf_file.name}: {len(result['extra_in_md'])} artículos "
            f"en MD no encontrados en PDF: {result['extra_in_md'][:10]}"
        )
    if result['match']:
        logger.info(f"[CROSS-VAL] {pdf_file.name}: Validación cruzada OK — {len(pdf_set)} artículos coinciden.")
    
    return result


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
    if RICH_AVAILABLE:
        console = Console()
        table = Table(title="JullBrain — Reporte de Validación de Normativas RAG", show_lines=True, box=box.MINIMAL_DOUBLE_HEAD)

        table.add_column("Documento", style="cyan", max_width=35)
        table.add_column("Artículos", justify="right")
        table.add_column("Faltantes", justify="right", style="yellow")
        table.add_column("Duplicados", justify="right", style="red")
        table.add_column("Cortos", justify="right", style="yellow")
        table.add_column("TOC", justify="center")
        table.add_column("Score", justify="right")
        table.add_column("Estado", justify="center")

        for r in reports:
            score = r.quality_score
            score_color = "green" if score >= 0.98 else "yellow" if score >= 0.95 else "red"
            status = "✅ OK" if r.overall_status == "OK" else "⚠️ WARNING" if r.overall_status == "WARNING" else "❌ ERROR"

            total_missing = sum(len(gap) for gap in r.sequence_gaps)

            table.add_row(
                r.filename[:35],
                str(r.articles_found),
                str(total_missing) if total_missing > 0 else "-",
                str(len(r.duplicates)) if r.duplicates else "-",
                str(len(r.short_articles)) if r.short_articles else "-",
                "✓" if r.has_toc else "✗",
                f"[{score_color}]{score:.1%}[/{score_color}]",
                status,
            )

        console.print(table)

        # Resumen consolidado
        total = len(reports)
        ok = sum(1 for r in reports if r.overall_status == "OK")
        warning = sum(1 for r in reports if r.overall_status == "WARNING")
        error = sum(1 for r in reports if r.overall_status == "ERROR")
        total_articles = sum(r.articles_found for r in reports)

        console.print(f"\n[bold]Total:[/bold] {total} documentos | "
                      f"[green]{ok} OK[/green] | "
                      f"[yellow]{warning} Advertencias[/yellow] | "
                      f"[red]{error} Errores[/red] | "
                      f"Total artículos: {total_articles}")
    else:
        total   = len(reports)
        ok      = sum(1 for r in reports if r.overall_status == "OK")
        warning = sum(1 for r in reports if r.overall_status == "WARNING")
        error   = sum(1 for r in reports if r.overall_status == "ERROR")
        total_articles = sum(r.articles_found for r in reports)

        print("\n" + "=" * 70)
        print("  RESUMEN DE VALIDACION - NORMATIVAS RAG (Fallback Text)")
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
