---
name: JullBrain-legalizer
description: >
  Skill especializado en el módulo legalizer.py de JullBrain. Úsalo cuando:
  artículos venezolanos no se detectan correctamente, la jerarquía TÍTULO/CAPÍTULO/Artículo
  está mal anidada, necesitas agregar soporte para un nuevo patrón de ley venezolana, 
  o los artículos se fusionan entre sí. También aplica al diseñar o depurar la lógica de separación de
  artículos y numeración de títulos.
  Trigger siempre que el usuario mencione: artículos fusionados, legalizer,
  jerarquía legal, separación de artículos.
---

# JullBrain Legalizer — Skill Especializado

## Responsabilidad del Módulo

| Módulo | Entrada | Salida |
|--------|---------|--------|
| `legalizer.py` | Markdown crudo de Docling | Markdown jerarquizado con TÍTULO/CAPÍTULO/Artículo formateados como headings de Markdown (`##`, `###`, `######`) |

> **IMPORTANTE**: La salida jerarquizada del `legalizer.py` es fundamental para que el motor `HierarchicalChunker` de IBM Docling (Fase 3 del pipeline) logre generar JSON chunks con la segmentación correcta. Si el legalizer no inyecta los `######` en los artículos, Docling no sabrá separarlos para RAGFlow.

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
## TÍTULO I
### CAPÍTULO I
#### SECCIÓN I

###### Artículo 1 — Objeto de la Ley
El presente código tiene por objeto...

###### Artículo 2 — Ámbito de Aplicación
La presente ley se aplica a...
```

> **Decisión de diseño**: Usar H6 (`######`) para artículos garantiza que no colisionen con la jerarquía estructural (Títulos, Capítulos) y son fácilmente identificables por el motor de fragmentación `HierarchicalChunker` de IBM Docling, el cual dividirá automáticamente el texto respetando los H6.
