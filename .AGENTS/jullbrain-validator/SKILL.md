---
name: JullBrain-validator
description: >
  Skill para el mÃ³dulo validator.py de JullBrain. Ãšsalo cuando necesites: verificar la
  integridad de artÃ­culos despuÃ©s de la conversiÃ³n, detectar artÃ­culos faltantes o
  duplicados, identificar artÃ­culos corruptos (muy cortos o ilegibles), validar que
  el frontmatter YAML estÃ© completo, generar reportes de calidad del pipeline, o
  configurar umbrales de alerta. TambiÃ©n aplica cuando un documento convertido da
  resultados inconsistentes y necesitas diagnosticar quÃ© fallÃ³ en el pipeline.
  Trigger siempre que el usuario mencione: validar normativas, artÃ­culos faltantes,
  saltos en secuencia, chunks corruptos, reporte de integridad, validator.py.
---

# JullBrain Validator â€” Skill Especializado

## Checks de ValidaciÃ³n

| Check | QuÃ© detecta | Severidad |
|-------|------------|-----------|
| Secuencia numÃ©rica | ArtÃ­culos saltados (1,2,4 â€” falta el 3) | WARNING |
| Duplicados | Mismo nÃºmero de artÃ­culo dos veces | ERROR |
| ArtÃ­culos cortos | Contenido < 50 caracteres (OCR fallido) | WARNING |
| Frontmatter YAML | Campos requeridos ausentes o `N/D` | WARNING |
| TOC presente | El Ã­ndice de artÃ­culos existe en el .md | INFO |
| SHA-256 consistente | El hash del chunk coincide con el del PDF | ERROR |
| ArtÃ­culos derogados | Detectar `(Derogado)` y marcarlo en metadata | INFO |

---

## ImplementaciÃ³n del Validador

```python
import re
import yaml
from pathlib import Path
from dataclasses import dataclass, field
from rich.console import Console
from rich.table import Table

console = Console()

@dataclass
class ValidationReport:
    document: str
    total_articles: int = 0
    missing: list[int] = field(default_factory=list)
    duplicates: list[int] = field(default_factory=list)
    short_articles: list[int] = field(default_factory=list)
    frontmatter_issues: list[str] = field(default_factory=list)
    has_toc: bool = False
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    
    @property
    def is_healthy(self) -> bool:
        return len(self.errors) == 0
    
    @property
    def quality_score(self) -> float:
        if self.total_articles == 0:
            return 0.0
        penalties = len(self.missing) + (len(self.duplicates) * 2) + len(self.short_articles)
        return max(0.0, 1.0 - (penalties / self.total_articles))


def validate_document(md_path: str) -> ValidationReport:
    """Valida un documento Markdown legalizado completo."""
    path = Path(md_path)
    report = ValidationReport(document=path.name)
    
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # â”€â”€ 1. Validar frontmatter â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    if content.startswith('---\n'):
        end = content.find('\n---\n', 3)
        if end != -1:
            try:
                metadata = yaml.safe_load(content[3:end])
                required = ['tipo_instrumento', 'nombre_oficial', 'gaceta_oficial',
                           'fecha_publicacion', 'hash_pdf_sha256']
                for field_name in required:
                    if field_name not in metadata:
                        report.frontmatter_issues.append(f"Falta: {field_name}")
                    elif metadata[field_name] == "N/D":
                        report.frontmatter_issues.append(f"No detectado: {field_name}")
            except yaml.YAMLError as e:
                report.errors.append(f"YAML invÃ¡lido: {e}")
        else:
            report.errors.append("Frontmatter YAML no cerrado correctamente")
    else:
        report.errors.append("Sin frontmatter YAML")
    
    # â”€â”€ 2. Detectar artÃ­culos â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    article_pattern = re.compile(r'^#{6}\s+Art[Ã­i]culo\s+(\d+)', re.MULTILINE)
    matches = article_pattern.findall(content)
    article_nums = [int(n) for n in matches]
    report.total_articles = len(article_nums)
    
    if not article_nums:
        report.errors.append("No se detectaron artÃ­culos en el documento")
        return report
    
    # â”€â”€ 3. Verificar secuencia â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    expected = set(range(min(article_nums), max(article_nums) + 1))
    found = set(article_nums)
    report.missing = sorted(expected - found)
    
    # â”€â”€ 4. Detectar duplicados â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    seen = set()
    for n in article_nums:
        if n in seen:
            report.duplicates.append(n)
        seen.add(n)
    
    # â”€â”€ 5. Detectar artÃ­culos cortos â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    article_blocks = re.split(r'^#{6}\s+Art[Ã­i]culo\s+\d+', content, flags=re.MULTILINE)
    for i, block in enumerate(article_blocks[1:], start=1):  # Skip el bloque antes del primer artÃ­culo
        # Obtener solo el contenido (hasta el prÃ³ximo --- o fin)
        body = re.split(r'\n---\n', block)[0].strip()
        if len(body) < 50:
            num = article_nums[i-1] if i-1 < len(article_nums) else -1
            report.short_articles.append(num)
    
    # â”€â”€ 6. Verificar TOC â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    report.has_toc = bool(re.search(r'ÃNDICE DE ARTÃCULOS', content))
    
    # â”€â”€ 7. Generar warnings â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    if report.missing:
        report.warnings.append(
            f"ArtÃ­culos faltantes ({len(report.missing)}): "
            f"{report.missing[:10]}{'...' if len(report.missing) > 10 else ''}"
        )
    if report.short_articles:
        report.warnings.append(
            f"ArtÃ­culos sospechosamente cortos: {report.short_articles}"
        )
    if not report.has_toc:
        report.warnings.append("Sin Ãndice de ArtÃ­culos (TOC)")
    if report.frontmatter_issues:
        report.warnings.extend([f"Metadata: {i}" for i in report.frontmatter_issues])
    
    if report.duplicates:
        report.errors.append(f"ArtÃ­culos duplicados: {report.duplicates}")
    
    return report


def validate_all(rag_dir: str) -> list[ValidationReport]:
    """Valida todos los documentos en normativas_rag/."""
    reports = []
    rag_path = Path(rag_dir)
    
    for md_file in sorted(rag_path.glob("*.md")):
        report = validate_document(str(md_file))
        reports.append(report)
    
    return reports
```

