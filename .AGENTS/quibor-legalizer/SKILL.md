---
name: quibor-legalizer
description: >
  Skill especializado en el módulo legalizer.py y chunker.py de QUIBOR. Úsalo cuando:
  artículos venezolanos no se detectan correctamente, la jerarquía TÍTULO/CAPÍTULO/Artículo
  está mal anidada, los chunks generados están vacíos o mal formados, necesitas agregar
  soporte para un nuevo patrón de ley venezolana, el TOC automático falla, o los artículos
  se fusionan entre sí. También aplica al diseñar o depurar la lógica de separación de
  artículos, numeración romana de títulos, o generación de IDs únicos por chunk.
  Trigger siempre que el usuario mencione: artículos fusionados, legalizer, chunker,
  jerarquía legal, TOC automático, separación de artículos.
---

# QUIBOR Legalizer & Chunker — Skill Especializado

## Responsabilidades de Cada Módulo

| Módulo | Entrada | Salida |
|--------|---------|--------|
| `legalizer.py` | Markdown crudo de Docling | Markdown jerarquizado con TÍTULO/CAPÍTULO/Artículo |
| `chunker.py` | Markdown jerarquizado | Un `.md` por artículo en `normativas_chunks/` |

---

## Patrones de Detección de Artículos

### Regex Principal (Venezuela)

```python
import re

# Patrones de artículo en leyes venezolanas (ordenados por especificidad)
ARTICLE_PATTERNS = [
    # Patrón estándar: "Artículo 1." o "Artículo 1-"
    r'^Art[íi]culo\s+(\d+)[.\-–]\s*(.{0,80}?)$',
    # Patrón con punto final en número: "Artículo 1°."  
    r'^Art[íi]culo\s+(\d+)[°º][.\-]?\s*(.{0,80}?)$',
    # Patrón en mayúsculas: "ARTÍCULO 1"
    r'^ART[ÍI]CULO\s+(\d+)[.\-–]?\s*(.{0,80}?)$',
    # Patrón corto: "Art. 1"
    r'^Art\.\s+(\d+)[.\-]?\s*(.{0,80}?)$',
]

TITLE_PATTERNS = [
    r'^T[ÍI]TULO\s+((?:[IVX]+|\d+))[.\-\s]',
    r'^TITULO\s+((?:[IVX]+|\d+))[.\-\s]',
]

CHAPTER_PATTERNS = [
    r'^CAP[ÍI]TULO\s+((?:[IVX]+|\d+|\w+))[.\-\s]',
    r'^CAPÍTULO\s+([A-ZÁÉÍÓÚ\s]+)[.\-]',
    r'^Capítulo\s+((?:[IVX]+|\d+))[.\-\s]',
]

SECTION_PATTERNS = [
    r'^SECCIÓN\s+((?:[IVX]+|\d+))[.\-\s]',
    r'^Sección\s+((?:[IVX]+|\d+))[.\-\s]',
]
```

### Función Principal de Detección

```python
def detect_hierarchy_level(line: str) -> tuple[str, str]:
    """
    Returns: (level, content)
    level: 'titulo' | 'capitulo' | 'seccion' | 'articulo' | 'text'
    """
    line = line.strip()
    
    for pattern in TITLE_PATTERNS:
        m = re.match(pattern, line, re.IGNORECASE)
        if m:
            return ('titulo', line)
    
    for pattern in CHAPTER_PATTERNS:
        m = re.match(pattern, line, re.IGNORECASE)
        if m:
            return ('capitulo', line)
    
    for pattern in SECTION_PATTERNS:
        m = re.match(pattern, line, re.IGNORECASE)
        if m:
            return ('seccion', line)
    
    for pattern in ARTICLE_PATTERNS:
        m = re.match(pattern, line, re.MULTILINE | re.IGNORECASE)
        if m:
            num = int(m.group(1))
            title = m.group(2).strip() if m.lastindex >= 2 else ''
            return ('articulo', f"Artículo {num}" + (f" — {title}" if title else ''))
    
    return ('text', line)
```

---

## Estructura de Salida del Legalizer

```markdown
## TÍTULO I — De los Principios Generales

### CAPÍTULO I — Disposiciones Fundamentales

###### Artículo 1 — Principio de Legalidad

[contenido del artículo]

---

###### Artículo 2 — Retroactividad Favorable

[contenido del artículo]

---
```

### Niveles de Heading por Jerarquía

| Nivel Legal | Heading Markdown | Motivo |
|------------|-----------------|--------|
| TÍTULO | `##` (H2) | Nivel máximo de agrupación |
| CAPÍTULO | `###` (H3) | Segundo nivel |
| SECCIÓN | `####` (H4) | Tercer nivel (raro en leyes venezolanas) |
| Artículo | `######` (H6) | Nivel hoja — fácil de extraer por regex |

> **Decisión de diseño**: Usar H6 (`######`) para artículos garantiza que no colisionen con la jerarquía estructural y son fácilmente identificables por `chunker.py`.

---

## Generación del TOC Automático

```python
def generate_toc(articles: list[dict]) -> str:
    """
    articles: [{'num': 1, 'title': 'Principio...', 'ubicacion': 'TÍTULO I > CAP I'}]
    """
    lines = ["### ÍNDICE DE ARTÍCULOS\n", "| Art. | Descripción | Ubicación |\n", 
             "|------|-------------|----------|\n"]
    
    for art in articles:
        title_short = art['title'][:50] + '...' if len(art['title']) > 50 else art['title']
        ubicacion_short = art['ubicacion'][:40] + '...' if len(art['ubicacion']) > 40 else art['ubicacion']
        lines.append(f"| {art['num']} | {title_short} | {ubicacion_short} |\n")
    
    return ''.join(lines)
```

