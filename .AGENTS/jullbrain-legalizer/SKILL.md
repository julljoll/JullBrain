---
name: JullBrain-legalizer
description: >
  Skill especializado en el mÃ³dulo legalizer.py de JullBrain. Ãšsalo cuando:
  artÃ­culos venezolanos no se detectan correctamente, la jerarquÃ­a TÃ TULO/CAPÃ TULO/ArtÃ­culo
  estÃ¡ mal anidada, necesitas agregar soporte para un nuevo patrÃ³n de ley venezolana, 
  o los artÃ­culos se fusionan entre sÃ­. TambiÃ©n aplica al diseÃ±ar o depurar la lÃ³gica de separaciÃ³n de
  artÃ­culos y numeraciÃ³n de tÃ­tulos.
  Trigger siempre que el usuario mencione: artÃ­culos fusionados, legalizer,
  jerarquÃ­a legal, separaciÃ³n de artÃ­culos.
---

# JullBrain Legalizer â€” Skill Especializado

## Responsabilidad del MÃ³dulo

| MÃ³dulo | Entrada | Salida |
|--------|---------|--------|
| `legalizer.py` | Markdown crudo de Docling | Markdown jerarquizado con TÃ TULO/CAPÃ TULO/ArtÃ­culo formateados como headings de Markdown (`##`, `###`, `######`) |

> **IMPORTANTE**: La salida jerarquizada del `legalizer.py` es fundamental para que el motor `HierarchicalChunker` de IBM Docling (Fase 3 del pipeline) logre generar JSON chunks con la segmentaciÃ³n correcta. Si el legalizer no inyecta los `######` en los artÃ­culos, Docling no sabrÃ¡ separarlos.

---

## Patrones de DetecciÃ³n de ArtÃ­culos

### Regex Principal (Venezuela)

```python
import re

# Patrones de artÃ­culo en leyes venezolanas (ordenados por especificidad)
ARTICLE_PATTERNS = [
    # PatrÃ³n estÃ¡ndar: "ArtÃ­culo 1." o "ArtÃ­culo 1-"
    r'^Art[Ã­i]culo\s+(\d+)[.\-â€“]\s*(.{0,80}?)$',
    # PatrÃ³n con punto final en nÃºmero: "ArtÃ­culo 1Â°."  
    r'^Art[Ã­i]culo\s+(\d+)[Â°Âº][.\-]?\s*(.{0,80}?)$',
    # PatrÃ³n en mayÃºsculas: "ARTÃ CULO 1"
    r'^ART[Ã I]CULO\s+(\d+)[.\-â€“]?\s*(.{0,80}?)$',
    # PatrÃ³n corto: "Art. 1"
    r'^Art\.\s+(\d+)[.\-]?\s*(.{0,80}?)$',
]

TITLE_PATTERNS = [
    r'^T[Ã I]TULO\s+((?:[IVX]+|\d+))[.\-\s]',
    r'^TITULO\s+((?:[IVX]+|\d+))[.\-\s]',
]

CHAPTER_PATTERNS = [
    r'^CAP[Ã I]TULO\s+((?:[IVX]+|\d+|\w+))[.\-\s]',
    r'^CAPÃ TULO\s+([A-ZÃ Ã‰Ã Ã“Ãš\s]+)[.\-]',
    r'^CapÃ­tulo\s+((?:[IVX]+|\d+))[.\-\s]',
]

SECTION_PATTERNS = [
    r'^SECCIÃ“N\s+((?:[IVX]+|\d+))[.\-\s]',
    r'^SecciÃ³n\s+((?:[IVX]+|\d+))[.\-\s]',
]
```

### FunciÃ³n Principal de DetecciÃ³n

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
            return ('articulo', f"ArtÃ­culo {num}" + (f" â€” {title}" if title else ''))
    
    return ('text', line)
```

---

## Estructura de Salida del Legalizer

```markdown
## TÃ TULO I
### CAPÃ TULO I
#### SECCIÃ“N I

###### ArtÃ­culo 1 â€” Objeto de la Ley
El presente cÃ³digo tiene por objeto...

###### ArtÃ­culo 2 â€” Ã mbito de AplicaciÃ³n
La presente ley se aplica a...
```

> **DecisiÃ³n de diseÃ±o**: Usar H6 (`######`) para artÃ­culos garantiza que no colisionen con la jerarquÃ­a estructural (TÃ­tulos, CapÃ­tulos) y son fÃ¡cilmente identificables por el motor de fragmentaciÃ³n `HierarchicalChunker` de IBM Docling, el cual dividirÃ¡ automÃ¡ticamente el texto respetando los H6.