---

## Reporte Visual (Rich Console)

```python
def print_report(reports: list[ValidationReport]) -> None:
    """Imprime tabla de resultados en consola con Rich."""
    table = Table(title="JullBrain â€” Reporte de ValidaciÃ³n", show_lines=True)
    
    table.add_column("Documento", style="cyan", max_width=35)
    table.add_column("ArtÃ­culos", justify="right")
    table.add_column("Faltantes", justify="right", style="yellow")
    table.add_column("Duplicados", justify="right", style="red")
    table.add_column("Cortos", justify="right", style="yellow")
    table.add_column("TOC", justify="center")
    table.add_column("Score", justify="right")
    table.add_column("Estado", justify="center")
    
    for r in reports:
        score = r.quality_score
        score_color = "green" if score >= 0.97 else "yellow" if score >= 0.90 else "red"
        status = "âœ… OK" if r.is_healthy else "âŒ ERROR"
        
        table.add_row(
            r.document[:35],
            str(r.total_articles),
            str(len(r.missing)) if r.missing else "-",
            str(len(r.duplicates)) if r.duplicates else "-",
            str(len(r.short_articles)) if r.short_articles else "-",
            "âœ“" if r.has_toc else "âœ—",
            f"[{score_color}]{score:.1%}[/{score_color}]",
            status,
        )
    
    console.print(table)
    
    # Resumen
    healthy = sum(1 for r in reports if r.is_healthy)
    console.print(f"\n[bold]Total:[/bold] {len(reports)} documentos | "
                  f"[green]{healthy} OK[/green] | "
                  f"[red]{len(reports) - healthy} con errores[/red]")
```

---

## Umbrales de Alerta

```python
QUALITY_THRESHOLDS = {
    'critical': 0.90,   # Por debajo â†’ ERROR, detener pipeline
    'warning': 0.95,    # Por debajo â†’ WARNING, revisar manualmente  
    'good': 0.98,       # Por debajo â†’ INFO, aceptable
    'excellent': 1.00,  # Perfecto
}

def get_quality_label(score: float) -> str:
    if score < QUALITY_THRESHOLDS['critical']:
        return "CRÃTICO â€” Revisar inmediatamente"
    elif score < QUALITY_THRESHOLDS['warning']:
        return "ADVERTENCIA â€” RevisiÃ³n recomendada"
    elif score < QUALITY_THRESHOLDS['good']:
        return "ACEPTABLE â€” Leve revisiÃ³n"
    else:
        return "EXCELENTE"
```

---

## ValidaciÃ³n de Chunks Individuales

```python
def validate_chunks_directory(chunks_dir: str, law_name: str) -> ValidationReport:
    """
    Valida los chunks en normativas_chunks/<ley>/.
    Verifica que cada chunk tenga frontmatter vÃ¡lido y contenido mÃ­nimo.
    """
    chunks_path = Path(chunks_dir) / law_name
    chunk_files = sorted(chunks_path.glob("articulo_*.md"))
    
    article_nums = []
    issues = []
    
    for chunk_file in chunk_files:
        # Extraer nÃºmero del nombre de archivo
        m = re.search(r'articulo_(\d+)\.md', chunk_file.name)
        if m:
            article_nums.append(int(m.group(1)))
        
        # Verificar frontmatter en cada chunk
        with open(chunk_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.startswith('---\n'):
            issues.append(f"{chunk_file.name}: Sin frontmatter")
        
        if len(content.strip()) < 100:
            issues.append(f"{chunk_file.name}: Contenido insuficiente")
    
    # Reutilizar lÃ³gica de secuencia
    report = ValidationReport(document=f"chunks/{law_name}")
    report.total_articles = len(article_nums)
    if article_nums:
        expected = set(range(min(article_nums), max(article_nums) + 1))
        report.missing = sorted(expected - set(article_nums))
    report.errors = issues
    
    return report
```

---

## IntegraciÃ³n con el Pipeline Principal

```python
# Al final de convert_normativas.py, ejecutar validaciÃ³n automÃ¡tica:

from validator import validate_document, print_report

def post_process_validation(output_path: str) -> bool:
    """
    Retorna True si el documento pasa los umbrales mÃ­nimos de calidad.
    Retorna False si hay errores crÃ­ticos.
    """
    report = validate_document(output_path)
    
    if not report.is_healthy:
        console.print(f"[red]âŒ ERRORES CRÃTICOS en {report.document}:[/red]")
        for error in report.errors:
            console.print(f"  â€¢ {error}")
        return False
    
    if report.warnings:
        console.print(f"[yellow]âš ï¸  Advertencias en {report.document}:[/yellow]")
        for warning in report.warnings:
            console.print(f"  â€¢ {warning}")
    
    score_label = get_quality_label(report.quality_score)
    console.print(f"[green]âœ… {report.document}[/green] â€” Score: {report.quality_score:.1%} ({score_label})")
    
    return report.quality_score >= QUALITY_THRESHOLDS['critical']
```