---

## Lógica del Chunker

### Algoritmo de Split

```python
def split_into_chunks(legalized_md: str, law_metadata: dict) -> list[dict]:
    """
    Divide el Markdown legalizado en chunks individuales por artículo.
    Preserva el contexto de TÍTULO y CAPÍTULO en cada chunk.
    """
    chunks = []
    current_titulo = ""
    current_capitulo = ""
    current_article_num = None
    current_article_lines = []
    
    for line in legalized_md.split('\n'):
        if line.startswith('## '):  # TÍTULO
            current_titulo = line[3:].strip()
            current_capitulo = ""  # Reset capítulo al cambiar título
            
        elif line.startswith('### '):  # CAPÍTULO
            current_capitulo = line[4:].strip()
            
        elif line.startswith('###### Artículo '):  # Artículo
            # Guardar artículo anterior
            if current_article_num and current_article_lines:
                chunks.append(build_chunk(
                    current_article_num, current_article_lines,
                    current_titulo, current_capitulo, law_metadata
                ))
            # Iniciar nuevo artículo
            current_article_num = extract_article_num(line)
            current_article_lines = [line]
            
        elif current_article_num is not None:
            if line.strip() == '---':  # Separador = fin de artículo
                chunks.append(build_chunk(
                    current_article_num, current_article_lines,
                    current_titulo, current_capitulo, law_metadata
                ))
                current_article_num = None
                current_article_lines = []
            else:
                current_article_lines.append(line)
    
    # Guardar último artículo
    if current_article_num and current_article_lines:
        chunks.append(build_chunk(
            current_article_num, current_article_lines,
            current_titulo, current_capitulo, law_metadata
        ))
    
    return chunks


def build_chunk(num: int, lines: list, titulo: str, capitulo: str, meta: dict) -> dict:
    """Construye el dict de un chunk con frontmatter YAML."""
    ubicacion = titulo
    if capitulo:
        ubicacion += f" > {capitulo}"
    
    frontmatter = (
        f"---\n"
        f"ley: \"{meta['nombre_oficial']}\"\n"
        f"articulo: {num}\n"
        f"ubicacion: \"{ubicacion}\"\n"
        f"gaceta_oficial: \"{meta.get('gaceta_oficial', 'N/D')}\"\n"
        f"fecha_publicacion: \"{meta.get('fecha_publicacion', 'N/D')}\"\n"
        f"hash_pdf_sha256: \"{meta.get('hash_pdf_sha256', '')}\"\n"
        f"---\n\n"
    )
    
    return {
        'num': num,
        'filename': f"articulo_{str(num).zfill(4)}.md",
        'content': frontmatter + '\n'.join(lines)
    }
```

---

## Casos Especiales de Artículos Venezolanos

### Artículos con Parágrafos

```
Artículo 5. El juez ordenará...

Parágrafo Único: Las disposiciones del presente artículo...

Parágrafo Primero: ...
Parágrafo Segundo: ...
```

**Regla**: Los parágrafos pertenecen al artículo anterior. No separarlos como chunks independientes.

```python
PARAGRAFO_PATTERNS = [
    r'^Parágrafo\s+(Único|Primero|Segundo|Tercero|[IVX]+|\d+)[:\.]',
    r'^PARÁGRAFO\s+',
]
# Si se detecta un parágrafo, acumular en el artículo actual (no crear nuevo chunk)
```

### Artículos con Numerales y Literales

```
Artículo 12. Son causas de extinción:
1. El pago;
2. La compensación;
   a) En forma total;
   b) En forma parcial;
3. La prescripción.
```

**Regla**: Los numerales y literales son parte del artículo. El chunk incluye todo el bloque hasta el próximo `Artículo N` o `---`.

### Artículos Modificados / Derogados

```
Artículo 45. (Derogado)
Artículo 46. (Reformado por la Gaceta N° 6.210 del 30-12-2015)
```

**Regla**: Generar el chunk igualmente. El estado del artículo queda registrado en el contenido. El validador puede marcarlo con `status: derogado`.

---

## Métricas de Calidad del Chunker

```python
def validate_chunks(chunks: list[dict]) -> dict:
    """Valida la calidad de los chunks generados."""
    issues = []
    
    nums = [c['num'] for c in chunks]
    
    # 1. Secuencia continua
    expected = list(range(min(nums), max(nums) + 1))
    missing = set(expected) - set(nums)
    if missing:
        issues.append(f"Artículos faltantes: {sorted(missing)}")
    
    # 2. Duplicados
    seen = set()
    duplicates = [n for n in nums if n in seen or seen.add(n)]
    if duplicates:
        issues.append(f"Artículos duplicados: {duplicates}")
    
    # 3. Chunks muy cortos (< 50 chars de contenido)
    short = [c['num'] for c in chunks if len(c['content']) < 200]
    if short:
        issues.append(f"Artículos sospechosamente cortos: {short}")
    
    return {
        'total_chunks': len(chunks),
        'issues': issues,
        'quality_score': (len(chunks) - len(issues)) / max(len(chunks), 1)
    }
```
